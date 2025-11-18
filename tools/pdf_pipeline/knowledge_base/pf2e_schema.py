"""Pydantic models for Pathfinder 2E rule structures.

This module defines the schema for representing PF2E game rules in a structured format.
These models are used to cache and query rules from the PF2E MCP server.

Requirements:
- PY-3: Pydantic MUST be used for data modeling and validation
- SWENG-2: Design by Contract with explicit preconditions and postconditions
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PF2EActionType(str, Enum):
    """Enumeration of PF2E action types."""

    FREE = "free"
    REACTION = "reaction"
    ONE_ACTION = "1"
    TWO_ACTIONS = "2"
    THREE_ACTIONS = "3"
    ACTIVITY = "activity"


class PF2EAbilityScore(BaseModel):
    """Represents a Pathfinder 2E ability score and its modifiers.

    PF2E uses ability modifiers from -5 to +7 with scores from 1 to 24+.
    """

    ability: str = Field(..., description="Ability name (STR, DEX, CON, INT, WIS, CHA)")
    modifier: int = Field(..., ge=-5, le=10, description="Ability modifier")
    description: str = Field(..., description="Ability description")
    source: str = Field(..., description="Source book or MCP reference")


class PF2ESave(BaseModel):
    """Represents a Pathfinder 2E saving throw.

    PF2E uses three saves: Fortitude, Reflex, and Will.
    """

    save_type: str = Field(..., description="Save type (Fortitude, Reflex, Will)")
    ability: str = Field(..., description="Key ability for this save")
    description: str = Field(..., description="Save description")
    critical_success: Optional[str] = Field(None, description="Critical success effect")
    success: Optional[str] = Field(None, description="Success effect")
    failure: Optional[str] = Field(None, description="Failure effect")
    critical_failure: Optional[str] = Field(None, description="Critical failure effect")
    source: str = Field(..., description="Source book or MCP reference")


class PF2ESkill(BaseModel):
    """Represents a Pathfinder 2E skill.

    PF2E uses proficiency ranks (Untrained, Trained, Expert, Master, Legendary).
    """

    name: str = Field(..., description="Skill name")
    ability: str = Field(..., description="Key ability for this skill")
    description: str = Field(..., description="Skill description")
    untrained_actions: List[str] = Field(
        default_factory=list, description="Actions available when untrained"
    )
    trained_actions: List[str] = Field(
        default_factory=list, description="Actions requiring trained proficiency"
    )
    source: str = Field(..., description="Source book or MCP reference")


class PF2ETrait(BaseModel):
    """Represents a Pathfinder 2E trait.

    Traits are keywords that convey mechanical or thematic information.
    """

    name: str = Field(..., description="Trait name")
    description: str = Field(..., description="Trait description")
    category: Optional[str] = Field(None, description="Trait category")
    source: str = Field(..., description="Source book or MCP reference")


class PF2EAction(BaseModel):
    """Represents a Pathfinder 2E action.

    Actions are the fundamental unit of gameplay in PF2E.
    """

    name: str = Field(..., description="Action name")
    action_cost: PF2EActionType = Field(..., description="Action cost")
    traits: List[str] = Field(default_factory=list, description="Action traits")
    trigger: Optional[str] = Field(None, description="Action trigger")
    requirements: Optional[str] = Field(None, description="Action requirements")
    description: str = Field(..., description="Action description")
    critical_success: Optional[str] = Field(None, description="Critical success effect")
    success: Optional[str] = Field(None, description="Success effect")
    failure: Optional[str] = Field(None, description="Failure effect")
    critical_failure: Optional[str] = Field(None, description="Critical failure effect")
    source: str = Field(..., description="Source book or MCP reference")


class PF2EFeat(BaseModel):
    """Represents a Pathfinder 2E feat.

    Feats are character options that grant special abilities.
    """

    name: str = Field(..., description="Feat name")
    level: int = Field(..., ge=1, description="Feat level")
    traits: List[str] = Field(default_factory=list, description="Feat traits")
    prerequisites: List[str] = Field(default_factory=list, description="Feat prerequisites")
    action_cost: Optional[PF2EActionType] = Field(None, description="Action cost if applicable")
    trigger: Optional[str] = Field(None, description="Trigger if applicable")
    requirements: Optional[str] = Field(None, description="Requirements if applicable")
    description: str = Field(..., description="Feat description")
    special: Optional[str] = Field(None, description="Special notes")
    source: str = Field(..., description="Source book or MCP reference")


class PF2ESpell(BaseModel):
    """Represents a Pathfinder 2E spell.

    PF2E spells have ranks (1-10), traditions, traits, and actions.
    """

    name: str = Field(..., description="Spell name")
    rank: int = Field(..., ge=1, le=10, description="Spell rank (level)")
    traditions: List[str] = Field(..., description="Spell traditions (arcane, divine, occult, primal)")
    traits: List[str] = Field(default_factory=list, description="Spell traits")
    action_cost: Optional[PF2EActionType] = Field(None, description="Casting time")
    components: List[str] = Field(default_factory=list, description="Spell components")
    range: Optional[str] = Field(None, description="Spell range")
    area: Optional[str] = Field(None, description="Area of effect")
    targets: Optional[str] = Field(None, description="Valid targets")
    duration: Optional[str] = Field(None, description="Spell duration")
    saving_throw: Optional[str] = Field(None, description="Saving throw")
    description: str = Field(..., description="Spell description")
    heightened: Optional[Dict[str, str]] = Field(
        None, description="Heightened effects by level"
    )
    source: str = Field(..., description="Source book or MCP reference")


class PF2EClass(BaseModel):
    """Represents a Pathfinder 2E character class.

    Contains class features, proficiencies, and progression.
    """

    name: str = Field(..., description="Class name")
    key_ability: List[str] = Field(..., description="Key ability choices")
    hit_points: int = Field(..., ge=6, le=12, description="HP per level")
    initial_proficiencies: Dict[str, str] = Field(
        ..., description="Starting proficiency ranks"
    )
    class_features: Dict[int, List[str]] = Field(
        ..., description="Class features by level"
    )
    class_dc: str = Field(..., description="Key ability for class DC")
    perception: str = Field(..., description="Perception proficiency")
    saving_throws: Dict[str, str] = Field(..., description="Save proficiencies")
    skills: Dict[str, int] = Field(..., description="Number of skill choices")
    attacks: Dict[str, str] = Field(..., description="Attack proficiencies")
    defenses: Dict[str, str] = Field(..., description="Defense proficiencies")
    spellcasting: Optional[Dict[str, str]] = Field(
        None, description="Spellcasting details if applicable"
    )
    description: str = Field(..., description="Class description")
    source: str = Field(..., description="Source book or MCP reference")


class PF2ERule(BaseModel):
    """Generic container for any PF2E rule.

    Used for rules that don't fit other specific schemas.
    """

    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    category: str = Field(..., description="Rule category")
    description: str = Field(..., description="Full rule description")
    traits: List[str] = Field(default_factory=list, description="Associated traits")
    examples: Optional[List[str]] = Field(None, description="Rule examples")
    source: str = Field(..., description="Source book or MCP reference")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")


class PF2ECachedQuery(BaseModel):
    """Represents a cached MCP query result.

    Used to store PF2E rule lookups locally to reduce MCP calls.
    """

    query: str = Field(..., description="Original query string")
    category: str = Field(..., description="Query category")
    results: List[Dict] = Field(..., description="Query results from MCP")
    timestamp: str = Field(..., description="ISO timestamp of query")
    source: str = Field(..., description="MCP server identifier")

