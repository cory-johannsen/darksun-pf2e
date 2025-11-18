"""
Regression test for Chapter 3 italics formatting.

This test ensures that italicized text (book titles, emphasized words) are properly
rendered with <i> or <em> tags in the HTML output.

Background:
- The source PDF uses font "MSTT31c576" for italicized text
- Recent refactors caused the is_italic() function to not recognize this font
- This resulted in italics being lost and words being incorrectly merged
"""

import re
from pathlib import Path


def test_chapter3_book_titles_are_italicized():
    """Verify that book titles are properly italicized in Chapter 3."""
    html_path = Path("data/html_output/chapter-three-player-character-classes.html")
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # Test that book titles are italicized
    # These should appear as <i>Title</i> or <em>Title</em>
    book_titles = [
        "The Complete Psionics Handbook",
        "Players Handbook",
        "Player's Handbook",
    ]
    
    for title in book_titles:
        # Check for italic tags around the title
        # Allow for variations like "the Players Handbook" or "Players Handbook"
        pattern_i = rf'<i>[^<]*{re.escape(title)}[^<]*</i>'
        pattern_em = rf'<em>[^<]*{re.escape(title)}[^<]*</em>'
        
        assert re.search(pattern_i, html_content, re.IGNORECASE) or \
               re.search(pattern_em, html_content, re.IGNORECASE), \
               f"Book title '{title}' should be italicized in Chapter 3"


def test_chapter3_no_word_merging_from_lost_italics():
    """Verify that words aren't incorrectly merged due to lost italic formatting."""
    html_path = Path("data/html_output/chapter-three-player-character-classes.html")
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # These are examples of words that would be merged if italics are lost
    # When "The" (italic) is followed by "Complete" (italic), they should not merge to "TheComplete"
    incorrect_merges = [
        "TheComplete",  # Should be "The Complete"
        "PlayersHandbook",  # Should be "Players Handbook" or within italic tags
        "DarkSun",  # Should be "Dark Sun" (if the title appears)
    ]
    
    for merged_word in incorrect_merges:
        assert merged_word not in html_content, \
               f"Found incorrectly merged word '{merged_word}' - likely due to lost italic formatting"


def test_chapter3_intro_paragraph_italic_formatting():
    """Verify that the intro paragraph has proper italic formatting for book titles."""
    html_path = Path("data/html_output/chapter-three-player-character-classes.html")
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # The intro paragraph mentions "The Complete Psionics Handbook"
    # This should be italicized
    intro_section = html_content[html_content.find("<section"):html_content.find("</section>")]
    
    # Look for the phrase "as described in" which precedes the book title
    if "as described in" in intro_section:
        # Find the next book title reference
        match = re.search(
            r'as described in\s*(<i>|<em>)?(The )?Complete Psionics Handbook(</i>|</em>)?',
            intro_section,
            re.IGNORECASE
        )
        assert match, "Book title 'The Complete Psionics Handbook' should appear after 'as described in'"
        
        # Verify italic tags are present
        assert match.group(1) or match.group(3), \
               "Book title 'The Complete Psionics Handbook' should be wrapped in italic tags"


def test_chapter3_fighters_section_handbook_references():
    """Verify Player's Handbook references in fighter section are italicized."""
    html_path = Path("data/html_output/chapter-three-player-character-classes.html")
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # Find the Fighter section
    fighter_match = re.search(
        r'<h2[^>]*>.*?Fighter.*?</h2>(.*?)<h2',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    
    assert fighter_match, "Fighter section not found"
    fighter_section = fighter_match.group(1)
    
    # Count Player's Handbook references
    handbook_refs = re.findall(
        r'Player[\'s]*\s*Handbook',
        fighter_section,
        re.IGNORECASE
    )
    
    # Count italicized handbook references
    italic_refs = re.findall(
        r'<(?:i|em)>[^<]*Player[\'s]*\s*Handbook[^<]*</(?:i|em)>',
        fighter_section,
        re.IGNORECASE
    )
    
    # Most or all handbook references should be italicized
    assert len(italic_refs) > 0, \
           f"Found {len(handbook_refs)} Player's Handbook references in Fighter section, " \
           f"but only {len(italic_refs)} are italicized"
    
    # At least 70% should be italicized (allowing for some edge cases)
    if len(handbook_refs) > 0:
        ratio = len(italic_refs) / len(handbook_refs)
        assert ratio >= 0.7, \
               f"Only {ratio*100:.0f}% of Player's Handbook references are italicized " \
               f"({len(italic_refs)}/{len(handbook_refs)}). Expected at least 70%."


def test_chapter3_common_italic_book_patterns():
    """Test that common book reference patterns are properly italicized throughout Chapter 3."""
    html_path = Path("data/html_output/chapter-three-player-character-classes.html")
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # Common patterns that should be italicized in RPG books
    italic_patterns = [
        r'The Complete [A-Z]\w+ Handbook',
        r'Players? Handbook',
        r'Dungeon Master[\'s]* Guide',
    ]
    
    for pattern in italic_patterns:
        # Find all matches
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if not matches:
            continue  # Pattern not present, skip
        
        # Find italicized matches
        italic_pattern = rf'<(?:i|em)>[^<]*{pattern}[^<]*</(?:i|em)>'
        italic_matches = re.findall(italic_pattern, html_content, re.IGNORECASE)
        
        # At least some should be italicized
        assert len(italic_matches) > 0, \
               f"Found {len(matches)} instances matching pattern '{pattern}' " \
               f"but none are italicized"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])

