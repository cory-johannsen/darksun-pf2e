"""Chapter 15 Processing - New Spells

This module handles extraction and formatting for Chapter 15 (New Spells).
Key responsibilities:
- Adjust header levels (H2 for spell level groups, H3 for individual spells)
- Extract and format the Find Familiar table (3 columns: Die Roll, Familiar, Sensory Powers)
- Extract and format the Mount table (2 columns: Caster Level, Mount)
- Extract and format the Reincarnation table (2 columns: D100 Roll, Incarnation)
- Extract and format the Doom Legion table (2 columns: Battle Type, Dice Roll)
- Extract and format the Time at Rest table (2 columns: Time at Rest, Chance to Ignore)
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def apply_chapter_15_adjustments(section_data: dict) -> None:
    """Apply all Chapter 15 specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    logger.info("=" * 60)
    logger.info("CHAPTER 15 ADJUSTMENTS CALLED!")
    logger.info("=" * 60)
    logger.info("Applying Chapter 15 adjustments")
    
    # Adjust header levels
    _adjust_spell_header_levels(section_data)
    
    # Extract Find Familiar table
    _extract_find_familiar_table(section_data)
    
    # Extract Mount table
    _extract_mount_table(section_data)
    
    # Extract Reincarnation table
    _extract_reincarnation_table(section_data)
    
    # Extract Doom Legion table
    _extract_doom_legion_table(section_data)
    
    # Extract Time at Rest table
    _extract_time_at_rest_table(section_data)
    
    logger.info("Chapter 15 adjustments complete")


def _adjust_spell_header_levels(section_data: dict) -> None:
    """Adjust header levels for spell sections.
    
    Spell level groups (e.g., "First Level Spells") should be H2.
    Individual spell names (e.g., "Charm Person", "Find Familiar", "Mount") should be H3.
    """
    logger.info("Adjusting spell header levels")
    
    pages = section_data.get("pages", [])
    
    # Patterns for different header types
    spell_level_pattern = re.compile(
        r'^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)[\s\-]?Level Spells$',
        re.IGNORECASE
    )
    
    # Spell names that should be H3
    # Note: We detect all colored spell headers automatically, but these require explicit marking
    first_level_spell_names = {
        "Charm Person",
        "Find Familiar",
        "Mount"
    }
    
    modifications = 0
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            # Get the full text of the block
            block_text = ""
            font_size = None
            color = None
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if span_text:
                        block_text += " " + span_text if block_text else span_text
                    # Capture font info from first span
                    if font_size is None:
                        font_size = span.get("size")
                        color = span.get("color")
            
            block_text = block_text.strip()
            
            # Check if this is a spell level header (should be H2)
            if spell_level_pattern.match(block_text):
                logger.info(f"  Marking '{block_text}' as H2")
                # Use the __render_as_h2 block-level flag
                block["__render_as_h2"] = True
                block["__header_text"] = block_text
                modifications += 1
            
            # Check if this is a specific spell name (should be H3)
            elif block_text in first_level_spell_names:
                logger.info(f"  Marking '{block_text}' as H3")
                # Use the __render_as_h3 block-level flag
                block["__render_as_h3"] = True
                block["__header_text"] = block_text
                modifications += 1
            
            # Also check for colored headers with spell header font (7.92 point, orange color)
            # These are individual spell names that should be H3
            elif (font_size and abs(font_size - 7.920000076293945) < 0.01 and 
                  color and color.lower() == "#ca5804" and 
                  len(block_text) < 100 and  # Spell names are short
                  not any(keyword in block_text.lower() for keyword in ["level", "spell"])):  # Not a level header
                logger.info(f"  Auto-detecting '{block_text}' as spell header (H3) based on font styling")
                block["__render_as_h3"] = True
                block["__header_text"] = block_text
                modifications += 1
    
    logger.info(f"Adjusted {modifications} spell headers")


def _get_block_text(block: dict) -> str:
    """Helper to extract text from a block."""
    text = ""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            text += span.get("text", "")
    return text.strip()


