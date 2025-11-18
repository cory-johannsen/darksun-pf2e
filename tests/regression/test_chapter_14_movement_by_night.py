"""
Regression test for Chapter 14 Movement by Night paragraph breaks.

This test verifies that the "Movement by Night" section does not have
an incorrect paragraph break at "The drawback to such".
"""

import unittest
import os
import re
from pathlib import Path


class TestChapter14MovementByNight(unittest.TestCase):
    """Test Chapter 14 Movement by Night paragraph integrity."""
    
    def setUp(self):
        """Set up test - find the HTML file."""
        self.project_root = Path(__file__).parent.parent.parent
        self.html_file = self.project_root / "data" / "html_output" / "chapter-fourteen-time-and-movement.html"
        
        if not self.html_file.exists():
            self.skipTest(f"HTML file not found: {self.html_file}")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def test_drawback_is_one_word(self):
        """Test that 'drawback' is one word, not 'draw back'."""
        # Check that "The draw back" does not appear (should be "The drawback")
        self.assertNotIn(
            'The draw back',
            self.html_content,
            "Found 'The draw back' (should be 'The drawback' as one word)"
        )
        
        # Verify the correct form exists
        self.assertIn(
            'The drawback',
            self.html_content,
            "Expected to find 'The drawback' in Movement by Night section"
        )
    
    def test_no_paragraph_break_in_sentence(self):
        """Test that there's no paragraph break in the middle of the drawback sentence."""
        # The sentence should read continuously:
        # "The drawback to such plans is that good rest under the blistering sun of the day is difficult."
        
        # Extract the Movement by Night section (note: header may have attributes)
        match = re.search(
            r'<p id="header-\d+-movement-by-night"[^>]*>.*?</p><p>(.*?)</p>',
            self.html_content,
            re.DOTALL
        )
        
        self.assertIsNotNone(
            match,
            "Could not find Movement by Night section"
        )
        
        movement_paragraph = match.group(1)
        
        # Verify the full sentence appears in one paragraph
        self.assertIn(
            'The drawback to such plans is that good rest under the blistering sun',
            movement_paragraph,
            "The drawback sentence should be in one continuous paragraph"
        )
    
    def test_movement_by_night_paragraph_structure(self):
        """Test the overall paragraph structure of Movement by Night section."""
        # Extract the Movement by Night section
        # It should have one main paragraph containing:
        # 1. Info about temperature drops and half water consumption
        # 2. The drawback about rest under the blistering sun
        # 3. Information about seeking shelter and making saves
        # 4. Note about thri-kreen
        
        match = re.search(
            r'<p id="header-\d+-movement-by-night"[^>]*>.*?</p><p>(.*?)</p>',
            self.html_content,
            re.DOTALL
        )
        
        self.assertIsNotNone(match, "Could not find Movement by Night section")
        
        paragraph = match.group(1)
        
        # Check for key phrases that should all be in the same paragraph
        expected_phrases = [
            'temperatures in all types of terrain drop significantly',
            'half water consumption',
            'The drawback to such plans',
            'good rest under the blistering sun',
            'seek shelter during their daytime rest periods',
            'save vs. poison',
            'Thri-kreen'
        ]
        
        for phrase in expected_phrases:
            self.assertIn(
                phrase,
                paragraph,
                f"Expected phrase not found in paragraph: '{phrase}'"
            )
    
    def test_no_extra_paragraph_tags(self):
        """Test that there are no extra paragraph tags splitting the Movement by Night content."""
        # Extract the section from header to the next header (note: headers have attributes)
        match = re.search(
            r'(<p id="header-\d+-movement-by-night"[^>]*>.*?)</p>\s*<p id="header-\d+-overland-movement"[^>]*>',
            self.html_content,
            re.DOTALL
        )
        
        self.assertIsNotNone(match, "Could not find Movement by Night to Overland Movement span")
        
        section = match.group(1)
        
        # Count paragraph tags - should be exactly 2:
        # 1. The header paragraph (id="header-...-movement-by-night")
        # 2. The content paragraph
        p_count = section.count('<p')
        
        self.assertEqual(
            p_count,
            2,
            f"Expected 2 paragraphs in Movement by Night section (header + content), found {p_count}"
        )


if __name__ == '__main__':
    unittest.main()

