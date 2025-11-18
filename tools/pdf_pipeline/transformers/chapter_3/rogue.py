"""
Rogue class (Bard & Thief) specific processing for Chapter 3.

This module handles PDF-level adjustments for rogue classes,
including table extraction and paragraph break forcing.
"""

import re
from .common import normalize_plain_text, update_block_bbox


def extract_bard_poison_table(page: dict) -> None:
    """Extract and format the Bard Poison Table on page 38.
    
    The table should have 5 columns (Die Roll, Class, Method, Onset, Strength)
    and 18 rows (1 header + 17 data rows).
    Poisons are labeled A through P (16 poisons), plus final "Player's Choice" row.
    Note: Poison H has die roll 7 (same as F).
    
    This function attaches the table data as a marker to the "Bard Poison Table" header block.
    """
    # Build the correct table structure
    # Header row
    header_row = {
        "cells": [
            {"text": "Die Roll"},
            {"text": "Class"},
            {"text": "Method"},
            {"text": "Onset"},
            {"text": "Strength"}
        ]
    }
    
    # Poison data - 17 data rows (A-P plus final "Player's Choice" row)
    poison_data = [
        ["2", "A", "Injected", "10-30 min.", "15/0"],
        ["3", "B", "Iniected", "2-12 min.", "20/1-3"],  # Note: "Iniected" typo in source
        ["4", "C", "Injected", "2-5 min.", "25/2-8"],
        ["5", "D", "Injected", "1-2 min.", "30/2-12"],
        ["6", "E", "Injected", "Immediate", "Death/20"],
        ["7", "F", "Injected", "Immediate", "Death/0"],
        ["8", "G", "Ingested", "2-12 hours", "20/10"],
        ["7", "H", "Ingested", "1-4 hours", "20/10"],  # Die roll is 7 (duplicate with F)
        ["10", "I", "Ingested", "2-12 min.", "30/15"],
        ["11", "J", "Ingested", "1-4 min.", "Death/20"],
        ["12", "K", "Contact", "2-8 min.", "5/0"],
        ["13", "L", "Contact", "2-8 min.", "10/0"],
        ["14", "M", "Contact", "1-4 min.", "20/5"],
        ["15", "N", "Contact", "1 minute", "Death/25"],
        ["16", "O", "Injected", "2-24 min.", "Paralytic"],
        ["17", "P", "Injected", "1-3 hours", "Debilitative"],
        ["18+", "Players Choice", "", "", ""]  # Final row - Class column has "Players Choice"
    ]
    
    # Build table rows
    rows = [header_row]
    for data in poison_data:
        row = {
            "cells": [{"text": cell} for cell in data]
        }
        rows.append(row)
    
    # Build the complete table structure
    table_data = {
        "rows": rows,
        "header_rows": 1
    }
    
    # Find the "Bard Poison Table" header block and attach the table as a marker
    header_block_found = False
    for block in page.get("blocks", []):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            if "Bard Poison Table" in all_text:
                # Attach table data as a marker to this header block
                block["__bard_poison_table"] = table_data
                header_block_found = True
                break
    
    if not header_block_found:
        # If header not found, log a warning but don't fail
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Bard Poison Table header block not found on page")
        return
    
    # Clear any malformed tables from the page
    page["tables"] = []
    
    # Clear leftover text blocks that were part of the malformed table
    # These typically contain poison data like "A Injected", "10-30 min", etc.
    for block in page.get("blocks", []):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            all_text = all_text.strip()
            
            # Check if this looks like leftover poison table data
            poison_keywords = ["Injected", "Iniected", "Ingested", "Contact", "10-30 min", "2-12 min", "2-12 hours", "1-4 hours", "Death/20", "Death/25", "Paralytic", "Debilitative", "Players Choice", "20/10", "min.5/0", "min.10/0", "min.20/5"]
            # Also check for poison letter patterns like:
            # - "2A", "3B", "4C" (die roll + poison letter)
            # - "5D6E" (multiple die rolls + poison letters combined)
            # - "1 0I", "1 1J" (spaced numbers + poison letter)
            # - "A B" or "ABCDEFGH" (consecutive poison letters)
            # - "1 0 I 1 1 J" (numbers with spaced poison letters)
            # - Just "3 6" (the old page number)
            # - Time patterns with strength values: "2-8 min.5/0" or "1-4 min.20/5"
            poison_letter_pattern = r'^\d+[A-P]$|^\d+[A-P]\d+[A-P]$|\d+\s+\d+\s*[A-P]|[A-P]{2,}|(\b[A-P]\s+){2,}|^3\s*6$|^\d+\s+[A-P]\s+\d+\s+[A-P]|\d+-\d+\s*min\.\d+/\d+'
            
            if (any(keyword in all_text for keyword in poison_keywords) or 
                re.search(poison_letter_pattern, all_text)):
                # Make sure it's not the actual content paragraphs or the header block
                if (not all_text.startswith("Athasian bards") and 
                    not all_text.startswith("In all cases") and
                    "Bard Poison Table" not in all_text):
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]




