"""
Chapter 3 (Player Character Classes) table extraction and fixes.

This post-processor extracts class ability requirement tables (2 columns, 3 rows)
for each class in Chapter 3.
"""

from pathlib import Path
import json
from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput


class Chapter3TableFixer(BaseProcessor):
    """Extracts class ability tables in Chapter 3."""
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Extract class ability tables for Chapter 3.
        
        Args:
            input_data: Output from previous processor
            context: Execution context
            
        Returns:
            ProcessorOutput with extracted tables
        """
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        
        # Find the Chapter 3 file
        chapter_3_file = None
        for file in sections_dir.glob("*chapter-three-player-character-classes.json"):
            chapter_3_file = file
            break
        
        if not chapter_3_file or not chapter_3_file.exists():
            # Chapter 3 file not found, return unchanged
            return input_data
        
        # Load the chapter data
        with open(chapter_3_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        # Apply the adjustments (this modifies section_data in place)
        from ..transformers import chapter_3_processing
        chapter_3_processing.apply_chapter_3_adjustments(section_data)
        
        # Write back to disk
        with open(chapter_3_file, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, indent=2, ensure_ascii=False)
        
        # Count tables added
        total_tables = sum(len(p.get("tables", [])) for p in section_data.get("pages", []))
        
        return ProcessorOutput(
            data=input_data.data,
            metadata={
                "status": "success",
                "message": f"Applied Chapter 3 table extraction to {chapter_3_file.name}",
                "tables_total": total_tables,
                "file_updated": str(chapter_3_file)
            }
        )

