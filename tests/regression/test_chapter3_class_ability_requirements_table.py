#!/usr/bin/env python3
"""
Regression Test: Chapter 3 Class Ability Requirements Table

This test verifies that the "Class Ability Requirements" table in Chapter 3
is properly formatted as an HTML table and not rendered as separate headers.

The table should have:
- 7 columns: Class, Str, Dex, Con, Int, Wis, Cha
- 5 rows: 1 header row + 4 data rows (Gladiator, Defiler, Templar, Psionicist)
- Proper HTML <table> structure with <th> and <td> tags

REGRESSION FIX: 2025-11-15
Previously, the table was not being rendered at all, and the fragmented table
elements were being rendered as individual headers (H1 and H2), causing them
to appear in the table of contents. This was due to the missing call to
extract_class_ability_requirements_table in the adjustments.py file.
"""

import re
import sys
from pathlib import Path


def test_class_ability_requirements_table_exists():
    """
    Verify that the Class Ability Requirements table exists in the HTML output.
    """
    print("\nTesting Class Ability Requirements table exists...")
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    
    if not html_file.exists():
        print(f"❌ FAILED: HTML file not found: {html_file}")
        return False
    
    html_content = html_file.read_text()
    
    # The table should exist after the "Class Ability Requirements" subheader
    if not ('<span class="header-h2"' in html_content or '<span class="subheader"' in html_content):
        print("❌ FAILED: No subheader styling found in HTML")
        return False
    print("  ✓ Subheader styling found")
    
    # Should contain a table with the class names
    if "<table" not in html_content:
        print("❌ FAILED: No table tags found in HTML")
        return False
    print("  ✓ Table tags found")
    
    if "Gladiator" not in html_content:
        print("❌ FAILED: Gladiator not found in HTML")
        return False
    print("  ✓ Gladiator found")
    
    if "Defiler" not in html_content:
        print("❌ FAILED: Defiler not found in HTML")
        return False
    print("  ✓ Defiler found")
    
    if "Templar" not in html_content:
        print("❌ FAILED: Templar not found in HTML")
        return False
    print("  ✓ Templar found")
    
    if "Psionicist" not in html_content:
        print("❌ FAILED: Psionicist not found in HTML")
        return False
    print("  ✓ Psionicist found")
    
    return True


def test_class_ability_requirements_table_structure():
    """
    Verify the table has correct structure with header row and data rows.
    """
    print("\nTesting Class Ability Requirements table structure...")
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    html_content = html_file.read_text()
    
    # Find all tables in the document
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL)
    
    # Find the Class Ability Requirements table
    # It should contain "Class", "Str", "Dex", "Con", "Int", "Wis", "Cha" headers
    class_table = None
    for table in tables:
        if "Gladiator" in table and "Defiler" in table and "Templar" in table and "Psionicist" in table:
            class_table = table
            break
    
    if class_table is None:
        print("❌ FAILED: Class Ability Requirements table not found")
        return False
    print("  ✓ Class Ability Requirements table found")
    
    # Count rows (should have 5: 1 header + 4 data rows)
    rows = re.findall(r'<tr>', class_table)
    if len(rows) != 5:
        print(f"❌ FAILED: Expected 5 rows, found {len(rows)}")
        return False
    print(f"  ✓ Table has 5 rows")
    
    # Check for header cells (<th>)
    header_cells = re.findall(r'<th[^>]*>(.*?)</th>', class_table, re.DOTALL)
    if len(header_cells) != 7:
        print(f"❌ FAILED: Expected 7 header cells, found {len(header_cells)}")
        return False
    print(f"  ✓ Table has 7 header cells")
    
    # Check header cell contents
    expected_headers = ["Class", "Str", "Dex", "Con", "Int", "Wis", "Cha"]
    for expected in expected_headers:
        if not any(expected in h for h in header_cells):
            print(f"❌ FAILED: Header '{expected}' not found in table")
            return False
    print(f"  ✓ All expected headers found")
    
    return True


