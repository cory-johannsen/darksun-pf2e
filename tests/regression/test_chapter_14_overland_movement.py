#!/usr/bin/env python3
"""
Regression test for Chapter 14 Overland Movement table.

Tests that the "Overland Movement" section correctly displays the Race/Movement Points/Force March
table and legend, without treating table column headers as document headers.
"""

import unittest
import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestChapter14OverlandMovement(unittest.TestCase):
    """Test Chapter 14 Overland Movement table rendering."""
    
    @classmethod
    def setUpClass(cls):
        """Load the generated HTML once for all tests."""
        html_file = Path(__file__).parent.parent.parent / 'data' / 'html_output' / 'chapter-fourteen-time-and-movement.html'
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        with open(html_file) as f:
            cls.html = f.read()
    
    def test_table_has_correct_headers(self):
        """Test that the table has proper <th> headers for Race, Movement Points, and Force March."""
        self.assertIn(
            '<th>Race</th>',
            self.html,
            "Table should have 'Race' as a table header (<th>)"
        )
        self.assertIn(
            '<th>Movement Points</th>',
            self.html,
            "Table should have 'Movement Points' as a table header (<th>)"
        )
        self.assertIn(
            '<th>Force March</th>',
            self.html,
            "Table should have 'Force March' as a table header (<th>)"
        )
    
    def test_table_has_correct_data(self):
        """Test that the table contains the expected race data."""
        # Check for some sample races
        self.assertIn('<td>Human</td><td>24</td><td>30</td>', self.html)
        self.assertIn('<td>Dwarf</td><td>12</td><td>15</td>', self.html)
        self.assertIn('<td>Elf</td><td>24</td><td>30</td>', self.html)
        self.assertIn('<td>Thri-kreen***</td><td>36</td><td>45</td>', self.html)
    
    def test_legend_is_present(self):
        """Test that the legend with *, **, *** is present after the table."""
        self.assertIn('* For overland movement, an elf may add his Constitution score', self.html)
        self.assertIn('** This is for a normal 10-hour marching day. A mul can move for 20 hours', self.html)
        self.assertIn('*** This is for a normal 10-hour marching day. A thri-kreen can always move', self.html)
    
    def test_legend_has_three_separate_paragraphs(self):
        """Test that the legend is split into three separate paragraphs, not one combined paragraph."""
        # Each legend item should start its own paragraph
        legend_items = [
            r'<p>\* For overland movement, an elf may add his Constitution score',
            r'<p>\*\* This is for a normal 10-hour marching day\. A mul can move for 20 hours',
            r'<p>\*\*\* This is for a normal 10-hour marching day\. A thri-kreen can always move'
        ]
        
        for i, pattern in enumerate(legend_items, 1):
            self.assertIsNotNone(
                re.search(pattern, self.html),
                f"Legend item {i} should be in its own separate paragraph starting with <p>"
            )
        
        # Ensure they're NOT all in one paragraph (the old format)
        combined_pattern = r'<p>\* For overland movement.*?\*\* This is for a normal 10-hour.*?\*\*\* This is for a normal 10-hour.*?</p>'
        self.assertIsNone(
            re.search(combined_pattern, self.html),
            "Legend should NOT be one combined paragraph with all three items"
        )
    
    def test_no_movement_points_document_header(self):
        """Test that 'Movement Points' is not rendered as a document header."""
        # Should not have a header with id containing "movement-points"
        pattern = r'<p id="header-\d+-movement-points">'
        self.assertIsNone(
            re.search(pattern, self.html),
            "'Movement Points' should not be a document header"
        )
    
    def test_no_force_march_document_header(self):
        """Test that 'Force March' is not rendered as a document header."""
        # Should not have a header with id containing "force-march"
        pattern = r'<p id="header-\d+-force-march">'
        self.assertIsNone(
            re.search(pattern, self.html),
            "'Force March' should not be a document header"
        )
    
    def test_no_race_document_header(self):
        """Test that 'Race' is not rendered as a document header."""
        # Should not have a header with id containing "race"
        pattern = r'<p id="header-\d+-race">'
        self.assertIsNone(
            re.search(pattern, self.html),
            "'Race' should not be a document header"
        )
    
    def test_toc_no_movement_points(self):
        """Test that 'Movement Points' is not in the table of contents."""
        toc_match = re.search(r'<nav id="table-of-contents">(.*?)</nav>', self.html, re.DOTALL)
        self.assertIsNotNone(toc_match, "Table of contents should exist")
        toc = toc_match.group(1)
        self.assertNotIn('Movement Points</a></li>', toc, "'Movement Points' should not be in TOC")
    
    def test_toc_no_force_march(self):
        """Test that 'Force March' is not in the table of contents."""
        toc_match = re.search(r'<nav id="table-of-contents">(.*?)</nav>', self.html, re.DOTALL)
        self.assertIsNotNone(toc_match, "Table of contents should exist")
        toc = toc_match.group(1)
        self.assertNotIn('Force March</a></li>', toc, "'Force March' should not be in TOC")
    
    def test_no_malformed_table_fragments(self):
        """Test that there are no malformed table fragments mixing unrelated text with race data."""
        # Should not have tables with mixed dehydration text and race data
        self.assertNotIn('<table class="ds-table"><tr><td>Animals and Dehydration</td><td>Human 24</td>', self.html)
        self.assertNotIn('<table class="ds-table"><tr><td>Animals also suffer dehydration', self.html)


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
