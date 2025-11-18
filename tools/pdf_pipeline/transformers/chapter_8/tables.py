"""
Table extraction and processing for Chapter 8.

This module handles extraction and processing of experience award tables,
including both class-specific and race-specific tables.
"""

from __future__ import annotations

import logging
import re
from typing import List, Tuple, Optional

from .common import (
    normalize_plain_text,
    update_block_bbox,
    is_class_award_header,
    is_race_award_header,
    is_column_header,
    is_xp_value,
    clean_xp_text,
)

logger = logging.getLogger(__name__)

def _build_block_info_from_page(page: dict, page_num: int) -> list:
    """Build list of text blocks with spatial information.
    
    Processes each line separately to avoid combining column headers with table headers.
    
    Args:
        page: Page dictionary
        page_num: Page number
        
    Returns:
        list: Block info dictionaries with spatial data
    """
    blocks = page.get("blocks", [])
    block_info = []
    
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        x0, y0, x1, y1 = bbox
        
        # Process each line separately - lines have their own bounding boxes!
        for line_idx, line in enumerate(lines):
            line_texts = []
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    line_texts.append(text)
            
            if line_texts:
                combined_text = " ".join(line_texts)
                line_bbox = line.get("bbox", bbox)
                line_x0, line_y0, line_x1, line_y1 = line_bbox
                
                is_legend = combined_text.strip().startswith("*")
                block_info.append({
                    "block_idx": idx,
                    "text": combined_text,
                    "x": line_x0,
                    "y": line_y0,
                    "width": line_x1 - line_x0,
                    "height": line_y1 - line_y0,
                    "bbox": line_bbox,
                    "is_header": is_class_award_header(combined_text),
                    "is_column_header": is_column_header(combined_text),
                    "is_xp": is_xp_value(combined_text),
                    "is_legend": is_legend,
                })
    
    return block_info

def _find_class_awards_section(block_info: list, page_num: int) -> Optional[int]:
    """Find the start of Individual Class Awards section.
    
    Args:
        block_info: List of block information
        page_num: Page number
        
    Returns:
        int or None: Index of section start, or None if not found
    """
    section_start = None
    
    for i, info in enumerate(block_info):
        if "Individual Class Awards" in info["text"]:
            section_start = i
            logger.info(f"Found 'Individual Class Awards' section at index {i}")
            break
        
        # On pages without the section header, start if we find a class header
        if info["is_header"] and section_start is None:
            section_start = max(0, i - 1)
            logger.info(f"Found class award header '{info['text']}' at index {i}, starting extraction from index {section_start}")
            break
    
    if section_start is None:
        logger.info("No 'Individual Class Awards' section or class headers found on this page")
    
    return section_start

def _determine_column_boundary(table_items: list) -> float:
    """Determine column boundary based on leftmost item X-coordinate.
    
    Args:
        table_items: List of table items
        
    Returns:
        float: Column boundary (120 for left column, 380 for right)
    """
    min_x = min(item["x"] for item in table_items) if table_items else 100
    return 120 if min_x < 200 else 380

def _complete_legend_entry(legend_lines: list) -> dict:
    """Complete a legend entry by combining lines.
    
    Args:
        legend_lines: List of legend line dicts
        
    Returns:
        dict: Legend entry
    """
    combined_text = " ".join(line["text"] for line in legend_lines)
    return {
        "text": combined_text,
        "x": legend_lines[0]["x"],
        "y": legend_lines[0]["y"],
        "block_idx": legend_lines[0]["block_idx"],
    }

def _finalize_current_table(current_table: str, table_items: list, tables: list, block_idx: int, page_num: int) -> None:
    """Finalize current table and add to tables list.
    
    Args:
        current_table: Table header name
        table_items: List of table items
        tables: List to append table to
        block_idx: Block index
        page_num: Page number
    """
    if not current_table or not table_items:
        return
    
    boundary = _determine_column_boundary(table_items)
    rows = pair_table_columns(table_items, boundary)
    tables.append({
        "header": current_table,
        "rows": rows,
        "block_idx": block_idx,
    })
    logger.info(f"Completed table '{current_table}' with {len(rows)} rows (col boundary={boundary})")