def test_no_stray_table_headers():
    """
    Verify that table elements like "Class", "S t r", "Dex" are NOT rendered as H1/H2 headers.
    
    This was the regression: table fragments were being rendered as individual headers
    instead of as part of a table structure.
    
    This test specifically checks the "Class Ability Score Requirements" section, not other tables.
    """
    print("\nTesting no stray table headers...")
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    html_content = html_file.read_text()
    
    # Extract the section around the Class Ability Score Requirements table
    # This is between the "Class Ability Score Requirements" H1 header and the "Newly Created Characters" header
    section_match = re.search(
        r'<p id="header-6-class-ability-score-requirements">.*?</p>(.*?)<p id="header-8-newly-created-characters">',
        html_content,
        re.DOTALL
    )
    
    if not section_match:
        print("❌ FAILED: Could not find Class Ability Score Requirements section")
        return False
    
    section_content = section_match.group(1)
    
    # These should NOT appear as H1/H2 headers within this specific section
    stray_patterns = [
        (r'<p id="header-\d+-class">.*?<span[^>]*>Class</span></p>', "Class"),
        (r'<p id="header-\d+-s-t-r">.*?<span[^>]*>S t r</span></p>', "S t r"),
        (r'<p id="header-\d+-str">.*?<span[^>]*>Str</span></p>', "Str"),
        (r'<p id="header-\d+-dex">.*?<span[^>]*>Dex</span></p>', "Dex"),
        (r'<p id="header-\d+-con">.*?<span[^>]*>Con</span></p>', "Con"),
        (r'<p id="header-\d+-int">.*?<span[^>]*>Int</span></p>', "Int"),
        (r'<p id="header-\d+-wis">.*?<span[^>]*>Wis</span></p>', "Wis"),
        (r'<p id="header-\d+-cha">.*?<span[^>]*>Cha</span></p>', "Cha"),
    ]
    
    for pattern, name in stray_patterns:
        match = re.search(pattern, section_content, re.IGNORECASE)
        if match:
            print(f"❌ FAILED: Found stray table header rendered as H1/H2 in Class Ability Requirements section: {name}")
            return False
    print("  ✓ No stray table headers found in Class Ability Requirements section")
    
    return True


def test_table_not_in_toc():
    """
    Verify that table column headers don't appear in the table of contents.
    
    The TOC should NOT contain links to standalone "Class", "Str", "Dex", "Con", etc. headers
    in the Class Ability Score Requirements section.
    """
    print("\nTesting table headers not in TOC...")
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    html_content = html_file.read_text()
    
    # Extract the table of contents section
    toc_match = re.search(r'<nav id="table-of-contents">(.*?)</nav>', html_content, re.DOTALL)
    if not toc_match:
        print("❌ FAILED: Table of contents not found")
        return False
    
    toc_content = toc_match.group(1)
    
    # Check that there are no TOC entries for stray table headers BETWEEN
    # "Class Ability Score Requirements" and "Newly Created Characters"
    # The legitimate "Class" from Bard Poison Table (header-51) is fine since that's a different issue
    
    # Find TOC entries in the relevant range (headers 7-8)
    # header-7 should be "Class Ability Requirements" (subheader) - OK
    # header-8 should be "Newly Created Characters" - OK
    # There should be NO headers between them for table columns
    
    # Check for stray headers by looking for the specific header IDs that would indicate table columns
    # These would be numbered between header-7 (Class Ability Requirements) and header-8 (Newly Created Characters)
    # Since there's only supposed to be one subheader (7) and then header-8, there should be no other entries
    
    # Look for any header-7-X pattern that's not "class-ability-requirements"
    stray_pattern = r'<a href="#header-7-(?!class-ability-requirements)[^"]+">(?:Class|Str|Dex|Con|Int|Wis|Cha)</a>'
    match = re.search(stray_pattern, toc_content, re.IGNORECASE)
    if match:
        print(f"❌ FAILED: Found stray table column header in TOC: {match.group(0)}")
        return False
    
    print("  ✓ No stray table headers in TOC for Class Ability Requirements section")
    
    return True


