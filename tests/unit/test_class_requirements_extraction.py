"""
Unit tests for class requirements table extraction.

These tests validate that the extraction logic correctly identifies and structures
class requirements blocks for all player classes in Chapter 3.
"""

import pytest
from tools.pdf_pipeline.transformers.chapter_3.common import (
    parse_class_ability_requirements,
    extract_class_ability_table,
)


class TestParseClassAbilityRequirements:
    """Test the parsing of class ability requirements text into structured rows."""
    
    def test_fighter_requirements(self):
        """Test Fighter ability requirements parsing."""
        text = "Ability Requirements: Strength 9 Prime Requisite: Strength Allowed Races: All"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Strength 9")
        assert rows[1] == ("Prime Requisite:", "Strength")
        assert rows[2] == ("Races Allowed:", "All")
    
    def test_gladiator_requirements(self):
        """Test Gladiator ability requirements parsing."""
        text = "Ability Requirements: Strength 13 Dexterity 12 Constitution 15 Prime Requisite: Strength Allowed Races: All"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Strength 13 Dexterity 12 Constitution 15")
        assert rows[1] == ("Prime Requisite:", "Strength")
        assert rows[2] == ("Races Allowed:", "All")
    
    def test_ranger_requirements(self):
        """Test Ranger ability requirements parsing with multiple prime requisites."""
        text = "Ability Requirements: Strength 13 Dexterity 13 Constitution 14 Wisdom 14 Prime Requisites: Strength, Dexterity, Wisdom Races Allowed: Human, Elf, Half-elf, Halfling, Thri-kreen"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Strength 13 Dexterity 13 Constitution 14 Wisdom 14")
        assert rows[1] == ("Prime Requisite:", "Strength, Dexterity, Wisdom")
        assert rows[2] == ("Races Allowed:", "Human, Elf, Half-elf, Halfling, Thri-kreen")
    
    def test_bard_requirements(self):
        """Test Bard ability requirements parsing with multiple abilities and prime requisites."""
        text = "Ability Requirements: Dexterity 12 Intelligence 13 Charisma 15 Prime Requisites: Dexterity, Charisma Races Allowed: Human, Half-elf"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Dexterity 12 Intelligence 13 Charisma 15")
        assert rows[1] == ("Prime Requisite:", "Dexterity, Charisma")
        assert rows[2] == ("Races Allowed:", "Human, Half-elf")
    
    def test_druid_requirements(self):
        """Test Druid ability requirements parsing with unusual race list."""
        text = "Ability Requirements: Wisdom 12 Charisma 15 Prime Requisites: Wisdom, Charisma Races Allowed: Human, Half-elf, Halfling, mul, Thri-kreen"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Wisdom 12 Charisma 15")
        assert rows[1] == ("Prime Requisite:", "Wisdom, Charisma")
        assert rows[2] == ("Races Allowed:", "Human, Half-elf, Halfling, mul, Thri-kreen")
    
    def test_psionicist_requirements(self):
        """Test Psionicist ability requirements parsing with 'Any' races."""
        text = "Ability Requirements: Constitution 11 Intelligence 12 Wisdom 15 Prime Requisites: Constitution, Wisdom Races Allowed: Any"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Constitution 11 Intelligence 12 Wisdom 15")
        assert rows[1] == ("Prime Requisite:", "Constitution, Wisdom")
        assert rows[2] == ("Races Allowed:", "Any")
    
    def test_templar_requirements(self):
        """Test Templar ability requirements parsing."""
        text = "Ability Requirements: Wisdom 3 Intelligence 10 Prime Requisite: Wisdom Races Allowed: Human, Dwarf, Elf, Half-elf"
        rows = parse_class_ability_requirements(text)
        
        assert len(rows) == 3
        assert rows[0] == ("Ability Requirements:", "Wisdom 3 Intelligence 10")
        assert rows[1] == ("Prime Requisite:", "Wisdom")
        assert rows[2] == ("Races Allowed:", "Human, Dwarf, Elf, Half-elf")


