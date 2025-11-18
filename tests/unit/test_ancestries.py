"""Unit tests for ancestries transformer."""

import unittest

from tools.pdf_pipeline.transformers.ancestries import (
    _normalize_text,
    _find_entity_windows,
    _ability_boosts,
    _ability_flaws,
    transform,
)


class TestNormalizeText(unittest.TestCase):
    """Test the _normalize_text function."""
    
    def test_combine_multiple_pages(self):
        """Test combining text from multiple pages."""
        pages = [
            {"text": "First page content."},
            {"text": "Second page content."},
            {"text": "Third page content."}
        ]
        result = _normalize_text(pages)
        self.assertIn("First page content", result)
        self.assertIn("Second page content", result)
        self.assertIn("Third page content", result)
    
    def test_repair_hyphenated_line_breaks(self):
        """Test that hyphenated line breaks are repaired."""
        pages = [
            {"text": "This is a hyphen-\nated word."}
        ]
        result = _normalize_text(pages)
        self.assertEqual(result.strip(), "This is a hyphenated word.")
    
    def test_normalize_carriage_returns(self):
        """Test that carriage returns are converted to newlines."""
        pages = [
            {"text": "Line one\rLine two\rLine three"}
        ]
        result = _normalize_text(pages)
        self.assertIn("\n", result)
        self.assertNotIn("\r", result)
    
    def test_collapse_excess_newlines(self):
        """Test that excessive newlines are collapsed."""
        pages = [
            {"text": "Paragraph one.\n\n\n\nParagraph two."}
        ]
        result = _normalize_text(pages)
        # Should have at most 2 newlines in a row
        self.assertNotIn("\n\n\n", result)
    
    def test_empty_pages(self):
        """Test handling empty pages."""
        pages = [
            {"text": ""},
            {"text": "Content"},
            {"text": ""}
        ]
        result = _normalize_text(pages)
        self.assertEqual(result.strip(), "Content")


class TestFindEntityWindows(unittest.TestCase):
    """Test the _find_entity_windows function."""
    
    def test_find_single_entity(self):
        """Test finding a single entity in text."""
        text = "Human\n\nHumans are versatile creatures."
        mapping = [
            {"name": "Human", "aliases": [], "heading": "Human"}
        ]
        
        result = _find_entity_windows(text, mapping)
        
        self.assertIn("Human", result)
        start, end = result["Human"]
        self.assertGreaterEqual(start, 0)
        self.assertEqual(end, len(text))
    
    def test_find_multiple_entities(self):
        """Test finding multiple entities in order."""
        text = """
Dwarf

Dwarves are stout and resilient.

Elf

Elves are graceful and quick.
"""
        mapping = [
            {"name": "Dwarf", "aliases": [], "heading": "Dwarf"},
            {"name": "Elf", "aliases": [], "heading": "Elf"}
        ]
        
        result = _find_entity_windows(text, mapping)
        
        self.assertIn("Dwarf", result)
        self.assertIn("Elf", result)
        
        # Dwarf window should come before Elf window
        dwarf_start, dwarf_end = result["Dwarf"]
        elf_start, elf_end = result["Elf"]
        self.assertLess(dwarf_start, elf_start)
        self.assertEqual(dwarf_end, elf_start)
    
    def test_find_entity_by_alias(self):
        """Test finding entity by alias."""
        text = "Half-Giant\n\nHalf-giants are enormous."
        mapping = [
            {"name": "Half-Giant", "aliases": ["Half Giant", "Halfgiant"], "heading": "Half-Giant"}
        ]
        
        result = _find_entity_windows(text, mapping)
        
        self.assertIn("Half-Giant", result)
    
    def test_entity_not_found_uses_fallback(self):
        """Test fallback search when heading doesn't match."""
        text = "Some intro text.\n\nMul\n\nMuls are hybrid beings."
        mapping = [
            {"name": "Mul", "aliases": ["Muls"], "heading": None}
        ]
        
        result = _find_entity_windows(text, mapping)
        
        # Should still find Mul by name/alias
        self.assertIn("Mul", result)


