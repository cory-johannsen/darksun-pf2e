"""Transform stage processors for data transformation.

This module wraps existing transformation logic in Processor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from ..transformers import REGISTRY as TRANSFORMER_REGISTRY


class JournalTransformProcessor(BaseProcessor):
    """Processor for transforming raw sections to formatted HTML journals.
    
    Wraps the existing journal_v2 transformer functionality.
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
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load profiles
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        
        # Get the journal transformer
        journal_transformer = TRANSFORMER_REGISTRY.get("journal_v2")
        if not journal_transformer:
            raise ValueError("journal_v2 transformer not found in registry")
        
        # Transform each section that uses journal_v2
        transformed_files = []
        for profile in profiles:
            if profile.get("transformer") != "journal_v2":
                continue
            
            slug = profile.get("slug")
            if not slug:
                continue
            
            # Find the section file
            section_files = list(sections_dir.glob(f"*-{slug}.json"))
            if not section_files:
                context.warnings.append(f"Section file not found for slug: {slug}")
                continue
            
            section_file = section_files[0]
            section_data = json.loads(section_file.read_text(encoding="utf-8"))
            
            # Apply transformation
            config = {}
            if mapping_path := profile.get("mapping"):
                mapping_file = profiles_path.parent / mapping_path
                if mapping_file.exists():
                    config = json.loads(mapping_file.read_text(encoding="utf-8"))
            
            if additional_config := profile.get("config"):
                config.update(additional_config)
            
            transformed = journal_transformer(section_data, config)
            
            # Write output
            output_name = profile.get("output_template", "{slug}.json").format(slug=slug)
            output_file = output_dir / output_name
            
            payload = {
                "slug": slug,
                "transformer": "journal_v2",
                "source_section": section_data.get("title"),
                "data": transformed,
            }
            
            output_file.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            transformed_files.append(str(output_file))
            context.items_processed += 1
        
        return ProcessorOutput(
            data={
                "output_dir": str(output_dir),
                "transformed_files": transformed_files,
            },
            metadata={
                "file_count": len(transformed_files),
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

