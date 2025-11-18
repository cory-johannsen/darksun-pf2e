"""Pydantic models for AD&D 2E rule structures.

This module defines the schema for representing AD&D 2E game rules in a structured format.
These models are used to extract, store, and query rules from AD&D 2E sourcebooks.

Requirements:
- PY-3: Pydantic MUST be used for data modeling and validation
- SWENG-2: Design by Contract with explicit preconditions and postconditions
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ADnDSourcebook(str, Enum):
    """Enumeration of AD&D 2E sourcebooks."""

    DMG_REVISED = "dmg_revised"
    DMG_ORIGINAL = "dmg_original"
    DMG_PREMIUM = "dmg_premium"
    PHB_REVISED = "phb_revised"
    PHB_ORIGINAL = "phb_original"
    PHB_PREMIUM = "phb_premium"
    DARK_SUN = "dark_sun"


class ADnDAbilityScore(BaseModel):
    """Represents an AD&D 2E ability score and its modifiers.

    Ability scores range from 3 to 25 in AD&D 2E, with different modifiers
    for each ability type (STR, DEX, CON, INT, WIS, CHA).
    """

    ability: str = Field(..., description="Ability name (STR, DEX, CON, INT, WIS, CHA)")
    score: int = Field(..., ge=3, le=25, description="Ability score value")
    modifiers: Dict[str, int] = Field(
        default_factory=dict, description="Ability-specific modifiers"
    )
    exceptional_strength: Optional[int] = Field(
        None, ge=1, le=100, description="Exceptional strength percentile (18/01-18/00)"
    )
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")

    @field_validator("ability")
    @classmethod
    def validate_ability(cls, v: str) -> str:
        """Validate ability name."""
        valid_abilities = {"STR", "DEX", "CON", "INT", "WIS", "CHA"}
        if v.upper() not in valid_abilities:
            raise ValueError(f"Invalid ability: {v}. Must be one of {valid_abilities}")
        return v.upper()


class ADnDSavingThrow(BaseModel):
    """Represents an AD&D 2E saving throw table entry.

    AD&D 2E uses five saving throw categories that vary by class and level.
    """

    class_name: str = Field(..., description="Character class name")
    level: int = Field(..., ge=1, le=20, description="Character level")
    paralyzation_poison_death: int = Field(..., description="Save vs. paralyzation, poison, death magic")
    rod_staff_wand: int = Field(..., description="Save vs. rod, staff, wand")
    petrification_polymorph: int = Field(..., description="Save vs. petrification, polymorph")
    breath_weapon: int = Field(..., description="Save vs. breath weapon")
    spell: int = Field(..., description="Save vs. spell")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDTHAC0(BaseModel):
    """Represents an AD&D 2E THAC0 (To Hit Armor Class 0) progression.

    THAC0 represents the attack roll needed to hit AC 0, decreasing as characters level.
    """

    class_name: str = Field(..., description="Character class name")
    level: int = Field(..., ge=1, le=20, description="Character level")
    thac0: int = Field(..., ge=1, le=20, description="THAC0 value")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDArmorClass(BaseModel):
    """Represents an AD&D 2E armor class entry.

    AD&D 2E uses descending AC where lower numbers are better (10 = unarmored, -10 = best).
    """

    armor_type: str = Field(..., description="Type of armor")
    base_ac: int = Field(..., ge=-10, le=10, description="Base armor class")
    dex_modifier_applies: bool = Field(True, description="Whether DEX modifier applies")
    weight: Optional[float] = Field(None, description="Weight in pounds")
    cost: Optional[str] = Field(None, description="Cost in gold pieces")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDSpellSlot(BaseModel):
    """Represents spell slots available at a given level."""

    level: int = Field(..., ge=1, le=20, description="Character level")
    spell_level: int = Field(..., ge=1, le=9, description="Spell level")
    slots: int = Field(..., ge=0, description="Number of spell slots")


class ADnDSpell(BaseModel):
    """Represents an AD&D 2E spell.

    AD&D 2E spells have level, school, components, range, duration, and effects.
    """

    name: str = Field(..., description="Spell name")
    spell_level: int = Field(..., ge=1, le=9, description="Spell level")
    school: str = Field(..., description="School of magic")
    sphere: Optional[str] = Field(None, description="Priest spell sphere")
    components: List[str] = Field(..., description="Spell components (V, S, M)")
    casting_time: str = Field(..., description="Casting time")
    range: str = Field(..., description="Spell range")
    duration: str = Field(..., description="Spell duration")
    area_of_effect: str = Field(..., description="Area of effect")
    saving_throw: str = Field(..., description="Saving throw details")
    description: str = Field(..., description="Spell description")
    reversible: bool = Field(False, description="Whether spell is reversible")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDProficiency(BaseModel):
    """Represents an AD&D 2E weapon or non-weapon proficiency.

    AD&D 2E uses proficiency slots that grant bonuses or allow skill use.
    """

    name: str = Field(..., description="Proficiency name")
    proficiency_type: str = Field(..., description="Type (weapon, non-weapon)")
    slots_required: int = Field(..., ge=1, description="Number of slots required")
    relevant_ability: Optional[str] = Field(None, description="Relevant ability score")
    check_modifier: Optional[int] = Field(None, description="Check modifier")
    description: str = Field(..., description="Proficiency description")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDClass(BaseModel):
    """Represents an AD&D 2E character class.

    Contains all class-specific rules, requirements, and progression.
    """

    name: str = Field(..., description="Class name")
    class_group: str = Field(..., description="Class group (Warrior, Wizard, Priest, Rogue)")
    prime_requisite: List[str] = Field(..., description="Prime requisite abilities")
    minimum_abilities: Dict[str, int] = Field(..., description="Minimum ability requirements")
    hit_die: str = Field(..., description="Hit die (e.g., d10, d6)")
    allowed_alignments: List[str] = Field(..., description="Allowed alignments")
    allowed_weapons: List[str] = Field(..., description="Allowed weapons")
    allowed_armor: List[str] = Field(..., description="Allowed armor types")
    thac0_progression: List[ADnDTHAC0] = Field(
        default_factory=list, description="THAC0 progression by level"
    )
    saving_throws: List[ADnDSavingThrow] = Field(
        default_factory=list, description="Saving throw progression by level"
    )
    spell_progression: Optional[List[ADnDSpellSlot]] = Field(
        None, description="Spell progression for spellcasters"
    )
    special_abilities: List[str] = Field(
        default_factory=list, description="Class special abilities"
    )
    experience_table: Dict[int, int] = Field(
        default_factory=dict, description="Experience points required per level"
    )
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDCombatMechanic(BaseModel):
    """Represents an AD&D 2E combat mechanic or rule.

    Covers initiative, attack modifiers, damage, special attacks, etc.
    """

    name: str = Field(..., description="Mechanic name")
    category: str = Field(..., description="Category (initiative, attack, damage, special)")
    description: str = Field(..., description="Mechanic description")
    modifiers: Dict[str, int] = Field(
        default_factory=dict, description="Situational modifiers"
    )
    conditions: List[str] = Field(
        default_factory=list, description="Conditions when this mechanic applies"
    )
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")


class ADnDRule(BaseModel):
    """Generic container for any AD&D 2E rule.

    Used for rules that don't fit other specific schemas.
    """

    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    category: str = Field(..., description="Rule category")
    description: str = Field(..., description="Full rule description")
    tables: Optional[List[Dict]] = Field(None, description="Associated tables")
    examples: Optional[List[str]] = Field(None, description="Rule examples")
    source: ADnDSourcebook = Field(..., description="Source sourcebook")
    page_reference: Optional[str] = Field(None, description="Page reference in source")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")

