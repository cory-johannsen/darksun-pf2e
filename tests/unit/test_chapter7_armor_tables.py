"""Unit tests for Chapter 7 armor table building functions."""

import unittest
from tools.pdf_pipeline.postprocessors.chapter_7_postprocessing import (
    _build_armor_type_table,
    _build_metal_armor_table
)


class TestArmorTables(unittest.TestCase):
    """Test suite for armor table building functions."""

    def test_build_armor_type_table(self):
        """Test that ARMOR TYPE table is built correctly from paragraph text."""
        # Sample HTML with the malformed armor type section
        input_html = '''<p id="header-20-armor-type"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">ARMOR TYPE</span></p><p id="header-21-d20-roll">XIV.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">d20 Roll</span></p><p id="header-22-armor">XV.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Armor</span></p><p>Brigandine Hide 2-5 Leather 6-8 Padded Ring Mail 11-12 Scale Mail 13-17 Shield Studded Leather Metal Armor Special</p>'''
        
        result = _build_armor_type_table(input_html)
        
        # Verify the table is built
        self.assertIn('<table class="ds-table">', result)
        self.assertIn('<tr><th>d20 Roll</th><th>Armor</th></tr>', result)
        
        # Verify all 10 armor types are in the table
        self.assertIn('<td>1</td><td>Brigandine</td>', result)
        self.assertIn('<td>2-5</td><td>Hide</td>', result)
        self.assertIn('<td>6-8</td><td>Leather</td>', result)
        self.assertIn('<td>9</td><td>Padded</td>', result)
        self.assertIn('<td>10</td><td>Ring Mail</td>', result)
        self.assertIn('<td>11-12</td><td>Scale Mail</td>', result)
        self.assertIn('<td>13-17</td><td>Shield</td>', result)
        self.assertIn('<td>18</td><td>Studded Leather</td>', result)
        self.assertIn('<td>19-20</td><td>Metal Armor</td>', result)
        self.assertIn('<td>00</td><td>Special</td>', result)
        
        # Verify the malformed headers are removed
        self.assertNotIn('header-21-d20-roll', result)
        self.assertNotIn('header-22-armor', result)
        
        # Verify the ARMOR TYPE header is still there
        self.assertIn('header-20-armor-type', result)

    def test_build_metal_armor_table(self):
        """Test that METAL ARMOR table is built correctly from paragraph text."""
        # Sample HTML with the malformed metal armor section
        input_html = '''<p id="header-23-metal-armor"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">METAL ARMOR</span></p><p id="header-24-di00-roll">XVII.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">dI00 roll</span></p><p id="header-25-armor">XVIII.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Armor</span></p><p>01-15 Banded Mail 16-23 Bronze Plate Mail 24-45 Chain Mail 46-50 Field Plate 51-55 Full Plate 56-65 Plate Mail 66-75 Splint Mail 76-99 Metal Shield Special</p><p>Magical adjustment to Armor Class is determined normally. Special armor is also determined normally, but elven chain mail does not exist on Athas; reroll if necessary.</p>'''
        
        result = _build_metal_armor_table(input_html)
        
        # Verify the table is built
        self.assertIn('<table class="ds-table">', result)
        self.assertIn('<tr><th>d100 Roll</th><th>Armor</th></tr>', result)
        
        # Verify all 9 armor types are in the table
        self.assertIn('<td>01-15</td><td>Banded Mail</td>', result)
        self.assertIn('<td>16-23</td><td>Bronze Plate Mail</td>', result)
        self.assertIn('<td>24-45</td><td>Chain Mail</td>', result)
        self.assertIn('<td>46-50</td><td>Field Plate</td>', result)
        self.assertIn('<td>51-55</td><td>Full Plate</td>', result)
        self.assertIn('<td>56-65</td><td>Plate Mail</td>', result)
        self.assertIn('<td>66-75</td><td>Splint Mail</td>', result)
        self.assertIn('<td>76-99</td><td>Metal Shield</td>', result)
        self.assertIn('<td>00</td><td>Special</td>', result)
        
        # Verify the malformed headers are removed
        self.assertNotIn('header-24-di00-roll', result)
        self.assertNotIn('header-25-armor', result)
        
        # Verify the METAL ARMOR header is still there
        self.assertIn('header-23-metal-armor', result)
        
        # Verify the explanation paragraph is still present
        self.assertIn('Magical adjustment to Armor Class is determined normally', result)

    def test_armor_type_table_structure(self):
        """Test that the ARMOR TYPE table has correct structure."""
        input_html = '''<p id="header-20-armor-type"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">ARMOR TYPE</span></p><p id="header-21-d20-roll">XIV.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">d20 Roll</span></p><p id="header-22-armor">XV.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Armor</span></p><p>Brigandine Hide 2-5 Leather 6-8 Padded Ring Mail 11-12 Scale Mail 13-17 Shield Studded Leather Metal Armor Special</p>'''
        
        result = _build_armor_type_table(input_html)
        
        # Count the number of table rows (header + 10 data rows = 11 total)
        row_count = result.count('<tr>')
        self.assertEqual(row_count, 11, f"Expected 11 rows (1 header + 10 data), got {row_count}")
        
        # Verify it's a 2-column table
        # Header row should have 2 <th> tags
        self.assertEqual(result.count('<th>'), 2)
        
        # Each data row should have 2 <td> tags (20 total for 10 rows)
        self.assertEqual(result.count('<td>'), 20)

    def test_metal_armor_table_structure(self):
        """Test that the METAL ARMOR table has correct structure."""
        input_html = '''<p id="header-23-metal-armor"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">METAL ARMOR</span></p><p id="header-24-di00-roll">XVII.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">dI00 roll</span></p><p id="header-25-armor">XVIII.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Armor</span></p><p>01-15 Banded Mail 16-23 Bronze Plate Mail 24-45 Chain Mail 46-50 Field Plate 51-55 Full Plate 56-65 Plate Mail 66-75 Splint Mail 76-99 Metal Shield Special</p><p>Magical adjustment to Armor Class is determined normally. Special armor is also determined normally, but elven chain mail does not exist on Athas; reroll if necessary.</p>'''
        
        result = _build_metal_armor_table(input_html)
        
        # Count the number of table rows (header + 9 data rows = 10 total)
        row_count = result.count('<tr>')
        self.assertEqual(row_count, 10, f"Expected 10 rows (1 header + 9 data), got {row_count}")
        
        # Verify it's a 2-column table
        # Header row should have 2 <th> tags
        self.assertEqual(result.count('<th>'), 2)
        
        # Each data row should have 2 <td> tags (18 total for 9 rows)
        self.assertEqual(result.count('<td>'), 18)

    def test_armor_type_table_no_match(self):
        """Test that function handles missing pattern gracefully."""
        input_html = '''<p>Some other content</p>'''
        
        result = _build_armor_type_table(input_html)
        
        # Should return unchanged HTML
        self.assertEqual(result, input_html)

    def test_metal_armor_table_no_match(self):
        """Test that function handles missing pattern gracefully."""
        input_html = '''<p>Some other content</p>'''
        
        result = _build_metal_armor_table(input_html)
        
        # Should return unchanged HTML
        self.assertEqual(result, input_html)


if __name__ == '__main__':
    unittest.main()

