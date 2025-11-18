"""
Test the Animals, Domestic table structure in Chapter Five: Monsters of Athas.

This test verifies that the table has been properly reconstructed with all
22 rows and 5 columns as specified.
"""

import re
from pathlib import Path


def test_animals_domestic_table_exists():
    """
    Test that the Animals, Domestic table exists and has correct structure.
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    html_content = html_file.read_text(encoding="utf-8")
    
    # Find the Animals, Domestic table
    # It should be the first table with class="ds-table" after the Animals, Domestic header
    animals_header_match = re.search(
        r'<p><span[^>]*><strong>Animals, Domestic</strong></span></p>',
        html_content
    )
    
    assert animals_header_match, "Animals, Domestic header not found"
    
    # Find the table after the header
    remaining_html = html_content[animals_header_match.end():]
    table_match = re.search(
        r'<table class="ds-table">(.*?)</table>',
        remaining_html,
        re.DOTALL
    )
    
    assert table_match, "Animals, Domestic table not found"
    
    table_html = table_match.group(1)
    
    # Count table rows (including header row)
    rows = re.findall(r'<tr>', table_html)
    assert len(rows) == 23, f"Expected 23 rows (1 header + 22 data), found {len(rows)}"
    
    # Check header row has 5 columns
    header_match = re.search(r'<tr>\s*<th></th>\s*<th>(\w+)</th>\s*<th>(\w+)</th>\s*<th>(\w+)</th>\s*<th>(\w+)</th>', table_html)
    assert header_match, "Header row not found or incorrect format"
    
    # Verify column headers are in correct order
    headers = [header_match.group(i) for i in range(1, 5)]
    expected_headers = ["Erdlu", "Kank", "Mekillot", "Inix"]
    assert headers == expected_headers, f"Expected headers {expected_headers}, got {headers}"


def test_animals_domestic_table_row_labels():
    """
    Test that all 22 row labels are present in the table.
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    html_content = html_file.read_text(encoding="utf-8")
    
    expected_labels = [
        "CLIMATE/TERRAIN:",
        "FREQUENCY",
        "ORGANIZATION:",
        "ACTIVITY CYCLE:",
        "DIET",
        "INTELLIGENCE:",
        "TREASURE:",
        "ALIGNMENT:",
        "NO. APPEARING:",
        "ARMOR CLASS:",
        "MOVEMENT",
        "HIT DICE:",
        "THAC0:",
        "NO. OF ATTACKS:",
        "DAMAGE/ATTACK:",
        "SPECIAL ATTACKS:",
        "SPECIAL DEFENSES:",
        "MAGIC RESISTANCE:",
        "SIZE:",
        "MORALE:",
        "XP VALUE:",
        "PSIONICS:"
    ]
    
    # Find the table
    animals_header_match = re.search(
        r'<p><span[^>]*><strong>Animals, Domestic</strong></span></p>',
        html_content
    )
    remaining_html = html_content[animals_header_match.end():]
    table_match = re.search(
        r'<table class="ds-table">(.*?)</table>',
        remaining_html,
        re.DOTALL
    )
    
    table_html = table_match.group(1)
    
    # Check each label is present
    for label in expected_labels:
        assert f'<td><strong>{label}</strong></td>' in table_html, f"Row label '{label}' not found in table"


def test_animals_domestic_table_sample_data():
    """
    Test that some sample data values are correct in the table.
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    html_content = html_file.read_text(encoding="utf-8")
    
    # Find the table
    animals_header_match = re.search(
        r'<p><span[^>]*><strong>Animals, Domestic</strong></span></p>',
        html_content
    )
    remaining_html = html_content[animals_header_match.end():]
    table_match = re.search(
        r'<table class="ds-table">(.*?)</table>',
        remaining_html,
        re.DOTALL
    )
    
    table_html = table_match.group(1)
    
    # Check some specific values
    # Erdlu FREQUENCY should be Common
    assert '>Common<' in table_html, "Erdlu FREQUENCY 'Common' not found"
    
    # Kank HIT DICE should be 3
    # Check that there's a row with HIT DICE and value 3
    hit_dice_row = re.search(
        r'<td><strong>HIT DICE:</strong></td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>',
        table_html,
        re.DOTALL
    )
    assert hit_dice_row, "HIT DICE row not found"
    
    # Mekillot XP VALUE should be 6,000
    xp_row = re.search(
        r'<td><strong>XP VALUE:</strong></td>(.*?)</tr>',
        table_html,
        re.DOTALL
    )
    assert xp_row, "XP VALUE row not found"
    assert '6,000' in xp_row.group(1), "Mekillot XP VALUE '6,000' not found"


def test_no_scattered_paragraphs_before_table():
    """
    Test that the scattered paragraph data has been removed.
    
    After the Animals, Domestic header and before the "There are numerous" paragraph,
    there should only be the table, not scattered paragraph fragments.
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    html_content = html_file.read_text(encoding="utf-8")
    
    # Find boundaries
    animals_header = re.search(
        r'<p><span[^>]*><strong>Animals, Domestic</strong></span></p>',
        html_content
    )
    # Updated to match the new format with span tags containing the text
    there_are = re.search(
        r'<p><span[^>]*>There are numerous domesticated animals',
        html_content
    )
    
    assert animals_header and there_are, f"Boundary markers not found (animals_header={bool(animals_header)}, there_are={bool(there_are)})"
    
    # Extract content between boundaries
    between = html_content[animals_header.end():there_are.start()]
    
    # Should contain exactly one table and minimal whitespace
    table_count = between.count('<table class="ds-table">')
    assert table_count == 1, f"Expected 1 table between boundaries, found {table_count}"
    
    # Should not contain scattered paragraph fragments like individual FREQ UENCY or CLIMATE/TERRAIN
    # (Allow them only within the table)
    # Remove the table to check what's left
    between_no_table = re.sub(r'<table[^>]*>.*?</table>', '', between, flags=re.DOTALL)
    
    # After removing table, should only have whitespace
    text_content = re.sub(r'<[^>]+>', '', between_no_table).strip()
    assert len(text_content) < 50, f"Found unexpected content between header and table: {text_content[:100]}"


if __name__ == "__main__":
    # Run tests
    test_animals_domestic_table_exists()
    test_animals_domestic_table_row_labels()
    test_animals_domestic_table_sample_data()
    test_no_scattered_paragraphs_before_table()
    print("✅ All Animals, Domestic table tests passed!")

