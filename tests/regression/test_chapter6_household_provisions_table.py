#!/usr/bin/env python3
"""Regression test for Chapter 6 Household Provisions table placement.

Requirements:
- The Household Provisions table should appear under the FIRST "Household Provisions" header in the "New Equipment" section
- The table should NOT appear under any later duplicate "Household Provisions" headers
- The table should contain 2 rows with columns: Item, Price
- The table should contain data for "Tun of water" and "Fire Kit"
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


def test_household_provisions_table_placement() -> bool:
    """Verify the Household Provisions table appears under the correct header."""
    html = _read_html()
    
    # Find the "New Equipment" header
    new_equipment_match = re.search(
        r'<p id="header-\d+-new-equipment">.*?New Equipment.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not new_equipment_match:
        print("❌ FAILED: Could not find 'New Equipment' header")
        return False
    
    # Find the FIRST "Household Provisions" header after "New Equipment"
    first_household_match = re.search(
        r'<p id="(header-\d+-household-provisions)">(.*?)</p>(.*?)(?=<p id="header-\d+)',
        html[new_equipment_match.end():],
        re.DOTALL
    )
    
    if not first_household_match:
        print("❌ FAILED: Could not find 'Household Provisions' header after 'New Equipment'")
        return False
    
    first_header_id = first_household_match.group(1)
    first_header_text = first_household_match.group(2)
    content_after_first = first_household_match.group(3)
    
    # Extract roman numeral from header
    roman_match = re.search(r'([IVX]+)\.', first_header_text)
    first_roman = roman_match.group(1) if roman_match else "Unknown"
    
    print(f"Found first 'Household Provisions' header: id='{first_header_id}', roman='{first_roman}'")
    
    # Check if the table appears after the first header
    table_after_first = re.search(
        r'<table[^>]*>.*?<th>Item</th>.*?<th>Price</th>.*?Tun of water.*?Fire Kit.*?</table>',
        content_after_first,
        re.DOTALL
    )
    
    if not table_after_first:
        print(f"❌ FAILED: Household Provisions table does NOT appear after first header ({first_roman})")
        print(f"Content after first header (first 500 chars): {content_after_first[:500]}")
        
        # Check if there's a SECOND "Household Provisions" header with the table
        remaining_html = html[new_equipment_match.end() + first_household_match.end():]
        second_household_match = re.search(
            r'<p id="(header-\d+-household-provisions)">(.*?)</p>(.*?)(?=<p id="header-\d+)',
            remaining_html,
            re.DOTALL
        )
        if second_household_match:
            second_header_id = second_household_match.group(1)
            second_header_text = second_household_match.group(2)
            content_after_second = second_household_match.group(3)
            roman_match2 = re.search(r'([IVX]+)\.', second_header_text)
            second_roman = roman_match2.group(1) if roman_match2 else "Unknown"
            
            table_after_second = re.search(r'<table[^>]*>.*?</table>', content_after_second, re.DOTALL)
            if table_after_second:
                print(f"❌ ERROR: Table appears under SECOND header ({second_roman}) instead of FIRST ({first_roman})")
                print("  This is the WRONG location - it should be in the 'New Equipment' section")
        
        return False
    
    # Verify there's no SECOND "Household Provisions" header with a duplicate table
    remaining_html = html[new_equipment_match.end() + first_household_match.end():]
    second_household_match = re.search(
        r'<p id="(header-\d+-household-provisions)">(.*?)</p>(.*?)(?=<p id="header-\d+)',
        remaining_html,
        re.DOTALL
    )
    
    if second_household_match:
        second_header_id = second_household_match.group(1)
        content_after_second = second_household_match.group(3)
        table_after_second = re.search(
            r'<table[^>]*>.*?<th>Item</th>.*?<th>Price</th>.*?</table>',
            content_after_second,
            re.DOTALL
        )
        if table_after_second:
            print(f"❌ FAILED: Household Provisions table appears under BOTH first and second headers")
            print(f"  Table should only appear under first header ({first_roman})")
            return False
    
    print(f"✅ SUCCESS: Household Provisions table correctly appears under first header ({first_roman}) in 'New Equipment' section")
    return True


def test_household_provisions_table_structure() -> bool:
    """Verify the table has the correct structure and content."""
    html = _read_html()
    
    # Find the "New Equipment" header
    new_equipment_match = re.search(
        r'<p id="header-\d+-new-equipment">.*?New Equipment.*?</p>',
        html,
        re.DOTALL | re.IGNORECASE
    )
    
    if not new_equipment_match:
        print("❌ FAILED: Could not find 'New Equipment' header")
        return False
    
    # Find the FIRST "Household Provisions" section after "New Equipment"
    first_household_match = re.search(
        r'<p id="header-\d+-household-provisions">.*?</p>(.*?)(?=<p id="header-\d+)',
        html[new_equipment_match.end():],
        re.DOTALL
    )
    
    if not first_household_match:
        print("❌ FAILED: Could not find first Household Provisions section")
        return False
    
    # Find table in this section
    table_match = re.search(
        r'<table[^>]*>(.*?)</table>',
        first_household_match.group(1),
        re.DOTALL
    )
    
    if not table_match:
        print("❌ FAILED: No table found after first Household Provisions header")
        return False
    
    table_html = table_match.group(1)
    
    # Verify columns
    if '<th>Item</th>' not in table_html or '<th>Price</th>' not in table_html:
        print("❌ FAILED: Table headers incorrect (expected Item, Price)")
        return False
    
    # Verify data rows
    if 'Tun of water (250 gal.)' not in table_html:
        print("❌ FAILED: Table missing 'Tun of water' row")
        return False
    
    if 'Fire Kit' not in table_html:
        print("❌ FAILED: Table missing 'Fire Kit' row")
        return False
    
    # Count rows (should be 3: 1 header + 2 data)
    rows = re.findall(r'<tr>', table_html)
    if len(rows) != 3:
        print(f"❌ FAILED: Table has {len(rows)} rows (expected 3: 1 header + 2 data)")
        return False
    
    print("✅ SUCCESS: Household Provisions table has correct structure and content")
    return True


def main() -> int:
    ok1 = test_household_provisions_table_placement()
    ok2 = test_household_provisions_table_structure()
    return 0 if (ok1 and ok2) else 1


if __name__ == "__main__":
    sys.exit(main())
