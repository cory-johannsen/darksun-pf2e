"""Extract stage processors for PDF extraction.

This module wraps existing extraction logic in Processor/PostProcessor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..base import BasePostProcessor, BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from ..extract import extract_sections, generate_manifest, load_manifest
from ..models import Manifest


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
    
    Wraps the existing extract_sections functionality.
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
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load manifest
        manifest = load_manifest(manifest_path)
        
        # Extract sections
        extract_sections(
            manifest,
            output_dir=output_dir,
            min_level=min_level,
            mode=mode,
            table_settings=table_settings,
        )
        
        # Count extracted files
        extracted_files = list(output_dir.glob("*.json"))
        context.items_processed = len(extracted_files)
        
        return ProcessorOutput(
            data={
                "sections_dir": str(output_dir),
                "extracted_files": [str(f) for f in extracted_files],
                "mode": mode,
            },
            metadata={
                "file_count": len(extracted_files),
                "extraction_mode": mode,
            }
        )


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

