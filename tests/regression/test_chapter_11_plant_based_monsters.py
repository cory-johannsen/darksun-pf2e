"""
Regression test for Chapter 11 Plant-Based Monsters paragraph
Tests that the Plant-Based Monsters section renders as a single paragraph.
"""

import re
from pathlib import Path


def test_plant_based_monsters_single_paragraph():
    """
    Verify that Plant-Based Monsters text is rendered as a single paragraph.
    
    The Plant-Based Monsters section should have:
    - A header (H2): "Plant-Based Monsters:"
    - A single paragraph of text describing defiling magic effects
    
    This is a regression test to ensure the text doesn't get split across
    multiple paragraphs again.
    """
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-eleven-encounters.html"
    
    assert html_path.exists(), f"HTML file not found: {html_path}"
    
    content = html_path.read_text()
    
    # Find the Plant-Based Monsters header (it's an H2 tag)
    header_match = re.search(
        r'<h2 id="header-5-plant-based-monsters"[^>]*>.*?</h2>',
        content,
        re.DOTALL
    )
    assert header_match, "Plant-Based Monsters header not found"
    
    # Find content after the header until the next header
    section_match = re.search(
        r'(<h2 id="header-5-plant-based-monsters"[^>]*>.*?</h2>)(.*?)(<h2 id="header-[^"]+"|<p id="header-)',
        content,
        re.DOTALL
    )
    assert section_match, "Could not extract Plant-Based Monsters section"
    
    after_header = section_match.group(2)
    
    # Count paragraph tags
    p_tags = re.findall(r'<p[^>]*>', after_header)
    
    assert len(p_tags) == 1, (
        f"Expected 1 paragraph after Plant-Based Monsters header, found {len(p_tags)}. "
        f"The text should be a single paragraph, not split across multiple paragraphs."
    )
    
    # Verify the paragraph contains the expected text
    paragraph_match = re.search(r'<p>(.*?)</p>', after_header, re.DOTALL)
    assert paragraph_match, "Could not extract paragraph text"
    
    paragraph_text = paragraph_match.group(1)
    
    # Check for key phrases
    assert "Defiling magic" in paragraph_text, "Missing 'Defiling magic' text"
    assert "plant-life" in paragraph_text, "Missing 'plant-life' text"
    assert "plant-based monster" in paragraph_text, "Missing 'plant-based monster' text"
    assert "no save allowed" in paragraph_text, "Missing 'no save allowed' text"
    
    print("✅ Plant-Based Monsters section verified:")
    print(f"   - Header found: ✓")
    print(f"   - Single paragraph: ✓")
    print(f"   - Expected content present: ✓")


if __name__ == "__main__":
    test_plant_based_monsters_single_paragraph()
    print("\n✅ All checks passed!")