def force_bard_poison_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks after the Bard Poison Table.
    
    Two paragraphs with breaks at:
    - "Athasian bards do not gain"
    - "In all cases where the rules here"
    """
    break_texts = [
        "Athasian bards do not gain",
        "In all cases where the rules here"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line contains any break point
            should_break = False
            for break_text in break_texts:
                if line_text.startswith(break_text):
                    should_break = True
                    break
            
            if should_break:
                # If this is the first line, just mark the block
                if line_idx == 0:
                    block["__force_paragraph_break"] = True
                    break
                else:
                    # Need to split this block
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
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_thief_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Thief class details section.
    
    Five paragraphs with breaks at:
    - (First paragraph: "Athasian thieves run the gamut..." - starts naturally)
    - "A thief" (meaning "A thiefs prime requisite is Dexterity")
    - "A thief can choose any"
    - "A thiefs selection of weapon"
    - "A thiefs skills are determined just"
    """
    break_texts = [
        "A thiefs prime requisite",
        "A thief can choose any",
        "A thiefs selection of weapon",
        "A thiefs skills are determined just"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line contains any break point
            should_break = False
            for break_text in break_texts:
                if line_text.startswith(break_text):
                    should_break = True
                    break
            
            if should_break:
                # If this is the first line, just mark the block
                if line_idx == 0:
                    block["__force_paragraph_break"] = True
                    break
                else:
                    # Need to split this block
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
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def extract_thieving_dexterity_adjustments_table(page: dict) -> None:
    """Extract and format the Thieving Skill Exceptional Dexterity Adjustments table on page 39.
    
    The table shows percentage adjustments for high Dexterity scores (18-22).
    6 columns: Dex, Pick Pockets, Open Locks, Find/Remove Traps, Move Silently, Hide in Shadows
    6 rows: 1 header row + 5 data rows (Dex 18-22)
    
    This function attaches the table data as a marker to the header block.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== extract_thieving_dexterity_adjustments_table called ===")
    
    # Hardcoded table data (source has whitespace issues like "13 + 1 5 %" instead of "19 +15%")
    dex_adjustments = [
        ["18", "+10%", "+15%", "+5%", "+10%", "+10%"],
        ["19", "+15%", "+20%", "+10%", "+15%", "+15%"],
        ["20", "+20%", "+25%", "+12%", "+20%", "+17%"],
        ["21", "+25%", "+27%", "+15%", "+25%", "+20%"],
        ["22", "+27%", "+30%", "+17%", "+30%", "+22%"]
    ]
    
    # Build the table structure
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Dex"},
                    {"text": "Pick Pockets"},
                    {"text": "Open Locks"},
                    {"text": "Find/Remove Traps"},
                    {"text": "Move Silently"},
                    {"text": "Hide in Shadows"}
                ]
            }
        ],
        "header_rows": 1
    }
    
    # Add data rows
    for row_data in dex_adjustments:
        row = {
            "cells": [{"text": cell} for cell in row_data]
        }
        table_data["rows"].append(row)
    
    logger.info(f"Table data built with {len(table_data['rows'])} rows")
    
    # Find the header block and attach the table as a marker
    header_block_found = False
    logger.info(f"Searching through {len(page.get('blocks', []))} blocks")
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            if "Thieving Skill Exceptional Dexterity Adjustments" in all_text:
                # Attach table data as a marker to this header block
                logger.info(f"FOUND header at block {idx}, attaching marker")
                block["__dexterity_adjustments_table"] = table_data
                header_block_found = True
                logger.info(f"Marker attached: {bool('__dexterity_adjustments_table' in block)}")
                break
    
    if not header_block_found:
        # If header not found, log a warning but don't fail
        logger.warning("Thieving Skill Exceptional Dexterity Adjustments header block not found on page")
        return
    else:
        logger.info("✓ Header found and marker attached successfully")
    
    # Clear any malformed tables from the page that might interfere
    page["tables"] = []
    
    # Clear leftover text blocks that were part of the malformed table
    for block in page.get("blocks", []):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            all_text_stripped = all_text.strip()
            
            # Check if this looks like table content
            # Match: column headers, or rows with multiple percentage values
            is_table_content = (
                "Pick    Open  Find" in all_text or
                ("Dex" in all_text and "Pockets" in all_text) or
                # Match rows like "18+10%" or "13+ 1 5 %" or "2 0+20%"
                all_text_stripped.startswith("18+") or
                all_text_stripped.startswith("13+") or
                all_text_stripped.startswith("2 0+") or  # "20" with space
                all_text_stripped.startswith("2 1+") or  # "21" with space
                all_text_stripped.startswith("22+")
            )
            
            if is_table_content:
                # Make sure it's not the actual content paragraphs or the header block
                if not all_text.startswith("Athasian thieves can employ") and \
                   "Thieving Skill Exceptional Dexterity Adjustments" not in all_text:
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]




def force_thief_abilities_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Thief abilities section after the Dexterity table.
    
    Five paragraphs with breaks at:
    - "Athasian thieves can employ the backstab"
    - "At 10th level a thief can attempt to attract"
    - "The base chance of finding a patron is a"
    - "In the campaign"
    - "In all cases where"
    """
    break_texts = [
        "Athasian thieves can employ the backstab",
        "At 10th level a thief can attempt to attract",
        "The base chance of finding a patron is a",
        "In the campaign",
        "In all cases where"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line contains any break point
            should_break = False
            for break_text in break_texts:
                if line_text.startswith(break_text):
                    should_break = True
                    break
            
            if should_break:
                # If this is the first line, just mark the block
                if line_idx == 0:
                    block["__force_paragraph_break"] = True
                    break
                else:
                    # Need to split this block
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
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def extract_thieving_racial_adjustments_table(page: dict) -> None:
    """Extract and format the Thieving Skill Racial Adjustments table on page 39.
    
    The table shows percentage adjustments for different races.
    6 columns: Skill, Dwarf, Elf, Half-elf, Halfling, Mul
    9 rows: 1 header + 8 skill rows
    
    This function attaches the table data as a marker to the header block.
    """
    # Hardcoded table data (source has fragmented layout across columns)
    racial_adjustments = [
        ["Pick Pockets", "-", "+5%", "+10%", "+5%", "-"],
        ["Open Locks", "+10%", "-5%", "-", "+5%", "-5%"],
        ["Find/Remove Traps", "+15%", "-", "-", "+5%", "-"],
        ["Move Silently", "-", "+5%", "-", "+10%", "+5%"],
        ["Hide in Shadows", "-", "+10%", "+5%", "+15%", "-"],
        ["Detect Noise", "-", "+5%", "-", "+5%", "-"],
        ["Climb Walls", "-10%", "-", "-", "-15%", "+5%"],
        ["Read Languages", "-5%", "-", "-", "-5%", "-5%"]
    ]
    
    # Build the table structure
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Skill"},
                    {"text": "Dwarf"},
                    {"text": "Elf"},
                    {"text": "Half-elf"},
                    {"text": "Halfling"},
                    {"text": "Mul"}
                ]
            }
        ],
        "header_rows": 1
    }
    
    # Add data rows
    for row_data in racial_adjustments:
        row = {
            "cells": [{"text": cell} for cell in row_data]
        }
        table_data["rows"].append(row)
    
    # Find the header block and attach the table as a marker
    header_block_found = False
    for block in page.get("blocks", []):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            if "Thieving Skill Racial Adjustments" in all_text:
                # Attach table data as a marker to this header block
                block["__racial_adjustments_table"] = table_data
                header_block_found = True
                break
    
    if not header_block_found:
        # If header not found, log a warning but don't fail
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Thieving Skill Racial Adjustments header block not found on page")
        return
    
    # Clear leftover text blocks that were part of the malformed table
    for block in page.get("blocks", []):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            all_text_stripped = all_text.strip()
            
            # Check if this looks like table content
            is_table_content = (
                "S k i l l" in all_text or
                ("Dwarf" in all_text and ("Pick Pockets" in all_text or "Elf" in all_text)) or
                ("Open Locks" in all_text and ("+10%" in all_text or "+ 1 0 %" in all_text)) or
                ("Find/Remove" in all_text and "Move Silently" in all_text) or
                ("Hide in Shadows" in all_text and "Detect Noise" in all_text) or
                ("Climb Walls" in all_text and all_text_stripped == "Climb Walls") or
                # Match common table data fragments (with spaces in percentages)
                re.match(r'^[\s\-\+\d%]+$', all_text_stripped) and len(all_text_stripped) < 50 or
                (all_text_stripped in ["Read Languages", "+ 1 5 % -", "- 5 % - + 5 % - 5 %", "- + 5 % - -",
                                        "+ 5 % - + 1 0 % + 5 %", "+ 1 0 % + 5 % + 1 5 % -", "+ 5 % - + 5 % -",
                                        "- - - 1 5 % + 5 %", "- - - 5 % - 5 %", "- 1 0 %", "- 5 %", "-",
                                        "Open Locks + 1 0 %"])
            )
            
            if is_table_content:
                # Make sure it's not the actual content or the header block
                if "Thieving Skill Racial Adjustments" not in all_text and \
                   not all_text.startswith("In the campaign") and \
                   not all_text.startswith("In all cases where"):
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]




