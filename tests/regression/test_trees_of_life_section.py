"""Regression test for Trees of Life section formatting in Chapter 7.

This test verifies that the Trees of Life section has:
1. Two paragraphs with a break at "tree of life is, in essence, a living magical item"
2. "Special Powers:" as an H2 header
3. "Destroying a Tree of Life:" as an H2 header  
4. "Regeneration:" as an H2 header
5. No corrupt table data mixed into the paragraphs
"""

import re
from pathlib import Path

def test_trees_of_life_section():
    """Test that Trees of Life section is properly formatted."""
    html_file = Path("data/html_output/chapter-seven-magic.html")
    
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_file}")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find the Trees of Life section
    trees_header_match = re.search(r'<p id="header-12-trees-of-life">', html)
    assert trees_header_match, "Could not find Trees of Life header"
    
    # Find the next major section (Magical Items)
    next_section_match = re.search(r'<p id="header-15-magical-items">', html)
    assert next_section_match, "Could not find Magical Items header"
    
    # Extract the Trees of Life section
    section = html[trees_header_match.start():next_section_match.start()]
    
    # Test 1: Check for two paragraphs with proper break
    # First paragraph should end with "tree of life is, in essence, a living magical item"
    # Note: The text may have spacing issues like "Atree" or "oftrees" instead of "A tree" or "of trees"
    first_para_pattern = r'A\s*tree\s*of\s*life\s*is.*?tree\s*of\s*life\s*is,\s+in\s+essence,\s+a\s+living\s+magical\s+item\.</p>'
    assert re.search(first_para_pattern, section, re.DOTALL), \
        "First paragraph should end with 'tree of life is, in essence, a living magical item.'"
    
    # Second paragraph should start with "It stores and channels"
    second_para_pattern = r'<p>It\s+stores\s+and\s+channels\s+energies'
    assert re.search(second_para_pattern, section), \
        "Second paragraph should start with 'It stores and channels energies'"
    
    # Test 2: "Special Powers:" should be H2
    special_powers_pattern = r'<p id="header-13-special-powers">\s*<a href="#top"[^>]*>\[.?\]</a>\s*<span class="header-h2"[^>]*>Special Powers:</span></p>'
    assert re.search(special_powers_pattern, section), \
        "Special Powers: should be an H2 header (no roman numeral, header-h2 class)"
    
    # Test 3: "Destroying a Tree of Life:" should be H2
    # Note: The ID might be like "header-13a-..." (with letter suffix)
    destroying_pattern = r'<p id="header-\d+[a-z]?-destroying-a-tree-of-life">\s*<a href="#top"[^>]*>\[.?\]</a>\s*<span class="header-h2"[^>]*>Destroying a Tree of Life:</span></p>'
    assert re.search(destroying_pattern, section), \
        "Destroying a Tree of Life: should be an H2 header (no roman numeral, header-h2 class)"
    
    # Test 4: "Regeneration:" should be H2
    regeneration_pattern = r'<p id="header-14-regeneration">\s*<a href="#top"[^>]*>\[.?\]</a>\s*<span class="header-h2"[^>]*>Regeneration:</span></p>'
    assert re.search(regeneration_pattern, section), \
        "Regeneration: should be an H2 header (no roman numeral, header-h2 class)"
    
    # Test 5: No corrupt table data
    # Check for armor type data that doesn't belong
    corrupt_patterns = [
        r'Hide\s+Leather',
        r'Padded.*Ring\s+Mail',
        r'Studded\s+Leather.*Metal\s+Armor',
        r'<table class="ds-table"><tr><td>nally created by wizards'
    ]
    
    for pattern in corrupt_patterns:
        assert not re.search(pattern, section), \
            f"Found corrupt table data in Trees of Life section: {pattern}"
    
    # Test 6: Verify complete text flow is present
    # Check that the "Trees of life in the World of Athas" paragraph exists and is complete
    athas_paragraph_pattern = r'Though\s+originally\s+created\s+by\s+wizards\s+to\s+combat\s+the\s+destruction\s+of\s+nature,\s+trees\s+of\s+life\s+are\s+now\s+heavily\s+exploited\s+by\s+defilers'
    assert re.search(athas_paragraph_pattern, section), \
        "Should have complete 'Trees of life in the World of Athas' paragraph"
    
    print("✓ Trees of Life section formatting is correct")

if __name__ == "__main__":
    test_trees_of_life_section()
    print("\nAll Trees of Life section tests passed!")

