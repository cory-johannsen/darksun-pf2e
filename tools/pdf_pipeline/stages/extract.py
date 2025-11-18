"""Extract stage processors for PDF extraction.

This module wraps existing extraction logic in Processor/PostProcessor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..base import BasePostProcessor, BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from .. import generate_manifest, load_manifest
from ..models import Section, Manifest, StructuredSection
from ..utils.parallel import run_process_pool, should_parallelize, get_max_workers

logger = logging.getLogger(__name__)


def _extract_section_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker function to extract a single section from PDF.
    
    This function is called in parallel by SectionExtractionProcessor.
    It must be at module level to be picklable.
    
    Args:
        task: Dict containing:
            - pdf_path: Path to PDF file
            - section: Section dict with title, slug, level, start_page, end_page, parent_slugs
            - output_path: Path where to write the output JSON
            - mode: "structured" or "legacy"
            - table_settings: Optional table detection settings
            
    Returns:
        Dict with items, warnings, errors, and path
    """
    import json
    from pathlib import Path
    import fitz
    import pdfplumber
    from ..extract import (
        _iter_sections, _serialize_blocks, _structured_blocks,
        _structured_tables, _extract_structured_section, DEFAULT_TABLE_SETTINGS
    )
    from ..models import Section, StructuredSection
    
    pdf_path = Path(task["pdf_path"])
    section_dict = task["section"]
    output_path = Path(task["output_path"])
    mode = task["mode"]
    table_settings = task.get("table_settings")
    
    warnings = []
    errors = []
    
    try:
        # Reconstruct Section object from dict
        # Extract parent_slugs first (Section model doesn't have this field)
        parent_slugs = tuple(section_dict.pop("parent_slugs", []))
        section = Section(**section_dict)
        
        if mode == "legacy":
            # Legacy extraction mode
            with fitz.open(pdf_path) as doc:
                pages = []
                for page_number in section.page_span:
                    page = doc[page_number - 1]
                    page_entry = {
                        "page_number": page_number,
                        "text": page.get_text("text"),
                        "blocks": _serialize_blocks(page.get_text("blocks")),
                    }
                    pages.append(page_entry)
                
                data = {
                    "title": section.title,
                    "slug": section.slug,
                    "level": section.level,
                    "start_page": section.start_page,
                    "end_page": section.end_page,
                    "parent_slugs": list(parent_slugs),
                    "pages": pages,
                }
                
                output_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        
        else:  # structured mode
            settings = DEFAULT_TABLE_SETTINGS.copy()
            if table_settings:
                settings.update(table_settings)
            
            with fitz.open(pdf_path) as doc, pdfplumber.open(str(pdf_path)) as plumber_doc:
                structured_section = _extract_structured_section(
                    doc,
                    plumber_doc,
                    section,
                    parent_slugs,
                    table_settings=settings,
                )
                
                output_path.write_text(
                    json.dumps(structured_section.model_dump(), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        
        return {
            "items": 1,
            "warnings": warnings,
            "errors": errors,
            "path": str(output_path),
        }
    
    except Exception as e:
        error_msg = f"Failed to extract section {section_dict.get('slug', 'unknown')}: {e}"
        errors.append(error_msg)
        return {
            "items": 0,
            "warnings": warnings,
            "errors": errors,
            "path": None,
        }


class ManifestProcessor(BaseProcessor):
    """Processor for generating PDF manifest from table of contents.
    
    Wraps the existing generate_manifest functionality.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Generate manifest from PDF.
        
        Args:
            input_data: Input containing PDF path or configuration
            context: Execution context
            
        Returns:
            ProcessorOutput with generated manifest
        """
        # Extract configuration
        pdf_path = Path(self.config.get("pdf_path", "tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf"))
        output_dir = Path(self.config.get("output_dir", "data/raw"))
        manifest_path = output_dir / "pdf_manifest.json"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate or load manifest
        if manifest_path.exists():
            manifest = load_manifest(manifest_path)
            context.metadata["manifest_loaded"] = True
        else:
            manifest = generate_manifest(pdf_path, manifest_path)
            context.metadata["manifest_generated"] = True
        
        context.items_processed = 1
        
        return ProcessorOutput(
            data={
                "manifest": manifest.model_dump() if hasattr(manifest, "model_dump") else manifest.dict(),
                "manifest_path": str(manifest_path),
                "pdf_path": str(pdf_path),
            },
            metadata={
                "section_count": len(manifest.sections),
                "page_count": manifest.page_count,
            }
        )


class SectionExtractionProcessor(BaseProcessor):
    """Processor for extracting sections from PDF based on manifest.
    
    Supports parallel extraction when enabled via config.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Extract sections from PDF.
        
        Args:
            input_data: Input containing manifest or manifest path
            context: Execution context
            
        Returns:
            ProcessorOutput with extracted sections information
        """
        # Extract configuration
        manifest_path = Path(self.config.get("manifest_path", "data/raw/pdf_manifest.json"))
        pdf_path = Path(self.config.get("pdf_path", "tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf"))
        output_dir = Path(self.config.get("output_dir", "data/raw_structured/sections"))
        mode = self.config.get("mode", "structured")
        min_level = self.config.get("min_level", 2)
        table_settings = self.config.get("table_settings")
        
        # Parallel config
        global_parallel = context.metadata.get("parallel", False)
        use_parallel = should_parallelize(self.config, global_parallel)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load manifest
        manifest = load_manifest(manifest_path)
        
        # Build task list for sections
        tasks = []
        for section, parents in self._iter_sections(manifest.sections):
            if section.level < min_level:
                continue
            
            filename = f"{section.level:02d}-{section.start_page:03d}-{section.slug}.json"
            output_path = output_dir / filename
            
            # Convert section to dict for pickling
            section_dict = section.model_dump() if hasattr(section, "model_dump") else section.dict()
            section_dict["parent_slugs"] = list(parents)
            
            task = {
                "pdf_path": str(pdf_path),
                "section": section_dict,
                "output_path": str(output_path),
                "mode": mode,
                "table_settings": table_settings,
            }
            tasks.append(task)
        
        # Extract sections (parallel or sequential)
        if use_parallel and len(tasks) > 1:
            max_workers = get_max_workers(self.config, default=4)
            chunksize = int(self.config.get("chunksize", 1))
            
            logger.info(f"Extracting {len(tasks)} sections in parallel with {max_workers} workers")
            result = run_process_pool(
                tasks,
                _extract_section_task,
                max_workers=max_workers,
                chunksize=chunksize,
                desc="section extraction"
            )
            
            context.items_processed = result["items_processed"]
            context.warnings.extend(result["warnings"])
            context.errors.extend(result["errors"])
            
            # Collect paths
            extracted_files = sorted([r["path"] for r in result["results"] if r.get("path")])
        
        else:
            # Sequential extraction
            logger.info(f"Extracting {len(tasks)} sections sequentially")
            extracted_files = []
            for task in tasks:
                result = _extract_section_task(task)
                context.items_processed += result["items"]
                context.warnings.extend(result["warnings"])
                context.errors.extend(result["errors"])
                if result.get("path"):
                    extracted_files.append(result["path"])
            extracted_files = sorted(extracted_files)
        
        return ProcessorOutput(
            data={
                "sections_dir": str(output_dir),
                "extracted_files": extracted_files,
                "mode": mode,
            },
            metadata={
                "file_count": len(extracted_files),
                "extraction_mode": mode,
                "parallel": use_parallel,
            }
        )
    
    @staticmethod
    def _iter_sections(sections: List[Section], parent_chain: Tuple[str, ...] = ()) -> List[Tuple[Section, Tuple[str, ...]]]:
        """Iterate through sections with their parent chain."""
        result = []
        for section in sections:
            chain = parent_chain + (section.slug,)
            result.append((section, parent_chain))
            if section.children:
                result.extend(SectionExtractionProcessor._iter_sections(section.children, chain))
        return result



class TableDetectionPostProcessor(BasePostProcessor):
    """PostProcessor for detecting and structuring tables in extracted content.
    
    This is currently a no-op as table detection is handled during extraction,
    but provides a hook for additional post-processing if needed.
    """
    
    def postprocess(self, input_data: ProcessorOutput, context: ExecutionContext) -> ProcessorOutput:
        """Post-process extracted sections for table detection.
        
        Args:
            input_data: Output from SectionExtractionProcessor
            context: Execution context
            
        Returns:
            ProcessorOutput with table detection applied
        """
        # Table detection is already performed during extraction
        # This postprocessor provides a hook for additional refinement
        
        detect_headers = self.config.get("detect_headers", True)
        merge_cells = self.config.get("merge_cells", True)
        
        # Currently a pass-through, but could add additional processing here
        context.metadata["table_detection_applied"] = True
        context.metadata["detect_headers"] = detect_headers
        context.metadata["merge_cells"] = merge_cells
        
        return input_data

