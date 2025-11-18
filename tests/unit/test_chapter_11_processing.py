"""
Unit tests for Chapter 11 processing (Encounters)

Tests the merging of "Wizard, Priest, and Psionicist" and "Encounters" headers
and paragraph break functionality.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "tools" / "pdf_pipeline"))

from transformers import chapter_11_processing


class TestChapter11Processing(unittest.TestCase):
    """Test Chapter 11 processing functions"""
    
    def test_merge_wizard_priest_encounters_headers(self):
        """Test that the two-line header is merged into a single line"""
        # Create test data that mimics the structure from the PDF
        section_data = {
            "slug": "chapter-eleven-encounters",
            "pages": [
                {
                    "page_number": 79,
                    "blocks": [
                        # This is the block we want to merge
                        {
                            "bbox": [35.5, 269.6, 238.2, 299.9],
                            "type": "text",
                            "lines": [
                                {
                                    "bbox": [36.0, 269.6, 238.2, 284.5],
                                    "spans": [
                                        {
                                            "text": "Wizard, Priest, and Psionicist",
                                            "font": "MSTT31c501",
                                            "size": 14.88,
                                            "flags": 4,
                                            "color": "#ca5804"
                                        }
                                    ]
                                },
                                {
                                    "bbox": [35.5, 285.0, 107.9, 299.9],
                                    "spans": [
                                        {
                                            "text": "Encounters",
                                            "font": "MSTT31c501",
                                            "size": 14.88,
                                            "flags": 4,
                                            "color": "#ca5804"
                                        }
                                    ]
                                }
                            ]
                        },
                        # Another block (shouldn't be touched)
                        {
                            "bbox": [36.0, 305.4, 275.2, 314.3],
                            "type": "text",
                            "lines": [
                                {
                                    "bbox": [36.0, 305.4, 275.2, 314.3],
                                    "spans": [
                                        {
                                            "text": "Spellcasters and psionicists pose problems",
                                            "font": "MSTT31c50d",
                                            "size": 8.88
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Apply the processing
        chapter_11_processing.apply_chapter_11_adjustments(section_data)
        
        # Check that the first block now has only one line
        block = section_data["pages"][0]["blocks"][0]
        self.assertEqual(len(block["lines"]), 1, 
                        "Block should have only one line after merging")
        
        # Check that the merged text is correct
        merged_text = block["lines"][0]["spans"][0]["text"]
        self.assertEqual(merged_text, "Wizard, Priest, and Psionicist Encounters",
                        f"Merged text should be 'Wizard, Priest, and Psionicist Encounters', got '{merged_text}'")
        
        # Check that the bbox was updated to encompass both original lines
        self.assertAlmostEqual(block["bbox"][3], 299.9, places=1,
                              msg="Block bbox should be updated to include second line")
        
        # Check that the second block was not modified
        second_block = section_data["pages"][0]["blocks"][1]
        self.assertEqual(len(second_block["lines"]), 1,
                        "Second block should still have one line")
        self.assertIn("Spellcasters", second_block["lines"][0]["spans"][0]["text"],
                     "Second block text should be unchanged")
    
    def test_no_merge_if_header_not_found(self):
        """Test that processing doesn't fail if the header is not found"""
        # Create test data without the target header
        section_data = {
            "slug": "chapter-eleven-encounters",
            "pages": [
                {
                    "page_number": 79,
                    "blocks": [
                        {
                            "bbox": [36.0, 150.4, 275.0, 161.1],
                            "type": "text",
                            "lines": [
                                {
                                    "bbox": [36.0, 150.4, 275.0, 161.1],
                                    "spans": [
                                        {
                                            "text": "Some other text",
                                            "font": "MSTT31c50d",
                                            "size": 8.88
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Apply the processing (should not crash)
        chapter_11_processing.apply_chapter_11_adjustments(section_data)
        
        # Check that the block was not modified
        block = section_data["pages"][0]["blocks"][0]
        self.assertEqual(len(block["lines"]), 1,
                        "Block should still have one line")
        self.assertEqual(block["lines"][0]["spans"][0]["text"], "Some other text",
                        "Block text should be unchanged")
    
    def test_get_line_text(self):
        """Test the helper function for extracting text from a line"""
        # Test with single span
        line = {
            "spans": [
                {"text": "Hello World"}
            ]
        }
        self.assertEqual(chapter_11_processing._get_line_text(line), "Hello World")
        
        # Test with multiple spans
        line = {
            "spans": [
                {"text": "Hello "},
                {"text": "World"}
            ]
        }
        self.assertEqual(chapter_11_processing._get_line_text(line), "Hello World")
        
        # Test with empty spans
        line = {
            "spans": []
        }
        self.assertEqual(chapter_11_processing._get_line_text(line), "")
        
        # Test with missing text keys
        line = {
            "spans": [
                {},
                {"text": "World"}
            ]
        }
        self.assertEqual(chapter_11_processing._get_line_text(line), "World")
    
    def test_wizard_priest_psionicist_paragraph_breaks(self):
        """Test paragraph break marking in Wizard, Priest, and Psionicist Encounters section"""
        section_data = {
            "slug": "chapter-eleven-encounters",
            "pages": [
                {
                    "page_number": 79,
                    "blocks": [
                        # Header block
                        {
                            "type": "text",
                            "lines": [
                                {
                                    "spans": [
                                        {"text": "Wizard, Priest, and Psionicist Encounters"}
                                    ]
                                }
                            ]
                        },
                        # Content block with paragraph break
                        {
                            "type": "text",
                            "lines": [
                                {
                                    "spans": [{"text": "Spellcasters and psionicists pose problems. "}]
                                },
                                {
                                    "spans": [{"text": "At times, an encounter with a large group calls for multiple casters."}]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Apply the processing
        chapter_11_processing.apply_chapter_11_adjustments(section_data)
        
        # Check that the line starting with "At times," was marked
        content_block = section_data["pages"][0]["blocks"][1]
        at_times_line = content_block["lines"][1]
        
        self.assertTrue(at_times_line.get("__force_line_break"),
                       "Line starting with 'At times,' should be marked for line break")
    
    def test_city_states_paragraph_breaks(self):
        """Test paragraph break marking in Encounters in City-States section"""
        section_data = {
            "slug": "chapter-eleven-encounters",
            "pages": [
                {
                    "page_number": 79,
                    "blocks": [
                        # Header block
                        {
                            "type": "text",
                            "lines": [
                                {
                                    "spans": [
                                        {"text": "Encounters in City-States"}
                                    ]
                                }
                            ]
                        },
                        # First content block with "When dealing"
                        {
                            "type": "text",
                            "lines": [
                                {
                                    "spans": [{"text": "Athasian city states are crowded. "}]
                                },
                                {
                                    "spans": [{"text": "When dealing with encounters in a city, ask whom. "}]
                                }
                            ]
                        },
                        # Second content block with "Specific encounters"
                        {
                            "type": "text",
                            "lines": [
                                {
                                    "spans": [{"text": "Specific encounters should be set up by the DM."}]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Apply the processing
        chapter_11_processing.apply_chapter_11_adjustments(section_data)
        
        # Check that line starting with "When dealing" was marked
        first_content_block = section_data["pages"][0]["blocks"][1]
        when_dealing_line = first_content_block["lines"][1]
        
        self.assertTrue(when_dealing_line.get("__force_line_break"),
                       "Line starting with 'When dealing' should be marked for line break")
        
        # Check that line starting with "Specific encounters" was marked
        second_content_block = section_data["pages"][0]["blocks"][2]
        specific_line = second_content_block["lines"][0]
        
        self.assertTrue(specific_line.get("__force_line_break"),
                       "Line starting with 'Specific encounters' should be marked for line break")


if __name__ == "__main__":
    unittest.main()