def _extract_find_familiar_table(section_data: dict) -> None:
    """Extract and format the Find Familiar table.
    
    The table has 3 columns: Die Roll, Familiar, Sensory Powers.
    Die Roll format is "#" or "#-#" (e.g., "1-3", "4-5", "6-8").
    """
    logger.info("Extracting Find Familiar table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    page = pages[0]
    blocks = page.get("blocks", [])
    
    # Find the "Find Familiar" header block (block 9)
    familiar_idx = None
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block)
            if text == "Find Familiar":
                familiar_idx = i
                logger.info(f"  Found 'Find Familiar' at block {i}")
                break
    
    if familiar_idx is None:
        logger.warning("  Could not find 'Find Familiar' header")
        return
    
    # Build table data from the PDF content (blocks 12-21)
    # Based on the actual PDF structure we examined
    table_data = {
        "rows": [
            {"cells": [{"text": "Die Roll"}, {"text": "Familiar"}, {"text": "Sensory Powers"}]},
            {"cells": [{"text": "1-3"}, {"text": "Bat"}, {"text": "Night, sonar-enhanced vision"}]},
            {"cells": [{"text": "4-5"}, {"text": "Beetle"}, {"text": "Senses minute vibrations"}]},
            {"cells": [{"text": "6-8"}, {"text": "Cat, black"}, {"text": "Excellent night vision and superior hearing"}]},
            {"cells": [{"text": "9"}, {"text": "Pseudodragon"}, {"text": "Normal sensory powers, but very intelligent"}]},
            {"cells": [{"text": "10-11"}, {"text": "Rat"}, {"text": "Excellent sense of taste and smell"}]},
            {"cells": [{"text": "12-15"}, {"text": "Scorpion"}, {"text": "Senses fear"}]},
            {"cells": [{"text": "16-20"}, {"text": "Snake"}, {"text": "Sensitivity to subtle temperature changes"}]},
        ],
        "header_rows": 1
    }
    
    # Mark the fragmented table data blocks (12-21) to skip rendering
    for i in range(familiar_idx + 3, min(familiar_idx + 13, len(blocks))):
        if i < len(blocks):
            block = blocks[i]
            text = _get_block_text(block)
            # Stop when we hit "Mount"
            if "Mount" in text and len(text) < 20:
                break
            # Skip blocks that contain table fragments
            # Include specific fragments like "Sensitivity to subtle tem-" and die roll patterns
            if any(keyword in text for keyword in ["Die Roll", "Bat", "Beetle", "Cat", "Pseudodragon", 
                                                    "Rat", "Scorpion", "Snake", "Sensory", "vibrations",
                                                    "vision", "hearing", "intelligent", "smell", "fear",
                                                    "Sensitivity", "subtle", "perature", "tem-", "16 -20"]):
                block["__skip_render"] = True
                logger.info(f"  Marked block {i} to skip (contains table fragment)")
    
    # Add the table to the page's tables list
    if "tables" not in page:
        page["tables"] = []
    
    # Position the table after the intro text
    intro_block = blocks[familiar_idx + 1] if familiar_idx + 1 < len(blocks) else blocks[familiar_idx]
    intro_bbox = intro_block.get("bbox", [0, 0, 600, 800])
    
    table = {
        "rows": table_data["rows"],
        "header_rows": table_data["header_rows"],
        "bbox": [intro_bbox[0], intro_bbox[3] + 5, intro_bbox[2], intro_bbox[3] + 150]
    }
    
    page["tables"].append(table)
    logger.info(f"  Inserted Find Familiar table with {len(table_data['rows'])} rows (including header)")


