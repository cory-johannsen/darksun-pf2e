"""
Regression test for Chapter 11 wilderness encounter tables - Scrub Plains, Rocky Badlands, Salt Flats.

Verifies that:
1. All three wilderness encounter tables are properly extracted
2. Table data spans both PDF columns correctly
3. Die Roll values are properly extracted (2-20)
4. Creature names are correct
5. Tables are rendered as proper HTML tables with headers
"""

import unittest
import os
from bs4 import BeautifulSoup


class TestChapter11NewWildernessTables(unittest.TestCase):
    """Test Scrub Plains, Rocky Badlands, and Salt Flats tables in Chapter 11."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 11 HTML output once for all tests."""
        html_path = "data/html_output/chapter-eleven-encounters.html"
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Chapter 11 HTML not found at {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_scrub_plains_table_exists(self):
        """Test that Scrub Plains table exists."""
        # Find the header for this table (now H2 instead of P)
        header_id = "header-scrub-plains"
        header = self.soup.find('h2', id=header_id)
        self.assertIsNotNone(header, f"Header for 'Scrub Plains' not found (looking for id='{header_id}')")
        
        # Find the table following the header
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, f"Table for 'Scrub Plains' not found after header")
    
    def test_scrub_plains_table_has_19_rows(self):
        """Test that Scrub Plains table has exactly 19 data rows (D20 rolls 2-20)."""
        header = self.soup.find('h2', id='header-scrub-plains')
        self.assertIsNotNone(header, "Scrub Plains header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Scrub Plains table not found")
        
        rows = table.find_all('tr')[1:]  # Skip header
        self.assertEqual(len(rows), 19, f"Expected 19 rows, got {len(rows)}")
    
    def test_scrub_plains_complete_data(self):
        """Test complete Scrub Plains table against reference."""
        expected_data = [
            ("2", "genie, jann"),
            ("3", "remorhaz"),
            ("4", "behir"),
            ("5", "ant lion, giant"),
            ("6", "mekillot"),
            ("7", "silk wyrm"),
            ("8", "cheetah"),
            ("9", "erdlu"),
            ("10", "gith"),
            ("11", "elves/slaves"),
            ("12", "kank"),
            ("13", "rat, giant"),
            ("14", "jaguar"),
            ("15", "scorpion, large"),
            ("16", "spider, giant"),
            ("17", "bat, huge"),
            ("18", "plant, carnivorous, man trap"),
            ("19", "pseudodragon"),
            ("20", "gaj"),
        ]
        
        header = self.soup.find('h2', id='header-scrub-plains')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]  # Skip header
        
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                cells = rows[i].find_all(['td', 'th'])
                self.assertEqual(cells[0].get_text().strip(), expected_roll)
                self.assertEqual(cells[1].get_text().strip(), expected_creature)
    
    def test_rocky_badlands_table_exists(self):
        """Test that Rocky Badlands table exists."""
        # Rocky Badlands header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            if 'Rocky Badlands' in h2.get_text():
                header = h2
                break
        
        self.assertIsNotNone(header, "Header for 'Rocky Badlands' not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, f"Table for 'Rocky Badlands' not found after header")
    
    def test_rocky_badlands_table_has_19_rows(self):
        """Test that Rocky Badlands table has exactly 19 data rows (D20 rolls 2-20)."""
        # Rocky Badlands header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            if 'Rocky Badlands' in h2.get_text():
                header = h2
                break
        
        self.assertIsNotNone(header, "Rocky Badlands header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Rocky Badlands table not found")
        
        rows = table.find_all('tr')[1:]  # Skip header
        self.assertEqual(len(rows), 19, f"Expected 19 rows, got {len(rows)}")
    
    def test_rocky_badlands_complete_data(self):
        """Test complete Rocky Badlands table against reference."""
        expected_data = [
            ("2", "aarakocra"),
            ("3", "dragonne"),
            ("4", "giant-kin, cyclops"),
            ("5", "roc"),
            ("6", "ankheg"),
            ("7", "belgoi"),
            ("8", "lizard, giant"),
            ("9", "beetle, fire"),
            ("10", "spider, large"),
            ("11", "gith/dwarves"),
            ("12", "kluzd"),
            ("13", "rat, giant"),
            ("14", "common lion"),
            ("15", "hornet"),
            ("16", "bat, huge"),
            ("17", "braxat"),
            ("18", "giant"),
            ("19", "genie, efreeti"),
            ("20", "ant, swarm"),
        ]
        
        # Rocky Badlands header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            if 'Rocky Badlands' in h2.get_text():
                header = h2
                break
        
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]  # Skip header
        
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                cells = rows[i].find_all(['td', 'th'])
                self.assertEqual(cells[0].get_text().strip(), expected_roll)
                self.assertEqual(cells[1].get_text().strip(), expected_creature)
    
    def test_salt_flats_table_exists(self):
        """Test that Salt Flats table exists."""
        # Salt Flats header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            text = h2.get_text()
            if 'Salt Flats' in text and 'Rocky Badlands' not in text:
                header = h2
                break
        
        self.assertIsNotNone(header, "Header for 'Salt Flats' not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, f"Table for 'Salt Flats' not found after header")
    
    def test_salt_flats_table_has_19_rows(self):
        """Test that Salt Flats table has exactly 19 data rows (D20 rolls 2-20)."""
        # Salt Flats header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            text = h2.get_text()
            if 'Salt Flats' in text and 'Rocky Badlands' not in text:
                header = h2
                break
        
        self.assertIsNotNone(header, "Salt Flats header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Salt Flats table not found")
        
        rows = table.find_all('tr')[1:]  # Skip header
        self.assertEqual(len(rows), 19, f"Expected 19 rows, got {len(rows)}")
    
    def test_salt_flats_complete_data(self):
        """Test complete Salt Flats table against reference."""
        expected_data = [
            ("2", "basilisk, dracolisk"),
            ("3", "zombie, juju"),
            ("4", "snake, spitting"),
            ("5", "ant, giant"),
            ("6", "wasp"),
            ("7", "wyvern"),
            ("8", "hornet"),
            ("9", "skeleton"),
            ("10", "scorpion, huge"),
            ("11", "zombie"),
            ("12", "centipede, giant"),
            ("13", "spider, large"),
            ("14", "lizard, giant"),
            ("15", "bat, large"),
            ("16", "skeleton"),
            ("17", "spider, phase"),
            ("18", "zombie, monster"),
            ("19", "remorhaz"),
            ("20", "gaj"),
        ]
        
        # Salt Flats header is now an H2
        all_h2s = self.soup.find_all('h2')
        header = None
        for h2 in all_h2s:
            text = h2.get_text()
            if 'Salt Flats' in text and 'Rocky Badlands' not in text:
                header = h2
                break
        
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]  # Skip header
        
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                cells = rows[i].find_all(['td', 'th'])
                self.assertEqual(cells[0].get_text().strip(), expected_roll)
                self.assertEqual(cells[1].get_text().strip(), expected_creature)


if __name__ == '__main__':
    unittest.main()

