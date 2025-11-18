#!/usr/bin/env python3
"""
Unit test for Transport table row counts.

Validates that the Transport table has the correct number of rows in each section
according to the specification.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_transport_table_structure():
    """Test that the Transport table has the correct row counts per section."""
    html_file = project_root / "data" / "html_output" / "chapter-six-money-and-equipment.html"
    
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the Transport table section
    transport_header = 'id="header-30-transport"'
    assert transport_header in content, "Transport header not found"
    
    # Extract the table that comes after the Transport header
    # Find the table after the Transport header
    start_idx = content.find(transport_header)
    table_start = content.find('<table class="ds-table">', start_idx)
    table_end = content.find('</table>', table_start) + len('</table>')
    
    table_html = content[table_start:table_end]
    
    # Count rows for each section
    sections = {
        "Chariot": 0,
        "Howdah": 0,
        "Wagon, open": 0,
        "Wagon, enclosed": 0
    }
    
    current_section = None
    lines = table_html.split('<tr>')
    
    for line in lines:
        # Check if this is a section header row
        if '<strong>Chariot</strong>' in line:
            current_section = "Chariot"
        elif '<strong>Howdah</strong>' in line:
            current_section = "Howdah"
        elif '<strong>Wagon, open</strong>' in line:
            current_section = "Wagon, open"
        elif '<strong>Wagon, enclosed</strong>' in line:
            current_section = "Wagon, enclosed"
        elif current_section and '<td>' in line and '</td>' in line:
            # This is a data row (not a header row with <th>)
            if '<th>' not in line and 'Type' not in line and 'Price' not in line:
                sections[current_section] += 1
    
    # Expected row counts per specification
    expected = {
        "Chariot": 3,
        "Howdah": 4,
        "Wagon, open": 4,  # Should include 10,000 pound capacity
        "Wagon, enclosed": 5  # Includes 10,000 pound capacity + armored caravan
    }
    
    print("\nTransport Table Row Counts:")
    print("=" * 60)
    for section, count in sections.items():
        expected_count = expected[section]
        status = "✓" if count == expected_count else "✗"
        print(f"{status} {section}: {count} rows (expected {expected_count})")
    
    # Verify each section
    errors = []
    for section, expected_count in expected.items():
        actual_count = sections[section]
        if actual_count != expected_count:
            errors.append(f"{section}: has {actual_count} rows, expected {expected_count}")
    
    if errors:
        raise AssertionError("Transport table row count mismatch:\n  " + "\n  ".join(errors))
    
    print("=" * 60)


def test_wagon_open_10000_capacity():
    """Test that Wagon, open section includes the 10,000 pound capacity row."""
    html_file = project_root / "data" / "html_output" / "chapter-six-money-and-equipment.html"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the Transport table section
    transport_header = 'id="header-30-transport"'
    start_idx = content.find(transport_header)
    table_start = content.find('<table class="ds-table">', start_idx)
    table_end = content.find('</table>', table_start) + len('</table>')
    
    table_html = content[table_start:table_end]
    
    # Check if 10,000 pound capacity appears in Wagon, open section
    # It should appear between <strong>Wagon, open</strong> and <strong>Wagon, enclosed</strong>
    wagon_open_idx = table_html.find('<strong>Wagon, open</strong>')
    wagon_enclosed_idx = table_html.find('<strong>Wagon, enclosed</strong>')
    
    assert wagon_open_idx >= 0, "Wagon, open section not found"
    assert wagon_enclosed_idx >= 0, "Wagon, enclosed section not found"
    
    wagon_open_section = table_html[wagon_open_idx:wagon_enclosed_idx]
    
    # Check for the 10,000 pound capacity row
    assert '10,000 pound capacity' in wagon_open_section, \
        "10,000 pound capacity row missing from Wagon, open section"
    
    print("✓ Wagon, open section includes 10,000 pound capacity row")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TRANSPORT TABLE ROW COUNT TESTS")
    print("=" * 70 + "\n")
    
    try:
        test_transport_table_structure()
        print("\n✓ Transport table structure test passed\n")
    except AssertionError as e:
        print(f"\n✗ Transport table structure test FAILED: {e}\n")
    
    try:
        test_wagon_open_10000_capacity()
        print("\n✓ Wagon, open 10,000 capacity test passed\n")
    except AssertionError as e:
        print(f"\n✗ Wagon, open 10,000 capacity test FAILED: {e}\n")
    
    print("=" * 70 + "\n")

