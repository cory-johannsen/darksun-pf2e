"""
Warrior class (Fighter & Gladiator) specific processing for Chapter 3.

This module handles PDF-level adjustments for the Fighter and Gladiator classes,
including table extraction and paragraph break forcing.
"""

import re
from typing import List, Tuple, Dict, Optional
from .common import normalize_plain_text, update_block_bbox


def extract_fighters_followers_table(page: dict) -> None:
    """Extract the Fighters Followers table from page 25.
    
    The table has 4 columns (Char. Level, Stands, Level, Special) and 10 data rows (levels 11-20).
    The data is heavily fragmented and split across two regions:
    - Header and level 11: y=690-703 (bottom of page)
    - Levels 12-20: y=148-256 (top of page)
    
    Refactored to follow best practices - broken into focused helper functions.
    
    Args:
        page: Page 25 data dictionary
    """
    # Collect table spans
    table_data, blocks_to_clear = _collect_fighters_table_spans(page)
    
    # Reconstruct rows
    rows = _reconstruct_fighters_rows(table_data)
    
    # Build and attach table
    table = _build_fighters_table_structure(rows)
    _attach_fighters_table(page, table, blocks_to_clear)
    
    # Process legend entries
    _process_fighters_legend_entries(page)


def _collect_fighters_table_spans(page: dict) -> Tuple[Dict[int, List[dict]], List[int]]:
    """Collect text spans from the fragmented table regions.
    
    Args:
        page: Page data dictionary
        
    Returns:
        Tuple of (table_data dict, blocks_to_clear list)
    """
    table_data = {}
    blocks_to_clear = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            for line in block.get("lines", []):
                bbox = line.get("bbox", [])
                if bbox and len(bbox) >= 4:
                    y, x = bbox[1], bbox[0]
                    
                    # Define regions
                    in_table_region = _is_in_fighters_table_region(x, y)
                    in_legend_region = (270 < y < 410 and x > 300)
                    in_table_header_region = (670 < y < 680 and x > 50)
                    
                    if in_table_region:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                y_bucket = round(y)
                                if y_bucket not in table_data:
                                    table_data[y_bucket] = []
                                table_data[y_bucket].append({'text': text, 'x': x})
                        
                        # Mark block to clear if not in protected regions
                        if (not in_legend_region and not in_table_header_region 
                            and idx not in blocks_to_clear):
                            blocks_to_clear.append(idx)
    
    return table_data, blocks_to_clear


def _is_in_fighters_table_region(x: float, y: float) -> bool:
    """Check if coordinates are in the fighters table regions.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        True if in table region
    """
    in_header_region = (686 < y < 692 and 50 < x < 300)
    in_first_row_region = (700 < y < 708 and 50 < x < 300)
    in_data_region = (140 < y < 270 and x > 300)
    return in_header_region or in_first_row_region or in_data_region


def _reconstruct_fighters_rows(table_data: Dict[int, List[dict]]) -> List[List[str]]:
    """Reconstruct table rows from fragmented y-coordinate data.
    
    Args:
        table_data: Dictionary mapping y-coordinates to text spans
        
    Returns:
        List of row data (each row is a list of strings)
    """
    rows = []
    sorted_y = sorted(table_data.keys())
    
    i = 0
    while i < len(sorted_y):
        current_y = sorted_y[i]
        row_data = table_data[current_y][:]
        
        # Group adjacent y-coordinates (within 3 pixels)
        j = i + 1
        while j < len(sorted_y) and abs(sorted_y[j] - current_y) < 3:
            row_data.extend(table_data[sorted_y[j]])
            j += 1
        
        # Skip header row
        if 686 < current_y < 692:
            i = j
            continue
        
        # Sort by x and clean
        row_data.sort(key=lambda d: d['x'])
        row_texts = [d['text'] for d in row_data]
        cleaned_row = _clean_fighters_row(row_texts)
        
        rows.append(cleaned_row)
        i = j
    
    # Fix data quality issues and sort
    _fix_fighters_data_quality(rows)
    rows.sort(key=lambda r: int(r[0]) if r and r[0].isdigit() else 999)
    
    return rows


def _clean_fighters_row(row_texts: List[str]) -> List[str]:
    """Clean up row text by fixing dice notation and splitting merged columns.
    
    Args:
        row_texts: List of raw text strings from row
        
    Returns:
        Cleaned list of column values
    """
    # Remove spaces from dice notation and percentages
    cleaned_row = []
    for text in row_texts:
        if any(c in text for c in ['d', '+', '%']):
            text = text.replace(' ', '')
        cleaned_row.append(text)
    
    # Handle merged columns (3 columns → should be 4)
    if len(cleaned_row) == 3:
        cleaned_row = _split_fighters_merged_columns(cleaned_row)
    
    return cleaned_row


