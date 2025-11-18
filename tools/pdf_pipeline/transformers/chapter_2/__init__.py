"""
Chapter 2 (Player Character Races) processing sub-package.

This package contains race-specific processing logic and table extraction
functions for Chapter 2 of the Dark Sun rules.
"""

# Re-export common functions for backwards compatibility
from .common import (
    update_block_bbox,
    find_block,
)

# Re-export table processing functions
from .tables import (
    process_table_2_ability_adjustments,
    process_racial_ability_requirements_table,
    process_table_3_racial_class_limits,
    process_other_languages_table,
)

# Re-export physical tables functions
from .physical_tables import (
    process_height_weight_table,
    process_starting_age_table,
)

# Re-export race-specific functions
from .dwarves import fix_dwarves_section_text_ordering
from .elves import fix_elves_section_paragraph_breaks, fix_elves_roleplaying_paragraph_breaks
from .half_elves import fix_half_elves_section_paragraph_breaks, fix_half_elves_roleplaying_paragraph_breaks
from .humans import force_human_paragraph_breaks
from .mul import process_mul_exertion_table, force_mul_paragraph_breaks, force_mul_roleplaying_paragraph_breaks
from .thri_kreen import force_thri_kreen_paragraph_breaks, force_thri_kreen_roleplaying_paragraph_breaks

__all__ = [
    # Common utilities
    "update_block_bbox",
    "find_block",
    # Table processing
    "process_table_2_ability_adjustments",
    "process_racial_ability_requirements_table",
    "process_table_3_racial_class_limits",
    "process_other_languages_table",
    # Physical tables
    "process_height_weight_table",
    "process_starting_age_table",
    # Dwarves
    "fix_dwarves_section_text_ordering",
    # Elves
    "fix_elves_section_paragraph_breaks",
    "fix_elves_roleplaying_paragraph_breaks",
    # Half-elves
    "fix_half_elves_section_paragraph_breaks",
    "fix_half_elves_roleplaying_paragraph_breaks",
    # Humans
    "force_human_paragraph_breaks",
    # Mul
    "process_mul_exertion_table",
    "force_mul_paragraph_breaks",
    "force_mul_roleplaying_paragraph_breaks",
    # Thri-kreen
    "force_thri_kreen_paragraph_breaks",
    "force_thri_kreen_roleplaying_paragraph_breaks",
]

