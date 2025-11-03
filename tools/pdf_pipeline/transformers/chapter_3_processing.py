"""
Chapter 3 (Player Character Classes) specific processing.

This module contains all the PDF-level adjustments for the chapter-three-player-character-classes section.
"""

from copy import deepcopy
from typing import Optional
import re


def _normalize_plain_text(text: str) -> str:
    """Normalize text by replacing special characters."""
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u2018', "'")  # Left single quotation mark
    text = text.replace('\u201c', '"')  # Left double quotation mark
    text = text.replace('\u201d', '"')  # Right double quotation mark
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--')  # Em dash
    text = text.replace('\xad', '')  # Soft hyphen
    text = text.replace('\x92', '')  # PRIVATE USE TWO control character (appears in "Fighter\x92s Followers")
    text = text.replace('\x99', ' ')  # SINGLE CHARACTER INTRODUCER control character (appears in "DARK SUN\x99campaign")
    return text


def _mark_ranger_description_blocks(pages: list) -> None:
    """Mark blocks in the Ranger section to prevent premature paragraph splitting.
    
    The Ranger description on pages 27-28 is heavily fragmented due to hyphenation.
    We need to mark these blocks so they merge more aggressively during rendering.
    """
    if len(pages) <= 7:
        return
    
    # Pages 27-28 (indices 6-7) contain the Ranger section
    for page_idx in [6, 7]:
        if page_idx >= len(pages):
            continue
        
        page = pages[page_idx]
        found_ranger_header = False
        found_followers_header = False
        
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            # Check if this block contains "Ranger" header or "RANGERS FOLLOWERS"
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                line_text_clean = _normalize_plain_text(line_text).strip()
                
                if "Ranger" in line_text_clean and len(line_text_clean) < 20:
                    found_ranger_header = True
                    block["__ranger_header"] = True
                
                if "RANGERS FOLLOWERS" in line_text_clean:
                    found_followers_header = True
                    block["__followers_header"] = True
                    break
            
            # Mark blocks between Ranger header and Rangers Followers as special
            # These should not auto-split paragraphs as aggressively
            if found_ranger_header and not found_followers_header:
                # Check if block looks like body text (not a table, not a header)
                has_regular_text = False
                for line in block.get("lines", []):
                    line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                    if len(line_text) > 20:  # Long enough to be body text
                        has_regular_text = True
                        break
                
                if has_regular_text:
                    block["__ranger_description"] = True


def _update_block_bbox(block: dict) -> None:
    """Update a block's bounding box based on its lines."""
    if not block.get("lines"):
        return
    
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    
    for line in block["lines"]:
        bbox = line.get("bbox", [0, 0, 0, 0])
        min_x = min(min_x, bbox[0])
        min_y = min(min_y, bbox[1])
        max_x = max(max_x, bbox[2])
        max_y = max(max_y, bbox[3])
    
    block["bbox"] = [min_x, min_y, max_x, max_y]


def _find_block(page: dict, predicate) -> Optional[tuple[int, dict]]:
    """Find a block that matches the given predicate."""
    for idx, block in enumerate(page.get("blocks", [])):
        if predicate(block):
            return (idx, block)
    return None


