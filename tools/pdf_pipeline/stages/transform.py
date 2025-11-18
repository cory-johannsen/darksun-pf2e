"""Transform stage processors for data transformation.

This module wraps existing transformation logic in Processor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from ..transformers import REGISTRY as TRANSFORMER_REGISTRY
from ..utils.parallel import run_process_pool, should_parallelize, get_max_workers

logger = logging.getLogger(__name__)


def _transform_journal_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker function to transform a single section to journal.
    
    Args:
        task: Dict with section_file, output_file, slug, config, etc.
        
    Returns:
        Dict with items, warnings, errors, and output_file
    """
    from pathlib import Path
    import json
    from ..transformers import REGISTRY as TRANSFORMER_REGISTRY
    
    section_file = Path(task["section_file"])
    output_file = Path(task["output_file"])
    slug = task["slug"]
    config = task.get("config", {})
    
    warnings = []
    errors = []
    
    try:
        # Load section data
        section_data = json.loads(section_file.read_text(encoding="utf-8"))
        
        # Get the journal transformer
        journal_transformer = TRANSFORMER_REGISTRY.get("journal")
        if not journal_transformer:
            raise ValueError("journal transformer not found in registry")
        
        # Apply transformation
        transformed = journal_transformer(section_data, config)
        
        # Write output
        payload = {
            "slug": slug,
            "transformer": "journal",
            "source_section": section_data.get("title"),
            "data": transformed,
        }
        
        output_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        return {
            "items": 1,
            "warnings": warnings,
            "errors": errors,
            "output_file": str(output_file),
        }
    
    except Exception as e:
        error_msg = f"Failed to transform section {slug}: {e}"
        errors.append(error_msg)
        return {
            "items": 0,
            "warnings": warnings,
            "errors": errors,
            "output_file": None,
        }



class JournalTransformProcessor(BaseProcessor):
    """Processor for transforming raw sections to formatted HTML journals.
    
    Supports parallel transformation when enabled via config.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Transform raw sections to HTML journals.
        
        Args:
            input_data: Input containing sections directory or configuration
            context: Execution context
            
        Returns:
            ProcessorOutput with transformed journals
        """
        # Extract configuration
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        output_dir = Path(self.config.get("output_dir", "data/processed/journals"))
        profiles_path = Path(self.config.get("profiles_path", "data/mappings/section_profiles.json"))
        
        # Parallel config
        global_parallel = context.metadata.get("parallel", False)
        use_parallel = should_parallelize(self.config, global_parallel)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load profiles
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        
        # Build task list
        skip_slugs = set()
        tasks = []
        
        for profile in profiles:
            if profile.get("transformer") != "journal":
                continue
            
            # Get configuration
            mapping_config = {}
            if mapping_path := profile.get("mapping"):
                mapping_file = profiles_path.parent / mapping_path
                if mapping_file.exists():
                    mapping_config = json.loads(mapping_file.read_text(encoding="utf-8"))
            
            additional_config = profile.get("config", {})
            profile_skip_slugs = set(profile.get("skip_slugs", []))
            skip_slugs.update(profile_skip_slugs)
            
            # Handle profile with specific slug
            if "slug" in profile:
                slug = profile["slug"]
                if slug in skip_slugs:
                    continue
                    
                # Find the section file
                section_files = list(sections_dir.glob(f"*-{slug}.json"))
                if not section_files:
                    context.warnings.append(f"Section file not found for slug: {slug}")
                    continue
                
                section_file = section_files[0]
                output_name = profile.get("output_template", "{slug}.json").format(slug=slug)
                output_file = output_dir / output_name
                
                config = {**mapping_config, **additional_config}
                task = {
                    "section_file": str(section_file),
                    "output_file": str(output_file),
                    "slug": slug,
                    "config": config,
                }
                tasks.append(task)
            
            # Handle profile with glob pattern
            elif "glob" in profile:
                glob_pattern = profile["glob"]
                for section_file in sorted(sections_dir.glob(glob_pattern)):
                    # Load section data to get slug
                    try:
                        section_data = json.loads(section_file.read_text(encoding="utf-8"))
                        slug = section_data.get("slug")
                        
                        if not slug:
                            context.warnings.append(f"Section file {section_file.name} missing slug")
                            continue
                        
                        if slug in skip_slugs:
                            continue
                        
                        output_name = profile.get("output_template", "{slug}.json").format(slug=slug)
                        output_file = output_dir / output_name
                        
                        config = {**mapping_config, **additional_config}
                        task = {
                            "section_file": str(section_file),
                            "output_file": str(output_file),
                            "slug": slug,
                            "config": config,
                        }
                        tasks.append(task)
                    except Exception as e:
                        context.warnings.append(f"Failed to read {section_file.name}: {e}")
                        continue
        
        # Transform (parallel or sequential)
        transformed_files = []
        if use_parallel and len(tasks) > 1:
            max_workers = get_max_workers(self.config, default=4)
            chunksize = int(self.config.get("chunksize", 1))
            
            logger.info(f"Transforming {len(tasks)} sections in parallel with {max_workers} workers")
            result = run_process_pool(
                tasks,
                _transform_journal_task,
                max_workers=max_workers,
                chunksize=chunksize,
                desc="journal transformation"
            )
            
            context.items_processed = result["items_processed"]
            context.warnings.extend(result["warnings"])
            context.errors.extend(result["errors"])
            transformed_files = sorted([r["output_file"] for r in result["results"] if r.get("output_file")])
        
        else:
            # Sequential transformation
            logger.info(f"Transforming {len(tasks)} sections sequentially")
            for task in tasks:
                result = _transform_journal_task(task)
                context.items_processed += result["items"]
                context.warnings.extend(result["warnings"])
                context.errors.extend(result["errors"])
                if result.get("output_file"):
                    transformed_files.append(result["output_file"])
            transformed_files = sorted(transformed_files)
        
        return ProcessorOutput(
            data={
                "output_dir": str(output_dir),
                "transformed_files": transformed_files,
            },
            metadata={
                "file_count": len(transformed_files),
                "parallel": use_parallel,
            }
        )