def extract_tables_from_page(page: dict, page_num: int) -> None:
    """Extract tables from a specific page using spatial layout.
    
    Refactored to follow best practices - broken into focused helper functions.
    
    Args:
        page: Page dictionary
        page_num: Page number
    """
    blocks = page.get("blocks", [])
    if not blocks:
        return
    
    logger.info(f"Processing page {page_num} with {len(blocks)} blocks for table extraction")
    
    # Build spatial block information
    block_info = _build_block_info_from_page(page, page_num)
    
    # Sort by Y-coordinate for page 1+ (Psionicist table needs Y-sorting)
    if page_num > 0:
        block_info = sorted(block_info, key=lambda x: x["y"])
    
    # Find section start
    section_start = _find_class_awards_section(block_info, page_num)
    if section_start is None:
        return
    
    # Initialize state
    tables = []
    current_table = None
    current_table_column_x = 0
    table_items = []
    legend_entries = []
    collecting_legend = False
    current_legend_lines = []
    
    # Determine loop start
    loop_start = section_start if (section_start < len(block_info) and 
                                     block_info[section_start].get("is_header")) else section_start + 1
    
    # Process blocks
    for i in range(loop_start, len(block_info)):
        info = block_info[i]
        text = info["text"]
        
        # Handle class award header (start new table)
        if info["is_header"]:
            # Save any collecting legend
            if collecting_legend and current_legend_lines:
                legend_entries.append(_complete_legend_entry(current_legend_lines))
                logger.info(f"Completed legend entry")
                collecting_legend = False
                current_legend_lines = []
            
            # Finalize previous table
            _finalize_current_table(current_table, table_items, tables, info["block_idx"], page_num)
            
            # Start new table
            current_table = text
            current_table_column_x = info["x"]
            table_items = []
            logger.info(f"Starting new table: {current_table} at x={current_table_column_x:.1f}")
            continue
        
        # Skip column headers and page numbers
        if info["is_column_header"]:
            continue
        if text.strip().isdigit() and len(text.strip()) <= 3:
            continue
        
        # Handle legend entries
        if info.get("is_legend") and (page_num == 0 or info["x"] < 300):
            # Finish any collecting legend
            if collecting_legend and current_legend_lines:
                legend_entries.append(_complete_legend_entry(current_legend_lines))
                logger.info(f"Completed legend entry")
                current_legend_lines = []
            
            # Finalize table before legend
            if current_table and table_items:
                _finalize_current_table(current_table, table_items, tables, info["block_idx"], page_num)
                current_table = None
                table_items = []
            
            # Start collecting legend
            collecting_legend = True
            current_legend_lines.append(info)
            logger.info(f"Started collecting legend entry: {text[:50]}...")
            continue
        
        # Check for section end
        if page_num > 0:
            stop_at_section = (info["x"] < 300) and (("Individual Class Awards" in text) or ("Individual Race Awards" in text))
        else:
            stop_at_section = ("Individual Class Awards" in text)
        
        if stop_at_section:
            # Finish legend if collecting
            if collecting_legend and current_legend_lines:
                legend_entries.append(_complete_legend_entry(current_legend_lines))
                logger.info(f"Completed legend entry at section end")
                collecting_legend = False
                current_legend_lines = []
            
            # Finalize last table
            _finalize_current_table(current_table, table_items, tables, info["block_idx"], page_num)
            current_table = None
            table_items = []
            break
        
        # Collect legend continuation
        if collecting_legend:
            if info["x"] < 300:
                current_legend_lines.append(info)
                logger.debug(f"Collected legend continuation: {text[:40]}...")
                continue
        
        # Collect table items
        if current_table:
            item_x = info["x"]
            # Column filtering
            if page_num == 0:
                same_column = True
            else:
                same_column = (current_table_column_x < 300 and item_x < 300) or \
                             (current_table_column_x >= 300 and item_x >= 300)
            
            if same_column:
                table_items.append(info)
    
    # Finalize any remaining state
    if collecting_legend and current_legend_lines:
        legend_entries.append(_complete_legend_entry(current_legend_lines))
        logger.info(f"Completed legend entry at end of loop")
    
    if current_table and table_items:
        _finalize_current_table(current_table, table_items, tables, len(blocks), page_num)
    
    logger.info(f"Extracted {len(tables)} tables from page {page_num}")
    logger.info(f"Collected {len(legend_entries)} legend entries")
    
    # Insert tables back into blocks
    insert_tables_into_blocks(page, tables, legend_entries, block_info, page_num)


