"""Unit tests for PF2E MCP client.

Requirements:
- SWENG-6: Test-driven development pattern
- SWENG-7: All functions MUST have automated unit tests
"""

import tempfile
import unittest
from pathlib import Path

from tools.pdf_pipeline.knowledge_base.pf2e_client import PF2EMCPClient
from tools.pdf_pipeline.knowledge_base.pf2e_schema import (
    PF2EAbilityScore,
    PF2ESave,
    PF2ESkill,
)


class TestPF2EMCPClient(unittest.TestCase):
    """Test PF2E MCP client."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "pf2e_cache"
        self.client = PF2EMCPClient(self.cache_dir)

    def test_client_initialization(self):
        """Test client initializes correctly."""
        self.assertTrue(self.cache_dir.exists())
        self.assertEqual(self.client.mcp_server, "p2fe")

    def test_query_ability_scores(self):
        """Test querying ability scores."""
        ability_scores = self.client.query_ability_scores()

        self.assertIsInstance(ability_scores, list)
        self.assertGreater(len(ability_scores), 0)

        # Check first result
        first_score = ability_scores[0]
        self.assertIsInstance(first_score, PF2EAbilityScore)
        self.assertIn(first_score.ability, ["STR", "DEX", "CON", "INT", "WIS", "CHA"])

    def test_query_saves(self):
        """Test querying saves."""
        saves = self.client.query_saves()

        self.assertIsInstance(saves, list)
        self.assertEqual(len(saves), 3)  # Fortitude, Reflex, Will

        # Check structure
        for save in saves:
            self.assertIsInstance(save, PF2ESave)
            self.assertIn(save.save_type, ["Fortitude", "Reflex", "Will"])

    def test_query_skills(self):
        """Test querying skills."""
        skills = self.client.query_skills()

        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)

        # Check structure
        for skill in skills:
            self.assertIsInstance(skill, PF2ESkill)
            self.assertIsNotNone(skill.name)
            self.assertIsNotNone(skill.ability)

    def test_cache_functionality(self):
        """Test that caching works."""
        # First query
        scores1 = self.client.query_ability_scores()

        # Second query should use cache
        scores2 = self.client.query_ability_scores()

        # Results should be identical
        self.assertEqual(len(scores1), len(scores2))
        self.assertEqual(scores1[0].ability, scores2[0].ability)

    def test_get_schema_type(self):
        """Test schema type retrieval."""
        from tools.pdf_pipeline.knowledge_base.knowledge_repository import RuleCategory

        schema_type = self.client._get_schema_type(RuleCategory.ABILITY_SCORES)
        self.assertEqual(schema_type, PF2EAbilityScore)

        schema_type = self.client._get_schema_type(RuleCategory.SAVES)
        self.assertEqual(schema_type, PF2ESave)


if __name__ == "__main__":
    unittest.main()

