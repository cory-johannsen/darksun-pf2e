"""
Elves race specific processing for Chapter 2.

This module handles PDF-level adjustments for elves character race,
including text ordering, paragraph breaks, and special formatting.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List

from ..journal import (
    _normalize_plain_text,
    _collect_cells_from_blocks,
    _build_matrix_from_cells,
    _table_from_rows,
    _compute_bbox_from_cells,
)
from .common import update_block_bbox, find_block


def fix_elves_section_paragraph_breaks(page3: dict) -> None:
    """Fix paragraph breaks in the Elves section on page 3.
    
    The Elves section has 11 paragraphs but they get merged into 1 huge paragraph
    due to the two-column layout. We need to add paragraph break hints based on
    sentence endings that should start new paragraphs.
    """
    # The Elves section starts with specific sentences that should be paragraph breaks.
    # We'll mark these blocks to force paragraph breaks in the renderer.
    
    paragraph_starts = [
        "The dunes and steppes of Athas",  # Para 1
        "Elves are all brethren",  # Para 2
        "Individually, tribal elves",  # Para 3
        "Elves use no beasts",  # Para 4
        "While most elven tribes",  # Para 5
        "Elven culture",  # Para 6
        "A player character elf",  # Para 7
        "Elves are masterful warriors",  # Para 8
        "Elves gain a bonus to surprise",  # Para 9
        "Elves have no special knowledge",  # Para 10
        "With nimble fingers",  # Para 11
    ]
    
    # Find blocks that start these paragraphs and mark them
    for block in page3.get("blocks", []):
        if not block.get("lines"):
            continue
        
        # Check first line of block
        first_line = block["lines"][0]
        first_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
        
        # If this block starts with one of our paragraph starts, mark it
        for para_start in paragraph_starts:
            if first_text.startswith(para_start):
                # Add a marker to force paragraph break
                block["__force_paragraph_break"] = True
                break




def fix_elves_roleplaying_paragraph_breaks(page4: dict) -> None:
    """Fix paragraph breaks in the Roleplaying section after Elves on page 4.
    
    The Roleplaying section has 3 paragraphs but they get merged into 1.
    We need to force paragraph breaks at specific sentences.
    
    The 3 paragraphs should be:
    1. "Elves have no great love..."
    2. "When encountering outsiders...will be taking animal or magical transportation."
    3. "Elves never ride on beasts..."
    """
    paragraph_starts = [
        "When encountering outsiders",  # Para 2
        "Elves never ride on beasts",   # Para 3
    ]
    
    # Find the Roleplaying block and mark lines that should start new paragraphs
    for block in page4.get("blocks", []):
        if not block.get("lines"):
            continue
        
        # Check if this is the Roleplaying block (contains "Roleplaying:" at start)
        first_line = block["lines"][0]
        first_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
        
        if not first_text.startswith("Roleplaying:"):
            continue
        
        # Mark lines that should start new paragraphs
        for line in block["lines"]:
            line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            for para_start in paragraph_starts:
                if line_text.startswith(para_start):
                    # Mark this line to force a paragraph break
                    line["__force_line_break"] = True
                    break
            
            # Special handling: If a line contains "transportation." followed by other content,
            # split it at that point
            if "will be taking animal or magical transportation." in line_text:
                # Check if there's content after "transportation." in the same line
                if line_text.index("transportation.") + len("transportation.") < len(line_text) - 1:
                    # There's more content after "transportation." - need to split mid-line
                    # Mark this line for splitting at "transportation."
                    line["__split_at_transportation"] = True





