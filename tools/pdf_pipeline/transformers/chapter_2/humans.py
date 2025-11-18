"""
Humans race specific processing for Chapter 2.

This module handles PDF-level adjustments for humans character race,
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


def force_human_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Human section by splitting and marking blocks.
    
    The Human section should have 5 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = _normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph (user-specified breaks)
            if (line_text.startswith("An average human male stands between 6") or
                line_text.startswith("On Athas, centuries of abusive magic") or
                line_text.startswith("The children of humans") or
                line_text.startswith("As in other AD&D") or
                line_text.startswith("AsinotherAD")):  # Handle merged text
                
                # Split this block at this line
                if line_idx > 0:
                    first_part_lines = lines[:line_idx]
                    second_part_lines = lines[line_idx:]
                    
                    block["lines"] = first_part_lines
                    update_block_bbox(block)
                    
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    update_block_bbox(second_block)
                    
                    blocks_to_insert.append((idx + 1, second_block))
                    break
                else:
                    block["__force_paragraph_break"] = True
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