def pair_table_columns(items: List[dict], column_boundary: float) -> List[List[str]]:
    """Pair action and award columns based on spatial layout.
    
    Args:
        items: List of text items with spatial information
        column_boundary: X-coordinate separating left and right columns
        
    Returns:
        List of [action, award] pairs
    """
    # Separate into left (action) and right (awards) columns
    left_items = [item for item in items if item["x"] < column_boundary]
    right_items = [item for item in items if item["x"] >= column_boundary]
    
    # Sort by y-coordinate
    left_items.sort(key=lambda x: x["y"])
    right_items.sort(key=lambda x: x["y"])
    
    # Merge consecutive right items that are close together
    merged_right = []
    if right_items:
        current_award_group = [right_items[0]]
        for i in range(1, len(right_items)):
            prev = right_items[i-1]
            curr = right_items[i]
            y_gap = curr["y"] - prev["y"]
            
            # Check if current has matching action
            curr_has_action = any(abs(left["y"] - curr["y"]) < 5 for left in left_items)
            
            # Merge if very close or moderately close without action
            should_merge = y_gap < 5 or (y_gap < 14 and not curr_has_action)
            
            if should_merge:
                current_award_group.append(curr)
            else:
                # Group complete
                merged_text = " ".join(item["text"] for item in current_award_group)
                merged_text = clean_xp_text(merged_text)
                merged_right.append({
                    "text": merged_text,
                    "y": current_award_group[0]["y"],
                    "x": current_award_group[0]["x"],
                })
                current_award_group = [curr]
        
        # Last group
        if current_award_group:
            merged_text = " ".join(item["text"] for item in current_award_group)
            merged_text = clean_xp_text(merged_text)
            merged_right.append({
                "text": merged_text,
                "y": current_award_group[0]["y"],
                "x": current_award_group[0]["x"],
            })
    
    right_items = merged_right
    
    # Group consecutive left items into multi-line actions
    action_groups = []
    current_group = []
    
    for i, left in enumerate(left_items):
        if not current_group:
            current_group = [left]
            continue
        
        last_y = current_group[-1]["y"]
        y_gap = left["y"] - last_y
        
        # Check if current group has matching award
        has_matching_award = any(abs(right["y"] - last_y) < 5 for right in right_items)
        
        # Split if large gap or has award with moderate gap
        should_split = y_gap > 20 or (has_matching_award and y_gap > 10)
        
        if should_split:
            action_groups.append(current_group)
            current_group = [left]
        else:
            current_group.append(left)
    
    if current_group:
        action_groups.append(current_group)
    
    # Match action groups to awards
    rows = []
    used_right = set()
    
    for action_group in action_groups:
        last_y = action_group[-1]["y"]
        
        # Find closest award
        best_match = None
        best_distance = float('inf')
        
        for right_idx, right in enumerate(right_items):
            if right_idx in used_right:
                continue
            
            y_distance = abs(right["y"] - last_y)
            
            if y_distance < 5 and y_distance < best_distance:
                best_distance = y_distance
                best_match = right_idx
        
        action_text = " ".join(item["text"] for item in action_group)
        
        if best_match is not None:
            rows.append([action_text, right_items[best_match]["text"]])
            used_right.add(best_match)
        else:
            rows.append([action_text, ""])
    
    # Add unmatched awards
    for right_idx, right in enumerate(right_items):
        if right_idx not in used_right:
            rows.append(["", right["text"]])
    
    return rows


