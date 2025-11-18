"""Unit tests for Chapter 10 Gem Table extraction."""

import unittest
import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'pdf_pipeline')))

from transformers.chapter_10.tables import extract_gem_table


class TestGemTableExtraction(unittest.TestCase):
    """Test the extraction of the Gem Table from Chapter 10."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock section data with Gem Table header
        self.section_data = {
            "pages": [
                {
                    "blocks": [
                        {
                            "type": "text",
                            "bbox": [295.0, 467.0, 372.0, 480.0],
                            "lines": [
                                {
                                    "bbox": [295.0, 467.0, 372.0, 480.0],
                                    "spans": [
                                        {
                                            "text": "Gem Table",
                                            "font": "MSTT31c501",
                                            "size": 10.8
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "bbox": [42.0, 492.0, 281.0, 636.0],
                            "lines": [
                                {
                                    "bbox": [42.0, 492.5, 69.0, 502.3],
                                    "spans": [{"text": "D 1 0 0", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [123.0, 492.2, 143.0, 502.1],
                                    "spans": [{"text": "Base", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [43.0, 505.4, 61.0, 515.3],
                                    "spans": [{"text": "Roil", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [122.6, 505.4, 148.4, 515.3],
                                    "spans": [{"text": "Value", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [203.0, 505.4, 227.6, 515.3],
                                    "spans": [{"text": "Cl ass", "font": "MSTT31c50d", "size": 9.56}]
                                },
                                # Row 1
                                {
                                    "bbox": [42.7, 519.1, 68.2, 529.0],
                                    "spans": [{"text": "0 1 - 2", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [124.5, 519.1, 148.9, 529.0],
                                    "spans": [{"text": "15 cp", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [203.2, 518.9, 260.1, 528.7],
                                    "spans": [{"text": "Ornamental", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                # Row 2
                                {
                                    "bbox": [42.9, 532.6, 67.3, 542.4],
                                    "spans": [{"text": "26-50", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [123.1, 532.8, 147.5, 542.6],
                                    "spans": [{"text": "75 cp", "font": "MSTT31c50d", "size": 9.84}]
                                },
                                {
                                    "bbox": [203.0, 532.6, 266.9, 542.4],
                                    "spans": [{"text": "semi-precious", "font": "MSTT31c50d", "size": 9.84}]
                                },
                            ]
                        }
                    ],
                    "tables": []
                }
            ]
        }

    def test_gem_table_found(self):
        """Test that the Gem Table header is found."""
        extract_gem_table(self.section_data)
        
        # Check that the header block was found
        gem_table_block = self.section_data["pages"][0]["blocks"][0]
        self.assertIn("__gem_table", gem_table_block)

    def test_gem_table_structure(self):
        """Test that the Gem Table has the correct structure."""
        extract_gem_table(self.section_data)
        
        gem_table_block = self.section_data["pages"][0]["blocks"][0]
        table = gem_table_block["__gem_table"]
        
        # Check table structure
        self.assertIn("rows", table)
        self.assertIn("header_rows", table)
        self.assertEqual(table["header_rows"], 1)
        
        # Check number of rows (1 header + 6 data)
        self.assertEqual(len(table["rows"]), 7)

    def test_gem_table_headers(self):
        """Test that the Gem Table has the correct column headers."""
        extract_gem_table(self.section_data)
        
        gem_table_block = self.section_data["pages"][0]["blocks"][0]
        table = gem_table_block["__gem_table"]
        
        # Check header row
        header_row = table["rows"][0]
        self.assertEqual(len(header_row["cells"]), 3)
        self.assertEqual(header_row["cells"][0]["text"], "D100 Roll")
        self.assertEqual(header_row["cells"][1]["text"], "Base Value")
        self.assertEqual(header_row["cells"][2]["text"], "Class")

    def test_gem_table_data_rows(self):
        """Test that the Gem Table has the correct data rows."""
        extract_gem_table(self.section_data)
        
        gem_table_block = self.section_data["pages"][0]["blocks"][0]
        table = gem_table_block["__gem_table"]
        
        # Expected data
        expected_data = [
            ("01-2", "15 cp", "Ornamental"),
            ("26-50", "75 cp", "semi-precious"),
            ("51-70", "15 sp", "Fancy"),
            ("71-90", "75 sp", "Precious"),
            ("91-99", "15 gp", "Gems"),
            ("00", "75 gp", "Jewels"),
        ]
        
        # Check each data row
        for i, (d100_roll, base_value, gem_class) in enumerate(expected_data):
            data_row = table["rows"][i + 1]  # Skip header row
            self.assertEqual(len(data_row["cells"]), 3)
            self.assertEqual(data_row["cells"][0]["text"], d100_roll)
            self.assertEqual(data_row["cells"][1]["text"], base_value)
            self.assertEqual(data_row["cells"][2]["text"], gem_class)

    def test_table_data_block_marked_for_removal(self):
        """Test that the table data block is marked for removal."""
        extract_gem_table(self.section_data)
        
        # Check that the data block is marked for removal
        table_data_block = self.section_data["pages"][0]["blocks"][1]
        self.assertTrue(table_data_block.get("__skip_render", False))

    def test_gem_table_not_found(self):
        """Test that extraction handles missing Gem Table gracefully."""
        # Create section data without Gem Table
        section_data = {
            "pages": [
                {
                    "blocks": [
                        {
                            "type": "text",
                            "bbox": [295.0, 467.0, 372.0, 480.0],
                            "lines": [
                                {
                                    "bbox": [295.0, 467.0, 372.0, 480.0],
                                    "spans": [
                                        {
                                            "text": "Other Header",
                                            "font": "MSTT31c501",
                                            "size": 10.8
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "tables": []
                }
            ]
        }
        
        # Should not raise an exception
        extract_gem_table(section_data)
        
        # Check that no table was attached
        block = section_data["pages"][0]["blocks"][0]
        self.assertNotIn("__gem_table", block)


if __name__ == '__main__':
    unittest.main()

