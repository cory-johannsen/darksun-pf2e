"""
Class requirements table extraction for Chapter 3.

This module contains specialized functions to extract and format class requirements
tables for ALL player classes in Dark Sun. Each class has a standard 3-row, 2-column
table containing:
- Row 1: Ability Requirements (list of "Ability #" pairs)
- Row 2: Prime Requisite (one or more abilities)
- Row 3: Races Allowed (list of races)
"""

import logging
from typing import List, Dict

from .common import extract_class_ability_table

logger = logging.getLogger(__name__)


# Class names that require requirements tables
# This is the definitive list of all player classes in Chapter 3
PLAYER_CLASSES_WITH_REQUIREMENTS = [
    # Warriors (pages 3-6)
    "Fighter",
    "Gladiator", 
    "Ranger",
    # Wizards (pages 7-10)
    "Defiler",
    "Preserver",
    "Illusionist",
    # Priests (pages 10-15)
    "Cleric",
    "Druid",
    "Templar",
    # Rogues (pages 16-18)
    "Bard",
    "Thief",
    # Psionicist (page 19)
    "Psionicist"
]


def extract_fighter_requirements_table(page: dict) -> bool:
    """Extract Fighter requirements table from page (PDF page 24).
    
    Expected format:
    - Ability Requirements: Strength 9
    - Prime Requisite: Strength
    - Allowed Races: All
    """
    logger.info("Extracting Fighter requirements table")
    return extract_class_ability_table(page, "Fighter")


def extract_gladiator_requirements_table(page: dict) -> bool:
    """Extract Gladiator requirements table from page (PDF page 25).
    
    Expected format:
    - Ability Requirements: Strength 13, Dexterity 12, Constitution 15
    - Prime Requisite: Strength
    - Allowed Races: All
    """
    logger.info("Extracting Gladiator requirements table")
    return extract_class_ability_table(page, "Gladiator")


