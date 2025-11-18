"""Rule translators for specific game mechanics.

This module provides specialized translators for different types of game rules,
converting from AD&D 2E to PF2E while preserving flavor and context.

Requirements:
- SWENG-1: Single Responsibility Principle
- PY-4: ABC for interface definition
- PY-6: Console logs tracing execution
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, List

from .semantic_mapper import MappingConfidence, MappingResult

if TYPE_CHECKING:
    from ..knowledge_base.pf2e_client import PF2EMCPClient
    from .context_analyzer import ContextAnalyzer

# Set up logging per PY-6
logger = logging.getLogger(__name__)


class RuleTranslator(ABC):
    """Abstract base class for rule translators.

    All concrete translators must inherit from this class and implement
    the translate() method.
    """

    def __init__(self, context_analyzer: ContextAnalyzer):
        """Initialize the translator.

        Args:
            context_analyzer: Context analyzer for setting-specific guidance
        """
        self.context_analyzer = context_analyzer

    @abstractmethod
    def translate(
        self, adnd_rule: Any, pf2e_client: PF2EMCPClient
    ) -> MappingResult:
        """Translate an AD&D rule to PF2E equivalent.

        Args:
            adnd_rule: AD&D rule to translate
            pf2e_client: PF2E client for querying target rules

        Returns:
            Mapping result with conversion
        """
        pass

    def _calculate_confidence(
        self, conversion: Dict[str, Any], recommendations: List[str]
    ) -> MappingConfidence:
        """Calculate confidence level for a conversion.

        Args:
            conversion: Conversion data
            recommendations: List of recommendations

        Returns:
            Confidence level
        """
        # Simple heuristic: fewer recommendations = higher confidence
        if not recommendations:
            return MappingConfidence.HIGH
        elif len(recommendations) <= 2:
            return MappingConfidence.MEDIUM
        else:
            return MappingConfidence.LOW


class AbilityScoreTranslator(RuleTranslator):
    """Translator for ability score rules."""

    def translate(
        self, adnd_rule: Any, pf2e_client: PF2EMCPClient
    ) -> MappingResult:
        """Translate an AD&D ability score to PF2E.

        Args:
            adnd_rule: AD&D ability score rule
            pf2e_client: PF2E client

        Returns:
            Mapping result
        """
        logger.debug(f"Translating ability score: {adnd_rule.ability}")

        # Get PF2E ability scores for reference
        pf2e_abilities = pf2e_client.query_ability_scores()

        # Analyze with context
        analysis = self.context_analyzer.analyze_ability_conversion(
            adnd_rule.ability, adnd_rule.score
        )

        # Create conversion
        conversion = {
            "ability": adnd_rule.ability,
            "pf2e_modifier": analysis["pf2e_modifier"],
            "original_score": adnd_rule.score,
            "conversion_method": "score_to_modifier",
        }

        result = MappingResult(
            adnd_rule_id=f"{adnd_rule.ability}_{adnd_rule.score}",
            confidence=self._calculate_confidence(
                conversion, analysis["recommendations"]
            ),
            conversion=conversion,
            recommendations=analysis["recommendations"],
            context_notes=analysis["context_notes"],
            metadata={"category": "ability_scores"},
        )

        logger.info(
            f"Translated {adnd_rule.ability} {adnd_rule.score} → modifier {analysis['pf2e_modifier']}"
        )
        return result


class CombatMechanicTranslator(RuleTranslator):
    """Translator for combat mechanics."""

    def translate(
        self, adnd_rule: Any, pf2e_client: PF2EMCPClient
    ) -> MappingResult:
        """Translate an AD&D combat mechanic to PF2E.

        Args:
            adnd_rule: AD&D combat mechanic rule
            pf2e_client: PF2E client

        Returns:
            Mapping result
        """
        logger.debug(f"Translating combat mechanic: {getattr(adnd_rule, 'name', 'unknown')}")

        recommendations = []
        context_notes = []

        # THAC0 conversion
        if hasattr(adnd_rule, "thac0"):
            conversion = self._convert_thac0(adnd_rule)
            recommendations.append(
                "THAC0 converted to PF2E attack bonus - verify against class progression"
            )
        # AC conversion
        elif hasattr(adnd_rule, "base_ac"):
            conversion = self._convert_armor_class(adnd_rule)
            recommendations.append(
                "AC converted from descending to ascending - verify modifiers"
            )
        # Generic combat mechanic
        else:
            conversion = {"mechanic": "generic", "requires_manual_review": True}
            recommendations.append("Combat mechanic requires manual conversion")

        result = MappingResult(
            adnd_rule_id=getattr(adnd_rule, "name", "unknown"),
            confidence=self._calculate_confidence(conversion, recommendations),
            conversion=conversion,
            recommendations=recommendations,
            context_notes=context_notes,
            metadata={"category": "combat"},
        )

        logger.info(f"Translated combat mechanic: {result.adnd_rule_id}")
        return result

    def _convert_thac0(self, adnd_rule: Any) -> Dict[str, Any]:
        """Convert THAC0 to PF2E attack bonus.

        Args:
            adnd_rule: AD&D THAC0 rule

        Returns:
            Conversion data
        """
        # PF2E attack bonus ≈ (20 - THAC0)
        # This is a simplified conversion
        thac0 = adnd_rule.thac0
        attack_bonus = 20 - thac0

        return {
            "adnd_thac0": thac0,
            "pf2e_attack_bonus": attack_bonus,
            "level": adnd_rule.level,
            "conversion_method": "thac0_to_attack_bonus",
        }

    def _convert_armor_class(self, adnd_rule: Any) -> Dict[str, Any]:
        """Convert AD&D AC to PF2E AC.

        Args:
            adnd_rule: AD&D armor class rule

        Returns:
            Conversion data
        """
        # PF2E AC ≈ 20 - AD&D AC (descending to ascending)
        adnd_ac = adnd_rule.base_ac
        pf2e_ac = 20 - adnd_ac

        return {
            "adnd_ac": adnd_ac,
            "pf2e_ac": pf2e_ac,
            "armor_type": adnd_rule.armor_type,
            "conversion_method": "descending_to_ascending",
        }


class SpellTranslator(RuleTranslator):
    """Translator for spell rules."""

    def translate(
        self, adnd_rule: Any, pf2e_client: PF2EMCPClient
    ) -> MappingResult:
        """Translate an AD&D spell to PF2E.

        Args:
            adnd_rule: AD&D spell rule
            pf2e_client: PF2E client

        Returns:
            Mapping result
        """
        logger.debug(f"Translating spell: {adnd_rule.name}")

        # Analyze with context
        analysis = self.context_analyzer.analyze_spell_conversion(
            adnd_rule.name, adnd_rule.school
        )

        # Query similar PF2E spells
        pf2e_spells = pf2e_client.query_spells(
            adnd_rule.name, rank=adnd_rule.spell_level
        )

        # Create conversion
        conversion = {
            "name": adnd_rule.name,
            "adnd_level": adnd_rule.spell_level,
            "pf2e_rank": adnd_rule.spell_level,  # Usually 1:1 for levels 1-9
            "school": adnd_rule.school,
            "description": adnd_rule.description,
            "similar_pf2e_spells": [s.name for s in pf2e_spells] if pf2e_spells else [],
        }

        # Add Dark Sun specific notes
        if analysis["defiling_impact"]:
            conversion["dark_sun_notes"] = "May have defiling consequences"

        result = MappingResult(
            adnd_rule_id=adnd_rule.name,
            confidence=self._calculate_confidence(
                conversion, analysis["recommendations"]
            ),
            conversion=conversion,
            recommendations=analysis["recommendations"],
            context_notes=analysis["context_notes"],
            fallback_strategy="preserve_flavor_text" if not pf2e_spells else None,
            metadata={"category": "spells", "defiling": analysis["defiling_impact"]},
        )

        logger.info(f"Translated spell: {adnd_rule.name}")
        return result

