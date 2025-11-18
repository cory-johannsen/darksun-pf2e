"""Chapter 7 (Magic) processing - header level adjustments and spell parsing.

This module adjusts header sizes in the Magic chapter to properly reflect
the document hierarchy, and parses spell lists into structured data.

[SEGMENT_PROCESSING] This file contains chapter-specific processing logic.
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def _clean_text(text: str) -> str:
    """Clean text extracted from PDF by removing problematic Unicode characters.
    
    Args:
        text: The raw text from PDF extraction
        
    Returns:
        Cleaned text with proper spacing and characters
    """
    # Replace Windows-1252 curly quotes and apostrophes with regular characters
    replacements = {
        '\x91': "'",  # LEFT SINGLE QUOTATION MARK
        '\x92': "'",  # RIGHT SINGLE QUOTATION MARK
        '\x93': '"',  # LEFT DOUBLE QUOTATION MARK
        '\x94': '"',  # RIGHT DOUBLE QUOTATION MARK
        '\x96': '-',  # EN DASH
        '\x97': '--', # EM DASH
        '\xa0': ' ',  # NON-BREAKING SPACE
    }
    
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)
    
    return text


def _clean_section_text(section_data: dict) -> None:
    """Clean all text in section data by removing problematic Unicode characters.
    
    This function modifies the section_data in place, cleaning all text in all spans
    to remove Windows-1252 characters that cause issues in HTML rendering.
    
    Args:
        section_data: The raw section data from PDF extraction (modified in place)
    """
    logger.info("Cleaning text in Chapter 7 section data")
    
    cleaned_count = 0
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    original_text = span.get("text", "")
                    cleaned_text = _clean_text(original_text)
                    
                    if original_text != cleaned_text:
                        span["text"] = cleaned_text
                        cleaned_count += 1
    
    logger.info(f"Cleaned {cleaned_count} text spans in Chapter 7")


def _merge_wizardly_magic_intro(section_data: dict) -> None:
    """Merge the text blocks between 'Wizardly Magic' and 'Defiling' into a single paragraph.
    
    The text between these two headers should be one continuous paragraph, but it's
    extracted as multiple separate blocks due to line breaks in the 2-column PDF layout.
    
    Expected text (one paragraph):
    "Wizards draw their magical energies from the living things and life-giving 
    elements around them. Preservers cast spells in harmony with nature, using 
    their magic so as to return to the land what they take from it. Defilers care 
    nothing for such harmony and damage the land with every spell they cast."
    """
    logger.debug("Merging Wizardly Magic intro paragraph")
    
    pages = section_data.get("pages", [])
    if not pages or len(pages) < 4:
        logger.warning("Not enough pages for Wizardly Magic section")
        return
    
    # The Wizardly Magic section is on page 3 (index 3)
    page = pages[3]
    blocks = page.get("blocks", [])
    
    # Find the Wizardly Magic header block
    wizardly_magic_idx = None
    defiling_idx = None
    
    for idx, block in enumerate(blocks):
        block_text = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                block_text += span.get("text", "")
        
        if "Wizardly Magic" in block_text:
            wizardly_magic_idx = idx
            logger.debug(f"Found Wizardly Magic header at block {idx}")
        elif "Defiling" in block_text and wizardly_magic_idx is not None:
            defiling_idx = idx
            logger.debug(f"Found Defiling header at block {idx}")
            break
    
    if wizardly_magic_idx is None or defiling_idx is None:
        logger.warning("Could not find Wizardly Magic or Defiling headers")
        return
    
    # Blocks between the headers (should be 36-40, which is wizardly_magic_idx+1 to defiling_idx-1)
    blocks_to_merge_indices = list(range(wizardly_magic_idx + 1, defiling_idx))
    
    if not blocks_to_merge_indices:
        logger.warning("No blocks to merge between Wizardly Magic and Defiling")
        return
    
    logger.info(f"Merging {len(blocks_to_merge_indices)} blocks into one paragraph (blocks {blocks_to_merge_indices[0]}-{blocks_to_merge_indices[-1]})")
    
    # Collect all lines from all blocks to merge
    merged_lines = []
    merged_bbox = None
    
    for idx in blocks_to_merge_indices:
        block = blocks[idx]
        block_lines = block.get("lines", [])
        merged_lines.extend(block_lines)
        
        # Expand bbox to include this block
        block_bbox = block.get("bbox", [])
        if merged_bbox is None:
            merged_bbox = block_bbox.copy()
        else:
            # Expand to include new block
            merged_bbox[0] = min(merged_bbox[0], block_bbox[0])  # min x0
            merged_bbox[1] = min(merged_bbox[1], block_bbox[1])  # min y0
            merged_bbox[2] = max(merged_bbox[2], block_bbox[2])  # max x1
            merged_bbox[3] = max(merged_bbox[3], block_bbox[3])  # max y1
    
    # Create the merged block
    merged_block = {
        "type": "text",
        "bbox": merged_bbox,
        "lines": merged_lines
    }
    
    # Replace the first block with the merged block
    blocks[blocks_to_merge_indices[0]] = merged_block
    
    # Remove the other blocks (in reverse order to maintain indices)
    for idx in reversed(blocks_to_merge_indices[1:]):
        del blocks[idx]
    
    page["blocks"] = blocks
    logger.info(f"Successfully merged Wizardly Magic intro into single paragraph")


def apply_chapter_7_adjustments(section_data: dict) -> None:
    """Apply chapter 7 (Magic) adjustments to section data.
    
    Args:
        section_data: The raw section data from PDF extraction (modified in place)
    """
    logger.info("Applying chapter 7 (Magic) adjustments")
    
    # Clean all text in the section data (remove problematic Unicode characters)
    _clean_section_text(section_data)
    
    # Merge Wizardly Magic intro paragraph (must be done first, before spell parsing)
    _merge_wizardly_magic_intro(section_data)
    
    # Adjust header sizes for sphere sections
    _adjust_sphere_header_sizes(section_data)
    
    # Adjust header sizes for defiling section
    _adjust_defiling_header_sizes(section_data)
    
    # Extract Defiler Magical Destruction Table
    _extract_defiler_destruction_table(section_data)
    
    # Parse spell lists and create structured data
    spells_data = _parse_spell_lists(section_data)
    
    # Save structured spell data to JSON
    _save_spell_data(spells_data)
    
    # Mark spell blocks for special rendering (as list items)
    _mark_spell_blocks_for_rendering(section_data, spells_data)


def _adjust_sphere_header_sizes(section_data: dict) -> None:
    """Adjust sphere header font sizes to make them H3 (subheaders under Priestly Magic).
    
    Headers that should be H3 (size 9.6):
    - Sphere of Earth
    - Sphere of Air
    - Sphere of Fire
    - Sphere of Water
    - Sphere of the Cosmos
    
    These are currently extracted as size 10.8 (H2) but should be H3 since they are
    subsections under "Priestly Magic" (H1, size 14.88).
    """
    logger.debug("Adjusting sphere header sizes from H2 (10.8) to H3 (9.6)")
    
    # Track which sphere we've found to avoid adjusting duplicates
    sphere_headers_adjusted = set()
    
    # List of sphere headers that should be H3
    sphere_h3_headers = [
        "Sphere of Earth",
        "Sphere of Air",
        "Sphere of Fire",
        "Sphere of Water",
        "Sphere of the Cosmos"
    ]
    
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    
                    # Check if this is one of the sphere headers
                    if text in sphere_h3_headers:
                        # Only adjust the first occurrence of each sphere header
                        if text not in sphere_headers_adjusted:
                            logger.debug(f"Adjusting '{text}' from size {span.get('size')} to 9.6 (H3)")
                            span["size"] = 9.6
                            span["font"] = "MSTT31c501"  # Header font
                            span["color"] = "#ca5804"     # Header color to ensure anchoring
                            sphere_headers_adjusted.add(text)
    
    logger.info(f"Adjusted {len(sphere_headers_adjusted)} sphere headers to H3 level")


def _adjust_defiling_header_sizes(section_data: dict) -> None:
    """Adjust defiling section header font sizes to establish proper hierarchy.
    
    Header adjustments:
    - "Defiling" -> H2 (size 10.8) - already correct, but ensure it's marked as H2
    - "Casting Defiler Spells:" -> H3 (size 9.6) - currently 8.88, needs to be promoted to H3
    - "Defiler Magical Destruction Table" -> H3 (size 9.6) - currently 8.88, needs to be promoted to H3
    
    Per [HEADER_NUMERALS], only H1 headers get roman numerals, so H2 and H3 should not have them.
    The raw extraction shows:
    - "Defiling" is already size 10.8 (H2)
    - "Casting Defiler Spells:" is size 8.88 (normal text)
    - "Defiler Magical Destruction Table" is size 8.88 (normal text)
    """
    logger.info("Adjusting defiling section header sizes")
    
    # Track which headers we've adjusted to avoid duplicates
    defiling_headers_adjusted = set()
    
    # Map of header text to target size (and current size for matching)
    # Format: text -> (current_size, target_size, header_level)
    defiling_headers = {
        "Defiling": (10.8, 10.8, "H2"),  # Already correct size, just ensure marking
        "Casting Defiler Spells:": (8.88, 9.6, "H3"),  # Promote from text to H3
        "Defiler Magical Destruction Table": (8.88, 9.6, "H3")  # Promote from text to H3
    }
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    
                    # Check if this is one of the defiling headers
                    if text in defiling_headers:
                        # Only adjust the first occurrence of each header
                        if text not in defiling_headers_adjusted:
                            current_size, target_size, header_level = defiling_headers[text]
                            original_size = span.get('size')
                            
                            # Check if the size matches approximately (allow for float precision)
                            if abs(original_size - current_size) < 0.5:
                                logger.info(f"Adjusting '{text}' from size {original_size:.2f} to {target_size} ({header_level}), page={page_idx}, block={block_idx}")
                                span["size"] = target_size
                                span["font"] = "MSTT31c501"  # Header font
                                span["color"] = "#ca5804"     # Header color to ensure anchoring
                                defiling_headers_adjusted.add(text)
    
    logger.info(f"Adjusted {len(defiling_headers_adjusted)} defiling headers to proper levels")


def _extract_defiler_destruction_table(section_data: dict) -> None:
    """Extract and structure the Defiler Magical Destruction Table.
    
    Table structure:
    - 10 columns: "Terrain Type" followed by 9 spell level columns (1-9)
    - 12 rows total: 1 header row, 1 spell level row, 10 terrain type rows
    
    Refactored to follow best practices - broken into focused helper functions.
    
    Args:
        section_data: The raw section data from PDF extraction (modified in place)
    """
    logger.info("Extracting Defiler Magical Destruction Table")
    
    pages = section_data.get("pages", [])
    if len(pages) < 5:
        logger.warning("Not enough pages for Defiler Magical Destruction Table")
        return
    
    page = pages[4]
    blocks = page.get("blocks", [])
    
    # Find headers
    table_header_idx, column_headers_idx = _find_defiler_table_headers(blocks)
    if table_header_idx is None or column_headers_idx is None:
        return
    
    # Extract data
    terrain_types = _get_defiler_terrain_types()
    table_data, accumulated = _extract_defiler_terrain_data(
        blocks, column_headers_idx, terrain_types
    )
    table_data = _assign_accumulated_numbers(
        table_data, accumulated, terrain_types
    )
    
    # Build and insert table
    table_rows = _build_defiler_table_rows(table_data, terrain_types)
    table = _create_defiler_table_structure(table_rows, blocks, table_header_idx)
    
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table)
    
    logger.info(f"Created Defiler Magical Destruction Table with {len(table_rows)} rows")
    
    # Mark blocks to skip
    _mark_defiler_blocks_to_skip(blocks, column_headers_idx, terrain_types)


def _find_defiler_table_headers(blocks: List[Dict]) -> Tuple[Optional[int], Optional[int]]:
    """Find the Defiler table header and column header blocks.
    
    Args:
        blocks: List of block dictionaries
        
    Returns:
        Tuple of (table_header_idx, column_headers_idx) or (None, None)
    """
    table_header_idx = None
    column_headers_idx = None
    
    for idx, block in enumerate(blocks):
        block_text = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                block_text += span.get("text", "")
        
        block_text = block_text.strip()
        
        if "Defiler Magical Destruction Table" in block_text:
            table_header_idx = idx
            logger.debug(f"Found table header at block {idx}")
        elif "Terrain Type" in block_text and "Spell Level" in block_text:
            column_headers_idx = idx
            logger.debug(f"Found column headers at block {idx}")
    
    if table_header_idx is None:
        logger.warning("Could not find Defiler Magical Destruction Table header")
    if column_headers_idx is None:
        logger.warning("Could not find table column headers")
    
    return table_header_idx, column_headers_idx


def _get_defiler_terrain_types() -> List[str]:
    """Get the ordered list of terrain types for the Defiler table.
    
    Returns:
        List of terrain type names
    """
    return [
        "Stony Barrens",
        "Sandy Wastes",
        "Rocky Badlands",
        "Salt Flats",
        "Boulder Fields",
        "Silt Sea",
        "Mountains",
        "Scrub Plains",
        "Verdant Belts",
        "Forest"
    ]


def _extract_defiler_terrain_data(
    blocks: List[Dict],
    column_headers_idx: int,
    terrain_types: List[str]
) -> Tuple[Dict[str, List[str]], List[str]]:
    """Extract terrain data and accumulated numbers from blocks.
    
    Args:
        blocks: List of block dictionaries
        column_headers_idx: Index of column headers block
        terrain_types: List of terrain type names
        
    Returns:
        Tuple of (table_data dict, accumulated_numbers list)
    """
    table_data = {}
    accumulated_numbers = []
    pattern = re.compile(r'\b(\d+)\b')
    
    for idx in range(column_headers_idx + 1, len(blocks)):
        block = blocks[idx]
        block_text = _get_block_text(block)
        
        # Stop at paragraph break
        if "The number shown is the radius" in block_text:
            logger.debug("Reached end of table data")
            break
        
        # Try to extract terrain data
        found_terrain = _extract_terrain_from_block(
            block_text, terrain_types, table_data, pattern
        )
        
        # If no terrain found, check for pure numeric data
        if not found_terrain and block_text.replace(' ', '').isdigit():
            digits = [d for d in block_text if d.isdigit()]
            accumulated_numbers.extend(digits)
            logger.debug(f"Accumulated {len(digits)} digits: {digits}")
    
    return table_data, accumulated_numbers


def _get_block_text(block: Dict) -> str:
    """Extract and normalize text from a block.
    
    Args:
        block: Block dictionary
        
    Returns:
        Normalized block text
    """
    block_text = ""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            block_text += span.get("text", " ")
    return " ".join(block_text.split())


def _extract_terrain_from_block(
    block_text: str,
    terrain_types: List[str],
    table_data: Dict[str, List[str]],
    pattern: re.Pattern
) -> bool:
    """Extract terrain type data from a block of text.
    
    Args:
        block_text: Text to extract from
        terrain_types: List of terrain type names
        table_data: Dictionary to update with extracted data
        pattern: Regex pattern for extracting numbers
        
    Returns:
        True if terrain was found and extracted
    """
    for terrain in terrain_types:
        if terrain in block_text and terrain not in table_data:
            _process_terrain_entry(
                terrain, block_text, terrain_types, table_data, pattern
            )
            return True
    return False


def _process_terrain_entry(
    terrain: str,
    block_text: str,
    terrain_types: List[str],
    table_data: Dict[str, List[str]],
    pattern: re.Pattern
) -> None:
    """Process a terrain entry and extract its values.
    
    Args:
        terrain: Terrain type name
        block_text: Text containing the terrain
        terrain_types: List of all terrain types
        table_data: Dictionary to update
        pattern: Regex pattern for numbers
    """
    terrain_idx = block_text.index(terrain)
    after_terrain = block_text[terrain_idx + len(terrain):]
    
    # Check for next terrain in same block
    next_terrain_pos = len(after_terrain)
    next_terrain_name = None
    for next_terrain in terrain_types[terrain_types.index(terrain)+1:]:
        if next_terrain in after_terrain:
            next_terrain_pos = after_terrain.index(next_terrain)
            next_terrain_name = next_terrain
            break
    
    # Extract numbers for this terrain
    numbers_text = after_terrain[:next_terrain_pos]
    numbers = pattern.findall(numbers_text)
    
    if len(numbers) >= 9:
        table_data[terrain] = numbers[:9]
        logger.debug(f"Extracted data for '{terrain}': {numbers[:9]}")
    elif len(numbers) == 1 and len(numbers[0]) >= 9:
        table_data[terrain] = list(numbers[0][:9])
        logger.debug(f"Extracted fragmented data for '{terrain}': {table_data[terrain]}")
    else:
        table_data[terrain] = numbers
        logger.debug(f"Partial data for '{terrain}': {numbers}")
    
    # Process next terrain if found
    if next_terrain_name:
        after_next = after_terrain[next_terrain_pos + len(next_terrain_name):]
        next_numbers = pattern.findall(after_next)
        if len(next_numbers) >= 9:
            table_data[next_terrain_name] = next_numbers[:9]
        elif len(next_numbers) == 1 and len(next_numbers[0]) >= 9:
            table_data[next_terrain_name] = list(next_numbers[0][:9])
        else:
            table_data[next_terrain_name] = next_numbers


def _assign_accumulated_numbers(
    table_data: Dict[str, List[str]],
    accumulated: List[str],
    terrain_types: List[str]
) -> Dict[str, List[str]]:
    """Assign accumulated numbers to missing terrain types.
    
    Args:
        table_data: Current table data
        accumulated: List of accumulated number strings
        terrain_types: List of terrain type names
        
    Returns:
        Updated table_data dictionary
    """
    missing_terrains = [t for t in terrain_types if t not in table_data]
    
    if missing_terrains and accumulated:
        logger.debug(
            f"Assigning {len(accumulated)} accumulated digits to "
            f"{len(missing_terrains)} missing terrains"
        )
        
        for terrain in missing_terrains:
            if len(accumulated) >= 9:
                table_data[terrain] = accumulated[:9]
                accumulated = accumulated[9:]
                logger.debug(f"Assigned fragmented data to '{terrain}'")
            else:
                logger.warning(
                    f"Not enough accumulated data for '{terrain}' "
                    f"(need 9, have {len(accumulated)})"
                )
    
    # Final check
    missing = [t for t in terrain_types if t not in table_data]
    if missing:
        logger.warning(f"Still missing data for terrain types: {missing}")
    
    return table_data


def _build_defiler_table_rows(
    table_data: Dict[str, List[str]],
    terrain_types: List[str]
) -> List[Dict]:
    """Build table rows from extracted terrain data.
    
    Args:
        table_data: Dictionary mapping terrain types to values
        terrain_types: Ordered list of terrain types
        
    Returns:
        List of row dictionaries
    """
    table_rows = []
    
    # Header row
    header_row = {
        "cells": [{"text": "Terrain Type"}] +
                 [{"text": str(i), "header": True} for i in range(1, 10)]
    }
    table_rows.append(header_row)
    
    # Data rows
    for terrain in terrain_types:
        if terrain in table_data:
            values = table_data[terrain][:]
            while len(values) < 9:
                values.append("")
            
            row_cells = [{"text": terrain}] + [{"text": v} for v in values[:9]]
            table_rows.append({"cells": row_cells})
        else:
            logger.warning(f"No data found for terrain: {terrain}")
    
    return table_rows


def _create_defiler_table_structure(
    table_rows: List[Dict],
    blocks: List[Dict],
    table_header_idx: int
) -> Dict:
    """Create the final table structure.
    
    Args:
        table_rows: List of table rows
        blocks: List of blocks
        table_header_idx: Index of table header block
        
    Returns:
        Table dictionary
    """
    return {
        "bbox": [50, blocks[table_header_idx].get("bbox", [0, 0, 0, 0])[1] + 20, 500, 400],
        "rows": table_rows,
        "header_rows": 1,
        "_table_name": "Defiler Magical Destruction Table"
    }


def _mark_defiler_blocks_to_skip(
    blocks: List[Dict],
    column_headers_idx: int,
    terrain_types: List[str]
) -> None:
    """Mark blocks containing table data to skip rendering.
    
    Args:
        blocks: List of block dictionaries
        column_headers_idx: Index of column headers block
        terrain_types: List of terrain type names
    """
    blocks[column_headers_idx]["__skip_render"] = True
    
    for idx in range(column_headers_idx + 1, len(blocks)):
        block = blocks[idx]
        block_text = _get_block_text(block)
        
        # Check if contains terrain data
        has_terrain = any(terrain in block_text for terrain in terrain_types)
        
        if has_terrain:
            block["__skip_render"] = True
            logger.debug(f"Marked block {idx} for skipping")
        
        # Stop at continuation text
        if "The number shown is the radius" in block_text:
            break
    
    logger.info("Marked table-related blocks to skip text rendering")


def _parse_spell_lists(section_data: dict) -> dict:
    """Parse spell lists from sphere sections.
    
    Args:
        section_data: The raw section data from PDF extraction
        
    Returns:
        Dictionary mapping sphere names to lists of spell dictionaries
        Format: {
            "Sphere of Earth": [
                {"name": "Magical Stone", "level": "1st", "page": 58, "block": 5},
                ...
            ],
            ...
        }
    """
    logger.info("Parsing spell lists from sphere sections")
    
    # Regex pattern to match spell format: "Spell Name (level)"
    # Matches things like "Magical Stone (1st)" or "Transport Via Plants (6th)"
    spell_pattern = re.compile(r'^(.+?)\s*\((\d+(?:st|nd|rd|th))\)\s*$')
    
    spells_by_sphere = {
        "Sphere of Earth": [],
        "Sphere of Air": [],
        "Sphere of Fire": [],
        "Sphere of Water": [],
        "Sphere of the Cosmos": []
    }
    
    # Track block coordinates for later marking
    spell_block_info = {}
    
    # Column detection threshold (X coordinate)
    # Blocks with X < 200 are left column, X >= 200 are right column
    COLUMN_THRESHOLD = 200
    
    # STRATEGY: Build a map of (page, block) -> sphere based on position analysis
    # For each page:
    #   1. Find all sphere headers and their positions (y-coordinate, column)
    #   2. Assign each block to the sphere that "owns" it based on reading order
    block_to_sphere = {}
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        # Find all sphere headers on this page with their positions
        headers = []  # List of (block_idx, sphere_name, column, y_pos)
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            block_bbox = block.get("bbox", [0, 0, 0, 0])
            block_x = block_bbox[0]
            block_y = block_bbox[1]
            column = "left" if block_x < COLUMN_THRESHOLD else "right"
            
            # Check if this block contains a sphere header
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    span_text = _clean_text(span.get("text", "")).strip()
                    if span_text:
                        line_text += " " + span_text if line_text else span_text
                line_text = line_text.strip()
                
                if line_text in spells_by_sphere.keys():
                    headers.append((block_idx, line_text, column, block_y))
                    logger.debug(f"Page {page_idx}, Block {block_idx}: Found header '{line_text}' in {column} column at y={block_y:.1f}")
                    break
        
        # Now assign spheres to all blocks based on the headers
        # Reading order: left column top-to-bottom, then right column top-to-bottom
        for block_idx, block in enumerate(page.get("blocks", [])):
            block_bbox = block.get("bbox", [0, 0, 0, 0])
            block_x = block_bbox[0]
            block_y = block_bbox[1]
            column = "left" if block_x < COLUMN_THRESHOLD else "right"
            
            # Find the most recent header for this block
            # For left column: find header in left column with y <= block_y
            # For right column: consider headers from both columns
            current_sphere = None
            
            if column == "left":
                # Find the last header in left column that comes before this block
                for hdr_idx, hdr_name, hdr_col, hdr_y in headers:
                    if hdr_col == "left" and hdr_y <= block_y:
                        current_sphere = hdr_name
            else:  # right column
                # For right column blocks, first check if there's a header in the right column
                right_col_header = None
                for hdr_idx, hdr_name, hdr_col, hdr_y in headers:
                    if hdr_col == "right" and hdr_y <= block_y:
                        right_col_header = hdr_name
                
                if right_col_header:
                    # Use the right column header
                    current_sphere = right_col_header
                else:
                    # No header in right column yet, inherit from left column's last header
                    for hdr_idx, hdr_name, hdr_col, hdr_y in reversed(headers):
                        if hdr_col == "left":
                            current_sphere = hdr_name
                            break
            
            if current_sphere:
                block_to_sphere[(page_idx, block_idx)] = current_sphere
    
    # Now parse spells using the block_to_sphere mapping
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            current_sphere = block_to_sphere.get((page_idx, block_idx))
            
            # Track if this entire block contains spell lines
            block_has_spells = False
            
            # Skip if this block doesn't belong to any sphere
            if not current_sphere:
                continue
            
            # Get the full block text to check for embedded spells
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
            
            # Check each line individually first (normal case)
            for line in block.get("lines", []):
                # Concatenate all spans in the line to handle split text
                line_text = ""
                
                for span in line.get("spans", []):
                    span_text = _clean_text(span.get("text", "")).strip()
                    if span_text:
                        line_text += " " + span_text if line_text else span_text
                
                line_text = line_text.strip()
                if not line_text:
                    continue
                
                # Skip if this is a sphere header itself
                if line_text in spells_by_sphere.keys():
                    continue
                
                # Try to parse as a spell
                match = spell_pattern.match(line_text)
                if match:
                    spell_name = match.group(1).strip()
                    spell_level = match.group(2)
                    
                    spell_data = {
                        "name": spell_name,
                        "level": spell_level,
                        "sphere": current_sphere,
                        "page": page_idx,
                        "block": block_idx
                    }
                    
                    spells_by_sphere[current_sphere].append(spell_data)
                    block_has_spells = True
                    
                    logger.debug(f"Parsed spell: {spell_name} ({spell_level}) in {current_sphere} [page={page_idx}, block={block_idx}]")
            
            # Also check for embedded spells in the full block text (handles mixed content)
            # Per [SPELL_FORMAT] rule: "spell_name (1st)", "spell_name (2nd)", "spell_name (3rd)", "spell_name (#th)"
            # Use negative lookbehind to avoid matching mid-spell (e.g., "Light Wounds" in "Cure Light Wounds")
            # Match: (start OR non-letter), then capture (Capital + lowercase words with spaces/hyphens/apostrophes/& OR Roman numerals), then (level)
            # Examples: "Animal Summoning II (5th)", "Commune With Nature (5th)", "Anti-Plant Shell (5th)"
            embedded_spell_pattern = re.compile(r'(?:^|(?<=[^A-Za-z]))([A-Z][a-z]+(?:[\s\-\'&]+(?:or|and|of|with|to|from|the)?[\s\-\'&]*[A-Z][a-z]+|[\s\-\'&]*[IVX]+)*)\s+\((\d+(?:st|nd|rd|th))\)')
            
            embedded_matches = list(embedded_spell_pattern.finditer(block_text))
            if embedded_matches:
                if current_sphere:
                    logger.warning(f"Page {page_idx}, Block {block_idx}: Found {len(embedded_matches)} potential embedded spells in '{current_sphere}'")
                else:
                    logger.warning(f"Page {page_idx}, Block {block_idx}: Found {len(embedded_matches)} potential embedded spells but NO SPHERE ASSIGNED")
                    # Log the first match to help debug
                    if embedded_matches:
                        first_match = embedded_matches[0]
                        logger.warning(f"  Example: {first_match.group(1)} ({first_match.group(2)})")
            
            for match in embedded_matches:
                spell_name = match.group(1).strip()
                spell_level = match.group(2)
                
                # Skip if already found (avoid duplicates)
                if any(s["name"] == spell_name and s["level"] == spell_level 
                       for s in spells_by_sphere.get(current_sphere, [])):
                    if current_sphere == "Sphere of the Cosmos":
                        logger.warning(f"  SKIP: {spell_name} ({spell_level}) - duplicate")
                    continue
                
                # Simple validation per [SPELL_FORMAT]
                start_pos = match.start()
                context_before = block_text[max(0, start_pos-10):start_pos]
                context_after = block_text[match.end():min(len(block_text), match.end()+20)]
                
                # Skip if lowercase before (mid-word/sentence)
                if context_before and context_before[-1:].isalpha() and context_before[-1:].islower():
                    if current_sphere == "Sphere of the Cosmos":
                        logger.warning(f"  SKIP: {spell_name} ({spell_level}) - lowercase before")
                    continue
                
                # Skip if followed by " level" (prose, not a spell)
                if context_after.strip().startswith('level'):
                    if current_sphere == "Sphere of the Cosmos":
                        logger.warning(f"  SKIP: {spell_name} ({spell_level}) - followed by 'level'")
                    continue
                
                # Skip common prose words that shouldn't be spell names
                prose_prefixes = ['Those spells', 'These', 'All spells', 'Such spells', 'The']
                if any(spell_name.startswith(prefix) for prefix in prose_prefixes):
                    if current_sphere == "Sphere of the Cosmos":
                        logger.warning(f"  SKIP: {spell_name} ({spell_level}) - prose prefix")
                    continue
                
                # Remove "Sphere " prefix if present (e.g., "Sphere Anti-Plant Shell" -> "Anti-Plant Shell")
                if spell_name.startswith('Sphere '):
                    logger.warning(f"  Removing 'Sphere ' prefix from: {spell_name}")
                    spell_name = spell_name[7:]  # Remove "Sphere " (7 chars)
                    logger.warning(f"  Cleaned spell name: {spell_name}")
                
                # This is a valid spell per [SPELL_FORMAT]
                spell_data = {
                    "name": spell_name,
                    "level": spell_level,
                    "sphere": current_sphere,
                    "page": page_idx,
                    "block": block_idx
                }
                
                spells_by_sphere[current_sphere].append(spell_data)
                block_has_spells = True
                
                if current_sphere == "Sphere of the Cosmos":
                    logger.warning(f"  ADDED: {spell_name} ({spell_level})")
                logger.debug(f"Extracted embedded spell: {spell_name} ({spell_level}) in {current_sphere} [page={page_idx}, block={block_idx}]")
            
            # Mark the entire block if it contains any spells
            if block_has_spells:
                block_key = f"{page_idx}_{block_idx}"
                spell_block_info[block_key] = {"page": page_idx, "block": block_idx}
    
    # Log summary
    total_spells = sum(len(spells) for spells in spells_by_sphere.values())
    logger.info(f"Parsed {total_spells} total spells across {len(spells_by_sphere)} spheres")
    for sphere, spells in spells_by_sphere.items():
        logger.info(f"  {sphere}: {len(spells)} spells")
    
    return {
        "spells_by_sphere": spells_by_sphere,
        "spell_block_info": spell_block_info
    }


def _save_spell_data(spells_data: dict) -> None:
    """Save structured spell data to JSON file.
    
    Args:
        spells_data: Dictionary containing spell data by sphere
    """
    output_path = Path("data/processed/chapter-seven-spells.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Extract just the spells_by_sphere for the JSON output
    output_data = {
        "chapter": "Chapter 7 - Magic",
        "spheres": spells_data["spells_by_sphere"],
        "metadata": {
            "total_spheres": len(spells_data["spells_by_sphere"]),
            "total_spells": sum(len(spells) for spells in spells_data["spells_by_sphere"].values())
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved spell data to {output_path}")


def _mark_spell_blocks_for_rendering(section_data: dict, spells_data: dict) -> None:
    """Mark spell text blocks for special rendering as list items.
    
    Args:
        section_data: The raw section data from PDF extraction (modified in place)
        spells_data: Dictionary containing spell data and block info
    """
    spell_block_info = spells_data["spell_block_info"]
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            block_key = f"{page_idx}_{block_idx}"
            
            if block_key in spell_block_info:
                # Mark this block as a spell list item for special rendering
                block["_render_as"] = "spell_list_item"
                block["_spell_data"] = spell_block_info[block_key]
                logger.debug(f"Marked block {block_key} as spell list item")
    
    logger.info(f"Marked {len(spell_block_info)} spell blocks for list rendering")

