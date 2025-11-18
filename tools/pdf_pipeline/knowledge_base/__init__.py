"""Knowledge base system for AD&D 2E to PF2E rules conversion.

This module provides the infrastructure for extracting, storing, and querying
game rules from both AD&D 2E and Pathfinder 2E systems.
"""

from .adnd_schema import (
    ADnDAbilityScore,
    ADnDArmorClass,
    ADnDClass,
    ADnDCombatMechanic,
    ADnDProficiency,
    ADnDSavingThrow,
    ADnDSpell,
    ADnDTHAC0,
)
from .knowledge_repository import KnowledgeRepository, RuleCategory
from .pf2e_schema import (
    PF2EAbilityScore,
    PF2EAction,
    PF2EClass,
    PF2EFeat,
    PF2ESave,
    PF2ESkill,
    PF2ESpell,
    PF2ETrait,
)

__all__ = [
    # AD&D 2E Schemas
    "ADnDAbilityScore",
    "ADnDArmorClass",
    "ADnDClass",
    "ADnDCombatMechanic",
    "ADnDProficiency",
    "ADnDSavingThrow",
    "ADnDSpell",
    "ADnDTHAC0",
    # PF2E Schemas
    "PF2EAbilityScore",
    "PF2EAction",
    "PF2EClass",
    "PF2EFeat",
    "PF2ESave",
    "PF2ESkill",
    "PF2ESpell",
    "PF2ETrait",
    # Repository
    "KnowledgeRepository",
    "RuleCategory",
]