class AncestryTransformProcessor(BaseProcessor):
    """Processor for transforming race sections to ancestry data.
    
    Wraps the existing ancestries transformer functionality.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Transform race sections to ancestry data.
        
        Args:
            input_data: Input containing sections directory or configuration
            context: Execution context
            
        Returns:
            ProcessorOutput with transformed ancestry data
        """
        # Extract configuration
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        output_dir = Path(self.config.get("output_dir", "data/processed"))
        mapping_file = Path(self.config.get("mapping_file", "data/mappings/ancestries.json"))
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the ancestry transformer
        ancestry_transformer = TRANSFORMER_REGISTRY.get("ancestries")
        if not ancestry_transformer:
            raise ValueError("ancestries transformer not found in registry")
        
        # Load mapping data
        mapping_data = {}
        if mapping_file.exists():
            mapping_data = json.loads(mapping_file.read_text(encoding="utf-8"))
        
        # Find the race chapter section
        race_section_files = list(sections_dir.glob("*-chapter-two-player-character-races.json"))
        if not race_section_files:
            context.warnings.append("Race section file not found")
            return ProcessorOutput(
                data={"ancestries": []},
                metadata={"ancestry_count": 0}
            )
        
        section_file = race_section_files[0]
        section_data = json.loads(section_file.read_text(encoding="utf-8"))
        
        # Apply transformation
        transformed = ancestry_transformer(section_data, mapping_data)
        
        # Write output
        output_file = output_dir / "ancestries.json"
        payload = {
            "slug": "chapter-two-player-character-races",
            "transformer": "ancestries",
            "source_section": section_data.get("title"),
            "data": transformed,
        }
        
        output_file.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        context.items_processed = 1
        
        return ProcessorOutput(
            data={
                "output_file": str(output_file),
                "ancestries": transformed,
            },
            metadata={
                "ancestry_count": len(transformed) if isinstance(transformed, list) else 0,
            }
        )