def _extract_mount_table(section_data: dict) -> None:
    """Extract and format the Mount table.
    
    The table has 2 columns: Caster Level, Mount.
    Caster Level format is "#-# level" (e.g., "1st-3rd level", "4th-7th level").
    """
    logger.info("Extracting Mount table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    page = pages[0]
    blocks = page.get("blocks", [])
    
    # Find the second "Mount" header (the one after Find Familiar, around block 22)
    mount_idx = None
    find_familiar_passed = False
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block)
            if text == "Find Familiar":
                find_familiar_passed = True
            if find_familiar_passed and text == "Mount":
                mount_idx = i
                logger.info(f"  Found 'Mount' table section at block {i}")
                break
    
    if mount_idx is None:
        logger.warning("  Could not find 'Mount' table section")
        return
    
    # Build table data from the PDF content (blocks 24-31)
    # Based on the actual PDF structure we examined
    table_data = {
        "rows": [
            {"cells": [{"text": "Caster Level"}, {"text": "Mount"}]},
            {"cells": [{"text": "1st-3rd level"}, {"text": "Wild Kank"}]},
            {"cells": [{"text": "4th-7th level"}, {"text": "Trained Kank"}]},
            {"cells": [{"text": "8th-12th level"}, {"text": "Inix"}]},
            {"cells": [{"text": "13th-14th level"}, {"text": "Mekillot (and howdah at 18th level)"}]},
            {"cells": [{"text": "15th level & up"}, {"text": "Roc (and saddle at 18th level)"}]},
        ],
        "header_rows": 1
    }
    
    # Mark the fragmented table data blocks (24-33) to skip rendering
    # Extend range to catch any stragglers after the table, including block 33 which is just "level)"
    for i in range(mount_idx + 2, min(mount_idx + 13, len(blocks))):
        if i < len(blocks):
            block = blocks[i]
            text = _get_block_text(block)
            # Skip blocks that contain table fragments
            # Include specific phrases to catch all Mount table fragments including trailing "level)"
            if any(keyword in text for keyword in ["Caster Level", "M o u n t", "Wild Kank", "Trained Kank", 
                                                    "Inix", "Mekillot", "Roc", "howdah", "saddle",
                                                    "1st-3rd", "4th-7th", "8th-12th", "13th-14th", "15th", "18th",
                                                    "level & up"]) or text.strip() == "level)":
                block["__skip_render"] = True
                logger.info(f"  Marked block {i} to skip (contains table fragment)")
    
    # Add the table to the page's tables list
    if "tables" not in page:
        page["tables"] = []
    
    # Position the table after the intro text
    intro_block = blocks[mount_idx + 1] if mount_idx + 1 < len(blocks) else blocks[mount_idx]
    intro_bbox = intro_block.get("bbox", [0, 0, 600, 800])
    
    table = {
        "rows": table_data["rows"],
        "header_rows": table_data["header_rows"],
        "bbox": [intro_bbox[0], intro_bbox[3] + 5, intro_bbox[2], intro_bbox[3] + 100]
    }
    
    page["tables"].append(table)
    logger.info(f"  Inserted Mount table with {len(table_data['rows'])} rows (including header)")


def _extract_reincarnation_table(section_data: dict) -> None:
    """Extract and format the Reincarnation table.
    
    The table has 2 columns: D100 Roll, Incarnation.
    D100 Roll format is "#-#" (e.g., "01-08", "90-96").
    Incarnation may contain hyphens and commas (e.g., "Giant-kin, Cyclops").
    The table spans two columns in the source PDF.
    The table ends before the "Transmute Water to Dust" spell.
    """
    logger.info("Extracting Reincarnation table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # Find page 95 which contains the Reincarnation spell
    page_95 = None
    for page in pages:
        if page["page_number"] == 95:
            page_95 = page
            break
    
    if page_95 is None:
        logger.warning("  Could not find page 95 for Reincarnation table")
        return
    
    blocks = page_95.get("blocks", [])
    
    # Find the "R e i n c a r n a t i o n" header block
    reincarnation_idx = None
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block)
            if "R e i n c a r n a t i o n" in text:
                reincarnation_idx = i
                logger.info(f"  Found 'Reincarnation' at block {i}")
                break
    
    if reincarnation_idx is None:
        logger.warning("  Could not find 'Reincarnation' header")
        return
    
    # Build table data from the PDF content
    # Based on the actual PDF structure we examined
    table_data = {
        "rows": [
            {"cells": [{"text": "D100 Roll"}, {"text": "Incarnation"}]},
            {"cells": [{"text": "01-08"}, {"text": "Aarakocra"}]},
            {"cells": [{"text": "09-16"}, {"text": "Belgoi"}]},
            {"cells": [{"text": "17-24"}, {"text": "Dwarf"}]},
            {"cells": [{"text": "25-32"}, {"text": "Elf"}]},
            {"cells": [{"text": "33-34"}, {"text": "Giant"}]},
            {"cells": [{"text": "35-37"}, {"text": "Giant-kin, Cyclops"}]},
            {"cells": [{"text": "38-48"}, {"text": "Half-elf"}]},
            {"cells": [{"text": "49-55"}, {"text": "Half-giant"}]},
            {"cells": [{"text": "56-66"}, {"text": "Halfling"}]},
            {"cells": [{"text": "67-78"}, {"text": "Human"}]},
            {"cells": [{"text": "79-85"}, {"text": "Kenku"}]},
            {"cells": [{"text": "86-89"}, {"text": "Mul"}]},
            {"cells": [{"text": "90-96"}, {"text": "Thri-kreen"}]},
            {"cells": [{"text": "97-00"}, {"text": "Yuan-ti"}]},
        ],
        "header_rows": 1
    }
    
    # Mark the fragmented table data blocks to skip rendering
    # Start from the block after the intro text (reincarnation_idx + 3)
    # and continue until we find "Transmute Water to Dust"
    for i in range(reincarnation_idx + 2, min(reincarnation_idx + 50, len(blocks))):
        if i < len(blocks):
            block = blocks[i]
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            
            # Stop when we hit "Transmute Water to Dust"
            if "Transmute Water to Dust" in text:
                logger.info(f"  Found end of table at block {i} (Transmute Water to Dust)")
                break
            
            # Skip blocks that contain table fragments
            # Include all the D100 rolls and incarnation values
            fragment_keywords = [
                "D100", "Roll", "Incarnation",
                "01-08", "09-16", "17-24", "25-32", "33-34", "35-37",
                "38-48", "49-55", "56-66", "67-78", "79-85", "86-89", "90-96", "97-00",
                "Aarakocra", "Belgoi", "Dwarf", "Elf", "Giant", "Cyclops",
                "Half-elf", "Half-giant", "Halfling", "Human", "Kenku",
                "M u l",  # Whitespace version
                "Thri-kreen", "Yuan-ti"
            ]
            
            if any(keyword in text for keyword in fragment_keywords):
                block["__skip_render"] = True
                logger.info(f"  Marked block {i} to skip (contains table fragment: {text[:50]}...)")
    
    # Add the table to the page's tables list
    if "tables" not in page_95:
        page_95["tables"] = []
    
    # Position the table after the intro text
    intro_block = blocks[reincarnation_idx + 2] if reincarnation_idx + 2 < len(blocks) else blocks[reincarnation_idx]
    intro_bbox = intro_block.get("bbox", [0, 0, 600, 800])
    
    table = {
        "rows": table_data["rows"],
        "header_rows": table_data["header_rows"],
        "bbox": [intro_bbox[0], intro_bbox[3] + 5, intro_bbox[2], intro_bbox[3] + 200]
    }
    
    page_95["tables"].append(table)
    logger.info(f"  Inserted Reincarnation table with {len(table_data['rows'])} rows (including header)")