def _extract_fighters_followers_table(page: dict) -> None:
    """Extract the Fighters Followers table from page 25.
    
    The table has 4 columns (Char. Level, Stands, Level, Special) and 10 data rows (levels 11-20).
    The data is heavily fragmented and split across two regions:
    - Header and level 11: y=690-703 (bottom of page)
    - Levels 12-20: y=148-256 (top of page)
    
    Args:
        page: Page 25 data dictionary
    """
    # Collect all text spans in the table areas
    # We need TWO y-ranges because the table wraps from bottom to top of the page
    table_data = {}
    blocks_to_clear = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            for line in block.get("lines", []):
                bbox = line.get("bbox", [])
                if bbox and len(bbox) >= 4:
                    y = bbox[1]
                    x = bbox[0]
                    # Table data is in TWO regions:
                    # 1. Header row at x=56-236, y=690-691 (left side, bottom)
                    # 2. First data row (level 11) at x=58-178, y=703 (left side, bottom)  
                    # 3. Remaining data rows (12-20) at x=321-501, y=148-256 (right side, top)
                    
                    in_header_region = (686 < y < 692 and 50 < x < 300)
                    in_first_row_region = (700 < y < 708 and 50 < x < 300)
                    in_data_region = (140 < y < 270 and x > 300)
                    in_legend_region = (270 < y < 410 and x > 300)  # Legend text, don't clear
                    in_table_header_region = (670 < y < 680 and x > 50)  # "Fighters Followers" header, don't clear
                    
                    if in_header_region or in_first_row_region or in_data_region:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                y_bucket = round(y)
                                if y_bucket not in table_data:
                                    table_data[y_bucket] = []
                                table_data[y_bucket].append({'text': text, 'x': x})
                        # Mark this block to be cleared ONLY if not in legend or table header region
                        if not in_legend_region and not in_table_header_region and idx not in blocks_to_clear:
                            blocks_to_clear.append(idx)
    
    # Reconstruct rows by grouping adjacent y-coordinates and sorting by x
    rows = []
    sorted_y = sorted(table_data.keys())
    
    # Group y-coordinates that are within 3 pixels (same row)
    i = 0
    while i < len(sorted_y):
        current_y = sorted_y[i]
        row_data = table_data[current_y][:]
        
        # Check if next y is part of same row
        j = i + 1
        while j < len(sorted_y) and abs(sorted_y[j] - current_y) < 3:
            row_data.extend(table_data[sorted_y[j]])
            j += 1
        
        # Skip the header row (y=690-691 contains "Char. Level Stands", "Level", "Special")
        if 686 < current_y < 692:
            i = j
            continue
        
        # Sort by x position and extract text
        row_data.sort(key=lambda d: d['x'])
        row_texts = [d['text'] for d in row_data]
        
        # Clean up fragmented dice notation (remove spaces in things like "1 d 1 0 + 2")
        cleaned_row = []
        for text in row_texts:
            # Remove spaces from dice notation and percentages
            if any(c in text for c in ['d', '+', '%']):
                text = text.replace(' ', '')
            cleaned_row.append(text)
        
        # Special case: Level 11 row has merged columns at x=178
        # "1d3+1  5%" (with double space) needs to be split
        if len(cleaned_row) == 3:
            # Check if the last column contains both level and special (dice + percentage)
            if 'd' in cleaned_row[-1] and '%' in cleaned_row[-1]:
                # Split on the percentage
                match = re.search(r'(1d\d+\+\d+)(\d+%)', cleaned_row[-1])
                if match:
                    cleaned_row = [cleaned_row[0], cleaned_row[1], match.group(1), match.group(2)]
            # Also check if column 2 contains merged stands+level
            elif 'd' in cleaned_row[1] and len(cleaned_row) == 3:
                # Pattern: first dice value ends with a number, immediately followed by "1d"
                match = re.search(r'(1d\d+\+\d+)(1d\d+\+\d+)', cleaned_row[1])
                if match:
                    # Split into two separate values (this is for level 20)
                    cleaned_row = [cleaned_row[0], match.group(1), match.group(2), cleaned_row[2]]
        
        # Fix known data quality issues from the PDF
        if len(cleaned_row) >= 1:
            # Fix "1 1" → "11" (level 11 has a space)
            if cleaned_row[0] == "1 1":
                cleaned_row[0] = "11"
            # Fix "1 7" → "17" (level 17 has a space)
            elif cleaned_row[0] == "1 7":
                cleaned_row[0] = "17"
        
        rows.append(cleaned_row)
        i = j
    
    # Sort rows by character level (first column) to ensure correct order (11-20)
    # Level 11 is at y=703 (bottom), levels 12-20 are at y=148-256 (top)
    # But FIRST, fix the "13" that should be "19" by checking the dice values
    # Level 13 should have "1d12+2" stands, level 19 should have "1d20+8" stands
    for row in rows:
        if len(row) >= 2 and row[0] == "13" and row[1] == "1d20+8":
            row[0] = "19"
    
    rows.sort(key=lambda r: int(r[0]) if r and r[0].isdigit() else 999)
    
    # Build the table structure in the format the renderer expects
    # Each row should be a dict with "cells" key, where each cell is a dict with "text" key
    table_rows = []
    
    # Header row
    header_row = {
        "cells": [
            {"text": "Char. Level"},
            {"text": "Stands"},
            {"text": "Level"},
            {"text": "Special"}
        ]
    }
    table_rows.append(header_row)
    
    # Add data rows (should be 9 rows for levels 12-20)
    for row in rows:
        if len(row) >= 4:
            data_row = {
                "cells": [
                    {"text": row[0]},  # Char. Level
                    {"text": row[1]},  # Stands
                    {"text": row[2]},  # Level
                    {"text": row[3]}   # Special
                ]
            }
            table_rows.append(data_row)
        elif len(row) == 3:
            # Some rows might be missing a column
            data_row = {
                "cells": [
                    {"text": cell} for cell in row
                ]
            }
            table_rows.append(data_row)
    
    # Create the table structure that the renderer expects
    table = {
        "type": "table",
        "bbox": [300, 140, 550, 270],  # Approximate table boundaries
        "rows": table_rows,
        "header_rows": 1,  # First row is a header
        "num_rows": len(table_rows),
        "num_cols": 4
    }
    
    # Add table to page
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table)
    
    # Clear the blocks that contained the fragmented table data
    for idx in blocks_to_clear:
        if idx < len(page.get("blocks", [])):
            page["blocks"][idx]["lines"] = []


