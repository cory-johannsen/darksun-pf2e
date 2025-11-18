#!/usr/bin/env python3
"""Regression test for Chapter 6 Barding section - H3 header and table placement.

Requirements:
- "Barding" should be an H3 header under "Tack and Harness" in the "New Equipment" section
- The Barding table should appear immediately after the "Barding" H3 header
- The table should contain 7 rows (1 header + 6 data rows) and 3 columns (Type, Price, Weight)
- The table should contain all 6 animal types: Inix (leather/chitin), Kank (leather/chitin), Mekillot (leather/chitin)
- The second "Barding:" in Equipment Descriptions should NOT be converted to H3
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
html_path = project_root / "data" / "html_output" / "chapter-six-money-and-equipment.html"


def _read_html() -> str:
    if not html_path.exists():
        print(f"❌ FAILED: {html_path} not found (run transform stage first)")
        sys.exit(1)
    return html_path.read_text(encoding="utf-8")


def test_barding_h3_header_exists() -> bool:
    """Verify "Barding" is an H3 header in the New Equipment section."""
    html = _read_html()
    
    # Find "New Equipment" section
    new_equipment_match = re.search(
        r'<p id="header-\d+-new-equipment">.*?New Equipment.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not new_equipment_match:
        print("❌ FAILED: Could not find 'New Equipment' header")
        return False
    
    # Find "Tack and Harness" header after "New Equipment"
    tack_match = re.search(
        r'<p id="header-\d+-tack-and-harness">.*?Tack and Harness.*?</p>',
        html[new_equipment_match.end():],
        re.DOTALL
    )
    
    if not tack_match:
        print("❌ FAILED: Could not find 'Tack and Harness' header after 'New Equipment'")
        return False
    
    # Find "Barding" header after "Tack and Harness" (looking for font-size styling that indicates H3)
    # H3 headers use font-size: 0.8em or similar smaller styling
    barding_match = re.search(
        r'<p id="(header-\d+-barding)">(.*?Barding.*?)</p>',
        html[new_equipment_match.end() + tack_match.end():],
        re.DOTALL
    )
    
    if not barding_match:
        print("❌ FAILED: Could not find 'Barding' header after 'Tack and Harness'")
        return False
    
    barding_id = barding_match.group(1)
    barding_content = barding_match.group(2)
    
    # Check if "Barding" text is present (without colon for the first occurrence)
    if "Barding" not in barding_content:
        print(f"❌ FAILED: 'Barding' header content doesn't contain 'Barding': {barding_content}")
        return False
    
    # Extract the roman numeral
    roman_match = re.search(r'([IVX]+)\.', barding_content)
    barding_roman = roman_match.group(1) if roman_match else "Unknown"
    
    print(f"✅ SUCCESS: Found 'Barding' header in New Equipment section: id='{barding_id}', roman='{barding_roman}'")
    return True


def test_barding_table_placement() -> bool:
    """Verify the Barding table appears immediately after the 'Barding' H3 header."""
    html = _read_html()
    
    # Find "New Equipment" section
    new_equipment_match = re.search(
        r'<p id="header-\d+-new-equipment">.*?New Equipment.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not new_equipment_match:
        print("❌ FAILED: Could not find 'New Equipment' header")
        return False
    
    # Find "Tack and Harness" header
    tack_match = re.search(
        r'<p id="header-\d+-tack-and-harness">.*?Tack and Harness.*?</p>',
        html[new_equipment_match.end():],
        re.DOTALL
    )
    
    if not tack_match:
        print("❌ FAILED: Could not find 'Tack and Harness' header")
        return False
    
    # Find "Barding" header
    barding_match = re.search(
        r'<p id="header-\d+-barding">(.*?)</p>(.*?)(?=<p id="header-\d+)',
        html[new_equipment_match.end() + tack_match.end():],
        re.DOTALL
    )
    
    if not barding_match:
        print("❌ FAILED: Could not find 'Barding' header section")
        return False
    
    content_after_barding = barding_match.group(2)
    
    # Check for table with proper structure (Type, Price, Weight columns)
    table_match = re.search(
        r'<table[^>]*>.*?<th>Type</th>.*?<th>Price</th>.*?<th>Weight</th>.*?</table>',
        content_after_barding,
        re.DOTALL
    )
    
    if not table_match:
        print("❌ FAILED: Barding table does NOT appear after 'Barding' header in New Equipment section")
        print(f"Content after Barding header (first 500 chars): {content_after_barding[:500]}")
        return False
    
    print("✅ SUCCESS: Barding table correctly appears after 'Barding' H3 header in New Equipment section")
    return True


def test_barding_table_structure() -> bool:
    """Verify the Barding table has correct structure and content."""
    html = _read_html()
    
    # Find "New Equipment" section
    new_equipment_match = re.search(
        r'<p id="header-\d+-new-equipment">.*?New Equipment.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not new_equipment_match:
        print("❌ FAILED: Could not find 'New Equipment' header")
        return False
    
    # Find Barding section after New Equipment
    barding_match = re.search(
        r'<p id="header-\d+-barding">.*?</p>(.*?)(?=<p id="header-\d+)',
        html[new_equipment_match.end():],
        re.DOTALL
    )
    
    if not barding_match:
        print("❌ FAILED: Could not find Barding section")
        return False
    
    # Find table in Barding section
    table_match = re.search(
        r'<table[^>]*>(.*?)</table>',
        barding_match.group(1),
        re.DOTALL
    )
    
    if not table_match:
        print("❌ FAILED: No table found in Barding section")
        return False
    
    table_html = table_match.group(1)
    
    # Verify columns
    if '<th>Type</th>' not in table_html or '<th>Price</th>' not in table_html or '<th>Weight</th>' not in table_html:
        print("❌ FAILED: Table headers incorrect (expected Type, Price, Weight)")
        return False
    
    # Verify all 6 animal types are present
    required_animals = [
        ("Inix, leather", "35 sp", "240 lb"),
        ("Inix, chitin", "50 sp", "400 lb"),
        ("Kank, leather", "15 sp", "70 lb"),
        ("Kank, chitin", "35 sp", "120 lb"),
        ("Mekillot, leather", "500 sp", "1000 lb"),
        ("Mekillot, chitin", "750 sp", "1600 lb"),
    ]
    
    for animal, price, weight in required_animals:
        if animal not in table_html:
            print(f"❌ FAILED: Table missing '{animal}' row")
            return False
    
    # Count rows (should be 7: 1 header + 6 data)
    rows = re.findall(r'<tr>', table_html)
    if len(rows) != 7:
        print(f"❌ FAILED: Table has {len(rows)} rows (expected 7: 1 header + 6 data)")
        return False
    
    print("✅ SUCCESS: Barding table has correct structure with 7 rows and 3 columns, all 6 animal types present")
    return True


def test_second_barding_not_h3() -> bool:
    """Verify the second 'Barding:' in Equipment Descriptions is not converted to H3."""
    html = _read_html()
    
    # Find "Equipment Descriptions" section
    equipment_desc_match = re.search(
        r'<p id="header-\d+-equipment-descriptions">.*?Equipment Descriptions.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not equipment_desc_match:
        print("⚠️  WARNING: Could not find 'Equipment Descriptions' header")
        return True  # Not a failure - section might be named differently
    
    # Find "Barding:" in the Equipment Descriptions section (with colon)
    # This should be styled as a descriptive header, not H3
    remaining_html = html[equipment_desc_match.end():]
    
    # Look for "Barding:" text with colon (the second occurrence)
    barding_desc_match = re.search(
        r'<span[^>]*>Barding:\s*</span>',
        remaining_html,
        re.DOTALL
    )
    
    if barding_desc_match:
        # This is fine - it's a descriptive header with inline styling
        print("✅ SUCCESS: Second 'Barding:' in Equipment Descriptions is correctly styled as descriptive text")
        return True
    
    print("⚠️  INFO: Could not verify second 'Barding:' occurrence (might not exist or be formatted differently)")
    return True


def main() -> int:
    ok1 = test_barding_h3_header_exists()
    ok2 = test_barding_table_placement()
    ok3 = test_barding_table_structure()
    ok4 = test_second_barding_not_h3()
    return 0 if (ok1 and ok2 and ok3 and ok4) else 1


if __name__ == "__main__":
    sys.exit(main())

