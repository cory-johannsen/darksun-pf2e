"""
Unit tests for Chapter 8 processing (Experience tables).
"""

import unittest
from tools.pdf_pipeline.transformers import chapter_8_processing


class TestChapter8Processing(unittest.TestCase):
    
    def test_is_class_award_header(self):
        """Test identification of class award headers."""
        self.assertTrue(chapter_8_processing._is_class_award_header("All Warriors:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Fighter:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Gladiator:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Ranger:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("All Wizards:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Preserver:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Defiler:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("All Priests:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Cleric:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Druid:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Templar:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("All Rogues:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Thief:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Bard:"))
        self.assertTrue(chapter_8_processing._is_class_award_header("Psionicist:"))
        
        # Negative cases
        self.assertFalse(chapter_8_processing._is_class_award_header("Fighter"))
        self.assertFalse(chapter_8_processing._is_class_award_header("Some Other Text"))
        self.assertFalse(chapter_8_processing._is_class_award_header("Action"))
        self.assertFalse(chapter_8_processing._is_class_award_header("Awards"))
    
    def test_is_column_header(self):
        """Test identification of column headers."""
        self.assertTrue(chapter_8_processing._is_column_header("Action"))
        self.assertTrue(chapter_8_processing._is_column_header("Awards"))
        self.assertTrue(chapter_8_processing._is_column_header("  Action  "))
        self.assertTrue(chapter_8_processing._is_column_header("  Awards  "))
        
        # Negative cases
        self.assertFalse(chapter_8_processing._is_column_header("Fighter:"))
        self.assertFalse(chapter_8_processing._is_column_header("10 XP/level"))
    
    def test_is_xp_value(self):
        """Test identification of XP values."""
        # Various XP formats
        self.assertTrue(chapter_8_processing._is_xp_value("10 XP/level"))
        self.assertTrue(chapter_8_processing._is_xp_value("50 XP/day"))
        self.assertTrue(chapter_8_processing._is_xp_value("5 XP/spell level"))
        self.assertTrue(chapter_8_processing._is_xp_value("100 XP"))
        self.assertTrue(chapter_8_processing._is_xp_value("XP value"))
        self.assertTrue(chapter_8_processing._is_xp_value("10 XP/cp value"))
        self.assertTrue(chapter_8_processing._is_xp_value("15 XP / PSP"))
        self.assertTrue(chapter_8_processing._is_xp_value("500 XP x level"))
        self.assertTrue(chapter_8_processing._is_xp_value("Hit Dice"))
        
        # Negative cases
        self.assertFalse(chapter_8_processing._is_xp_value("Fighter:"))
        self.assertFalse(chapter_8_processing._is_xp_value("Action"))
        self.assertFalse(chapter_8_processing._is_xp_value("Stand commanded in combat"))
    
    def test_class_award_headers_list(self):
        """Test that all 15 class award headers are defined."""
        headers = chapter_8_processing.CLASS_AWARD_HEADERS
        self.assertEqual(len(headers), 15)
        self.assertIn("All Warriors:", headers)
        self.assertIn("Fighter:", headers)
        self.assertIn("Gladiator:", headers)
        self.assertIn("Ranger:", headers)
        self.assertIn("All Wizards:", headers)
        self.assertIn("Preserver:", headers)
        self.assertIn("Defiler:", headers)
        self.assertIn("All Priests:", headers)
        self.assertIn("Cleric:", headers)
        self.assertIn("Druid:", headers)
        self.assertIn("Templar:", headers)
        self.assertIn("All Rogues:", headers)
        self.assertIn("Thief:", headers)
        self.assertIn("Bard:", headers)
        self.assertIn("Psionicist:", headers)
    
    def test_extract_class_award_tables_mock(self):
        """Test table extraction with mock data."""
        # Create mock section data
        section_data = {
            "pages": [
                {
                    "blocks": [
                        {
                            "type": "text",
                            "bbox": [0, 0, 100, 20],
                            "lines": [{
                                "spans": [{
                                    "text": "Individual Class Awards",
                                    "font": "MSTT31c501",
                                    "size": 14.88,
                                    "color": "#ca5804",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [0, 30, 100, 40],
                            "lines": [{
                                "spans": [{
                                    "text": "All Warriors:",
                                    "font": "MSTT31c5c6",
                                    "size": 8.88,
                                    "color": "#ca5804",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [0, 50, 100, 60],
                            "lines": [{
                                "spans": [{
                                    "text": "Per Hit Die of creature defeated",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [200, 50, 300, 60],
                            "lines": [{
                                "spans": [{
                                    "text": "10 XP/level",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [0, 100, 100, 110],
                            "lines": [{
                                "spans": [{
                                    "text": "Individual Race Awards",
                                    "font": "MSTT31c501",
                                    "size": 14.88,
                                    "color": "#ca5804",
                                }]
                            }]
                        },
                    ]
                }
            ]
        }
        
        # Apply processing
        chapter_8_processing.apply_chapter_8_adjustments(section_data)
        
        # Verify that table markers were added
        blocks = section_data["pages"][0]["blocks"]
        table_blocks = [b for b in blocks if b.get("__class_award_table")]
        
        self.assertGreater(len(table_blocks), 0, "Should have at least one table marker")
        
        # Check first table
        table = table_blocks[0]
        self.assertEqual(table["__table_header"], "All Warriors:")
        self.assertGreater(len(table["__table_rows"]), 0)
    
    def test_clean_xp_text(self):
        """Test XP text whitespace cleanup."""
        # Test cases from the Psionicist table and others
        self.assertEqual(chapter_8_processing._clean_xp_text("1 0  X P / P S P"), "10 XP/PSP")
        self.assertEqual(chapter_8_processing._clean_xp_text("1 5  X P / P S P"), "15 XP/PSP")
        self.assertEqual(chapter_8_processing._clean_xp_text("2 0 0  X P"), "200 XP")
        self.assertEqual(chapter_8_processing._clean_xp_text("7 5 0  X P"), "750 XP")
        self.assertEqual(chapter_8_processing._clean_xp_text("500 XP x level"), "500 XP x level")
        self.assertEqual(chapter_8_processing._clean_xp_text("100 XP/level or Hit Dice"), "100 XP/level or Hit Dice")
        
        # Already clean text should remain unchanged
        self.assertEqual(chapter_8_processing._clean_xp_text("10 XP/level"), "10 XP/level")
        self.assertEqual(chapter_8_processing._clean_xp_text("50 XP/day"), "50 XP/day")
    
    def test_psionicist_table_extraction(self):
        """Test that Psionicist table is properly extracted with all 4 rows."""
        # Create mock section data with Psionicist table structure
        # Simulating the actual PDF structure with split text and whitespace issues
        section_data = {
            "pages": [
                {
                    "blocks": [
                        {
                            "type": "text",
                            "bbox": [42.0, 100.0, 400.0, 120.0],
                            "lines": [{
                                "bbox": [42.0, 100.0, 400.0, 120.0],
                                "spans": [{
                                    "text": "Individual Class Awards",
                                    "font": "MSTT31c501",
                                    "size": 14.88,
                                    "color": "#ca5804",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [38.64, 153.01, 82.50, 161.90],
                            "lines": [{
                                "bbox": [38.64, 153.01, 82.50, 161.90],
                                "spans": [{
                                    "text": "Psionicist:",
                                    "font": "MSTT31c5c6",
                                    "size": 8.88,
                                    "color": "#ca5804",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [38.88, 165.01, 175.41, 173.89],
                            "lines": [{
                                "bbox": [38.88, 165.01, 175.41, 173.89],
                                "spans": [{
                                    "text": "Psionics used to defeat foe or",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [220.56, 177.97, 276.97, 186.85],
                            "lines": [{
                                "bbox": [220.56, 177.97, 276.97, 186.85],
                                "spans": [{
                                    "text": "1 0  X P / P S P",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [39.12, 178.93, 78.21, 187.81],
                            "lines": [{
                                "bbox": [39.12, 178.93, 78.21, 187.81],
                                "spans": [{
                                    "text": "problem",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [38.88, 191.89, 179.79, 200.77],
                            "lines": [{
                                "bbox": [38.88, 191.89, 179.79, 200.77],
                                "spans": [{
                                    "text": "Psionics used to avoid combat",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [220.32, 191.41, 276.97, 200.29],
                            "lines": [{
                                "bbox": [220.32, 191.41, 276.97, 200.29],
                                "spans": [{
                                    "text": "1 5  X P / P S P",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [217.20, 205.09, 277.36, 213.97],
                            "lines": [{
                                "bbox": [217.20, 205.09, 277.36, 213.97],
                                "spans": [{
                                    "text": "100 XP/level",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [38.88, 205.57, 162.04, 214.45],
                            "lines": [{
                                "bbox": [38.88, 205.57, 162.04, 214.45],
                                "spans": [{
                                    "text": "Psionic opponent defeated",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [223.92, 218.53, 277.41, 227.41],
                            "lines": [{
                                "bbox": [223.92, 218.53, 277.41, 227.41],
                                "spans": [{
                                    "text": "or Hit Dice",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [38.88, 232.21, 128.73, 241.09],
                            "lines": [{
                                "bbox": [38.88, 232.21, 128.73, 241.09],
                                "spans": [{
                                    "text": "Create psionic item",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [210.24, 231.97, 277.14, 240.85],
                            "lines": [{
                                "bbox": [210.24, 231.97, 277.14, 240.85],
                                "spans": [{
                                    "text": "500 XP x level",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                        {
                            "type": "text",
                            "bbox": [0, 250, 100, 260],
                            "lines": [{
                                "bbox": [0, 250, 100, 260],
                                "spans": [{
                                    "text": "*Footnote marker",
                                    "font": "MSTT31c50d",
                                    "size": 8.88,
                                    "color": "#000000",
                                }]
                            }]
                        },
                    ]
                }
            ]
        }
        
        # Apply processing
        chapter_8_processing.apply_chapter_8_adjustments(section_data)
        
        # Verify that Psionicist table was extracted
        blocks = section_data["pages"][0]["blocks"]
        table_blocks = [b for b in blocks if b.get("__class_award_table")]
        
        # Find Psionicist table
        psionicist_table = None
        for table in table_blocks:
            if table.get("__table_header") == "Psionicist:":
                psionicist_table = table
                break
        
        self.assertIsNotNone(psionicist_table, "Psionicist table should be extracted")
        
        # Verify all 4 rows
        rows = psionicist_table.get("__table_rows", [])
        self.assertEqual(len(rows), 4, "Psionicist table should have 4 rows")
        
        # Verify row contents and whitespace cleanup
        # Row 1: Psionics used to defeat foe or problem | 10 XP/PSP
        self.assertIn("defeat foe or problem", rows[0][0])
        self.assertEqual(rows[0][1], "10 XP/PSP", "First award should have whitespace cleaned up")
        
        # Row 2: Psionics used to avoid combat | 15 XP/PSP
        self.assertIn("avoid combat", rows[1][0])
        self.assertEqual(rows[1][1], "15 XP/PSP", "Second award should have whitespace cleaned up")
        
        # Row 3: Psionic opponent defeated | 100 XP/level or Hit Dice
        self.assertIn("opponent defeated", rows[2][0])
        self.assertIn("100 XP/level", rows[2][1])
        self.assertIn("Hit Dice", rows[2][1])
        
        # Row 4: Create psionic item | 500 XP x level
        self.assertIn("Create psionic item", rows[3][0])
        self.assertEqual(rows[3][1], "500 XP x level")


if __name__ == "__main__":
    unittest.main()

