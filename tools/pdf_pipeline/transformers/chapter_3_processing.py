"""
Chapter 3 (Player Character Classes) specific processing.

This module contains all the PDF-level adjustments for the chapter-three-player-character-classes section.
"""

from copy import deepcopy
from typing import Optional, List, Tuple, Union
import re

# Import extracted functions from chapter_3 sub-modules
from .chapter_3.warrior import (
    extract_fighters_followers_table as _extract_fighters_followers_table,
    force_gladiator_paragraph_breaks as _force_gladiator_paragraph_breaks,
    force_fighter_benefits_paragraph_breaks as _force_fighter_benefits_paragraph_breaks,
    force_fighter_paragraph_breaks as _force_fighter_paragraph_breaks,
)
from .chapter_3.ranger import (
    fix_ranger_ability_requirements_table as _fix_ranger_ability_requirements_table,
    force_ranger_paragraph_breaks as _force_ranger_paragraph_breaks,
    reconstruct_rangers_followers_table_inplace as _reconstruct_rangers_followers_table_inplace,
    extract_rangers_followers_table as _extract_rangers_followers_table,
    extract_rangers_followers_table_from_pages as _extract_rangers_followers_table_from_pages,
    mark_ranger_description_blocks as _mark_ranger_description_blocks,
)
from .chapter_3.wizard import (
    extract_defiler_experience_table as _extract_defiler_experience_table,
    force_wizard_classes_paragraph_breaks as _force_wizard_classes_paragraph_breaks,
    force_wizard_section_paragraph_breaks as _force_wizard_section_paragraph_breaks,
    force_defiler_paragraph_breaks as _force_defiler_paragraph_breaks,
    extract_defiler_experience_levels_table as _extract_defiler_experience_levels_table,
    force_preserver_paragraph_breaks as _force_preserver_paragraph_breaks,
)
from .chapter_3.priest import (
    extract_templar_spell_progression_table as _extract_templar_spell_progression_table,
    force_priest_section_paragraph_breaks as _force_priest_section_paragraph_breaks,
    force_spheres_of_magic_paragraph_breaks as _force_spheres_of_magic_paragraph_breaks,
    force_cleric_paragraph_breaks as _force_cleric_paragraph_breaks,
    force_cleric_powers_paragraph_breaks as _force_cleric_powers_paragraph_breaks,
    force_druid_paragraph_breaks as _force_druid_paragraph_breaks,
    force_druid_granted_powers_paragraph_breaks as _force_druid_granted_powers_paragraph_breaks,
    fix_templar_ability_table as _fix_templar_ability_table,
    force_templar_paragraph_breaks as _force_templar_paragraph_breaks,
    force_priest_classes_paragraph_breaks as _force_priest_classes_paragraph_breaks,
)
from .chapter_3.rogue import (
    extract_bard_poison_table as _extract_bard_poison_table,
    force_bard_poison_paragraph_breaks as _force_bard_poison_paragraph_breaks,
    force_thief_paragraph_breaks as _force_thief_paragraph_breaks,
    extract_thieving_dexterity_adjustments_table as _extract_thieving_dexterity_adjustments_table,
    force_thief_abilities_paragraph_breaks as _force_thief_abilities_paragraph_breaks,
    extract_thieving_racial_adjustments_table as _extract_thieving_racial_adjustments_table,
    force_bard_paragraph_breaks as _force_bard_paragraph_breaks,
    force_rogue_classes_paragraph_breaks as _force_rogue_classes_paragraph_breaks,
)
from .chapter_3.psionicist import (
    force_psionicist_paragraph_breaks as _force_psionicist_paragraph_breaks,
    extract_inherent_potential_table as _extract_inherent_potential_table,
    force_psionicist_class_paragraph_breaks as _force_psionicist_class_paragraph_breaks,
)
from .chapter_3.multiclass import (
    extract_multiclass_combinations as _extract_multiclass_combinations,
    force_multiclass_paragraph_breaks as _force_multiclass_paragraph_breaks,
    force_level_advancement_paragraph_breaks as _force_level_advancement_paragraph_breaks,
    extract_experience_points_table as _extract_experience_points_table,
)


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


