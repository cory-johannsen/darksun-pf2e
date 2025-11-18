"""Unit tests for Chapter 7 (Magic) postprocessing.

Tests the HTML postprocessing logic that fixes issues with:
- Duplicate table elements
- Spell ordering in 2-column layouts
- Prose paragraphs mixed with spell lists
"""

import re


def test_cosmos_sphere_paragraph_extraction():
    """Test that prose paragraphs are correctly extracted from spell lists.
    
    The Sphere of the Cosmos section has two descriptive paragraphs that
    should appear after the spell list but before Wizardly Magic:
    1. "Clerics have major access to the sphere of the element they worship..."
    2. "There are no deities in Dark Sun..."
    
    This test verifies these paragraphs are:
    - Not fragmented
    - Not intermixed with spell list items
    - Placed correctly in the output
    """
    # Read the generated HTML
    with open("data/html_output/chapter-seven-magic.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Test 1: Verify the clerics paragraph exists as a complete paragraph
    # Use \s+ to match any amount of whitespace (to handle cases with extra spaces)
    clerics_pattern = r'<p>Clerics\s+have\s+major\s+access\s+to\s+the\s+sphere\s+of\s+the\s+element\s+they\s+worship,\s+plus\s+minor\s+access\s+to\s+the\s+Sphere\s+of\s+the\s+Cosmos\.\s+Templars\s+have\s+major\s+access\s+to\s+all\s+spheres,\s+but\s+gain\s+spells\s+more\s+slowly\.</p>'
    assert re.search(clerics_pattern, html), "Clerics paragraph should be a complete, non-fragmented paragraph"
    
    # Test 2: Verify the deities paragraph exists as a complete paragraph
    deities_pattern = r'<p>\s*There\s+are\s+no\s+deities\s+in\s+Dark\s+Sun\.\s+Those\s+spells\s+that\s+indicate\s+some\s+contact\s+with\s+a\s+deity\s+instead\s+reflect\s+contact\s+with\s+a\s+powerful\s+being\s+of\s+the\s+elemental\s+planes\.</p>'
    assert re.search(deities_pattern, html), "Deities paragraph should be a complete, non-fragmented paragraph"
    
    # Test 3: Verify the paragraphs appear together (not separated by spell items)
    # Use flexible whitespace matching
    combined_pattern = (
        r'<p>Clerics\s+have\s+major\s+access\s+to\s+the\s+sphere\s+of\s+the\s+element\s+they\s+worship,\s+plus\s+minor\s+access\s+to\s+the\s+Sphere\s+of\s+the\s+Cosmos\.\s+Templars\s+have\s+major\s+access\s+to\s+all\s+spheres,\s+but\s+gain\s+spells\s+more\s+slowly\.</p>\s*'
        r'<p>\s*There\s+are\s+no\s+deities\s+in\s+Dark\s+Sun\.\s+Those\s+spells\s+that\s+indicate\s+some\s+contact\s+with\s+a\s+deity\s+instead\s+reflect\s+contact\s+with\s+a\s+powerful\s+being\s+of\s+the\s+elemental\s+planes\.</p>'
    )
    assert re.search(combined_pattern, html), "Both paragraphs should appear together without spell items between them"
    
    # Test 4: Verify the paragraphs appear before Wizardly Magic
    # Extract the section between Sphere of the Cosmos and Wizardly Magic
    cosmos_to_wizardly = re.search(
        r'<p id="header-5-sphere-of-the-cosmos">.*?<p id="header-6-wizardly-magic">',
        html,
        re.DOTALL
    )
    assert cosmos_to_wizardly, "Should find section from Cosmos to Wizardly Magic"
    
    section = cosmos_to_wizardly.group(0)
    
    # Verify both paragraphs are in this section
    assert "Clerics have major access" in section, "Clerics paragraph should be in Sphere of the Cosmos section"
    assert "There are no deities" in section, "Deities paragraph should be in Sphere of the Cosmos section"
    
    # Test 5: Verify the fragmented versions do NOT exist
    fragmented_clerics_patterns = [
        r'<p>Clerics have major access to the sphere of the ele-</p>',
        r'<p>ment they worship, plus minor access to the Sphere</p>',
    ]
    
    for pattern in fragmented_clerics_patterns:
        assert not re.search(pattern, html), f"Fragmented clerics paragraph should not exist: {pattern}"
    
    fragmented_deities_patterns = [
        r'<p>There are no deities in Dark Sun\. Those spells</p>',
        r'<p>that indicate some contact with a deity instead reflect contact with a powerful being of the elemental</p>',
    ]
    
    for pattern in fragmented_deities_patterns:
        assert not re.search(pattern, html), f"Fragmented deities paragraph should not exist: {pattern}"
    
    # Test 6: Verify the paragraphs are NOT intermixed with spell list items
    # Check that there are no <li> tags between the two paragraphs
    intermixed_pattern = (
        r'<p>Clerics have major access.*?</p>.*?<li class="spell-list-item">.*?<p>There are no deities'
    )
    assert not re.search(intermixed_pattern, html, re.DOTALL), "Paragraphs should not have spell list items between them"
    
    # Test 7: CRITICAL - Verify paragraphs are NOT inside the spell list
    # These paragraphs should appear AFTER all spell items, not between them
    # Look for spell items AFTER the clerics paragraph - this indicates the paragraphs are in the wrong place
    spell_after_paragraph_pattern = (
        r'<p>Clerics have major access.*?</p>.*?<ul class="spell-list">.*?<li class="spell-list-item">'
    )
    assert not re.search(spell_after_paragraph_pattern, html, re.DOTALL), (
        "Clerics paragraph should NOT be followed by more spell list items. "
        "The paragraphs must appear AFTER all spell lists in the Sphere of the Cosmos section."
    )
    
    # Test 8: Verify the last spell item in Cosmos comes BEFORE the paragraphs
    # The last 7th level spells should appear before the clerics paragraph
    last_spell_before_paragraphs = (
        r'Symbol \(7th\).*?</ul>.*?<p>Clerics have major access'
    )
    assert re.search(last_spell_before_paragraphs, html, re.DOTALL), (
        "The last spell in Sphere of the Cosmos (Symbol) should appear BEFORE the clerics paragraph"
    )
    
    print("✅ All Chapter 7 Sphere of the Cosmos paragraph tests passed")


def test_spell_list_structure():
    """Test that spell lists are properly structured without prose paragraphs intermixed."""
    with open("data/html_output/chapter-seven-magic.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # Find all spell list items in the Sphere of the Cosmos section
    cosmos_section = re.search(
        r'<p id="header-5-sphere-of-the-cosmos">.*?<p id="header-6-wizardly-magic">',
        html,
        re.DOTALL
    )
    
    if cosmos_section:
        section_html = cosmos_section.group(0)
        
        # Count spell list items
        spell_items = re.findall(r'<li class="spell-list-item">([^<]+)</li>', section_html)
        assert len(spell_items) > 0, "Should find spell list items in Sphere of the Cosmos"
        
        # Verify that each spell item matches the pattern "Name (level)"
        spell_pattern = re.compile(r'^.+?\s*\(\d+(?:st|nd|rd|th)\)$')
        for spell in spell_items:
            assert spell_pattern.match(spell.strip()), f"Spell item should match pattern: {spell}"
        
        print(f"✅ Found {len(spell_items)} properly formatted spell items in Sphere of the Cosmos")


if __name__ == "__main__":
    test_cosmos_sphere_paragraph_extraction()
    test_spell_list_structure()
    print("\n✅ ALL CHAPTER 7 POSTPROCESSING TESTS PASSED")