def insert_tables_into_blocks(page: dict, tables: List[dict], legend_entries: List[dict], block_info: List[dict], page_num: int = 0) -> None:
    """Insert extracted tables and legend entries back into page blocks."""
    if not tables:
        return
    
    blocks = page.get("blocks", [])
    
    # Find insertion point
    insert_idx = None
    header_block_idx = None
    
    if page_num == 0:
        # Look for "Individual Class Awards" header
        for idx, block in enumerate(blocks):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if "Individual Class Awards" in span.get("text", ""):
                        header_block_idx = idx
                        insert_idx = idx + 1
                        break
                if insert_idx:
                    break
            if insert_idx:
                break
        
        if insert_idx is None:
            logger.warning("Could not find insertion point for tables on page 0")
            return
    else:
        # Page 1+: Insert at beginning
        insert_idx = 0
        header_block_idx = None
    
    # Find suppression endpoint
    suppress_until_idx = None
    for idx in range(insert_idx, len(blocks)):
        block = blocks[idx]
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if "Individual Race Awards" in span.get("text", ""):
                    suppress_until_idx = idx
                    logger.info(f"Found 'Individual Race Awards' at block {idx}")
                    break
            if suppress_until_idx:
                break
        if suppress_until_idx:
            break
    
    if suppress_until_idx is None:
        suppress_until_idx = len(blocks)
    
    # Mark header as H1
    if header_block_idx is not None:
        blocks[header_block_idx]["__render_as_h1"] = True
        blocks[header_block_idx]["__header_text"] = "Individual Class Awards"
        logger.info(f"Marking 'Individual Class Awards' at block {header_block_idx} as H1")
    
    # Get base Y for tables
    if header_block_idx is not None and header_block_idx < len(blocks):
        header_bbox = blocks[header_block_idx].get("bbox", [42.0, 100.0, 400.0, 120.0])
        base_y = header_bbox[1] + 20
    else:
        base_y = blocks[0].get("bbox", [42.0, 100.0, 400.0, 120.0])[1] if blocks else 100.0
    
    # Insert table markers
    insertion_point = header_block_idx + 1 if header_block_idx is not None else insert_idx
    
    for table_idx, table in enumerate(tables):
        table_y = base_y + (table_idx * 100)
        table_block = {
            "type": "text",
            "bbox": [42.0, table_y, 400.0, table_y + 20.0],
            "__class_award_table": True,
            "__table_header": table["header"],
            "__table_rows": table["rows"],
            "lines": [],
        }
        
        blocks.insert(insertion_point + table_idx, table_block)
        logger.info(f"Inserted table marker for '{table['header']}' at index {insertion_point + table_idx}")
    
    # Attach legend entries to Psionicist table (page 1 only)
    if legend_entries and page_num == 1:
        psionicist_table_idx = insertion_point + len(tables) - 1
        if psionicist_table_idx < len(blocks):
            blocks[psionicist_table_idx]["__legend_entries"] = [entry["text"] for entry in legend_entries]
            logger.info(f"Attached {len(legend_entries)} legend entries to Psionicist table")
    
    # Suppress original blocks
    suppress_start = insertion_point + len(tables)
    suppress_end = suppress_until_idx + len(tables)
    
    for idx in range(suppress_start, suppress_end):
        if idx < len(blocks):
            blocks[idx]["__skip_render"] = True
    
    logger.info(f"Suppressed {suppress_end - suppress_start} blocks from {suppress_start} to {suppress_end-1}")
    
    page["blocks"] = blocks


