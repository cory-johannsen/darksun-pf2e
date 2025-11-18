"""
Unit tests for Chapter 13 processing.
"""

import unittest
from unittest.mock import Mock
from tools.pdf_pipeline.transformers.chapter_13_processing import (
    apply_chapter_13_adjustments,
    _merge_intro_paragraphs,
    _mark_visibility_ranges_as_h2,
    _extract_visibility_table
)


class TestChapter13Processing(unittest.TestCase):
    """Test Chapter 13 processing functions."""
    
    def test_merge_intro_paragraphs(self):
        """Test merging of intro paragraphs."""
        # Create test data with left and right column text
        section_data = {
            "pages": [{
                "blocks": [
                    {
                        "bbox": [50, 171, 289, 194],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [60, 171, 289, 180],
                                "spans": [{"text": "All of the conditions presented on the Visibility"}]
                            },
                            {
                                "bbox": [50, 185, 288, 194],
                                "spans": [{"text": "Ranges table in the Player's Handbook exist on"}]
                            }
                        ]
                    },
                    {
                        "bbox": [313, 171, 551, 194],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [313, 171, 551, 180],
                                "spans": [{"text": "Athas. However, there are a number of conditions"}]
                            },
                            {
                                "bbox": [313, 185, 495, 194],
                                "spans": [{"text": "unique to Athas that should be added."}]
                            }
                        ]
                    }
                ]
            }]
        }
        
        _merge_intro_paragraphs(section_data["pages"])
        
        # Check that the first block now has all lines
        first_block = section_data["pages"][0]["blocks"][0]
        self.assertEqual(len(first_block["lines"]), 4)
        
        # Check that the second block has been zeroed out
        second_block = section_data["pages"][0]["blocks"][1]
        self.assertEqual(second_block["bbox"], [0.0, 0.0, 0.0, 0.0])
    
    def test_mark_visibility_ranges_as_h2(self):
        """Test marking of 'Dark Sun Visibility Ranges' as H2."""
        section_data = {
            "pages": [{
                "blocks": [
                    {
                        "bbox": [50, 210, 179, 221],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [50, 210, 179, 221],
                                "spans": [
                                    {
                                        "text": "Dark Sun Visibility Ranges",
                                        "font": "MSTT31c501",
                                        "size": 10.8,
                                        "color": "#ca5804"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }]
        }
        
        _mark_visibility_ranges_as_h2(section_data["pages"])
        
        # Check that the span was marked as H2
        span = section_data["pages"][0]["blocks"][0]["lines"][0]["spans"][0]
        self.assertTrue(span.get("is_h2", False))
        self.assertEqual(span["size"], 12.0)
    
    def test_extract_visibility_table(self):
        """Test extraction of visibility table data."""
        # Create test data with table elements
        section_data = {
            "pages": [{
                "blocks": [
                    {
                        "bbox": [49, 232, 252, 253],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [49, 232, 86, 240],
                                "spans": [
                                    {
                                        "text": "Condition",
                                        "color": "#ca5804",
                                        "size": 7.92
                                    }
                                ]
                            },
                            {
                                "bbox": [211, 233, 252, 241],
                                "spans": [
                                    {
                                        "text": "Movement",
                                        "color": "#ca5804",
                                        "size": 7.92
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "bbox": [50, 244, 117, 253],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [50, 244, 117, 253],
                                "spans": [
                                    {
                                        "text": "Sand, blowing",
                                        "color": "#000000",
                                        "size": 8.88
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }]
        }
        
        _extract_visibility_table(section_data["pages"])
        
        # Check that table headers are marked
        condition_span = section_data["pages"][0]["blocks"][0]["lines"][0]["spans"][0]
        self.assertTrue(condition_span.get("is_table_header", False))
        self.assertTrue(condition_span.get("skip_render", False))
        
        movement_span = section_data["pages"][0]["blocks"][0]["lines"][1]["spans"][0]
        self.assertTrue(movement_span.get("is_table_header", False))
        self.assertTrue(movement_span.get("skip_render", False))
        
        # Check that condition values are marked
        sand_span = section_data["pages"][0]["blocks"][1]["lines"][0]["spans"][0]
        self.assertTrue(sand_span.get("is_table_data", False))
        self.assertTrue(sand_span.get("skip_render", False))
    
    def test_apply_chapter_13_adjustments(self):
        """Test that all adjustments are applied."""
        section_data = {
            "pages": [{
                "blocks": [
                    {
                        "bbox": [50, 171, 289, 194],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [60, 171, 289, 180],
                                "spans": [{"text": "All of the conditions presented"}]
                            }
                        ]
                    },
                    {
                        "bbox": [313, 171, 551, 194],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [313, 171, 551, 180],
                                "spans": [{"text": "Athas. However, there are"}]
                            }
                        ]
                    },
                    {
                        "bbox": [50, 210, 179, 221],
                        "type": "text",
                        "lines": [
                            {
                                "bbox": [50, 210, 179, 221],
                                "spans": [
                                    {
                                        "text": "Dark Sun Visibility Ranges",
                                        "size": 10.8,
                                        "color": "#ca5804"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }]
        }
        
        apply_chapter_13_adjustments(section_data)
        
        # Check that adjustments were applied
        self.assertTrue(section_data.get("__chapter_13_adjusted", False))
    
    def test_apply_chapter_13_adjustments_idempotent(self):
        """Test that adjustments are not applied twice."""
        section_data = {
            "__chapter_13_adjusted": True,
            "pages": []
        }
        
        # Should not raise error and should not process
        apply_chapter_13_adjustments(section_data)
        
        # Still marked as adjusted
        self.assertTrue(section_data.get("__chapter_13_adjusted", False))


if __name__ == "__main__":
    unittest.main()