def _split_fighters_merged_columns(row: List[str]) -> List[str]:
    """Split merged columns in a fighters followers row.
    
    Args:
        row: Row with 3 columns
        
    Returns:
        Row with 4 columns (or original if no merge detected)
    """
    # Check if last column contains both level and special (dice + percentage)
    if 'd' in row[-1] and '%' in row[-1]:
        match = re.search(r'(1d\d+\+\d+)(\d+%)', row[-1])
        if match:
            return [row[0], row[1], match.group(1), match.group(2)]
    
    # Check if column 2 contains merged stands+level
    if 'd' in row[1] and len(row) == 3:
        match = re.search(r'(1d\d+\+\d+)(1d\d+\+\d+)', row[1])
        if match:
            return [row[0], match.group(1), match.group(2), row[2]]
    
    return row


def _fix_fighters_data_quality(rows: List[List[str]]) -> None:
    """Fix known data quality issues in fighters followers table.
    
    Args:
        rows: List of rows (modified in place)
    """
    for row in rows:
        if len(row) >= 1:
            # Fix spaced level numbers
            if row[0] == "1 1":
                row[0] = "11"
            elif row[0] == "1 7":
                row[0] = "17"
        
        # Fix misread level 19 (shows as 13 but has level 19 dice)
        if len(row) >= 2 and row[0] == "13" and row[1] == "1d20+8":
            row[0] = "19"


def _build_fighters_table_structure(rows: List[List[str]]) -> dict:
    """Build the table structure for rendering.
    
    Args:
        rows: List of cleaned row data
        
    Returns:
        Table dictionary
    """
    table_rows = [
        {
            "cells": [
                {"text": "Char. Level"},
                {"text": "Stands"},
                {"text": "Level"},
                {"text": "Special"}
            ]
        }
    ]
    
    # Add data rows
    for row in rows:
        if len(row) >= 4:
            table_rows.append({
                "cells": [
                    {"text": row[0]},
                    {"text": row[1]},
                    {"text": row[2]},
                    {"text": row[3]}
                ]
            })
        elif len(row) == 3:
            table_rows.append({
                "cells": [{"text": cell} for cell in row]
            })
    
    return {
        "type": "table",
        "bbox": [300, 140, 550, 270],
        "rows": table_rows,
        "header_rows": 1,
        "num_rows": len(table_rows),
        "num_cols": 4
    }


def _attach_fighters_table(page: dict, table: dict, blocks_to_clear: List[int]) -> None:
    """Attach table to page and clear fragmented blocks.
    
    Args:
        page: Page dictionary
        table: Table structure
        blocks_to_clear: List of block indices to clear
    """
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table)
    
    # Clear fragmented blocks
    for idx in blocks_to_clear:
        if idx < len(page.get("blocks", [])):
            page["blocks"][idx]["lines"] = []


def _process_fighters_legend_entries(page: dict) -> None:
    """Process legend entries by merging and styling them.
    
    Args:
        page: Page dictionary
    """
    legend_entries = ["Stands", "Level", "Special"]
    blocks = page.get("blocks", [])
    blocks_to_clear = []
    
    for legend_name in legend_entries:
        # Find legend main block
        legend_idx = _find_fighters_legend_block(blocks, legend_name)
        if legend_idx is None:
            continue
        
        # Collect full description
        full_description = _collect_fighters_legend_description(
            blocks, legend_idx, legend_name, legend_entries, blocks_to_clear
        )
        
        # Rebuild main block with styling
        _rebuild_fighters_legend_block(blocks[legend_idx], legend_name, full_description)
    
    # Clear continuation blocks
    for idx in blocks_to_clear:
        if idx < len(blocks):
            blocks[idx]["lines"] = []


def _find_fighters_legend_block(blocks: List[dict], legend_name: str) -> Optional[int]:
    """Find the block containing the legend header.
    
    Args:
        blocks: List of blocks
        legend_name: Name of legend entry
        
    Returns:
        Block index or None
    """
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        spans = lines[0].get("spans", [])
        if len(spans) >= 2 and spans[0].get("text", "").strip().startswith(legend_name):
            return idx
    
    return None


def _collect_fighters_legend_description(
    blocks: List[dict],
    legend_idx: int,
    legend_name: str,
    all_legend_names: List[str],
    blocks_to_clear: List[int]
) -> str:
    """Collect full legend description from main and continuation blocks.
    
    Args:
        blocks: List of blocks
        legend_idx: Index of legend main block
        legend_name: Current legend name
        all_legend_names: All legend entry names
        blocks_to_clear: List to append continuation block indices
        
    Returns:
        Full description text
    """
    main_block = blocks[legend_idx]
    parts = []
    
    # Get text from main block (skip first span = header)
    main_spans = main_block["lines"][0]["spans"]
    for span in main_spans[1:]:
        parts.append(span.get("text", "").strip())
    
    # Collect continuation blocks
    next_idx = legend_idx + 1
    while next_idx < len(blocks):
        next_block = blocks[next_idx]
        if next_block.get("type") != "text":
            break
        
        next_lines = next_block.get("lines", [])
        if not next_lines:
            next_idx += 1
            continue
        
        next_text = " ".join(
            " ".join(span.get("text", "") for span in line.get("spans", []))
            for line in next_lines
        ).strip()
        
        # Stop if hit another legend or unrelated content
        if any(other in next_text for other in all_legend_names if other != legend_name):
            break
        if next_text.startswith("It is") or next_text.startswith("A fighter"):
            break
        
        parts.append(next_text)
        blocks_to_clear.append(next_idx)
        next_idx += 1
    
    return " ".join(parts)


