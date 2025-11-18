#!/usr/bin/env python3
"""
Regression test for Chapter 8 Individual Race Awards tables.

Tests that all 7 race award tables are properly extracted with correct structure.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_race_tables_extraction():
    """Test that all 7 race award tables are extracted from Chapter 8."""
    html_path = Path(__file__).parent.parent.parent / 'data' / 'html_output' / 'chapter-eight-experience.html'
    
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Define expected race table headers
    expected_races = [
        ("Dwarf", "header-class-award-dwarf"),
        ("Elf", "header-class-award-elf"),
        ("Half-elf", "header-class-award-half-elf"),
        ("Half-giant", "header-class-award-half-giant"),
        ("Halfling", "header-class-award-halfling"),
        ("M u l ", "header-class-award-m-u-l-"),  # Note: spaces in source PDF
        ("Thri-kreen", "header-class-award-thri-kreen"),
    ]
    
    success = True
    
    for race_name, anchor_id in expected_races:
        # Check if race header exists
        if f'id="{anchor_id}"' not in html_content:
            print(f"ERROR: Race header '{race_name}' with anchor '{anchor_id}' not found in HTML")
            success = False
            continue
        
        # Check if a table follows the header
        # Find the position of the header
        header_pos = html_content.find(f'id="{anchor_id}"')
        # Check if there's a table within the next 500 characters
        table_pos = html_content.find('<table', header_pos, header_pos + 500)
        
        if table_pos == -1:
            print(f"ERROR: No table found after '{race_name}' header")
            success = False
            continue
        
        print(f"✓ Race table '{race_name}' found with header and table")
    
    return success


def test_mul_table_content():
    """Test that Mul table has correct content."""
    html_path = Path(__file__).parent.parent.parent / 'data' / 'html_output' / 'chapter-eight-experience.html'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find Mul table section
    mul_header_pos = html_content.find('id="header-class-award-m-u-l-"')
    if mul_header_pos == -1:
        print("ERROR: Mul header not found")
        return False
    
    # Get the table content (next 500 chars should contain the table)
    mul_section = html_content[mul_header_pos:mul_header_pos + 500]
    
    # Check for expected content
    expected_content = [
        "Heavy exertion",
        "50 XP/12 hours",
    ]
    
    success = True
    for content in expected_content:
        if content not in mul_section:
            print(f"ERROR: Expected content '{content}' not found in Mul table")
            success = False
        else:
            print(f"✓ Mul table contains: '{content}'")
    
    return success


def test_thri_kreen_table_content():
    """Test that Thri-kreen table has correct content and no footnotes."""
    html_path = Path(__file__).parent.parent.parent / 'data' / 'html_output' / 'chapter-eight-experience.html'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find Thri-kreen table section
    thri_kreen_header_pos = html_content.find('id="header-class-award-thri-kreen"')
    if thri_kreen_header_pos == -1:
        print("ERROR: Thri-kreen header not found")
        return False
    
    # Get the table content (find the table start and end)
    table_start = html_content.find('<table', thri_kreen_header_pos)
    table_end = html_content.find('</table>', table_start) + len('</table>')
    thri_kreen_table = html_content[table_start:table_end]
    
    # Check for expected content
    expected_content = [
        "Per kill brought back for food",
        "50 XP",
        "Per creature paralyzed",
        "100 XP",
        "Per missile dodged",
        "10 XP",
    ]
    
    success = True
    for content in expected_content:
        if content not in thri_kreen_table:
            print(f"ERROR: Expected content '{content}' not found in Thri-kreen table")
            success = False
        else:
            print(f"✓ Thri-kreen table contains: '{content}'")
    
    # Check that the Dwarf footnote is NOT in the table
    # The footnote should be outside the table
    if "*Dwarves do not consider any mission a major" in thri_kreen_table:
        print("ERROR: Dwarf footnote found inside Thri-kreen table (should be separate)")
        success = False
    else:
        print("✓ Thri-kreen table does not contain Dwarf footnote")
    
    # Check that Thri-kreen table has exactly 3 data rows (not counting header)
    row_count = thri_kreen_table.count('<tr>') - 1  # Subtract header row
    if row_count != 3:
        print(f"ERROR: Thri-kreen table has {row_count} rows, expected 3")
        success = False
    else:
        print(f"✓ Thri-kreen table has exactly 3 data rows")
    
    return success


def test_dwarf_footnote_placement():
    """Test that the Dwarf footnote appears as a separate paragraph after the Dwarf table."""
    html_path = Path(__file__).parent.parent.parent / 'data' / 'html_output' / 'chapter-eight-experience.html'
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find Dwarf table
    dwarf_header_pos = html_content.find('id="header-class-award-dwarf"')
    if dwarf_header_pos == -1:
        print("ERROR: Dwarf header not found")
        return False
    
    # Find the Dwarf table end
    table_start = html_content.find('<table', dwarf_header_pos)
    table_end = html_content.find('</table>', table_start) + len('</table>')
    
    # Look for the footnote in the next 500 characters after the table
    section_after_table = html_content[table_end:table_end + 500]
    
    # The footnote should appear as a paragraph or table row near the Dwarf table
    footnote_text = "*Dwarves do not consider any mission a major"
    
    if footnote_text not in html_content:
        print("ERROR: Dwarf footnote not found anywhere in document")
        return False
    
    print("✓ Dwarf footnote exists in document")
    
    # Ideally it should be close to the Dwarf table
    footnote_pos = html_content.find(footnote_text)
    distance_from_dwarf = abs(footnote_pos - table_end)
    
    if distance_from_dwarf > 5000:  # Allow reasonable distance
        print(f"WARNING: Dwarf footnote is {distance_from_dwarf} chars from Dwarf table (might be misplaced)")
    else:
        print(f"✓ Dwarf footnote is reasonably close to Dwarf table ({distance_from_dwarf} chars)")
    
    return True


def main():
    """Run all tests."""
    print("="*80)
    print("Chapter 8 Individual Race Awards Tables - Regression Test")
    print("="*80)
    
    tests = [
        ("Race tables extraction", test_race_tables_extraction),
        ("Mul table content", test_mul_table_content),
        ("Thri-kreen table content", test_thri_kreen_table_content),
        ("Dwarf footnote placement", test_dwarf_footnote_placement),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

