"""
Table processing functions for Chapter 2.

This module handles extraction and processing of tables from Chapter 2 (Player Character Races),
including ability adjustments, class limits, and language tables.
"""

from __future__ import annotations

from copy import deepcopy
from typing import List, Sequence

from ..journal import (
    _normalize_plain_text,
    _collect_cells_from_blocks,
    _build_matrix_from_cells,
    _table_from_rows,
    _compute_bbox_from_cells,
    _join_fragments,
)
from .common import update_block_bbox, find_block


def process_table_2_ability_adjustments(page0: dict) -> None:
    """Process Table 2: Ability Adjustments on page 0."""
    found = find_block(page0, lambda texts: any(text == "Table 2: Ability Adjustments" for text in texts))
    if not found:
        return
    
    heading_idx, heading_block = found
    next_heading = find_block(page0, lambda texts: any(text == "Racial Ability Requirements" for text in texts))
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    y_min = heading_bbox[1] - 2.0
    y_max = (
        float(next_heading[1]["bbox"][1]) - 2.0
        if next_heading
        else float(page0.get("height", 0) or 0)
    )
    x_min = heading_bbox[0] - 10.0
    x_max = heading_bbox[2] + 160.0
    table_blocks = []
    for idx, block in enumerate(page0.get("blocks", [])):
        if idx == heading_idx:
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if not block.get("lines"):
            continue
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        if bbox[0] < x_min or bbox[2] > x_max:
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page0, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=2, row_tolerance=4.0)
    allowed = {
        "Race",
        "Dwarf",
        "Elf",
        "Half-Elf",
        "Half-Giant",
        "Halfling",
        "Mul",
        "Thri-kreen",
    }
    merged_rows: List[List[str]] = []
    for row in rows:
        if not row:
            continue
        key = row[0]
        if key in allowed:
            merged_rows.append(row[:])
            continue
        if merged_rows and (not key or key == ""):
            value = row[1] if len(row) > 1 else ""
            if value:
                combined = _join_fragments([merged_rows[-1][1], value])
                merged_rows[-1][1] = combined
    filtered_rows = []
    for row in merged_rows:
        if not row:
            continue
        row[1] = row[1].rstrip(",")
        filtered_rows.append(row)
    if len(filtered_rows) >= 2:
        bbox = _compute_bbox_from_cells(cells)
        table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
        page0.setdefault("tables", []).append(table)
        for idx in table_blocks:
            page0["blocks"][idx]["lines"] = []




def process_racial_ability_requirements_table(page0: dict) -> None:
    """Process Racial Ability Requirements table on page 0."""
    header_match = find_block(
        page0,
        lambda texts: "Ability" in texts and {"Dwarf", "Elf", "H-Elf", "H-giant", "Halfling", "Mul", "Thri-kreen"}.issubset(set(texts)),
    )
    if not header_match:
        return
    
    header_idx, header_block = header_match
    header_bbox = [float(coord) for coord in header_block.get("bbox", [0, 0, 0, 0])]
    y_min = header_bbox[1] - 2.0
    y_max = float(page0.get("height", 0) or 0)
    table_blocks = []
    for idx in range(header_idx, len(page0.get("blocks", []))):
        block = page0["blocks"][idx]
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if idx != header_idx and any(text.startswith("Table ") for text in texts):
            break
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page0, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=8, row_tolerance=4.0)
    allowed = {
        "Ability",
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    }
    filtered_rows = [row for row in rows if row and row[0] in allowed]
    if len(filtered_rows) < 2:
        return
    
    bbox = _compute_bbox_from_cells(cells)
    page_width = float(page0.get("width", 0) or 0)
    column_width = (
        max(header_bbox[2] - header_bbox[0], (page_width / 2) - 20.0)
        if page_width
        else header_bbox[2] - header_bbox[0]
    )
    bbox[0] = header_bbox[0]
    bbox[2] = bbox[0] + column_width
    if page_width:
        bbox[2] = min(bbox[2], page_width - 10.0)
    bbox[1] = max(bbox[1], header_bbox[3] + 2.0)
    bbox[3] = max(bbox[3], bbox[1] + 4.0)
    table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
    page0.setdefault("tables", []).append(table)
    for idx in table_blocks:
        if idx == header_idx:
            continue
        page0["blocks"][idx]["lines"] = []

    cleanup_labels = {
        "Ability",
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
        "Dwarf",
        "Elf",
        "H-Elf",
        "H-giant",
        "Halfling",
        "Mul",
        "Thri-kreen",
    }
    # Reposition the Racial Ability Requirements table and header to come before Racial Ability Adjustments
    # Find the target positions
    racial_req_header_idx = None
    racial_adj_header_idx = None
    for idx, block in enumerate(page0.get("blocks", [])):
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if any(text == "Racial Ability Requirements" for text in texts):
            racial_req_header_idx = idx
        elif any(text == "Racial Ability Adjustments" for text in texts):
            racial_adj_header_idx = idx
    
    if racial_req_header_idx is not None and racial_adj_header_idx is not None:
        # Get the requirements header block
        req_header_block = page0["blocks"][racial_req_header_idx]
        req_header_bbox = [float(c) for c in req_header_block.get("bbox", [0, 0, 0, 0])]
        
        # Get the adjustments header block
        adj_header_block = page0["blocks"][racial_adj_header_idx]
        adj_header_bbox = [float(c) for c in adj_header_block.get("bbox", [0, 0, 0, 0])]
        
        # Calculate new position for requirements header (just above adjustments header)
        new_req_y = adj_header_bbox[1] - 20.0  # Place it 20 pixels above adjustments
        
        # Update requirements header position
        height = req_header_bbox[3] - req_header_bbox[1]
        req_header_block["bbox"] = [req_header_bbox[0], new_req_y, req_header_bbox[2], new_req_y + height]
        for line in req_header_block.get("lines", []):
            line_bbox = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            line_height = line_bbox[3] - line_bbox[1]
            line["bbox"] = [line_bbox[0], new_req_y, line_bbox[2], new_req_y + line_height]
        
        # Update the requirements table position if it exists
        for table in page0.get("tables", []):
            table_bbox = [float(c) for c in table.get("bbox", [0, 0, 0, 0])]
            # Identify requirements table by column count (8 columns)
            if table.get("rows") and len(table["rows"][0].get("cells", [])) == 8:
                table_height = table_bbox[3] - table_bbox[1]
                new_table_y = new_req_y + height + 4.0
                table["bbox"] = [table_bbox[0], new_table_y, table_bbox[2], new_table_y + table_height]
    
    # Sort tables on page 0 by Y-coordinate to ensure correct rendering order
    if page0.get("tables"):
        page0["tables"].sort(key=lambda t: float(t.get("bbox", [0, 0, 0, 0])[1]))
    
    for block in page0.get("blocks", []):
        lines = block.get("lines", [])
        if not lines:
            continue
        remaining = []
        for line in lines:
            text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            if text in cleanup_labels:
                continue
            remaining.append(line)
        if len(remaining) != len(lines):
            block["lines"] = remaining
            if remaining:
                update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]




