"""
Test paragraph breaks in Chapter Five: Monsters of Athas introductory text.

This test verifies that the introductory paragraph is properly split into 
3 distinct paragraphs as specified by the user.
"""

import re
from pathlib import Path


def test_chapter_five_monsters_intro_paragraph_breaks():
    """
    Test that Chapter Five: Monsters of Athas has proper paragraph breaks.
    
    The intro should be split into 3 paragraphs:
    1. "Life is a mysterious... sun-baked clay."
    2. "To survive... pages that follow."
    3. "Over the course... is often deadly on Athas."
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    html_content = html_file.read_text(encoding="utf-8")
    
    # Find the intro section (after the TOC, before the first header)
    # Look for content between the TOC closing and the first H2 header
    content_match = re.search(
        r'</nav>.*?<section class="content">\s*(.*?)<h2[^>]*id="header',
        html_content,
        re.DOTALL
    )
    
    assert content_match, "Could not find intro content section"
    intro_section = content_match.group(1)
    
    # Count paragraphs in the intro section
    # Look for <p> tags (but not those with ids, which are headers)
    paragraphs = re.findall(r'<p>([^<]*(?:<[^/][^>]*>[^<]*</[^>]*>)*[^<]*)</p>', intro_section)
    
    # Filter out empty paragraphs and those that are just whitespace
    paragraphs = [p.strip() for p in paragraphs if p.strip() and not p.strip().startswith('<a id="top">')]
    
    # There should be exactly 3 paragraphs in the intro
    assert len(paragraphs) >= 3, (
        f"Expected at least 3 paragraphs in intro, found {len(paragraphs)}. "
        f"Paragraphs: {[p[:50] + '...' for p in paragraphs]}"
    )
    
    # Verify the content of each paragraph
    para1_found = False
    para2_found = False
    para3_found = False
    
    for para in paragraphs:
        # Remove HTML tags for text matching
        text = re.sub(r'<[^>]+>', '', para)
        text = text.replace('&#x27;', "'").replace('&quot;', '"')
        
        if 'Life is a mysterious' in text and 'sun-baked clay' in text:
            para1_found = True
            # First paragraph should NOT contain "To survive"
            assert 'To survive' not in text, (
                "First paragraph incorrectly contains 'To survive'"
            )
        
        if 'To survive' in text and 'pages that follow' in text:
            para2_found = True
            # Second paragraph should NOT contain "Over the course"
            assert 'Over the course' not in text, (
                "Second paragraph incorrectly contains 'Over the course'"
            )
        
        if 'Over the course' in text and 'is often deadly on Athas' in text:
            para3_found = True
    
    # All three paragraphs must be present and separated
    assert para1_found, "First paragraph ('Life is a mysterious...') not found"
    assert para2_found, "Second paragraph ('To survive...') not found"
    assert para3_found, "Third paragraph ('Over the course...') not found"


def test_chapter_five_monsters_intro_not_merged():
    """
    Test that the intro paragraphs are NOT merged into a single paragraph.
    
    This is a regression test to ensure the breaks at "To survive" and
    "Over the course" are maintained.
    """
    html_file = Path("data/html_output/chapter-five-monsters-of-athas.html")
    
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    html_content = html_file.read_text(encoding="utf-8")
    
    # Check that "Life is a mysterious" and "To survive" are NOT in the same <p></p> pair
    # Use a pattern that doesn't match across paragraph tags
    para1_bad = re.search(
        r'<p>(?:(?!</p>).)*Life is a mysterious(?:(?!</p>).)*To survive(?:(?!</p>).)*</p>',
        html_content,
        re.DOTALL
    )
    
    assert not para1_bad, (
        "ERROR: 'Life is a mysterious' and 'To survive' are in the same paragraph. "
        "They should be in separate paragraphs."
    )
    
    # Check that "To survive" and "Over the course" are NOT in the same <p></p> pair
    para2_bad = re.search(
        r'<p>(?:(?!</p>).)*To survive(?:(?!</p>).)*Over the course(?:(?!</p>).)*</p>',
        html_content,
        re.DOTALL
    )
    
    assert not para2_bad, (
        "ERROR: 'To survive' and 'Over the course' are in the same paragraph. "
        "They should be in separate paragraphs."
    )


if __name__ == "__main__":
    # Run tests
    test_chapter_five_monsters_intro_paragraph_breaks()
    test_chapter_five_monsters_intro_not_merged()
    print("✅ All Chapter Five: Monsters of Athas paragraph tests passed!")

