"""
Chapter 8 Processing - Experience Tables

This module extracts and formats the 15 Individual Class Awards tables in Chapter 8.
Each table has 2 columns (Action, Awards) with various XP formats.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

# Import extracted functions from chapter_8 sub-modules
from .chapter_8.common import (
    normalize_plain_text as _normalize_plain_text,
    update_block_bbox as _update_block_bbox,
    is_class_award_header as _is_class_award_header,
    is_race_award_header as _is_race_award_header,
    is_column_header as _is_column_header,
    is_xp_value as _is_xp_value,
    clean_xp_text as _clean_xp_text,
)
from .chapter_8.tables import (
    extract_tables_from_page as _extract_tables_from_page,
    pair_table_columns as _pair_table_columns,
    insert_tables_into_blocks as _insert_tables_into_blocks,
    extract_race_tables_from_page as _extract_race_tables_from_page,
    insert_race_tables_into_blocks as _insert_race_tables_into_blocks,
)
from .chapter_8.class_awards import extract_class_award_tables as _extract_class_award_tables
from .chapter_8.race_awards import extract_race_award_tables as _extract_race_award_tables
from .chapter_8.formatting import (
    set_header_sizes as _set_header_sizes,
    mark_race_description_headers as _mark_race_description_headers,
    mark_trust_test_sections as _mark_trust_test_sections,
    collect_list_items_after_header as _collect_list_items_after_header,
    collect_full_list_item_text as _collect_full_list_item_text,
    mark_class_description_paragraph_breaks as _mark_class_description_paragraph_breaks,
    mark_race_description_paragraph_breaks as _mark_race_description_paragraph_breaks,
)

logger = logging.getLogger(__name__)

# Define the 15 class award table names that should be H2 headers
CLASS_AWARD_HEADERS = [
    "All Warriors:",
    "Fighter:",
    "Gladiator:",
    "Ranger:",
    "All Wizards:",
    "Preserver:",
    "Defiler:",
    "All Priests:",
    "Cleric:",
    "Druid:",
    "Templar:",
    "All Rogues:",
    "Thief:",
    "Bard:",
    "Psionicist:",
]

# Define the 7 race award table names that should be H2 headers
RACE_AWARD_HEADERS = [
    "Dwarf:",
    "Elf:",
    "Half-elf:",
    "Half-giant:",  # Note: lowercase 'g' to match PDF
    "Halfling:",
    "M u l :",  # Note: spaces between letters in PDF
    "Thri-kreen:",
]


# _is_class_award_header - MOVED to chapter_8/common.py


# _is_race_award_header - MOVED to chapter_8/common.py


# _is_column_header - MOVED to chapter_8/common.py


# _is_xp_value - MOVED to chapter_8/common.py


# _clean_xp_text - MOVED to chapter_8/common.py


# _extract_class_award_tables - MOVED to chapter_8/class_awards.py

# _extract_tables_from_page - MOVED to chapter_8/tables.py


# _pair_table_columns - MOVED to chapter_8/tables.py


# _insert_tables_into_blocks - MOVED to chapter_8/tables.py


# _extract_race_award_tables - MOVED to chapter_8/race_awards.py

# _extract_race_tables_from_page - MOVED to chapter_8/tables.py


# _insert_race_tables_into_blocks - MOVED to chapter_8/tables.py


# _set_header_sizes - MOVED to chapter_8/formatting.py


# _mark_race_description_headers - MOVED to chapter_8/formatting.py


# _mark_trust_test_sections - MOVED to chapter_8/formatting.py


# _collect_list_items_after_header - MOVED to chapter_8/formatting.py


# _collect_full_list_item_text - MOVED to chapter_8/formatting.py

# _normalize_plain_text - MOVED to chapter_8/common.py


# _update_block_bbox - MOVED to chapter_8/common.py


# _mark_class_description_paragraph_breaks - MOVED to chapter_8/formatting.py


# _mark_race_description_paragraph_breaks - MOVED to chapter_8/formatting.py


def apply_chapter_8_adjustments(section_data: dict) -> None:
    """
    Apply all Chapter 8 specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    logger.info("Applying Chapter 8 adjustments")
    
    # Extract and structure the Individual Class Awards tables
    _extract_class_award_tables(section_data)
    
    # Extract and structure the Individual Race Awards tables
    _extract_race_award_tables(section_data)
    
    # Set header sizes for class and race names
    _set_header_sizes(section_data)
    
    # Mark race description headers as H2
    _mark_race_description_headers(section_data)
    
    # Mark trust test sections as H3 with lists
    _mark_trust_test_sections(section_data)
    
    # Mark paragraph breaks in class descriptions
    _mark_class_description_paragraph_breaks(section_data)
    
    # Mark paragraph breaks in race descriptions
    _mark_race_description_paragraph_breaks(section_data)
    
    logger.info("Chapter 8 adjustments complete")

