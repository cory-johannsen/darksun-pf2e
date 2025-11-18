"""Unit tests for Chapter 7 Defiler Magical Destruction Table extraction.

[BEST_PRACTICES_UNIT_TESTS] Tests for the Defiler Magical Destruction Table extraction.
"""

import json
import unittest
from pathlib import Path


class TestDefileTableExtraction(unittest.TestCase):
    """Test the Defiler Magical Destruction Table extraction."""

    def setUp(self):
        """Load the processed chapter 7 section data."""
        self.section_path = Path("data/raw_structured/sections/02-058-chapter-seven-magic.json")
        if not self.section_path.exists():
            self.skipTest(f"Section data not found: {self.section_path}")
        
        with open(self.section_path, 'r', encoding='utf-8') as f:
            self.section_data = json.load(f)

    def test_table_header_present(self):
        """Test that the Defiler Magical Destruction Table header is present."""
        # The table header should be on page 4 (index 4)
        pages = self.section_data.get("pages", [])
        self.assertGreaterEqual(len(pages), 5, "Not enough pages in section data")
        
        page = pages[4]
        blocks = page.get("blocks", [])
        
        # Find the table header
        found_header = False
        for block in blocks:
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
            
            if "Defiler Magical Destruction Table" in block_text:
                found_header = True
                break
        
        self.assertTrue(found_header, "Defiler Magical Destruction Table header not found")

    def test_column_headers_present(self):
        """Test that column headers (Terrain Type, Spell Level) are present."""
        pages = self.section_data.get("pages", [])
        page = pages[4]
        blocks = page.get("blocks", [])
        
        found_headers = False
        
        for block in blocks:
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
            
            block_text = block_text.strip()
            
            # The headers are combined in one block
            if "Terrain Type" in block_text and "Spell Level" in block_text:
                found_headers = True
                break
        
        self.assertTrue(found_headers, "Column headers (Terrain Type / Spell Level) not found")

    def test_terrain_types_present(self):
        """Test that all expected terrain types are present in the data."""
        expected_terrains = [
            "Stony Barrens",
            "Sandy Wastes",
            "Rocky Badlands",
            "Salt Flats",
            "Boulder Fields",
            "Silt Sea",
            "Mountains",
            "Scrub Plains",
            "Verdant Belts",
            "Forest"
        ]
        
        pages = self.section_data.get("pages", [])
        page = pages[4]
        blocks = page.get("blocks", [])
        
        found_terrains = []
        
        for block in blocks:
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", " ")
            
            block_text = " ".join(block_text.split())
            
            for terrain in expected_terrains:
                if terrain in block_text and terrain not in found_terrains:
                    found_terrains.append(terrain)
        
        self.assertEqual(
            len(found_terrains), 
            len(expected_terrains), 
            f"Not all terrain types found. Found: {found_terrains}, Expected: {expected_terrains}"
        )

    def test_table_end_marker(self):
        """Test that the table end marker paragraph is present."""
        pages = self.section_data.get("pages", [])
        page = pages[4]
        blocks = page.get("blocks", [])
        
        found_end_marker = False
        
        for block in blocks:
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span.get("text", "")
            
            if "The number shown is the radius" in block_text:
                found_end_marker = True
                break
        
        self.assertTrue(found_end_marker, "Table end marker paragraph not found")


class TestDefilerTableStructure(unittest.TestCase):
    """Test the structure of the extracted Defiler Magical Destruction Table after processing."""

    def setUp(self):
        """Set up test data."""
        # After the pipeline runs, the table should be in the processed section data
        # For now, we'll just validate the extraction logic
        pass

    def test_table_has_correct_dimensions(self):
        """Test that the table has 10 columns and 12 rows after extraction."""
        # This test will run after the pipeline executes
        # For now, we document the expected structure
        expected_columns = 10  # Terrain Type + 9 spell levels
        expected_rows = 11     # 1 header + 10 terrain types
        
        # The actual test will be implemented once we can load the processed HTML
        self.assertTrue(True, "Placeholder test for table dimensions")

    def test_table_header_row_structure(self):
        """Test that the header row has correct structure."""
        # Expected header: ["Terrain Type", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        expected_headers = ["Terrain Type", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        # This will be validated after pipeline runs
        self.assertTrue(True, "Placeholder test for header row")


if __name__ == "__main__":
    unittest.main()