def _parse_class_ability_requirements(text: str) -> List[Tuple[str, str]]:
    """Parse a class ability requirements text block into structured rows.
    
    Returns a list of (label, value) tuples suitable for a 2-column table.
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


def _extract_class_ability_table(page: dict, class_name: str) -> bool:
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
    import sys
    
    # Strategy 1: Check if class name and ability requirements are in a single block (like Fighter)
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = " ".join(
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in lines
        )
        
        # Check if this block starts with the class name followed by ability requirements
        if text.startswith(class_name + " Ability Requirement"):
            # Strip the class name from the beginning to get just the ability requirements
            ability_text = text[len(class_name) + 1:] if text.startswith(class_name + " ") else text
            
            table_rows = _parse_class_ability_requirements(ability_text)
            if table_rows and len(table_rows) >= 2:
                # Create a new header block for the class name
                _create_class_name_header_block(page, class_name, block, idx)
                # Then create the table for ability requirements
                _create_class_ability_table(page, table_rows, block["bbox"], idx + 1)  # idx+1 because we inserted a header
                return True
            return False
    
    # Strategy 2: Look for separate class header followed by ability requirements blocks (like Gladiator)
    class_header_idx = None
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = " ".join(
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in lines
        )
        
        # Check if this block is just the class header
        # Special case for Psionicist which has "(Dark Sun variation)" in the header
        if text.strip() == class_name:
            class_header_idx = idx
            break
        elif class_name == "Psionicist" and text.strip().startswith("Psionicist") and "(Dark Sun variation)" in text:
            class_header_idx = idx
            break
    
    if class_header_idx is None:
        return False
    
    # Special handling for Psionicist: split the header into class name and "(Dark Sun variation)" label
    inserted_label_block = False
    if class_name == "Psionicist":
        header_block = page["blocks"][class_header_idx]
        lines = header_block.get("lines", [])
        if lines:
            text = " ".join(
                _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
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
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
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
                break
        
        combined_text += " " + text if combined_text else text
        ability_blocks.append(block)
        ability_block_indices.append(idx)
        
        # Check if we have all three fields
        has_ability = "Ability Requirement" in combined_text
        has_prime = "Prime Requisite" in combined_text
        has_races = ("Races Allowed" in combined_text or "Allowed Races" in combined_text)
        
        if has_ability and has_prime and has_races:
            # We have everything we need
            break
    
    if not combined_text:
        return False
    
    # Parse the ability requirements into table rows
    table_rows = _parse_class_ability_requirements(combined_text)
    
    if not table_rows or len(table_rows) < 2:  # Need at least 2 rows
        return False
    
    # Use the bbox from the first ability block
    bbox = ability_blocks[0]["bbox"] if ability_blocks else [0, 0, 0, 0]
    _create_class_ability_table(page, table_rows, bbox, ability_block_indices)
    
    return True


def _create_class_name_header_block(page: dict, class_name: str, original_block: dict, insert_at_idx: int) -> None:
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


def _create_class_ability_table(page: dict, table_rows: list, bbox: list, block_indices: Union[int, List[int]]) -> None:
    """Create and add a class ability requirements table to the page.
    
    Args:
        page: The page dictionary to add the table to
        table_rows: List of (label, value) tuples for the table
        bbox: Bounding box for the table
        block_indices: Index or list of indices of blocks to clear
    """
    # Create the table structure
    table_data = {
        "rows": [{"cells": [{"text": label}, {"text": value}]} for label, value in table_rows],
        "bbox": list(bbox)
    }
    
    # Add the table to the page's tables list
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table_data)
    
    # Clear the original text blocks containing the ability requirements
    if isinstance(block_indices, int):
        block_indices = [block_indices]
    
    for idx in block_indices:
        if idx < len(page["blocks"]):
            page["blocks"][idx]["lines"] = []
            page["blocks"][idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]


# _fix_ranger_ability_requirements_table - MOVED to chapter_3/ranger.py


# _force_ranger_paragraph_breaks - MOVED to chapter_3/ranger.py


# _reconstruct_rangers_followers_table_inplace - MOVED to chapter_3/ranger.py


# _extract_rangers_followers_table (from page) - MOVED to chapter_3/ranger.py


# _mark_ranger_description_blocks - MOVED to chapter_3/ranger.py


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


# _extract_fighters_followers_table - MOVED to chapter_3/warrior.py


# _force_gladiator_paragraph_breaks - MOVED to chapter_3/warrior.py


# _force_fighter_benefits_paragraph_breaks - MOVED to chapter_3/warrior.py


def _extract_class_ability_requirements_table(page: dict) -> None:
    """Extract and format the Class Ability Requirements table on page 23.
    
    This is a borderless table with 7 columns and 5 rows (including header).
    Headers: Class, Str, Dex, Con, Int, Wis, Cha (in this specific order)
    Data rows: Gladiator, Defiler, Templar, Psionicist (with their ability requirements)
    """
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
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        for line in lines:
            text = _normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Find the header
            if "Class Ability Requirements" in text and header_idx is None:
                header_idx = idx
                header_block = block
                # Make this a subheader by changing the font size
                for line in lines:
                    for span in line.get("spans", []):
                        span["size"] = 8.88  # Subheader size
                break
    
    # If we found the header, look for the next several blocks that are part of the table
    if header_idx is not None:
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
                _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                for line in lines
            )
            
            # Look for table-related keywords
            table_keywords = ["Class", "S t r", "Str", "Dex", "Con", "Cha", "Int", "Wis", 
                            "Gladiator", "Defiler", "Templar", "Psionicist", "11", "12", "13", "15"]
            
            # Stop when we hit section headers that come after the table
            if any(stop_keyword in block_text for stop_keyword in ["Newly Created", "Starting Level", "Starting Hit"]):
                break
            
            # If this block contains any table keywords or numbers from the table, mark for clearing
            if any(keyword in block_text for keyword in table_keywords):
                blocks_to_clear.append(idx)
    
    # Clear the identified table blocks and insert the table
    if header_idx is not None and blocks_to_clear:
        # Set the table's bbox based on the header block's position
        if header_block and "bbox" in header_block:
            header_bbox = header_block["bbox"]
            # Place table just below the header
            table_data["bbox"] = [header_bbox[0], header_bbox[3] + 5, header_bbox[2], header_bbox[3] + 100]
        
        # Add the table to the page's tables list (creating it if it doesn't exist)
        if "tables" not in page:
            page["tables"] = []
        page["tables"].append(table_data)
        
        # Clear all the fragmented table text blocks
# _extract_templar_spell_progression_table - MOVED to chapter_3/priest.py

# _extract_rangers_followers_table (from pages) - MOVED to chapter_3/ranger.py


# _extract_defiler_experience_table - MOVED to chapter_3/wizard.py


# _extract_templar_spell_progression_table - MOVED to chapter_3/priest.py


# _extract_bard_poison_table - MOVED to chapter_3/rogue.py


# _force_bard_poison_paragraph_breaks - MOVED to chapter_3/rogue.py


# _force_thief_paragraph_breaks - MOVED to chapter_3/rogue.py


# _extract_thieving_dexterity_adjustments_table - MOVED to chapter_3/rogue.py


# _force_thief_abilities_paragraph_breaks - MOVED to chapter_3/rogue.py


# _force_psionicist_paragraph_breaks - MOVED to chapter_3/psionicist.py

# _extract_thieving_racial_adjustments_table - MOVED to chapter_3/rogue.py


# _extract_inherent_potential_table - MOVED to chapter_3/psionicist.py


def _force_warrior_classes_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Warrior Classes section by splitting and marking blocks.
    
    The Warrior Classes section should have 5 paragraphs based on user-specified breaks.
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
            line_text = _normalize_plain_text(
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
                    _update_block_bbox(block)
                    
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    _update_block_bbox(second_block)
                    
                    blocks_to_insert.append((idx + 1, second_block))
                    break
                else:
                    block["__force_paragraph_break"] = True
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)


# _force_wizard_classes_paragraph_breaks - MOVED to chapter_3/wizard.py


# _force_priest_section_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_defiler_paragraph_breaks - MOVED to chapter_3/wizard.py


# _extract_defiler_experience_levels_table - MOVED to chapter_3/wizard.py


# _force_preserver_paragraph_breaks - MOVED to chapter_3/wizard.py


# _force_priest_section_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_spheres_of_magic_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_spheres_of_magic_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_cleric_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_cleric_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_cleric_powers_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_cleric_powers_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_druid_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_druid_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_druid_granted_powers_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_druid_granted_powers_paragraph_breaks - MOVED to chapter_3/priest.py

# _fix_templar_ability_table - MOVED to chapter_3/priest.py

# _fix_templar_ability_table - MOVED to chapter_3/priest.py

# _force_templar_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_templar_paragraph_breaks - MOVED to chapter_3/priest.py


# _force_bard_paragraph_breaks - MOVED to chapter_3/rogue.py

# _force_priest_classes_paragraph_breaks - MOVED to chapter_3/priest.py

# _force_priest_classes_paragraph_breaks - MOVED to chapter_3/priest.py


# _force_rogue_classes_paragraph_breaks - MOVED to chapter_3/rogue.py


# _force_psionicist_class_paragraph_breaks - MOVED to chapter_3/psionicist.py

# _force_fighter_paragraph_breaks - MOVED to chapter_3/warrior.py


def _update_block_bbox(block: dict) -> None:
    """Update a block's bbox based on its lines."""
    lines = block.get("lines", [])
    if not lines:
        return
    
    x0 = min(line["bbox"][0] for line in lines)
    y0 = min(line["bbox"][1] for line in lines)
    x1 = max(line["bbox"][2] for line in lines)
    y1 = max(line["bbox"][3] for line in lines)
    
    block["bbox"] = [x0, y0, x1, y1]


