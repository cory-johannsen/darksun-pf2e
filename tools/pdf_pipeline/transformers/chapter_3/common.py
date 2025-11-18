"""
Common utilities for Chapter 3 (Player Character Classes) processing.

This module contains shared utility functions used across all class-specific
processing modules. These functions handle text normalization, table extraction,
block manipulation, and other common operations.
"""

import logging
import re
from typing import List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


def normalize_plain_text(text: str) -> str:
    """Normalize text by replacing special characters.
    
    Args:
        text: Input text with potential special characters
        
    Returns:
        Normalized text with standard ASCII equivalents
    """
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


def parse_class_ability_requirements(text: str) -> List[Tuple[str, str]]:
    """Parse a class ability requirements text block into structured rows.
    
    Args:
        text: Text block containing ability requirements
        
    Returns:
        List of (label, value) tuples suitable for a 2-column table.
        Handles both "Races Allowed" and "Allowed Races" orderings.
    """
    rows = []
    
    # Extract Ability Requirements
    # Stop at "Prime" (for Prime Requisite) or "Allowed" (for Allowed Races) or end of string
    ability_match = re.search(r'Ability Requirements?:\s*([^PA]*?)(?=Prime|Allowed|$)', text, re.DOTALL)
    if ability_match:
        ability_value = ability_match.group(1).strip()
        rows.append(("Ability Requirements:", ability_value))
    
    # Extract Prime Requisite(s)
    # Stop at "Races Allowed" or "Allowed Races" or end of string
    prime_match = re.search(r'Prime Requisites?:\s*([^RA]*?)(?=(?:Races?\s+Allowed|Allowed\s+Races?)|$)', text, re.DOTALL)
    if prime_match:
        prime_value = prime_match.group(1).strip()
        rows.append(("Prime Requisite:", prime_value))
    
    # Extract Races Allowed (handle both "Races Allowed:" and "Allowed Races:")
    races_match = re.search(r'(?:Races?\s+Allowed|Allowed\s+Races?):\s*(.+?)$', text, re.DOTALL)
    if races_match:
        races_value = races_match.group(1).strip()
        rows.append(("Races Allowed:", races_value))
    
    return rows


