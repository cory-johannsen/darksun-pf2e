"""
Chapter 3 class-specific adjustment helper functions.

This module contains adjustment functions extracted from apply_chapter_3_adjustments
to improve maintainability by grouping related operations.
"""

from __future__ import annotations

from typing import List


def normalize_all_text(pages: List[dict]) -> None:
    """Normalize all text in pages to remove control characters.
    
    Args:
        pages: List of page dictionaries
    """
    def normalize_plain_text(text: str) -> str:
        """Normalize text by replacing special characters."""
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--')  # Em dash
        text = text.replace('\xad', '')  # Soft hyphen
        text = text.replace('\x92', '')  # PRIVATE USE TWO control character
        text = text.replace('\x99', ' ')  # SINGLE CHARACTER INTRODUCER control character
        return text
    
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if "text" in span:
                            span["text"] = normalize_plain_text(span["text"])



# Import all the class-specific functions from their modules
from .common import (
    force_warrior_classes_paragraph_breaks,
    extract_class_ability_requirements_table,
)

from .warrior import (
    force_fighter_paragraph_breaks,
    force_fighter_benefits_paragraph_breaks,
    force_gladiator_paragraph_breaks,
    extract_fighters_followers_table,
)

from .ranger import (
    force_ranger_paragraph_breaks,
    extract_rangers_followers_table,
    extract_rangers_followers_table_from_pages,
    fix_ranger_ability_requirements_table,
    reconstruct_rangers_followers_table_inplace,
    mark_ranger_description_blocks,
)

from .wizard import (
    force_wizard_classes_paragraph_breaks,
    force_wizard_section_paragraph_breaks,
    force_defiler_paragraph_breaks,
    extract_defiler_experience_levels_table,
    force_preserver_paragraph_breaks,
)

from .priest import (
    force_priest_section_paragraph_breaks,
    force_spheres_of_magic_paragraph_breaks,
    force_cleric_paragraph_breaks,
    force_cleric_powers_paragraph_breaks,
    force_druid_paragraph_breaks,
    force_druid_granted_powers_paragraph_breaks,
    force_templar_paragraph_breaks,
    fix_templar_ability_table,
    extract_templar_spell_progression_table,
    force_priest_classes_paragraph_breaks,
)

from .rogue import (
    force_rogue_classes_paragraph_breaks,
    force_thief_paragraph_breaks,
    force_thief_abilities_paragraph_breaks,
    extract_thieving_dexterity_adjustments_table,
    extract_thieving_racial_adjustments_table,
    force_bard_paragraph_breaks,
    force_bard_poison_paragraph_breaks,
    extract_bard_poison_table,
)

from .psionicist import (
    force_psionicist_class_paragraph_breaks,
    force_psionicist_paragraph_breaks,
    extract_inherent_potential_table,
)

from .multiclass import (
    force_multiclass_paragraph_breaks,
    force_level_advancement_paragraph_breaks,
    extract_multiclass_combinations,
)

from .class_requirements import (
    extract_all_class_requirements_tables,
)


