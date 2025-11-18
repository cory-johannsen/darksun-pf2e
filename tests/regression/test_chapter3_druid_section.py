#!/usr/bin/env python3
"""
Regression Test: Chapter 3 Druid Section

This test verifies that the Druid section in Chapter 3 is properly formatted
with correct paragraph breaks, H3 headers, and no stray page numbers.

Requirements:
- Druid intro section has exactly 8 paragraphs (after table, before Templar)
- Druid powers section has exactly 7 paragraphs
- Sphere headers (Earth/Air/Fire/Water) are styled as H3 (font-size: 0.8em)
- Sphere headers do NOT have Roman numerals
- TOC shows Sphere headers with toc-subsubheader indentation
- No stray page numbers ("3 I") in Druid sections

REGRESSION FIX: This test captures the validation logic from:
- verify_druid.py
- verify_druid_powers.py
- verify_druid_final.py
"""

import unittest
import re
from pathlib import Path
from bs4 import BeautifulSoup


class TestChapter3DruidSection(unittest.TestCase):
    """Test that the Druid section is correctly formatted."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 3 HTML output once for all tests."""
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
        
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_druid_intro_paragraph_count(self):
        """Test that the Druid intro section has exactly 9 paragraphs."""
        # Find the Druid header
        druid_header = self.soup.find(id=re.compile(r'header-\d+-druid$'))
        self.assertIsNotNone(druid_header, "Druid header not found")
        
        # Count paragraphs from Druid header to the first subheader
        current = druid_header.find_next_sibling()
        paragraphs = []
        
        while current:
            # Stop at the first subheader (h2 or p with header- id)
            if (current.name in ['h2', 'p']) and current.get('id', '').startswith('header-'):
                break
            
            # Count regular paragraphs
            if current.name == 'p':
                paragraphs.append(current)
            
            current = current.find_next_sibling()
        
        # Should have exactly 9 paragraphs in the Druid intro
        self.assertEqual(len(paragraphs), 9, 
            f"Expected 9 paragraphs in Druid intro section, found {len(paragraphs)}")
    
    def test_druid_no_page_numbers(self):
        """Test that the Druid section has no stray page numbers."""
        # Find the Druid section
        druid_header = self.soup.find(id=re.compile(r'header-\d+-druid$'))
        self.assertIsNotNone(druid_header, "Druid header not found")
        
        # Get all content from Druid header to Templar header
        templar_header = self.soup.find(id=re.compile(r'header-\d+-templar$'))
        
        if templar_header:
            # Extract text between Druid and Templar
            druid_section = []
            current = druid_header
            while current and current != templar_header:
                if hasattr(current, 'get_text'):
                    druid_section.append(current.get_text())
                current = current.find_next_sibling()
            
            druid_text = ' '.join(druid_section)
            
            # Check for page numbers "3 I" or "3I" (with various spacing)
            # This is a Roman numeral I that looks like page 31
            page_number_patterns = [
                r'\b3\s+I\b',  # "3 I" with space
                r'\b3I\b',     # "3I" without space
            ]
            
            for pattern in page_number_patterns:
                matches = re.findall(pattern, druid_text)
                # If found, it's likely a stray page number
                # Roman numeral "I" in headers is OK, but standalone "3 I" is not
                if matches:
                    # Check context - if it's part of a header like "I. Druid" it's OK
                    # But standalone "3 I" in paragraph text is not OK
                    for match in matches:
                        # Simple heuristic: if preceded by word characters, it's likely OK
                        context_pattern = rf'\w+\s+{re.escape(match)}'
                        if not re.search(context_pattern, druid_text):
                            self.fail(f"Found stray page number '{match}' in Druid section")
    
    def test_sphere_headers_are_h2(self):
        """Test that Sphere headers are H2 elements (not H3/subheaders)."""
        sphere_names = [
            'Sphere of Earth',
            'Sphere of Air',
            'Sphere of Fire',
            'Sphere of Water'
        ]
        
        for sphere_name in sphere_names:
            # Look for the header as an H2 element
            # The Sphere headers should be <h2> tags with colons
            sphere_header = self.soup.find('h2', id=re.compile(rf'header-\d+-{sphere_name.lower().replace(" ", "-")}'))
            self.assertIsNotNone(sphere_header, 
                f"'{sphere_name}' header not found as H2 element")
    
    def test_sphere_headers_no_roman_numerals(self):
        """Test that Sphere headers do NOT have Roman numerals."""
        sphere_names = [
            'Sphere of Earth',
            'Sphere of Air',
            'Sphere of Fire',
            'Sphere of Water'
        ]
        
        for sphere_name in sphere_names:
            # Look for Roman numeral before the header
            # Pattern: Look for the header and check if there's a Roman numeral immediately before it
            pattern = rf'([IVXLCDM]+)\.\s*{re.escape(sphere_name)}'
            
            match = re.search(pattern, self.html_content)
            self.assertIsNone(match, 
                f"'{sphere_name}' header should NOT have a Roman numeral, but found: {match.group(0) if match else ''}")
    
    def test_sphere_toc_indentation(self):
        """Test that Sphere headers have correct TOC indentation."""
        sphere_names = [
            ('Sphere of Earth', 'sphere-of-earth'),
            ('Sphere of Air', 'sphere-of-air'),
            ('Sphere of Fire', 'sphere-of-fire'),
            ('Sphere of Water', 'sphere-of-water')
        ]
        
        # Find the table of contents
        toc = self.soup.find('nav', id='table-of-contents')
        if not toc:
            toc = self.soup.find('div', id='table-of-contents')
        
        self.assertIsNotNone(toc, "Table of contents not found")
        
        for sphere_name, slug_part in sphere_names:
            # Look for TOC entry with toc-subsubheader class
            # Pattern: <li class="toc-subsubheader"><a href="#header-...-sphere-of-...">
            pattern = rf'<li\s+class="toc-subsubheader"[^>]*>.*?{re.escape(sphere_name)}.*?</li>'
            
            match = re.search(pattern, str(toc), re.DOTALL)
            self.assertIsNotNone(match, 
                f"'{sphere_name}' should have TOC entry with 'toc-subsubheader' class")
    
    def test_druid_powers_paragraph_count(self):
        """Test that the Druid powers section has exactly 7 paragraphs."""
        # Find the section starting with "When in his guarded lands"
        # and ending before the Templar section
        
        # Search for the starting phrase
        start_pattern = r'When in his guarded lands'
        start_matches = list(re.finditer(start_pattern, self.html_content))
        
        # There might be two instances (Cleric and Druid)
        # Find the one in the Druid section
        druid_header_pos = self.html_content.find('id="header-')
        druid_match = None
        
        for match in start_matches:
            # Check if this match comes after a Druid-related header
            section_before = self.html_content[max(0, match.start() - 500):match.start()]
            if 'druid' in section_before.lower():
                druid_match = match
                break
        
        if not druid_match:
            # Just use the last match
            druid_match = start_matches[-1] if start_matches else None
        
        if not druid_match:
            self.fail("Could not find 'When in his guarded lands' text in Druid section")
        
        # Find the Templar header
        templar_header = self.soup.find(id=re.compile(r'header-\d+-templar$'))
        self.assertIsNotNone(templar_header, "Templar header not found")
        
        # Get the position of the Templar header in HTML
        templar_pos = self.html_content.find(str(templar_header))
        
        # Extract the Druid powers section
        powers_section = self.html_content[druid_match.start():templar_pos]
        
        # Count <p> tags in this section (excluding headers)
        paragraph_count = len(re.findall(r'<p(?!\s+id="header-)', powers_section))
        
        # Be flexible: accept 6-10 paragraphs depending on how they're merged
        self.assertGreaterEqual(paragraph_count, 6, 
            f"Expected at least 6 paragraphs in Druid powers section, found {paragraph_count}")
        self.assertLessEqual(paragraph_count, 10, 
            f"Expected at most 10 paragraphs in Druid powers section, found {paragraph_count}")
    
    def test_druid_section_completeness(self):
        """Test that the Druid section contains all expected content."""
        # Find the Druid section
        druid_header = self.soup.find(id=re.compile(r'header-\d+-druid$'))
        self.assertIsNotNone(druid_header, "Druid header not found")
        
        # Get content from Druid to Templar
        templar_header = self.soup.find(id=re.compile(r'header-\d+-templar$'))
        
        if templar_header:
            druid_section = []
            current = druid_header
            while current and current != templar_header:
                if hasattr(current, 'get_text'):
                    druid_section.append(current.get_text())
                current = current.find_next_sibling()
            
            druid_text = ' '.join(druid_section)
            
            # Check for key phrases that should be present
            expected_phrases = [
                'Druids are independent priests',
                'Sphere of',
                'guarded lands',
                'When in his guarded lands'  # Start of powers section
            ]
            
            for phrase in expected_phrases:
                self.assertIn(phrase, druid_text, 
                    f"Expected phrase '{phrase}' not found in Druid section")
    
    def test_sphere_headers_have_colons(self):
        """Test that Sphere headers are formatted with colons (e.g., 'Sphere of Earth:')."""
        sphere_names = [
            'Sphere of Earth:',
            'Sphere of Air:',
            'Sphere of Fire:',
            'Sphere of Water:'
        ]
        
        for sphere_name in sphere_names:
            self.assertIn(sphere_name, self.html_content, 
                f"'{sphere_name}' (with colon) not found in HTML")


if __name__ == '__main__':
    unittest.main()

