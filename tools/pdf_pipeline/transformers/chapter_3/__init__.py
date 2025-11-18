"""
Chapter 3 (Player Character Classes) processing modules.

This package contains the refactored chapter 3 processing logic,
split into manageable class-specific modules.

Status: Partial extraction in progress
- ✅ common.py - Common utilities (9 functions)
- ⏸️ warrior.py - Fighter & Gladiator (pending)
- ⏸️ ranger.py - Ranger-specific (pending)
- ⏸️ wizard.py - Defiler & Preserver (pending)
- ⏸️ priest.py - Cleric, Druid, Templar (pending)
- ⏸️ rogue.py - Bard & Thief (pending)
- ⏸️ psionicist.py - Psionicist (pending)
- ⏸️ multiclass.py - Multiclass combinations (pending)
"""

# Re-export common functions for backwards compatibility
from .common import (
    normalize_plain_text,
    parse_class_ability_requirements,
    extract_class_ability_table,
    create_class_name_header_block,
    create_class_ability_table,
    extract_class_ability_requirements_table,
    update_block_bbox,
    find_block,
    force_warrior_classes_paragraph_breaks,
)

# Re-export warrior functions
from .warrior import (
    extract_fighters_followers_table,
    force_gladiator_paragraph_breaks,
    force_fighter_benefits_paragraph_breaks,
    force_fighter_paragraph_breaks,
)

# Re-export ranger functions
from .ranger import (
    fix_ranger_ability_requirements_table,
    force_ranger_paragraph_breaks,
    reconstruct_rangers_followers_table_inplace,
    extract_rangers_followers_table,
    extract_rangers_followers_table_from_pages,
    mark_ranger_description_blocks,
)

# Re-export wizard functions
from .wizard import (
    extract_defiler_experience_table,
    force_wizard_classes_paragraph_breaks,
    force_wizard_section_paragraph_breaks,
    force_defiler_paragraph_breaks,
    extract_defiler_experience_levels_table,
    force_preserver_paragraph_breaks,
)

# Re-export priest functions
from .priest import (
    extract_templar_spell_progression_table,
    force_priest_section_paragraph_breaks,
    force_spheres_of_magic_paragraph_breaks,
    force_cleric_paragraph_breaks,
    force_cleric_powers_paragraph_breaks,
    force_druid_paragraph_breaks,
    force_druid_granted_powers_paragraph_breaks,
    fix_templar_ability_table,
    force_templar_paragraph_breaks,
    force_priest_classes_paragraph_breaks,
)

# Re-export rogue functions
from .rogue import (
    extract_bard_poison_table,
    force_bard_poison_paragraph_breaks,
    force_thief_paragraph_breaks,
    extract_thieving_dexterity_adjustments_table,
    force_thief_abilities_paragraph_breaks,
    extract_thieving_racial_adjustments_table,
    force_bard_paragraph_breaks,
    force_rogue_classes_paragraph_breaks,
)

# Re-export psionicist functions
from .psionicist import (
    force_psionicist_paragraph_breaks,
    extract_inherent_potential_table,
    force_psionicist_class_paragraph_breaks,
)

# Re-export multiclass functions
from .multiclass import (
    extract_multiclass_combinations,
    force_multiclass_paragraph_breaks,
    force_level_advancement_paragraph_breaks,
    extract_experience_points_table,
)

__all__ = [
    # Common utilities (extracted)
    "normalize_plain_text",
    "parse_class_ability_requirements",
    "extract_class_ability_table",
    "create_class_name_header_block",
    "create_class_ability_table",
    "extract_class_ability_requirements_table",
    "update_block_bbox",
    "find_block",
    "force_warrior_classes_paragraph_breaks",
    # Warrior functions (extracted)
    "extract_fighters_followers_table",
    "force_gladiator_paragraph_breaks",
    "force_fighter_benefits_paragraph_breaks",
    "force_fighter_paragraph_breaks",
    # Ranger functions (extracted)
    "fix_ranger_ability_requirements_table",
    "force_ranger_paragraph_breaks",
    "reconstruct_rangers_followers_table_inplace",
    "extract_rangers_followers_table",
    "extract_rangers_followers_table_from_pages",
    "mark_ranger_description_blocks",
    # Wizard functions (extracted)
    "extract_defiler_experience_table",
    "force_wizard_classes_paragraph_breaks",
    "force_wizard_section_paragraph_breaks",
    "force_defiler_paragraph_breaks",
    "extract_defiler_experience_levels_table",
    "force_preserver_paragraph_breaks",
    # Priest functions (extracted)
    "extract_templar_spell_progression_table",
    "force_priest_section_paragraph_breaks",
    "force_spheres_of_magic_paragraph_breaks",
    "force_cleric_paragraph_breaks",
    "force_cleric_powers_paragraph_breaks",
    "force_druid_paragraph_breaks",
    "force_druid_granted_powers_paragraph_breaks",
    "fix_templar_ability_table",
    "force_templar_paragraph_breaks",
    "force_priest_classes_paragraph_breaks",
    # Rogue functions (extracted)
    "extract_bard_poison_table",
    "force_bard_poison_paragraph_breaks",
    "force_thief_paragraph_breaks",
    "extract_thieving_dexterity_adjustments_table",
    "force_thief_abilities_paragraph_breaks",
    "extract_thieving_racial_adjustments_table",
    "force_bard_paragraph_breaks",
    "force_rogue_classes_paragraph_breaks",
    # Psionicist functions (extracted)
    "force_psionicist_paragraph_breaks",
    "extract_inherent_potential_table",
    "force_psionicist_class_paragraph_breaks",
    # Multiclass functions (extracted)
    "extract_multiclass_combinations",
    "force_multiclass_paragraph_breaks",
    "force_level_advancement_paragraph_breaks",
    "extract_experience_points_table",
]

