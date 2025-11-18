"""
Ranger class specific processing for Chapter 3.

This module handles PDF-level adjustments for the Ranger class,
including table extraction, table reconstruction, and paragraph break forcing.
"""

import logging
from .common import normalize_plain_text, update_block_bbox

logger = logging.getLogger(__name__)


def fix_ranger_ability_requirements_table(page: dict) -> None:
    """Fix the malformed Ranger Ability Requirements table on page 27 (index 6).
    
    The PDF extraction creates a malformed table with only 2 rows and incorrect data.
    We need to reconstruct it properly with 3 rows.
    """
    blocks = page.get("blocks", [])
    tables = page.get("tables", [])
    
    # Find the Ranger header
    ranger_header_idx = None
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        text = ' '.join(' '.join(span.get('text', '') for span in line.get('spans', [])) for line in lines).strip()
        
        if text.strip() == "Ranger":
            ranger_header_idx = idx
            break
    
    if ranger_header_idx is None:
        return
    
    # Find the malformed table (should be within next few blocks or in tables list)
    # Look for a table with "Ability Requirements" as first cell
    malformed_table_idx = None
    for idx, table in enumerate(tables):
        rows = table.get("rows", [])
        if rows and len(rows) >= 1:
            first_cell = rows[0].get("cells", [{}])[0]
            if "Ability Requirements" in first_cell.get("text", ""):
                malformed_table_idx = idx
                break
    
    if malformed_table_idx is None:
        return
    
    # Create the corrected table
    corrected_table = {
        "type": "table",
        "bbox": tables[malformed_table_idx].get("bbox", [0, 0, 0, 0]),
        "rows": [
            {
                "cells": [
                    {"text": "Ability Requirements:"},
                    {"text": "Strength 13 Dexterity 13 Constitution 14 Wisdom 14"}
                ]
            },
            {
                "cells": [
                    {"text": "Prime Requisite:"},
                    {"text": "Strength, Dexterity, Wisdom"}
                ]
            },
            {
                "cells": [
                    {"text": "Races Allowed:"},
                    {"text": "Human, Elf, Half-elf, Halfling, Thri-kreen"}
                ]
            }
        ],
        "header_rows": 0
    }
    
    # Replace the malformed table
    tables[malformed_table_idx] = corrected_table
    
    # Clear any text blocks that contain "Races Allowed" or the race list fragments
    # The race list is split across blocks: "dom Human, Elf, Half-elf," and "Halfling, Thri-kreen"
    for block in blocks:
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        text = ' '.join(' '.join(span.get('text', '') for span in line.get('spans', [])) for line in lines).strip()
        
        # Clear blocks containing race-related text that should now be in the table
        if ("Races Allowed" in text or 
            "dom Human" in text or  # Fragment from "Wisdom Human, Elf, Half-elf"
            ("Halfling" in text and "Thri-kreen" in text)):  # Second fragment
            block["lines"] = []


