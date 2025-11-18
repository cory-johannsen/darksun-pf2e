"""Unit tests for Chapter 10 Individual and Small Lair Treasures table extraction."""

import unittest
import logging
import json
from tools.pdf_pipeline.transformers.chapter_10.tables import (
    extract_individual_treasures_table,
    _extract_individual_table_cells_from_blocks,
    _organize_individual_cells_into_table,
)
from tools.pdf_pipeline.transformers.chapter_10.common import normalize_plain_text

logger = logging.getLogger(__name__)


class TestIndividualTreasuresTableExtraction(unittest.TestCase):
    """Test Individual and Small Lair Treasures table extraction."""

    @classmethod
    def setUpClass(cls):
        """Load raw data once for all tests."""
        with open('data/raw_structured/sections/02-075-chapter-ten-treasure.json', 'r') as f:
            cls.raw_data = json.load(f)

    def test_header_found(self):
        """Test that Individual and Small Lair Treasures header is found."""
        header_found = False
        for page in self.raw_data.get("pages", []):
            for block in page.get("blocks", []):
                if block.get("type") != "text":
                    continue
                text = normalize_plain_text(block)
                if "Individual and Small Lair Treasures" == text.strip():
                    header_found = True
                    break
            if header_found:
                break
        
        self.assertTrue(header_found, "Individual and Small Lair Treasures header not found")

    def test_table_extraction(self):
        """Test that table is extracted with correct structure."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Find the header block with the attached table
        table_found = False
        table_data = None
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if "__individual_treasures_table" in block:
                    table_found = True
                    table_data = block["__individual_treasures_table"]
                    break
            if table_found:
                break
        
        self.assertTrue(table_found, "Individual Treasures table marker not found")
        self.assertIsNotNone(table_data, "Table data is None")
        
        # Check table structure
        self.assertIn("rows", table_data, "Table missing 'rows' key")
        self.assertIn("header_rows", table_data, "Table missing 'header_rows' key")
        self.assertEqual(table_data["header_rows"], 1, "Table should have 1 header row")
        
        # Check we have header + 17 data rows (J through Z)
        self.assertEqual(len(table_data["rows"]), 18, "Table should have 18 total rows (1 header + 17 data)")
        
        # Check header row
        header_row = table_data["rows"][0]
        self.assertIn("cells", header_row, "Header row missing 'cells' key")
        self.assertEqual(len(header_row["cells"]), 7, "Header row should have 7 cells")
        
        # Check column headers
        expected_headers = ["Treasure Type", "Bits", "Ceramic", "Silver", "Gold", "Gems", "Magical Item"]
        for i, expected in enumerate(expected_headers):
            self.assertEqual(header_row["cells"][i]["text"], expected, 
                           f"Header cell {i} should be '{expected}'")

    def test_treasure_types(self):
        """Test that all treasure types J-Z are present."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Find the table
        table_data = None
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if "__individual_treasures_table" in block:
                    table_data = block["__individual_treasures_table"]
                    break
            if table_data:
                break
        
        self.assertIsNotNone(table_data, "Table data not found")
        
        # Check treasure types (skip header row)
        expected_types = ["J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        for i, expected_type in enumerate(expected_types):
            row = table_data["rows"][i + 1]  # +1 to skip header
            actual_type = row["cells"][0]["text"]
            self.assertEqual(actual_type, expected_type, 
                           f"Row {i+1} should have treasure type '{expected_type}'")

    def test_cell_formats(self):
        """Test that cell values follow the expected formats."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Find the table
        table_data = None
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if "__individual_treasures_table" in block:
                    table_data = block["__individual_treasures_table"]
                    break
            if table_data:
                break
        
        self.assertIsNotNone(table_data, "Table data not found")
        
        # Valid cell formats (regex patterns)
        import re
        valid_patterns = [
            r'^-$',                                    # "-"
            r'^\d+-\d+$',                             # "#-#"
            r'^\d+-\d+\n\d+%$',                       # "#-#\n#%"
            r'^\d+-\d+ potions?$',                    # "#-# potions" or "#-# potion"
            r'^\d+-\d+ scrolls?$',                    # "#-# scrolls" or "#-# scroll"
            r'^Any \d+$',                             # "Any #"
            r'^Any \d+ potions?$',                    # "Any # potions" (without percentage)
            r'^Any \d+ scrolls?$',                    # "Any # scrolls" (without percentage)
            r'^Any \d+\n\d+%$',                       # "Any #\n#%"
            r'^Any \d+ potions?\n\d+%$',              # "Any # potions\n#%" or "Any # potion\n#%"
            r'^Any \d+\+\d+ potions?\n\d+%$',         # "Any #+# potion\n#%" or "Any #+# potions\n#%"
            r'^Any \d+\+\d+ scrolls?\n\d+%$',         # "Any #+# scroll\n#%" or "Any #+# scrolls\n#%"
            r'^Any \d+ except weapons\n\d+%$',        # "Any # except weapons\n#%"
            r'^Armor Weapon\n\d+%$',                  # "Armor Weapon\n#%"
        ]
        
        # Check each data row (skip header)
        for row_idx in range(1, len(table_data["rows"])):
            row = table_data["rows"][row_idx]
            treasure_type = row["cells"][0]["text"]
            
            # Check each cell (skip treasure type column)
            for cell_idx in range(1, len(row["cells"])):
                cell_text = row["cells"][cell_idx]["text"]
                
                # Check if cell matches any valid pattern
                matched = any(re.match(pattern, cell_text) for pattern in valid_patterns)
                self.assertTrue(matched, 
                              f"Cell [{treasure_type}, column {cell_idx}] has invalid format: '{cell_text}'")

    def test_whitespace_cleaning(self):
        """Test that whitespace is properly cleaned in cell values."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Find the table
        table_data = None
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if "__individual_treasures_table" in block:
                    table_data = block["__individual_treasures_table"]
                    break
            if table_data:
                break
        
        self.assertIsNotNone(table_data, "Table data not found")
        
        # Check that there are no common whitespace errors
        for row in table_data["rows"][1:]:  # Skip header
            for cell in row["cells"][1:]:  # Skip treasure type
                cell_text = cell["text"]
                
                # Check for common whitespace issues
                self.assertNotIn("  ", cell_text, 
                               f"Cell has double spaces: '{cell_text}'")
                # Check for space before % (but allow newline before %)
                self.assertNotRegex(cell_text, r'\d\s%', 
                                  f"Cell has space before %: '{cell_text}'")
                # Check for space within number on same line (not across newline)
                lines = cell_text.split('\n')
                for line in lines:
                    self.assertNotRegex(line, r'\d\s+\d', 
                                      f"Cell has space within number on same line: '{line}' in '{cell_text}'")

    def test_header_marked_as_h2(self):
        """Test that the header is marked as H2."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Find the header block
        header_found = False
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if block.get("type") != "text":
                    continue
                
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if "Individual and Small Lair Treasures" in span.get("text", ""):
                            # Check that size was set to H2 (12.0)
                            self.assertEqual(span.get("size"), 12.0, 
                                           "Header should be marked with size 12.0 (H2)")
                            header_found = True
                            break
                    if header_found:
                        break
                if header_found:
                    break
            if header_found:
                break
        
        self.assertTrue(header_found, "Individual and Small Lair Treasures header not found after marking")

    def test_fragmented_blocks_marked_for_skip(self):
        """Test that fragmented table blocks are marked with __skip_render."""
        # Make a copy to avoid modifying the original
        test_data = json.loads(json.dumps(self.raw_data))
        
        # Extract the table
        extract_individual_treasures_table(test_data)
        
        # Count blocks marked for skipping
        skip_count = 0
        for page in test_data.get("pages", []):
            for block in page.get("blocks", []):
                if block.get("__skip_render"):
                    skip_count += 1
        
        # There should be at least some blocks marked for skipping (the fragmented table content)
        self.assertGreater(skip_count, 0, "At least some blocks should be marked with __skip_render")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()

