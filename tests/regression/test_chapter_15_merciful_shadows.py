"""
Test for Chapter 15 - Spell name formatting

Verifies:
1. "MercifulShadows" has a space -> "Merciful Shadows"
2. "CharmPersonorMammal" has spaces -> "Charm Person or Mammal"
3. Spell stat block is properly formatted with line breaks
"""

import unittest
from pathlib import Path


class TestChapter15SpellNameFormatting(unittest.TestCase):
    """Test spell name formatting in Chapter 15."""
    
    def setUp(self):
        """Load the Chapter 15 HTML output."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-fifteen-new-spells.html"
        with open(html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()
    
    def test_merciful_shadows_has_space(self):
        """Test that 'Merciful Shadows' has a space in the spell name."""
        # Should have "Merciful Shadows" not "MercifulShadows"
        self.assertIn("Merciful Shadows", self.html_content,
                     "Spell name should be 'Merciful Shadows' with a space")
        self.assertNotIn("MercifulShadows", self.html_content,
                        "Spell name should not be 'MercifulShadows' without a space")
    
    def test_charm_person_or_mammal_has_spaces(self):
        """Test that 'Charm Person or Mammal' has spaces in the spell name."""
        # Should have "Charm Person or Mammal" not "CharmPersonorMammal"
        self.assertIn("Charm Person or Mammal", self.html_content,
                     "Spell name should be 'Charm Person or Mammal' with spaces")
        self.assertNotIn("CharmPersonorMammal", self.html_content,
                        "Spell name should not be 'CharmPersonorMammal' without spaces")
    
    def test_merciful_shadows_stat_block_formatting(self):
        """Test that Merciful Shadows spell stat block has proper line breaks."""
        # The spell stat block should have each stat on its own line with <br> tags
        # Look for the pattern after "Merciful Shadows" header
        
        # Check that stat block components are separated by <br> tags
        # Should have patterns like: "Sphere: Cosmos<br>" or "Sphere: Cosmos</div>"
        stat_block_patterns = [
            "Sphere: Cosmos",
            "Range: Touch",
            "Components: V, S, M",
            "Duration: 1 day/5 levels",
            "Casting Time: 1 round",
            "Area of Effect: Person touched",
            "Saving Throw: Neg."
        ]
        
        # Find the Merciful Shadows H3 header in the body (not in TOC)
        # Look for it as an H3 tag, not just the text
        merciful_idx = self.html_content.find('<h3 id="header-m-e-r-c-i-f-u-l--s-h-a-d-o-w-s')
        self.assertGreater(merciful_idx, -1, "Could not find 'Merciful Shadows' H3 header in HTML")
        
        # Extract a reasonable chunk after the header (next 1000 chars should contain the stat block)
        section = self.html_content[merciful_idx:merciful_idx + 1000]
        
        # Check that all stat components are present
        for pattern in stat_block_patterns:
            self.assertIn(pattern, section,
                         f"Stat block should contain '{pattern}'")
        
        # Check that stats are separated by line breaks (not all on one line)
        # Should NOT have "Range: Touch Components:" (without a break between them)
        self.assertNotIn("Range: Touch Components:", section,
                        "Stats should not be on the same line without breaks")
        
        # Should have "Range: Touch" followed by a break tag
        # Either <br> or </div> (if wrapped in a div)
        import re
        range_with_break = re.search(r'Range:\s*Touch\s*(<br|</div)', section)
        self.assertIsNotNone(range_with_break,
                           "Range: Touch should be followed by a line break or closing div")


if __name__ == '__main__':
    unittest.main()