def extract_class_ability_table(page: dict, class_name: str) -> bool:
    """Extract and format a class ability requirements table for a specific class.
    
    This creates a 2-column, 3-row table with:
    - Row 1: Ability Requirements
    - Row 2: Prime Requisite
    - Row 3: Races Allowed
    
    Args:
        page: The page dictionary containing blocks
        class_name: The name of the class (e.g., "Fighter", "Gladiator")
    
    Returns:
        True if the table was extracted, False otherwise
    """
    logger.debug(f"Extracting requirements table for {class_name}")
    
    # Strategy 1: Check if class name and ability requirements are in a single block (like Fighter)
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = " ".join(
            normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in lines
        )
        
        # Check if this block starts with the class name followed by ability requirements
        if text.startswith(class_name + " Ability Requirement"):
            # Strip the class name from the beginning to get just the ability requirements
            ability_text = text[len(class_name) + 1:] if text.startswith(class_name + " ") else text
            
            table_rows = parse_class_ability_requirements(ability_text)
            if table_rows and len(table_rows) >= 2:
                # Create a new header block for the class name
                create_class_name_header_block(page, class_name, block, idx)
                # Then create the table for ability requirements
                create_class_ability_table(page, table_rows, block["bbox"], idx + 1)  # idx+1 because we inserted a header
                return True
            return False
    
    # Strategy 2: Look for separate class header followed by ability requirements blocks (like Gladiator)
    logger.debug(f"  {class_name}: Trying Strategy 2 - looking for separate header")
    class_header_idx = None
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = " ".join(
            normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in lines
        )
        
        # Check if this block is just the class header
        # Special case for Psionicist which has "(Dark Sun variation)" in the header
        if text.strip() == class_name:
            class_header_idx = idx
            logger.debug(f"  {class_name}: Found class header at block {idx}")
            break
        elif class_name == "Psionicist" and text.strip().startswith("Psionicist") and "(Dark Sun variation)" in text:
            class_header_idx = idx
            logger.debug(f"  {class_name}: Found Psionicist header with variation at block {idx}")
            break
    
    if class_header_idx is None:
        logger.debug(f"  {class_name}: Strategy 2 - class header not found")
        return False
    
    logger.debug(f"  {class_name}: Strategy 2 - found header at block {class_header_idx}, starting requirements collection")
    
    # Special handling for Psionicist: split the header into class name and "(Dark Sun variation)" label
    inserted_label_block = False
    if class_name == "Psionicist":
        header_block = page["blocks"][class_header_idx]
        lines = header_block.get("lines", [])
        if lines:
            text = " ".join(
                normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                for line in lines
            )
            if "(Dark Sun variation)" in text:
                # Split the header block into two: class name and label
                # Create a new block for just "Psionicist"
                psionicist_header_block = {
                    "type": "text",
                    "bbox": list(header_block.get("bbox", [0, 0, 0, 0])),
                    "lines": [
                        {
                            "bbox": list(header_block.get("bbox", [0, 0, 0, 0])),
                            "spans": [
                                {
                                    "text": "Psionicist",
                                    "color": "#ca5804",  # Header color
                                    "size": 10.8,
                                    "font": "MSTT31c501"
                                }
                            ]
                        }
                    ]
                }
                
                # Create a new block for "(Dark Sun variation)" label
                label_block = {
                    "type": "text",
                    "bbox": list(header_block.get("bbox", [0, 0, 0, 0])),
                    "lines": [
                        {
                            "bbox": list(header_block.get("bbox", [0, 0, 0, 0])),
                            "spans": [
                                {
                                    "text": "(Dark Sun variation)",
                                    "color": "#000000",  # Regular text color
                                    "size": 8.88,
                                    "font": lines[0]["spans"][0].get("font", "")
                                }
                            ]
                        }
                    ]
                }
                
                # Replace the original header block with the two new blocks
                page["blocks"][class_header_idx] = psionicist_header_block
                page["blocks"].insert(class_header_idx + 1, label_block)
                inserted_label_block = True
    
    # Collect ability requirement blocks following the header
    # These might be split across multiple blocks
    ability_blocks = []
    ability_block_indices = []
    combined_text = ""
    
    # If we inserted a label block for Psionicist, skip it when looking for ability requirements
    start_search_idx = class_header_idx + 2 if inserted_label_block else class_header_idx + 1
    
    for idx in range(start_search_idx, min(start_search_idx + 10, len(page.get("blocks", [])))):
        block = page["blocks"][idx]
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = " ".join(
            normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in lines
        )
        
        # Check if this looks like ability requirements content
        if not combined_text and not text.startswith("Ability Requirement"):
            # Haven't found the start yet
            continue
        
        # Once we've started collecting, keep going until we hit a stopping condition
        if combined_text:
            # Stop if we hit a paragraph that doesn't look like ability requirements
            if not any(keyword in text for keyword in ["Dexterity", "Constitution", "Strength", "Intelligence", "Wisdom", "Charisma", "Prime", "Races", "Allowed"]):
                # This doesn't look like ability requirements anymore
                logger.debug(f"  {class_name}: Stopping at block {idx} - no keywords found in: {text[:50]}")
                break
        
        combined_text += " " + text if combined_text else text
        ability_blocks.append(block)
        ability_block_indices.append(idx)
        logger.debug(f"  {class_name}: Collected block {idx}: {text[:80]}")
        logger.debug(f"  {class_name}: Combined so far: {combined_text[:150]}")
        
        # Check if we have all three fields
        has_ability = "Ability Requirement" in combined_text
        has_prime = "Prime Requisite" in combined_text
        has_races = ("Races Allowed" in combined_text or "Allowed Races" in combined_text)
        logger.debug(f"  {class_name}: has_ability={has_ability}, has_prime={has_prime}, has_races={has_races}")
        
        if has_ability and has_prime and has_races:
            # We have everything we need
            logger.debug(f"  {class_name}: All fields found, stopping collection")
            break
    
    if not combined_text:
        # Strategy 3: Check for reversed format (value before label), e.g., Preserver
        # Format: "Intelligence 9 Ability Requirements:" instead of "Ability Requirements: Intelligence 9"
        ability_blocks_reversed = []
        ability_block_indices_reversed = []
        combined_text_reversed = ""
        
        for idx in range(start_search_idx, min(start_search_idx + 10, len(page.get("blocks", [])))):
            block = page["blocks"][idx]
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            if not lines:
                continue
            
            text = " ".join(
                normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                for line in lines
            )
            
            # Check for reversed format - ends with "Ability Requirements:" or "Prime Requisite:" or "Races Allowed:"
            if re.search(r'Ability Requirements?:\s*$', text) or \
               re.search(r'Prime Requisites?:\s*$', text) or \
               re.search(r'(?:Races?\s+Allowed|Allowed\s+Races?):\s*$', text):
                # This is a reversed format block
                combined_text_reversed += " " + text if combined_text_reversed else text
                ability_blocks_reversed.append(block)
                ability_block_indices_reversed.append(idx)
                
                # Check if we have all three fields
                has_ability = re.search(r'Ability Requirements?:', combined_text_reversed)
                has_prime = re.search(r'Prime Requisites?:', combined_text_reversed)
                has_races = re.search(r'(?:Races?\s+Allowed|Allowed\s+Races?):', combined_text_reversed)
                
                if has_ability and has_prime and has_races:
                    # We have everything, now parse it
                    break
        
        if combined_text_reversed:
            # Parse the reversed format: "Intelligence 9 Ability Requirements:"
            # Need to rearrange to standard format: "Ability Requirements: Intelligence 9"
            reversed_rows = []
            
            # Extract each field with reversed format
            ability_match = re.search(r'(.+?)\s+Ability Requirements?:', combined_text_reversed)
            if ability_match:
                reversed_rows.append(("Ability Requirements:", ability_match.group(1).strip()))
            
            prime_match = re.search(r'(.+?)\s+Prime Requisites?:', combined_text_reversed)
            if prime_match:
                reversed_rows.append(("Prime Requisite:", prime_match.group(1).strip()))
            
            races_match = re.search(r'(.+?)\s+(?:Races?\s+Allowed|Allowed\s+Races?):', combined_text_reversed)
            if races_match:
                reversed_rows.append(("Races Allowed:", races_match.group(1).strip()))
            
            if reversed_rows and len(reversed_rows) >= 2:
                bbox = ability_blocks_reversed[0]["bbox"] if ability_blocks_reversed else [0, 0, 0, 0]
                create_class_ability_table(page, reversed_rows, bbox, ability_block_indices_reversed)
                return True
        
        return False
    
    # Parse the ability requirements into table rows
    table_rows = parse_class_ability_requirements(combined_text)
    logger.debug(f"  {class_name}: Parsed {len(table_rows)} rows from combined text")
    logger.debug(f"  {class_name}: Combined text: {combined_text}")
    logger.debug(f"  {class_name}: Parsed rows: {table_rows}")
    
    if not table_rows or len(table_rows) < 2:  # Need at least 2 rows
        logger.warning(f"  {class_name}: Failed - only {len(table_rows)} rows parsed (need at least 2)")
        return False
    
    # Use the bbox from the first ability block
    bbox = ability_blocks[0]["bbox"] if ability_blocks else [0, 0, 0, 0]
    create_class_ability_table(page, table_rows, bbox, ability_block_indices)
    logger.info(f"  {class_name}: Successfully created requirements table with {len(table_rows)} rows")
    
    return True


