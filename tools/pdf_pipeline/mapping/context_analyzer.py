"""Context analyzer for setting-specific rule conversions.

This module analyzes Dark Sun-specific context to inform appropriate
rule mappings and conversions.

Requirements:
- SWENG-1: Single Responsibility Principle
- PY-6: Console logs tracing execution
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Set up logging per PY-6
logger = logging.getLogger(__name__)


class SettingTheme(str, Enum):
    """Enumeration of Dark Sun setting themes."""

    SURVIVAL = "survival"
    SCARCITY = "scarcity"
    PSIONICS = "psionics"
    DEFILING_MAGIC = "defiling_magic"
    HARSH_ENVIRONMENT = "harsh_environment"
    CITY_STATES = "city_states"
    SLAVERY = "slavery"


class DarkSunContext(BaseModel):
    """Context information for Dark Sun setting.

    Used to inform rule conversion decisions based on setting themes.
    """

    themes: List[SettingTheme] = Field(
        default_factory=list, description="Active setting themes"
    )
    metal_scarcity: bool = Field(True, description="Metal is scarce")
    water_scarcity: bool = Field(True, description="Water is scarce")
    psionics_common: bool = Field(True, description="Psionics are common")
    defiling_magic: bool = Field(True, description="Defiling magic exists")
    harsh_environment: bool = Field(True, description="Environment is harsh")
    context_tags: List[str] = Field(
        default_factory=list, description="Additional context tags"
    )


class ContextAnalyzer:
    """Analyzes game context to inform rule conversions.

    Provides setting-specific guidance for converting rules in a way
    that preserves Dark Sun's unique flavor.
    """

    def __init__(self, setting_context: Optional[DarkSunContext] = None):
        """Initialize the context analyzer.

        Args:
            setting_context: Optional Dark Sun context, uses default if not provided
        """
        self.context = setting_context or self._create_default_context()
        logger.info("Initialized ContextAnalyzer for Dark Sun setting")

    def analyze_ability_conversion(
        self, adnd_ability: str, adnd_score: int
    ) -> Dict[str, Any]:
        """Analyze how to convert an ability score considering Dark Sun context.

        Args:
            adnd_ability: AD&D ability name
            adnd_score: AD&D ability score

        Returns:
            Analysis with conversion recommendations
        """
        logger.debug(f"Analyzing ability conversion: {adnd_ability} {adnd_score}")

        # Base conversion
        pf2e_modifier = self._score_to_modifier(adnd_score)

        analysis = {
            "adnd_ability": adnd_ability,
            "adnd_score": adnd_score,
            "pf2e_modifier": pf2e_modifier,
            "recommendations": [],
            "context_notes": [],
        }

        # Dark Sun specific considerations
        if adnd_ability == "CON" and self.context.harsh_environment:
            analysis["recommendations"].append(
                "Consider CON bonus due to harsh environment adaptation"
            )
            analysis["context_notes"].append(
                "Dark Sun natives have enhanced constitution from harsh environment"
            )

        if adnd_ability == "WIS" and self.context.psionics_common:
            analysis["recommendations"].append(
                "WIS affects psionic abilities in Dark Sun"
            )
            analysis["context_notes"].append(
                "Consider psionic potential when converting WIS-based abilities"
            )

        return analysis

    def analyze_spell_conversion(
        self, spell_name: str, spell_school: str
    ) -> Dict[str, Any]:
        """Analyze how to convert a spell considering Dark Sun context.

        Args:
            spell_name: Spell name
            spell_school: Spell school

        Returns:
            Analysis with conversion recommendations
        """
        logger.debug(f"Analyzing spell conversion: {spell_name} ({spell_school})")

        analysis = {
            "spell_name": spell_name,
            "spell_school": spell_school,
            "recommendations": [],
            "context_notes": [],
            "defiling_impact": False,
        }

        # Check for defiling magic considerations
        if self.context.defiling_magic:
            if spell_school in ["Evocation", "Transmutation", "Conjuration"]:
                analysis["defiling_impact"] = True
                analysis["recommendations"].append(
                    "Consider defiling/preserving magic distinction"
                )
                analysis["context_notes"].append(
                    "Powerful spells may have defiling consequences in Dark Sun"
                )

        # Water-related spells are rare/powerful
        if self.context.water_scarcity and any(
            water_term in spell_name.lower()
            for water_term in ["water", "rain", "moisture"]
        ):
            analysis["recommendations"].append(
                "Water-related spells should be rarer or more powerful"
            )
            analysis["context_notes"].append(
                "Water scarcity makes water magic extremely valuable"
            )

        return analysis

    def analyze_equipment_conversion(
        self, item_name: str, material: str
    ) -> Dict[str, Any]:
        """Analyze how to convert equipment considering Dark Sun context.

        Args:
            item_name: Item name
            material: Item material

        Returns:
            Analysis with conversion recommendations
        """
        logger.debug(f"Analyzing equipment conversion: {item_name} ({material})")

        analysis = {
            "item_name": item_name,
            "material": material,
            "recommendations": [],
            "context_notes": [],
            "substitute_material": None,
        }

        # Metal scarcity
        if self.context.metal_scarcity and material.lower() in [
            "iron",
            "steel",
            "metal",
        ]:
            analysis["recommendations"].append(
                "Substitute metal with bone, stone, or obsidian"
            )
            analysis["substitute_material"] = "bone or obsidian"
            analysis["context_notes"].append(
                "Metal is extremely rare in Dark Sun; most weapons are bone/stone"
            )

        return analysis

    def get_setting_modifiers(self, rule_category: str) -> Dict[str, Any]:
        """Get setting-specific modifiers for a rule category.

        Args:
            rule_category: Category of rule being converted

        Returns:
            Dictionary of setting modifiers
        """
        modifiers = {
            "survival_emphasis": SettingTheme.SURVIVAL in self.context.themes,
            "resource_scarcity": SettingTheme.SCARCITY in self.context.themes,
            "psionic_integration": SettingTheme.PSIONICS in self.context.themes,
        }

        logger.debug(f"Retrieved setting modifiers for {rule_category}")
        return modifiers

    def _create_default_context(self) -> DarkSunContext:
        """Create default Dark Sun context.

        Returns:
            Default Dark Sun context
        """
        return DarkSunContext(
            themes=[
                SettingTheme.SURVIVAL,
                SettingTheme.SCARCITY,
                SettingTheme.PSIONICS,
                SettingTheme.DEFILING_MAGIC,
                SettingTheme.HARSH_ENVIRONMENT,
            ],
            metal_scarcity=True,
            water_scarcity=True,
            psionics_common=True,
            defiling_magic=True,
            harsh_environment=True,
            context_tags=["desert", "post-apocalyptic", "survival"],
        )

    def _score_to_modifier(self, score: int) -> int:
        """Convert AD&D ability score to PF2E modifier.

        Args:
            score: AD&D ability score (3-25)

        Returns:
            PF2E ability modifier (-5 to +7)
        """
        # PF2E uses (score - 10) // 2
        # But we need to map from AD&D scores
        return (score - 10) // 2

