"""Unit tests for AD&D 2E rule extractor.

Requirements:
- SWENG-6: Test-driven development pattern
- SWENG-7: All functions MUST have automated unit tests
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.pdf_pipeline.domain import ExecutionContext, ProcessorInput
from tools.pdf_pipeline.knowledge_base.adnd_extractor import ADnDRuleExtractor
from tools.pdf_pipeline.knowledge_base.adnd_schema import (
    ADnDAbilityScore,
    ADnDSourcebook,
)
from tools.pdf_pipeline.knowledge_base.knowledge_repository import (
    KnowledgeRepository,
    RuleCategory,
)


class TestADnDExtractor(unittest.TestCase):
    """Test AD&D rule extractor."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.kb_dir = Path(self.temp_dir) / "knowledge_base"
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        # Create test sourcebook registry
        self.registry_file = self.kb_dir / "sourcebook_registry.json"
        registry_data = {
            "sourcebooks": [
                {
                    "id": "dmg_revised",
                    "filename": "test_dmg.pdf",
                    "extract_rules": ["ability_scores"],
                }
            ],
            "extraction_order": ["dmg_revised"],
        }
        self.registry_file.write_text(json.dumps(registry_data), encoding="utf-8")

    def test_extractor_initialization(self):
        """Test extractor can be initialized."""
        spec = MagicMock()
        spec.config = {
            "sourcebook_registry": str(self.registry_file),
            "knowledge_base_dir": str(self.kb_dir),
        }

        extractor = ADnDRuleExtractor(spec)
        self.assertEqual(extractor.config["knowledge_base_dir"], str(self.kb_dir))

    def test_get_category_for_rule(self):
        """Test category determination for rules."""
        spec = MagicMock()
        spec.config = {}
        extractor = ADnDRuleExtractor(spec)

        ability_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={},
            source=ADnDSourcebook.DMG_REVISED,
        )

        category = extractor._get_category_for_rule(ability_rule)
        self.assertEqual(category, RuleCategory.ABILITY_SCORES)

    def test_extract_ability_scores_structure(self):
        """Test ability score extraction returns correct structure."""
        spec = MagicMock()
        spec.config = {}
        extractor = ADnDRuleExtractor(spec)

        # Mock PDF extraction
        with patch("pdfplumber.open"):
            results = extractor._extract_ability_scores(
                Path("dummy.pdf"), ADnDSourcebook.DMG_REVISED
            )

        # Should return a list
        self.assertIsInstance(results, list)


class TestKnowledgeRepository(unittest.TestCase):
    """Test knowledge repository."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo = KnowledgeRepository(Path(self.temp_dir))

    def test_repository_initialization(self):
        """Test repository initializes correctly."""
        self.assertTrue(self.repo.adnd_dir.exists())
        self.assertTrue(self.repo.pf2e_dir.exists())
        self.assertIsNotNone(self.repo.index)

    def test_store_and_retrieve_adnd_rule(self):
        """Test storing and retrieving AD&D rules."""
        ability_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={"to_hit": 3, "damage": 7},
            source=ADnDSourcebook.DMG_REVISED,
            page_reference="14",
        )

        # Store rule
        rule_id = self.repo.store_adnd_rule(
            ability_rule, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        self.assertIsNotNone(rule_id)

        # Retrieve rule
        retrieved = self.repo.get_adnd_rule(
            rule_id, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.ability, "STR")
        self.assertEqual(retrieved.score, 18)

    def test_list_rules(self):
        """Test listing rules."""
        # Store some rules
        for score in [10, 15, 18]:
            ability_rule = ADnDAbilityScore(
                ability="STR",
                score=score,
                modifiers={},
                source=ADnDSourcebook.DMG_REVISED,
            )
            self.repo.store_adnd_rule(
                ability_rule, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
            )

        rules = self.repo.list_adnd_rules(
            category=RuleCategory.ABILITY_SCORES,
            sourcebook=ADnDSourcebook.DMG_REVISED,
        )

        self.assertEqual(len(rules), 3)

    def test_search_rules(self):
        """Test searching rules."""
        ability_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={},
            source=ADnDSourcebook.DMG_REVISED,
        )
        self.repo.store_adnd_rule(
            ability_rule, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        results = self.repo.search_adnd_rules("STR")
        self.assertGreater(len(results), 0)

    def test_get_statistics(self):
        """Test getting repository statistics."""
        stats = self.repo.get_statistics()

        self.assertIn("total_adnd_rules", stats)
        self.assertIn("total_pf2e_rules", stats)
        self.assertIsInstance(stats["total_adnd_rules"], int)


if __name__ == "__main__":
    unittest.main()

