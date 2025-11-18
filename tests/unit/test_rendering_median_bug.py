"""
Test for median import bug in journal_lib/rendering.py

This test reproduces the bug where median() is called but not imported.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestMedianImportBug(unittest.TestCase):
    """Test case for the median import bug in rendering.py"""
    
    def test_median_function_is_available_in_rendering(self):
        """Test that median function can be called in rendering module.
        
        This reproduces the bug where median() was used but not imported from statistics.
        """
        from tools.pdf_pipeline.transformers.journal_lib import rendering
        
        # Check that median is available in the module's scope
        # This would fail before the fix because median wasn't imported
        has_median = (
            hasattr(rendering, 'median') or 
            hasattr(rendering, 'statistics') and hasattr(rendering.statistics, 'median')
        )
        self.assertTrue(has_median, 
            "median should be available either directly or via statistics module")
    
    def test_normalize_plain_text_exists_in_rendering(self):
        """Test that normalize_plain_text is accessible in rendering module.
        
        This reproduces the bug where _normalize_plain_text was called but doesn't exist.
        """
        from tools.pdf_pipeline.transformers.journal_lib import rendering
        
        # The function should be available (imported from utilities)
        self.assertTrue(hasattr(rendering, 'normalize_plain_text'),
            "normalize_plain_text should be available in rendering module")
    
    def test_render_line_with_bold_and_italic(self):
        """Test that render_line can process spans without NameErrors.
        
        This exercises the code path that uses _is_bold, _is_italic, and _wrap_span.
        """
        from tools.pdf_pipeline.transformers.journal_lib.rendering import render_line
        
        # Create a minimal test line
        test_line = {
            "bbox": [50, 100, 200, 120],
            "spans": [
                {
                    "text": "Bold text",
                    "font": "TestFont-Bold",
                    "size": 10,
                    "color": "#000000",
                    "flags": 16,  # Bold flag
                }
            ]
        }
        
        # This should not raise NameError about _is_bold, _is_italic, or _wrap_span
        try:
            result = render_line(test_line)
            self.assertIsInstance(result, str, "render_line should return a string")
            self.assertIn("Bold text", result, "Should contain the text content")
        except NameError as e:
            if any(name in str(e) for name in ['_is_bold', '_is_italic', '_wrap_span', '_normalize_plain_text']):
                self.fail(f"NameError with underscore-prefixed function: {e}")
            raise


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

