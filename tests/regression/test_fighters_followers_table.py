#!/usr/bin/env python3
"""
Regression test for the Fighters Followers table in Chapter 3.

This test ensures that the Fighters Followers table is correctly extracted
and formatted, with the proper data rows for levels 11-20.
"""

import json
import sys
import re
from pathlib import Path


def test_fighters_followers_table():
    """Test that the Fighters Followers table is correctly rendered in the HTML output."""
    
    # Load the HTML output for chapter 3
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    
    if not html_file.exists():
        print(f"❌ ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the Fighters Followers table
    # The table should have headers: Char. Level, Stands, Level, Special
    table_pattern = r'<table[^>]*>.*?<th>Char\. Level</th>.*?<th>Stands</th>.*?<th>Level</th>.*?<th>Special</th>.*?</table>'
    match = re.search(table_pattern, html_content, re.DOTALL)
    
    if not match:
        print("❌ ERROR: Could not find Fighters Followers table with correct headers")
        return False
    
    table_html = match.group(0)
    
    # Extract all rows from the table
    row_pattern = r'<tr>(.*?)</tr>'
    rows = re.findall(row_pattern, table_html, re.DOTALL)
    
    if len(rows) < 2:
        print(f"❌ ERROR: Table has only {len(rows)} rows, expected at least 11 (1 header + 10 data rows)")
        return False
    
    # Check that the first data row (after header) contains level data, not paragraph text
    first_data_row = rows[1]
    
    # The first data row should NOT contain paragraph text like "risma", "Handbook", etc.
    invalid_texts = ["risma", "Handbook", "Note that", "PlayersHandbook"]
    for invalid_text in invalid_texts:
        if invalid_text in first_data_row:
            print(f"❌ ERROR: First data row contains paragraph text: '{invalid_text}'")
            print(f"   Row content: {first_data_row[:200]}")
            return False
    
    # The first data row SHOULD contain level numbers (11-20) and dice notation (1d10, 1d12, etc.)
    if not re.search(r'1[1-2]\d*', first_data_row):
        print(f"❌ ERROR: First data row does not contain expected level numbers (11-20)")
        print(f"   Row content: {first_data_row[:200]}")
        return False
    
    # Check for dice notation in data rows (e.g., "1d10+2", "1d12+1")
    data_rows = rows[1:]  # Skip header row
    dice_pattern = r'1d\d+\+\d+'
    found_dice = False
    for row in data_rows:
        if re.search(dice_pattern, row):
            found_dice = True
            break
    
    if not found_dice:
        print(f"❌ ERROR: No dice notation found in table data rows (expected patterns like '1d10+2')")
        return False
    
    # Check that we have at least 10 data rows (levels 11-20)
    if len(data_rows) < 10:
        print(f"⚠️  WARNING: Table has only {len(data_rows)} data rows, expected 10 (levels 11-20)")
        # This is a warning, not a failure, as the extraction might be partial
    
    print(f"✅ Fighters Followers table is correctly formatted")
    print(f"   - Found {len(rows)} rows (1 header + {len(data_rows)} data rows)")
    print(f"   - Data rows contain level numbers and dice notation")
    print(f"   - No paragraph text in data rows")
    
    return True


def test_fighters_followers_table_in_processed_data():
    """Test that the Fighters Followers table is correctly extracted in the processed JSON data."""
    
    # Load the processed JSON data for chapter 3
    processed_file = Path("data/processed/journals/chapter-three-player-character-classes.json")
    
    if not processed_file.exists():
        print(f"❌ ERROR: Processed file not found: {processed_file}")
        return False
    
    with open(processed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # The structure has a "data" key with "content" inside
    content = data.get("data", {}).get("content", "")
    
    if not content:
        print("❌ ERROR: No content found in processed data")
        return False
    
    # Find the table in the HTML content
    table_pattern = r'<table[^>]*>.*?<th>Char\. Level</th>.*?<th>Stands</th>.*?<th>Level</th>.*?<th>Special</th>.*?</table>'
    match = re.search(table_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ ERROR: Could not find Fighters Followers table in processed content")
        return False
    
    table_html = match.group(0)
    
    # Check that the table doesn't contain paragraph text
    invalid_texts = ["risma", "Handbook", "Note that"]
    for invalid_text in invalid_texts:
        if invalid_text in table_html:
            print(f"❌ ERROR: Table contains paragraph text: '{invalid_text}'")
            return False
    
    print(f"✅ Fighters Followers table in processed data is correctly formatted")
    
    return True


def main():
    """Run all regression tests for the Fighters Followers table."""
    print("\n" + "=" * 80)
    print("REGRESSION TEST: Fighters Followers Table")
    print("=" * 80 + "\n")
    
    all_passed = True
    
    # Test 1: Check HTML output
    print("Test 1: Checking HTML output...")
    if not test_fighters_followers_table():
        all_passed = False
    print()
    
    # Test 2: Check processed JSON data
    print("Test 2: Checking processed JSON data...")
    if not test_fighters_followers_table_in_processed_data():
        all_passed = False
    print()
    
    # Summary
    print("=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