def extract_ranger_requirements_table(page: dict) -> bool:
    """Extract Ranger requirements table from page (PDF page 27).
    
    Ranger has an extremely fragmented format across 8+ blocks:
    - Block 17: "Ranger" (header)
    - Block 18: "Ability Requirements: Strength 13"
    - Block 19: "Dexterity 13"
    - Block 20: "Constitution 14 Wisdom 14"
    - Block 21: "Strength, Dexterity, Wis-"
    - Block 22: "Prime Requisites:"
    - Block 23: "dom Human, Elf, Half-elf,"
    - Block 24: "Races Allowed:"
    - Block 25: "Halfling, Thri-kreen"
    
    This requires custom extraction logic.
    """
    logger.info("Extracting Ranger requirements table")
    from .common import normalize_plain_text, create_class_ability_table
    
    # Find Ranger header
    ranger_header_idx = None
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        text = normalize_plain_text(text).strip()
        if text == "Ranger":
            ranger_header_idx = idx
            break
    
    if ranger_header_idx is None:
        logger.warning("  Ranger: Header not found")
        return False
    
    # Manually extract and reconstruct the requirements from fragmented blocks
    # Expected indices (relative to header):
    # +1: "Ability Requirements: Strength 13"
    # +2: "Dexterity 13"
    # +3: "Constitution 14 Wisdom 14"
    # +4: "Strength, Dexterity, Wis-"
    # +5: "Prime Requisites:"
    # +6: "dom Human, Elf, Half-elf,"
    # +7: "Races Allowed:"
    # +8: "Halfling, Thri-kreen"
    
    try:
        blocks_to_clear = []
        
        # Collect ability requirements (blocks +1, +2, +3)
        abilities = []
        for offset in [1, 2, 3]:
            idx = ranger_header_idx + offset
            if idx < len(page["blocks"]):
                block = page["blocks"][idx]
                lines = block.get("lines", [])
                text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
                text = normalize_plain_text(text)
                # Remove the "Ability Requirements:" label if present
                text = text.replace("Ability Requirements:", "").strip()
                if text:
                    abilities.append(text)
                blocks_to_clear.append(idx)
        
        abilities_text = " ".join(abilities)
        
        # Collect prime requisite (blocks +4, +5, +6)
        # Block +4 has "Strength, Dexterity, Wis-"
        # Block +5 has "Prime Requisites:" (label)
        # Block +6 has "dom Human, Elf, Half-elf,"
        # Need to extract: "Wis-" + "dom" = "Wisdom" and prepend "Strength, Dexterity, "
        prime_parts = []
        
        idx_4 = ranger_header_idx + 4
        if idx_4 < len(page["blocks"]):
            block = page["blocks"][idx_4]
            lines = block.get("lines", [])
            text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            text = normalize_plain_text(text).strip()
            prime_parts.append(text)
            blocks_to_clear.append(idx_4)
        
        idx_6 = ranger_header_idx + 6
        if idx_6 < len(page["blocks"]):
            block = page["blocks"][idx_6]
            lines = block.get("lines", [])
            text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            text = normalize_plain_text(text)
            # This block has "dom Human, Elf, Half-elf," - extract just "dom"
            if text.startswith("dom "):
                prime_parts.append("dom")
            blocks_to_clear.append(idx_6)
        
        # Also clear the "Prime Requisites:" label block
        idx_5 = ranger_header_idx + 5
        if idx_5 < len(page["blocks"]):
            blocks_to_clear.append(idx_5)
        
        # Reconstruct prime requisite by joining "Wis-" + "dom"
        # Remove hyphen at word break
        prime_text = "".join(prime_parts).replace("Wis-dom", "Wisdom")
        
        # Collect races allowed (blocks +6, +7, +8)
        # Block +6 has "dom Human, Elf, Half-elf," - extract after "dom "
        # Block +7 has "Races Allowed:" (label)
        # Block +8 has "Halfling, Thri-kreen"
        races_parts = []
        
        if idx_6 < len(page["blocks"]):
            block = page["blocks"][idx_6]
            lines = block.get("lines", [])
            text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            text = normalize_plain_text(text)
            # Extract "Human, Elf, Half-elf," after "dom "
            if "dom " in text:
                races_parts.append(text.split("dom ", 1)[1])
        
        idx_8 = ranger_header_idx + 8
        if idx_8 < len(page["blocks"]):
            block = page["blocks"][idx_8]
            lines = block.get("lines", [])
            text = " ".join(" ".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            text = normalize_plain_text(text).strip()
            races_parts.append(text)
            blocks_to_clear.append(idx_8)
        
        # Also clear the "Races Allowed:" label block
        idx_7 = ranger_header_idx + 7
        if idx_7 < len(page["blocks"]):
            blocks_to_clear.append(idx_7)
        
        races_text = " ".join(races_parts)
        
        # Create the table
        table_rows = [
            ("Ability Requirements:", abilities_text),
            ("Prime Requisite:", prime_text),
            ("Races Allowed:", races_text)
        ]
        
        # Use the bbox from the first ability block
        bbox = page["blocks"][ranger_header_idx + 1]["bbox"] if ranger_header_idx + 1 < len(page["blocks"]) else [0, 0, 0, 0]
        
        # Create table at the position after the header
        create_class_ability_table(page, table_rows, bbox, blocks_to_clear)
        
        logger.info(f"  Ranger: Successfully created requirements table with {len(table_rows)} rows (custom handler)")
        return True
        
    except Exception as e:
        logger.error(f"  Ranger: Failed to extract requirements table: {e}")
        return False


def extract_defiler_requirements_table(page: dict) -> bool:
    """Extract Defiler requirements table from page (PDF page 27).
    
    Expected format:
    - Ability Requirements: Intelligence 9
    - Prime Requisite: Intelligence
    - Races Allowed: Human, Elf, Half-elf
    """
    logger.info("Extracting Defiler requirements table")
    return extract_class_ability_table(page, "Defiler")


def extract_preserver_requirements_table(page: dict) -> bool:
    """Extract Preserver requirements table from page (0-indexed page 8, PDF page 29).
    
    Expected format:
    - Ability Requirements: Intelligence 9
    - Prime Requisite: Intelligence
    - Races Allowed: Human, Elf, Half-elf
    """
    logger.info("Extracting Preserver requirements table")
    return extract_class_ability_table(page, "Preserver")


def extract_illusionist_requirements_table(page: dict) -> bool:
    """Extract Illusionist requirements table from page (PDF page 29).
    
    Expected format:
    - Ability Requirements: Dexterity 16
    - Prime Requisite: Intelligence
    - Races Allowed: Human, Elf, Half-elf, Halfling
    """
    logger.info("Extracting Illusionist requirements table")
    return extract_class_ability_table(page, "Illusionist")


def extract_cleric_requirements_table(page: dict) -> bool:
    """Extract Cleric requirements table from page (PDF page 30).
    
    Expected format:
    - Ability Requirements: Wisdom 9
    - Prime Requisite: Wisdom
    - Races Allowed: All
    """
    logger.info("Extracting Cleric requirements table")
    return extract_class_ability_table(page, "Cleric")


def extract_druid_requirements_table(page: dict) -> bool:
    """Extract Druid requirements table from page (PDF page 32).
    
    Expected format:
    - Ability Requirements: Wisdom 12, Charisma 15
    - Prime Requisites: Wisdom, Charisma
    - Races Allowed: Human, Half-elf, Halfling, mul, Thri-kreen
    """
    logger.info("Extracting Druid requirements table")
    return extract_class_ability_table(page, "Druid")


def extract_templar_requirements_table(page: dict) -> bool:
    """Extract Templar requirements table from page (PDF page 34).
    
    Expected format:
    - Ability Requirements: Wisdom 3, Intelligence 10
    - Prime Requisite: Wisdom
    - Races Allowed: Human, Dwarf, Elf, Half-elf
    """
    logger.info("Extracting Templar requirements table")
    return extract_class_ability_table(page, "Templar")


def extract_bard_requirements_table(page: dict) -> bool:
    """Extract Bard requirements table from page (PDF page 37).
    
    Expected format:
    - Ability Requirements: Dexterity 12, Intelligence 13, Charisma 15
    - Prime Requisites: Dexterity, Charisma
    - Races Allowed: Human, Half-elf
    """
    logger.info("Extracting Bard requirements table")
    return extract_class_ability_table(page, "Bard")


def extract_thief_requirements_table(page: dict) -> bool:
    """Extract Thief requirements table from page (PDF page 38).
    
    Expected format:
    - Ability Requirements: Dexterity 9
    - Prime Requisite: Dexterity
    - Races Allowed: All
    """
    logger.info("Extracting Thief requirements table")
    return extract_class_ability_table(page, "Thief")


def extract_psionicist_requirements_table(page: dict) -> bool:
    """Extract Psionicist requirements table from page (PDF page 39).
    
    Expected format:
    - Ability Requirements: Constitution 11, Intelligence 12, Wisdom 15
    - Prime Requisites: Constitution, Wisdom
    - Races Allowed: Any
    """
    logger.info("Extracting Psionicist requirements table")
    return extract_class_ability_table(page, "Psionicist")


def extract_all_class_requirements_tables(pages: List[dict]) -> Dict[str, bool]:
    """Extract all class requirements tables from their respective pages.
    
    Args:
        pages: List of page dictionaries from the chapter
        
    Returns:
        Dictionary mapping class names to extraction success status
    """
    logger.info("=== Extracting ALL class requirements tables ===")
    
    results = {}
    
    # Warriors
    if len(pages) > 3:  # Fighter is on page 3 (0-indexed), PDF page 24
        results["Fighter"] = extract_fighter_requirements_table(pages[3])
    
    if len(pages) > 5:  # Gladiator is on page 5, PDF page 26
        results["Gladiator"] = extract_gladiator_requirements_table(pages[5])
    
    if len(pages) > 6:  # Ranger is on page 6, PDF page 27
        results["Ranger"] = extract_ranger_requirements_table(pages[6])
    
    # Wizards
    if len(pages) > 7:  # Defiler is on page 7, PDF page 28
        results["Defiler"] = extract_defiler_requirements_table(pages[7])
    
    if len(pages) > 8:  # Preserver is on page 8, PDF page 29
        results["Preserver"] = extract_preserver_requirements_table(pages[8])
    
    if len(pages) > 9:  # Illusionist is on page 9, PDF page 30
        results["Illusionist"] = extract_illusionist_requirements_table(pages[9])
    
    # Priests
    if len(pages) > 10:  # Cleric is on page 10, PDF page 31
        results["Cleric"] = extract_cleric_requirements_table(pages[10])
    
    if len(pages) > 12:  # Druid is on page 12, PDF page 33
        results["Druid"] = extract_druid_requirements_table(pages[12])
    
    if len(pages) > 13:  # Templar is on page 13, PDF page 34
        results["Templar"] = extract_templar_requirements_table(pages[13])
    
    # Rogues
    if len(pages) > 16:  # Bard is on page 16, PDF page 37
        results["Bard"] = extract_bard_requirements_table(pages[16])
    
    if len(pages) > 17:  # Thief is on page 17, PDF page 38
        results["Thief"] = extract_thief_requirements_table(pages[17])
    
    # Psionicist
    if len(pages) > 18:  # Psionicist is on page 18, PDF page 39
        results["Psionicist"] = extract_psionicist_requirements_table(pages[18])
    
    # Log results
    successful = [k for k, v in results.items() if v]
    failed = [k for k, v in results.items() if not v]
    
    logger.info(f"Successfully extracted {len(successful)} class requirements tables: {successful}")
    if failed:
        logger.warning(f"Failed to extract {len(failed)} class requirements tables: {failed}")
    
    return results