def test_table_has_proper_data():
    """
    Verify the table contains the correct ability score requirements for each class.
    """
    print("\nTesting table has proper data...")
    html_file = Path("data/html_output/chapter-three-player-character-classes.html")
    html_content = html_file.read_text()
    
    # Find the Class Ability Requirements table
    tables = re.findall(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL)
    class_table = None
    for table in tables:
        if "Gladiator" in table and "Defiler" in table:
            class_table = table
            break
    
    if class_table is None:
        print("❌ FAILED: Class Ability Requirements table not found")
        return False
    print("  ✓ Class Ability Requirements table found")
    
    # Verify specific data values
    # Gladiator: Str 13, Dex 12, Con 15
    gladiator_row = re.search(r'<tr>.*?Gladiator.*?</tr>', class_table, re.DOTALL)
    if not gladiator_row:
        print("❌ FAILED: Gladiator row not found")
        return False
    if "13" not in gladiator_row.group(0):
        print("❌ FAILED: Gladiator Str requirement (13) not found")
        return False
    if "12" not in gladiator_row.group(0):
        print("❌ FAILED: Gladiator Dex requirement (12) not found")
        return False
    if "15" not in gladiator_row.group(0):
        print("❌ FAILED: Gladiator Con requirement (15) not found")
        return False
    print("  ✓ Gladiator requirements correct")
    
    # Defiler: Int 3
    defiler_row = re.search(r'<tr>.*?Defiler.*?</tr>', class_table, re.DOTALL)
    if not defiler_row:
        print("❌ FAILED: Defiler row not found")
        return False
    if "3" not in defiler_row.group(0):
        print("❌ FAILED: Defiler Int requirement (3) not found")
        return False
    print("  ✓ Defiler requirements correct")
    
    # Templar: Int 10, Wis 7
    templar_row = re.search(r'<tr>.*?Templar.*?</tr>', class_table, re.DOTALL)
    if not templar_row:
        print("❌ FAILED: Templar row not found")
        return False
    if "10" not in templar_row.group(0):
        print("❌ FAILED: Templar Int requirement (10) not found")
        return False
    if "7" not in templar_row.group(0):
        print("❌ FAILED: Templar Wis requirement (7) not found")
        return False
    print("  ✓ Templar requirements correct")
    
    # Psionicist: Con 11, Int 12, Wis 15
    psionicist_row = re.search(r'<tr>.*?Psionicist.*?</tr>', class_table, re.DOTALL)
    if not psionicist_row:
        print("❌ FAILED: Psionicist row not found")
        return False
    if "11" not in psionicist_row.group(0):
        print("❌ FAILED: Psionicist Con requirement (11) not found")
        return False
    if "12" not in psionicist_row.group(0):
        print("❌ FAILED: Psionicist Int requirement (12) not found")
        return False
    if "15" not in psionicist_row.group(0):
        print("❌ FAILED: Psionicist Wis requirement (15) not found")
        return False
    print("  ✓ Psionicist requirements correct")
    
    return True


def main():
    """Run all tests."""
    print("="*80)
    print("Chapter 3 Class Ability Requirements Table Regression Test")
    print("="*80)
    
    tests = [
        test_class_ability_requirements_table_exists,
        test_class_ability_requirements_table_structure,
        test_no_stray_table_headers,
        test_table_not_in_toc,
        test_table_has_proper_data,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ EXCEPTION: {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*80)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("="*80)
        return 0
    else:
        print(f"❌ {results.count(False)} TEST(S) FAILED")
        print("="*80)
        return 1


if __name__ == "__main__":
    sys.exit(main())

