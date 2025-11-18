"""Test for Chapter 6 New Weapons table structure and ordering."""

import re
from pathlib import Path


def test_weapons_table_after_animals():
    """Verify that the Weapons table appears after Animals in the New Equipment section."""
    html_file = Path("data/html_output/chapter-six-money-and-equipment.html")
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    content = html_file.read_text()
    
    # Find the Animals header in New Equipment section (should be H2 with table)
    # Pattern needs to account for class="h2-header" attribute in the <p> tag
    animals_match = re.search(r'<p id="header-\d+-animals"[^>]*>.*?<span[^>]*>Animals</span></p>\s*<table', content)
    assert animals_match, "Animals H2 header with table not found in New Equipment section"
    animals_pos = animals_match.start()
    
    # Find the Weapons header that comes after Animals (should also be H2 with table)
    # Look for pattern: <p id="header-X-weapons" ...><span>Weapons</span></p><table>
    weapons_after_animals = re.search(r'<p id="header-\d+-weapons"[^>]*>.*?<span[^>]*>Weapons</span></p>\s*<table', content[animals_pos:])
    assert weapons_after_animals, "Weapons H2 header with table not found after Animals"
    weapons_pos = animals_pos + weapons_after_animals.start()
    
    # Verify Weapons comes after Animals
    assert weapons_pos > animals_pos, f"Weapons table (pos {weapons_pos}) should appear after Animals table (pos {animals_pos})"
    
    print(f"✓ Weapons table correctly positioned after Animals")


def test_weapons_table_structure():
    """Verify the Weapons table has correct structure: 8 columns, 2 header rows, 5 weapon rows."""
    html_file = Path("data/html_output/chapter-six-money-and-equipment.html")
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    content = html_file.read_text()
    
    # Find the Weapons table after Animals
    # First find Animals table (in New Equipment section - header-31)
    animals_table_match = re.search(
        r'<p id="header-3\d-animals"[^>]*>.*?Animals.*?</span></p>\s*<table.*?</table>',
        content,
        re.DOTALL
    )
    assert animals_table_match, "Could not find Animals table"
    
    # Now find Weapons table that comes after Animals
    content_after_animals = content[animals_table_match.end():]
    weapons_table_match = re.search(
        r'<p id="header-3\d-weapons"[^>]*>.*?Weapons.*?</span></p>\s*<table class="ds-table">(.*?)</table>',
        content_after_animals,
        re.DOTALL
    )
    assert weapons_table_match, "Could not find Weapons table after Animals table"
    
    table_content = weapons_table_match.group(1)
    
    # Count rows
    rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
    assert len(rows) == 7, f"Expected 7 rows (2 header + 5 data), found {len(rows)}"
    
    # Check first header row: ["Weapons", "", "", "", "", "", "Damage" (colspan=2)]
    first_header = rows[0]
    assert '<th>Weapons</th>' in first_header, "First header should have 'Weapons' column"
    assert 'colspan="2">Damage</th>' in first_header, "First header should have 'Damage' spanning 2 columns"
    
    # Count cells in first header (should be 8 including the colspan)
    header_cells = re.findall(r'<th[^>]*>([^<]*)</th>', first_header)
    # Weapons + 5 empty + Damage = 7 visible cells, but Damage spans 2, so 8 columns total
    
    # Check second header row: ["", "Cost", "Wt", "Size", "Type", "Speed", "S-M", "L"]
    second_header = rows[1]
    assert '<th>Cost</th>' in second_header, "Second header should have 'Cost' column"
    assert '<th>Wt</th>' in second_header, "Second header should have 'Wt' column"
    assert '<th>Size</th>' in second_header, "Second header should have 'Size' column"
    assert '<th>Type</th>' in second_header, "Second header should have 'Type' column"
    assert '<th>Speed</th>' in second_header, "Second header should have 'Speed' column"
    assert '<th>S-M</th>' in second_header, "Second header should have 'S-M' column"
    assert '<th>L</th>' in second_header, "Second header should have 'L' column"
    
    # Check weapon data rows
    weapon_names = ["Chatkcha", "Impaler", "Polearm, Gythka", "Quabone", "Wrist Razor"]
    for i, weapon_name in enumerate(weapon_names, start=2):
        weapon_row = rows[i]
        assert f'<td>{weapon_name}</td>' in weapon_row, f"Row {i} should contain weapon '{weapon_name}'"
    
    print(f"✓ Weapons table has correct structure: 8 columns, 2 header rows, 5 weapon rows")


