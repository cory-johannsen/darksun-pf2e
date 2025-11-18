"""
Test for Chapter 15 - Air Lens paragraph structure

Verifies that Air Lens (Alteration) has exactly 3 paragraphs:
1. Main description (starts with "By means of this spell")
2. Ignition effects (starts with "The spell can also")
3. Material component (starts with "The material component")
"""

import unittest
from pathlib import Path
import re


class TestChapter15AirLensParagraphs(unittest.TestCase):
    """Test Air Lens spell paragraph structure in Chapter 15."""
    
    def setUp(self):
        """Load the Chapter 15 HTML output."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-fifteen-new-spells.html"
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def test_air_lens_has_three_paragraphs(self):
        """Test that Air Lens has exactly 3 paragraphs after the stat block."""
        # Find the Air Lens section
        air_lens_pattern = re.compile(
            r'<h3[^>]*id="header-air-lens-\(alteration\)"[^>]*>.*?</h3>.*?'  # Air Lens header
            r'<div class="spell-stats">.*?</div>'  # Stat block
            r'(.*?)'  # Content between stat block and next header
            r'<h2',  # Next header (Fourth-Level Spells)
            re.DOTALL | re.IGNORECASE
        )
        
        match = air_lens_pattern.search(self.html_content)
        self.assertIsNotNone(match, "Could not find Air Lens spell section")
        
        content = match.group(1)
        
        # Count paragraphs
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        self.assertEqual(len(paragraphs), 3, 
                        f"Air Lens should have exactly 3 paragraphs, found {len(paragraphs)}")
    
    def test_air_lens_first_paragraph_starts_correctly(self):
        """Test that first paragraph starts with 'By means of this spell'."""
        air_lens_pattern = re.compile(
            r'<h3[^>]*id="header-air-lens-\(alteration\)"[^>]*>.*?</h3>.*?'
            r'<div class="spell-stats">.*?</div>'
            r'(.*?)'
            r'<h2',
            re.DOTALL | re.IGNORECASE
        )
        
        match = air_lens_pattern.search(self.html_content)
        self.assertIsNotNone(match)
        
        content = match.group(1)
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        
        self.assertTrue(paragraphs[0].strip().startswith('By means of this spell'),
                       "First paragraph should start with 'By means of this spell'")
    
    def test_air_lens_second_paragraph_starts_correctly(self):
        """Test that second paragraph starts with 'The spell can also'."""
        air_lens_pattern = re.compile(
            r'<h3[^>]*id="header-air-lens-\(alteration\)"[^>]*>.*?</h3>.*?'
            r'<div class="spell-stats">.*?</div>'
            r'(.*?)'
            r'<h2',
            re.DOTALL | re.IGNORECASE
        )
        
        match = air_lens_pattern.search(self.html_content)
        self.assertIsNotNone(match)
        
        content = match.group(1)
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        
        self.assertTrue(paragraphs[1].strip().startswith('The spell can also'),
                       "Second paragraph should start with 'The spell can also'")
    
    def test_air_lens_third_paragraph_starts_correctly(self):
        """Test that third paragraph starts with 'The material component'."""
        air_lens_pattern = re.compile(
            r'<h3[^>]*id="header-air-lens-\(alteration\)"[^>]*>.*?</h3>.*?'
            r'<div class="spell-stats">.*?</div>'
            r'(.*?)'
            r'<h2',
            re.DOTALL | re.IGNORECASE
        )
        
        match = air_lens_pattern.search(self.html_content)
        self.assertIsNotNone(match)
        
        content = match.group(1)
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        
        self.assertTrue(paragraphs[2].strip().startswith('The material component'),
                       "Third paragraph should start with 'The material component'")
    
    def test_air_lens_first_paragraph_does_not_contain_ignition_text(self):
        """Test that first paragraph does NOT end with 'The spell can also'."""
        air_lens_pattern = re.compile(
            r'<h3[^>]*id="header-air-lens-\(alteration\)"[^>]*>.*?</h3>.*?'
            r'<div class="spell-stats">.*?</div>'
            r'(.*?)'
            r'<h2',
            re.DOTALL | re.IGNORECASE
        )
        
        match = air_lens_pattern.search(self.html_content)
        self.assertIsNotNone(match)
        
        content = match.group(1)
        paragraphs = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        
        # First paragraph should NOT contain "The spell can also"
        self.assertNotIn('The spell can also', paragraphs[0],
                        "First paragraph should not contain 'The spell can also' text")


if __name__ == '__main__':
    unittest.main()

