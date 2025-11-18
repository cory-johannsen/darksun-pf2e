"""
Chapter 6 (Money & Equipment) processing sub-package.

This package contains equipment table extraction and processing
functions for Chapter 6 of the Dark Sun rules.
"""

# Re-export common functions
from .common import (
    normalize_plain_text,
    clean_whitespace,
    adjust_header_sizes,
    split_service_header,
    split_shields_header,
    get_block_text,
    merge_studded_leather_header,
    merge_chain_splint_header,
    extract_table_cell_text,
    merge_armor_headers,
)

# Re-export weapon processing functions
from .weapons import (
    extract_weapon_materials_table,
    extract_new_weapons_table,
    suppress_duplicate_weapon_column_headers,
)

# Re-export armor processing functions
from .armor import extract_barding_table

# Re-export transport processing functions
from .transport import (
    extract_transport_table,
    extract_animals_table,
)

# Re-export equipment processing functions
from .equipment import (
    extract_household_provisions_table,
    extract_common_wages_table,
)

__all__ = [
    # Common utilities
    "normalize_plain_text",
    "clean_whitespace",
    "adjust_header_sizes",
    "split_service_header",
    "split_shields_header",
    "get_block_text",
    "merge_studded_leather_header",
    "merge_chain_splint_header",
    "extract_table_cell_text",
    "merge_armor_headers",
    # Weapons
    "extract_weapon_materials_table",
    "extract_new_weapons_table",
    "suppress_duplicate_weapon_column_headers",
    # Armor
    "extract_barding_table",
    # Transport
    "extract_transport_table",
    "extract_animals_table",
    # Equipment
    "extract_household_provisions_table",
    "extract_common_wages_table",
]

