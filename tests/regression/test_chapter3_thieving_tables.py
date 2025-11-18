"""
Regression test for Chapter 3 thieving tables.

This test verifies that the Thieving Skill Exceptional Dexterity Adjustments table
and the Thieving Skill Racial Adjustments table render properly as HTML tables,
not as malformed headers or paragraphs.
"""

import os
import re
from pathlib import Path


def test_dexterity_adjustments_table():
    """Verify that the Thieving Skill Exceptional Dexterity Adjustments table renders as a proper HTML table."""
    
    html_file = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_file.exists():
        # HTML not generated yet, skip test
        print(f"HTML file not found at {html_file}, skipping test")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the section with the Dexterity table header
    dex_header_pattern = r'Thieving Skill Exceptional Dexterity Adjustments'
    assert re.search(dex_header_pattern, html_content), \
        "Thieving Skill Exceptional Dexterity Adjustments header not found in HTML"
    
    # Extract the section after the Dexterity header up to the next major header
    # Use a more specific pattern that looks for the header followed by the table
    dex_section_match = re.search(
        r'id="header-[^"]*-thieving-skill-exceptional-dexterity-adjustments"[^>]*>.*?</p>\s*(<table.*?</table>)',
        html_content,
        re.DOTALL
    )
    
    assert dex_section_match, \
        "Expected to find a table after Dexterity Adjustments header, but found none"
    
    table_html = dex_section_match.group(1)
    
    # Verify the table has the expected structure
    # Should have 1 header row + 5 data rows (Dex 18-22)
    assert '<table' in table_html, "Table tag not found"
    assert 'class="ds-table"' in table_html, "Table missing ds-table class"
    
    # Count rows
    row_count = table_html.count('<tr>')
    assert row_count == 6, f"Expected 6 rows (1 header + 5 data), found {row_count}"
    
    # Verify header cells
    assert '>Dex<' in table_html, "Header 'Dex' not found"
    assert '>Pick Pockets<' in table_html, "Header 'Pick Pockets' not found"
    assert '>Open Locks<' in table_html, "Header 'Open Locks' not found"
    assert '>Find/Remove Traps<' in table_html, "Header 'Find/Remove Traps' not found"
    assert '>Move Silently<' in table_html, "Header 'Move Silently' not found"
    assert '>Hide in Shadows<' in table_html, "Header 'Hide in Shadows' not found"
    
    # Verify some data cells
    assert '>18<' in table_html, "Dex value '18' not found"
    assert '>19<' in table_html, "Dex value '19' not found"
    assert '>20<' in table_html, "Dex value '20' not found"
    assert '>21<' in table_html, "Dex value '21' not found"
    assert '>22<' in table_html, "Dex value '22' not found"
    assert '>+10%<' in table_html, "Percentage '+10%' not found"
    assert '>+15%<' in table_html, "Percentage '+15%' not found"
    
    # Make sure it's NOT rendered as headers (regression check)
    # The table content should NOT appear as H2 headers
    bad_pattern = r'<span class="header-h2"[^>]*>(?:Dex|Pick|Open|Find|Move|Hide)'
    assert not re.search(bad_pattern, table_html), \
        "Table columns are being rendered as H2 headers (regression detected)"
    
    print("✅ Thieving Skill Exceptional Dexterity Adjustments table renders correctly")


def test_racial_adjustments_table():
    """Verify that the Thieving Skill Racial Adjustments table renders as a proper HTML table."""
    
    html_file = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_file.exists():
        # HTML not generated yet, skip test
        print(f"HTML file not found at {html_file}, skipping test")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the section with the Racial Adjustments table header
    racial_header_pattern = r'Thieving Skill Racial Adjustments'
    assert re.search(racial_header_pattern, html_content), \
        "Thieving Skill Racial Adjustments header not found in HTML"
    
    # Extract the section after the Racial Adjustments header
    # Use a more specific pattern that looks for the header followed by the table
    racial_section_match = re.search(
        r'id="header-[^"]*-thieving-skill-racial-adjustments"[^>]*>.*?</p>\s*(<table.*?</table>)',
        html_content,
        re.DOTALL
    )
    
    assert racial_section_match, \
        "Expected to find a table after Racial Adjustments header, but found none"
    
    table_html = racial_section_match.group(1)
    
    # Verify the table has the expected structure
    # Should have 1 header row + 8 skill rows
    assert '<table' in table_html, "Table tag not found"
    assert 'class="ds-table"' in table_html, "Table missing ds-table class"
    
    # Count rows
    row_count = table_html.count('<tr>')
    assert row_count == 9, f"Expected 9 rows (1 header + 8 skills), found {row_count}"
    
    # Verify header cells
    assert '>Skill<' in table_html, "Header 'Skill' not found"
    assert '>Dwarf<' in table_html, "Header 'Dwarf' not found"
    assert '>Elf<' in table_html, "Header 'Elf' not found"
    assert '>Half-elf<' in table_html, "Header 'Half-elf' not found"
    assert '>Halfling<' in table_html, "Header 'Halfling' not found"
    assert '>Mul<' in table_html, "Header 'Mul' not found"
    
    # Verify some skill rows
    assert '>Pick Pockets<' in table_html, "Skill 'Pick Pockets' not found"
    assert '>Open Locks<' in table_html, "Skill 'Open Locks' not found"
    assert '>Find/Remove Traps<' in table_html, "Skill 'Find/Remove Traps' not found"
    assert '>Climb Walls<' in table_html, "Skill 'Climb Walls' not found"
    
    # Make sure it's NOT rendered as headers (regression check)
    bad_pattern = r'<span class="header-h2"[^>]*>(?:Skill|Dwarf|Elf|Half-elf|Halfling|Mul)'
    assert not re.search(bad_pattern, table_html), \
        "Table columns are being rendered as H2 headers (regression detected)"
    
    print("✅ Thieving Skill Racial Adjustments table renders correctly")


if __name__ == "__main__":
    try:
        test_dexterity_adjustments_table()
        test_racial_adjustments_table()
        print("\n🎉 All Chapter 3 thieving table tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)