def apply_warrior_adjustments(pages: List[dict]) -> None:
    """Apply all warrior-related adjustments (Fighter, Gladiator, Ranger).
    
    Args:
        pages: List of page dictionaries
    """
    # Warrior Classes overview (page 0)
    if len(pages) > 0:
        force_warrior_classes_paragraph_breaks(pages[0])
    
    # Fighter section (pages 3-4)
    if len(pages) > 3:
        force_fighter_paragraph_breaks(pages[3])
    if len(pages) > 4:
        force_fighter_paragraph_breaks(pages[4])
    
    # Fighter Benefits (page 4)
    if len(pages) > 4:
        force_fighter_benefits_paragraph_breaks(pages[4])
    
    # Fighter Followers table (page 4, PDF page 25)
    if len(pages) > 4:
        extract_fighters_followers_table(pages[4])
    
    # Gladiator section (page 5)
    if len(pages) > 5:
        force_gladiator_paragraph_breaks(pages[5])
    
    # Ranger section (pages 6-7)
    if len(pages) > 6:
        force_ranger_paragraph_breaks(pages[6])
    if len(pages) > 7:
        force_ranger_paragraph_breaks(pages[7])
    
    # Ranger Followers table (pages 6-7)
    if len(pages) > 7:
        extract_rangers_followers_table_from_pages(pages)
        # Need to reconstruct on BOTH pages 6 and 7 since malformed tables can appear on either
        reconstruct_rangers_followers_table_inplace(pages[6])
        reconstruct_rangers_followers_table_inplace(pages[7])
    
    # Ranger ability requirements (page 6)
    if len(pages) > 6:
        fix_ranger_ability_requirements_table(pages[6])
    
    # Mark Ranger description blocks (pages 6-7)
    # This also normalizes "RANGERS FOLLOWERS" to "Rangers Followers"
    if len(pages) > 6:
        mark_ranger_description_blocks(pages[6])
    if len(pages) > 7:
        mark_ranger_description_blocks(pages[7])
    
    # Normalize "RANGERS FOLLOWERS" to "Rangers Followers" across all pages
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") == "text":
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if "RANGERS FOLLOWERS" in span.get("text", ""):
                            span["text"] = span["text"].replace("RANGERS FOLLOWERS", "Rangers Followers")


def apply_wizard_adjustments(pages: List[dict]) -> None:
    """Apply all wizard-related adjustments (Defiler, Preserver).
    
    Args:
        pages: List of page dictionaries
    """
    # Wizard Classes overview (pages 0-1)
    if len(pages) > 0:
        force_wizard_classes_paragraph_breaks(pages[0])
    if len(pages) > 1:
        force_wizard_classes_paragraph_breaks(pages[1])
    
    # Wizard section (page 7)
    if len(pages) > 7:
        force_wizard_section_paragraph_breaks(pages[7])
    
    # Defiler section (page 7)
    if len(pages) > 7:
        force_defiler_paragraph_breaks(pages[7])
    
    # Defiler Experience table (page 8)
    if len(pages) > 8:
        extract_defiler_experience_levels_table(pages[8])
    
    # Preserver section (page 9)
    if len(pages) > 9:
        force_preserver_paragraph_breaks(pages[9])


def apply_priest_adjustments(pages: List[dict]) -> None:
    """Apply all priest-related adjustments (Cleric, Druid, Templar).
    
    Args:
        pages: List of page dictionaries
    """
    # Priest Classes overview (page 1)
    if len(pages) > 1:
        force_priest_classes_paragraph_breaks(pages[1])
    
    # Priest section (page 10)
    if len(pages) > 10:
        force_priest_section_paragraph_breaks(pages[10])
    
    # Spheres of Magic (page 10)
    if len(pages) > 10:
        force_spheres_of_magic_paragraph_breaks(pages[10])
    
    # Cleric section (pages 10-11)
    if len(pages) > 10:
        force_cleric_paragraph_breaks(pages[10])
    if len(pages) > 11:
        force_cleric_paragraph_breaks(pages[11])
    
    # Cleric Powers (pages 11-12)
    if len(pages) > 11:
        force_cleric_powers_paragraph_breaks(pages[11])
    if len(pages) > 12:
        force_cleric_powers_paragraph_breaks(pages[12])
    
    # Druid section (page 12)
    if len(pages) > 12:
        force_druid_paragraph_breaks(pages[12])
    
    # Druid Powers (page 13)
    if len(pages) > 13:
        force_druid_granted_powers_paragraph_breaks(pages[13])
    
    # Templar section (pages 13-16)
    for page_idx in range(13, min(17, len(pages))):
        force_templar_paragraph_breaks(pages[page_idx])
    
    # Templar ability table (page 14)
    if len(pages) > 14:
        fix_templar_ability_table(pages[14])
    
    # Templar spell progression (page 15)
    if len(pages) > 15:
        extract_templar_spell_progression_table(pages[15])


