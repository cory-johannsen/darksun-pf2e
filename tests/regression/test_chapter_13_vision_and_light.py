"""
Regression test for Chapter 13: Vision and Light

This test ensures that:
1. The intro paragraph is properly merged
2. "Dark Sun Visibility Ranges" is rendered as H2
3. The visibility table is properly formatted
4. Table headers are not rendered as document headers
"""

import sys
from pathlib import Path
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_chapter_13_vision_and_light():
    """Test Chapter 13 rendering."""
    html_file = project_root / "data" / "html_output" / "chapter-thirteen-vision-and-light.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found: {html_file}")
        return False
    
    html = html_file.read_text(encoding="utf-8")
    
    # Test 1: Check that intro paragraph is properly merged
    intro_pattern = r'<p>All of the conditions presented.*?exist on Athas\. However, there are a number.*?should be added\.</p>'
    if not re.search(intro_pattern, html, re.DOTALL):
        print("❌ FAIL: Intro paragraph not properly merged")
        print("   Expected: Single paragraph containing both 'All of the conditions' and 'However, there are'")
        return False
    print("✅ PASS: Intro paragraph properly merged")
    
    # Test 2: Check that "Dark Sun Visibility Ranges" is H2
    h2_pattern = r'<h2[^>]*>.*?Dark Sun Visibility Ranges.*?</h2>'
    if not re.search(h2_pattern, html, re.DOTALL):
        print("❌ FAIL: 'Dark Sun Visibility Ranges' is not H2")
        return False
    print("✅ PASS: 'Dark Sun Visibility Ranges' is H2")
    
    # Test 3: Check that visibility table exists
    table_pattern = r'<table[^>]*class="visibility-ranges"[^>]*>.*?</table>'
    if not re.search(table_pattern, html, re.DOTALL):
        print("❌ FAIL: Visibility ranges table not found")
        return False
    print("✅ PASS: Visibility ranges table found")
    
    # Test 4: Check table headers
    required_headers = ["Condition", "Movement", "Spotted", "Type", "ID", "Detail"]
    for header in required_headers:
        header_pattern = rf'<th[^>]*>{header}</th>'
        if not re.search(header_pattern, html):
            print(f"❌ FAIL: Table header '{header}' not found")
            return False
    print("✅ PASS: All table headers present")
    
    # Test 5: Check table rows
    required_conditions = [
        "Sand, blowing",
        "Sandstorm, mild",
        "Sandstorm, driving",
        "Night, both moons",
        "Silt Sea, calm",
        "Silt Sea, rolling"
    ]
    for condition in required_conditions:
        condition_pattern = rf'<td>{re.escape(condition)}</td>'
        if not re.search(condition_pattern, html):
            print(f"❌ FAIL: Table row for '{condition}' not found")
            return False
    print("✅ PASS: All table rows present")
    
    # Test 6: Check that table headers are NOT rendered as document headers
    # (Condition, Movement, Type, Spotted, Detail should not be H1/H2/H3/H4)
    for header in ["Condition", "Movement", "Type", "Spotted", "Detail"]:
        # Check for these as document headers (with roman numerals)
        bad_pattern = rf'<[ph]\d[^>]*>(?:I+\.\s+)?.*?{re.escape(header)}.*?</[ph]\d>'
        if re.search(bad_pattern, html, re.IGNORECASE):
            print(f"❌ FAIL: '{header}' incorrectly rendered as document header")
            return False
    print("✅ PASS: Table headers not rendered as document headers")
    
    # Test 7: Check that table has correct number of rows (6 data rows + 1 header row)
    table_match = re.search(table_pattern, html, re.DOTALL)
    if table_match:
        table_html = table_match.group(0)
        tbody_match = re.search(r'<tbody>(.*?)</tbody>', table_html, re.DOTALL)
        if tbody_match:
            tbody_html = tbody_match.group(1)
            data_rows = re.findall(r'<tr>', tbody_html)
            if len(data_rows) != 6:
                print(f"❌ FAIL: Expected 6 data rows, found {len(data_rows)}")
                return False
            print("✅ PASS: Table has correct number of rows")
    
    # Test 8: Check that condition values are not rendered outside the table
    for condition in required_conditions:
        # Check if condition appears in a paragraph (outside table)
        bad_pattern = rf'<p[^>]*>{re.escape(condition)}(?:\s+\d+)*</p>'
        if re.search(bad_pattern, html):
            print(f"❌ FAIL: '{condition}' incorrectly rendered outside table")
            return False
    print("✅ PASS: Condition values only appear in table")
    
    print("\n🎉 All Chapter 13 tests passed!")
    return True


if __name__ == "__main__":
    success = test_chapter_13_vision_and_light()
    sys.exit(0 if success else 1)