def _extract_doom_legion_table(section_data: dict) -> None:
    """Extract and format the Doom Legion table.
    
    The table has 2 columns: Battle Type, Dice Roll.
    Dice Roll format is "#d#" (e.g., "3d12", "6d12", "10d20").
    The table has 3 data rows following the text "rolls dice to find how many undead are raised:".
    The table ends before "Animated bodies that are less than".
    """
    logger.info("Extracting Doom Legion table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # Find page 95 which contains the Doom Legion spell
    page_95 = None
    for page in pages:
        if page["page_number"] == 95:
            page_95 = page
            break
    
    if page_95 is None:
        logger.warning("  Could not find page 95 for Doom Legion table")
        return
    
    blocks = page_95.get("blocks", [])
    
    # Find the "find how many undead are raised:" text block
    table_intro_idx = None
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block)
            if "find how many undead are raised:" in text.lower():
                table_intro_idx = i
                logger.info(f"  Found table intro at block {i}")
                break
    
    if table_intro_idx is None:
        logger.warning("  Could not find Doom Legion table intro text")
        return
    
    # Build table data from the PDF content
    # Based on the actual PDF structure we examined
    table_data = {
        "rows": [
            {"cells": [{"text": "Battle Type"}, {"text": "Dice Roll"}]},
            {"cells": [{"text": "Skirmish"}, {"text": "3d12"}]},
            {"cells": [{"text": "Small Battle"}, {"text": "6d12"}]},
            {"cells": [{"text": "Major Battle"}, {"text": "10d20"}]},
        ],
        "header_rows": 1
    }
    
    # Mark the fragmented table data blocks to skip rendering
    # Start from the block after the intro text
    # and continue until we find "Animated bodies"
    for i in range(table_intro_idx + 1, min(table_intro_idx + 10, len(blocks))):
        if i < len(blocks):
            block = blocks[i]
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            
            # Stop when we hit "Animated bodies"
            if "Animated bodies" in text:
                logger.info(f"  Found end of table at block {i} (Animated bodies)")
                break
            
            # Skip blocks that contain table fragments
            fragment_keywords = [
                "S k i r m i s h", "3 d 12", "3d12",
                "Small Battle", "6d12",
                "Major Battle", "10d20",
                "find how many undead are raised"
            ]
            
            if any(keyword in text for keyword in fragment_keywords):
                block["__skip_render"] = True
                logger.info(f"  Marked block {i} to skip (contains table fragment: {text[:50]}...)")
    
    # Add the table to the page's tables list
    if "tables" not in page_95:
        page_95["tables"] = []
    
    # Position the table after the intro text
    intro_block = blocks[table_intro_idx + 1] if table_intro_idx + 1 < len(blocks) else blocks[table_intro_idx]
    intro_bbox = intro_block.get("bbox", [0, 0, 600, 800])
    
    table = {
        "rows": table_data["rows"],
        "header_rows": table_data["header_rows"],
        "bbox": [intro_bbox[0], intro_bbox[3] + 5, intro_bbox[2], intro_bbox[3] + 100]
    }
    
    page_95["tables"].append(table)
    logger.info(f"  Inserted Doom Legion table with {len(table_data['rows'])} rows (including header)")


