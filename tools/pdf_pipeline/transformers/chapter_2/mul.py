"""
Mul race specific processing for Chapter 2.

This module handles PDF-level adjustments for mul character race,
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


def process_mul_exertion_table(page: dict) -> None:
    """Process Mul Exertion Table on the Mul page."""
    # Find the "Mul Exertion Table" or "Type of Exertion" header
    match = find_block(page, lambda texts: any("Mul Exertion Table" in text or "Type of Exertion" in text for text in texts))
    if not match:
        return
    
    heading_idx, heading_block = match
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    y_min = heading_bbox[1] - 2.0
    
    # Find next section (Roleplaying)
    next_heading = find_block(page, lambda texts: any(text == "Roleplaying:" for text in texts))
    y_max = float(next_heading[1]["bbox"][1]) - 5.0 if next_heading else float(page.get("height", 0) or 0)
    
    # Collect all blocks in the table region
    table_blocks = []
    for idx in range(heading_idx, len(page.get("blocks", []))):
        if idx == heading_idx:
            continue  # Skip the heading itself
        block = page["blocks"][idx]
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        table_blocks.append(idx)
    
    if not table_blocks:
        return
    
    # Build the table manually based on expected structure
    # The table should have:
    # Header: Type of Exertion | Duration
    # Rows: Various exertion types with their durations
    rows = [
        ["Type of Exertion", "Duration"],
        ["Heavy Labor (stone construction, quarry work, running)", "8 hours"],
        ["Medium Labor (light construction, mining, jogging)", "16 hours"],
        ["Light Labor (combat training, walking encumbered)", "24 hours"],
        ["Normal Activity (walking, conversation)", "unlimited"],
    ]
    
    # Use the heading bbox as the table bbox
    bbox = [heading_bbox[0], heading_bbox[1], heading_bbox[2] + 200, y_max]
    
    # Create the table
    table = _table_from_rows(rows, header_rows=1, bbox=bbox)
    page.setdefault("tables", []).append(table)

    # If the Age headers are currently positioned above the Height & Weight table,
    # move the Age header group (Age, Starting Age, Aging Effects) to start after the table.
    age_match = find_block(page, lambda texts: any(text == "Age" for text in texts))
    if age_match:
        age_idx, age_block = age_match
        start_match = find_block(page, lambda texts: any("Starting Age" in t for t in texts))
        effects_match = find_block(page, lambda texts: any("Aging Effects" in t for t in texts))
        # Collect present blocks preserving their original order of appearance
        age_group: List[dict] = []
        for candidate in [age_block, start_match[1] if start_match else None, effects_match[1] if effects_match else None]:
            if candidate:
                age_group.append(candidate)
        if age_group:
            first_y0 = float(age_group[0].get("bbox", [0, 0, 0, 0])[1])
            table_bottom = float(bbox[3])
            # Only adjust if the age group currently begins above the table bottom
            if first_y0 <= table_bottom:
                new_base_top = table_bottom + 8.0
                for idx, blk in enumerate(age_group):
                    bx0, by0, bx1, by1 = [float(c) for c in blk.get("bbox", [0, 0, 0, 0])]
                    # Preserve original relative offset from the first age block
                    new_y0 = new_base_top + (by0 - first_y0)
                    new_y1 = new_base_top + (by1 - first_y0)
                    blk["bbox"] = [bx0, new_y0, bx1, new_y1]
                    # Shift all lines by the same delta
                    for line in blk.get("lines", []):
                        lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                        line_delta = new_y0 - by0
                        line["bbox"] = [lx0, ly0 + line_delta, lx1, ly1 + line_delta]
    
    # Clear the text blocks that were part of the table
    for idx in table_blocks:
        if idx < len(page["blocks"]):
            page["blocks"][idx]["lines"] = []




def force_mul_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Mul main section by splitting and marking blocks.
    
    The Mul section should have 8 paragraphs based on user-specified breaks.
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
            if (line_text.startswith("A full-grown mul stands") or
                line_text.startswith("Born as they are to lives of") or
                line_text.startswith("Many slave muls have either") or
                line_text.startswith("A player character mul may become") or
                line_text.startswith("A mul character adds two to") or
                line_text.startswith("Mules are able to") or
                line_text.startswith("Regardless of the preceding type")):
                
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




def force_mul_roleplaying_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Mul Roleplaying section by splitting and marking blocks.
    
    The Mul Roleplaying section should have 2 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts the second paragraph
        for line_idx, line in enumerate(lines):
            line_text = _normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph (user-specified)
            if line_text.startswith("Like their dwarven parent,") or line_text.startswith("Like their dwarven parent"):
                
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




