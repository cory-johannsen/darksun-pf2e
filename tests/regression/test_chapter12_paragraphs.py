"""
Test Chapter 12 paragraph breaks in Spellcasters as NPCs section.

This test verifies that the "Spellcasters as NPCs" section has proper
paragraph breaks at the specified locations.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


def test_spellcasters_as_npcs_paragraph_breaks():
    """Test that Spellcasters as NPCs section has 5 paragraphs with correct breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-twelve-npcs.html"
    
    assert html_file.exists(), f"Chapter 12 HTML not found at {html_file}"
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the Spellcasters as NPCs header (it's an H2 tag)
    header = soup.find('h2', id='header-0-spellcasters-as-npcs')
    assert header is not None, "Could not find 'Spellcasters as NPCs' header"
    
    # Get all paragraphs between this header and the next header
    paragraphs = []
    current = header.find_next_sibling()
    while current:
        # Stop at the next H2 header
        if current.name == 'h2' and current.get('id', '').startswith('header-'):
            break
        # Collect regular paragraphs
        if current.name == 'p' and not current.get('id', '').startswith('header-'):
            paragraphs.append(current.get_text())
        current = current.find_next_sibling()
    
    # Should have exactly 5 paragraphs
    assert len(paragraphs) == 5, f"Expected 5 paragraphs, found {len(paragraphs)}"
    
    # Verify content of each paragraph (allow for unicode variations)
    assert "Priests" in paragraphs[0] and "DARK SUN" in paragraphs[0], \
        f"First paragraph should contain 'Priests' and 'DARK SUN', got: {paragraphs[0][:100]}"
    
    assert paragraphs[1].startswith("Druid NPCs"), \
        f"Second paragraph should start with 'Druid NPCs', got: {paragraphs[1][:100]}"
    
    assert paragraphs[2].startswith("Wizard NPCs"), \
        f"Third paragraph should start with 'Wizard NPCs', got: {paragraphs[2][:100]}"
    
    assert paragraphs[3].startswith("Rare instances"), \
        f"Fourth paragraph should start with 'Rare instances', got: {paragraphs[3][:100]}"
    
    assert paragraphs[4].startswith("One notable"), \
        f"Fifth paragraph should start with 'One notable', got: {paragraphs[4][:100]}"
    
    print("✅ All paragraph breaks verified in Spellcasters as NPCs section")
    return True


if __name__ == "__main__":
    try:
        test_spellcasters_as_npcs_paragraph_breaks()
        print("\n🎉 Chapter 12 paragraph breaks test PASSED")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test ERROR: {e}")
        sys.exit(1)