def _extract_time_at_rest_table(section_data: dict) -> None:
    """Extract and format the Time at Rest table.
    
    The table has 2 columns: Time at Rest, Chance to Ignore.
    Time at Rest format is "# day", "# week", "# month/months", "# year/years", "Over 100 years".
    Chance to Ignore format is "# %" (e.g., "90%", "50%", "0%").
    The table has 10 data rows following the header.
    The table ends before "An army" paragraph.
    """
    logger.info("Extracting Time at Rest table")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # Find page 96 which contains the Time at Rest table
    page_96 = None
    for page in pages:
        if page["page_number"] == 96:
            page_96 = page
            break
    
    if page_96 is None:
        logger.warning("  Could not find page 96 for Time at Rest table")
        return
    
    blocks = page_96.get("blocks", [])
    
    # Find the "Time at RestChance to Ignore" header block
    table_header_idx = None
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block)
            if "time at rest" in text.lower() and "chance to ignore" in text.lower():
                table_header_idx = i
                logger.info(f"  Found table header at block {i}")
                break
    
    if table_header_idx is None:
        logger.warning("  Could not find Time at Rest table header")
        return
    
    # Build table data from the PDF content
    # Based on the actual PDF structure we examined
    table_data = {
        "rows": [
            {"cells": [{"text": "Time at Rest"}, {"text": "Chance to Ignore"}]},
            {"cells": [{"text": "1 day"}, {"text": "90%"}]},
            {"cells": [{"text": "1 week"}, {"text": "80%"}]},
            {"cells": [{"text": "1 month"}, {"text": "70%"}]},
            {"cells": [{"text": "3 months"}, {"text": "60%"}]},
            {"cells": [{"text": "1 year"}, {"text": "50%"}]},
            {"cells": [{"text": "5 years"}, {"text": "40%"}]},
            {"cells": [{"text": "10 years"}, {"text": "30%"}]},
            {"cells": [{"text": "50 years"}, {"text": "20%"}]},
            {"cells": [{"text": "100 years"}, {"text": "10%"}]},
            {"cells": [{"text": "Over 100 years"}, {"text": "0%"}]},
        ],
        "header_rows": 1
    }
    
    # Mark the fragmented table data blocks to skip rendering
    # Start from the header block and continue until we find "An army"
    for i in range(table_header_idx, min(table_header_idx + 15, len(blocks))):
        if i < len(blocks):
            block = blocks[i]
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            
            # Stop when we hit "An army"
            if "An army" in text:
                logger.info(f"  Found end of table at block {i} (An army)")
                break
            
            # Skip blocks that contain table fragments
            fragment_keywords = [
                "Time at Rest", "Chance to Ignore",
                "1 day", "9 0 %", "90%",
                "1 week", "8 0 %", "80%",
                "1 month", "7 0 %", "70%",
                "3 months", "6 0 %", "60%",
                "1 year", "5 0 %", "50%",
                "5 years", "4 0 %", "40%",
                "10 years", "3 0 %", "30%",
                "50 years", "2 0 %", "20%",
                "100 years", "1 0 %", "10%",
                "Over 100 years", "0 %", "0%"
            ]
            
            if any(keyword in text for keyword in fragment_keywords):
                block["__skip_render"] = True
                logger.info(f"  Marked block {i} to skip (contains table fragment: {text[:50]}...)")
    
    # Add the table to the page's tables list
    if "tables" not in page_96:
        page_96["tables"] = []
    
    # Position the table after the header block
    header_block = blocks[table_header_idx]
    header_bbox = header_block.get("bbox", [0, 0, 600, 800])
    
    table = {
        "rows": table_data["rows"],
        "header_rows": table_data["header_rows"],
        "bbox": [header_bbox[0], header_bbox[3] + 5, header_bbox[2], header_bbox[3] + 150]
    }
    
    page_96["tables"].append(table)
    logger.info(f"  Inserted Time at Rest table with {len(table_data['rows'])} rows (including header)")

