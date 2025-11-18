#!/usr/bin/env python3
"""
Regression test for Bard Poison Table in Chapter 3.

This test verifies that the Bard Poison Table is properly extracted,
formatted, and rendered in the HTML output.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup


def test_bard_poison_table():
    """Verify Bard Poison Table exists and has correct format."""
    # Load the HTML output
    html_file = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_file.exists():
        raise FileNotFoundError(f"HTML output not found: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test 1: Verify "Bard Poison Table" header exists
    header_found = False
    for tag in soup.find_all(['h2', 'h3', 'h4', 'p']):
        if 'Bard Poison Table' in tag.get_text():
            header_found = True
            header_element = tag
            break
    
    assert header_found, "❌ 'Bard Poison Table' header not found in HTML"
    print("✅ Found 'Bard Poison Table' header")
    
    # Test 2: Verify a table follows the header
    # Find the next sibling that contains a table
    table = None
    current = header_element.next_sibling
    
    # Look ahead for table within next few siblings
    for _ in range(10):
        if current is None:
            break
        # Only process Tag elements, skip NavigableString
        if hasattr(current, 'name') and current.name:
            if current.name == 'table':
                table = current
                break
            # Also check if current element contains a table
            found_tables = current.find_all('table')
            if found_tables:
                table = found_tables[0]
                break
        current = current.next_sibling
    
    assert table is not None, "❌ No table found after 'Bard Poison Table' header"
    print("✅ Found table after header")
    
    # Test 3: Verify table structure
    rows = table.find_all('tr')
    assert len(rows) >= 18, f"❌ Expected at least 18 rows (1 header + 17 data), got {len(rows)}"
    print(f"✅ Table has {len(rows)} rows (expected 18: 1 header + 17 data)")
    
    # Test 4: Verify header row has 5 columns
    header_row = rows[0]
    header_cells = header_row.find_all(['th', 'td'])
    assert len(header_cells) == 5, f"❌ Expected 5 header columns, got {len(header_cells)}"
    print(f"✅ Header row has 5 columns")
    
    # Test 5: Verify header column names
    expected_headers = ["Die Roll", "Class", "Method", "Onset", "Strength"]
    actual_headers = [cell.get_text(strip=True) for cell in header_cells]
    assert actual_headers == expected_headers, f"❌ Header mismatch. Expected {expected_headers}, got {actual_headers}"
    print(f"✅ Header columns correct: {actual_headers}")
    
    # Test 6: Verify data rows have 5 columns each
    for i, row in enumerate(rows[1:], start=1):
        cells = row.find_all(['th', 'td'])
        assert len(cells) == 5, f"❌ Row {i} has {len(cells)} columns, expected 5"
    print(f"✅ All data rows have 5 columns")
    
    # Test 7: Verify some poison data is present
    # Check for poison class letters A-P
    table_text = table.get_text()
    
    # Should have poison classes A through P - look for them anywhere in the table
    poison_classes_found = []
    for letter in 'ABCDEFGHIJKLMNOP':
        # Look for the letter (it's in a cell, so it should appear)
        if letter in table_text:
            poison_classes_found.append(letter)
    
    # We should find most of the poison classes (at least 10 out of 16)
    assert len(poison_classes_found) >= 10, f"❌ Expected to find at least 10 poison classes (A-P), found {len(poison_classes_found)}: {poison_classes_found}"
    print(f"✅ Found {len(poison_classes_found)} poison classes: {poison_classes_found}")
    
    # Test 8: Verify method types are present
    methods = ['Injected', 'Ingested', 'Contact']
    methods_found = []
    for method in methods:
        if method in table_text or 'Iniected' in table_text:  # Note: source has typo "Iniected"
            methods_found.append(method)
    
    assert len(methods_found) >= 2, f"❌ Expected to find multiple method types, found {len(methods_found)}: {methods_found}"
    print(f"✅ Found poison methods: {methods_found} (or 'Iniected' typo from source)")
    
    # Test 9: Verify "Players Choice" final row
    last_row = rows[-1]
    last_row_text = last_row.get_text()
    assert 'Players Choice' in last_row_text or 'Player' in last_row_text, f"❌ Expected 'Players Choice' in last row, got: {last_row_text}"
    print("✅ Final row contains 'Players Choice'")
    
    print("\n🎉 All Bard Poison Table tests passed!")
    return True


if __name__ == "__main__":
    test_bard_poison_table()