def process_table_3_racial_class_limits(page1: dict) -> None:
    """Process Table 3: Racial Class And Level Limits on page 1."""
    match = find_block(
        page1,
        lambda texts: any(text == "Table 3: Racial Class And Level Limits" for text in texts),
    )
    if not match:
        return
    
    heading_idx, heading_block = match
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    page_width = float(page1.get("width", 0) or 0)
    y_min = heading_bbox[1] - 2.0

    def _is_footer_or_legend(texts: Sequence[str]) -> bool:
        """Check if this block is part of the table footer/legend."""
        if not texts:
            return False
        text_combined = " ".join(texts).lower()
        # Check for legend markers
        if any(texts[0].startswith(prefix) for prefix in ["U:", "Any #", "-:", "The Player"]):
            return True
        # Also check for partial legend text
        if "book gives rules for advancing" in text_combined:
            return True
        if "cannot belong to the listed class" in text_combined:
            return True
        if "player characters to 20th level" in text_combined:
            return True
        return False

    footer = None
    legend_blocks = []  # Track all legend/footer blocks
    for idx in range(heading_idx + 1, len(page1.get("blocks", []))):
        block = page1["blocks"][idx]
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if _is_footer_or_legend(texts):
            if footer is None:
                footer = block
            legend_blocks.append(idx)

    y_max = float(footer.get("bbox", [0, 0, 0, page1.get("height", 0) or 0])[1]) - 2.0 if footer else float(page1.get("height", 0) or 0)

    table_blocks = []
    for idx, block in enumerate(page1.get("blocks", [])):
        if idx < heading_idx:
            continue
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if idx != heading_idx and any(text.startswith("Table ") for text in texts):
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page1, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=9, row_tolerance=4.0)
    allowed = {
        "Class",
        "Bard",
        "Cleric",
        "Defiler",
        "Druid",
        "Fighter",
        "Gladiator",
        "Illusionist",
        "Preserver",
        "Psionicist",
        "Ranger",
        "Templar",
        "Thief",
    }
    filtered_rows = [row for row in rows if row and (row[0] in allowed)]
    if len(filtered_rows) < 2:
        return
    
    bbox = _compute_bbox_from_cells(cells)
    table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
    
    # Remove any existing incorrectly detected tables on this page
    # (borderless table detector may have found a malformed version)
    page1["tables"] = []
    
    page1.setdefault("tables", []).append(table)
    for idx in table_blocks:
        if idx == heading_idx:
            continue
        page1["blocks"][idx]["lines"] = []

    # Note: Legend blocks are NOT cleared here - they will be preserved in the output
    # and reordered by HTML post-processing to appear after the table.
    # Table 3 heading repositioning also removed to prevent it from being inserted
    # in the middle of the Languages intro paragraph.




def process_other_languages_table(page2: dict) -> None:
    """Process Other Languages table on page 2."""
    match = find_block(page2, lambda texts: any(text == "Other Languages" for text in texts))
    if not match:
        return
    
    heading_idx, heading_block = match
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    y_min = heading_bbox[1] - 2.0
    next_heading = find_block(page2, lambda texts: any(text == "Dwarves" for text in texts))
    y_max = float(next_heading[1]["bbox"][1]) - 2.0 if next_heading else float(page2.get("height", 0) or 0)

    table_blocks = []
    for idx in range(heading_idx + 1, len(page2.get("blocks", []))):
        block = page2["blocks"][idx]
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        width = bbox[2] - bbox[0]
        if width > 140.0:
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page2, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=2, row_tolerance=4.0)
    allowed_first = {
        "Aarakocra*",
        "Belgoi",
        "Ettercap",
        "Giant",
        "Goblin Spider",
        "Jozhal*",
        "Meazel",
        "Yuan-ti",
    }
    allowed_second = {
        "Anakore",
        "Braxat",
        "Genie*",
        "Gith",
        "Halfling",
        "Kenku*",
        "Thri-kreen",
    }
    filtered_rows = []
    for row in rows:
        if not row:
            continue
        if len(row) >= 2 and (row[0] in allowed_first or row[1] in allowed_second):
            filtered_rows.append(row)
    if filtered_rows:
        bbox = _compute_bbox_from_cells(cells)
        table = _table_from_rows(filtered_rows, header_rows=0, bbox=bbox)
        page2.setdefault("tables", []).append(table)
        for idx in table_blocks:
            page2["blocks"][idx]["lines"] = []




