"""
TDD Test Suite for Chapter 11 Wilderness Encounter Tables
Testing against reference data provided by user
"""

import unittest
import os
import sys
from bs4 import BeautifulSoup

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStoneyBarrensTableExtraction(unittest.TestCase):
    """Test Stoney Barrens table extraction against reference data."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 11 HTML output."""
        html_path = "data/html_output/chapter-eleven-encounters.html"
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Chapter 11 HTML not found at {html_path}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_stoney_barrens_has_20_rows(self):
        """Test that Stoney Barrens table has exactly 19 data rows (covering die rolls 2-20)."""
        header = self.soup.find('h2', id='header-stoney-barrens')
        self.assertIsNotNone(header, "Stoney Barrens header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Stoney Barrens table not found")
        
        rows = table.find_all('tr')[1:]  # Skip header
        self.assertEqual(len(rows), 19, f"Expected 19 rows (die rolls 2-20), got {len(rows)}")
    
    def test_stoney_barrens_row_2(self):
        """Test row: 2 -> gai"""
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        row = rows[0]  # First data row
        cells = row.find_all(['td', 'th'])
        self.assertEqual(cells[0].get_text().strip(), "2")
        self.assertEqual(cells[1].get_text().strip(), "gai")
    
    def test_stoney_barrens_row_3(self):
        """Test row: 3 -> bulette"""
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        row = rows[1]
        cells = row.find_all(['td', 'th'])
        self.assertEqual(cells[0].get_text().strip(), "3")
        self.assertEqual(cells[1].get_text().strip(), "bulette")
    
    def test_stoney_barrens_row_5_with_comma(self):
        """Test row: 5 -> genie, dao"""
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        row = rows[3]  # 5th entry (index 3)
        cells = row.find_all(['td', 'th'])
        self.assertEqual(cells[0].get_text().strip(), "5")
        self.assertEqual(cells[1].get_text().strip(), "genie, dao")
    
    def test_stoney_barrens_duplicate_die_roll_7(self):
        """Test that die roll 7 appears twice with different creatures."""
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        # Find all rows with die roll "7"
        rows_with_7 = []
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells and cells[0].get_text().strip() == "7":
                rows_with_7.append(cells[1].get_text().strip())
        
        self.assertEqual(len(rows_with_7), 2, "Die roll 7 should appear twice")
        self.assertIn("wyvern", rows_with_7)
        self.assertIn("spider huge", rows_with_7)
    
    def test_stoney_barrens_row_11_with_slash(self):
        """Test row: 11 -> ettercap/ behir"""
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        # Find row with die roll 11
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells and cells[0].get_text().strip() == "11":
                creature = cells[1].get_text().strip()
                self.assertEqual(creature, "ettercap/ behir")
                break
        else:
            self.fail("Row with die roll 11 not found")
    
    def test_stoney_barrens_complete_data(self):
        """Test complete Stoney Barrens table against reference."""
        expected_data = [
            ("2", "gai"),
            ("3", "bulette"),
            ("4", "roc"),
            ("5", "genie, dao"),
            ("6", "ankheg"),
            ("7", "wyvern"),
            ("8", "basilisk, lesser"),
            ("7", "spider huge"),
            ("10", "gith"),
            ("11", "ettercap/ behir"),
            ("12", "centipede, giant"),
            ("13", "beetle, boring"),
            ("14", "baazrag"),
            ("15", "tembo"),
            ("16", "braxat"),
            ("16", "bat, huge"),
            ("17", "ettin"),
            ("18", "basilisk, greater"),
            ("19", "ant, swarm"),
        ]
        
        header = self.soup.find('h2', id='header-stoney-barrens')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        # Note: Reference shows 20 rows but only lists 19 (missing one)
        # We'll check the rows we have
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                if i < len(rows):
                    cells = rows[i].find_all(['td', 'th'])
                    actual_roll = cells[0].get_text().strip()
                    actual_creature = cells[1].get_text().strip()
                    
                    self.assertEqual(actual_roll, expected_roll,
                                   f"Row {i}: Expected die roll '{expected_roll}', got '{actual_roll}'")
                    self.assertEqual(actual_creature, expected_creature,
                                   f"Row {i}: Expected creature '{expected_creature}', got '{actual_creature}'")


