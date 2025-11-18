"""
Thri-kreen race specific processing for Chapter 2.

This module handles PDF-level adjustments for thri-kreen character race,
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


def force_thri_kreen_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Thri-kreen main section by splitting and marking blocks.
    
    The Thri-kreen section should have 15 paragraphs based on user-specified breaks.
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
            if (line_text.startswith("The individual thri-kreen is a six-limbed creature") or
                line_text.startswith("A thri-kreens head has two large eyes") or
                line_text.startswith("Thri-kreen have no need of sleep") or
                line_text.startswith("Thri-kreen make and use a variety of weapons") or
                line_text.startswith("Thri-kreen can use most magical items such as") or
                line_text.startswith("The pack is the single unit of organization among") or
                line_text.startswith("Thri-kreen are carnivores and the pack is con") or
                line_text.startswith("Thri-kreen player characters can become clerics") or
                line_text.startswith("A thri-kreen has formidable natural attacks") or
                line_text.startswith("A thri-kreen can leap up and forward when he") or
                line_text.startswith("A thri-kreen can use a venomous saliva against") or
                line_text.startswith("A thri-kreen masters the use of the chatkcha") or
                line_text.startswith("A thri-kreen can dodge missiles fired at it on a roll") or
                line_text.startswith("Thri-kreen add one to their initial Wisdom score")):
                
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




def force_thri_kreen_roleplaying_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Thri-kreen Roleplaying section by splitting and marking blocks.
    
    The Thri-kreen Roleplaying section should have 4 paragraphs based on user-specified breaks.
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
            
            # Check if this line should start a new paragraph (user-specified)
            if (line_text.startswith("From birth, all thri-kreen are involved in the") or
                line_text.startswith("To outsiders, thri-kreen sometimes seem overly") or
                line_text.startswith("Their pack intelligence also makes them protect")):
                
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