def _rebuild_fighters_legend_block(block: dict, legend_name: str, description: str) -> None:
    """Rebuild legend block with proper styling.
    
    Args:
        block: Block dictionary (modified in place)
        legend_name: Legend entry name
        description: Full description text
    """
    if not block.get("lines") or not block["lines"][0].get("spans"):
        return
    
    # Create combined span
    combined_text = f"{legend_name}: {description}"
    combined_span = {
        "text": combined_text,
        "size": 9.0,
        "color": "#000000",
        "font": "MSTT31c501",
        "__legend_entry": legend_name
    }
    
    block["lines"][0]["spans"] = [combined_span]
    update_block_bbox(block)
    block["__force_paragraph_break"] = True


def force_gladiator_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Gladiator section.
    
    The section should have 10 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    # Define the paragraph break points
    break_points = [
        "A gladiator who has a Strength score (his prime",
        "Gladiators can have any alignment: good, evil,",
        "A gladiator can use most magical items,",
        "Gladiators have the following special benefits:",
        "A gladiator is automatically proficient in all",
        "A gladiator can specialize in multiple weapons.",
        "A gladiator is an expert in unarmed",
        "A gladiator learns to optimize his armor when he",
        "A gladiator attracts followers when he reaches 9th"
    ]
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        # We need to handle multiple matches in the same block
        first_match_idx = None
        split_done = False
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line matches any break point
            should_break = any(line_text.startswith(bp) for bp in break_points)
            
            if should_break:
                if first_match_idx is None:
                    first_match_idx = line_idx
                    if line_idx == 0:
                        # Mark the block itself
                        block["__force_paragraph_break"] = True
                elif line_idx > first_match_idx:
                    # Found a second match - split here
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
                    split_done = True
                    break
        
        # If we found a match at line_idx > 0 but no second match, still split
        if first_match_idx is not None and first_match_idx > 0 and not split_done:
            first_part_lines = lines[:first_match_idx]
            second_part_lines = lines[first_match_idx:]
            
            block["lines"] = first_part_lines
            update_block_bbox(block)
            
            second_block = {
                "type": "text",
                "lines": second_part_lines,
                "__force_paragraph_break": True
            }
            update_block_bbox(second_block)
            
            blocks_to_insert.append((idx + 1, second_block))
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)


def force_fighter_benefits_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Fighter benefits section after the legend.
    
    The section should have 10 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    # Define the paragraph break points
    break_points = [
        "It is important to remember that these are merely",
        "A fighter has the following special benefits:",
        "A fighter can teach weapon proficiencies when he",
        "A fighter can operate heavy war machines when",
        "A fighter can supervise the construction of defenses",
        "A fighter can command large numbers of troops",
        "In BATTLESYSTEM",
        "A fighter can construct heavy war machines when",
        "In all cases where the rules here"
    ]
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line matches any break point
            should_break = any(line_text.startswith(bp) for bp in break_points)
            
            if should_break:
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


def force_fighter_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Fighter section by splitting and marking blocks.
    
    The Fighter section should have 7 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    # Define the paragraph break points
    # Note: "As the fighter gains each new level beyond the" is split across blocks 19-20,
    # but block 19 starts with this text, so marking it forces a new paragraph.
    # Block 20 ("10th, he will attract...") will continue in the same paragraph.
    break_points = [
        "Fighters can have any alignment, use magical",
        "As a fighter increases in experience levels, his rep",
        "Followers are always gained in groups of 10 indi",
        "Once a fighter reaches 10th level, he attracts his",
        "As the fighter gains each new level beyond the",
        "A fighter cannot avoid gaining followers. The"
    ]
    
    for idx, block in enumerate(list(page.get("blocks", []))):  # Use list() to avoid mutation issues
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line matches any break point
            should_break = any(line_text.startswith(bp) for bp in break_points)
            
            if should_break:
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
    
    # Special case: merge blocks where a sentence is split incompletely
    # Specifically, merge "As the fighter gains each new level beyond the" with "10th, he will attract..."
    blocks = page.get("blocks", [])
    blocks_to_remove = []
    for idx in range(len(blocks) - 1):
        block = blocks[idx]
        next_block = blocks[idx + 1]
        
        if block.get("type") != "text" or next_block.get("type") != "text":
            continue
        
        block_text = " ".join(
            normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ).strip()
        
        next_block_text = " ".join(
            normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in next_block.get("lines", [])
        ).strip()
        
        # Check if this is the specific case we need to merge
        if (block_text == "As the fighter gains each new level beyond the" and 
            next_block_text.startswith("10th")):
            # Merge next_block into block
            block["lines"].extend(next_block["lines"])
            update_block_bbox(block)
            blocks_to_remove.append(idx + 1)
    
    # Remove merged blocks (in reverse order to maintain indices)
    for idx in reversed(blocks_to_remove):
        page["blocks"].pop(idx)

