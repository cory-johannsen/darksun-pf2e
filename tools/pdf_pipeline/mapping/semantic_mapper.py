"""Semantic mapping engine for rule conversions.

This module provides the core mapping logic that translates AD&D 2E rules
to PF2E equivalents using knowledge bases and context analysis.

Requirements:
- SWENG-1: Single Responsibility Principle
- SWENG-2: Design by Contract
- PY-6: Console logs tracing execution
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ..knowledge_base.adnd_schema import ADnDSourcebook
from ..knowledge_base.knowledge_repository import KnowledgeRepository, RuleCategory
from ..knowledge_base.pf2e_client import PF2EMCPClient
from .context_analyzer import ContextAnalyzer, DarkSunContext

if TYPE_CHECKING:
    from .rule_translator import (
        AbilityScoreTranslator,
        CombatMechanicTranslator,
        SpellTranslator,
    )

# Set up logging per PY-6
logger = logging.getLogger(__name__)


class MappingConfidence(str, Enum):
    """Confidence level for rule mappings."""

    HIGH = "high"  # Automatic conversion recommended
    MEDIUM = "medium"  # Review recommended
    LOW = "low"  # Manual intervention required
    UNMAPPABLE = "unmappable"  # No direct mapping available


class MappingResult(BaseModel):
    """Result of a rule mapping operation.

    Contains the converted rule, confidence level, and metadata.
    """

    adnd_rule_id: str = Field(..., description="Source AD&D rule identifier")
    pf2e_rule_id: Optional[str] = Field(None, description="Target PF2E rule identifier")
    confidence: MappingConfidence = Field(..., description="Mapping confidence level")
    conversion: Dict[str, Any] = Field(
        default_factory=dict, description="Converted rule data"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Conversion recommendations"
    )
    context_notes: List[str] = Field(
        default_factory=list, description="Context-specific notes"
    )
    fallback_strategy: Optional[str] = Field(
        None, description="Fallback strategy if mapping fails"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class SemanticMapper:
    """Semantic mapper for converting AD&D 2E rules to PF2E.

    Uses knowledge bases, context analysis, and rule translators to perform
    intelligent rule conversions that preserve setting flavor.

    Preconditions:
    - Knowledge repository must be initialized with AD&D rules
    - PF2E client must have access to PF2E rule data

    Postconditions:
    - All mappings include confidence scores
    - Flavor text is preserved per SPEC.md
    """

    def __init__(
        self,
        knowledge_base_dir: Path,
        context: Optional[DarkSunContext] = None,
        mcp_server: str = "p2fe",
    ):
        """Initialize the semantic mapper.

        Args:
            knowledge_base_dir: Path to knowledge base directory
            context: Optional Dark Sun context
            mcp_server: MCP server identifier for PF2E queries
        """
        # Import translators at runtime to avoid circular import
        from .rule_translator import (
            AbilityScoreTranslator,
            CombatMechanicTranslator,
            SpellTranslator,
        )
        
        self.repo = KnowledgeRepository(knowledge_base_dir)
        self.pf2e_client = PF2EMCPClient(
            knowledge_base_dir / "pf2e_cache", mcp_server
        )
        self.context_analyzer = ContextAnalyzer(context)

        # Initialize translators
        self.ability_translator = AbilityScoreTranslator(self.context_analyzer)
        self.combat_translator = CombatMechanicTranslator(self.context_analyzer)
        self.spell_translator = SpellTranslator(self.context_analyzer)

        logger.info(f"Initialized SemanticMapper with KB at {knowledge_base_dir}")

    def map_rule(
        self,
        rule_id: str,
        category: RuleCategory,
        sourcebook: ADnDSourcebook,
    ) -> MappingResult:
        """Map a single AD&D rule to PF2E equivalent.

        Args:
            rule_id: AD&D rule identifier
            category: Rule category
            sourcebook: Source sourcebook

        Returns:
            Mapping result with conversion and confidence
        """
        logger.debug(f"Mapping rule: {rule_id} ({category.value})")

        # Retrieve AD&D rule
        adnd_rule = self.repo.get_adnd_rule(rule_id, category, sourcebook)
        if not adnd_rule:
            return self._create_unmappable_result(
                rule_id, "Rule not found in knowledge base"
            )

        # Route to appropriate translator
        try:
            if category == RuleCategory.ABILITY_SCORES:
                return self.ability_translator.translate(adnd_rule, self.pf2e_client)
            elif category == RuleCategory.COMBAT:
                return self.combat_translator.translate(adnd_rule, self.pf2e_client)
            elif category == RuleCategory.SPELLS:
                return self.spell_translator.translate(adnd_rule, self.pf2e_client)
            else:
                return self._create_generic_mapping(adnd_rule, category)

        except Exception as e:
            logger.error(f"Error mapping rule {rule_id}: {e}", exc_info=True)
            return self._create_unmappable_result(rule_id, str(e))

    def map_batch(
        self,
        rule_ids: List[str],
        category: RuleCategory,
        sourcebook: ADnDSourcebook,
    ) -> List[MappingResult]:
        """Map multiple AD&D rules in batch.

        Args:
            rule_ids: List of AD&D rule identifiers
            category: Rule category
            sourcebook: Source sourcebook

        Returns:
            List of mapping results
        """
        logger.info(f"Mapping batch of {len(rule_ids)} rules")

        results = []
        for rule_id in rule_ids:
            result = self.map_rule(rule_id, category, sourcebook)
            results.append(result)

        return results

    def analyze_mapping_coverage(
        self, sourcebook: ADnDSourcebook
    ) -> Dict[str, Any]:
        """Analyze mapping coverage for a sourcebook.

        Args:
            sourcebook: Source sourcebook

        Returns:
            Coverage statistics
        """
        logger.info(f"Analyzing mapping coverage for {sourcebook.value}")

        stats = {
            "total_rules": 0,
            "mapped_rules": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "unmappable": 0,
            "by_category": {},
        }

        # Get all rules from sourcebook
        all_rules = self.repo.list_adnd_rules(sourcebook=sourcebook)
        stats["total_rules"] = len(all_rules)

        # For now, return basic stats
        # Real implementation would analyze all mappings
        logger.debug(f"Coverage analysis complete: {stats}")
        return stats

    def _create_generic_mapping(
        self, adnd_rule: Any, category: RuleCategory
    ) -> MappingResult:
        """Create a generic mapping for unsupported categories.

        Args:
            adnd_rule: AD&D rule
            category: Rule category

        Returns:
            Mapping result with low confidence
        """
        rule_name = getattr(adnd_rule, "name", "unknown")

        return MappingResult(
            adnd_rule_id=rule_name,
            confidence=MappingConfidence.LOW,
            recommendations=["Manual conversion required for this rule category"],
            context_notes=["Generic mapping applied - category not yet supported"],
            fallback_strategy="preserve_as_variant_rule",
            metadata={"category": category.value},
        )

    def _create_unmappable_result(
        self, rule_id: str, reason: str
    ) -> MappingResult:
        """Create an unmappable result.

        Args:
            rule_id: Rule identifier
            reason: Reason for unmappable status

        Returns:
            Mapping result with unmappable confidence
        """
        return MappingResult(
            adnd_rule_id=rule_id,
            confidence=MappingConfidence.UNMAPPABLE,
            recommendations=["Rule could not be mapped"],
            context_notes=[f"Unmappable: {reason}"],
            fallback_strategy="manual_review_required",
        )

