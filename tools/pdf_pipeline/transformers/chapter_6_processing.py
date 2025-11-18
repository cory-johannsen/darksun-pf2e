"""Chapter 6 (Money and Equipment) specific processing logic."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List

# Import extracted functions from chapter_6 sub-modules
from .chapter_6.common import (
    normalize_plain_text as _normalize_plain_text,
    clean_whitespace as _clean_whitespace,
    adjust_header_sizes as _adjust_header_sizes,
    split_service_header as _split_service_header,
    split_shields_header as _split_shields_header,
    get_block_text as _get_block_text,
    merge_studded_leather_header as _merge_studded_leather_header,
    merge_chain_splint_header as _merge_chain_splint_header,
    extract_table_cell_text as _extract_table_cell_text,
    merge_armor_headers as _merge_armor_headers,
)
from .chapter_6.weapons import (
    extract_weapon_materials_table as _extract_weapon_materials_table,
    extract_new_weapons_table as _extract_new_weapons_table,
    suppress_duplicate_weapon_column_headers as _suppress_duplicate_weapon_column_headers,
)
from .chapter_6.armor import extract_barding_table as _extract_barding_table
from .chapter_6.transport import (
    extract_transport_table as _extract_transport_table,
    extract_animals_table as _extract_animals_table,
)
from .chapter_6.equipment import (
    extract_household_provisions_table as _extract_household_provisions_table,
    extract_common_wages_table as _extract_common_wages_table,
)


# _normalize_plain_text - MOVED to chapter_6/common.py


# _clean_whitespace - MOVED to chapter_6/common.py


# _adjust_header_sizes - MOVED to chapter_6/common.py


# _split_service_header - MOVED to chapter_6/common.py


# _split_shields_header - MOVED to chapter_6/common.py


# _merge_armor_headers - MOVED to chapter_6/common.py


# _get_block_text - MOVED to chapter_6/common.py


# _merge_studded_leather_header - MOVED to chapter_6/common.py


# _merge_chain_splint_header - MOVED to chapter_6/common.py


# _extract_table_cell_text - MOVED to chapter_6/common.py


# _extract_common_wages_table - MOVED to chapter_6/equipment.py


def _extract_initial_character_funds_table(section_data: dict) -> None:
    """Extract and format the Initial Character Funds table.

    The table has:
    - 2 columns: Character Group, Die Range
    - 6 rows (1 header + 5 data rows)
    - Die Range format: "#d# x #cp"
    
    Data rows:
    - Warrior: 5d4 x 30cp
    - Wizard: (1d4+1) x 30cp
    - Rogue: 2d6 x 30cp
    - Priest: 3d6 x 30cp
    - Psionicist: 3d4 x 30cp
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Debug: Write to file
    with open('/tmp/chapter6_debug.txt', 'a') as f:
        f.write(f"\n=== _extract_initial_character_funds_table called ===\n")
        f.write(f"Searching in {len(section_data.get('pages', []))} pages\n")
    
    logger.info(f"Searching for Initial Character Funds table in {len(section_data.get('pages', []))} pages")
    for page_idx, page in enumerate(section_data.get("pages", [])):
        if "blocks" not in page:
            logger.warning(f"Page {page_idx} has no blocks")
            continue
        blocks = page["blocks"]
        
        # Debug: Write to file
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"  Checking page {page_idx}: {len(blocks)} blocks\n")
        
        logger.info(f"Page {page_idx} has {len(blocks)} blocks")
        
        # Find the "Initial Character Funds" header
        initial_funds_idx = None
        initial_funds_bbox = None
        for idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            # Collect all text from this block for logging
            block_texts = []
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    block_texts.append(text)
                    if "Initial Character Funds" in text:
                        initial_funds_idx = idx
                        initial_funds_bbox = block.get("bbox", [37.439998626708984, 200.0, 300.0, 280.0])
                        with open('/tmp/chapter6_debug.txt', 'a') as f:
                            f.write(f"    FOUND at block {idx}: '{text}'\n")
                            f.write(f"    Block bbox: {initial_funds_bbox}\n")
                        logger.info(f"Found 'Initial Character Funds' at block index {idx} on page {page_idx}, bbox={initial_funds_bbox}")
                        break
                if initial_funds_idx is not None:
                    break
            if initial_funds_idx is not None:
                break
        
        if initial_funds_idx is None:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    NOT FOUND on page {page_idx}\n")
            logger.warning(f"Could not find 'Initial Character Funds' header on page {page_idx}")
            continue
        
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"    Found Initial Character Funds at block {initial_funds_idx}, searching for Athasian Market...\n")
        
        # Find where "Athasian Market" starts (next section)
        athasian_market_idx = None
        athasian_market_bbox = None
        for idx in range(initial_funds_idx + 1, len(blocks)):
            block = blocks[idx]
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if "Athasian Market" in text or "List of" in text:
                            athasian_market_idx = idx
                            athasian_market_bbox = block.get("bbox")
                            with open('/tmp/chapter6_debug.txt', 'a') as f:
                                f.write(f"    FOUND Athasian Market at block {idx}: '{text}'\n")
                                f.write(f"    Athasian Market bbox: {athasian_market_bbox}\n")
                            logger.info(f"Found 'Athasian Market' at block index {idx}, bbox={athasian_market_bbox}")
                            break
                    if athasian_market_idx is not None:
                        break
            if athasian_market_idx is not None:
                break
        
        # Remove all blocks between Initial Character Funds and Athasian Market
        # These are the fragmented table pieces and malformed headers
        if athasian_market_idx is not None:
            num_blocks_to_remove = athasian_market_idx - initial_funds_idx - 1
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    Removing {num_blocks_to_remove} blocks between them\n")
            logger.info(f"Removing {num_blocks_to_remove} blocks between Initial Character Funds and Athasian Market")
            # Remove in reverse order to maintain indices
            for idx in reversed(range(initial_funds_idx + 1, athasian_market_idx)):
                del blocks[idx]
            
            # Recalculate athasian_market_idx after deletions
            athasian_market_idx = initial_funds_idx + 1
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    After removal, Athasian Market is now at block {athasian_market_idx}\n")
        else:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    NOT FOUND: Athasian Market\n")
            logger.warning(f"Could not find 'Athasian Market' header after 'Initial Character Funds'")
        
        # Build the table structure from source specification
        # This data is extracted from the PDF (pages 54-55) and validated against the source
        header_row = {"cells": [
            {"text": "Character Group"},
            {"text": "Die Range"}
        ]}
        
        # Data rows: 5 character classes
        data_rows = [
            {"cells": [{"text": "Warrior"}, {"text": "5d4 x 30cp"}]},
            {"cells": [{"text": "Wizard"}, {"text": "(1d4+1) x 30cp"}]},
            {"cells": [{"text": "Rogue"}, {"text": "2d6 x 30cp"}]},
            {"cells": [{"text": "Priest"}, {"text": "3d6 x 30cp"}]},
            {"cells": [{"text": "Psionicist"}, {"text": "3d4 x 30cp"}]},
        ]
        
        all_rows = [header_row] + data_rows
        
        # Use the bbox from the Initial Character Funds header, adjusted to place table just below it
        # CRITICAL: For multi-column rendering, the table's y-coordinate determines when it will be consumed.
        # The multi-column rendering processes left and right columns in ascending y order, consuming
        # full-width items when their y is less than or equal to the current column item's y.
        # Solution: Set the table y to be just after Initial Character Funds (y=149.90) and before
        # the next right-column item (y=162.34), so it gets consumed immediately after Initial Character Funds.
        if initial_funds_bbox:
            # Set y to be just after Initial Character Funds to ensure it's consumed at the right time
            table_y_start = initial_funds_bbox[3] + 0.5  # Just below the Initial Character Funds header
            table_y_end = table_y_start + 10  # Small height to keep it compact
            table_bbox = [
                initial_funds_bbox[0],  # Same left x as Initial Character Funds
                table_y_start,  # Start just below Initial Character Funds
                initial_funds_bbox[2],  # Same right x
                table_y_end  # Compact height
            ]
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"    Calculated table bbox for proper multi-column rendering:\n")
                f.write(f"      Initial Funds y range: {initial_funds_bbox[1]} to {initial_funds_bbox[3]}\n")
                f.write(f"      Table y range: {table_y_start} to {table_y_end}\n")
        else:
            table_bbox = [37.439998626708984, 150.0, 300.0, 160.0]  # Fallback
        
        table = {
            "rows": all_rows,
            "header_rows": 1,
            "bbox": table_bbox
        }
        
        # Instead of inserting a separate table block, attach the table data directly to the
        # "Initial Character Funds" header block. This ensures the table will be rendered
        # immediately after the header, bypassing the complex multi-column rendering logic.
        blocks[initial_funds_idx]["__initial_character_funds_table"] = table
        
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"    SUCCESS: Attached table data to Initial Character Funds header block at index {initial_funds_idx}\n")
            f.write(f"    Page now has {len(blocks)} blocks\n")
        
        # Break after processing the first (and only) Initial Character Funds section
        break


