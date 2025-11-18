#!/usr/bin/env python3
"""
Regression test for Chapter 6 weapon description headers.

Verifies that weapon description headers (Chatkcha:, Gythka:, Impaler:, Quabone:, Wrist Razor:)
in the Equipment Descriptions > Weapons section are rendered as H3 headers.
"""

import re
import sys
from pathlib import Path


def test_weapon_description_headers():
    """Test that weapon description headers are H3 in Equipment Descriptions section."""
    
    html_file = Path("data/html_output/chapter-six-money-and-equipment.html")
    
    if not html_file.exists():
        print(f"ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Define weapon description headers that should be H3 (class="header-h3" or font-size: 0.8em)
    weapon_headers = ["Chatkcha:", "Gythka:", "Impaler:", "Quabone:", "Wrist Razor:"]
    
    found_headers = []
    missing_headers = []
    incorrect_level = []
    
    for weapon in weapon_headers:
        # Look for the weapon header in the HTML
        # H3 headers should have class="header-h3" or font-size: 0.8em
        # Pattern: <span ... style="color: #ca5804; font-size: 0.8em">Weapon:</span>
        # or: <span class="header-h3" ...>Weapon:</span>
        
        # Check for H3 styling (font-size: 0.8em or class="header-h3")
        h3_pattern = rf'<span[^>]*(?:class="header-h3"|font-size:\s*0\.8em)[^>]*>{re.escape(weapon)}</span>'
        
        if re.search(h3_pattern, html):
            found_headers.append(weapon)
        else:
            # Check if the header exists at all
            header_pattern = rf'<span[^>]*style="color:\s*#ca5804[^>]*>{re.escape(weapon)}</span>'
            if re.search(header_pattern, html):
                incorrect_level.append(weapon)
                print(f"WARNING: {weapon} found but not styled as H3")
            else:
                missing_headers.append(weapon)
                print(f"ERROR: {weapon} not found in HTML")
    
    # Report results
    print(f"\nWeapon Description Headers Test Results:")
    print(f"  Found as H3: {len(found_headers)}/{len(weapon_headers)}")
    
    if found_headers:
        print(f"  ✓ Correct H3: {', '.join(found_headers)}")
    
    if incorrect_level:
        print(f"  ✗ Wrong level: {', '.join(incorrect_level)}")
    
    if missing_headers:
        print(f"  ✗ Missing: {', '.join(missing_headers)}")
    
    # Test passes if all headers are found and styled as H3
    return len(found_headers) == len(weapon_headers) and not incorrect_level and not missing_headers


if __name__ == "__main__":
    success = test_weapon_description_headers()
    sys.exit(0 if success else 1)

