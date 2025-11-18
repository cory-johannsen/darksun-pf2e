"""Unit tests for semantic mapper.

Requirements:
- SWENG-6: Test-driven development pattern
- SWENG-7: All functions MUST have automated unit tests
"""

import tempfile
import unittest
from pathlib import Path

from tools.pdf_pipeline.knowledge_base.adnd_schema import (
    ADnDAbilityScore,
    ADnDSourcebook,
)
from tools.pdf_pipeline.knowledge_base.knowledge_repository import (
    KnowledgeRepository,
    RuleCategory,
)
from tools.pdf_pipeline.mapping.context_analyzer import ContextAnalyzer, DarkSunContext
from tools.pdf_pipeline.mapping.rule_translator import AbilityScoreTranslator
from tools.pdf_pipeline.mapping.semantic_mapper import (
    MappingConfidence,
    SemanticMapper,
)


class TestContextAnalyzer(unittest.TestCase):
    """Test context analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContextAnalyzer()

    def test_analyzer_initialization(self):
        """Test analyzer initializes with Dark Sun context."""
        self.assertIsNotNone(self.analyzer.context)
        self.assertTrue(self.analyzer.context.metal_scarcity)
        self.assertTrue(self.analyzer.context.psionics_common)

    def test_analyze_ability_conversion(self):
        """Test ability score conversion analysis."""
        analysis = self.analyzer.analyze_ability_conversion("STR", 18)

        self.assertIn("pf2e_modifier", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("context_notes", analysis)
        self.assertEqual(analysis["pf2e_modifier"], 4)  # 18 -> +4

    def test_analyze_spell_conversion(self):
        """Test spell conversion analysis."""
        analysis = self.analyzer.analyze_spell_conversion(
            "Fireball", "Evocation"
        )

        self.assertIn("defiling_impact", analysis)
        self.assertTrue(analysis["defiling_impact"])  # Evocation can have defiling impact

    def test_analyze_equipment_conversion(self):
        """Test equipment conversion analysis."""
        analysis = self.analyzer.analyze_equipment_conversion(
            "Iron Sword", "iron"
        )

        self.assertIn("substitute_material", analysis)
        self.assertIsNotNone(analysis["substitute_material"])

    def test_score_to_modifier(self):
        """Test ability score to modifier conversion."""
        test_cases = [
            (3, -4),
            (10, 0),
            (11, 0),
            (18, 4),
            (20, 5),
        ]

        for score, expected_mod in test_cases:
            mod = self.analyzer._score_to_modifier(score)
            self.assertEqual(mod, expected_mod, f"Score {score} should give modifier {expected_mod}")


class TestRuleTranslator(unittest.TestCase):
    """Test rule translators."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContextAnalyzer()
        self.translator = AbilityScoreTranslator(self.analyzer)

    def test_translate_ability_score(self):
        """Test ability score translation."""
        from unittest.mock import MagicMock

        adnd_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={},
            source=ADnDSourcebook.DMG_REVISED,
        )

        # Mock PF2E client
        pf2e_client = MagicMock()
        pf2e_client.query_ability_scores.return_value = []

        result = self.translator.translate(adnd_rule, pf2e_client)

        self.assertIsNotNone(result)
        self.assertIn("confidence", result.__dict__)
        self.assertIn("conversion", result.__dict__)
        self.assertEqual(result.conversion["pf2e_modifier"], 4)


class TestSemanticMapper(unittest.TestCase):
    """Test semantic mapper."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.kb_dir = Path(self.temp_dir) / "knowledge_base"
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        # Initialize repository with test data
        self.repo = KnowledgeRepository(self.kb_dir)

        # Add test rule
        ability_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={},
            source=ADnDSourcebook.DMG_REVISED,
        )
        self.test_rule_id = self.repo.store_adnd_rule(
            ability_rule, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        # Initialize mapper
        self.mapper = SemanticMapper(self.kb_dir)

    def test_mapper_initialization(self):
        """Test mapper initializes correctly."""
        self.assertIsNotNone(self.mapper.repo)
        self.assertIsNotNone(self.mapper.pf2e_client)
        self.assertIsNotNone(self.mapper.context_analyzer)

    def test_map_rule(self):
        """Test mapping a single rule."""
        result = self.mapper.map_rule(
            self.test_rule_id,
            RuleCategory.ABILITY_SCORES,
            ADnDSourcebook.DMG_REVISED,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.adnd_rule_id, self.test_rule_id)
        self.assertIsInstance(result.confidence, MappingConfidence)

    def test_analyze_mapping_coverage(self):
        """Test coverage analysis."""
        stats = self.mapper.analyze_mapping_coverage(ADnDSourcebook.DMG_REVISED)

        self.assertIn("total_rules", stats)
        self.assertGreaterEqual(stats["total_rules"], 0)


if __name__ == "__main__":
    unittest.main()

