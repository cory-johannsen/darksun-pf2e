"""
Test to verify the Rangers Followers table is correctly positioned.

The table should appear AFTER the sentence "To determine the type of follower acquired,
consult the following table (rolling once for each follower)." and NOT after 
"the ranger answers that challenge."
"""

import sys
from pathlib import Path

def test_rangers_followers_table_placement():
    """Verify Rangers Followers table appears in the correct location."""
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_path.exists():
        print(f"ERROR: HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find the position of key text markers
    ranger_challenge_pos = html_content.find("the ranger answers that challenge.")
    consult_table_pos = html_content.find("consult the following table")
    table_header_pos = html_content.find('Follower Type</th>')  # Part of the Rangers Followers table header
    
    if ranger_challenge_pos == -1:
        print("ERROR: Could not find 'the ranger answers that challenge' text")
        return False
    
    if consult_table_pos == -1:
        print("ERROR: Could not find 'consult the following table' text")
        return False
    
    if table_header_pos == -1:
        print("ERROR: Could not find Rangers Followers table (looking for 'Follower Type' header)")
        return False
    
    # The table should appear AFTER "consult the following table"
    # and NOT between "ranger answers" and "consult the following table"
    
    # Check 1: Table should be AFTER consult_table_pos
    if table_header_pos < consult_table_pos:
        print(f"FAIL: Rangers Followers table appears BEFORE 'consult the following table'")
        print(f"  'ranger answers that challenge' at position: {ranger_challenge_pos}")
        print(f"  'consult the following table' at position: {consult_table_pos}")
        print(f"  Table header at position: {table_header_pos}")
        print(f"\n  The table should appear AFTER the 'consult the following table' sentence.")
        return False
    
    # Check 2: Table should NOT be between ranger_challenge and consult_table
    if ranger_challenge_pos < table_header_pos < consult_table_pos:
        print(f"FAIL: Rangers Followers table appears in the WRONG location")
        print(f"  Table is between 'ranger answers that challenge' and 'consult the following table'")
        print(f"  'ranger answers that challenge' at position: {ranger_challenge_pos}")
        print(f"  Table header at position: {table_header_pos}")
        print(f"  'consult the following table' at position: {consult_table_pos}")
        return False
    
    # Check 3: Verify the table header "RANGERS FOLLOWERS" is present (as H2)
    rangers_followers_header = 'RANGERS FOLLOWERS</h2>'
    if rangers_followers_header not in html_content:
        print(f"WARNING: Could not find 'RANGERS FOLLOWERS' H2 header")
        # This is a warning, not a failure - the header might be formatted differently
    
    # Check 4: Verify there's only ONE Rangers Followers table
    follower_type_count = html_content.count('Follower Type</th>')
    if follower_type_count > 1:
        print(f"FAIL: Found {follower_type_count} instances of Rangers Followers table, expected 1")
        return False
    
    print("PASS: Rangers Followers table is correctly positioned after 'consult the following table'")
    print(f"  'ranger answers that challenge' at position: {ranger_challenge_pos}")
    print(f"  'consult the following table' at position: {consult_table_pos}")
    print(f"  Table header at position: {table_header_pos}")
    return True


if __name__ == "__main__":
    success = test_rangers_followers_table_placement()
    sys.exit(0 if success else 1)