def create_class_name_header_block(page: dict, class_name: str, original_block: dict, insert_at_idx: int) -> None:
    """Create a separate header block for the class name.
    
    Args:
        page: The page dictionary to add the header block to
        class_name: The name of the class (e.g., "Fighter")
        original_block: The original block containing class name + ability requirements
        insert_at_idx: Index where to insert the new header block
    """
    # Create a new block with just the class name, styled as a header
    header_block = {
        "type": "text",
        "bbox": list(original_block.get("bbox", [0, 0, 0, 0])),
        "lines": [
            {
                "bbox": list(original_block.get("bbox", [0, 0, 0, 0])),
                "spans": [
                    {
                        "text": class_name,
                        "color": "#ca5804",  # Orange color for headers
                        "size": 10.8,  # Header size (matching Gladiator)
                        "font": "MSTT31c501"  # Header font (matching Gladiator)
                    }
                ]
            }
        ]
    }
    
    # Insert the header block at the specified position
    page["blocks"].insert(insert_at_idx, header_block)


def create_class_ability_table(page: dict, table_rows: list, bbox: list, block_indices: Union[int, List[int]]) -> None:
    """Create and add a class ability requirements table to the page.
    
    Args:
        page: The page dictionary to add the table to
        table_rows: List of (label, value) tuples for the table
        bbox: Bounding box for the table
        block_indices: Index or list of indices of blocks to clear/replace
    """
    # Create a text block with a special marker for the table
    # This follows the pattern used by other tables in the codebase
    table_block = {
        "type": "text",  # MUST be "text" to be rendered
        "bbox": list(bbox),
        "lines": [],  # Empty lines since we're using a marker
        "__class_requirements_table": {
            "rows": [{"cells": [{"text": label}, {"text": value}]} for label, value in table_rows]
        }
    }
    
    # Convert block_indices to a list
    if isinstance(block_indices, int):
        block_indices = [block_indices]
    
    # Replace the first block with the table marker, and clear the rest
    if block_indices and len(block_indices) > 0:
        first_idx = block_indices[0]
        if first_idx < len(page["blocks"]):
            # Replace the first block with our table marker
            page["blocks"][first_idx] = table_block
            
            # Clear the remaining blocks (set them to empty text blocks)
            for idx in block_indices[1:]:
                if idx < len(page["blocks"]):
                    page["blocks"][idx] = {
                        "type": "text",
                        "bbox": [0.0, 0.0, 0.0, 0.0],
                        "lines": []
                    }
            
            logger.debug(f"Inserted table marker block at index {first_idx}, cleared {len(block_indices) - 1} additional blocks")