def extract_race_tables_from_page(page: dict, page_num: int) -> None:
    """Extract race award tables from a specific page."""
    blocks = page.get("blocks", [])
    if not blocks:
        return
    
    logger.info(f"Processing page {page_num} for race award tables with {len(blocks)} blocks")
    
    # Build block info (including __skip_render blocks)
    block_info = []
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        
        for line_idx, line in enumerate(lines):
            line_texts = []
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text:
                    line_texts.append(text)
            
            if line_texts:
                combined_text = " ".join(line_texts)
                line_bbox = line.get("bbox", bbox)
                line_x0, line_y0, line_x1, line_y1 = line_bbox
                
                block_info.append({
                    "block_idx": idx,
                    "text": combined_text,
                    "x": line_x0,
                    "y": line_y0,
                    "width": line_x1 - line_x0,
                    "height": line_y1 - line_y0,
                    "bbox": line_bbox,
                    "is_header": is_race_award_header(combined_text),
                    "is_column_header": is_column_header(combined_text),
                    "is_xp": is_xp_value(combined_text),
                })
    
    # Find "Individual Race Awards" section
    section_start = None
    for i, info in enumerate(block_info):
        if "Individual Race Awards" in info["text"]:
            section_start = i
            logger.info(f"Found 'Individual Race Awards' section at index {i}")
            break
        if info["is_header"] and section_start is None:
            section_start = max(0, i - 1)
            logger.info(f"Found race award header '{info['text']}' at index {i}")
            break
    
    if section_start is None:
        logger.info("No 'Individual Race Awards' section found")
        return
    
    # Process blocks for race tables
    tables = []
    current_table = None
    current_table_column_x = 0
    table_items = []
    skip_next_as_continuation = False
    
    loop_start = section_start if (section_start < len(block_info) and 
                                     block_info[section_start].get("is_header")) else section_start + 1
    
    for i in range(loop_start, len(block_info)):
        info = block_info[i]
        text = info["text"]
        
        # Skip footnote continuations
        if skip_next_as_continuation:
            skip_next_as_continuation = False
            if text and text[0].islower() and "XP" not in text:
                continue
        
        # Handle race award header
        if info["is_header"]:
            # Finalize previous table
            if current_table and table_items:
                is_table_in_right_column = current_table_column_x >= 300
                table_column_boundary = 380 if is_table_in_right_column else 120
                rows = pair_table_columns(table_items, table_column_boundary)
                tables.append({
                    "header": current_table,
                    "rows": rows,
                    "block_idx": info["block_idx"],
                })
                logger.info(f"Completed race table '{current_table}' with {len(rows)} rows")
            
            # Start new table
            current_table = text
            current_table_column_x = info["x"]
            table_items = []
            logger.info(f"Starting new race table: {current_table} at x={current_table_column_x:.1f}")
            continue
        
        # Skip column headers and page numbers
        if info["is_column_header"]:
            continue
        if text.strip().isdigit() and len(text.strip()) <= 3:
            continue
        
        # Skip footnotes
        if text.strip().startswith("*"):
            skip_next_as_continuation = True
            continue
        
        # Check for section end
        stop_at_section = False
        if "Individual Class Awards" in text and info["x"] >= 300:
            stop_at_section = True
        elif "roleplaying revolves" in text.lower():
            stop_at_section = True
        
        if stop_at_section:
            # Finalize last table
            if current_table and table_items:
                is_table_in_right_column = current_table_column_x >= 300
                table_column_boundary = 380 if is_table_in_right_column else 120
                rows = pair_table_columns(table_items, table_column_boundary)
                tables.append({
                    "header": current_table,
                    "rows": rows,
                    "block_idx": info["block_idx"],
                })
                logger.info(f"Completed final race table '{current_table}' with {len(rows)} rows")
                current_table = None
                table_items = []
            break
        
        # Collect items for current table
        if current_table:
            item_x = info["x"]
            is_table_in_right_column = current_table_column_x >= 300
            same_column = (item_x >= 300) if is_table_in_right_column else (item_x < 300)
            
            if same_column:
                table_items.append(info)
    
    # Finalize pending table
    if current_table and table_items:
        is_table_in_right_column = current_table_column_x >= 300
        table_column_boundary = 380 if is_table_in_right_column else 120
        rows = pair_table_columns(table_items, table_column_boundary)
        tables.append({
            "header": current_table,
            "rows": rows,
            "block_idx": len(blocks),
        })
        logger.info(f"Completed final race table '{current_table}' with {len(rows)} rows")
    
    logger.info(f"Extracted {len(tables)} race award tables from page {page_num}")
    
    # Insert race tables
    insert_race_tables_into_blocks(page, tables, block_info, page_num)