def _extract_class_ability_requirements_table(page: dict) -> None:
    """Extract and format the Class Ability Requirements table on page 23.
    
    The table should have:
    - Headers: Class, Str, Dex, Con, Cha, Int, Wis
    - Rows: Gladiator, Defiler, Templar, Psionicist (with their ability requirements)
    """
    # TODO: Implement table extraction
    pass


def _extract_rangers_followers_table(pages: list) -> None:
    """Extract and format the Rangers Followers table on pages 27-28 (indices 6-7).
    
    This is a d100 table with 2 columns and 22 rows (1 header + 21 data rows).
    Column 1: d100 Roll range (e.g., "01-04")
    Column 2: Follower type description
    
    The table is heavily fragmented across two pages.
    """
    if len(pages) <= 7:
        return
    
    # This table spans pages 27-28 (indices 6-7)
    # Collect all text from both pages that appears to be table data
    table_data = []
    
    # Define the d100 ranges we're looking for (21 entries based on 22 rows including header)
    # Standard Rangers Followers table typically has entries like:
    # 01-04, 05-08, 09-12, 13-24, 25-48, 49-72, 73-82, 83-86, 87-90, 91-94, 95-96, 97-98, 99-00
    # But we need to extract what's actually in the PDF
    
    # For now, create a placeholder table structure that can be filled in manually
    # This follows Rule #23 - we're not inventing data, just creating structure
    # The actual data extraction from this heavily fragmented table requires manual verification
    
    # Mark this as needing manual data entry
    # TODO: Extract complete table data from heavily fragmented PDF source
    pass


def _extract_defiler_experience_table(page: dict) -> None:
    """Extract and format the Defiler Experience Levels table on page 29.
    
    The table shows XP progression for defiler wizards (faster than preservers).
    """
    # TODO: Implement table extraction
    pass


def _extract_templar_spell_progression_table(page: dict) -> None:
    """Extract and format the Templar Spell Progression table on page 35.
    
    The table shows spell slots per level for templar priests.
    """
    # TODO: Implement table extraction
    pass


def _extract_bard_poison_table(page: dict) -> None:
    """Extract and format the Bard Poison Table on page 38.
    
    The table lists 18 different poisons (A-P) with their characteristics.
    """
    # TODO: Implement table extraction
    pass


def _extract_thieving_dexterity_adjustments_table(page: dict) -> None:
    """Extract and format the Thieving Skill Exceptional Dexterity Adjustments table on page 39.
    
    The table shows percentage adjustments for high Dexterity scores (16-21).
    """
    # TODO: Implement table extraction
    pass


def _extract_thieving_racial_adjustments_table(page: dict) -> None:
    """Extract and format the Thieving Skill Racial Adjustments table on page 39.
    
    The table shows percentage adjustments for different races.
    """
    # TODO: Implement table extraction
    pass


def _extract_inherent_potential_table(page: dict) -> None:
    """Extract and format the Inherent Potential Table on page 40.
    
    The table shows psionic ability score modifiers for scores 16-22.
    """
    # TODO: Implement table extraction
    pass


def apply_chapter_3_adjustments(section_data: dict) -> None:
    """Apply all Chapter 3 specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # First, normalize all text to remove control characters like \x92 and \x99
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if "text" in span:
                            span["text"] = _normalize_plain_text(span["text"])
    
    # Mark Ranger description blocks to prevent premature paragraph splitting
    _mark_ranger_description_blocks(pages)
    
    # Extract the Fighters Followers table on page 25 (index 4)
    if len(pages) > 4:
        _extract_fighters_followers_table(pages[4])
    
    # Page indices are 0-based, but the PDF pages are labeled 21-43
    # Page 21 is index 0, page 23 is index 2, etc.
    
    # Extract tables at PDF level
    if len(pages) > 2:  # Page 23 (index 2)
        _extract_class_ability_requirements_table(pages[2])
    
    if len(pages) > 6:  # Pages 27-28 (indices 6-7)
        _extract_rangers_followers_table(pages)
    
    if len(pages) > 8:  # Page 29 (index 8)
        _extract_defiler_experience_table(pages[8])
    
    if len(pages) > 14:  # Page 35 (index 14)
        _extract_templar_spell_progression_table(pages[14])
    
    if len(pages) > 17:  # Page 38 (index 17)
        _extract_bard_poison_table(pages[17])
    
    if len(pages) > 18:  # Page 39 (index 18)
        _extract_thieving_dexterity_adjustments_table(pages[18])
        _extract_thieving_racial_adjustments_table(pages[18])
    
    if len(pages) > 19:  # Page 40 (index 19)
        _extract_inherent_potential_table(pages[19])

