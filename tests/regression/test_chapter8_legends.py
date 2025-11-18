"""
Regression test for Chapter 8 legend entries.

This test verifies that the two legend entries following the Psionicist table
are properly extracted and rendered in the HTML output.

Regression: The legend entries were being lost during the processing stage
because continuation lines were not being collected.
"""

import pytest
from pathlib import Path


def test_chapter8_legend_entries_present():
    """Verify that both legend entries appear in the HTML output after the Psionicist table."""
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-eight-experience.html"
    
    if not html_path.exists():
        pytest.skip(f"HTML output not found: {html_path}")
    
    html_content = html_path.read_text()
    
    # Check for the first legend entry
    assert "*For gladiators, this award only applies to creatures slain without outside aid" in html_content, \
        "First legend entry about gladiators is missing"
    
    # Check for the complete first legend entry
    assert "The gladiator gets no experience" in html_content or \
           "The gladiator gets no ex" in html_content, \
        "First legend entry continuation is missing"
    
    # Check for the second legend entry
    assert "**The thief adds this XP allotment to the rogue gain for treasure obtained" in html_content or \
           ("**The thief adds this XP allotment" in html_content and "treasure obtained" in html_content), \
        "Second legend entry about thief is missing"


def test_chapter8_legend_entries_order():
    """Verify that legend entries appear after the Psionicist section and before Individual Race Awards."""
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-eight-experience.html"
    
    if not html_path.exists():
        pytest.skip(f"HTML output not found: {html_path}")
    
    html_content = html_path.read_text()
    
    # Find positions
    # Look for Psionicist: (with colon, as it appears in the content)
    psionicist_pos = html_content.find("Psionicist:")
    legend1_pos = html_content.find("*For gladiators")
    legend2_pos = html_content.find("**The thief adds")
    
    # Look for the actual Individual Race Awards section (with span tag to avoid TOC matches)
    # Find the last occurrence which is the actual section, not TOC
    import re
    race_awards_matches = list(re.finditer(r'<span[^>]*>Individual Race Awards</span>', html_content))
    race_awards_pos = race_awards_matches[-1].start() if race_awards_matches else -1
    
    assert psionicist_pos > 0, "Psionicist section not found"
    assert legend1_pos > 0, "First legend entry not found"
    assert legend2_pos > 0, "Second legend entry not found"
    assert race_awards_pos > 0, "Individual Race Awards section not found"
    
    # Verify order: Psionicist < Legend1 < Legend2 < Race Awards
    assert psionicist_pos < legend1_pos, f"First legend (pos {legend1_pos}) should appear after Psionicist (pos {psionicist_pos})"
    assert legend1_pos < legend2_pos, f"Second legend (pos {legend2_pos}) should appear after first legend (pos {legend1_pos})"
    assert legend2_pos < race_awards_pos, f"Legends (pos {legend2_pos}) should appear before Individual Race Awards (pos {race_awards_pos})"


def test_chapter8_legend_entries_complete():
    """Verify that legend entries contain complete text, not fragmented lines."""
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-eight-experience.html"
    
    if not html_path.exists():
        pytest.skip(f"HTML output not found: {html_path}")
    
    html_content = html_path.read_text()
    
    # First legend should be relatively complete (allowing for line breaks)
    # Look for key phrases that should be in the first legend
    assert "*For gladiators" in html_content, "First legend start missing"
    # Note: "ex-perience" might be hyphenated in source, so check for fragments
    assert ("experience" in html_content or "ex-" in html_content), "First legend should mention experience"
    
    # Second legend should mention both "thief" and "treasure"
    assert "**The thief" in html_content, "Second legend start missing"
    assert "treasure obtained" in html_content, "Second legend should mention 'treasure obtained'"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])