def _fix_multiclass_header(page: dict) -> None:
    """
    Fix the "Multi-Class and Dual-Class Characters" header.
    The header is split across two lines, both with header color, causing them to render as separate headers.
    We need to merge them into a single line. If the header is missing entirely, we insert it.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    blocks = page.get("blocks", [])
    header_found = False
    
    for block in blocks:
        if block.get("type") != "text":
            continue
        
        # Check if this block contains "Multi-Class and Dual-Class" 
        has_multiclass = False
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if "Multi-Class and Dual-Class" in span.get("text", ""):
                    has_multiclass = True
                    break
            if has_multiclass:
                break
        
        if not has_multiclass:
            continue
        
        header_found = True
        
        # Found the block - merge the two lines into one
        lines = block.get("lines", [])
        if len(lines) >= 2:
            # Line 0 should be "Multi-Class and Dual-Class"
            # Line 1 should be "Characters"
            # Merge them into a single line
            first_line = lines[0]
            second_line = lines[1]
            
            # Get the text from both lines
            first_text = ''.join(span.get('text', '') for span in first_line.get('spans', []))
            second_text = ''.join(span.get('text', '') for span in second_line.get('spans', []))
            
            if 'Multi-Class' in first_text and 'Characters' in second_text:
                # Merge into first line
                first_line['spans'] = [{
                    'text': 'Multi-Class and Dual-Class Characters',
                    'color': '#ca5804',
                    'size': first_line['spans'][0].get('size', 10.8) if first_line['spans'] else 10.8
                }]
                
                # Update bbox to encompass both lines
                first_bbox = first_line.get('bbox', [0, 0, 0, 0])
                second_bbox = second_line.get('bbox', [0, 0, 0, 0])
                first_line['bbox'] = [
                    first_bbox[0],
                    first_bbox[1],
                    max(first_bbox[2], second_bbox[2]),
                    second_bbox[3]
                ]
                
                # Remove the second line
                block['lines'] = [first_line] + lines[2:]
                
                # Update block bbox
                if block['lines']:
                    all_bboxes = [line.get('bbox', [0,0,0,0]) for line in block['lines']]
                    block['bbox'] = [
                        min(b[0] for b in all_bboxes),
                        min(b[1] for b in all_bboxes),
                        max(b[2] for b in all_bboxes),
                        max(b[3] for b in all_bboxes)
                    ]
                break
    
    # If header not found, insert it at the beginning of the multi-class section
    if not header_found:
        logger.info("Multi-Class and Dual-Class Characters header not found - inserting it")
        
        # Find the "Any demihuman character" intro paragraph to position the header before it
        intro_y = None
        for block in blocks:
            if block.get("type") != "text":
                continue
            
            all_text = ''
            for line in block.get('lines', []):
                all_text += ''.join(span.get('text', '') for span in line.get('spans', []))
            
            # Be robust to leading fragments/splits across lines by using containment rather than startswith
            if "Any demihuman" in all_text:
                intro_y = block.get("bbox", [0, 0, 0, 0])[1]
                break
        
        # If we found the intro paragraph, place the header 30 pixels above it
        # Otherwise, derive a reasonable Y from the earliest right-column colored header,
        # falling back to a safe default if none are found.
        if intro_y is not None:
            header_y = intro_y - 30
        else:
            try:
                right_col_header_ys: list[float] = []
                for b in blocks:
                    if b.get("type") != "text":
                        continue
                    for ln in b.get("lines", []):
                        spans = ln.get("spans", [])
                        if any(s.get("color") == "#ca5804" for s in spans):
                            bbox = ln.get("bbox", [0, 0, 0, 0])
                            x0 = bbox[0] if bbox else 0
                            y0 = bbox[1] if bbox else 0
                            # Right column heuristic for this page
                            if x0 >= 298:
                                right_col_header_ys.append(y0)
                header_y = (min(right_col_header_ys) - 30) if right_col_header_ys else 265
            except Exception:
                header_y = 265
        
        # Create the header block in the right column (x=298-518 for page 19)
        header_block = {
            "type": "text",
            "lines": [{
                "spans": [{
                    "text": "Multi-Class and Dual-Class Characters",
                    "color": "#ca5804",  # Header color
                    "size": 10.8  # Standard header size
                }],
                "bbox": [298, header_y, 518, header_y + 10]
            }],
            "bbox": [298, header_y, 518, header_y + 10]
        }
        
        # Insert at the beginning of blocks list so it appears first in the section
        page.setdefault("blocks", []).insert(0, header_block)
        logger.info(f"Inserted Multi-Class and Dual-Class Characters header at Y={header_y}")


def _merge_multiclass_intro_paragraph(page: dict) -> None:
    """
    Merge the split "Any demihuman character" paragraph on page 19.
    
    This paragraph starts with "Any demihuman character who meets the ability"
    and ends with "based upon the race of the character." but is split across
    MULTIPLE blocks in the PDF. We need to merge them all into one block.
    """
    # Find the first part: "Any demihuman character who meets the ability"
    first_block_idx = None
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        all_text = ''
        for line in block.get('lines', []):
            all_text += ''.join(span.get('text', '') for span in line.get('spans', []))
        
        if all_text.strip() == "Any demihuman character who meets the ability":
            first_block_idx = idx
            break
    
    if first_block_idx is None:
        return
    
    first_block = page["blocks"][first_block_idx]
    
    # Find ALL blocks that are part of this paragraph by looking for specific text fragments
    # The paragraph continues with: "requirements may elect", "character, subject", 
    # "Players Handbook. The following", "possible character class combinations", "based upon the race"
    paragraph_fragments = [
        "requirements may elect",
        "character, subject",
        "Players Handbook. The following",
        "possible character class combinations",
        "based upon the race"
    ]
    
    blocks_to_merge = []
    for fragment in paragraph_fragments:
        for idx, block in enumerate(page.get("blocks", [])):
            if idx == first_block_idx:
                continue  # Skip the first block itself
            if block.get("type") != "text":
                continue
            
            all_text = ''
            for line in block.get('lines', []):
                all_text += ''.join(span.get('text', '') for span in line.get('spans', []))
            
            if fragment in all_text:
                blocks_to_merge.append((idx, block))
                break  # Found this fragment, move to next
    
    if not blocks_to_merge:
        return
    
    # Merge all blocks into the first one
    for idx, block in blocks_to_merge:
        first_block["lines"].extend(block["lines"])
        
        # Update bounding box
        first_bbox = first_block.get("bbox", [0, 0, 0, 0])
        block_bbox = block.get("bbox", [0, 0, 0, 0])
        first_block["bbox"] = [
            min(first_bbox[0], block_bbox[0]),
            min(first_bbox[1], block_bbox[1]),
            max(first_bbox[2], block_bbox[2]),
            max(first_bbox[3], block_bbox[3])
        ]
        
        # Clear the merged block
        page["blocks"][idx] = {
            "type": "text",
            "lines": [],
            "bbox": [0, 0, 0, 0]
        }


def _fix_halfgiant_header(page: dict) -> None:
    """
    Fix the Half-giant header to be a subheader (H2) instead of a main header (H1).
    The Half-giant header has "XXXIII." prefix but should be styled as a subheader.
    We add a marker to indicate this header should be treated as a subheader.
    """
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        
        all_text = ''
        for line in block.get('lines', []):
            all_text += ''.join(span.get('text', '') for span in line.get('spans', []))
        
        if all_text.strip() == "Half-giant":
            # Mark this header as a subheader by adding a marker
            # This will prevent it from getting a Roman numeral and will apply subheader styling
            block['__subheader'] = True
            break


def _extract_text_between_positions(page: dict, start_y: float, end_y: float, x_min: float = 0, x_max: float = 999) -> list[tuple[float, str]]:
    """
    Extract text from blocks between two Y positions and within an X range.
    
    Returns list of (y_position, text) tuples, sorted by Y position.
    """
    results = []
    
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        x, y = bbox[0], bbox[1]
        
        # Check if block is in the right position
        if start_y < y < end_y and x_min <= x <= x_max:
            text = ''
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text += span.get('text', '')
            
            text = text.strip()
            if text:
                results.append((y, text))
    
    # Sort by Y position
    results.sort(key=lambda x: x[0])
    return results


def _extract_all_multiclass_blocks(page: dict) -> list[tuple[float, float, str]]:
    """
    Extract ALL multi-class combination blocks from a page.
    Returns list of (y_pos, x_pos, text) tuples.
    """
    import re
    
    results = []
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        x, y = bbox[0], bbox[1]
        
        text = ''
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                text += span.get('text', '')
        
        text = text.strip()
        
        # Check if it's a multi-class combination
        if '/' in text and any(cls in text for cls in ['Fighter', 'Cleric', 'Thief', 'Psionicist', 'Mage', 'Illusionist', 'Ranger', 'Druid']):
            # Split concatenated combinations
            if ' ' not in text and text.count('/') >= 1:
                parts = re.split(r'(?<=[a-z])(?=[A-Z])', text)
                for part in parts:
                    if '/' in part and part.strip():
                        results.append((y, x, part.strip()))
            else:
                results.append((y, x, text.strip()))
    
    return results


def _group_blocks_into_sections(blocks: list[tuple[float, float, str]], y_threshold: float = 80) -> list[list[tuple[float, float, str]]]:
    """
    Group blocks into sections based on Y-position gaps.
    A gap larger than y_threshold indicates a new section/race.
    """
    if not blocks:
        return []
    
    # Sort by Y position
    sorted_blocks = sorted(blocks, key=lambda b: b[0])
    
    sections = []
    current_section = [sorted_blocks[0]]
    
    for i in range(1, len(sorted_blocks)):
        prev_y = sorted_blocks[i-1][0]
        curr_y = sorted_blocks[i][0]
        
        if curr_y - prev_y > y_threshold:
            # Big gap - start new section
            sections.append(current_section)
            current_section = [sorted_blocks[i]]
        else:
            current_section.append(sorted_blocks[i])
    
    if current_section:
        sections.append(current_section)
    
    return sections


def _sort_blocks_column_first(blocks: list[tuple[float, float, str]]) -> list[str]:
    """
    Sort blocks in column-first order for 2-column layout.
    Groups blocks by column (left vs right), sorts each column by Y, then interleaves.
    """
    if not blocks:
        return []
    
    # Find the median X to split into left/right columns
    x_positions = [b[1] for b in blocks]
    median_x = sorted(x_positions)[len(x_positions) // 2]
    
    # Split into columns
    left_col = sorted([b for b in blocks if b[1] < median_x], key=lambda b: b[0])
    right_col = sorted([b for b in blocks if b[1] >= median_x], key=lambda b: b[0])
    
    # For column-first order, collect all from left column, then all from right
    result = [b[2] for b in left_col] + [b[2] for b in right_col]
    
    return result


def _extract_multiclass_text_values(page: dict, header_y: float, next_header_y: float, column_x_min: float = 290, column_x_max: float = 550) -> list[str]:
    """
    Extract multi-class combination text from blocks between two headers.
    
    Returns a list of multi-class combination strings (e.g., "Fighter/Cleric").
    """
    import re
    
    # Get all text between the headers
    text_blocks = _extract_text_between_positions(page, header_y, next_header_y, column_x_min, column_x_max)
    
    combinations = []
    for y, text in text_blocks:
        # Check if it's a multi-class combination (contains / and class names)
        if '/' in text and any(cls in text for cls in ['Fighter', 'Cleric', 'Thief', 'Psionicist', 'Mage', 'Illusionist', 'Ranger', 'Druid']):
            # Sometimes multiple combinations are concatenated without spaces
            # Examples: "Fighter/ClericFighter/Psionicist" or "Cleric/ThiefPsionicist/Thief"
            # Split on capital letter that follows a lowercase letter (no space between)
            if ' ' not in text and text.count('/') >= 1:
                # Split before capital letters that follow lowercase letters
                parts = re.split(r'(?<=[a-z])(?=[A-Z])', text)
                for part in parts:
                    if '/' in part and part.strip():
                        combinations.append(part.strip())
            else:
                # Single combination or has spaces
                combinations.append(text.strip())
    
    return combinations


def build_multiclass_table(combinations: list[str], num_cols: int = 2) -> dict:
    """
    Build a 2-column table from a list of multi-class combinations in column-first order.
    
    This is a reusable function that takes any list of combination strings and creates
    a properly formatted table structure. Column-first order means the list is split
    into columns, with items filling the left column first, then the right column.
    
    Args:
        combinations: List of combination strings (e.g., ["Fighter/Cleric", "Fighter/Thief", ...])
        num_cols: Number of columns (default 2)
    
    Returns:
        A table dict with 'rows' containing properly formatted cells for journal.py
        
    Example:
        Given 8 combinations and 2 columns:
        combinations = ["A", "B", "C", "D", "E", "F", "G", "H"]
        Result table layout:
            | A | E |
            | B | F |
            | C | G |
            | D | H |
    """
    if not combinations:
        return {"rows": []}
    
    # Calculate number of rows needed (ceiling division)
    num_rows = (len(combinations) + num_cols - 1) // num_cols
    
    # Build table in column-first order
    rows = []
    for row_idx in range(num_rows):
        cells = []
        for col_idx in range(num_cols):
            # Column-first indexing: col_idx * num_rows + row_idx
            combo_idx = col_idx * num_rows + row_idx
            
            if combo_idx < len(combinations):
                cell_text = combinations[combo_idx]
            else:
                cell_text = ""  # Empty cell for partial last column
            
            # Create cell structure expected by journal.py
            cells.append({
                "text": cell_text,
                "spans": [{"text": cell_text, "color": "#000000", "font": "Arial", "size": 9}] if cell_text else []
            })
        
        rows.append({"cells": cells})
    
    return {"rows": rows}


def _extract_combinations_from_source_pdf(pdf_path: str, page_nums: list[int]) -> list[tuple[int, float, float, str]]:
    """
    Extract multi-class combinations directly from source PDF.
    
    This extracts from the SOURCE PDF before any processing, ensuring we get
    clean data without mixed tables or processed artifacts.
    
    Args:
        pdf_path: Path to the source PDF
        page_nums: List of PDF page numbers to extract from
    
    Returns:
        List of (page_num, y, x, combination_text) tuples
    """
    import fitz
    
    doc = fitz.open(pdf_path)
    all_combos = []
    
    class_names = ['Fighter', 'Cleric', 'Thief', 'Psionicist', 'Mage', 'Illusionist', 'Ranger', 'Druid']
    
    for page_num in page_nums:
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block['type'] == 0:  # Text block
                bbox = block['bbox']
                y, x = bbox[1], bbox[0]
                
                text = ''
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        text += span.get('text', '')
                
                text = text.strip()
                
                # Check if it's a multi-class combination
                if '/' in text and any(cls in text for cls in class_names):
                    # Split concatenated combinations
                    parts = text.split()
                    for part in parts:
                        import re
                        subparts = re.split(r'(?<=[a-z])(?=[A-Z])', part)
                        for subpart in subparts:
                            subpart = subpart.strip()
                            if '/' in subpart:
                                all_combos.append((page_num, y, x, subpart))
    
    doc.close()
    return all_combos


# _extract_multiclass_combinations - MOVED to chapter_3/multiclass.py


def _merge_multiclass_intro_paragraph(page: dict) -> None:
    """Merge split intro paragraph in the Multi-Class section into a single block.
    
    Approach:
    - Locate the 'Multi-Class Combinations' subheader.
    - Concatenate all subsequent plain text blocks up to (but not including) the
      first race subheader (e.g., 'Dwarf', 'Elf or Half-elf', etc.).
    - Replace the first intro text block with the combined text and clear the rest.
    """
    if not page or page.get("type") == "image":
        return
    
    def _block_text(block: dict) -> str:
        lines = block.get("lines", [])
        return "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
    
    def _has_colored_header_spans(block: dict) -> bool:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("color") == "#ca5804":
                    return True
        return False
    
    def _is_text_block(block: dict) -> bool:
        return block.get("type") == "text" and bool(block.get("lines"))
    
    def _is_race_header_text(text: str) -> bool:
        t = _normalize_plain_text(text).strip()
        return t in {"Dwarf", "Elf or Half-elf", "Half-giant", "Halfling", "Mul", "Thri-kreen"}
    
    blocks = page.get("blocks", [])
    if not blocks:
        return
    
    # 1) Find the "Multi-Class Combinations" subheader index (if present)
    header_idx = None
    for idx, block in enumerate(blocks):
        if not _is_text_block(block):
            continue
        text = _normalize_plain_text(_block_text(block)).strip()
        if "Multi-Class Combinations" in text:
            header_idx = idx
            break
    
    # 2) Determine start index for the intro paragraph (first non-empty text after header)
    start_idx = None
    search_from = header_idx + 1 if header_idx is not None else 0
    for idx in range(search_from, len(blocks)):
        block = blocks[idx]
        if not _is_text_block(block):
            continue
        text = _normalize_plain_text(_block_text(block)).strip()
        if text:
            start_idx = idx
            break
    
    if start_idx is None:
        return
    
    # 3) Find the end index: stop before the first race subheader (colored header span with race name)
    end_idx = len(blocks)
    for idx in range(start_idx + 1, len(blocks)):
        block = blocks[idx]
        if not _is_text_block(block):
            continue
        text = _normalize_plain_text(_block_text(block)).strip()
        if not text:
            continue
        # Stop at the first colored header that looks like a race header
        if _has_colored_header_spans(block) and _is_race_header_text(text):
            end_idx = idx
            break
    
    # 4) Concatenate text across [start_idx, end_idx)
    parts: list[str] = []
    for idx in range(start_idx, end_idx):
        text = _normalize_plain_text(_block_text(blocks[idx])).strip()
        if not text:
            continue
        parts.append(text)
    
    if not parts:
        return
    
    combined_text = " ".join(parts)
    # Normalize whitespace
    combined_text = " ".join(combined_text.split())
    
    # 5) Replace text in the first intro block and clear the rest
    intro_block = blocks[start_idx]
    intro_lines = intro_block.get("lines", [])
    if not intro_lines:
        return
    # Use the last line's last span as the text container
    last_line = intro_lines[-1]
    spans = last_line.get("spans", [])
    if not spans:
        spans.append({"text": ""})
        last_line["spans"] = spans
    spans[-1]["text"] = combined_text
    _update_block_bbox(intro_block)
    
    # Clear subsequent blocks that contributed to the paragraph
    for idx in range(start_idx + 1, end_idx):
        blocks[idx]["lines"] = []
        blocks[idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    page["blocks"] = blocks

def _adjust_header_levels(pages: List[dict]) -> None:
    """Adjust header levels for Chapter 3 to match document hierarchy.
    
    - Warriors, Wizard, Priest, Rogue, Psionicist (Dark Sun variation) → Keep as H1 (default)
    - Fighter, Gladiator, Ranger, Defiler, Preserver, Illusionist, Cleric, Druid, Templar, Bard, Thief → H3
    - Fighters Followers, Rangers Followers, Defiler Experience Levels, etc. → H4
    - Sphere headers (Sphere of Earth, etc.) → H4
    
    This function adds CSS class markers to the header spans so that the TOC/anchor
    generation logic recognizes them as H3/H4 headers and handles them correctly
    (no roman numerals, proper indentation, etc.).
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Class names that should be H3
    h3_class_names = [
        "Fighter", "Gladiator", "Ranger",
        "Defiler", "Preserver", "Illusionist",
        "Cleric", "Druid", "Templar",
        "Bard", "Thief"
    ]
    
    # Subsection headers that should be H4
    h4_subsections = [
        "Fighters Followers", "Rangers Followers",
        "Defiler Experience Levels",
        "Sphere of Earth", "Sphere of Air", "Sphere of Fire", "Sphere of Water",
        "Templar Spell Progression", "Spell Level",
        "Bard Poison Table",
        "Thieving Skill Exceptional Dexterity Adjustments",
        "Thieving Skill Racial Adjustments",
        "Inherent Potential Table"
    ]
    
    modified_count = 0
    
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
                
            lines = block.get("lines", [])
            if not lines:
                continue
            
            # Get text from first line to check header
            first_line_text = "".join(
                span.get("text", "") for span in lines[0].get("spans", [])
            ).strip()
            
            # Check if this is a colored header (color #ca5804 and size 10.8)
            is_header = False
            header_spans = []
            for line in lines:
                for span in line.get("spans", []):
                    if span.get("color") == "#ca5804" and span.get("size") in [10.8, 11.0]:
                        is_header = True
                        header_spans.append(span)
                if is_header:
                    break
            
            if not is_header or not header_spans:
                continue
            
            # Check if this header should be H3
            if any(class_name in first_line_text for class_name in h3_class_names):
                # Add CSS class marker to the header spans
                for span in header_spans:
                    # Add CSS class attribute to mark this as H3
                    span["__css_class"] = "header-h3"
                modified_count += 1
                logger.debug(f"Marked '{first_line_text}' as H3")
            
            # Check if this header should be H4
            elif any(subsection in first_line_text for subsection in h4_subsections):
                # Add CSS class marker to the header spans
                for span in header_spans:
                    # Add CSS class attribute to mark this as H4
                    span["__css_class"] = "header-h4"
                modified_count += 1
                logger.debug(f"Marked '{first_line_text}' as H4")
    
    logger.info(f"Adjusted {modified_count} header levels in Chapter 3")


