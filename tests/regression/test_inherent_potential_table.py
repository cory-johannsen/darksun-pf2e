#!/usr/bin/env python3
"""
Regression test for Inherent Potential Table extraction in Chapter 3.

This test verifies that the table has the correct structure and data after
the fix for the regression where the table was showing multi-class combinations
instead of ability score data.
"""

import re
import sys
from pathlib import Path

def test_inherent_potential_table():
    """Test that the Inherent Potential Table is correctly extracted and formatted."""
    
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    
    if not html_file.exists():
        print("❌ FAILED: HTML file not found")
        return False
    
    with open(html_file, 'r') as f:
        html = f.read()
    
    print("Testing Inherent Potential Table...")
    
    # 1. Check that the header exists
    header_match = re.search(
        r'<p id="header-\d+-inherent-potential-table">.*?</p>',
        html,
        re.DOTALL
    )
    
    if not header_match:
        print("❌ FAILED: 'Inherent Potential Table' header not found")
        return False
    
    print("  ✓ Header found")
    
    # 2. Check that a table immediately follows the header
    table_match = re.search(
        r'<p id="header-\d+-inherent-potential-table">.*?</p>\s*(<table[^>]*>.*?</table>)',
        html,
        re.DOTALL
    )
    
    if not table_match:
        print("❌ FAILED: No table found immediately after header")
        return False
    
    print("  ✓ Table found after header")
    
    table_html = table_match.group(1)
    
    # 3. Check row count (should be 9: 1 header + 8 data rows)
    rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
    if len(rows) != 9:
        print(f"❌ FAILED: Table has {len(rows)} rows, expected 9 (1 header + 8 data)")
        return False
    
    print(f"  ✓ Table has correct number of rows: {len(rows)}")
    
    # 4. Check column count (should be 3)
    first_row = rows[0]
    cells = re.findall(r'<t[hd][^>]*>.*?</t[hd]>', first_row, re.DOTALL)
    if len(cells) != 3:
        print(f"❌ FAILED: Table has {len(cells)} columns, expected 3")
        return False
    
    print(f"  ✓ Table has correct number of columns: {len(cells)}")
    
    # 5. Check header row content
    header_texts = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
    expected_headers = ["Ability Score", "Base Score", "Ability Modifier"]
    
    if header_texts != expected_headers:
        print(f"❌ FAILED: Headers are {header_texts}, expected {expected_headers}")
        return False
    
    print(f"  ✓ Headers are correct: {header_texts}")
    
    # 6. Check data rows
    expected_data = [
        ("15", "20", "0"),
        ("16", "22", "+1"),
        ("17", "24", "+2"),
        ("18", "26", "+3"),
        ("19", "28", "+4"),
        ("20", "30", "+5"),
        ("21", "32", "+6"),
        ("22", "34", "+7")
    ]
    
    for i, (expected_ability, expected_base, expected_modifier) in enumerate(expected_data, start=1):
        row = rows[i]
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        
        if len(cells) != 3:
            print(f"❌ FAILED: Data row {i} has {len(cells)} cells, expected 3")
            return False
        
        ability = re.sub(r'<[^>]+>', '', cells[0]).strip()
        base = re.sub(r'<[^>]+>', '', cells[1]).strip()
        modifier = re.sub(r'<[^>]+>', '', cells[2]).strip()
        
        if ability != expected_ability or base != expected_base or modifier != expected_modifier:
            print(f"❌ FAILED: Row {i} has ({ability}, {base}, {modifier}), expected ({expected_ability}, {expected_base}, {expected_modifier})")
            return False
    
    print("  ✓ All data rows are correct")
    
    # 7. Check for whitespace issues (e.g., "+ 1" instead of "+1")
    if "+ 1" in table_html or "+ 2" in table_html or "+ 3" in table_html:
        print("❌ FAILED: Table contains extra whitespace in modifiers (e.g., '+ 1' instead of '+1')")
        return False
    
    print("  ✓ No whitespace issues in modifiers")
    
    # 8. Check that multiclass combinations are NOT in this table
    multiclass_keywords = ["Fighter/", "Cleric/", "Thief/", "Psionicist/"]
    if any(keyword in table_html for keyword in multiclass_keywords):
        print("❌ FAILED: Table contains multi-class combinations (regression detected!)")
        return False
    
    print("  ✓ No multi-class combinations in table (regression prevented)")
    
    return True


def main():
    """Run all tests."""
    print("="*80)
    print("Inherent Potential Table Regression Test")
    print("="*80)
    
    success = test_inherent_potential_table()
    
    print("="*80)
    if success:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()

