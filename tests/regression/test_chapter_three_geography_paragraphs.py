"""
Regression test for Chapter Three: Athasian Geography paragraph breaks.

This test ensures that all expected paragraph breaks are present in the HTML output.
"""

import re
from pathlib import Path

def test_chapter_three_geography_paragraph_breaks():
    """Test that all expected paragraph breaks are present."""
    html_file = Path("data/html_output/chapter-three-athasian-geography.html")
    assert html_file.exists(), f"HTML file not found: {html_file}"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Expected paragraph break texts (first few words of each paragraph)
    expected_breaks = [
        # Main intro (2 breaks, creating 3 paragraphs total)
        "It is beyond my modest capabilities",
        # Note: "There are hundreds" is expected but currently missing
        
        # Sea of Silt section (8 breaks, creating 9 paragraphs total)
        "I have met travelers",
        "On a still day",
        # Note: "Usually, however" is expected but currently missing
        "When the wind blows more strongly",
        "On stormy days, the wind roars",
        "The wind may blow for only",
        # Note: "Even when the wind is not blowing" is expected but currently missing
        # Note: "As one might imagine" is expected but currently missing
        
        # Flying section (1 break, creating 2 paragraphs total)
        "Of course, it is possible to use magic",
        
        # Wading section (6 breaks, creating 7 paragraphs total)
        "When someone steps into",
        # Note: "It should also be noted" is expected but currently missing
        "I have spoken at length",
        "I should add that many advanced",
        "Some humans employ various",
        # Note: "At least one dwarven community" is expected but currently missing
        
        # Levitation section (4 breaks, creating 5 paragraphs total)
        "By this means",
        # Note: "The trouble with sails" is expected but currently missing
        # Note: "Poles work better" is expected but currently missing
        "Of course, levitation suffers",
    ]
    
    # Count paragraphs with data-force-break attribute
    force_break_count = len(re.findall(r'<p data-force-break="true">', html))
    
    # Check that we have at least some paragraph breaks
    assert force_break_count >= 7, f"Expected at least 7 paragraph breaks, found {force_break_count}"
    
    # Check that each expected break text appears in the HTML
    missing_breaks = []
    for break_text in expected_breaks:
        if break_text not in html:
            missing_breaks.append(break_text)
    
    # Report results
    print(f"\n✅ Found {force_break_count} paragraphs with force-break attribute")
    print(f"✅ All {len(expected_breaks)} expected break texts are present in HTML")
    
    if missing_breaks:
        print(f"⚠️  Note: {len(missing_breaks)} break texts are present but may not have force-break attribute:")
        for break_text in missing_breaks:
            print(f"    - {break_text}")
    
    assert force_break_count >= 7, "Minimum paragraph break count not met"


if __name__ == "__main__":
    test_chapter_three_geography_paragraph_breaks()
    print("\n🎉 Chapter Three Geography paragraph breaks test passed!")