class TestSandyWastesTableExtraction(unittest.TestCase):
    """Test Sandy Wastes table extraction against reference data."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 11 HTML output."""
        html_path = "data/html_output/chapter-eleven-encounters.html"
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_sandy_wastes_has_20_rows(self):
        """Test that Sandy Wastes table has exactly 19 data rows (covering die rolls 2-20)."""
        header = self.soup.find('h2', id='header-sandy-wastes')
        self.assertIsNotNone(header, "Sandy Wastes header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Sandy Wastes table not found")
        
        rows = table.find_all('tr')[1:]
        self.assertEqual(len(rows), 19, f"Expected 19 rows (die rolls 2-20), got {len(rows)}")
    
    def test_sandy_wastes_complete_data(self):
        """Test complete Sandy Wastes table against reference."""
        expected_data = [
            ("2", "genie, djinn"),
            ("3", "basilisk, dracolisk"),
            ("4", "spotted lion"),
            ("5", "lizard, minotaur"),
            ("6", "wasp"),
            ("7", "snake, giant constrictor"),
            ("8", "snake, constrictor"),
            ("9", "sandling"),
            ("10", "elves/gith"),
            ("11", "kank"),
            ("12", "scorpion, huge"),
            ("13", "slaves"),
            ("14", "inix"),
            ("15", "anakore"),
            ("16", "jozhal"),
            ("17", "spider, phase"),
            ("18", "centipede, megalo-"),
            ("17", "yuan-ti"),
            ("20", "dragonne"),
        ]
        
        header = self.soup.find('h2', id='header-sandy-wastes')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                if i < len(rows):
                    cells = rows[i].find_all(['td', 'th'])
                    actual_roll = cells[0].get_text().strip()
                    actual_creature = cells[1].get_text().strip()
                    
                    self.assertEqual(actual_roll, expected_roll,
                                   f"Row {i}: Expected die roll '{expected_roll}', got '{actual_roll}'")
                    self.assertEqual(actual_creature, expected_creature,
                                   f"Row {i}: Expected creature '{expected_creature}', got '{actual_creature}'")


class TestMountainsTableExtraction(unittest.TestCase):
    """Test Mountains table extraction against reference data."""
    
    @classmethod
    def setUpClass(cls):
        """Load the Chapter 11 HTML output."""
        html_path = "data/html_output/chapter-eleven-encounters.html"
        with open(html_path, 'r', encoding='utf-8') as f:
            cls.html_content = f.read()
        cls.soup = BeautifulSoup(cls.html_content, 'html.parser')
    
    def test_mountains_exists(self):
        """Test that Mountains table exists."""
        header = self.soup.find('h2', id='header-mountains')
        self.assertIsNotNone(header, "Mountains header not found")
        
        table = header.find_next_sibling('table')
        self.assertIsNotNone(table, "Mountains table not found")
    
    def test_mountains_has_20_rows(self):
        """Test that Mountains table has exactly 19 data rows (covering die rolls 2-20)."""
        header = self.soup.find('h2', id='header-mountains')
        table = header.find_next_sibling('table')
        
        rows = table.find_all('tr')[1:]
        self.assertEqual(len(rows), 19, f"Expected 19 rows (die rolls 2-20), got {len(rows)}")
    
    def test_mountains_complete_data(self):
        """Test complete Mountains table against reference."""
        expected_data = [
            ("2", "lizard, fire"),
            ("3", "ettin"),
            ("4", "roc"),
            ("5", "ant, giant"),
            ("6", "giant-kin, cyclops"),
            ("7", "lizard, giant"),
            ("8", "leopard"),
            ("9", "beetle, fire"),
            ("10", "bat, common"),
            ("11", "halflings/dwarves"),
            ("12", "gith"),
            ("13", "slaves"),
            ("14", "kenku"),
            ("15", "spider, giant"),
            ("16", "ettercap"),
            ("17", "zombie"),
            ("18", "aarakocra"),
            ("17", "pseudodragon"),
            ("20", "bulette"),
        ]
        
        header = self.soup.find('h2', id='header-mountains')
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')[1:]
        
        for i, (expected_roll, expected_creature) in enumerate(expected_data):
            with self.subTest(row=i):
                if i < len(rows):
                    cells = rows[i].find_all(['td', 'th'])
                    actual_roll = cells[0].get_text().strip()
                    actual_creature = cells[1].get_text().strip()
                    
                    self.assertEqual(actual_roll, expected_roll,
                                   f"Row {i}: Expected die roll '{expected_roll}', got '{actual_roll}'")
                    self.assertEqual(actual_creature, expected_creature,
                                   f"Row {i}: Expected creature '{expected_creature}', got '{actual_creature}'")


if __name__ == '__main__':
    unittest.main()

