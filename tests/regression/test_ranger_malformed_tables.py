"""
Test to verify no malformed tables exist in the Ranger section.

The user reported two malformed tables appearing after the paragraph ending 
"ranger answers that challenge." and before the paragraph beginning 
"A rangers motivations can vary greatly".

These malformed tables mix paragraph text with table data like:
- "largely unchanged. The wilderness is harsh and unforgiving, calling for skilled and capable men to" 
  mixed with "01-04 Aarakocra"
- Similar fragments

This regression test ensures such malformed tables don't exist.
"""

import re
import sys
from pathlib import Path

def test_no_malformed_ranger_tables():
    """Verify no malformed tables exist in the Ranger section."""
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the position of key text markers
    ranger_challenge_pos = html_content.find("the ranger answers that challenge.")
    rangers_motivations_pos = html_content.find("A rangers motivations can vary greatly")
    
    if ranger_challenge_pos == -1:
        print("ERROR: Could not find 'the ranger answers that challenge' text")
        return False
    
    if rangers_motivations_pos == -1:
        print("WARNING: Could not find 'A rangers motivations can vary greatly' text - might be missing")
        # Use end of section as fallback
        rangers_motivations_pos = html_content.find('id="header-21-rangers-followers"')
        if rangers_motivations_pos == -1:
            print("ERROR: Could not find Rangers Followers header either")
            return False
    
    # Extract the HTML content between these two markers
    section_html = html_content[ranger_challenge_pos:rangers_motivations_pos]
    
    # Check 1: Look for tables in this section
    tables_in_section = re.findall(r'<table[^>]*>.*?</table>', section_html, re.DOTALL)
    
    if len(tables_in_section) > 1:
        print(f"FAIL: Found {len(tables_in_section)} tables between 'ranger answers that challenge' and 'Rangers Followers'")
        print(f"  Expected: At most 1 table (the requirements table)")
        print(f"\n  Malformed table(s) detected:")
        for i, table in enumerate(tables_in_section[1:], 1):
            # Show first 200 chars of each extra table
            table_preview = table[:200].replace('\n', ' ')
            print(f"    Table {i}: {table_preview}...")
        return False
    
    # Check 2: Look for specific telltale signs of malformed tables
    malformed_indicators = [
        "largely unchanged.*Aarakocra",  # Paragraph text mixed with table data
        "A rangers motivations.*Behir",  # Another common fragment
        "<td>largely unchanged",          # Table cell with paragraph text
        "<td>harsh and unforgiving",      # Another paragraph fragment in table
    ]
    
    for indicator in malformed_indicators:
        if re.search(indicator, section_html, re.IGNORECASE):
            print(f"FAIL: Found malformed table indicator: {indicator}")
            print(f"  This suggests paragraph text is mixed with table data")
            return False
    
    # Check 3: The only table allowed is the requirements table immediately after the Ranger header
    # It should have: Ability Requirements, Prime Requisite, Races Allowed
    if len(tables_in_section) == 1:
        table = tables_in_section[0]
        if not ("Ability Requirements" in table and 
                "Prime Requisite" in table and 
                "Races Allowed" in table):
            print(f"FAIL: Found an unexpected table in the Ranger section")
            print(f"  The only table should be the class requirements table")
            table_preview = table[:300].replace('\n', ' ')
            print(f"  Found: {table_preview}...")
            return False
    
    print("✅ PASS: No malformed tables found in the Ranger section")
    print(f"  Section checked: positions {ranger_challenge_pos} to {rangers_motivations_pos}")
    print(f"  Tables found: {len(tables_in_section)} (expected: 0-1 requirements table)")
    return True


if __name__ == "__main__":
    success = test_no_malformed_ranger_tables()
    sys.exit(0 if success else 1)

