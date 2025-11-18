"""
Regression tests for Chapter 15 processing - New Spells.

Tests:
- Proper H2 and H3 header structure
- Find Familiar table extraction (3 columns, 7 rows)
- Mount table extraction (2 columns, 5 rows)
"""

import unittest
import json
import os
from bs4 import BeautifulSoup


class TestChapter15Processing(unittest.TestCase):
    """Test Chapter 15 (New Spells) processing."""

    @classmethod
    def setUpClass(cls):
        """Load the HTML output for Chapter 15."""
        html_path = os.path.join(
            os.path.dirname(__file__),
            "../../data/html_output/chapter-fifteen-new-spells.html"
        )
        
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Chapter 15 HTML not found at {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')

    def test_first_level_spells_is_h2(self):
        """Test that 'First Level Spells' is an H2 header."""
        # Find all H2 elements
        h2_elements = self.soup.find_all('h2')
        h2_texts = [h2.get_text(strip=True) for h2 in h2_elements]
        
        # Check if "First Level Spells" is in H2 (may have roman numeral prefix)
        matching = [text for text in h2_texts if 'First Level Spells' in text]
        
        self.assertTrue(
            len(matching) > 0,
            f"'First Level Spells' not found as H2. Found H2s: {h2_texts}"
        )

    def test_charm_person_is_h3(self):
        """Test that 'Charm Person' is an H3 header."""
        # Find all H3 elements
        h3_elements = self.soup.find_all('h3')
        h3_texts = [h3.get_text(strip=True) for h3 in h3_elements]
        
        # Check if "Charm Person" is in H3
        matching = [text for text in h3_texts if 'Charm Person' in text]
        
        self.assertTrue(
            len(matching) > 0,
            f"'Charm Person' not found as H3. Found H3s: {h3_texts}"
        )

    def test_find_familiar_is_h3(self):
        """Test that 'Find Familiar' is an H3 header."""
        # Find all H3 elements
        h3_elements = self.soup.find_all('h3')
        h3_texts = [h3.get_text(strip=True) for h3 in h3_elements]
        
        # Check if "Find Familiar" is in H3
        matching = [text for text in h3_texts if 'Find Familiar' in text]
        
        self.assertTrue(
            len(matching) > 0,
            f"'Find Familiar' not found as H3. Found H3s: {h3_texts}"
        )

    def test_mount_is_h3(self):
        """Test that 'Mount' is an H3 header."""
        # Find all H3 elements
        h3_elements = self.soup.find_all('h3')
        h3_texts = [h3.get_text(strip=True) for h3 in h3_elements]
        
        # Check if "Mount" is in H3 (first occurrence, not the table header)
        # Strip the back-to-top link "[^]" before checking
        matching = [text for text in h3_texts if 'Mount' in text.replace('[^]', '').strip()]
        
        self.assertTrue(
            len(matching) > 0,
            f"'Mount' not found as H3. Found H3s: {h3_texts}"
        )

    def test_find_familiar_table_exists(self):
        """Test that the Find Familiar table exists."""
        tables = self.soup.find_all('table')
        
        # Look for table with "Die Roll", "Familiar", "Sensory Powers" headers
        familiar_table = None
        for table in tables:
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True) for th in headers]
            if 'Die Roll' in header_texts and 'Familiar' in header_texts and 'Sensory Powers' in header_texts:
                familiar_table = table
                break
        
        self.assertIsNotNone(
            familiar_table,
            f"Find Familiar table not found. Found {len(tables)} tables total."
        )

    def test_find_familiar_table_structure(self):
        """Test that the Find Familiar table has correct structure."""
        tables = self.soup.find_all('table')
        
        # Find the Find Familiar table
        familiar_table = None
        for table in tables:
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True) for th in headers]
            if 'Die Roll' in header_texts and 'Familiar' in header_texts:
                familiar_table = table
                break
        
        self.assertIsNotNone(familiar_table, "Find Familiar table not found")
        
        # Check column count
        headers = familiar_table.find_all('th')
        self.assertEqual(
            len(headers),
            3,
            f"Expected 3 columns in Find Familiar table, found {len(headers)}"
        )
        
        # Check row count (should be 7 data rows + 1 header row = 8 total)
        # Note: render_table doesn't generate <tbody>, all rows are direct children
        all_rows = familiar_table.find_all('tr')
        self.assertEqual(
            len(all_rows),
            8,  # 1 header row + 7 data rows
            f"Expected 8 total rows in Find Familiar table, found {len(all_rows)}"
        )
        
        # Verify first data row (second tr, after header)
        data_rows = [row for row in all_rows if row.find('td')]
        self.assertEqual(
            len(data_rows),
            7,
            f"Expected 7 data rows, found {len(data_rows)}"
        )

    def test_mount_table_exists(self):
        """Test that the Mount table exists."""
        tables = self.soup.find_all('table')
        
        # Look for table with "Caster Level", "Mount" headers
        mount_table = None
        for table in tables:
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True) for th in headers]
            if 'Caster Level' in header_texts and 'Mount' in header_texts:
                mount_table = table
                break
        
        self.assertIsNotNone(
            mount_table,
            f"Mount table not found. Found {len(tables)} tables total."
        )

    def test_mount_table_structure(self):
        """Test that the Mount table has correct structure."""
        tables = self.soup.find_all('table')
        
        # Find the Mount table
        mount_table = None
        for table in tables:
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True) for th in headers]
            if 'Caster Level' in header_texts and 'Mount' in header_texts:
                mount_table = table
                break
        
        self.assertIsNotNone(mount_table, "Mount table not found")
        
        # Check column count
        headers = mount_table.find_all('th')
        self.assertEqual(
            len(headers),
            2,
            f"Expected 2 columns in Mount table, found {len(headers)}"
        )
        
        # Check row count (should be 5 data rows + 1 header row = 6 total)
        # Note: render_table doesn't generate <tbody>, all rows are direct children
        all_rows = mount_table.find_all('tr')
        self.assertEqual(
            len(all_rows),
            6,  # 1 header row + 5 data rows
            f"Expected 6 total rows in Mount table, found {len(all_rows)}"
        )
        
        # Verify first data row (second tr, after header)
        data_rows = [row for row in all_rows if row.find('td')]
        self.assertEqual(
            len(data_rows),
            5,
            f"Expected 5 data rows, found {len(data_rows)}"
        )

    def test_no_orphaned_table_headers(self):
        """Test that table headers are not in the regular text flow."""
        # Check that "Die Roll Familiar" and "Sensory Powers" don't appear as headers in the text
        content = self.soup.find('section', class_='content')
        self.assertIsNotNone(content, "Content section not found")
        
        # Get all paragraph and header text (excluding tables)
        text_elements = content.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
        all_text = ' '.join([elem.get_text() for elem in text_elements])
        
        # These should NOT appear as standalone headers
        self.assertNotIn(
            'V.  [^] Die Roll Familiar',
            all_text,
            "Table header 'Die Roll Familiar' should not appear as standalone header"
        )
        self.assertNotIn(
            'VI.  [^] Sensory Powers',
            all_text,
            "Table header 'Sensory Powers' should not appear as standalone header"
        )

    def test_table_css_class(self):
        """Test that tables use the ds-table CSS class."""
        tables = self.soup.find_all('table')
        
        for table in tables:
            classes = table.get('class', [])
            self.assertIn(
                'ds-table',
                classes,
                f"Table missing 'ds-table' CSS class: {table}"
            )
    
    def test_spell_paragraph_breaks(self):
        """Test that spell descriptions have proper paragraph breaks."""
        # Find the Detect Psionics spell
        content = self.soup.find('section', class_='content')
        self.assertIsNotNone(content, "Content section not found")
        
        # Get all paragraphs after the Detect Psionics header
        detect_psionics_header = content.find('h3', id='header-detect-psionics-(divination)')
        self.assertIsNotNone(detect_psionics_header, "Detect Psionics header not found")
        
        # Get the next few elements (stat block + paragraphs)
        next_elements = []
        current = detect_psionics_header.find_next_sibling()
        for _ in range(10):  # Get up to 10 following elements
            if current and current.name in ['div', 'p']:
                next_elements.append(current)
                current = current.find_next_sibling()
            else:
                break
        
        # Find paragraphs that start with our expected phrases
        paragraph_texts = [elem.get_text(strip=True) for elem in next_elements if elem.name == 'p']
        
        # Check that key phrases start their own paragraphs
        has_at_level_paragraph = any(text.startswith('At level') for text in paragraph_texts)
        has_casters_who_paragraph = any(text.startswith('Casters who') for text in paragraph_texts)
        has_finally_paragraph = any(text.startswith('Finally,') for text in paragraph_texts)
        
        self.assertTrue(
            has_at_level_paragraph,
            f"'At level' should start its own paragraph. Paragraphs found: {paragraph_texts[:5]}"
        )
        self.assertTrue(
            has_casters_who_paragraph,
            f"'Casters who' should start its own paragraph. Paragraphs found: {paragraph_texts[:5]}"
        )
        self.assertTrue(
            has_finally_paragraph,
            f"'Finally,' should start its own paragraph. Paragraphs found: {paragraph_texts[:5]}"
        )
    
    def test_raze_spell_paragraph_breaks(self):
        """Test that the Raze spell has 4 distinct paragraphs."""
        # Find the Raze spell header
        content = self.soup.find('section', class_='content')
        self.assertIsNotNone(content, "Content section not found")
        
        raze_header = content.find('h3', id='header-raze-(alteration)')
        self.assertIsNotNone(raze_header, "Raze (Alteration) header not found")
        
        # Get the next few elements (stat block + paragraphs)
        next_elements = []
        current = raze_header.find_next_sibling()
        for _ in range(10):  # Get up to 10 following elements
            if current and current.name in ['div', 'p']:
                next_elements.append(current)
                current = current.find_next_sibling()
            else:
                break
        
        # Find paragraphs (skip the stat block div)
        paragraph_texts = [elem.get_text(strip=True) for elem in next_elements if elem.name == 'p']
        
        # Check that we have at least 3 paragraphs (description paragraphs, not counting material components)
        self.assertGreaterEqual(
            len(paragraph_texts),
            3,
            f"Expected at least 3 paragraphs for Raze spell, found {len(paragraph_texts)}"
        )
        
        # Check that key phrases start their own paragraphs
        has_this_spell_paragraph = any(text.startswith('This spell duplicates') for text in paragraph_texts)
        has_casting_paragraph = any(text.startswith('The casting of the spell') for text in paragraph_texts)
        has_ash_paragraph = any(text.startswith('The ash created') for text in paragraph_texts)
        has_material_paragraph = any(text.startswith('The material') for text in paragraph_texts)
        
        self.assertTrue(
            has_this_spell_paragraph,
            f"'This spell duplicates' should start paragraph 1. Paragraphs found: {paragraph_texts}"
        )
        self.assertTrue(
            has_casting_paragraph,
            f"'The casting of the spell' should start paragraph 2. Paragraphs found: {paragraph_texts}"
        )
        self.assertTrue(
            has_ash_paragraph,
            f"'The ash created' should start paragraph 3. Paragraphs found: {paragraph_texts}"
        )
        self.assertTrue(
            has_material_paragraph,
            f"'The material' should start paragraph 4. Paragraphs found: {paragraph_texts}"
        )
    
    def test_transmute_sand_to_stone_title(self):
        """Test that 'Transmute Sand to Stone' title is properly formatted."""
        # Find the spell header - it may have various ID formats due to character spacing
        content = self.soup.find('section', class_='content')
        self.assertIsNotNone(content, "Content section not found")
        
        # Look for the header by searching for text containing "Transmute" and "Sand"
        # Note: ID may have spaced-out letters, so we search by text content
        headers = content.find_all('h3')
        
        found_correct_title = False
        for header in headers:
            title_text = header.get_text(strip=True)
            # Look for Transmute spell with "Sand" in the title
            if 'Transmute' in title_text and 'Sand' in title_text:
                # Check that it's properly formatted
                if 'Sand to Stone' in title_text and 'Sandto' not in title_text:
                    found_correct_title = True
                    # Also check spacing around "Alteration"
                    self.assertIn('(Alteration)', title_text, 
                                f"Title should have '(Alteration)' without extra spaces: {title_text}")
                    break
        
        self.assertTrue(found_correct_title, 
                       "Could not find properly formatted 'Transmute Sand to Stone' title (should be 'Sand to Stone', not 'Sandto Stone')")
    
    def test_transmute_sand_to_stone_paragraph_breaks(self):
        """Test that Transmute Sand to Stone has proper paragraph breaks."""
        content = self.soup.find('section', class_='content')
        self.assertIsNotNone(content, "Content section not found")
        
        # Find the Transmute Sand to Stone header
        headers = content.find_all('p', id=lambda x: x and 'transmute' in x.lower() and 'stone' in x.lower())
        
        if not headers:
            self.skipTest("Transmute Sand to Stone header not found")
        
        header = headers[0]
        
        # Get the next few elements (stat block + paragraphs)
        next_elements = []
        current = header.find_next_sibling()
        for _ in range(10):
            if current and current.name in ['div', 'p']:
                next_elements.append(current)
                current = current.find_next_sibling()
            else:
                break
        
        # Find paragraphs (skip stat blocks)
        paragraph_texts = [elem.get_text(strip=True) for elem in next_elements if elem.name == 'p']
        
        # Check for expected paragraph breaks
        has_this_spell_paragraph = any(text.startswith('This spell') for text in paragraph_texts)
        has_material_paragraph = any(text.startswith('The material') for text in paragraph_texts)
        
        self.assertTrue(
            has_this_spell_paragraph,
            f"'This spell' should start a paragraph. Paragraphs: {paragraph_texts[:3]}"
        )
        self.assertTrue(
            has_material_paragraph,
            f"'The material' should start its own paragraph. Paragraphs: {paragraph_texts[-2:]}"
        )


if __name__ == '__main__':
    unittest.main()

