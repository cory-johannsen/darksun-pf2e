"""Unit tests for Chapter 7 column-aware spell parsing.

This test ensures that spells from "Sphere of the Cosmos" are not incorrectly
mixed into "Wizardly Magic" due to 2-column layout issues.

[BEST_PRACTICES_UNIT_TESTS] Every function that is created should have an automated unit test.
[REGRESSION_TESTING] This test prevents regressions in spell sphere assignment.
"""

import json
import unittest
from pathlib import Path


class TestChapter7ColumnAwareParsing(unittest.TestCase):
    """Test that Chapter 7 spell parsing correctly handles 2-column layout."""
    
    def test_sphere_of_cosmos_ends_with_symbol(self):
        """Verify that 'Sphere of the Cosmos' spell list ends with 'Symbol (7th)'."""
        spell_data_path = Path("data/processed/chapter-seven-spells.json")
        
        self.assertTrue(
            spell_data_path.exists(),
            f"Spell data file not found at {spell_data_path}"
        )
        
        with open(spell_data_path, 'r') as f:
            spell_data = json.load(f)
        
        cosmos_spells = spell_data["spheres"]["Sphere of the Cosmos"]
        
        # Verify we have spells
        self.assertGreater(
            len(cosmos_spells),
            0,
            "Sphere of the Cosmos should have spells"
        )
        
        # Find the last 7th level spell
        seventh_level_spells = [
            spell for spell in cosmos_spells
            if spell["level"] == "7th"
        ]
        
        self.assertGreater(
            len(seventh_level_spells),
            0,
            "Sphere of the Cosmos should have 7th level spells"
        )
        
        # Verify Symbol is in the list
        symbol_spells = [
            spell for spell in seventh_level_spells
            if spell["name"] == "Symbol"
        ]
        
        self.assertEqual(
            len(symbol_spells),
            1,
            "Should have exactly one 'Symbol' spell in Sphere of the Cosmos"
        )
    
    def test_no_wizardly_spells_in_cosmos_sphere(self):
        """Verify that Wizardly Magic spells are not in Sphere of the Cosmos."""
        spell_data_path = Path("data/processed/chapter-seven-spells.json")
        
        with open(spell_data_path, 'r') as f:
            spell_data = json.load(f)
        
        cosmos_spells = spell_data["spheres"]["Sphere of the Cosmos"]
        cosmos_spell_names = [spell["name"] for spell in cosmos_spells]
        
        # These spells should NOT be in Sphere of the Cosmos
        # (they belong to wizard spell lists, not priest spheres)
        wizardly_spell_indicators = [
            "Magic Missile",
            "Lightning Bolt",
            "Fireball",
            "Advanced Illusion"
        ]
        
        for wizard_spell in wizardly_spell_indicators:
            self.assertNotIn(
                wizard_spell,
                cosmos_spell_names,
                f"Wizard spell '{wizard_spell}' should not be in Sphere of the Cosmos"
            )
    
    def test_html_cosmos_sphere_ends_before_wizardly_magic(self):
        """Verify that in HTML output, Sphere of Cosmos spells end before Wizardly Magic section."""
        html_path = Path("data/html_output/chapter-seven-magic.html")
        
        self.assertTrue(
            html_path.exists(),
            f"HTML output not found at {html_path}"
        )
        
        with open(html_path, 'r') as f:
            html_content = f.read()
        
        # Find the positions of key markers
        symbol_pos = html_content.find("Symbol (7th)")
        wizardly_magic_pos = html_content.find('id="header-6-wizardly-magic"')
        
        self.assertGreater(
            symbol_pos,
            0,
            "Should find 'Symbol (7th)' in HTML"
        )
        
        self.assertGreater(
            wizardly_magic_pos,
            0,
            "Should find Wizardly Magic header in HTML"
        )
        
        # The issue was that spells after Symbol (like Animal Summoning III, etc.)
        # were appearing AFTER the Wizardly Magic header. Now they should appear BEFORE.
        # We verify this by checking that all Cosmos spells appear between
        # the Cosmos header and the Wizardly Magic header.
        
        cosmos_header_pos = html_content.find('id="header-5-sphere-of-the-cosmos"')
        
        # Extract the section between Cosmos header and Wizardly Magic header
        cosmos_section = html_content[cosmos_header_pos:wizardly_magic_pos]
        
        # Verify Symbol is in the Cosmos section
        self.assertIn(
            "Symbol (7th)",
            cosmos_section,
            "Symbol (7th) should be in the Sphere of the Cosmos section"
        )
        
        # Verify these high-level cosmos spells are NOT after Wizardly Magic
        wizardly_magic_section = html_content[wizardly_magic_pos:]
        
        cosmos_spell_names = [
            "Animal Summoning III (6th)",
            "Animate Object (6th)",
            "Anti-Animal Shell (6th)",
            "Blade Barrier (6th)",
            "Changestaff (7th)",
            "Confusion (7th)",
            "Creeping Doom (7th)",
            "Resurrection (7th)"
        ]
        
        # Count how many cosmos spells appear after Wizardly Magic
        spells_after_wizardly = []
        for spell_name in cosmos_spell_names:
            if spell_name in wizardly_magic_section:
                # Check if it's in a spell list item context
                # (it might appear in explanatory text, which would be OK)
                spell_list_context = f'<li class="spell-list-item">{spell_name}</li>'
                if spell_list_context in wizardly_magic_section:
                    spells_after_wizardly.append(spell_name)
        
        self.assertEqual(
            len(spells_after_wizardly),
            0,
            f"These Cosmos spells should not appear as list items after Wizardly Magic header: {spells_after_wizardly}"
        )


if __name__ == "__main__":
    unittest.main()