class TestExtractClassAbilityTable:
    """Test the extraction of class ability tables from page blocks."""
    
    def test_fighter_extraction(self):
        """Test that Fighter requirements are extracted and formatted as a table."""
        # Create a mock page with Fighter requirements in a single block
        page = {
            "blocks": [
                {
                    "type": "text",
                    "bbox": [56.0, 100.0, 300.0, 120.0],
                    "lines": [
                        {
                            "bbox": [56.0, 100.0, 300.0, 120.0],
                            "spans": [
                                {
                                    "text": "Fighter Ability Requirements: Strength 9 Prime Requisite: Strength Allowed Races: All",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_class_ability_table(page, "Fighter")
        
        # Should successfully extract and create table
        assert result is True
        assert "tables" in page
        assert len(page["tables"]) == 1
        
        table = page["tables"][0]
        assert len(table["rows"]) == 3
        
        # Check table content
        assert table["rows"][0]["cells"][0]["text"] == "Ability Requirements:"
        assert table["rows"][0]["cells"][1]["text"] == "Strength 9"
        assert table["rows"][1]["cells"][0]["text"] == "Prime Requisite:"
        assert table["rows"][1]["cells"][1]["text"] == "Strength"
        assert table["rows"][2]["cells"][0]["text"] == "Races Allowed:"
        assert table["rows"][2]["cells"][1]["text"] == "All"
    
    def test_gladiator_extraction_separate_blocks(self):
        """Test that Gladiator requirements are extracted when class name and requirements are in separate blocks."""
        # Create a mock page with Gladiator as a separate header block
        page = {
            "blocks": [
                {
                    "type": "text",
                    "bbox": [56.0, 80.0, 200.0, 95.0],
                    "lines": [
                        {
                            "bbox": [56.0, 80.0, 200.0, 95.0],
                            "spans": [
                                {
                                    "text": "Gladiator",
                                    "font": "MSTT31c501",
                                    "size": 10.8,
                                    "color": "#ca5804"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "bbox": [56.0, 100.0, 300.0, 115.0],
                    "lines": [
                        {
                            "bbox": [56.0, 100.0, 300.0, 115.0],
                            "spans": [
                                {
                                    "text": "Ability Requirements: Strength 13",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "bbox": [56.0, 116.0, 300.0, 131.0],
                    "lines": [
                        {
                            "bbox": [56.0, 116.0, 300.0, 131.0],
                            "spans": [
                                {
                                    "text": "Dexterity 12 Constitution 15",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "bbox": [56.0, 132.0, 300.0, 147.0],
                    "lines": [
                        {
                            "bbox": [56.0, 132.0, 300.0, 147.0],
                            "spans": [
                                {
                                    "text": "Prime Requisite: Strength",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "bbox": [56.0, 148.0, 300.0, 163.0],
                    "lines": [
                        {
                            "bbox": [56.0, 148.0, 300.0, 163.0],
                            "spans": [
                                {
                                    "text": "Allowed Races: All",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = extract_class_ability_table(page, "Gladiator")
        
        # Should successfully extract and create table
        assert result is True
        assert "tables" in page
        assert len(page["tables"]) == 1
        
        table = page["tables"][0]
        assert len(table["rows"]) == 3
        
        # Check table content
        assert table["rows"][0]["cells"][0]["text"] == "Ability Requirements:"
        assert "Strength 13" in table["rows"][0]["cells"][1]["text"]
        assert "Dexterity 12" in table["rows"][0]["cells"][1]["text"]
        assert "Constitution 15" in table["rows"][0]["cells"][1]["text"]


class TestAllPlayerClasses:
    """Test that all expected player classes are covered."""
    
    def test_all_player_classes_list(self):
        """Verify that all player classes are in the requirements extraction list."""
        from tools.pdf_pipeline.transformers.chapter_3.class_requirements import (
            PLAYER_CLASSES_WITH_REQUIREMENTS
        )
        
        expected_classes = [
            # Warriors
            "Fighter", "Gladiator", "Ranger",
            # Wizards
            "Defiler", "Preserver", "Illusionist",
            # Priests
            "Cleric", "Druid", "Templar",
            # Rogues
            "Bard", "Thief",
            # Psionicist
            "Psionicist"
        ]
        
        assert len(PLAYER_CLASSES_WITH_REQUIREMENTS) == len(expected_classes)
        for expected_class in expected_classes:
            assert expected_class in PLAYER_CLASSES_WITH_REQUIREMENTS, \
                f"Missing player class: {expected_class}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