class TestAbilityBoosts(unittest.TestCase):
    """Test the _ability_boosts function."""
    
    def test_two_positive_modifiers(self):
        """Test with two positive ability modifiers."""
        mods = {"str": 2, "con": 1, "dex": 0, "int": 0, "wis": 0, "cha": 0}
        result = _ability_boosts(mods)
        
        # Should return str, con, and free
        self.assertEqual(len(result), 3)
        self.assertIn("strength", result)
        self.assertIn("constitution", result)
        self.assertIn("free", result)
    
    def test_one_positive_modifier(self):
        """Test with one positive ability modifier."""
        mods = {"str": 2, "con": 0, "dex": 0, "int": 0, "wis": 0, "cha": 0}
        result = _ability_boosts(mods)
        
        # Should return str and free
        self.assertEqual(len(result), 2)
        self.assertIn("strength", result)
        self.assertIn("free", result)
    
    def test_three_positive_modifiers(self):
        """Test with three positive modifiers (takes top 2)."""
        mods = {"str": 2, "con": 2, "dex": 1, "int": 0, "wis": 0, "cha": 0}
        result = _ability_boosts(mods)
        
        # Should return top 2 plus free
        self.assertEqual(len(result), 3)
        self.assertIn("free", result)
        # Should include str and con (highest values)
        self.assertIn("strength", result)
        self.assertIn("constitution", result)
    
    def test_no_positive_modifiers(self):
        """Test with no positive modifiers."""
        mods = {"str": 0, "con": 0, "dex": -1, "int": 0, "wis": 0, "cha": 0}
        result = _ability_boosts(mods)
        
        # Should return free boost
        self.assertIn("free", result)
    
    def test_equal_positive_modifiers(self):
        """Test with equal positive modifiers (alphabetical order)."""
        mods = {"str": 1, "dex": 1, "con": 1, "int": 0, "wis": 0, "cha": 0}
        result = _ability_boosts(mods)
        
        # Should have 3 boosts
        self.assertEqual(len(result), 3)
        self.assertIn("free", result)


class TestAbilityFlaws(unittest.TestCase):
    """Test the _ability_flaws function."""
    
    def test_single_negative_modifier(self):
        """Test with one negative ability modifier."""
        mods = {"str": 0, "con": 0, "dex": 0, "int": 0, "wis": 0, "cha": -2}
        result = _ability_flaws(mods)
        
        self.assertEqual(len(result), 1)
        self.assertIn("charisma", result)
    
    def test_multiple_equal_negative_modifiers(self):
        """Test with multiple equal negative modifiers."""
        mods = {"str": -1, "con": 0, "dex": 0, "int": 0, "wis": -1, "cha": 0}
        result = _ability_flaws(mods)
        
        # Should return both
        self.assertEqual(len(result), 2)
        self.assertIn("strength", result)
        self.assertIn("wisdom", result)
    
    def test_different_negative_modifiers(self):
        """Test with different negative modifiers (takes worst)."""
        mods = {"str": -1, "con": 0, "dex": 0, "int": 0, "wis": 0, "cha": -2}
        result = _ability_flaws(mods)
        
        # Should only return the worst (cha -2)
        self.assertEqual(len(result), 1)
        self.assertIn("charisma", result)
    
    def test_no_negative_modifiers(self):
        """Test with no negative modifiers."""
        mods = {"str": 1, "con": 0, "dex": 0, "int": 0, "wis": 0, "cha": 0}
        result = _ability_flaws(mods)
        
        self.assertEqual(len(result), 0)