def test_weapons_table_data_format():
    """Verify the Weapons table data follows the specified formats."""
    html_file = Path("data/html_output/chapter-six-money-and-equipment.html")
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    content = html_file.read_text()
    
    # Find the Weapons table (same as test_weapons_table_structure)
    animals_table_match = re.search(
        r'<p id="header-3\d-animals"[^>]*>.*?Animals.*?</span></p>\s*<table.*?</table>',
        content,
        re.DOTALL
    )
    assert animals_table_match, "Could not find Animals table"
    
    content_after_animals = content[animals_table_match.end():]
    weapons_table_match = re.search(
        r'<p id="header-3\d-weapons"[^>]*>.*?Weapons.*?</span></p>\s*<table class="ds-table">(.*?)</table>',
        content_after_animals,
        re.DOTALL
    )
    assert weapons_table_match, "Could not find Weapons table after Animals table"
    
    table_content = weapons_table_match.group(1)
    rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
    
    # Skip header rows, check data rows
    for row in rows[2:]:  # Skip 2 header rows
        cells = re.findall(r'<td>([^<]*)</td>', row)
        assert len(cells) == 8, f"Each data row should have 8 cells, found {len(cells)}"
        
        # Cell 0: Weapon name (string)
        # Cell 1: Cost (format: "# cp" or "# sp")
        cost = cells[1].strip()
        if cost and cost != '&nbsp;':
            assert re.match(r'\d+\s*[cs]p', cost), f"Cost should match '# cp' or '# sp', got '{cost}'"
        
        # Cell 2: Wt (numeric or fraction, can be empty)
        # Cell 3: Size (S, M, or L)
        size = cells[3].strip()
        if size and size != '&nbsp;':
            assert size in ['S', 'M', 'L'], f"Size should be S, M, or L, got '{size}'"
        
        # Cell 4: Type (single letter or combination like P/S, P/B)
        # Cell 5: Speed (numeric)
        speed = cells[5].strip()
        if speed and speed != '&nbsp;':
            assert speed.isdigit(), f"Speed should be numeric, got '{speed}'"
        
        # Cell 6: S-M (dice notation like "1d4+1" or "2d4")
        sm_damage = cells[6].strip()
        if sm_damage and sm_damage != '&nbsp;':
            assert re.match(r'\d+d\d+(\+\d+)?', sm_damage), f"S-M damage should be dice notation, got '{sm_damage}'"
        
        # Cell 7: L (dice notation like "1d3" or "1d10")
        l_damage = cells[7].strip()
        if l_damage and l_damage != '&nbsp;':
            assert re.match(r'\d+d\d+(\+\d+)?', l_damage), f"L damage should be dice notation, got '{l_damage}'"
    
    print(f"✓ Weapons table data follows specified formats")


def test_no_fragmented_headers():
    """Verify that fragmented column headers (Cost, Wt, Size as separate headers) are not present."""
    html_file = Path("data/html_output/chapter-six-money-and-equipment.html")
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    content = html_file.read_text()
    
    # Find the Weapons table after Animals (same as other tests)
    animals_table_match = re.search(
        r'<p id="header-3\d-animals"[^>]*>.*?Animals.*?</span></p>\s*<table.*?</table>',
        content,
        re.DOTALL
    )
    assert animals_table_match, "Could not find Animals table"
    
    content_after_animals = content[animals_table_match.end():]
    weapons_table_end = re.search(
        r'<p id="header-3\d-weapons"[^>]*>.*?Weapons.*?</span></p>\s*<table class="ds-table">.*?</table>',
        content_after_animals,
        re.DOTALL
    )
    assert weapons_table_end, "Could not find Weapons table"
    
    # Check the content after the Weapons table (relative to animals_table_match)
    content_after = content_after_animals[weapons_table_end.end():]
    
    # Look for Equipment Descriptions section (should be the next major section)
    next_section = re.search(r'<p id="header-\d+-equipment-descriptions">', content_after)
    if next_section:
        content_between = content_after[:next_section.start()]
    else:
        # Check up to 2000 chars after table
        content_between = content_after[:2000]
    
    # These should NOT appear as standalone H1 headers after the Weapons table
    fragmented_patterns = [
        r'<p id="header-\d+-cost"[^>]*>.*?<span[^>]*>Cost</span></p>(?!\s*<table)',  # Cost as header without table
        r'<p id="header-\d+-wt"[^>]*>.*?<span[^>]*>Wt</span></p>(?!\s*<table)',  # Wt as header without table
        r'<p id="header-\d+-size"[^>]*>.*?<span[^>]*>Size</span></p>(?!\s*<table)',  # Size as header without table
        r'<p id="header-\d+-type"[^>]*>.*?<span[^>]*>Type</span></p>(?!\s*<table)',  # Type as header without table
        r'<p id="header-\d+-speed"[^>]*>.*?<span[^>]*>Speed</span></p>(?!\s*<table)',  # Speed as header without table
        r'<p id="header-\d+-damage"[^>]*>.*?<span[^>]*>Damage</span></p>(?!\s*<table)',  # Damage as header without table
    ]
    
    for pattern in fragmented_patterns:
        match = re.search(pattern, content_between, re.IGNORECASE)
        assert not match, f"Found fragmented header that should have been removed: {match.group(0) if match else ''}"
    
    print(f"✓ No fragmented column headers found after Weapons table")


if __name__ == "__main__":
    print("Testing Chapter 6 Weapons table...")
    try:
        test_weapons_table_after_animals()
        test_weapons_table_structure()
        test_weapons_table_data_format()
        test_no_fragmented_headers()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise

