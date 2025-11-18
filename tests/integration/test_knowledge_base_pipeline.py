"""Integration tests for knowledge base pipeline.

Requirements:
- SWENG-8: Integration tests MUST span extraction, transformation, processing
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from tools.pdf_pipeline.domain import ExecutionContext, ProcessorInput
from tools.pdf_pipeline.knowledge_base.adnd_extractor import ADnDRuleExtractor
from tools.pdf_pipeline.knowledge_base.knowledge_repository import KnowledgeRepository
from tools.pdf_pipeline.knowledge_base.pf2e_client import PF2ECacheInitializer
from tools.pdf_pipeline.stages.rules_conversion import ADnDToPF2EProcessor


class TestKnowledgeBasePipeline(unittest.TestCase):
    """Integration tests for complete knowledge base pipeline."""

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
                    "extract_rules": [],  # Empty for integration test
                }
            ],
            "extraction_order": ["dmg_revised"],
        }
        self.registry_file.write_text(json.dumps(registry_data), encoding="utf-8")

    def test_complete_pipeline_flow(self):
        """Test complete pipeline from extraction to conversion."""
        # 1. Initialize knowledge repository
        repo = KnowledgeRepository(self.kb_dir)
        self.assertTrue(repo.adnd_dir.exists())
        self.assertTrue(repo.pf2e_dir.exists())

        # 2. Initialize PF2E cache
        cache_spec = MagicMock()
        cache_spec.config = {
            "cache_dir": str(self.kb_dir / "pf2e_cache"),
            "mcp_server": "p2fe",
            "initial_queries": ["ability_scores"],
        }

        cache_initializer = PF2ECacheInitializer(cache_spec)
        context = ExecutionContext()
        input_data = ProcessorInput(data={})

        cache_result = cache_initializer.process(input_data, context)
        self.assertGreater(cache_result.data["cached_items"], 0)

        # 3. Test conversion processor with knowledge base
        processed_dir = self.kb_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)

        # Create test processed file
        test_file = processed_dir / "test_data.json"
        test_file.write_text(json.dumps({"test": "data"}), encoding="utf-8")

        conversion_spec = MagicMock()
        conversion_spec.config = {
            "processed_dir": str(processed_dir),
            "output_dir": str(self.kb_dir / "pf2e_converted"),
            "knowledge_base_dir": str(self.kb_dir),
            "preserve_flavor": True,
        }

        converter = ADnDToPF2EProcessor(conversion_spec)
        conversion_result = converter.process(input_data, context)

        self.assertGreater(conversion_result.metadata["file_count"], 0)
        self.assertEqual(conversion_result.metadata["conversion_mode"], "semantic_mapping")

    def test_repository_to_mapper_integration(self):
        """Test integration between repository and semantic mapper."""
        from tools.pdf_pipeline.knowledge_base.adnd_schema import (
            ADnDAbilityScore,
            ADnDSourcebook,
        )
        from tools.pdf_pipeline.knowledge_base.knowledge_repository import RuleCategory
        from tools.pdf_pipeline.mapping.semantic_mapper import SemanticMapper

        # Store test rule
        repo = KnowledgeRepository(self.kb_dir)
        ability_rule = ADnDAbilityScore(
            ability="STR",
            score=18,
            modifiers={},
            source=ADnDSourcebook.DMG_REVISED,
        )
        rule_id = repo.store_adnd_rule(
            ability_rule, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        # Map rule using semantic mapper
        mapper = SemanticMapper(self.kb_dir)
        result = mapper.map_rule(
            rule_id, RuleCategory.ABILITY_SCORES, ADnDSourcebook.DMG_REVISED
        )

        self.assertEqual(result.adnd_rule_id, rule_id)
        self.assertIsNotNone(result.confidence)
        self.assertIn("conversion", result.__dict__)


if __name__ == "__main__":
    unittest.main()

