"""Regression test for Chapter 7 Wizardly Magic intro paragraph merge.

This test verifies that the text between "Wizardly Magic" and "Defiling" headers
is rendered as a single paragraph, not multiple fragmented paragraphs.

Issue: The PDF extraction split this text into 5 separate blocks, which were
being rendered as 5 separate paragraphs. The fix merges them into one.
"""

import re
from pathlib import Path


def test_wizardly_magic_single_paragraph():
    """Test that the Wizardly Magic intro is rendered as a single paragraph."""
    
    html_file = Path("data/html_output/chapter-seven-magic.html")
    
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    content = html_file.read_text(encoding='utf-8')
    
    # Find the section between Wizardly Magic and Defiling headers
    # Pattern: Find text after Wizardly Magic header and before Defiling header
    pattern = re.compile(
        r'<p id="header-6-wizardly-magic">.*?</p>'  # Wizardly Magic header
        r'(.*?)'  # Capture content between headers
        r'<p id="header-7-defiling">',  # Defiling header
        re.DOTALL
    )
    
    match = pattern.search(content)
    assert match, "Could not find Wizardly Magic and Defiling headers"
    
    content_between = match.group(1).strip()
    
    # Count paragraphs in this section
    # Should be exactly one <p> tag
    paragraph_count = content_between.count('<p>')
    
    assert paragraph_count == 1, (
        f"Expected 1 paragraph between Wizardly Magic and Defiling, "
        f"but found {paragraph_count}. Content: {content_between[:200]}..."
    )
    
    # Verify the complete expected text is in a single paragraph
    expected_text_parts = [
        "Wizards draw their magical energies from the living things",
        "Preservers cast spells in harmony with nature",
        "Defilers care nothing for such harmony"
    ]
    
    for text_part in expected_text_parts:
        assert text_part in content_between, (
            f"Expected text '{text_part}' not found in paragraph"
        )
    
    # Ensure there are no line breaks creating fake paragraphs
    # The content should be in a single <p> tag
    assert '</p><p>' not in content_between, (
        "Found multiple paragraph tags, text should be in single paragraph"
    )
    
    print("✓ Wizardly Magic intro is correctly rendered as a single paragraph")


def test_wizardly_magic_text_completeness():
    """Test that all expected text is present in the merged paragraph."""
    
    html_file = Path("data/html_output/chapter-seven-magic.html")
    content = html_file.read_text(encoding='utf-8')
    
    # Extract the paragraph after Wizardly Magic
    pattern = re.compile(
        r'<p id="header-6-wizardly-magic">.*?</p>'
        r'<p>(.*?)</p>',
        re.DOTALL
    )
    
    match = pattern.search(content)
    assert match, "Could not find paragraph after Wizardly Magic header"
    
    paragraph_text = match.group(1).strip()
    
    # Remove HTML entities and tags for text comparison
    paragraph_text = re.sub(r'<[^>]+>', '', paragraph_text)
    paragraph_text = paragraph_text.replace('&#x27;', "'")
    
    # Expected complete text (allowing for minor formatting differences)
    expected_phrases = [
        "Wizards draw their magical energies",
        "from the living things and life-giving elements around them",
        "Preservers cast spells in harmony with nature",
        "using their magic so as to return to the land what they take from it",
        "Defilers care nothing for such harmony",
        "damage the land with every spell they cast"
    ]
    
    for phrase in expected_phrases:
        assert phrase in paragraph_text, (
            f"Expected phrase '{phrase}' not found in paragraph. "
            f"Paragraph text: {paragraph_text}"
        )
    
    # Ensure no hyphenation artifacts remain
    assert "liv-ing" not in paragraph_text, "Found hyphenation artifact 'liv-ing'"
    assert "liv- ing" not in paragraph_text, "Found hyphenation artifact 'liv- ing'"
    
    print("✓ Wizardly Magic intro contains all expected text")


if __name__ == "__main__":
    test_wizardly_magic_single_paragraph()
    test_wizardly_magic_text_completeness()
    print("\n✅ All Chapter 7 Wizardly Magic paragraph tests passed!")

