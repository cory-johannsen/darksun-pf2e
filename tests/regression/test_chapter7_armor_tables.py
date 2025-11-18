"""Regression test for Chapter 7 armor tables.

This test ensures that the ARMOR TYPE and METAL ARMOR tables in Chapter 7
are properly formatted as HTML tables with correct structure and content.
"""

import unittest
from pathlib import Path


class TestChapter7ArmorTables(unittest.TestCase):
    """Regression tests for Chapter 7 armor table rendering."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 7 HTML file once for all tests."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-seven-magic.html"
        
        if not html_path.exists():
            raise FileNotFoundError(f"Chapter 7 HTML not found at {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
    
    def test_armor_type_table_exists(self):
        """Test that the ARMOR TYPE table exists in the HTML."""
        self.assertIn('<table class="ds-table">', self.html_content, 
                     "No table found in Chapter 7 HTML")
        self.assertIn('ARMOR TYPE', self.html_content,
                     "ARMOR TYPE header not found")
    
    def test_armor_type_table_has_correct_header(self):
        """Test that the ARMOR TYPE table has the correct header row."""
        # Find the ARMOR TYPE header element (not in TOC)
        armor_type_start = self.html_content.find('id="header-20-armor-type"')
        self.assertGreater(armor_type_start, -1, "ARMOR TYPE section not found")
        
        # Find the first table after ARMOR TYPE header
        table_start = self.html_content.find('<table', armor_type_start)
        table_end = self.html_content.find('</table>', table_start) + len('</table>')
        
        table_content = self.html_content[table_start:table_end]
        
        # Check for correct header row
        self.assertIn('<th>d20 Roll</th>', table_content,
                     "d20 Roll header not found in ARMOR TYPE table")
        self.assertIn('<th>Armor</th>', table_content,
                     "Armor header not found in ARMOR TYPE table")
    
    def test_armor_type_table_has_all_rows(self):
        """Test that the ARMOR TYPE table has all 10 armor types."""
        # Find the ARMOR TYPE header element (not in TOC)
        armor_type_start = self.html_content.find('id="header-20-armor-type"')
        table_start = self.html_content.find('<table', armor_type_start)
        table_end = self.html_content.find('</table>', table_start) + len('</table>')
        table_content = self.html_content[table_start:table_end]
        
        # Verify all armor types are present
        expected_armors = [
            'Brigandine',
            'Hide',
            'Leather',
            'Padded',
            'Ring Mail',
            'Scale Mail',
            'Shield',
            'Studded Leather',
            'Metal Armor',
            'Special'
        ]
        
        for armor in expected_armors:
            self.assertIn(armor, table_content,
                         f"{armor} not found in ARMOR TYPE table")
    
    def test_armor_type_table_has_correct_roll_ranges(self):
        """Test that the ARMOR TYPE table has correct d20 roll ranges."""
        armor_type_start = self.html_content.find('id="header-20-armor-type"')
        table_start = self.html_content.find('<table', armor_type_start)
        table_end = self.html_content.find('</table>', table_start) + len('</table>')
        table_content = self.html_content[table_start:table_end]
        
        # Verify key roll ranges are present
        expected_rolls = [
            '<td>1</td>',
            '<td>2-5</td>',
            '<td>6-8</td>',
            '<td>9</td>',
            '<td>10</td>',
            '<td>11-12</td>',
            '<td>13-17</td>',
            '<td>18</td>',
            '<td>19-20</td>',
            '<td>00</td>'
        ]
        
        for roll in expected_rolls:
            self.assertIn(roll, table_content,
                         f"{roll} not found in ARMOR TYPE table")
    
    def test_metal_armor_table_exists(self):
        """Test that the METAL ARMOR table exists in the HTML."""
        self.assertIn('METAL ARMOR', self.html_content,
                     "METAL ARMOR header not found")
    
    def test_metal_armor_table_has_correct_header(self):
        """Test that the METAL ARMOR table has the correct header row."""
        # Find the METAL ARMOR header element (not in TOC)
        metal_armor_start = self.html_content.find('id="header-23-metal-armor"')
        self.assertGreater(metal_armor_start, -1, "METAL ARMOR section not found")
        
        # Find the first table after METAL ARMOR header
        table_start = self.html_content.find('<table', metal_armor_start)
        table_end = self.html_content.find('</table>', table_start) + len('</table>')
        
        table_content = self.html_content[table_start:table_end]
        
        # Check for correct header row
        self.assertIn('<th>d100 Roll</th>', table_content,
                     "d100 Roll header not found in METAL ARMOR table")
        self.assertIn('<th>Armor</th>', table_content,
                     "Armor header not found in METAL ARMOR table")
    
    def test_metal_armor_table_has_all_rows(self):
        """Test that the METAL ARMOR table has all 9 armor types."""
        # Find the METAL ARMOR header element (not in TOC)
        metal_armor_start = self.html_content.find('id="header-23-metal-armor"')
        table_start = self.html_content.find('<table', metal_armor_start)
        table_end = self.html_content.find('</table>', table_start) + len('</table>')
        table_content = self.html_content[table_start:table_end]
        
        # Verify all metal armor types are present
        expected_armors = [
            'Banded Mail',
            'Bronze Plate Mail',
            'Chain Mail',
            'Field Plate',
            'Full Plate',
            'Plate Mail',
            'Splint Mail',
            'Metal Shield',
            'Special'
        ]
        
        for armor in expected_armors:
            self.assertIn(armor, table_content,
                         f"{armor} not found in METAL ARMOR table")
    
    def test_malformed_headers_removed(self):
        """Test that the malformed header elements have been removed from the body content."""
        # These header IDs should not appear as actual headers in the body content
        # (they may still exist in the TOC which is generated before postprocessing)
        
        # Find the start of the actual body content (after the TOC)
        body_start = self.html_content.find('<section class="content">')
        if body_start == -1:
            # Fallback: look for the first H1 or the ARMOR TYPE section
            body_start = self.html_content.find('id="header-20-armor-type"')
        
        # After ARMOR TYPE header, the next header should be METAL ARMOR
        # not "d20 Roll" or "Armor" as separate headers
        armor_type_index = self.html_content.find('id="header-20-armor-type"', body_start)
        self.assertGreater(armor_type_index, -1, "ARMOR TYPE header should exist in body")
        
        # Check the section after ARMOR TYPE header
        armor_type_section_end = self.html_content.find('id="header-23-metal-armor"', armor_type_index)
        
        section_between = self.html_content[armor_type_index:armor_type_section_end]
        
        # These should not appear as actual <p id="header-21..."> or <p id="header-22..."> elements
        self.assertNotIn('<p id="header-21-d20-roll">', section_between,
                        "d20 Roll should not be a separate header paragraph")
        self.assertNotIn('<p id="header-22-armor">', section_between,
                        "Armor should not be a separate header paragraph")


if __name__ == '__main__':
    unittest.main()