def insert_race_tables_into_blocks(page: dict, tables: List[dict], block_info: List[dict], page_num: int = 0) -> None:
    """Insert extracted race award tables back into page blocks."""
    if not tables:
        return
    
    blocks = page.get("blocks", [])
    
    # Find "Individual Race Awards" header
    insert_idx = None
    header_block_idx = None
    header_bbox = None
    
    for idx, block in enumerate(blocks):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if "Individual Race Awards" in span.get("text", ""):
                    header_block_idx = idx
                    insert_idx = idx + 1
                    header_bbox = block.get("bbox")
                    break
            if insert_idx:
                break
        if insert_idx:
            break
    
    if insert_idx is None:
        logger.warning("Could not find insertion point for race award tables")
        return
    
    # Mark header as H1
    if header_block_idx is not None:
        blocks[header_block_idx]["__render_as_h1"] = True
        blocks[header_block_idx]["__header_text"] = "Individual Race Awards"
        logger.info(f"Marking 'Individual Race Awards' at block {header_block_idx} as H1")
    
    # Determine column
    if header_bbox:
        header_x = header_bbox[0]
        is_right_column = header_x >= 300
        base_x = header_x
        base_y = header_bbox[1] + 20
        width = 250.0
    else:
        is_right_column = False
        base_x = 42.0
        base_y = 411.0
        width = 250.0
    
    # Insert table markers
    insertion_point = insert_idx
    
    for table_idx, table in enumerate(tables):
        table_y = base_y + (table_idx * 5)
        table_block = {
            "type": "text",
            "bbox": [base_x, table_y, base_x + width, table_y + 20.0],
            "__class_award_table": True,
            "__table_header": table["header"],
            "__table_rows": table["rows"],
            "lines": [],
        }
        
        blocks.insert(insertion_point + table_idx, table_block)
        logger.info(f"Inserted race table marker for '{table['header']}' at index {insertion_point + table_idx}")
    
    # Find suppression endpoint
    suppress_until_idx = None
    found_class_header = False
    
    for idx in range(insert_idx, len(blocks)):
        block = blocks[idx]
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                
                if "Individual Class Awards" in text and not found_class_header:
                    found_class_header = True
                    continue
                
                if found_class_header:
                    if ("Fighter:" in text or "The fighters" in text.lower() or 
                        "The cleric" in text.lower() or "roleplaying revolves" in text.lower()):
                        suppress_until_idx = idx
                        break
            if suppress_until_idx:
                break
        if suppress_until_idx:
            break
    
    if suppress_until_idx is None:
        suppress_until_idx = len(blocks)
    
    # Suppress blocks (preserve footnotes and class awards header)
    suppress_start = insertion_point + len(tables)
    suppress_end = suppress_until_idx
    
    suppressed_count = 0
    for idx in range(suppress_start, suppress_end):
        if idx < len(blocks):
            block = blocks[idx]
            should_preserve = False
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text.startswith("*") or "Individual Class Awards" in text:
                        should_preserve = True
                        break
                if should_preserve:
                    break
            
            if not should_preserve:
                blocks[idx]["__skip_render"] = True
                suppressed_count += 1
            else:
                logger.info(f"NOT suppressing block at index {idx}")
    
    logger.info(f"Suppressed {suppressed_count} race award blocks from {suppress_start} to {suppress_end-1}")
    
    page["blocks"] = blocks
