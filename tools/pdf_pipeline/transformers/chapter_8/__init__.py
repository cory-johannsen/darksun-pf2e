"""
Chapter 8 (Experience) processing sub-package.

This package contains experience award table extraction and formatting
functions for Chapter 8 of the Dark Sun rules.
"""

# Re-export common functions
from .common import (
    normalize_plain_text,
    update_block_bbox,
    is_class_award_header,
    is_race_award_header,
    is_column_header,
    is_xp_value,
    clean_xp_text,
)

# Re-export table processing functions
from .tables import (
    extract_tables_from_page,
    pair_table_columns,
    insert_tables_into_blocks,
    extract_race_tables_from_page,
    insert_race_tables_into_blocks,
)

# Re-export award-specific functions
from .class_awards import extract_class_award_tables
from .race_awards import extract_race_award_tables

# Re-export formatting functions
from .formatting import (
    set_header_sizes,
    mark_race_description_headers,
    mark_trust_test_sections,
    collect_list_items_after_header,
    collect_full_list_item_text,
    mark_class_description_paragraph_breaks,
    mark_race_description_paragraph_breaks,
)

__all__ = [
    # Common utilities
    "normalize_plain_text",
    "update_block_bbox",
    "is_class_award_header",
    "is_race_award_header",
    "is_column_header",
    "is_xp_value",
    "clean_xp_text",
    # Table processing
    "extract_tables_from_page",
    "pair_table_columns",
    "insert_tables_into_blocks",
    "extract_race_tables_from_page",
    "insert_race_tables_into_blocks",
    # Awards
    "extract_class_award_tables",
    "extract_race_award_tables",
    # Formatting
    "set_header_sizes",
    "mark_race_description_headers",
    "mark_trust_test_sections",
    "collect_list_items_after_header",
    "collect_full_list_item_text",
    "mark_class_description_paragraph_breaks",
    "mark_race_description_paragraph_breaks",
]