def update_block_bbox(block: dict) -> None:
    """Update a block's bounding box based on its lines.
    
    Args:
        block: Block dictionary with lines to recalculate bbox from
    """
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


def find_block(page: dict, predicate) -> Optional[Tuple[int, dict]]:
    """Find a block that matches the given predicate.
    
    Args:
        page: Page dictionary containing blocks
        predicate: Function that takes a block and returns True if it matches
        
    Returns:
        Tuple of (index, block) if found, None otherwise
    """
    for idx, block in enumerate(page.get("blocks", [])):
        if predicate(block):
            return (idx, block)
    return None


def extract_class_ability_requirements_table(page: dict) -> None:
    """Extract and format the Class Ability Requirements table on page 23.
    
    This is a borderless table with 7 columns and 5 rows (including header).
    Headers: Class, Str, Dex, Con, Int, Wis, Cha (in this specific order)
    Data rows: Gladiator, Defiler, Templar, Psionicist (with their ability requirements)
    
    Args:
        page: Page dictionary to extract table from and add structured table to
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== extract_class_ability_requirements_table START ===")
    
    # Create the table structure based on known content
    # This is a clean, well-structured table that appears after "Class Ability Requirements" subheader
    rows_data = [
        ["Class", "Str", "Dex", "Con", "Int", "Wis", "Cha"],
        ["Gladiator", "13", "12", "15", "-", "-", "-"],
        ["Defiler", "-", "-", "-", "3", "-", "-"],
        ["Templar", "-", "-", "-", "10", "7", "-"],
        ["Psionicist", "-", "-", "11", "12", "15", "-"]
    ]
    
    table_data = {
        "rows": [{"cells": [{"text": cell} for cell in row]} for row in rows_data],
        "header_rows": 1,
        "bbox": [0, 0, 0, 0]
    }
    
    # Find the "Class Ability Requirements" header and subsequent table-related blocks
    # Also modify the header to be a subheader (smaller font)
    header_idx = None
    header_block = None
    blocks_to_clear = []
    
    logger.info(f"Processing page with {len(page.get('blocks', []))} blocks")
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        for line in lines:
            text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Find the header
            if "Class Ability Requirements" in text and header_idx is None:
                logger.info(f"Found Class Ability Requirements header at block {idx}")
                header_idx = idx
                header_block = block
                # Make this a subheader by changing the font size
                for line in lines:
                    for span in line.get("spans", []):
                        span["size"] = 8.88  # Subheader size
                break
    
    # If we found the header, look for the next several blocks that are part of the table
    if header_idx is not None:
        logger.info(f"Searching for table blocks after header at {header_idx}")
        # The table fragments typically appear in the next 10-15 blocks
        for idx in range(header_idx + 1, min(header_idx + 15, len(page["blocks"]))):
            block = page["blocks"][idx]
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            if not lines:
                continue
            
            # Collect all text in this block
            block_text = " ".join(
                normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                for line in lines
            )
            
            # Look for table-related keywords
            table_keywords = ["Class", "S t r", "Str", "Dex", "Con", "Cha", "Int", "Wis", 
                            "Gladiator", "Defiler", "Templar", "Psionicist", "11", "12", "13", "15"]
            
            # Stop when we hit section headers that come after the table
            if any(stop_keyword in block_text for stop_keyword in ["Newly Created", "Starting Level", "Starting Hit"]):
                logger.info(f"Stopping at block {idx} - found stop keyword: {block_text[:50]}")
                break
            
            # If this block contains any table keywords or numbers from the table, mark for clearing
            if any(keyword in block_text for keyword in table_keywords):
                logger.info(f"Marking block {idx} for clearing: {block_text[:50]}")
                blocks_to_clear.append(idx)
    else:
        logger.warning("Could not find 'Class Ability Requirements' header")
    
    # Clear the identified table blocks and insert the table
    if header_idx is not None and blocks_to_clear:
        logger.info(f"Clearing {len(blocks_to_clear)} blocks and inserting table")
        # Set the table's bbox based on the header block's position
        if header_block and "bbox" in header_block:
            header_bbox = header_block["bbox"]
            # Place table just below the header
            table_data["bbox"] = [header_bbox[0], header_bbox[3] + 5, header_bbox[2], header_bbox[3] + 100]
        
        # Add the table to the page's tables list (creating it if it doesn't exist)
        if "tables" not in page:
            page["tables"] = []
        page["tables"].append(table_data)
        logger.info(f"Added table to page. Total tables now: {len(page.get('tables', []))}")
        
        # Clear all the fragmented table text blocks
        for idx in sorted(blocks_to_clear, reverse=True):
            if idx < len(page["blocks"]):
                page["blocks"][idx]["lines"] = []
                page["blocks"][idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]
        logger.info(f"Cleared {len(blocks_to_clear)} blocks")
    else:
        logger.warning(f"Did not insert table. header_idx={header_idx}, blocks_to_clear={len(blocks_to_clear)}")
    
    logger.info("=== extract_class_ability_requirements_table END ===")



def force_warrior_classes_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Warrior Classes section by splitting and marking blocks.
    
    The Warrior Classes section should have 5 paragraphs based on user-specified breaks.
    
    Args:
        page: Page dictionary containing blocks to process
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
            if (line_text.startswith("The fighter is a skilled warrior, trained for both") or
                line_text.startswith("The ranger is a warrior knowledgeable in the ways") or
                line_text.startswith("The gladiator is a specialized warrior trained for") or
                line_text.startswith("As a note, there are no paladins on Athas")):
                
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