# _extract_weapon_materials_table - MOVED to chapter_6/weapons.py


def _merge_athasian_market_header(section_data: dict) -> None:
    """Merge 'Athasian Market: List of' and 'Provisions' into a single header.
    
    In the source PDF, this header is split across two lines within the same block
    but should be treated as a single header.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            i = 0
            while i < len(lines) - 1:
                line = lines[i]
                next_line = lines[i + 1]
                
                # Check if this line contains "Athasian Market: List of"
                found_first_part = False
                first_span = None
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if "Athasian Market" in text and "List of" in text:
                        found_first_part = True
                        first_span = span
                        break
                
                if not found_first_part:
                    i += 1
                    continue
                
                # Check if next line contains "Provisions" as a header
                found_second_part = False
                for span in next_line.get("spans", []):
                    text = span.get("text", "").strip()
                    # Check if this is just "Provisions" as a header (same color, font)
                    if text == "Provisions" and span.get("color") == "#ca5804":
                        found_second_part = True
                        break
                
                if found_second_part:
                    # Merge the headers: append " Provisions" to the first header
                    first_span["text"] = "Athasian Market: List of Provisions"
                    logger.info("Merged 'Athasian Market: List of' and 'Provisions' headers")
                    
                    # Remove the second line (Provisions)
                    lines.pop(i + 1)
                    logger.info("Removed separate 'Provisions' header line")
                    break  # Exit the while loop after merging
                
                i += 1


# _extract_household_provisions_table - MOVED to chapter_6/equipment.py

# _extract_barding_table - MOVED to chapter_6/armor.py


# _extract_transport_table - MOVED to chapter_6/transport.py

# _extract_new_weapons_table - MOVED to chapter_6/weapons.py


# _extract_animals_table - MOVED to chapter_6/transport.py

# _suppress_duplicate_weapon_column_headers - MOVED to chapter_6/weapons.py


def apply_chapter_6_adjustments(section_data: dict) -> None:
    """Apply Chapter 6-specific adjustments to section data.
    
    This should be called during the transformation stage before rendering HTML.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Applying Chapter 6 adjustments, section has {len(section_data.get('pages', []))} pages")
    _merge_athasian_market_header(section_data)
    _merge_armor_headers(section_data)
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

