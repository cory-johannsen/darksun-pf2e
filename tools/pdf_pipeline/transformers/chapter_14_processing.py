"""
Chapter 14 Processing - Time and Movement

This module handles the extraction and transformation of Chapter 14,
which contains time, calendar, and movement rules for Dark Sun.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def apply_chapter_14_adjustments(section_data: dict) -> None:
    """
    Apply Chapter 14-specific processing adjustments.
    
    Args:
        section_data: The section data dictionary containing pages and blocks
    """
    logger.info("Starting Chapter 14 adjustments")
    
    _mark_athasian_calendar_table(section_data)
    _extract_overland_movement_table(section_data)
    _extract_terrain_costs_table(section_data)
    _extract_mounted_movement_table(section_data)
    _fix_whitespace_issues(section_data)
    _adjust_header_levels(section_data)
    
    logger.info("Chapter 14 adjustments complete")


def _mark_athasian_calendar_table(section_data: dict) -> None:
    """
    Mark the Athasian Calendar table headers and data for special handling.
    
    The table shows the Endlean Cycle (11 parts) and Seofean Cycle (7 parts).
    Headers and data need to be marked to prevent them from being treated as
    regular document headers and paragraphs.
    """
    logger.info("Marking Athasian Calendar table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # Process page 87 (first page) where the calendar table appears
    page = pages[0]
    blocks = page.get("blocks", [])
    
    for block in blocks:
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line in lines:
            spans = line.get("spans", [])
            for span in spans:
                text = span.get("text", "").strip()
                bbox = line.get("bbox", [])
                
                # Mark table headers (orange text, ~7.92 size)
                if text in ["The  Endlean Cycle", "The Endlean Cycle"]:
                    logger.debug(f"Marking 'The Endlean Cycle' as table header")
                    span["is_table_header"] = True
                    span["skip_render"] = True
                    block["skip_render"] = True
                
                elif text == "The Seofean Cycle":
                    logger.debug(f"Marking 'The Seofean Cycle' as table header")
                    span["is_table_header"] = True
                    span["skip_render"] = True
                    block["skip_render"] = True
                
                # Mark calendar table data (y-coords ~527-630)
                elif len(bbox) >= 4 and 516 <= bbox[1] <= 640:
                    # Left column (Endlean Cycle) - x < 120
                    if bbox[0] < 120 and text in [
                        "Ral", "Friend", "Desert", "Priest", "W i n d", "Wind",
                        "Dragon", "Mountain", "King", "Silt", "Enemy", "Guthay"
                    ]:
                        logger.debug(f"Marking '{text}' as Endlean Cycle data")
                        span["is_table_data"] = True
                        span["calendar_table"] = "endlean"
                        span["skip_render"] = True
                        block["skip_render"] = True
                    
                    # Right column (Seofean Cycle) - x > 150
                    elif bbox[0] > 150 and text in [
                        "Fury", "Contemplation", "Vengeance", "Slumber",
                        "Defiance", "Reverence", "Agitation"
                    ]:
                        logger.debug(f"Marking '{text}' as Seofean Cycle data")
                        span["is_table_data"] = True
                        span["calendar_table"] = "seofean"
                        span["skip_render"] = True
                        block["skip_render"] = True


def _extract_overland_movement_table(section_data: dict) -> None:
    """
    Extract and format the Overland Movement race table on Page 2.
    
    The table has 3 columns: Race, Movement Points, Force March
    And 8 rows of data for different races.
    
    Below the table is a legend with three items marked *, **, ***.
    """
    logger.info("=" * 80)
    logger.info("EXTRACTING OVERLAND MOVEMENT TABLE")
    logger.info("=" * 80)
    
    pages = section_data.get("pages", [])
    
    if len(pages) < 3:
        logger.warning("Not enough pages for Overland Movement table extraction")
        return
    
    page = pages[2]  # Page 2 (index 2)
    blocks = page.get("blocks", [])
    
    logger.info(f"Page 2 has {len(blocks)} blocks")
    
    # Define table data based on PDF structure
    # Block 53: "R a c e" (header - will be fixed by whitespace function)
    # Block 54: "Movement Points" and "Force March" (column headers)
    # Blocks 55-67: Race data
    
    table_rows = [
        {"race": "Human", "movement_points": "24", "force_march": "30"},
        {"race": "Dwarf", "movement_points": "12", "force_march": "15"},
        {"race": "Elf", "movement_points": "24", "force_march": "30"},
        {"race": "Half-elf", "movement_points": "24", "force_march": "30"},
        {"race": "Half-giant", "movement_points": "30", "force_march": "37"},
        {"race": "Halfling", "movement_points": "12", "force_march": "15"},
        {"race": "Mul**", "movement_points": "24", "force_march": "30"},
        {"race": "Thri-kreen***", "movement_points": "36", "force_march": "45"},
    ]
    
    # Find the "R a c e" block (block 53) and mark it for table extraction
    for block_idx, block in enumerate(blocks):
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line in lines:
            spans = line.get("spans", [])
            text = " ".join(s.get("text", "") for s in spans).strip()
            
            # Log ALL blocks that mention Human, Dwarf, or Race (debug logging can be removed later)
            # if "Human" in text or "Dwarf" in text or "R a c e" in text:
            #     logger.warning(f"OVERLAND: Block {block_idx} contains race data: '{text[:80]}'")
            
            if block_idx >= 50 and block_idx <= 55:
                logger.info(f"  Block {block_idx}: '{text[:30]}'")
            
            # Mark "R a c e" header block
            if text == "R a c e":
                logger.info(f"✅ Found 'R a c e' header at block {block_idx}")
                block["overland_movement_table"] = {
                    "type": "race_movement_table",
                    "headers": ["Race", "Movement Points", "Force March"],
                    "rows": table_rows,
                    "legend": [
                        "* For overland movement, an elf may add his Constitution score to 24 (his normal movement rate) or 30 (his forced march rate) to determine his actual movement in miles (or points) per day.",
                        "** This is for a normal 10-hour marching day. A mul can move for 20 hours per day on each of three consecutive days. The fourth day, however, must be one of rest in which the character only travels for 10 hours. A \"resting\" mul can still force march.",
                        "*** This is for a normal 10-hour marching day. A thri-kreen can always move for 20 hours per day."
                    ]
                }
                # Don't mark this block to skip - we need it to render the table!
                # block["skip_render"] = True
                
                # Mark blocks 54-67 to skip rendering (they'll be part of the table)
                for skip_idx in range(block_idx + 1, min(block_idx + 15, len(blocks))):
                    skip_block = blocks[skip_idx]
                    skip_lines = skip_block.get("lines", [])
                    if skip_lines:
                        skip_text = " ".join(
                            " ".join(s.get("text", "") for s in line.get("spans", []))
                            for line in skip_lines
                        ).strip()
                        
                        # Skip blocks that are part of the table
                        # Also skip any blocks with the condensed race list "Human Dwarf Elf Half-elf..."
                        if any(keyword in skip_text for keyword in [
                            "Movement Points", "Force March", "Human", "Dwarf", "E l f",
                            "Half-elf", "Half-giant", "Halfling", "M u l", "Thri-kreen***",
                            "24", "30", "12", "15", "36", "37", "45", "2 4", "3 0",
                            "Human Dwarf Elf"  # Condensed race list that appears as duplicate
                        ]):
                            skip_block["skip_render"] = True
                            logger.debug(f"OVERLAND: Marking block {skip_idx} to skip: {skip_text[:50]}")
                
                logger.info(f"✅ Created Overland Movement table with {len(table_rows)} rows")
                return
    
    logger.warning("❌ Could not find 'R a c e' header for Overland Movement table")


def _extract_terrain_costs_table(section_data: dict) -> None:
    """
    Extract and format the Terrain Costs table on Page 3.
    
    The table has 2 columns: Terrain Type, Movement Cost
    With 8 rows of terrain data.
    """
    logger.warning("=" * 80)
    logger.warning("EXTRACTING TERRAIN COSTS TABLE")
    logger.warning("=" * 80)
    
    pages = section_data.get("pages", [])
    if len(pages) < 4:
        logger.warning("Not enough pages for Terrain Costs table extraction")
        return
    
    page = pages[3]  # Page 3 (index 3)
    blocks = page.get("blocks", [])
    
    logger.info(f"Page 3 has {len(blocks)} blocks")
    
    # Define table data based on PDF structure
    # Block 13: "Terrain Type Movement Cost Stony Barrens"
    # Blocks 14-22: Terrain data
    
    table_rows = [
        {"terrain_type": "Stony Barrens", "movement_cost": "2"},
        {"terrain_type": "Sandy Wastes", "movement_cost": "3"},
        {"terrain_type": "Rocky Badlands", "movement_cost": "3"},
        {"terrain_type": "Mountains", "movement_cost": "8"},
        {"terrain_type": "Scrub Plains", "movement_cost": "1"},
        {"terrain_type": "Forest", "movement_cost": "4"},
        {"terrain_type": "Salt Flats", "movement_cost": "2"},
        {"terrain_type": "Boulder Fields", "movement_cost": "3"},
    ]
    
    # Find the "Terrain Type" block (block 13) and mark it for table extraction
    found_count = 0
    for block_idx, block in enumerate(blocks):
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Build full block text by concatenating all spans from all lines
        full_block_text = ""
        for line in lines:
            for span in line.get("spans", []):
                full_block_text += span.get("text", "")
        
        if block_idx >= 11 and block_idx <= 16:
            logger.info(f"  Block {block_idx}: '{full_block_text[:50]}'")
        
        # Mark "Terrain Type" header block
        # Note: The text is "Terrain TypeMovement CostStony Barrens" (no spaces between Type and Movement)
        if "Terrain Type" in full_block_text and "Movement Cost" in full_block_text:
            logger.info(f"✅ Found 'Terrain Type Movement Cost' header at block {block_idx}")
            found_count += 1
            block["terrain_costs_table"] = {
                "type": "terrain_costs_table",
                "headers": ["Terrain Type", "Movement Cost"],
                "rows": table_rows
            }
            # Don't mark this block to skip - we need it to render the table!
            
            # Mark blocks 14-22 to skip rendering (they'll be part of the table)
            for skip_idx in range(block_idx + 1, min(block_idx + 10, len(blocks))):
                skip_block = blocks[skip_idx]
                skip_lines = skip_block.get("lines", [])
                if skip_lines:
                    skip_text = " ".join(
                        " ".join(s.get("text", "") for s in line.get("spans", []))
                        for line in skip_lines
                    ).strip()
                    
                    # Skip blocks that are part of the table
                    if any(keyword in skip_text for keyword in [
                        "Stony Barrens", "Sandy Wastes", "Rocky Badlands", "Mountains",
                        "Scrub Plains", "Forest", "Salt Flats", "Boulder Fields",
                        "2 3", "8 2", "3 1 4"
                    ]):
                        skip_block["skip_render"] = True
                        logger.debug(f"Marking block {skip_idx} to skip (table data)")
            
            logger.info(f"✅ Created Terrain Costs table with {len(table_rows)} rows")
            return
    
    logger.warning("❌ Could not find 'Terrain Type Movement Cost' header for Terrain Costs table")


def _extract_mounted_movement_table(section_data: dict) -> None:
    """
    Extract and format the Mounted Overland Movement table.
    
    The table has 2 columns: Mount, Movement Points
    With 3 rows for Kank, Inix, and Mekillot.
    """
    logger.info("=" * 80)
    logger.info("EXTRACTING MOUNTED MOVEMENT TABLE")
    logger.info("=" * 80)
    
    pages = section_data.get("pages", [])
    logger.info(f"Chapter 14 has {len(pages)} pages total")
    
    # Define table data based on PDF structure and Dark Sun mount speeds
    table_rows = [
        {"mount": "Kank", "movement_points": "12"},
        {"mount": "Inix", "movement_points": "15"},
        {"mount": "Mekillot", "movement_points": "9"},
    ]
    
    # Search across all pages for the Mount header
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            lines = block.get("lines", [])
            if not lines:
                continue
            
            # Build full block text
            full_block_text = ""
            for line in lines:
                for span in line.get("spans", []):
                    full_block_text += span.get("text", "")
            
            # Look for the "Mount" header near "common mounts" text
            # or just "Mount" by itself as a header
            if full_block_text.strip() == "Mount":
                logger.info(f"✅ Found 'Mount' header at page {page_idx}, block {block_idx}")
                block["mounted_movement_table"] = {
                    "type": "mounted_movement_table",
                    "headers": ["Mount", "Movement Points"],
                    "rows": table_rows
                }
                
                # Mark subsequent blocks with mount data to skip rendering
                for skip_idx in range(block_idx + 1, min(block_idx + 10, len(blocks))):
                    skip_block = blocks[skip_idx]
                    skip_lines = skip_block.get("lines", [])
                    if skip_lines:
                        skip_text = " ".join(
                            " ".join(s.get("text", "") for s in line.get("spans", []))
                            for line in skip_lines
                        ).strip()
                        
                        # Skip blocks that contain mount names
                        if any(keyword in skip_text for keyword in [
                            "Kank", "Inix", "Mekillot"
                        ]) and not "These overland" in skip_text:  # Don't skip the paragraph after
                            skip_block["skip_render"] = True
                            logger.debug(f"Marking block {skip_idx} to skip (mount table data): {skip_text[:50]}")
                
                logger.info(f"✅ Created Mounted Movement table with {len(table_rows)} rows")
                return
    
    logger.warning("❌ Could not find 'Mount' header for Mounted Movement table")


def _fix_whitespace_issues(section_data: dict) -> None:
    """
    Fix whitespace issues in Chapter 14.
    
    Examples:
    - "W i n d" should be "Wind"
    - "M u l" should be "Mul"
    """
    logger.info("Fixing whitespace issues in Chapter 14")
    
    pages = section_data.get("pages", [])
    
    for page in pages:
        blocks = page.get("blocks", [])
        
        for block in blocks:
            lines = block.get("lines", [])
            
            for line in lines:
                spans = line.get("spans", [])
                
                for span in spans:
                    text = span.get("text", "")
                    
                    # Fix "W i n d" -> "Wind"
                    if text == "W i n d":
                        span["text"] = "Wind"
                        logger.debug("Fixed 'W i n d' -> 'Wind'")
                    
                    # Fix "M u l" -> "Mul"
                    elif text == "M u l":
                        span["text"] = "Mul"
                        logger.debug("Fixed 'M u l' -> 'Mul'")
                    
                    # Fix "E l f" -> "Elf"
                    elif text == "E l f":
                        span["text"] = "Elf"
                        logger.debug("Fixed 'E l f' -> 'Elf'")
                    
                    # Fix "R a c e" -> "Race"
                    elif text == "R a c e":
                        span["text"] = "Race"
                        logger.debug("Fixed 'R a c e' -> 'Race'")
                    
                    # Fix "Fo r" -> "For"
                    elif text == "Fo r":
                        span["text"] = "For"
                        logger.debug("Fixed 'Fo r' -> 'For'")


def _adjust_header_levels(section_data: dict) -> None:
    """
    Adjust header levels for Chapter 14.
    
    Per user feedback:
    - H2: "Year of the Messenger", "Starting the Campaign", "Water Consumption", 
          "Effects of Dehydration", "Rehydration", "Terrain Modifiers in Overland Movement",
          "Mounted Overland Movement", "Use of Vehicles"
    - H3: "Unusual Races", "Dehydration Effects Table", "Terrain Costs For Overland Movement",
          "Half-giants and Thri-kreen", "Care of Animals"
    - H4: "Thri-kreen:", "Half-giants:", "Kank:", "Inix:", "Mekillot:"
    
    The system determines header level from font size:
    - H1: size ~14.88 (default for headers)
    - H2: size ~12.96 
    - H3: size ~11.76
    - H4: size ~10.56
    """
    logger.info("Adjusting header levels for Chapter 14")
    
    # Define header level mappings with target sizes
    # H2: size ~12.96
    h2_headers = {
        "Year of the Messenger",
        "Starting the Campaign",
        "Water Consumption",
        "Effects of Dehydration",
        "Rehydration",
        "Terrain Modifiers in Overland Movement",
        "Mounted Overland Movement",
        "Use of Vehicles"
    }
    
    # H3: size ~11.76 (or use a smaller size if needed)
    h3_headers = {
        "Unusual Races",
        "Dehydration Effects Table",
        "Terrain Costs For Overland Movement",
        "Half-giants and Thri-kreen",
        "Care of Animals"
    }
    
    # H4: size ~10.56
    h4_headers = {
        "Thri-kreen:",
        "Half-giants:",
        "Kank:",
        "Inix:",
        "Mekillot:"
    }
    
    # Target font sizes for each level
    H2_SIZE = 12.96
    H3_SIZE = 10.8  # Slightly smaller for H3
    H4_SIZE = 9.6   # Even smaller for H4
    
    adjusted_count = 0
    pages = section_data.get("pages", [])
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            lines = block.get("lines", [])
            
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                
                for span_idx, span in enumerate(spans):
                    text = span.get("text", "").strip()
                    original_size = span.get("size", 0)
                    
                    # Check if this text matches any of our header mappings
                    if text in h2_headers:
                        span["size"] = H2_SIZE
                        span["header_level"] = 2
                        logger.debug(f"Set '{text}' to H2 size {H2_SIZE} (was {original_size:.2f}, page={page_idx}, block={block_idx})")
                        adjusted_count += 1
                    elif text in h3_headers:
                        span["size"] = H3_SIZE
                        span["header_level"] = 3
                        logger.debug(f"Set '{text}' to H3 size {H3_SIZE} (was {original_size:.2f}, page={page_idx}, block={block_idx})")
                        adjusted_count += 1
                    elif text in h4_headers:
                        span["size"] = H4_SIZE
                        span["header_level"] = 4
                        logger.debug(f"Set '{text}' to H4 size {H4_SIZE} (was {original_size:.2f}, page={page_idx}, block={block_idx})")
                        adjusted_count += 1
    
    logger.info(f"Adjusted {adjusted_count} header levels in Chapter 14")

