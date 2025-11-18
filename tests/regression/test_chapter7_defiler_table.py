"""Regression test for Chapter 7 Defiler Magical Destruction Table rendering.

[REGRESSION_TESTING] This test validates that the Defiler Magical Destruction Table
is properly extracted and rendered in the HTML output.
"""

import re
import unittest
from pathlib import Path


class TestDefilerTableRendering(unittest.TestCase):
    """Test that the Defiler Magical Destruction Table is properly rendered in HTML."""

    def setUp(self):
        """Load the Chapter 7 HTML output."""
        self.html_path = Path("data/html_output/chapter-seven-magic.html")
        if not self.html_path.exists():
            self.skipTest(f"HTML output not found: {self.html_path}")
        
        with open(self.html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()

    def test_defiler_table_exists(self):
        """Test that the Defiler Magical Destruction Table exists in the HTML."""
        # Look for the table header
        self.assertIn("Defiler Magical Destruction Table", self.html_content,
                      "Defiler Magical Destruction Table header not found in HTML")
        
        # Look for the table tag
        self.assertIn('<table class="ds-table">', self.html_content,
                      "Table tag not found in HTML")

    def test_defiler_table_structure(self):
        """Test that the table has the correct structure (10 columns, 11 rows)."""
        # Extract the table HTML
        table_pattern = r'<table class="ds-table">.*?</table>'
        match = re.search(table_pattern, self.html_content, re.DOTALL)
        
        self.assertIsNotNone(match, "Could not find Defiler table in HTML")
        
        table_html = match.group(0)
        
        # Count rows
        row_count = table_html.count('<tr>')
        self.assertEqual(row_count, 11, f"Expected 11 rows (1 header + 10 data), found {row_count}")
        
        # Check header row has 10 columns
        header_pattern = r'<tr>(.*?)</tr>'
        header_match = re.search(header_pattern, table_html, re.DOTALL)
        self.assertIsNotNone(header_match, "Could not find header row")
        
        header_row = header_match.group(1)
        header_cells = header_row.count('<th>')
        self.assertEqual(header_cells, 10, f"Expected 10 header cells, found {header_cells}")

    def test_terrain_types_in_table(self):
        """Test that all 10 terrain types are present in the table."""
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
        
        for terrain in expected_terrains:
            self.assertIn(f"<td>{terrain}</td>", self.html_content,
                          f"Terrain type '{terrain}' not found in table")

    def test_column_headers_not_duplicated(self):
        """Test that column headers are not rendered as separate paragraphs."""
        # The column headers should only appear in the table, not as separate text
        
        # Look for the table section
        table_section_pattern = r'Defiler Magical Destruction Table.*?<table'
        match = re.search(table_section_pattern, self.html_content, re.DOTALL)
        
        self.assertIsNotNone(match, "Could not find table section")
        
        section_before_table = match.group(0)
        
        # Check that "Terrain TypeSpell Level" does not appear as a paragraph
        self.assertNotIn("Terrain TypeSpell Level", section_before_table,
                         "Column headers should not be rendered as separate text")
        
        # Check that terrain data is not duplicated outside the table
        # Look for the paragraph after the table
        after_table_pattern = r'</table>(.*?)<p'
        after_match = re.search(after_table_pattern, self.html_content, re.DOTALL)
        
        if after_match:
            after_table = after_match.group(1)
            # Should start with "The number shown is the radius"
            self.assertIn("The number shown is the radius", after_table or self.html_content,
                          "Expected paragraph after table not found")

    def test_spell_level_headers(self):
        """Test that spell level headers (1-9) are present in the table."""
        # Extract the table header row
        header_pattern = r'<tr><th>Terrain Type</th>(.*?)</tr>'
        match = re.search(header_pattern, self.html_content)
        
        self.assertIsNotNone(match, "Could not find table header row")
        
        header_row = match.group(1)
        
        # Check that spell levels 1-9 are present as header cells
        for level in range(1, 10):
            self.assertIn(f"<th>{level}</th>", header_row,
                          f"Spell level {level} not found in table headers")

    def test_terrain_data_values(self):
        """Test that terrain data contains expected numeric values."""
        # Check a few sample rows
        test_cases = [
            ("Stony Barrens", ["10", "14", "17", "20", "22", "24", "26", "28", "30"]),
            ("Scrub Plains", ["3", "4", "4", "5", "5", "5", "5", "6", "6"]),
            ("Verdant Belts", ["2", "2", "2", "3", "3", "3", "4", "4", "4"]),
            ("Forest", ["1", "1", "2", "2", "2", "2", "2", "3", "3"])
        ]
        
        for terrain, expected_values in test_cases:
            # Find the row for this terrain
            row_pattern = rf'<tr><td>{re.escape(terrain)}</td>(.*?)</tr>'
            match = re.search(row_pattern, self.html_content)
            
            self.assertIsNotNone(match, f"Could not find row for {terrain}")
            
            row_data = match.group(1)
            
            # Check that all expected values are present
            for value in expected_values:
                self.assertIn(f"<td>{value}</td>", row_data,
                              f"Value {value} not found in {terrain} row")


if __name__ == "__main__":
    unittest.main()

