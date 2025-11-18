#!/usr/bin/env python3
"""Regression test for Chapter 10 Magical Items section formatting."""

import unittest
import re
from pathlib import Path


class TestChapter10MagicalItemsFormatting(unittest.TestCase):
    """Test that Chapter 10 Magical Items section has correct formatting."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 10 HTML output."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-ten-treasure.html"
        with open(html_path, 'r') as f:
            cls.html_content = f.read()
    
    def test_magical_items_paragraph_count(self):
        """Test that Magical Items section has at least 5 paragraphs before the list."""
        # Find the section from "II. Magical Items" to the first list item
        magical_items_start = 'id="header-7-magical-items"'
        first_list_item = 'Potion of Giant Control'
        
        start_idx = self.html_content.find(magical_items_start)
        end_idx = self.html_content.find(first_list_item)
        
        self.assertNotEqual(start_idx, -1, "Could not find Magical Items header")
        self.assertNotEqual(end_idx, -1, "Could not find first list item")
        
        section_content = self.html_content[start_idx:end_idx]
        
        # Count paragraph tags
        p_count = section_content.count('<p')
        
        # Should have at least 5 paragraphs:
        # 1. The nature of magical items...
        # 2. If a Dark Sun...
        # 3. Other magical items...
        # 4. A final group...
        # 5. The following items...
        self.assertGreaterEqual(p_count, 5, 
            f"Expected at least 5 paragraphs in Magical Items section, found {p_count}")
    
    def test_magical_items_list_formatting(self):
        """Test that the 9 items are properly formatted."""
        items = [
            "Potion of Giant Control",
            "Potion of Giant Strength",
            "Potion of Undead Control",
            "Rod of Resurrection",
            "Boots of Varied Tracks",
            "Candle of Invocation",
            "Deck of Illusions",
            "Figurines of Wondrous Power",
            "Necklace of Prayer Beads"
        ]
        
        for item in items:
            self.assertIn(item, self.html_content, 
                f"Item '{item}' not found in HTML output")
            
            # Find the paragraph containing this item
            item_idx = self.html_content.find(item)
            
            # Look backwards to find the opening <p> tag for this item
            before_item = self.html_content[max(0, item_idx-200):item_idx]
            last_p_tag_pos = before_item.rfind('<p')
            self.assertNotEqual(last_p_tag_pos, -1, 
                f"Item '{item}' should have <p> tag before it")
            
            # Extract the text between the last <p> and this item
            text_before_item = before_item[last_p_tag_pos:]
            
            # CRITICAL 1: Item name should be at/near the start of its paragraph
            # Check that no other item names appear before this one in the same paragraph
            other_items = [other for other in items if other != item]
            for other_item in other_items:
                self.assertNotIn(other_item, text_before_item,
                    f"Item '{item}' paragraph should not contain '{other_item}' before it")
            
            # CRITICAL 2: "campaigns:" should NOT be in the same paragraph as "Potion of Giant Control"
            if item == "Potion of Giant Control":
                # Find the paragraph containing this item
                p_start = self.html_content.rfind('<p', 0, item_idx)
                p_end = self.html_content.find('</p>', item_idx)
                paragraph_text = self.html_content[p_start:p_end + 4]
                self.assertNotIn("campaigns", paragraph_text.lower(),
                    "The first item should not contain 'campaigns:' text")
            
            # CRITICAL 3: Each item's description should be continuous (not split across paragraphs)
            # Find the paragraph containing this item
            p_start = self.html_content.rfind('<p', 0, item_idx)
            p_end = self.html_content.find('</p>', item_idx)
            
            if p_end != -1:
                # Get the full paragraph HTML
                paragraph_html = self.html_content[p_start:p_end + 4]
                
                # Count how many times the item name appears - should be exactly once
                item_count = paragraph_html.count(item)
                self.assertEqual(item_count, 1,
                    f"Item '{item}' should appear exactly once in its paragraph, found {item_count}")
                
                # Check that the paragraph ends with the closing tag (description is complete)
                self.assertTrue(paragraph_html.endswith('</p>'),
                    f"Item '{item}' paragraph should end with </p>")
            
            # Check formatting: item should have bold and/or color
            context = self.html_content[max(0, item_idx-100):item_idx+len(item)+10]
            has_formatting = ('<strong>' in context or '<span style="color' in context)
            self.assertTrue(has_formatting,
                f"Item '{item}' should have formatting (bold or colored)")
    
    def test_if_a_dark_sun_paragraph_break(self):
        """Test that 'If a Dark Sun' starts a new paragraph."""
        # Find "If a Dark Sun" and check if it's preceded by a <p> tag
        idx = self.html_content.find("If a Dark Sun")
        self.assertNotEqual(idx, -1, "Could not find 'If a Dark Sun' text")
        
        # Look at the 50 characters before it
        before_text = self.html_content[max(0, idx-50):idx]
        
        # Should have a <p> or </p> nearby indicating paragraph break
        has_p_tag = '<p' in before_text or '</p>' in before_text
        self.assertTrue(has_p_tag,
            "'If a Dark Sun' should start a new paragraph")
    
    def test_other_magical_items_paragraph_break(self):
        """Test that 'Other magical items' starts a new paragraph."""
        idx = self.html_content.find("Other magical items")
        self.assertNotEqual(idx, -1, "Could not find 'Other magical items' text")
        
        before_text = self.html_content[max(0, idx-50):idx]
        has_p_tag = '<p' in before_text or '</p>' in before_text
        self.assertTrue(has_p_tag,
            "'Other magical items' should start a new paragraph")
    
    def test_a_final_group_paragraph_break(self):
        """Test that 'A final group' starts a new paragraph."""
        idx = self.html_content.find("A final group")
        self.assertNotEqual(idx, -1, "Could not find 'A final group' text")
        
        before_text = self.html_content[max(0, idx-50):idx]
        has_p_tag = '<p' in before_text or '</p>' in before_text
        self.assertTrue(has_p_tag,
            "'A final group' should start a new paragraph")


if __name__ == '__main__':
    unittest.main()

