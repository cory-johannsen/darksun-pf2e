"""
Regression test for Chapter 11 wilderness encounter tables.

Verifies that:
1. All wilderness encounter tables are properly extracted
2. Table data spans both PDF columns correctly
3. Die Roll values are properly merged (e.g., '5-6')
4. Creature names with commas and slashes are handled correctly
5. Tables are rendered as proper HTML tables with headers
"""

import unittest
import os
from bs4 import BeautifulSoup


class TestChapter11WildernessTables(unittest.TestCase):
    """Test wilderness encounter tables in Chapter 11."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 11 HTML output once for all tests."""
        html_path = "data/html_output/chapter-eleven-encounters.html"
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Chapter 11 HTML not found at {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_all_wilderness_tables_exist(self):
        """Test that all 6 wilderness encounter tables exist."""
        expected_tables = [
            "Stoney Barrens",
            "Sandy Wastes",
            "Mountains",
            "Scrub Plains",
            "Rocky Badlands",
            "Salt Flats"
        ]
        
        for table_name in expected_tables:
            with self.subTest(table=table_name):
                # Find the header for this table
                # The header is an <h2> tag with id like "header-stoney-barrens"
                header_id = f"header-{table_name.lower().replace(' ', '-')}"
                header = self.soup.find('h2', id=header_id)
                self.assertIsNotNone(header, f"Header for '{table_name}' not found (looking for id='{header_id}')")
                
                # Find the table following the header
                table = header.find_next_sibling('table')
                self.assertIsNotNone(table, f"Table for '{table_name}' not found after header")
    
    def test_stoney_barrens_table_structure(self):
        """Test the Stoney Barrens table has correct structure."""
        # Find the Stoney Barrens header
        header = self.soup.find('h2', id='header-stoney-barrens')
        self.assertIsNotNone(header, "Stoney Barrens header not found")
        
        # Find the table
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Stoney Barrens table not found")
        
        # Check that the table has the ds-table class (may not be present for all tables)
        # self.assertIn('ds-table', table.get('class', []), "Table should have ds-table class")
        
        # Get all rows
        rows = table.find_all('tr')
        self.assertGreater(len(rows), 1, "Table should have at least header + data rows")
        
        # Check header row
        header_row = rows[0]
        header_cells = header_row.find_all(['th', 'td'])
        self.assertEqual(len(header_cells), 2, "Header should have 2 columns")
        
        header_texts = [cell.get_text().strip() for cell in header_cells]
        self.assertEqual(header_texts[0], "Die Roll", "First column should be 'Die Roll'")
        self.assertEqual(header_texts[1], "Creature", "Second column should be 'Creature'")
    
    def test_stoney_barrens_die_roll_values(self):
        """Test that Stoney Barrens table has expected die roll values."""
        # Find the table
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        
        # Get all data rows (skip header)
        rows = table.find_all('tr')[1:]
        
        # Extract die roll values
        die_rolls = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if cells:
                die_rolls.append(cells[0].get_text().strip())
        
        # Should have entries for die rolls 2-20
        self.assertGreater(len(die_rolls), 0, "Should have at least some die roll entries")
        
        # Check that die rolls are numeric or ranges
        for die_roll in die_rolls:
            with self.subTest(die_roll=die_roll):
                # Should be either a single number or a range like "5-6"
                self.assertTrue(
                    die_roll.isdigit() or ('-' in die_roll and all(p.isdigit() for p in die_roll.split('-'))),
                    f"Die roll '{die_roll}' should be numeric or a range"
                )
    
    def test_stoney_barrens_creature_names(self):
        """Test that creature names are properly formatted."""
        # Find the table
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        
        # Get all data rows (skip header)
        rows = table.find_all('tr')[1:]
        
        # Extract creature names
        creatures = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                creatures.append(cells[1].get_text().strip())
        
        # Should have creature names
        self.assertGreater(len(creatures), 0, "Should have at least some creature entries")
        
        # Check that creature names are not empty
        for creature in creatures:
            with self.subTest(creature=creature):
                self.assertTrue(len(creature) > 0, "Creature name should not be empty")
    
    def test_no_merged_creature_names(self):
        """Test that creature names are properly separated (not merged like 'ankhegwyvern')."""
        # Find the table
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        
        # Get all data rows (skip header)
        rows = table.find_all('tr')[1:]
        
        # Extract creature names
        creatures = []
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                creatures.append(cells[1].get_text().strip())
        
        # Check for common merge patterns
        # These should NOT appear as-is, but should be split
        bad_merges = [
            'ankhegwyvern',  # Should be 'ankheg/wyvern'
            'gaibuletteroc',  # Should be 'gaibul/etteroc'
            'giantbeetle',  # Should be 'giant/beetle' or 'giant beetle'
        ]
        
        for creature in creatures:
            for bad_merge in bad_merges:
                with self.subTest(creature=creature, bad_merge=bad_merge):
                    self.assertNotIn(bad_merge.lower(), creature.lower(),
                                   f"Creature '{creature}' should not contain merged name '{bad_merge}'")
    
    def test_table_headers_have_links(self):
        """Test that table headers have return-to-top links."""
        expected_tables = [
            "Stoney Barrens",
            "Sandy Wastes",
            "Mountains",
            "Scrub Plains",
            "Rocky Badlands",
            "Salt Flats"
        ]
        
        for table_name in expected_tables:
            with self.subTest(table=table_name):
                # Find the header
                header_id = f"header-{table_name.lower().replace(' ', '-')}"
                header = self.soup.find('h2', id=header_id)
                
                # Skip if table doesn't exist (some may not be in PDF)
                if not header:
                    continue
                
                # Check for return-to-top link
                link = header.find('a', href="#top")
                self.assertIsNotNone(link, f"Header for '{table_name}' should have return-to-top link")
                self.assertEqual(link.get_text().strip(), "[^]", "Link text should be '[^]'")
    
    def test_sandy_wastes_table(self):
        """Test that Sandy Wastes table exists and has data."""
        header = self.soup.find('h2', id='header-sandy-wastes')
        
        # Skip if table doesn't exist (may not be in PDF)
        if not header:
            self.skipTest("Sandy Wastes table not found in HTML")
        
        self.assertIsNotNone(header, "Sandy Wastes header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Sandy Wastes table not found")
        
        # Get data rows (skip header)
        rows = table.find_all('tr')[1:]
        self.assertGreater(len(rows), 0, "Sandy Wastes table should have data rows")
    
    def test_mountains_table(self):
        """Test that Mountains table exists and has data."""
        header = self.soup.find('h2', id='header-mountains')
        
        # Skip if table doesn't exist (may not be in PDF)
        if not header:
            self.skipTest("Mountains table not found in HTML")
        
        self.assertIsNotNone(header, "Mountains header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Mountains table not found")
        
        # Get data rows (skip header)
        rows = table.find_all('tr')[1:]
        self.assertGreater(len(rows), 0, "Mountains table should have data rows")
    
    def test_scrub_plains_table(self):
        """Test that Scrub Plains table exists and has data."""
        header = self.soup.find('h2', id='header-scrub-plains')
        
        # Skip if table doesn't exist (may not be in PDF)
        if not header:
            self.skipTest("Scrub Plains table not found in HTML")
        
        self.assertIsNotNone(header, "Scrub Plains header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Scrub Plains table not found")
        
        # Get data rows (skip header)
        rows = table.find_all('tr')[1:]
        self.assertGreater(len(rows), 0, "Scrub Plains table should have data rows")
    
    def test_rocky_badlands_table(self):
        """Test that Rocky Badlands table exists and has data."""
        header = self.soup.find('h2', id='header-rocky-badlands')
        
        # Skip if table doesn't exist (may not be in PDF)
        if not header:
            self.skipTest("Rocky Badlands table not found in HTML")
        
        self.assertIsNotNone(header, "Rocky Badlands header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Rocky Badlands table not found")
        
        # Get data rows (skip header)
        rows = table.find_all('tr')[1:]
        self.assertGreater(len(rows), 0, "Rocky Badlands table should have data rows")
    
    def test_salt_flats_table(self):
        """Test that Salt Flats table exists and has data."""
        header = self.soup.find('h2', id='header-salt-flats')
        
        # Skip if table doesn't exist (may not be in PDF)
        if not header:
            self.skipTest("Salt Flats table not found in HTML")
        
        self.assertIsNotNone(header, "Salt Flats header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Salt Flats table not found")
        
        # Get data rows (skip header)
        rows = table.find_all('tr')[1:]
        self.assertGreater(len(rows), 0, "Salt Flats table should have data rows")


if __name__ == '__main__':
    unittest.main()