class TestTransform(unittest.TestCase):
    """Test the transform function."""
    
    def test_transform_single_entity(self):
        """Test transforming a single entity."""
        section_data = {
            "title": "Player Character Races",
            "start_page": 10,
            "end_page": 15,
            "pages": [
                {"text": "Human\n\nHumans are versatile and adaptable."}
            ]
        }
        config = {
            "entities": [
                {
                    "name": "Human",
                    "slug": "human",
                    "aliases": [],
                    "heading": "Human",
                    "ability_mods": {"str": 0, "dex": 0, "con": 0, "int": 0, "wis": 0, "cha": 0},
                    "size": "medium",
                    "hit_points": 8,
                    "speed": 25,
                    "languages": ["Common"],
                    "traits": ["Human", "Humanoid"],
                    "heritages": [],
                    "features": []
                }
            ]
        }
        
        result = transform(section_data, config)
        
        self.assertEqual(result["entity_type"], "ancestry")
        self.assertEqual(len(result["entities"]), 1)
        
        entity = result["entities"][0]
        self.assertEqual(entity["name"], "Human")
        self.assertEqual(entity["slug"], "human")
        self.assertIn("versatile", entity["description"].lower())
        self.assertEqual(entity["source_section"], "Player Character Races")
        self.assertEqual(entity["source_pages"], [10, 15])
        
        # Check PF2E data
        pf2e = entity["pf2e"]
        self.assertEqual(pf2e["size"], "medium")
        self.assertEqual(pf2e["hit_points"], 8)
        self.assertEqual(pf2e["speed"], 25)
        self.assertIn("Common", pf2e["languages"])
        self.assertIn("free", pf2e["boosts"])
    
    def test_transform_multiple_entities(self):
        """Test transforming multiple entities."""
        section_data = {
            "title": "Races",
            "start_page": 1,
            "end_page": 10,
            "pages": [
                {"text": "Dwarf\n\nDwarves are strong.\n\nElf\n\nElves are agile."}
            ]
        }
        config = {
            "entities": [
                {
                    "name": "Dwarf",
                    "slug": "dwarf",
                    "aliases": [],
                    "heading": "Dwarf",
                    "ability_mods": {"str": 2, "con": 2, "dex": 0, "int": 0, "wis": 1, "cha": -1},
                    "size": "medium",
                    "hit_points": 10,
                    "speed": 20,
                    "languages": ["Common", "Dwarven"],
                    "traits": ["Dwarf", "Humanoid"],
                    "heritages": [],
                    "features": []
                },
                {
                    "name": "Elf",
                    "slug": "elf",
                    "aliases": [],
                    "heading": "Elf",
                    "ability_mods": {"str": 0, "con": -1, "dex": 2, "int": 1, "wis": 0, "cha": 0},
                    "size": "medium",
                    "hit_points": 6,
                    "speed": 30,
                    "languages": ["Common", "Elven"],
                    "traits": ["Elf", "Humanoid"],
                    "heritages": [],
                    "features": []
                }
            ]
        }
        
        result = transform(section_data, config)
        
        self.assertEqual(len(result["entities"]), 2)
        
        # Check Dwarf
        dwarf = next(e for e in result["entities"] if e["name"] == "Dwarf")
        self.assertIn("strong", dwarf["description"].lower())
        self.assertIn("strength", dwarf["pf2e"]["boosts"])
        self.assertIn("constitution", dwarf["pf2e"]["boosts"])
        self.assertIn("charisma", dwarf["pf2e"]["flaws"])
        
        # Check Elf
        elf = next(e for e in result["entities"] if e["name"] == "Elf")
        self.assertIn("agile", elf["description"].lower())
        self.assertIn("dexterity", elf["pf2e"]["boosts"])
        self.assertIn("constitution", elf["pf2e"]["flaws"])
    
    def test_transform_with_metadata(self):
        """Test that metadata is properly included."""
        section_data = {
            "title": "Races",
            "start_page": 1,
            "end_page": 5,
            "pages": [
                {"text": "Mul\n\nMuls are strong hybrids."}
            ]
        }
        config = {
            "entities": [
                {
                    "name": "Mul",
                    "slug": "mul",
                    "aliases": ["Muls", "Half-Dwarf"],
                    "heading": "Mul",
                    "ability_mods": {"str": 2, "con": 1, "dex": 0, "int": 0, "wis": 0, "cha": 0},
                    "size": "medium",
                    "hit_points": 10,
                    "speed": 25,
                    "languages": ["Common"],
                    "traits": ["Mul", "Humanoid"],
                    "heritages": [],
                    "features": ["Tireless"],
                    "notes": "Sterile hybrid race"
                }
            ]
        }
        
        result = transform(section_data, config)
        
        entity = result["entities"][0]
        self.assertIn("Muls", entity["metadata"]["aliases"])
        self.assertIn("Half-Dwarf", entity["metadata"]["aliases"])
        self.assertEqual(entity["metadata"]["notes"], "Sterile hybrid race")
        self.assertIn("Tireless", entity["pf2e"]["additional_features"])


if __name__ == "__main__":
    unittest.main()

