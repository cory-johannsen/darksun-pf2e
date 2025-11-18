"""Semantic mapping system for AD&D 2E to PF2E rule conversion.

This module provides intelligent rule translation using knowledge bases
and context analysis.
"""

from .context_analyzer import ContextAnalyzer, DarkSunContext
from .rule_translator import (
    AbilityScoreTranslator,
    CombatMechanicTranslator,
    RuleTranslator,
    SpellTranslator,
)
from .semantic_mapper import MappingConfidence, MappingResult, SemanticMapper

__all__ = [
    "SemanticMapper",
    "MappingResult",
    "MappingConfidence",
    "RuleTranslator",
    "AbilityScoreTranslator",
    "CombatMechanicTranslator",
    "SpellTranslator",
    "ContextAnalyzer",
    "DarkSunContext",
]