def force_bard_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Bard class details section.
    
    The Bard section should have 11 paragraphs with breaks at specific points.
    """
    # Break points for the Bard section
    bard_breaks = [
        "As described in",
        "Athasian bards have no",
        "Bards are first and foremost entertainers",
        "Among the nobility of the cities",
        "A bard has a bewildering variety of benefits",
        "A bard can use all thief abilities",
        "A bard can influence reactions",
        "Music, poetry, and stories of the bard can",
        "Bards also learn a",
        "A bard is a master of poisons"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line contains any break point
            should_break = False
            
            # Check break points (startswith to handle line continuations)
            for break_text in bard_breaks:
                if line_text.startswith(break_text):
                    should_break = True
                    break
            
            if should_break:
                # If this is the first line, just mark the block
                if line_idx == 0:
                    block["__force_paragraph_break"] = True
                    break
                else:
                    # Need to split this block
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
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_rogue_classes_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Rogue Classes section by splitting and marking blocks.
    
    The Rogue Classes section should have 3 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
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
            
            # Check if this line should start a new paragraph (user-specified breaks)
            # P2: "The thief..." - starts paragraph 2 (thief description)
            # P3: "The bard..." - starts paragraph 3 (bard description)
            if (line_text.startswith("The thief is a rogue whose strengths lie in stealth") or
                line_text.startswith("The bard is a rogue who uses songs and tales as")):
                
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




