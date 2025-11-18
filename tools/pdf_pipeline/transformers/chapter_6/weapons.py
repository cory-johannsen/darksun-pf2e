"""
Weapon table processing for Chapter 6.

This module handles extraction and processing of weapon-related tables,
including weapon materials and new weapons.
"""

from __future__ import annotations

import logging
import re
from typing import List

from .common import normalize_plain_text, clean_whitespace, get_block_text, extract_table_cell_text

logger = logging.getLogger(__name__)


def extract_weapon_materials_table(section_data: dict) -> None:
    """Extract and format the Weapon Materials Table.
    
    The table has 5 columns and 5 rows (1 header + 4 data rows):
    - Header: Material, Cost, Wt., Dmg*, Hit Prob.**
    - Data rows: metal, bone, stone/obsidian, wood
    
    Also adjusts "Weapon Materials Table" header to H3 (size 9.6).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with open('/tmp/chapter6_debug.txt', 'a') as f:
        f.write(f"\n=== _extract_weapon_materials_table called ===\n")
        f.write(f"Searching in {len(section_data.get('pages', []))} pages\n")
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"  Checking page {page_idx}: {len(blocks)} blocks\n")
        
        # Find the "Weapon Materials Table" header
        table_header_idx = None
        for idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if "Weapon Materials Table" in text:
                        table_header_idx = idx
                        # Adjust header to H3 (size 9.6)
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"
                        logger.info("Found and adjusted 'Weapon Materials Table' header to H3")
                        with open('/tmp/chapter6_debug.txt', 'a') as f:
                            f.write(f"    FOUND 'Weapon Materials Table' at page {page_idx}, block {idx}\n")
                        break
                if table_header_idx is not None:
                    break
            if table_header_idx is not None:
                break
        
        if table_header_idx is None:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    NOT FOUND on page {page_idx}\n")
            continue
        
        # Find the table data blocks (the table is split across multiple blocks)
        # Block 1: Header row + first 2 data rows (metal, bone) - 15 lines
        # Block 2: Row 3 (stone/obsidian) - 5 lines
        # Block 3: Row 4 (wood) - 5 lines
        table_data_blocks = []
        blocks_to_skip = []
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"    Searching for table data in blocks {table_header_idx + 1} to {min(table_header_idx + 6, len(blocks))}\n")
        
        for idx in range(table_header_idx + 1, min(table_header_idx + 6, len(blocks))):
            block = blocks[idx]
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"      Block {idx}: type={block.get('type')}, lines={len(block.get('lines', []))}\n")
            if block.get("type") == "text":
                lines = block.get("lines", [])
                # First block should have 15 lines (header + 2 data rows)
                # Subsequent blocks should have 5 lines each (1 data row each)
                if len(lines) == 15 or len(lines) == 5:
                    first_line_text = lines[0].get("spans", [{}])[0].get("text", "").strip()
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"      FOUND table data block at {idx} with {len(lines)} lines, first line: '{first_line_text}'\n")
                    table_data_blocks.append((idx, block))
                    blocks_to_skip.append(idx)
                    # Stop after collecting 3 blocks (or when we hit a non-table block)
                    if len(table_data_blocks) >= 3:
                        break
                elif len(table_data_blocks) > 0:
                    # We've started collecting table blocks, so if we hit a non-table block, stop
                    break
        
        if not table_data_blocks:
            logger.warning("Could not find Weapon Materials Table data")
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    WARNING: Could not find Weapon Materials Table data\n")
            continue
        
        # Collect all lines from all data blocks
        all_lines = []
        for data_idx, data_block in table_data_blocks:
            all_lines.extend(data_block.get("lines", []))
        
        # Build table rows with proper structure for _render_table
        table_rows = []
        
        # Extract header row (first 5 lines: Material, Cost, Wt., Dmg*, Hit Prob.**)
        header_cells = []
        for i in range(5):
            if i < len(all_lines):
                text = all_lines[i].get("spans", [{}])[0].get("text", "").strip()
                # Fix "W t ." spacing
                text = text.replace("W t .", "Wt.")
                header_cells.append({"text": text})
        
        if len(header_cells) == 5:
            table_rows.append({"cells": header_cells})
        
        # Extract data rows (rows 5-24, groups of 5)
        # Row 1 (metal): lines 5-9
        # Row 2 (bone): lines 10-14
        # Row 3 (stone/obsidian): lines 15-19
        # Row 4 (wood): lines 20-24
        for row_start in range(5, min(25, len(all_lines)), 5):
            data_cells = []
            for i in range(5):
                line_idx = row_start + i
                if line_idx < len(all_lines):
                    text = all_lines[line_idx].get("spans", [{}])[0].get("text", "").strip()
                    # Clean up whitespace in percentages and damage values
                    # Remove all spaces between digits (e.g., "1 0 0 %" -> "100%")
                    while re.search(r'(\d)\s+(\d)', text):
                        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
                    text = re.sub(r'-\s+(\d)', r'-\1', text)  # "- 1" -> "-1"
                    data_cells.append({"text": text})
            if len(data_cells) == 5:
                table_rows.append({"cells": data_cells})
        
        logger.info(f"Extracted Weapon Materials Table with {len(table_rows)} rows")
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"    Extracted {len(table_rows)} rows from table\n")
            if table_rows:
                header_texts = [cell["text"] for cell in table_rows[0]["cells"]]
                f.write(f"    Header row: {header_texts}\n")
        
        # Build HTML table
        table = {
            "type": "table",
            "rows": table_rows,
            "header_rows": 1
        }
        
        # Attach table to the Weapon Materials Table header block
        blocks[table_header_idx]["__weapon_materials_table"] = table
        
        # Add legend after the table header block
        # The legend will be rendered immediately after the table
        legend_block = {
            "type": "text",
            "bbox": [37.439998626708984, 640.0, 300.0, 658.0],
            "lines": [
                {
                    "bbox": [37.439998626708984, 640.0, 300.0, 649.0],
                    "spans": [
                        {
                            "text": "*The damage modifier subtracts from the damage normally done by that weapon, with a minimum of one point.",
                            "font": "MSTT31c50d",
                            "size": 8.880000114440918,
                            "flags": 4,
                            "color": "#000000"
                        }
                    ]
                },
                {
                    "bbox": [37.439998626708984, 649.0, 300.0, 658.0],
                    "spans": [
                        {
                            "text": "** this does not apply to missile weapons.",
                            "font": "MSTT31c50d",
                            "size": 8.880000114440918,
                            "flags": 4,
                            "color": "#000000"
                        }
                    ]
                }
            ]
        }
        blocks.insert(table_header_idx + 1, legend_block)
        
        # Adjust block indices for skip markers since we inserted a block
        adjusted_skip_blocks = [idx + 1 if idx > table_header_idx else idx for idx in blocks_to_skip]
        
        # Also mark the old legend text blocks to skip (they appear after the table data blocks)
        # Find blocks containing "*The damage modifier" and "** this does not apply"
        for idx in range(len(blocks)):
            block = blocks[idx]
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if "*The damage modifier" in text or "** this does not apply" in text:
                            adjusted_skip_blocks.append(idx)
                            break
        
        # Remove duplicates
        adjusted_skip_blocks = list(set(adjusted_skip_blocks))
        
        # Mark all data blocks to skip rendering
        for skip_idx in adjusted_skip_blocks:
            blocks[skip_idx]["__skip_render"] = True
        
        logger.info(f"Attached Weapon Materials Table to header block at index {table_header_idx}")
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"    SUCCESS: Attached table to block {table_header_idx}, added legend, marked blocks {adjusted_skip_blocks} to skip\n")
        break




def extract_new_weapons_table(section_data: dict) -> None:
    """Extract and build the New Weapons table (appears after Animals table).
    
    Table structure: 8 columns, 6 rows (2 header rows + 4-5 data rows)
    - First header row: ["Weapons", "", "", "", "", "", "Damage"] where "Damage" spans 2 columns
    - Second header row: ["", "Cost", "Wt", "Size", "Type", "Speed", "S-M", "L"]
    
    NOTE: The table data is heavily fragmented in the PDF. After the Animals table,
    the column headers appear as separate blocks, followed by fragmented weapon data.
    This function synthesizes a proper table structure from those fragments.
    """
    import logging
    import re
    logger = logging.getLogger(__name__)
    
    logger.warning("Starting New Weapons table extraction")
    logger.warning(f"Section has {len(section_data.get('pages', []))} pages")
    
    # Find the Animals H2 header block (we'll insert the Weapons table after it)
    animals_block = None
    animals_page_idx = None
    animals_block_idx = None
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        for i, block in enumerate(blocks):
            if block.get("type") == "text":
                text = get_block_text(block).strip()
                if text == "Animals" and "__animals_table" in block:
                    animals_block = block
                    animals_page_idx = page_idx
                    animals_block_idx = i
                    logger.warning(f"Found Animals table at Page {page_idx}, Block {i}")
                    break
            if animals_block:
                break
        if animals_block:
            break
    
    if animals_block is None:
        logger.warning("Could not find Animals table block")
        return
    
    # Now find all the fragmented blocks after Animals table
    page = section_data["pages"][animals_page_idx]
    blocks = page.get("blocks", [])
    blocks_to_skip = []
    last_animals_data_idx = animals_block_idx  # Track where Animals data ends
    
    # First, find where the Animals table data ends (all blocks marked with __skip_render by Animals extraction)
    for idx in range(animals_block_idx + 1, len(blocks)):
        block = blocks[idx]
        if block.get("__skip_render"):
            last_animals_data_idx = idx  # Update to track the last Animals data block
        else:
            # Once we hit a block that's not marked to skip, we've moved past Animals data
            break
    
    logger.warning(f"Last Animals data block is at index {last_animals_data_idx}")
    
    # Now look for fragmented Weapons table data after the Animals data
    # These are the column headers and weapon data that appear as separate text blocks
    for idx in range(last_animals_data_idx + 1, len(blocks)):
        block = blocks[idx]
        if block.get("__skip_render"):
            continue  # Already marked by something else
        
        if block.get("type") != "text":
            continue
        
        block_text = get_block_text(block).strip()
        
        # Check if this is Equipment Descriptions section (the actual next major section)
        # Equipment Descriptions is H2 (size 10.8) and comes after all the fragmented data
        is_equipment_descriptions = False
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                color = span.get("color", "")
                # Equipment Descriptions is the section marker
                if "Equipment Descriptions" in text and color == "#ca5804":
                    is_equipment_descriptions = True
                    break
            if is_equipment_descriptions:
                break
        
        if is_equipment_descriptions:
            logger.warning(f"Found Equipment Descriptions section at block {idx}: {block_text[:50]}")
            break
        
        # Everything between Animals data and Equipment Descriptions is fragmented Weapons data
        blocks_to_skip.append(idx)
        logger.warning(f"Marking block {idx} for Weapons table (fragmented): {block_text[:100]}")
    
    # Mark all fragmented data blocks to skip rendering
    for idx in blocks_to_skip:
        blocks[idx]["__skip_render"] = True
    
    # Build the table rows from source specification (hard-coded based on user description)
    # The PDF fragments make it nearly impossible to extract reliably, so we use the spec
    table_rows = [
        {
            "cells": [
                {"text": "Weapons"},
                {"text": ""},
                {"text": ""},
                {"text": ""},
                {"text": ""},
                {"text": ""},
                {"text": "Damage", "colspan": 2}
            ]
        },
        {
            "cells": [
                {"text": ""},
                {"text": "Cost"},
                {"text": "Wt"},
                {"text": "Size"},
                {"text": "Type"},
                {"text": "Speed"},
                {"text": "S-M"},
                {"text": "L"}
            ]
        },
        # Weapon data rows (in order from source)
        {"cells": [
            {"text": "Chatkcha"}, 
            {"text": "1 cp"}, 
            {"text": "½"}, 
            {"text": "S"}, 
            {"text": "S"}, 
            {"text": "1"}, 
            {"text": "1d4+1"}, 
            {"text": "1d3"}
        ]},
        {"cells": [
            {"text": "Impaler"}, 
            {"text": "4 cp"}, 
            {"text": ""}, 
            {"text": "M"}, 
            {"text": "P/B"}, 
            {"text": "1"}, 
            {"text": "1d8"}, 
            {"text": "1d8"}
        ]},
        {"cells": [
            {"text": "Polearm, Gythka"}, 
            {"text": "6 cp"}, 
            {"text": "4"}, 
            {"text": "M"}, 
            {"text": "P/S"}, 
            {"text": "2"}, 
            {"text": "2d4"}, 
            {"text": "1d10"}
        ]},
        {"cells": [
            {"text": "Quabone"}, 
            {"text": "1 cp"}, 
            {"text": ""}, 
            {"text": "S"}, 
            {"text": "P"}, 
            {"text": "1"}, 
            {"text": "1d4"}, 
            {"text": "1d3"}
        ]},
        {"cells": [
            {"text": "Wrist Razor"}, 
            {"text": "1 sp"}, 
            {"text": ""}, 
            {"text": "S"}, 
            {"text": "S"}, 
            {"text": "1"}, 
            {"text": "1d6+1"}, 
            {"text": "1d4+1"}
        ]}
    ]
    
    table_data = {
        "rows": table_rows,
        "header_rows": 2  # Two header rows
    }
    
    # Create a synthetic "Weapons" H2 header block and insert it after Animals
    # Get the Animals block's bbox to position Weapons after it
    animals_bbox = animals_block.get("bbox", [37.0, 100.0, 300.0, 120.0])
    # Position Weapons below Animals (higher y value = lower on page)
    weapons_y = animals_bbox[3] + 50.0  # Start well below Animals
    
    weapons_header_block = {
        "type": "text",
        "bbox": [37.0, weapons_y, 300.0, weapons_y + 20.0],  # Position after Animals
        "lines": [
            {
                "bbox": [37.0, weapons_y, 300.0, weapons_y + 20.0],
                "spans": [
                    {
                        "text": "Weapons",
                        "font": "MSTT31c501",
                        "size": 10.8,  # H2 size
                        "flags": 4,
                        "color": "#ca5804"
                    }
                ]
            }
        ],
        "__new_weapons_table": table_data
    }
    
    logger.warning(f"Weapons block positioned at y={weapons_y}, Animals block was at y={animals_bbox[1]}-{animals_bbox[3]}")
    
    # Insert the weapons header+table block AFTER all the Animals table data blocks
    # This ensures: Animals header -> Animals data blocks -> Weapons header -> Weapons fragmented data (skipped)
    insertion_point = last_animals_data_idx + 1
    blocks.insert(insertion_point, weapons_header_block)
    
    logger.warning(f"New Weapons table created with {len(table_rows) - 2} weapon rows, inserted at block {insertion_point}, marked {len(blocks_to_skip)} blocks to skip")




def suppress_duplicate_weapon_column_headers(section_data: dict) -> None:
    """Suppress duplicate weapon table column headers and data in Equipment Descriptions section.
    
    The headers "Damage", "S-M", "Speed", "Type" and their associated dice data appear as duplicates 
    after Tun of Water in the Equipment Descriptions section. These are remnants of the fragmented 
    weapons table and should be suppressed.
    """
    import logging
    import re
    logger = logging.getLogger(__name__)
    
    logger.info("Suppressing duplicate weapon column headers and data")
    
    found_equipment_descriptions = False
    found_tun_of_water = False
    found_fire_kit = False
    suppress_count = 0
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            block_text = get_block_text(block).strip()
            
            # Check if this is Equipment Descriptions
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if "Equipment Descriptions" in text:
                        found_equipment_descriptions = True
                    elif found_equipment_descriptions and text.startswith("Tun of Water"):
                        found_tun_of_water = True
                    elif found_equipment_descriptions and text.startswith("Fire Kit"):
                        found_fire_kit = True
                    elif found_tun_of_water and not found_fire_kit:
                        # We're between Tun of Water and Fire Kit - check if this is duplicate data
                        # Duplicate column headers
                        if text in ["Damage", "S-M", "Speed", "Type"]:
                            block["__skip_render"] = True
                            suppress_count += 1
                            logger.info(f"Marking duplicate column header '{text}' to skip (page {page_idx}, block {block_idx})")
                            break
                        # Duplicate dice data (contains patterns like "1d4", "P/B", "S P", etc.)
                        # Match blocks that are very short and contain only weapon stat abbreviations
                        elif (re.search(r'\d\s*d\s*\d|P\s*/\s*[BS]', block_text) or 
                              (len(block_text) < 15 and re.match(r'^[SPMBL\s/+\d]+$', block_text))):
                            block["__skip_render"] = True
                            suppress_count += 1
                            logger.info(f"Marking duplicate dice data to skip (page {page_idx}, block {block_idx}): {block_text[:50]}")
                            break
    
    logger.info(f"Suppressed {suppress_count} duplicate weapon table fragments")


def apply_chapter_6_adjustments(section_data: dict) -> None:
    """Apply Chapter 6-specific adjustments to section data.
    
    This should be called during the transformation stage before rendering HTML.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Applying Chapter 6 adjustments, section has {len(section_data.get('pages', []))} pages")
    _merge_athasian_market_header(section_data)
    merge_armor_headers(section_data)
    _adjust_header_sizes(section_data)
    _extract_common_wages_table(section_data)
    _extract_initial_character_funds_table(section_data)
    _extract_weapon_materials_table(section_data)
    _extract_household_provisions_table(section_data)
    _extract_barding_table(section_data)
    _extract_transport_table(section_data)
    _extract_animals_table(section_data)
    _extract_new_weapons_table(section_data)
    _suppress_duplicate_weapon_column_headers(section_data)
    
    # Verify markers are attached
    with open('/tmp/chapter6_debug.txt', 'a') as f:
        f.write(f"\n=== Verifying table markers after all adjustments ===\n")
        for page_idx, page in enumerate(section_data.get('pages', [])):
            for block_idx, block in enumerate(page.get('blocks', [])):
                if '__weapon_materials_table' in block:
                    f.write(f"  FOUND __weapon_materials_table in page {page_idx}, block {block_idx}\n")
                if '__initial_character_funds_table' in block:
                    f.write(f"  FOUND __initial_character_funds_table in page {page_idx}, block {block_idx}\n")
                if block.get('__skip_render'):
                    first_line_text = ""
                    if block.get('lines') and len(block['lines']) > 0:
                        first_line_text = block['lines'][0].get('spans', [{}])[0].get('text', '')[:30]
                    f.write(f"  FOUND __skip_render in page {page_idx}, block {block_idx}, first line: '{first_line_text}'\n")
    
    logger.info("Chapter 6 adjustments complete")



