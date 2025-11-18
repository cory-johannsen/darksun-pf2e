"""Regression tests for rule mappings.

Requirements:
- VALIDATION-2: Regression tests to prevent reversions
- VALIDATION-3: ALL regression tests must pass after modifications
"""

import unittest

from tools.pdf_pipeline.mapping.context_analyzer import ContextAnalyzer


class TestRuleMappingRegression(unittest.TestCase):
    """Regression tests for rule mappings."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ContextAnalyzer()

    def test_ability_score_to_modifier_mapping(self):
        """Test ability score to modifier conversions don't regress."""
        # These mappings should remain consistent
        test_cases = {
            3: -4,
            4: -3,
            6: -2,
            8: -1,
            10: 0,
            11: 0,
            12: 1,
            14: 2,
            16: 3,
            18: 4,
            20: 5,
            22: 6,
            24: 7,
        }

        for score, expected_modifier in test_cases.items():
            modifier = self.analyzer._score_to_modifier(score)
            self.assertEqual(
                modifier,
                expected_modifier,
                f"Ability score {score} should map to modifier {expected_modifier}, got {modifier}",
            )

    def test_dark_sun_context_preservation(self):
        """Test Dark Sun context settings don't regress."""
        context = self.analyzer.context

        # Core Dark Sun setting features must be enabled
        self.assertTrue(context.metal_scarcity, "Metal scarcity must be True for Dark Sun")
        self.assertTrue(context.water_scarcity, "Water scarcity must be True for Dark Sun")
        self.assertTrue(context.psionics_common, "Psionics must be common in Dark Sun")
        self.assertTrue(context.defiling_magic, "Defiling magic must exist in Dark Sun")
        self.assertTrue(context.harsh_environment, "Environment must be harsh in Dark Sun")

    def test_spell_defiling_detection(self):
        """Test defiling spell detection doesn't regress."""
        # Evocation spells should have defiling impact
        analysis = self.analyzer.analyze_spell_conversion("Fireball", "Evocation")
        self.assertTrue(
            analysis["defiling_impact"],
            "Evocation spells should have defiling impact",
        )

        # Transmutation spells should have defiling impact
        analysis = self.analyzer.analyze_spell_conversion("Polymorph", "Transmutation")
        self.assertTrue(
            analysis["defiling_impact"],
            "Transmutation spells should have defiling impact",
        )

        # Conjuration spells should have defiling impact
        analysis = self.analyzer.analyze_spell_conversion("Summon Monster", "Conjuration")
        self.assertTrue(
            analysis["defiling_impact"],
            "Conjuration spells should have defiling impact",
        )

    def test_metal_substitution_detection(self):
        """Test metal substitution recommendations don't regress."""
        metal_materials = ["iron", "steel", "metal"]

        for material in metal_materials:
            analysis = self.analyzer.analyze_equipment_conversion(
                f"{material.title()} Sword", material
            )

            self.assertIsNotNone(
                analysis["substitute_material"],
                f"{material.title()} should have substitute material recommendation",
            )
            self.assertIn(
                "bone",
                analysis["substitute_material"].lower(),
                f"Substitute should mention bone for {material}",
            )

    def test_water_spell_rarity_detection(self):
        """Test water spell rarity detection doesn't regress."""
        water_spells = ["Create Water", "Water Breathing", "Wall of Water"]

        for spell_name in water_spells:
            analysis = self.analyzer.analyze_spell_conversion(spell_name, "Conjuration")

            # Should have recommendations about rarity
            has_water_recommendation = any(
                "water" in rec.lower() for rec in analysis["recommendations"]
            )
            has_water_note = any("water" in note.lower() for note in analysis["context_notes"])

            self.assertTrue(
                has_water_recommendation or has_water_note,
                f"Water spell {spell_name} should have water-related recommendations or notes",
            )


class TestConversionFormulaRegression(unittest.TestCase):
    """Regression tests for conversion formulas."""

    def test_thac0_to_attack_bonus_formula(self):
        """Test THAC0 conversion formula doesn't change."""
        from tools.pdf_pipeline.mapping.rule_translator import CombatMechanicTranslator

        analyzer = ContextAnalyzer()
        translator = CombatMechanicTranslator(analyzer)

        # Mock THAC0 rule
        class MockTHAC0:
            thac0 = 15
            level = 5

        rule = MockTHAC0()
        conversion = translator._convert_thac0(rule)

        # Formula: 20 - THAC0
        expected_bonus = 20 - 15
        self.assertEqual(
            conversion["pf2e_attack_bonus"],
            expected_bonus,
            "THAC0 conversion formula should be 20 - THAC0",
        )

    def test_armor_class_conversion_formula(self):
        """Test AC conversion formula doesn't change."""
        from tools.pdf_pipeline.mapping.rule_translator import CombatMechanicTranslator

        analyzer = ContextAnalyzer()
        translator = CombatMechanicTranslator(analyzer)

        # Mock AC rule
        class MockAC:
            base_ac = 5
            armor_type = "Chain Mail"

        rule = MockAC()
        conversion = translator._convert_armor_class(rule)

        # Formula: 20 - AD&D AC
        expected_ac = 20 - 5
        self.assertEqual(
            conversion["pf2e_ac"],
            expected_ac,
            "AC conversion formula should be 20 - AD&D AC",
        )


if __name__ == "__main__":
    unittest.main()

