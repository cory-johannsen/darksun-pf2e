"""
Test for substring not found errors in journal_lib/rendering.py

These tests identify and fix ValueError issues when using .index() without checking
if the substring exists first.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestSubstringNotFoundBug(unittest.TestCase):
    """Test case for substring not found bugs in rendering.py"""
    
    def test_merge_lines_handles_missing_rarely_pattern(self):
        """Test that merge_lines doesn't crash when '. Rarely' pattern is absent.
        
        This reproduces the bug where code calls .index() on a substring that
        doesn't exist, causing ValueError: substring not found
        """
        from tools.pdf_pipeline.transformers.journal_lib.rendering import merge_lines
        
        # Create test lines with __split_at_rarely flag but without the pattern
        test_lines = [
            {
                "bbox": [50, 100, 200, 120],
                "__split_at_rarely": True,
                "spans": [
                    {
                        "text": "This text does not contain the expected pattern.",
                        "font": "TestFont",
                        "size": 10,
                        "color": "#000000",
                    }
                ]
            }
        ]
        
        # This should not raise ValueError
        try:
            result = merge_lines(test_lines)
            self.assertIsInstance(result, list, "merge_lines should return a list")
        except ValueError as e:
            if "substring not found" in str(e):
                self.fail(f"ValueError when pattern is missing: {e}")
            raise
    
    def test_merge_lines_handles_missing_also_pattern(self):
        """Test that merge_lines doesn't crash when '. Also' pattern is absent."""
        from tools.pdf_pipeline.transformers.journal_lib.rendering import merge_lines
        
        test_lines = [
            {
                "bbox": [50, 100, 200, 120],
                "__split_at_also": True,
                "spans": [
                    {
                        "text": "This text does not contain the also pattern.",
                        "font": "TestFont",
                        "size": 10,
                        "color": "#000000",
                    }
                ]
            }
        ]
        
        try:
            result = merge_lines(test_lines)
            self.assertIsInstance(result, list, "merge_lines should return a list")
        except ValueError as e:
            if "substring not found" in str(e):
                self.fail(f"ValueError when '. Also' pattern is missing: {e}")
            raise
    
    def test_merge_adjacent_paragraph_html_handles_malformed_content(self):
        """Test that merge_adjacent_paragraph_html handles content without closing tags."""
        from tools.pdf_pipeline.transformers.journal_lib.rendering import merge_adjacent_paragraph_html
        
        # Test with paragraph content that doesn't have proper closing tag
        test_html = '<p data-test="true">Some content without proper structure'
        
        try:
            result = merge_adjacent_paragraph_html(test_html)
            self.assertIsInstance(result, str, "Should return a string")
        except ValueError as e:
            if "substring not found" in str(e) or ">' not in" in str(e):
                self.fail(f"ValueError when handling malformed HTML: {e}")
            raise
    
    def test_collect_cells_from_blocks_has_normalize_plain_text(self):
        """Test that collect_cells_from_blocks has access to _normalize_plain_text."""
        from tools.pdf_pipeline.transformers.journal_lib.blocks import collect_cells_from_blocks
        
        # Create test page with blocks
        test_page = {
            "blocks": [
                {
                    "lines": [
                        {
                            "bbox": [50, 100, 200, 120],
                            "spans": [
                                {
                                    "text": "Test content",
                                    "font": "TestFont",
                                    "size": 10,
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        try:
            result = collect_cells_from_blocks(test_page, [0])
            self.assertIsInstance(result, list, "Should return a list")
            if result:
                self.assertIn("text", result[0], "Cells should have text field")
        except NameError as e:
            if "_normalize_plain_text" in str(e):
                self.fail(f"NameError: _normalize_plain_text not accessible in blocks.py: {e}")
            raise


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