def force_ranger_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Ranger section.
    
    The section should have 9 paragraphs based on user-specified breaks.
    """
    blocks = page.get("blocks", [])
    blocks_to_insert = []
    
    # First, merge blocks that were incorrectly split
    # "A ranger can learn clerical spells when he reaches" + "8th level..."
    for idx in range(len(blocks) - 1):
        block = blocks[idx]
        next_block = blocks[idx + 1]
        
        if block.get("type") != "text" or next_block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        next_lines = next_block.get("lines", [])
        
        if not lines or not next_lines:
            continue
        
        text = normalize_plain_text(
            "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        )
        next_text = normalize_plain_text(
            "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in next_lines)
        )
        
        # Check if this is the split block
        if "when he reaches" in text and next_text.startswith("8th level"):
            # Merge the blocks
            block["lines"].extend(next_lines)
            update_block_bbox(block)
            # Clear the next block
            next_block["lines"] = []
            break
    
    # Define the paragraph break points
    break_points = [
        "A rangers motivations can",  # Note: no apostrophe in source
        "A ranger can use any weapon or wear any armor,",
        "A ranger also gains the tracking, move silently,",
        "An Athasian ranger must also choose a species",
        "A ranger is skilled at animal handling",  # Shortened to match actual text
        "A ranger can learn clerical spells",  # Shortened to avoid split across blocks
        "While a ranger cannot enchant magical potions",
        "At 10th level, a ranger attracts 2d6 followers, but"
    ]
    
    for idx, block in enumerate(list(blocks)):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        split_done = False
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line matches any break point
            should_break = any(line_text.startswith(bp) for bp in break_points)
            
            if should_break:
                if line_idx == 0:
                    # Mark the block itself
                    block["__force_paragraph_break"] = True
                else:
                    # Split this block at this line
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
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)


def reconstruct_rangers_followers_table_inplace(page: dict) -> None:
    """Reconstruct the malformed Rangers Followers table in-place.
    
    The PDF extraction creates malformed tables with mixed content.
    We remove ALL malformed tables and reconstruct a single correct table.
    
    Args:
        page: Page data dictionary
    """
    tables = page.get("tables", [])
    logger.info(f"reconstruct_rangers_followers_table_inplace: Processing {len(tables)} tables")
    
    # Define the correct table data as reference
    roll_data = [
        ("01-04", "Aarakocra"),
        ("05-08", "Anakore"),
        ("09-12", "Ant Lion, Giant"),
        ("13", "Behir"),
        ("14-19", "Belgoi"),
        ("20-25", "Baazrag"),
        ("26-30", "Cat, Great"),
        ("31", "Dragonne"),
        ("32-35", "Druid"),
        ("36-37", "Ettin"),
        ("40-45", "Fighter (human)"),
        ("46-52", "Fighter (elf)"),
        ("53-58", "Fighter (thri-kreen)"),
        ("53-62", "Giant"),
        ("63-68", "Kenku"),
        ("67-78", "Lizard"),
        ("73-82", "Preserver"),
        ("83", "Psionicist (human)"),
        ("84-90", "Roc"),
        ("91-95", "Tiref"),
        ("96-78", "Wyvern"),
        ("99", "Yuan-ti"),
        ("00", "Other wilderness creature (chosen by the DM)")
    ]
    
    # Find ALL malformed tables that contain Rangers Followers data
    followers_keywords = [
        "Aarakocra", "Anakore", "Ant Lion", "Belgoi", "Baazrag", 
        "Dragonne", "Druid", "Ettin", "Kenku", "Fighter (elf)", 
        "Fighter (human)", "Fighter (thri-kreen)", "Roc", "Tiref"
    ]
    roll_ranges = ["01-04", "05-08", "09-12", "13", "14-19", "20-25", "26-30", 
                   "32-35", "36-37", "40-45", "46-52", "53-58", "63-68", "73-82", 
                   "84-90", "91-95"]
    
    malformed_table_indices = []
    for idx, table in enumerate(tables):
        rows = table.get("rows", [])
        if not rows:
            continue
        
        # Check if this table contains Rangers Followers data
        has_followers_data = False
        for row in rows[:10]:
            cells = row.get("cells", [])
            for cell in cells:
                text = cell.get("text", "")
                # Check for creature names or roll ranges
                if any(creature in text for creature in followers_keywords):
                    has_followers_data = True
                    break
                if any(roll in text for roll in roll_ranges):
                    has_followers_data = True
                    break
            if has_followers_data:
                break
        
        # Also check if the table contains mixed paragraph + table data (a telltale sign)
        for row in rows[:5]:
            cells = row.get("cells", [])
            for cell in cells:
                text = cell.get("text", "")
                # If a cell contains both long paragraph text AND a creature name, it's malformed
                if len(text) > 50 and any(creature in text for creature in followers_keywords):
                    has_followers_data = True
                    break
                # If a cell contains "largely unchanged" or similar paragraph fragments
                if ("largely unchanged" in text or "A rangers motivations" in text or 
                    "harsh and unforgiving" in text):
                    has_followers_data = True
                    break
            if has_followers_data:
                break
        
        if has_followers_data:
            malformed_table_indices.append(idx)
    
    if not malformed_table_indices:
        logger.warning("Could not find any malformed Rangers Followers tables to reconstruct")
        return
    
    logger.info(f"Found {len(malformed_table_indices)} malformed Rangers Followers table(s) at indices {malformed_table_indices}, removing and reconstructing...")
    
    # Remove ALL malformed tables (in reverse order to maintain indices)
    for idx in reversed(malformed_table_indices):
        del tables[idx]
    
    # Create a single new correctly structured table
    new_rows = [
        {
            "cells": [
                {"text": "d100 Roll"},
                {"text": "Follower Type"}
            ]
        }
    ]
    
    # Add data rows
    for roll, follower in roll_data:
        new_rows.append({
            "cells": [
                {"text": roll},
                {"text": follower}
            ]
        })
    
    # Create the correct table
    corrected_table = {
        "type": "table",
        "bbox": [50, 400, 500, 600],  # Placeholder bbox
        "rows": new_rows,
        "header_rows": 1
    }
    
    # Add the corrected table back to the tables list
    tables.append(corrected_table)
    
    # Clear any text blocks on this page that contain table data fragments
    # These appear as leftover paragraphs after the Rangers Followers header
    blocks = page.get("blocks", [])
    for block in blocks:
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        
        # Check if this block contains table data (both creature names AND roll ranges)
        has_creature = any(creature in text for creature in ["Aarakocra", "Anakore", "Belgoi", "Druid", "Ettin"])
        has_roll = any(roll in text for roll in ["01-04", "05-08", "09-12", "14-19", "20-25"])
        
        # Clear the block if it contains table data
        if has_creature and has_roll:
            block["lines"] = []
            block["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    logger.info(f"Rangers Followers table reconstruction complete. Page now has {len(tables)} table(s).")


def extract_rangers_followers_table(page: dict) -> None:
    """Extract and format the Rangers Followers table on pages 27-28 (indices 6-7).
    
    This is a d100 table with 2 columns (d100 Roll, Follower Type) and 23 data rows.
    The table shows what type of followers a ranger attracts at 10th level.
    The table data is split across pages, so we need to find the right insertion point.
    
    Args:
        page: Page data dictionary
    """
    blocks = page.get("blocks", [])
    tables = page.get("tables", [])
    
    # Look for the paragraph about 10th level followers
    # This is where we want to insert the table
    insertion_point_idx = None
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        text = normalize_plain_text(
            "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        )
        
        if "At 10th level, a ranger attracts" in text:
            insertion_point_idx = idx
            break
    
    if insertion_point_idx is None:
        return
    
    # Check if we've already added the table (to avoid duplicates)
    for table in tables:
        rows = table.get("rows", [])
        if rows and len(rows) > 0:
            first_cell = rows[0].get("cells", [{}])[0]
            if "d100 Roll" in first_cell.get("text", ""):
                return  # Table already exists
    
    # Define the table data
    # d100 Roll ranges and corresponding follower types
    roll_data = [
        ("01-04", "Aarakocra"),
        ("05-08", "Anakore"),
        ("09-12", "Ant Lion, Giant"),
        ("13", "Behir"),
        ("14-19", "Belgoi"),
        ("20-25", "Baazrag"),
        ("26-30", "Cat, Great"),
        ("31", "Dragonne"),
        ("32-35", "Druid"),
        ("36-37", "Ettin"),
        ("40-45", "Fighter (human)"),
        ("46-52", "Fighter (elf)"),
        ("53-58", "Fighter (thri-kreen)"),
        ("53-62", "Giant"),
        ("63-68", "Kenku"),
        ("67-78", "Lizard"),
        ("73-82", "Preserver"),
        ("83", "Psionicist (human)"),
        ("84-90", "Roc"),
        ("91-95", "Tiref"),
        ("96-78", "Wyvern"),
        ("99", "Yuan-ti"),
        ("00", "Other wilderness creature (chosen by the DM)")
    ]
    
    # Create the table structure
    table_rows = [
        {
            "cells": [
                {"text": "d100 Roll"},
                {"text": "Follower Type"}
            ]
        }
    ]
    
    # Add data rows
    for roll, follower in roll_data:
        table_rows.append({
            "cells": [
                {"text": roll},
                {"text": follower}
            ]
        })
    
    # Create the table
    rangers_table = {
        "type": "table",
        "bbox": [50, 400, 500, 600],  # Placeholder bbox
        "rows": table_rows,
        "header_rows": 1
    }
    
    # Create a header block for "Rangers Followers" 
    # Insert it after the "At 10th level" paragraph
    header_block = {
        "type": "text",
        "lines": [{
            "spans": [{
                "text": "Rangers Followers",
                "font": "MSTT31c501",
                "size": 10.8,
                "flags": 20,
                "color": 0
            }],
            "bbox": [50, 500, 200, 510]
        }],
        "bbox": [50, 500, 200, 510]
    }
    
    # Remove the old "RANGERS FOLLOWERS" header from the PDF if it exists
    blocks_to_remove = []
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                if "RANGERS FOLLOWERS" in line_text:
                    # Mark this block for removal
                    blocks_to_remove.append(i)
                    break
    
    # Adjust insertion_point_idx if we're removing blocks before it
    adjusted_insertion_idx = insertion_point_idx
    for i in blocks_to_remove:
        if i <= insertion_point_idx:
            adjusted_insertion_idx -= 1
    
    # Remove blocks in reverse order to maintain indices
    for i in reversed(blocks_to_remove):
        blocks.pop(i)
    
    # Insert the header after the adjusted insertion point
    blocks.insert(adjusted_insertion_idx + 1, header_block)
    
    # Add the table to the page
    if tables is None:
        page["tables"] = []
        tables = page["tables"]
    tables.append(rangers_table)
    
    # Clear any malformed table blocks that might exist
    # Look for blocks with table-like data (roll ranges, creature names)
    blocks_to_clear = []
    table_keywords = [
        "Aarakocra", "Anakore", "Ant Lion", "Behir", "Belgoi", "Baazrag",
        "Dragonne", "Druid", "Ettin", "Kenku", "Lizard", "Preserver",
        "Psionicist", "Tiref", "Wyvern", "Yuan-ti", "01-04", "05-08",
        "09-12", "20-25", "26-30", "40-45", "46-52", "53-58", "63-68",
        "73-82", "84-90", "91-95", "14-19", "32-35", "36-37", "96-78"
    ]
    
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        # Don't clear the insertion point (the "At 10th level" paragraph)
        if idx == insertion_point_idx or idx == insertion_point_idx + 1:
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        
        # Check if this block contains table data
        if any(keyword in text for keyword in table_keywords):
            blocks_to_clear.append(idx)
    
    # Clear the identified blocks
    for idx in blocks_to_clear:
        if idx < len(blocks):
            blocks[idx]["lines"] = []
            blocks[idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]


def extract_rangers_followers_table_from_pages(pages: list) -> None:
    """Extract and format the Rangers Followers table on pages 27-28 (indices 6-7).
    
    This is a d100 table with 2 columns and 22 rows (1 header + 21 data rows).
    Column 1: d100 Roll range (e.g., "01-04")
    Column 2: Follower type description
    
    The table is heavily fragmented across two pages.
    This is a placeholder function for future enhancement if needed.
    """
    # NOTE: This function is a placeholder. The single-page version
    # (extract_rangers_followers_table) handles this case adequately.
    pass


def mark_ranger_description_blocks(pages: list) -> None:
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
            
            # Check if this block contains "Ranger" header or "Rangers Followers" (or "RANGERS FOLLOWERS" from PDF)
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                line_text_clean = normalize_plain_text(line_text).strip()
                
                if "Ranger" in line_text_clean and len(line_text_clean) < 20:
                    found_ranger_header = True
                    block["__ranger_header"] = True
                
                # Match both "Rangers Followers" and "RANGERS FOLLOWERS" (from PDF)
                if "Rangers Followers" in line_text_clean or "RANGERS FOLLOWERS" in line_text:
                    found_followers_header = True
                    block["__followers_header"] = True
                    # Normalize the text to "Rangers Followers" to match other follower tables
                    for span in line.get("spans", []):
                        if "RANGERS FOLLOWERS" in span.get("text", ""):
                            span["text"] = "Rangers Followers"
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

