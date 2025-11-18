"""Regression test for Chapter 15 - Rejuvenate spell paragraph breaks.

This test verifies that the Rejuvenate (Alteration) spell in Chapter 15 has the correct
5 paragraph structure as specified.
"""

import unittest
from pathlib import Path


class TestChapter15RejuvenateParagraphs(unittest.TestCase):
    """Test that Rejuvenate spell has proper paragraph breaks."""

    def setUp(self):
        """Set up test fixtures."""
        self.html_path = Path("data/html_output/chapter-fifteen-new-spells.html")
        self.assertTrue(self.html_path.exists(), f"HTML file not found: {self.html_path}")
        
        with open(self.html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()

    def test_rejuvenate_has_five_paragraphs(self):
        """Test that Rejuvenate spell description has 5 distinct paragraphs."""
        # Find the Rejuvenate section (5th level spell)
        rejuvenate_start = self.html_content.find('id="header-rejuvenate-(alteration)"')
        self.assertNotEqual(rejuvenate_start, -1, "Could not find Rejuvenate (Alteration) header")
        
        # Find the next spell header to bound our search
        next_header_start = self.html_content.find('id="header-wall-of-iron"', rejuvenate_start)
        self.assertNotEqual(next_header_start, -1, "Could not find Wall of Iron header")
        
        # Extract the Rejuvenate section
        rejuvenate_section = self.html_content[rejuvenate_start:next_header_start]
        
        # Verify the 5 required paragraph starting phrases exist
        required_paragraphs = [
            "This spell grants",
            "In either case",
            "The duration of the spell",
            "The material component",
            "Defilers cannot"
        ]
        
        for paragraph_start in required_paragraphs:
            self.assertIn(
                paragraph_start,
                rejuvenate_section,
                f"Missing paragraph starting with '{paragraph_start}'"
            )
    
    def test_rejuvenate_paragraph_separation(self):
        """Test that the 5 paragraphs are properly separated with <p> tags."""
        # Find the Rejuvenate section
        rejuvenate_start = self.html_content.find('id="header-rejuvenate-(alteration)"')
        next_header_start = self.html_content.find('id="header-wall-of-iron"', rejuvenate_start)
        rejuvenate_section = self.html_content[rejuvenate_start:next_header_start]
        
        # Check that each paragraph is in its own <p> tag
        # (not all in one long line after the stat block)
        
        # First, verify "This spell grants" comes after the spell-stats div
        self.assertIn('<div class="spell-stats">', rejuvenate_section)
        stats_end = rejuvenate_section.find('</div>')
        self.assertNotEqual(stats_end, -1, "Could not find end of spell-stats div")
        
        after_stats = rejuvenate_section[stats_end:]
        
        # Verify paragraphs are in separate <p> tags
        # Look for pattern: </p><p>In either case
        self.assertRegex(
            after_stats,
            r'</p>\s*<p>In either case',
            "Paragraph 'In either case' not properly separated"
        )
        
        self.assertRegex(
            after_stats,
            r'</p>\s*<p>The duration of the spell',
            "Paragraph 'The duration of the spell' not properly separated"
        )
        
        self.assertRegex(
            after_stats,
            r'</p>\s*<p>The material component',
            "Paragraph 'The material component' not properly separated"
        )
        
        self.assertRegex(
            after_stats,
            r'</p>\s*<p>Defilers cannot',
            "Paragraph 'Defilers cannot' not properly separated"
        )
    
    def test_rejuvenate_no_merged_content(self):
        """Test that content is not all merged into one paragraph."""
        # Find the Rejuvenate section
        rejuvenate_start = self.html_content.find('id="header-rejuvenate-(alteration)"')
        next_header_start = self.html_content.find('id="header-wall-of-iron"', rejuvenate_start)
        rejuvenate_section = self.html_content[rejuvenate_start:next_header_start]
        
        # Find the stat block
        stats_start = rejuvenate_section.find('<div class="spell-stats">')
        stats_end = rejuvenate_section.find('</div>', stats_start)
        
        # Get content after the stat block
        after_stats = rejuvenate_section[stats_end:]
        
        # Should NOT have all content merged in one line like:
        # "Saving Throw: None This spell grants...In either case...The duration..."
        # 
        # Instead, look for evidence of improper merging
        # If "In either case" appears in the same <p> tag as "This spell grants"
        # without a closing </p> in between, it's merged incorrectly
        
        # Find the first <p> after stats
        first_p_start = after_stats.find('<p>')
        if first_p_start != -1:
            first_p_end = after_stats.find('</p>', first_p_start)
            first_paragraph = after_stats[first_p_start:first_p_end]
            
            # The first paragraph should contain "This spell grants"
            # but should NOT contain "In either case" (that should be in the next paragraph)
            if "This spell grants" in first_paragraph:
                self.assertNotIn(
                    "In either case",
                    first_paragraph,
                    "Paragraphs are incorrectly merged: 'In either case' should be in a separate <p> tag"
                )
                self.assertNotIn(
                    "The duration of the spell",
                    first_paragraph,
                    "Paragraphs are incorrectly merged: 'The duration of the spell' should be in a separate <p> tag"
                )
                self.assertNotIn(
                    "Defilers cannot",
                    first_paragraph,
                    "Paragraphs are incorrectly merged: 'Defilers cannot' should be in a separate <p> tag"
                )


if __name__ == '__main__':
    unittest.main()

