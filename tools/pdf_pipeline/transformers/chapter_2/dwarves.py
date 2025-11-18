"""
Dwarves race specific processing for Chapter 2.

This module handles PDF-level adjustments for dwarves character race,
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


def fix_dwarves_section_text_ordering(page2: dict) -> None:
    """Fix text ordering in the Dwarves section on page 2.
    
    The sentence "The task to which a dwarf is presently committed" appears at the end
    but should be at the beginning of the paragraph starting with "is referred to as his focus".
    The ending "for compromise in the mind of a dwarf." should be appended to the paragraph 
    ending with "There is very little room".
    """
    # First pass: Find the relevant blocks
    focus_start_block = None  # Block with "is referred to as his focus"
    focus_end_block = None  # Block with "There is very little room"
    duplicate_block_idx = None
    ending_line_to_append = None
    
    for block_idx, block in enumerate(page2.get("blocks", [])):
        if not block.get("lines"):
            continue
        
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            for line in block.get("lines", [])
        ]
        combined = " ".join(texts)
        
        # Find the focus start block
        if combined.startswith("is referred to as his focus") or any(text.startswith("is referred to as his focus") for text in texts):
            focus_start_block = block
        
        # Find the focus end block
        if "There is very little room" in combined:
            focus_end_block = block
        
        # Find the duplicate block with both phrases
        if "The task to which a dwarf is presently committed" in combined and "for compromise in the mind of a dwarf" in combined:
            duplicate_block_idx = block_idx
            # Extract the ending line
            for line in block.get("lines", []):
                line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                # Only save the line with "for compromise" (not the "The task" line)
                if "for compromise in the mind of a dwarf" in line_text and "The task to which a dwarf is presently committed" not in line_text:
                    ending_line_to_append = deepcopy(line)
                    break
    
    # Second pass: Modify the blocks
    if focus_start_block and focus_end_block and ending_line_to_append:
        # Prepend "The task to which a dwarf is presently committed " to the focus start block
        if focus_start_block.get("lines"):
            first_line = focus_start_block["lines"][0]
            first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
            
            if first_line_text.startswith("is referred to as his focus"):
                # Modify the first span of this line
                if first_line.get("spans"):
                    first_span = first_line["spans"][0]
                    original_text = first_span.get("text", "")
                    # Only prepend if it hasn't been done already
                    if not original_text.startswith("The task to which a dwarf"):
                        first_span["text"] = "The task to which a dwarf is presently committed " + original_text
        
        # Append "for compromise in the mind of a dwarf." to the focus end block
        focus_end_block["lines"].append(ending_line_to_append)
        update_block_bbox(focus_end_block)
    
    # Remove the duplicate block
    if duplicate_block_idx is not None and duplicate_block_idx < len(page2.get("blocks", [])):
        page2["blocks"].pop(duplicate_block_idx)