def apply_rogue_adjustments(pages: List[dict]) -> None:
    """Apply all rogue-related adjustments (Thief, Bard).
    
    Args:
        pages: List of page dictionaries
    """
    # Rogue Classes overview (page 1)
    if len(pages) > 1:
        force_rogue_classes_paragraph_breaks(pages[1])
    
    # Bard section (pages 16-17)
    if len(pages) > 16:
        force_bard_paragraph_breaks(pages[16])
    if len(pages) > 17:
        force_bard_paragraph_breaks(pages[17])
    
    # Bard Poison (page 17)
    if len(pages) > 17:
        force_bard_poison_paragraph_breaks(pages[17])
        extract_bard_poison_table(pages[17])
    
    # Thief section (pages 18-19)
    if len(pages) > 18:
        force_thief_paragraph_breaks(pages[18])
    if len(pages) > 19:
        force_thief_paragraph_breaks(pages[19])
    
    # Thief Abilities (page 19)
    if len(pages) > 19:
        force_thief_abilities_paragraph_breaks(pages[19])
    
    # Thieving tables (page 18, not 19!)
    if len(pages) > 18:
        extract_thieving_dexterity_adjustments_table(pages[18])
        extract_thieving_racial_adjustments_table(pages[18])


def apply_psionicist_adjustments(pages: List[dict]) -> None:
    """Apply all psionicist-related adjustments.
    
    Args:
        pages: List of page dictionaries
    """
    # Psionicist Class overview (page 1)
    if len(pages) > 1:
        force_psionicist_class_paragraph_breaks(pages[1])
    
    # Psionicist section with Inherent Potential Table (page 19 - 0-indexed)
    if len(pages) > 19:
        force_psionicist_paragraph_breaks(pages[19])
        extract_inherent_potential_table(pages[19])


def apply_multiclass_adjustments(pages: List[dict]) -> None:
    """Apply all multiclass-related adjustments.
    
    Args:
        pages: List of page dictionaries
    """
    # Multiclass section (page 2)
    if len(pages) > 2:
        force_multiclass_paragraph_breaks(pages[2])
    
    # Level Advancement (page 2)
    if len(pages) > 2:
        force_level_advancement_paragraph_breaks(pages[2])
    
    # Extract tables (pages 2-3, corresponding to pages 19-20 in PDF)
    if len(pages) > 3:
        extract_multiclass_combinations(pages[2], pages[3])


def apply_general_adjustments(pages: List[dict]) -> None:
    """Apply general adjustments that don't fit into specific class categories.
    
    Args:
        pages: List of page dictionaries
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("===== apply_general_adjustments CALLED =====")
    logger.info(f"Total pages: {len(pages)}")
    
    # Class Ability Requirements table (page 2, PDF page 23)
    if len(pages) > 2:
        logger.info("Calling extract_class_ability_requirements_table for page 2")
        extract_class_ability_requirements_table(pages[2])
    else:
        logger.warning(f"Not enough pages ({len(pages)}) to extract Class Ability Requirements table")
    
    # Extract individual class requirements tables for ALL player classes
    logger.info("Extracting individual class requirements tables")
    extract_all_class_requirements_tables(pages)


def remove_page_numbers(pages: List[dict]) -> None:
    """Remove stray page numbers from specific pages.
    
    Args:
        pages: List of page dictionaries
    """
    # Remove "2 7" from page 8
    if len(pages) > 8:
        blocks = pages[8].get("blocks", [])
        for block in blocks:
            if block.get("type") == "text":
                lines = block.get("lines", [])
                text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
                if text.strip() == "2 7":
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]
                    break
    
    # Remove "2 9" from page 10
    if len(pages) > 10:
        blocks = pages[10].get("blocks", [])
        for block in blocks:
            if block.get("type") == "text":
                lines = block.get("lines", [])
                text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
                if text.strip() == "2 9":
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]
                    break
    
    # Clear "3 0" from page 11, block 29
    if len(pages) > 11:
        blocks = pages[11].get("blocks", [])
        if len(blocks) > 29:
            block = blocks[29]
            if block.get("type") == "text":
                lines = block.get("lines", [])
                if lines:
                    text = "".join(span.get("text", "") for span in lines[0].get("spans", []))
                    if text.strip() == "3 0":
                        block["lines"] = []
                        block["bbox"] = [0.0, 0.0, 0.0, 0.0]
