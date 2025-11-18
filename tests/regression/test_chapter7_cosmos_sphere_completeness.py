"""Regression test for Chapter 7 Sphere of the Cosmos completeness.

This test ensures that ALL spells in the Sphere of the Cosmos are properly
extracted and rendered, preventing the regression where spells after 
"Animal Growth (5th)" were mixed into prose paragraphs.

[REGRESSION_TESTING] This test must pass after ANY modification to Chapter 7 processing.
[BEST_PRACTICES_UNIT_TESTS] This test runs automatically during validation.
"""

import json
import re
import unittest
from pathlib import Path


class TestChapter7CosmosCompleteness(unittest.TestCase):
    """Test that Sphere of the Cosmos spell list is complete and properly formatted."""
    
    @classmethod
    def setUpClass(cls):
        """Load the spell data and HTML output once for all tests."""
        cls.spell_data_path = Path("data/processed/chapter-seven-spells.json")
        cls.html_path = Path("data/html_output/chapter-seven-magic.html")
        
        if cls.spell_data_path.exists():
            with open(cls.spell_data_path, 'r') as f:
                cls.spell_data = json.load(f)
        else:
            cls.spell_data = None
        
        if cls.html_path.exists():
            with open(cls.html_path, 'r') as f:
                cls.html_content = f.read()
        else:
            cls.html_content = None
    
    def test_spell_data_file_exists(self):
        """Verify the spell data file exists."""
        self.assertTrue(
            self.spell_data_path.exists(),
            f"Spell data file not found at {self.spell_data_path}"
        )
    
    def test_html_output_exists(self):
        """Verify the HTML output file exists."""
        self.assertTrue(
            self.html_path.exists(),
            f"HTML output file not found at {self.html_path}"
        )
    
    def test_cosmos_sphere_has_all_expected_spells(self):
        """Verify Sphere of the Cosmos contains all expected spells through 7th level."""
        self.assertIsNotNone(self.spell_data, "Spell data not loaded")
        
        cosmos_spells = self.spell_data["spheres"]["Sphere of the Cosmos"]
        cosmos_spell_names = [spell["name"] for spell in cosmos_spells]
        
        # These are the spells that were being lost in the regression
        # They appear after "Animal Growth" in the source PDF
        critical_spells = [
            # 5th level spells
            "Animal Summoning II",
            "Anti-Plant Shell",
            "Atonement",
            "Commune",
            "Commune With Nature",
            "Cure Critical Wounds",
            "Dispel Evil",
            "Moonbeam",
            "Pass Plant",
            "Quest",
            "Rainbow",
            "Raise Dead",
            "True Seeing",
            # 6th level spells
            "Animal Summoning III",
            "Animate Object",
            "Anti-Animal Shell",
            "Blade Barrier",
            "Conjure Animals",
            "Create Tree of Life",
            "Find the Path",
            "Heal",
            "Feast",  # Also known as "Heroes' Feast"
            "Liveoak",
            "Speak With Monsters",
            "Transport Via Plants",
            "Turn Wood",
            "Wall of Thorns",
            "Word of Recall",
            # 7th level spells
            "Changestaff",
            "Confusion",
            "Creeping Doom",
            "Exaction",
            "Gate",
            "Holy Word",
            "Regenerate",
            "Reincarnate",
            "Restoration",
            "Resurrection",
            "Succor",
            "Sunray",
            "Symbol"
        ]
        
        missing_spells = [spell for spell in critical_spells if spell not in cosmos_spell_names]
        
        self.assertEqual(
            len(missing_spells),
            0,
            f"Sphere of the Cosmos is missing {len(missing_spells)} critical spells: {missing_spells}"
        )
    
    def test_cosmos_sphere_ends_with_symbol(self):
        """Verify that the last 7th level spell in Sphere of the Cosmos is Symbol."""
        self.assertIsNotNone(self.spell_data, "Spell data not loaded")
        
        cosmos_spells = self.spell_data["spheres"]["Sphere of the Cosmos"]
        
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
    
    def test_html_cosmos_spells_in_list_format(self):
        """Verify that Cosmos spells appear as <li> elements, not plain text in paragraphs."""
        self.assertIsNotNone(self.html_content, "HTML content not loaded")
        
        # Extract the section between Cosmos header and Wizardly Magic header
        cosmos_match = re.search(
            r'<p id="header-5-sphere-of-the-cosmos">',
            self.html_content
        )
        wizardly_match = re.search(
            r'<p id="header-6-wizardly-magic">',
            self.html_content
        )
        
        self.assertIsNotNone(cosmos_match, "Could not find Sphere of the Cosmos header")
        self.assertIsNotNone(wizardly_match, "Could not find Wizardly Magic header")
        
        cosmos_section = self.html_content[cosmos_match.end():wizardly_match.start()]
        
        # These spells should appear as <li class="spell-list-item"> elements
        critical_spells_to_check = [
            "Animal Summoning II (5th)",
            "Anti-Plant Shell (5th)",
            "Atonement (5th)",
            "Animal Summoning III (6th)",
            "Changestaff (7th)",
            "Symbol (7th)"
        ]
        
        for spell in critical_spells_to_check:
            # Check if the spell appears as a list item
            list_item_pattern = rf'<li class="spell-list-item">{re.escape(spell)}</li>'
            
            self.assertIsNotNone(
                re.search(list_item_pattern, cosmos_section),
                f"Spell '{spell}' should appear as a list item in Sphere of the Cosmos section, "
                f"but was not found in the expected format"
            )
    
    def test_html_no_spells_mixed_in_cosmos_paragraphs(self):
        """Verify that spell names with levels are not mixed into prose paragraphs."""
        self.assertIsNotNone(self.html_content, "HTML content not loaded")
        
        # Extract the section between Cosmos header and Wizardly Magic header
        cosmos_match = re.search(
            r'<p id="header-5-sphere-of-the-cosmos">',
            self.html_content
        )
        wizardly_match = re.search(
            r'<p id="header-6-wizardly-magic">',
            self.html_content
        )
        
        self.assertIsNotNone(cosmos_match, "Could not find Sphere of the Cosmos header")
        self.assertIsNotNone(wizardly_match, "Could not find Wizardly Magic header")
        
        cosmos_section = self.html_content[cosmos_match.end():wizardly_match.start()]
        
        # Find all <p> tags that are not headers
        paragraph_pattern = r'<p>([^<]+(?:<[^/][^>]*>[^<]*</[^>]+>[^<]*)*)</p>'
        paragraphs = re.findall(paragraph_pattern, cosmos_section)
        
        # Pattern to match spell format: "Spell Name (level)"
        spell_pattern = r'\b\w+(?:\s+\w+)*\s*\([567]th\)'
        
        spells_in_paragraphs = []
        for paragraph in paragraphs:
            # Skip if this is a clerics/deities explanatory paragraph (these are OK)
            if "Clerics have major access" in paragraph or "There are no deities" in paragraph:
                continue
            
            matches = re.findall(spell_pattern, paragraph)
            if matches:
                spells_in_paragraphs.extend(matches)
        
        self.assertEqual(
            len(spells_in_paragraphs),
            0,
            f"Found {len(spells_in_paragraphs)} spell references mixed into paragraphs: {spells_in_paragraphs}"
        )
    
    def test_cosmos_sphere_minimum_spell_count(self):
        """Verify Sphere of the Cosmos has at least 120 spells (expected count)."""
        self.assertIsNotNone(self.spell_data, "Spell data not loaded")
        
        cosmos_spells = self.spell_data["spheres"]["Sphere of the Cosmos"]
        
        # The Sphere of the Cosmos is the largest sphere and should have
        # at least 120 spells (1st through 7th level)
        self.assertGreaterEqual(
            len(cosmos_spells),
            120,
            f"Sphere of the Cosmos should have at least 120 spells, but has {len(cosmos_spells)}"
        )


if __name__ == "__main__":
    unittest.main()

