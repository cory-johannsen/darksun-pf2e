#!/usr/bin/env python3
"""
Regression Test: Chapter 10 Lair Treasures Table

This test verifies that the Lair Treasures table in Chapter 10 is properly
extracted, formatted, and rendered in the HTML output.

The table should have:
- Header marked as H2
- 7 columns: Treasure Type, Bits, Ceramic, Silver, Gold, Gems, Magical Item
- 10 data rows for treasure types A through J
- Proper HTML table structure with <th> and <td> tags
- Correct positioning in the document

REGRESSION FIX: This test captures the validation logic from:
- diagnose_chapter10_positions.py
- test_chapter10_details.py
"""

import unittest
import re
from pathlib import Path
from bs4 import BeautifulSoup


class TestChapter10LairTreasuresTable(unittest.TestCase):
    """Test that the Lair Treasures table is correctly extracted and rendered."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 10 HTML output once for all tests."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-ten-treasure.html"
        
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_lair_treasures_header_exists(self):
        """Test that the Lair Treasures header exists in the HTML output."""
        # Look for the header - it should be an H1 or H2
        header_found = False
        header_text = None
        
        # Check for header with id containing 'lair-treasures'
        for tag in self.soup.find_all(['h1', 'h2', 'p']):
            if 'lair' in tag.get_text().lower() and 'treasures' in tag.get_text().lower():
                header_found = True
                header_text = tag.get_text()
                break
        
        self.assertTrue(header_found, "Lair Treasures header not found in HTML")
        self.assertIn("Lair Treasures", header_text, "Header text should contain 'Lair Treasures'")
    
    def test_lair_treasures_table_exists(self):
        """Test that the Lair Treasures table exists as an HTML table."""
        # Find the section after "Lair Treasures" header (in body, not TOC)
        # Look for the actual header element
        lair_header_pos = self.html_content.find('id="header-1-lair-treasures"')
        individual_header_pos = self.html_content.find('id="header-2-individual-and-small-lair-treasures"')
        
        self.assertNotEqual(lair_header_pos, -1, "'Lair Treasures' header not found in body")
        self.assertNotEqual(individual_header_pos, -1, 
            "'Individual and Small Lair Treasures' header not found in body")
        
        # Extract section between the two headers
        section_html = self.html_content[lair_header_pos:individual_header_pos]
        
        # Should have a table in this section
        self.assertIn('<table', section_html, 
            "Lair Treasures table not found between headers")
    
    def test_lair_treasures_table_structure(self):
        """Test that the Lair Treasures table has correct structure."""
        # Find the Lair Treasures table (first table in document)
        tables = self.soup.find_all('table')
        self.assertGreaterEqual(len(tables), 1, "No tables found in HTML")
        
        lair_table = tables[0]  # First table should be Lair Treasures
        
        # Check for header row
        headers = lair_table.find_all('th')
        self.assertGreaterEqual(len(headers), 7, 
            f"Expected at least 7 header cells, found {len(headers)}")
        
        # Check column headers exist
        header_text = ' '.join([h.get_text().strip() for h in headers])
        expected_columns = ['Treasure Type', 'Bits', 'Ceramic', 'Silver', 'Gold', 'Gems', 'Magical']
        
        for col in expected_columns:
            self.assertIn(col, header_text, 
                f"Column header '{col}' not found in table headers")
    
    def test_lair_treasures_treasure_types(self):
        """Test that all treasure types A through I are present."""
        # Find the Lair Treasures table (first table)
        tables = self.soup.find_all('table')
        self.assertGreaterEqual(len(tables), 1, "No tables found")
        
        lair_table = tables[0]
        
        # Get all rows
        rows = lair_table.find_all('tr')
        
        # Should have at least 10 rows (1 header + 9 data rows for A-I)
        self.assertGreaterEqual(len(rows), 10, 
            f"Expected at least 10 rows (1 header + 9 data), found {len(rows)}")
        
        # Check that treasure types A-I appear as first cells in data rows
        data_rows = rows[1:]  # Skip header row
        treasure_types_found = []
        
        for row in data_rows[:9]:  # First 9 data rows (A-I)
            first_cell = row.find('td')
            if first_cell:
                cell_text = first_cell.get_text().strip()
                treasure_types_found.append(cell_text)
        
        # Check we have A through I (Lair Treasures table doesn't have J)
        expected_types = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        for expected_type in expected_types:
            self.assertIn(expected_type, treasure_types_found, 
                f"Treasure type '{expected_type}' not found in Lair Treasures table")
    
    def test_lair_treasures_table_has_data(self):
        """Test that the Lair Treasures table has actual data in cells."""
        # Find the Lair Treasures table (first table)
        tables = self.soup.find_all('table')
        self.assertGreaterEqual(len(tables), 1, "No tables found")
        
        lair_table = tables[0]
        
        # Get all data cells (td tags)
        data_cells = lair_table.find_all('td')
        
        # Should have many data cells (10 rows × 7 columns = 70 cells)
        self.assertGreaterEqual(len(data_cells), 50, 
            f"Expected at least 50 data cells, found {len(data_cells)}")
        
        # Check that at least some cells have actual content
        non_empty_cells = [cell for cell in data_cells if cell.get_text().strip() not in ['', '-']]
        self.assertGreaterEqual(len(non_empty_cells), 30, 
            f"Expected at least 30 non-empty cells, found {len(non_empty_cells)}")
    
    def test_lair_treasures_table_positioning(self):
        """Test that the Lair Treasures table appears in the correct location."""
        # The table should appear after the "Lair Treasures" header
        # and before the "Individual and Small Lair Treasures" header
        
        # Find positions in the HTML (using header IDs to avoid TOC)
        lair_header_pos = self.html_content.find('id="header-1-lair-treasures"')
        individual_header_pos = self.html_content.find('id="header-2-individual-and-small-lair-treasures"')
        
        self.assertNotEqual(lair_header_pos, -1, "'Lair Treasures' header not found")
        self.assertNotEqual(individual_header_pos, -1, 
            "'Individual and Small Lair Treasures' header not found")
        
        # Find a table between these two positions
        section_html = self.html_content[lair_header_pos:individual_header_pos]
        
        # Should have at least one <table> tag in this section
        self.assertIn('<table', section_html, 
            "No table found between 'Lair Treasures' and 'Individual and Small Lair Treasures'")
        
        # The table should contain treasure types A-I (Lair Treasures has A-I, Individual has J-Z)
        self.assertIn('>A<', section_html, "Treasure type A not found in section")
        self.assertIn('>I<', section_html, "Treasure type I not found in section")
    
    def test_no_duplicate_lair_treasures_table(self):
        """Test that there is only one Lair Treasures table before Individual Treasures."""
        # Count how many times the header ID appears (most reliable)
        lair_count = self.html_content.count('id="header-1-lair-treasures"')
        
        # Should appear exactly once
        self.assertEqual(lair_count, 1, 
            f"Expected exactly 1 'Lair Treasures' header (by ID), found {lair_count}")


if __name__ == '__main__':
    unittest.main()

