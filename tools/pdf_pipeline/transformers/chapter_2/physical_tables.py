"""
Physical characteristic tables for Chapter 2.

This module handles extraction and processing of height, weight, age, and aging tables
for all player character races in Dark Sun.
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
    _join_fragments,
)
from .common import update_block_bbox, find_block


def process_height_weight_table(page: dict) -> None:
    """Process Height and Weight table programmatically (5 columns, 10 rows, 2 header rows).
    
    Structure:
      - Header row 1: "Race" (rowspan=2) | "Height in Inches" (colspan=2) | "Weight in Pounds" (colspan=2)
      - Header row 2: "Base" | "Modifier" | "Base" | "Modifier"
      - Data rows (8): One per race
    
    Refactored to follow best practices - broken into focused helper functions.
    """
    # Find section bounds
    bounds = _find_hw_table_bounds(page)
    if not bounds:
        return
    hw_bbox, y_min, y_max = bounds
    
    # Check if table already exists and reposition if needed
    if _reposition_existing_hw_table(page, hw_bbox, y_max):
        return
    
    # Extract header positions
    header_pos = _extract_hw_header_positions(page)
    if not header_pos:
        return
    race_x1, h_base_x, h_mod_x, w_base_x, w_mod_x = header_pos
    
    # Find row anchors  
    race_split_x = (race_x1 + min(h_base_x, h_mod_x)) / 2.0
    row_anchors = _collect_hw_row_anchors(page, y_min, y_max, race_split_x)
    if not row_anchors:
        return
    
    # Build table
    table = _build_hw_table(
        page, row_anchors, race_split_x, h_base_x, h_mod_x, w_base_x, w_mod_x,
        hw_bbox, y_max
    )
    
    # Clean up and attach
    _cleanup_hw_blocks(page, row_anchors, race_split_x, h_base_x, h_mod_x, w_base_x, w_mod_x, header_pos)
    page.setdefault("tables", []).append(table)


def _line_text(line: dict) -> str:
    """Extract normalized text from a line."""
    return _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()


def _find_hw_table_bounds(page: dict) -> tuple | None:
    """Find Height and Weight table section bounds.
    
    Args:
        page: Page dictionary
        
    Returns:
        Tuple of (hw_bbox, y_min, y_max) or None
    """
    hw_match = find_block(page, lambda texts: any("Height and Weight" in t for t in texts))
    if not hw_match:
        return None
    _, hw_block = hw_match
    hw_bbox = [float(c) for c in hw_block.get("bbox", [0, 0, 0, 0])]
    y_min = hw_bbox[3] + 2.0
    
    next_header = find_block(page, lambda texts: any(t in {"Age", "Starting Age"} for t in texts))
    y_max = float(next_header[1]["bbox"][1]) - 2.0 if next_header else float(page.get("height", 0) or 0)
    
    return hw_bbox, y_min, y_max


def _reposition_existing_hw_table(page: dict, hw_bbox: list, y_max: float) -> bool:
    """Reposition existing Height and Weight table if found.
    
    Args:
        page: Page dictionary
        hw_bbox: Header bounding box
        y_max: Maximum Y coordinate
        
    Returns:
        True if table was found and repositioned
    """
    for table in page.get("tables", []):
        rows = table.get("rows", [])
        if not rows:
            continue
        header_rows = int(table.get("header_rows", 0) or 0)
        if header_rows >= 2:
            first = rows[0].get("cells", [])
            if len(first) >= 3:
                texts = [c.get("text", "") for c in first]
                if any("Height in Inches" in t for t in texts) and any("Weight in Pounds" in t for t in texts):
                    _move_hw_table(page, table, hw_bbox, y_max)
                    return True
    return False


def _move_hw_table(page: dict, table: dict, hw_bbox: list, y_max: float) -> None:
    """Move existing Height and Weight table to correct position.
    
    Args:
        page: Page dictionary
        table: Table to reposition
        hw_bbox: Header bounding box
        y_max: Maximum Y coordinate
    """
    tb = [float(c) for c in table.get("bbox", [0, 0, 0, 0])]
    desired_top = hw_bbox[3] + 1.0
    height = max(4.0, tb[3] - tb[1])
    new_bottom = min(desired_top + height, y_max)
    
    page_width = float(page.get("width", 0) or 612.0)
    table["bbox"] = [0.0, desired_top, page_width, new_bottom]
    
    # Move Age header group and footnotes
    y_min = hw_bbox[3] + 2.0
    _move_age_group_below_table(page, new_bottom)
    _move_footnotes_below_table(page, y_min, new_bottom)


def _move_age_group_below_table(page: dict, table_bottom: float) -> None:
    """Move Age header group below the table if needed.
    
    Args:
        page: Page dictionary
        table_bottom: Bottom Y coordinate of table
    """
    age_match = find_block(page, lambda texts: any(text == "Age" for text in texts))
    if not age_match:
        return
    
    _, age_block = age_match
    start_match = find_block(page, lambda texts: any("Starting Age" in t for t in texts))
    effects_match = find_block(page, lambda texts: any("Aging Effects" in t for t in texts))
    age_group = [b for b in [age_block, start_match[1] if start_match else None, effects_match[1] if effects_match else None] if b]
    
    if not age_group:
        return
    
    first_y0 = float(age_group[0].get("bbox", [0, 0, 0, 0])[1])
    if first_y0 > table_bottom:
        return
    
    base_top = table_bottom + 8.0
    for blk in age_group:
        bx0, by0, bx1, by1 = [float(c) for c in blk.get("bbox", [0, 0, 0, 0])]
        new_y0 = base_top + (by0 - first_y0)
        new_y1 = base_top + (by1 - first_y0)
        blk["bbox"] = [bx0, new_y0, bx1, new_y1]
        for line in blk.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            delta = new_y0 - by0
            line["bbox"] = [lx0, ly0 + delta, lx1, ly1 + delta]


def _move_footnotes_below_table(page: dict, y_min: float, table_bottom: float) -> None:
    """Move footnote blocks below the table.
    
    Args:
        page: Page dictionary
        y_min: Minimum Y coordinate of table section
        table_bottom: Bottom Y coordinate of table
    """
    footnote_blocks: List[dict] = []
    for blk in page.get("blocks", []):
        if blk.get("type") != "text":
            continue
        bx0, by0, bx1, by1 = [float(c) for c in blk.get("bbox", [0, 0, 0, 0])]
        if by0 < y_min or by0 > table_bottom:
            continue
        
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in ln.get("spans", []))).strip()
            for ln in blk.get("lines", [])
        ]
        if any(t.startswith("*") for t in texts if t):
            footnote_blocks.append(blk)
    
    if not footnote_blocks:
        return
    
    foot_y = table_bottom + 4.0
    for blk in footnote_blocks:
        bx0, by0, bx1, by1 = [float(c) for c in blk.get("bbox", [0, 0, 0, 0])]
        height = by1 - by0
        delta = foot_y - by0
        blk["bbox"] = [bx0, foot_y, bx1, foot_y + height]
        for line in blk.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            line["bbox"] = [lx0, ly0 + delta, lx1, ly1 + delta]
        foot_y += height + 2.0


def _extract_hw_header_positions(page: dict) -> tuple | None:
    """Extract column x-positions from table headers.
    
    Args:
        page: Page dictionary
        
    Returns:
        Tuple of (race_x1, h_base_x, h_mod_x, w_base_x, w_mod_x) or None
    """
    left_header = find_block(page, lambda texts: any("Height in Inches" in t for t in texts))
    right_header = find_block(page, lambda texts: any("Weight in Pounds" in t for t in texts))
    if not left_header or not right_header:
        return None
    
    _, left_block = left_header
    _, right_block = right_header
    
    race_x1 = None
    h_base_x = None
    h_mod_x = None
    w_base_x = None
    w_mod_x = None
    
    for line in left_block.get("lines", []):
        txt = _line_text(line)
        x0, _, x1, _ = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
        cx = (x0 + x1) / 2.0
        if txt == "Race":
            race_x1 = x1
        elif txt == "Base":
            h_base_x = cx
        elif txt == "Modifier":
            h_mod_x = cx
    
    for line in right_block.get("lines", []):
        txt = _line_text(line)
        x0, _, x1, _ = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
        cx = (x0 + x1) / 2.0
        if txt == "Base":
            if w_base_x is None:
                w_base_x = cx
        elif txt == "Modifier":
            if w_mod_x is None:
                w_mod_x = cx
    
    if any(v is None for v in [race_x1, h_base_x, h_mod_x, w_base_x, w_mod_x]):
        return None
    
    return race_x1, h_base_x, h_mod_x, w_base_x, w_mod_x


def _collect_hw_row_anchors(page: dict, y_min: float, y_max: float, race_split_x: float) -> List[tuple[float, str]]:
    """Collect and merge row anchors from race column.
    
    Args:
        page: Page dictionary
        y_min: Minimum Y coordinate
        y_max: Maximum Y coordinate
        race_split_x: X coordinate separating race column
        
    Returns:
        List of (y_center, race_name) tuples
    """
    row_anchors: List[tuple[float, str]] = []
    footnote_prefix = "*"
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if y0 < y_min or y0 > y_max:
                continue
            if x1 <= race_split_x:
                txt = _line_text(line)
                if not txt or txt in {"Race"} or txt.startswith(footnote_prefix):
                    continue
                row_anchors.append((((y0 + y1) / 2.0), txt))
    
    if not row_anchors:
        return []
    
    # Deduplicate anchors by proximity
    row_anchors.sort(key=lambda a: a[0])
    merged_anchors: List[tuple[float, str]] = []
    y_tol = 3.5
    
    for y_c, txt in row_anchors:
        if not merged_anchors:
            merged_anchors.append((y_c, txt))
            continue
        last_y, last_txt = merged_anchors[-1]
        if abs(y_c - last_y) <= y_tol:
            merged_anchors[-1] = (min(y_c, last_y), _join_fragments([last_txt, txt]))
        else:
            merged_anchors.append((y_c, txt))
    
    return merged_anchors


def _build_hw_table(
    page: dict, row_anchors: List[tuple[float, str]], race_split_x: float,
    h_base_x: float, h_mod_x: float, w_base_x: float, w_mod_x: float,
    hw_bbox: list, y_max: float
) -> dict:
    """Build complete Height and Weight table structure.
    
    Args:
        page: Page dictionary
        row_anchors: List of (y_center, race_name) tuples
        race_split_x: X coordinate separating race column
        h_base_x, h_mod_x, w_base_x, w_mod_x: Column x positions
        hw_bbox: Header bounding box
        y_max: Maximum Y coordinate
        
    Returns:
        Complete table dictionary
    """
    # Find header blocks for bbox calculation
    left_block = find_block(page, lambda texts: any("Height in Inches" in t for t in texts))[1]
    right_block = find_block(page, lambda texts: any("Weight in Pounds" in t for t in texts))[1]
    
    # Build rows
    data_rows = _build_hw_data_rows(page, row_anchors, h_base_x, h_mod_x, w_base_x, w_mod_x)
    if not data_rows:
        return {}
    
    # Compute bbox
    bbox = _compute_hw_table_bbox(
        page, row_anchors, left_block, right_block,
        h_base_x, h_mod_x, w_base_x, w_mod_x, race_split_x,
        hw_bbox, y_max
    )
    
    # Build final table
    header_row_1 = {
        "cells": [
            {"text": "Race", "rowspan": 2},
            {"text": "Height in Inches", "colspan": 2},
            {"text": "Weight in Pounds", "colspan": 2},
        ]
    }
    header_row_2 = {
        "cells": [
            {"text": "Base"},
            {"text": "Modifier"},
            {"text": "Base"},
            {"text": "Modifier"},
        ]
    }
    
    table_rows = [header_row_1, header_row_2] + data_rows
    page_width = float(page.get("width", 0) or 612.0)
    
    return {
        "rows": table_rows,
        "header_rows": 2,
        "bbox": [0.0, bbox[1], page_width, bbox[3]],
    }


def _build_hw_data_rows(
    page: dict, row_anchors: List[tuple[float, str]],
    h_base_x: float, h_mod_x: float, w_base_x: float, w_mod_x: float
) -> List[dict]:
    """Build data rows for Height and Weight table.
    
    Args:
        page: Page dictionary
        row_anchors: List of (y_center, race_name) tuples
        h_base_x, h_mod_x, w_base_x, w_mod_x: Column x positions
        
    Returns:
        List of row dictionaries
    """
    data_rows: List[dict] = []
    y_tol = 3.5
    
    def _find_near(x_target: float, y_center: float) -> str:
        best_txt = ""
        best_dx = 1e9
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                if abs(((y0 + y1) / 2.0) - y_center) > y_tol:
                    continue
                cx = (x0 + x1) / 2.0
                dx = abs(cx - x_target)
                if dx < best_dx:
                    txt = _line_text(line)
                    if txt in {"Race", "Base", "Modifier", "Height in Inches", "Weight in Pounds"}:
                        continue
                    best_dx = dx
                    best_txt = txt
        return best_txt
    
    for y_c, race_txt in row_anchors:
        row_cells = [
            {"text": race_txt},
            {"text": _find_near(h_base_x, y_c)},
            {"text": _find_near(h_mod_x, y_c)},
            {"text": _find_near(w_base_x, y_c)},
            {"text": _find_near(w_mod_x, y_c)},
        ]
        populated = sum(1 for c in row_cells if c.get("text", "").strip())
        if populated >= 3:
            data_rows.append({"cells": row_cells})
    
    return data_rows


def _compute_hw_table_bbox(
    page: dict, row_anchors: List[tuple[float, str]], left_block: dict, right_block: dict,
    h_base_x: float, h_mod_x: float, w_base_x: float, w_mod_x: float, race_split_x: float,
    hw_bbox: list, y_max: float
) -> list:
    """Compute table bounding box from header blocks and data lines.
    
    Args:
        page: Page dictionary
        row_anchors: List of (y_center, race_name) tuples
        left_block, right_block: Header blocks
        h_base_x, h_mod_x, w_base_x, w_mod_x: Column x positions
        race_split_x: X coordinate separating race column
        hw_bbox: Header bounding box
        y_max: Maximum Y coordinate
        
    Returns:
        Bounding box [x0, y0, x1, y1]
    """
    x_values: List[float] = []
    y_values: List[float] = []
    y_tol = 3.5
    
    # Header blocks
    for blk in (left_block, right_block):
        bx0, by0, bx1, by1 = [float(c) for c in blk.get("bbox", [0, 0, 0, 0])]
        x_values.extend([bx0, bx1])
        y_values.extend([by0, by1])
    
    # Data blocks
    x_targets = [h_base_x, h_mod_x, w_base_x, w_mod_x]
    for y_c, _ in row_anchors:
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                if abs(((y0 + y1) / 2.0) - y_c) > y_tol:
                    continue
                cx = (x0 + x1) / 2.0
                if any(abs(cx - xt) <= 40.0 for xt in x_targets) or x1 <= race_split_x:
                    x_values.extend([x0, x1])
                    y_values.extend([y0, y1])
    
    if not x_values or not y_values:
        bbox = [0.0, hw_bbox[3] + 1.0, float(page.get("width", 612.0) or 612.0), y_max]
    else:
        desired_top = hw_bbox[3] + 1.0
        table_height = max(4.0, max(y_values) - min(y_values))
        bbox = [
            min(x_values),
            desired_top,
            max(x_values),
            min(desired_top + table_height, y_max)
        ]
    
    return bbox


def _cleanup_hw_blocks(
    page: dict, row_anchors: List[tuple[float, str]], race_split_x: float,
    h_base_x: float, h_mod_x: float, w_base_x: float, w_mod_x: float,
    header_pos: tuple
) -> None:
    """Clean up blocks that were converted into the table.
    
    Args:
        page: Page dictionary
        row_anchors: List of (y_center, race_name) tuples
        race_split_x: X coordinate separating race column
        h_base_x, h_mod_x, w_base_x, w_mod_x: Column x positions
        header_pos: Header position tuple
    """
    # Clear header blocks
    left_header = find_block(page, lambda texts: any("Height in Inches" in t for t in texts))
    right_header = find_block(page, lambda texts: any("Weight in Pounds" in t for t in texts))
    if left_header:
        left_header[1]["lines"] = []
    if right_header:
        right_header[1]["lines"] = []
    
    # Clear duplicate race/value fragments
    y_tol = 3.5
    footnote_prefix = "*"
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        remaining = []
        for line in block.get("lines", []):
            txt = _line_text(line)
            if not txt:
                continue
            if txt.startswith(footnote_prefix):
                remaining.append(line)
                continue
            
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            y_c = (y0 + y1) / 2.0
            cx = (x0 + x1) / 2.0
            
            close_to_col = (
                x1 <= race_split_x or
                abs(cx - h_base_x) <= 40.0 or
                abs(cx - h_mod_x) <= 40.0 or
                abs(cx - w_base_x) <= 40.0 or
                abs(cx - w_mod_x) <= 40.0
            )
            in_row = any(abs(y_c - ry) <= y_tol for ry, _ in row_anchors)
            
            if close_to_col and in_row:
                continue
            remaining.append(line)
        
        if len(remaining) != len(block.get("lines", [])):
            block["lines"] = remaining
            update_block_bbox(block) if remaining else block.update({"bbox": [0.0, 0.0, 0.0, 0.0]})




def process_starting_age_table(page: dict) -> None:
    """Process Starting Age table programmatically (4 columns, 2 header rows).
    
    Structure:
      - Header row 1: Race (rowspan=2) | Starting Age (colspan=2) | Maximum Age Range (Base + Variable) (rowspan=2)
      - Header row 2: Base Age | Variable
      - Data rows (8): race rows
    
    Refactored to follow best practices - broken into focused helper functions.
    """
    # Find section bounds
    bounds = _find_age_table_bounds(page)
    if not bounds:
        return
    start_block, y_min, y_max = bounds
    
    # Check if table already exists
    if _handle_existing_age_table(page, y_min, y_max):
        return
    
    # Extract column positions
    col_positions = _extract_age_column_positions(page)
    if not col_positions:
        return
    base_age_cx, start_var_cx, base_plus_cx, race_split_x = col_positions
    
    # Collect row anchors
    unique_y = _collect_age_row_anchors(page, y_min, y_max, base_age_cx)
    if not unique_y:
        return
    
    # Build data rows
    data_rows = _build_age_data_rows(
        page, unique_y, race_split_x, base_age_cx,
        start_var_cx, base_plus_cx, y_min, y_max
    )
    if not data_rows:
        return
    
    # Build and attach table
    table = _build_age_table_structure(
        data_rows, start_block, page, y_min, y_max, unique_y
    )
    _attach_age_table(page, table, y_min, y_max)
    
    # Clean up blocks
    _cleanup_age_table_blocks(
        page, data_rows, y_min, y_max, base_age_cx,
        start_var_cx, base_plus_cx, race_split_x, unique_y
    )


def _find_age_table_bounds(page: dict) -> tuple | None:
    """Find Starting Age table section bounds.
    
    Args:
        page: Page dictionary
        
    Returns:
        Tuple of (start_block, y_min, y_max) or None
    """
    start_match = find_block(page, lambda texts: any("Starting Age" in t for t in texts))
    if not start_match:
        return None
    _, start_block = start_match
    y_min = float(start_block.get("bbox", [0, 0, 0, 0])[3]) + 2.0
    end_match = find_block(page, lambda texts: any("Aging Effects" in t for t in texts))
    y_max = float(end_match[1]["bbox"][1]) - 2.0 if end_match else float(page.get("height", 0) or 0)
    return start_block, y_min, y_max


def _handle_existing_age_table(page: dict, y_min: float, y_max: float) -> bool:
    """Check for and handle existing Starting Age table.
    
    Args:
        page: Page dictionary
        y_min: Minimum Y coordinate
        y_max: Maximum Y coordinate
        
    Returns:
        True if existing table was found and handled
    """
    existing_table = None
    for table in page.get("tables", []):
        rows = table.get("rows", [])
        if not rows:
            continue
        header_rows = int(table.get("header_rows", 0) or 0)
        if header_rows >= 1:
            header_cells = [c.get("text", "") for c in rows[0].get("cells", [])]
            header_joined = " ".join(header_cells)
            if ("Base Age" in header_joined and "Variable" in header_joined) and (
                "Max Age Range (Base + Variable)" in header_joined or "Maximum Age Range" in header_joined
            ):
                existing_table = table
                break
    
    if not existing_table:
        return False
    
    # Derive race names from table
    races = []
    for r in existing_table.get("rows", [])[1:]:
        cells = r.get("cells", [])
        if cells and isinstance(cells[0], dict):
            name = (cells[0].get("text") or "").strip()
            if name:
                races.append(name)
    _cleanup_age_labels_and_aggregates(page, y_min, y_max, races)
    return True


def _cleanup_age_labels_and_aggregates(page: dict, y_min: float, y_max: float, existing_race_names: list[str] | None = None) -> None:
    """Clean up header labels and aggregated race list lines.
    
    Args:
        page: Page dictionary
        y_min: Minimum Y coordinate
        y_max: Maximum Y coordinate
        existing_race_names: List of race names from existing table
    """
    header_labels = {"Race", "Base Age", "Variable", "(Base + Variable)", "Maximum Age Range"}
    lower_race_names = set(n.lower() for n in (existing_race_names or []))
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        remaining = []
        changed = False
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if y0 <= y_min or y0 >= y_max:
                remaining.append(line)
                continue
            txt = _line_text(line)
            # Remove simple header labels
            if txt in header_labels:
                changed = True
                continue
            # Remove aggregated race list line
            if lower_race_names:
                tlow = txt.lower()
                matches = sum(1 for rn in lower_race_names if rn and rn in tlow)
                if matches >= 3:
                    changed = True
                    continue
            remaining.append(line)
        if changed:
            block["lines"] = remaining
            if remaining:
                update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]


def _extract_age_column_positions(page: dict) -> tuple | None:
    """Extract column x-positions for Starting Age table.
    
    Args:
        page: Page dictionary
        
    Returns:
        Tuple of (base_age_cx, start_var_cx, base_plus_cx, race_split_x) or None
    """
    base_age_block = find_block(page, lambda texts: any("Base Age" in t for t in texts))
    base_plus_block = find_block(page, lambda texts: any("(Base + Variable)" in t for t in texts))
    if not base_age_block or not base_plus_block:
        return None
    
    def _line_center_for(block: dict, target: str) -> float | None:
        for line in block.get("lines", []):
            txt = _line_text(line)
            if txt == target:
                x0, _, x1, _ = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                return (x0 + x1) / 2.0
        return None
    
    base_age_cx = _line_center_for(base_age_block[1], "Base Age")
    base_plus_cx = _line_center_for(base_plus_block[1], "(Base + Variable)")
    if base_age_cx is None or base_plus_cx is None:
        return None
    
    start_var_cx = (base_age_cx + base_plus_cx) / 2.0
    race_split_x = min(base_age_cx, start_var_cx) - 20.0
    
    return base_age_cx, start_var_cx, base_plus_cx, race_split_x


def _collect_age_row_anchors(page: dict, y_min: float, y_max: float, base_age_cx: float) -> List[float]:
    """Collect row anchors by finding base age integers.
    
    Args:
        page: Page dictionary
        y_min: Minimum Y coordinate
        y_max: Maximum Y coordinate
        base_age_cx: Base age column x position
        
    Returns:
        List of unique Y positions
    """
    y_tol = 3.5
    anchors: List[tuple[float, dict]] = []
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if y0 <= y_min or y0 >= y_max:
                continue
            cx = (x0 + x1) / 2.0
            if abs(cx - base_age_cx) <= 40.0:
                txt = _line_text(line)
                if txt.isdigit():
                    anchors.append((((y0 + y1) / 2.0), line))
    
    if not anchors:
        return []
    
    anchors.sort(key=lambda a: a[0])
    # Deduplicate by y
    unique_y: List[float] = []
    for y_c, _ in anchors:
        if not unique_y or all(abs(y_c - y_prev) > y_tol for y_prev in unique_y):
            unique_y.append(y_c)
    
    return unique_y


def _build_age_data_rows(
    page: dict, unique_y: List[float], race_split_x: float,
    base_age_cx: float, start_var_cx: float, base_plus_cx: float,
    y_min: float, y_max: float
) -> List[dict]:
    """Build data rows for Starting Age table.
    
    Args:
        page: Page dictionary
        unique_y: List of unique Y positions
        race_split_x: X coordinate separating race column
        base_age_cx, start_var_cx, base_plus_cx: Column x positions
        y_min, y_max: Section bounds
        
    Returns:
        List of row dictionaries
    """
    data_rows: List[dict] = []
    
    for y_c in unique_y:
        race = _find_age_race(page, y_c, race_split_x)
        base_age = _find_age_near(page, base_age_cx, y_c, accept_pattern=r"^\d{1,3}$")
        var = _find_age_variable(page, y_c, base_age_cx, base_plus_cx, start_var_cx)
        max_range = _find_age_near(page, base_plus_cx, y_c, accept_pattern=r"^\d+\s*\+\s*\d+d\d+|-$", x_window=60.0)
        
        # Only include rows that have at least race and max_range
        if race and max_range:
            data_rows.append({"cells": [{"text": race}, {"text": base_age}, {"text": var}, {"text": max_range}]})
    
    return data_rows


def _find_age_race(page: dict, y_center: float, race_split_x: float) -> str:
    """Find race name for a row.
    
    Args:
        page: Page dictionary
        y_center: Row Y position
        race_split_x: X coordinate separating race column
        
    Returns:
        Race name or empty string
    """
    y_tol = 3.5
    best = ""
    best_x = 1e9
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if abs(((ly0 + ly1) / 2.0) - y_center) > y_tol:
                continue
            if lx1 >= race_split_x:
                continue
            txt = _line_text(line)
            if not txt or txt in {"Race"}:
                continue
            # Prefer the leftmost text
            if lx0 < best_x:
                best_x = lx0
                best = txt
    
    return best


def _find_age_near(page: dict, x_target: float, y_center: float, *, accept_pattern: str | None = None, x_window: float | None = 40.0) -> str:
    """Find text near target position with optional pattern matching.
    
    Args:
        page: Page dictionary
        x_target: Target X position
        y_center: Target Y position
        accept_pattern: Optional regex pattern to match
        x_window: Maximum X distance
        
    Returns:
        Matching text or empty string
    """
    y_tol = 3.5
    best_txt = ""
    best_dx = 1e9
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if abs(((ly0 + ly1) / 2.0) - y_center) > y_tol:
                continue
            cx = (lx0 + lx1) / 2.0
            dx = abs(cx - x_target)
            if x_window is not None and dx > x_window:
                continue
            if dx < best_dx:
                txt = _line_text(line)
                if not txt:
                    continue
                if accept_pattern:
                    import re
                    if not re.search(accept_pattern, txt):
                        continue
                best_dx = dx
                best_txt = txt
    
    return best_txt


def _find_age_variable(page: dict, y_c: float, base_age_cx: float, base_plus_cx: float, start_var_cx: float) -> str:
    """Find variable column value (e.g., '1d4').
    
    Args:
        page: Page dictionary
        y_c: Row Y position
        base_age_cx: Base age column X position
        base_plus_cx: Base + variable column X position
        start_var_cx: Variable column center estimate
        
    Returns:
        Variable value or empty string
    """
    y_tol = 3.5
    var = ""
    import re as _re
    best_dx = 1e9
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if abs(((ly0 + ly1) / 2.0) - y_c) > y_tol:
                continue
            cx = (lx0 + lx1) / 2.0
            # Only consider candidates between the two major columns
            if not (base_age_cx + 10.0 <= cx <= base_plus_cx - 10.0):
                continue
            txt = _line_text(line)
            if _re.match(r"^\d+d\d+$", txt):
                dx = abs(cx - start_var_cx)
                if dx < best_dx:
                    best_dx = dx
                    var = txt
    
    return var


def _build_age_table_structure(
    data_rows: List[dict], start_block: dict, page: dict,
    y_min: float, y_max: float, unique_y: List[float]
) -> dict:
    """Build complete Starting Age table structure.
    
    Args:
        data_rows: List of data rows
        start_block: Starting Age header block
        page: Page dictionary
        y_min, y_max: Section bounds
        unique_y: List of row Y positions
        
    Returns:
        Complete table dictionary
    """
    header_row = {
        "cells": [
            {"text": "Race"},
            {"text": "Base Age"},
            {"text": "Variable"},
            {"text": "Max Age Range (Base + Variable)"},
        ]
    }
    table_rows = [header_row] + data_rows
    
    # Compute bbox
    base_age_block = find_block(page, lambda texts: any("Base Age" in t for t in texts))[1]
    base_plus_block = find_block(page, lambda texts: any("(Base + Variable)" in t for t in texts))[1]
    
    col_xs = [
        float(base_age_block["bbox"][0]), float(base_age_block["bbox"][2]),
        float(base_plus_block["bbox"][0]), float(base_plus_block["bbox"][2]),
    ]
    x_left = max(0.0, min(col_xs) - 8.0)
    x_right = min(float(page.get("width", 612.0) or 612.0), max(col_xs) + 8.0)
    
    start_y = float(start_block.get("bbox", [0, 0, 0, 0])[3]) + 6.0
    last_row_y = max(unique_y) if unique_y else start_y + 20.0
    end_y = min(y_max, last_row_y + 18.0)
    
    page_width = float(page.get("width", 0) or 612.0)
    bbox = [0.0, start_y, page_width, end_y]
    
    return {"rows": table_rows, "header_rows": 1, "bbox": bbox}


def _attach_age_table(page: dict, table: dict, y_min: float, y_max: float) -> None:
    """Remove old tables and attach new Starting Age table.
    
    Args:
        page: Page dictionary
        table: Table to attach
        y_min, y_max: Section bounds
    """
    # Remove any pre-existing malformed tables in this section
    cleaned_tables = []
    for t in page.get("tables", []):
        tb = [float(c) for c in t.get("bbox", [0, 0, 0, 0])]
        ty0, ty1 = tb[1], tb[3]
        # Keep tables that are clearly outside the section
        if ty1 < y_min - 5.0 or ty0 > y_max + 5.0:
            cleaned_tables.append(t)
    page["tables"] = cleaned_tables
    page.setdefault("tables", []).append(table)


def _cleanup_age_table_blocks(
    page: dict, data_rows: List[dict], y_min: float, y_max: float,
    base_age_cx: float, start_var_cx: float, base_plus_cx: float,
    race_split_x: float, unique_y: List[float]
) -> None:
    """Clean up blocks used to build the table.
    
    Args:
        page: Page dictionary
        data_rows: List of data rows
        y_min, y_max: Section bounds
        base_age_cx, start_var_cx, base_plus_cx: Column x positions
        race_split_x: X coordinate separating race column
        unique_y: List of row Y positions
    """
    y_tol = 3.5
    
    # Remove header label lines
    header_labels = {"Race", "Base Age", "Variable", "(Base + Variable)", "Maximum Age Range"}
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        remaining = []
        changed = False
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if y0 <= y_min or y0 >= y_max:
                remaining.append(line)
                continue
            txt = _line_text(line)
            if txt in header_labels:
                changed = True
                continue
            remaining.append(line)
        if changed:
            block["lines"] = remaining
            if remaining:
                update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    # Remove duplicate row fragments
    x_targets = [base_age_cx, start_var_cx, base_plus_cx]
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        remaining = []
        changed = False
        for line in block.get("lines", []):
            lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            y_center = (ly0 + ly1) / 2.0
            if y_center <= y_min or y_center >= y_max:
                remaining.append(line)
                continue
            # Check proximity to any column center or race area
            cx = (lx0 + lx1) / 2.0
            close_to_col = any(abs(cx - xt) <= 40.0 for xt in x_targets) or lx1 <= race_split_x
            in_row = any(abs(y_center - ry) <= y_tol for ry in unique_y)
            if close_to_col and in_row:
                changed = True
                continue
            remaining.append(line)
        if changed:
            block["lines"] = remaining
            if remaining:
                update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    # Remove aggregated race-list lines
    extracted_race_names = {row["cells"][0]["text"] for row in data_rows if row.get("cells") and row["cells"][0].get("text")}
    extracted_race_names_lower = {name.lower() for name in extracted_race_names}
    if extracted_race_names_lower:
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            remaining = []
            changed = False
            for line in block.get("lines", []):
                x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                if y0 <= y_min or y0 >= y_max:
                    remaining.append(line)
                    continue
                txt = _line_text(line).lower()
                if not txt:
                    remaining.append(line)
                    continue
                # Count how many distinct race names appear in this line
                matches = sum(1 for rn in extracted_race_names_lower if rn and rn in txt)
                if matches >= 3:
                    changed = True
                    continue
                remaining.append(line)
            if changed:
                block["lines"] = remaining
                if remaining:
                    update_block_bbox(block)
                else:
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]