def apply_chapter_3_adjustments(section_data: dict) -> None:
    """Apply all Chapter 3 specific adjustments to the section data.
    
    This function orchestrates all class-specific adjustments by calling
    helper functions from the chapter_3.adjustments module.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("===  apply_chapter_3_adjustments called ===")
    
    from .chapter_3.adjustments import (
        normalize_all_text,
        apply_warrior_adjustments,
        apply_wizard_adjustments,
        apply_priest_adjustments,
        apply_rogue_adjustments,
        apply_psionicist_adjustments,
        apply_multiclass_adjustments,
        apply_general_adjustments,
        remove_page_numbers,
    )
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    logger.info(f"Chapter 3 has {len(pages)} pages")
    
    # Apply adjustments in logical order
    normalize_all_text(pages)
    remove_page_numbers(pages)
    apply_general_adjustments(pages)
    apply_warrior_adjustments(pages)
    apply_wizard_adjustments(pages)
    apply_priest_adjustments(pages)
    logger.info("About to call apply_rogue_adjustments...")
    apply_rogue_adjustments(pages)
    logger.info("apply_rogue_adjustments completed")
    apply_psionicist_adjustments(pages)
    apply_multiclass_adjustments(pages)
    
    # Adjust header levels for proper hierarchy
    _adjust_header_levels(pages)
    
