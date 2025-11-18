"""
Test for Chapter 15 - Conjure Elemental table

Verifies that Conjure Elemental spell has a proper table with Roll and Hit Dice columns.
"""

import unittest
from pathlib import Path
import re


class TestChapter15ConjureElementalTable(unittest.TestCase):
    """Test Conjure Elemental table structure in Chapter 15."""
    
    def setUp(self):
        """Load the Chapter 15 HTML output."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-fifteen-new-spells.html"
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def _get_conjure_elemental_section(self):
        """Helper method to extract the Conjure Elemental section."""
        # Find the Conjure Elemental H3 header
        header_pattern = r'<h3[^>]*id="header-conjure-elemental[^"]*"[^>]*>.*?</h3>'
        header_match = re.search(header_pattern, self.html_content, re.DOTALL | re.IGNORECASE)
        if not header_match:
            return None
        
        header_end = header_match.end()
        
        # Extract from header to next H2 or H3
        section_pattern = r'(.*?)(?=<h[23]|</section>|</body>)'
        section_match = re.search(section_pattern, self.html_content[header_end:header_end + 3000], re.DOTALL)
        
        if section_match:
            return section_match.group(1)
        return None
    
    def test_conjure_elemental_has_table(self):
        """Test that Conjure Elemental spell has a table element."""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section, "Could not extract Conjure Elemental section")
        
        # Check that section contains a table
        self.assertIn('<table', section,
                     "Conjure Elemental section should contain a <table> element")
    
    def test_conjure_elemental_table_has_headers(self):
        """Test that the table has Roll and Hit Dice headers."""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section)
        
        # Check for table headers
        self.assertIn('Roll', section,
                     "Table should have 'Roll' column header")
        self.assertIn('Hit Dice', section,
                     "Table should have 'Hit Dice' column header")
    
    def test_conjure_elemental_table_has_three_rows(self):
        """Test that the table has 3 data rows."""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section)
        
        # Extract the table
        table_match = re.search(r'<table.*?</table>', section, re.DOTALL)
        self.assertIsNotNone(table_match, "Could not extract table")
        
        table_html = table_match.group(0)
        
        # Count data rows (exclude header row)
        # Look for <tr> tags that are not part of <thead>
        tbody_match = re.search(r'<tbody>(.*?)</tbody>', table_html, re.DOTALL)
        if tbody_match:
            tbody = tbody_match.group(1)
            data_rows = re.findall(r'<tr>', tbody)
            self.assertEqual(len(data_rows), 3,
                           f"Table should have 3 data rows, found {len(data_rows)}")
        else:
            # Count all tr tags except the first (header)
            all_rows = re.findall(r'<tr>', table_html)
            # Assuming first row is header
            self.assertEqual(len(all_rows) - 1, 3,
                           f"Table should have 3 data rows plus header, found {len(all_rows) - 1} data rows")
    
    def test_conjure_elemental_table_has_correct_data(self):
        """Test that the table contains the correct roll ranges and hit dice."""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section)
        
        # Check for specific roll ranges
        self.assertIn('01-65', section,
                     "Table should contain roll range '01-65'")
        self.assertIn('66-90', section,
                     "Table should contain roll range '66-90'")
        self.assertIn('91-00', section,
                     "Table should contain roll range '91-00'")
        
        # Check for hit dice values (8, 12, and likely 16)
        self.assertIn('8', section,
                     "Table should contain hit dice value '8'")
        self.assertIn('12', section,
                     "Table should contain hit dice value '12'")
    
    def test_conjure_elemental_table_placement(self):
        """Test that the table appears after 'The Hit Dice of the elemental are determined randomly.'"""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section)
        
        # Find the sentence about Hit Dice
        hit_dice_idx = section.find('The Hit Dice of the elemental are determined randomly')
        self.assertGreater(hit_dice_idx, -1,
                          "Could not find 'The Hit Dice of the elemental are determined randomly' text")
        
        # Find the table
        table_idx = section.find('<table')
        self.assertGreater(table_idx, -1,
                          "Could not find table")
        
        # Table should appear after the text
        self.assertGreater(table_idx, hit_dice_idx,
                          "Table should appear after 'The Hit Dice of the elemental are determined randomly' text")
    
    def test_no_malformed_header_for_table_data(self):
        """Test that table data is not rendered as an H3 header."""
        section = self._get_conjure_elemental_section()
        self.assertIsNotNone(section)
        
        # Check that "R o l l Hit Dice" is NOT in an H3 header
        malformed_pattern = r'<h3[^>]*>.*?R o l l.*?Hit Dice.*?</h3>'
        malformed_match = re.search(malformed_pattern, section, re.DOTALL | re.IGNORECASE)
        
        self.assertIsNone(malformed_match,
                         "Table data should not be rendered as an H3 header")


if __name__ == '__main__':
    unittest.main()

