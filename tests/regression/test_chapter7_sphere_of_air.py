"""Regression test for Chapter 7 Sphere of Air spell list formatting.

This test ensures that all spells in the Sphere of Air section are properly
formatted as list items in the HTML output, not as plain paragraph text.

Issue: After "Air Walk (5th)", the remaining spells were being rendered as
plain text instead of formatted list items.
"""

import re
from pathlib import Path
import sys

def test_sphere_of_air_spell_formatting():
    """Test that all Sphere of Air spells are formatted as list items."""
    
    html_file = Path("data/html_output/chapter-seven-magic.html")
    
    if not html_file.exists():
        print(f"ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find the Sphere of Air section
    sphere_of_air_match = re.search(
        r'<p id="header-2-sphere-of-air">.*?</p>(.*?)<p id="header-3-sphere-of-fire">',
        html,
        re.DOTALL
    )
    
    if not sphere_of_air_match:
        print("ERROR: Could not find Sphere of Air section in HTML")
        return False
    
    sphere_section = sphere_of_air_match.group(1)
    
    # Expected spells that should all be formatted as list items
    # Note: Some spells may have HTML entities (e.g., &#x27; for apostrophe)
    expected_spells = [
        ("Dust Devil (2nd)", r"Dust Devil \(2nd\)"),
        ("Call Lightning (3rd)", r"Call Lightning \(3rd\)"),
        ("Control Temperature, 10 Radius (4th)", r"Control Temperature, 10(?:&#x27;|') Radius \(4th\)"),
        ("Protection From Lightning (4th)", r"Protection From Lightning \(4th\)"),
        ("Air Walk (5th)", r"Air Walk \(5th\)"),
        ("Conjure Elemental (Air) (5th)", r"Conjure Elemental \(Air\) \(5th\)"),
        ("Control Winds (5th)", r"Control Winds \(5th\)"),
        ("Insect Plague (5th)", r"Insect Plague \(5th\)"),
        ("Plane Shift (5th)", r"Plane Shift \(5th\)"),
        ("Aerial Servant (6th)", r"Aerial Servant \(6th\)"),
        ("Weather Summoning (6th)", r"Weather Summoning \(6th\)"),
        ("Astral Spell (7th)", r"Astral Spell \(7th\)"),
        ("Control Weather (7th)", r"Control Weather \(7th\)"),
        ("Wind Walk (7th)", r"Wind Walk \(7th\)")
    ]
    
    errors = []
    
    # Check that each spell is in a <li class="spell-list-item"> element
    for spell_name, spell_pattern in expected_spells:
        # Look for the spell in a list item (using regex pattern to handle HTML entities)
        list_item_pattern = rf'<li class="spell-list-item">{spell_pattern}</li>'
        
        if not re.search(list_item_pattern, sphere_section):
            # Check if it's incorrectly in a paragraph instead
            para_pattern = rf'<p>.*?{spell_pattern}.*?</p>'
            if re.search(para_pattern, sphere_section):
                errors.append(f"  ✗ '{spell_name}' found in paragraph instead of list item")
            else:
                errors.append(f"  ✗ '{spell_name}' not found in expected format")
        else:
            print(f"  ✓ '{spell_name}' correctly formatted as list item")
    
    # Also check that no spell names appear in plain paragraph tags
    # Pattern to find spell names in <p> tags (not in list items)
    para_spells = re.findall(
        r'<p>([^<]*?(?:Conjure Elemental|Control Winds|Insect Plague|Plane Shift|Aerial Servant|Weather Summoning|Astral Spell|Control Weather|Wind Walk)[^<]*?)</p>',
        sphere_section
    )
    
    if para_spells:
        errors.append("\n  Found spells in paragraph tags:")
        for para_spell in para_spells:
            errors.append(f"    - {para_spell[:80]}")
    
    if errors:
        print("\nERROR: Sphere of Air spell list formatting issues:")
        for error in errors:
            print(error)
        return False
    
    print("\n✓ All Sphere of Air spells are correctly formatted as list items")
    return True


if __name__ == "__main__":
    success = test_sphere_of_air_spell_formatting()
    sys.exit(0 if success else 1)

