"""Unit tests for journal transformer."""

import unittest
from unittest.mock import Mock, patch

from tools.pdf_pipeline.transformers.journal import transform


class TestJournalTransform(unittest.TestCase):
    """Test the transform function in journal transformer.
    
    Note: The journal transformer is complex and primarily tested through integration tests.
    These unit tests focus on basic structure and error handling.
    """
    
    def test_transform_basic_structure(self):
        """Test that transform returns the expected structure."""
        section_data = {
            "title": "Test Chapter",
            "slug": "test-chapter",
            "start_page": 1,
            "end_page": 2,
            "pages": [
                {
                    "page_num": 1,
                    "width": 612,
                    "height": 792,
                    "blocks": [
                        {
                            "bbox": [50, 100, 500, 150],
                            "lines": [
                                {
                                    "bbox": [50, 100, 500, 120],
                                    "spans": [
                                        {
                                            "text": "This is a test paragraph.",
                                            "font": "TimesRoman",
                                            "size": 12,
                                            "bbox": [50, 100, 500, 120]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        result = transform(section_data, config={})
        
        # Check basic structure is returned
        self.assertIsInstance(result, dict)
        self.assertIn("slug", result)
        self.assertEqual(result["slug"], "test-chapter")
        self.assertIn("entity_type", result)
        self.assertEqual(result["entity_type"], "journal")
        self.assertIn("title", result)
        self.assertIn("content", result)
        self.assertIn("source_pages", result)
        self.assertIn("metadata", result)
    
    def test_transform_returns_content(self):
        """Test that transform returns content field."""
        section_data = {
            "title": "Content Test",
            "slug": "content-test",
            "start_page": 1,
            "end_page": 1,
            "pages": []
        }
        
        result = transform(section_data, config={})
        
        # Should always have content (even if empty)
        self.assertIn("content", result)
        self.assertIsInstance(result["content"], str)
    
    def test_transform_with_empty_pages(self):
        """Test handling of empty pages."""
        section_data = {
            "title": "Empty Test",
            "slug": "empty-test",
            "start_page": 1,
            "end_page": 1,
            "pages": []
        }
        
        result = transform(section_data, config={})
        
        # Should still return valid structure
        self.assertIn("slug", result)
        self.assertIn("entity_type", result)
        self.assertIn("content", result)
    
    def test_transform_with_config(self):
        """Test that config parameter is accepted."""
        section_data = {
            "title": "Config Test",
            "slug": "config-test",
            "start_page": 1,
            "end_page": 1,
            "pages": []
        }
        
        config = {
            "include_tables": True,
            "wrap_pages": False
        }
        
        result = transform(section_data, config)
        
        # Should complete successfully with config
        self.assertIn("slug", result)
        self.assertIn("entity_type", result)
        self.assertEqual(result["entity_type"], "journal")
    
    def test_transform_with_none_config(self):
        """Test that None config is handled."""
        section_data = {
            "title": "None Config Test",
            "slug": "none-config-test",
            "start_page": 1,
            "end_page": 1,
            "pages": []
        }
        
        result = transform(section_data, None)
        
        # Should handle None config gracefully
        self.assertIn("slug", result)
        self.assertIn("entity_type", result)
    
    def test_transform_preserves_metadata(self):
        """Test that metadata fields are preserved."""
        section_data = {
            "title": "Metadata Test",
            "slug": "metadata-test",
            "start_page": 5,
            "end_page": 10,
            "parent_slugs": ["parent1", "parent2"],
            "level": 2,
            "pages": []
        }
        
        result = transform(section_data, config={})
        
        # Should preserve source pages
        self.assertEqual(result["source_pages"], [5, 10])
        
        # Should have metadata
        self.assertIn("metadata", result)
        metadata = result["metadata"]
        self.assertIn("parent_slugs", metadata)
        self.assertEqual(metadata["parent_slugs"], ["parent1", "parent2"])
        self.assertIn("level", metadata)
        self.assertEqual(metadata["level"], 2)


if __name__ == "__main__":
    unittest.main()

