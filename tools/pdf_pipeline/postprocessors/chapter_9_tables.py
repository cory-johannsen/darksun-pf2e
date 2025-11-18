"""Post-processor for Chapter 9 specific table fixes and content reordering.

Handles the "Bonus to AC Per Type of Piece" table extraction and reordering
to improve readability.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
import logging


class Chapter9TableFixer(BaseProcessor):
    """Fixes specific table issues in Chapter 9: Combat.
    
    Handles:
    - Bonus to AC Per Type of Piece table extraction and reconstruction
    - Table reordering to place it after Important Considerations section
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Fix Chapter 9 tables and content ordering.
        
        Args:
            input_data: Output from previous processor
            context: Execution context
            
        Returns:
            ProcessorOutput with fixed tables and reordered content
        """
        logger = logging.getLogger(__name__)
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        
        # Find the Chapter 9 combat section file
        chapter_9_file = None
        for file in sections_dir.glob("*chapter-nine-combat.json"):
            chapter_9_file = file
            break
        
        if not chapter_9_file or not chapter_9_file.exists():
            # Chapter 9 file not found, return unchanged
            logger.debug("Chapter 9 file not found, skipping chapter_9_table_fixes")
            return input_data
        
        logger.info(f"Processing Chapter 9 tables from {chapter_9_file.name}")
        
        # Load the section
        with open(chapter_9_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        # Apply all chapter 9 adjustments (including table reordering)
        from ..transformers import chapter_9_processing
        chapter_9_processing.apply_chapter_9_adjustments(section_data)
        
        # Save the modified data
        logger.debug(f"Saving modified Chapter 9 data to {chapter_9_file}")
        with open(chapter_9_file, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, ensure_ascii=False, indent=2)
        
        context.items_processed = 1
        
        return ProcessorOutput(
            data={"tables_fixed": 1},
            metadata={
                "chapter_9_tables_fixed": True,
                "file_updated": str(chapter_9_file)
            }
        )

