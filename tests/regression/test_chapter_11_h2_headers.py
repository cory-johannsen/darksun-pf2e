"""
Regression test for Chapter 11 H2 headers.

Verifies that Magic, Psionics, and Plant-Based Monsters are styled as H2 headers
in the HTML output.
"""

import re
from pathlib import Path

def test_chapter_11_h2_headers():
    """Verify that Magic, Psionics, and Plant-Based Monsters are H2 headers."""
    html_file = Path("data/html_output/chapter-eleven-encounters.html")
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    issues = []
    
    # Check that H2 headers have the h2-header class
    h2_headers = [
        ('header-3-magic', 'Magic:'),
        ('header-4-psionics', 'Psionics:'),
        ('header-5-plant-based-monsters', 'Plant-Based Monsters:'),
    ]
    
    for header_id, header_text in h2_headers:
        # Check for semantic <h2> tag (not styled <p> tag)
        pattern = f'<h2 id="{header_id}">'
        if pattern not in html:
            issues.append(f"❌ Header '{header_text}' (id={header_id}) is not using semantic <h2> tag")
        else:
            print(f"✅ Header '{header_text}' is using semantic <h2> tag")
        
        # Check that H2 headers don't have Roman numerals
        # Pattern: <h2 id="header-3-magic">IV.
        numeral_pattern = f'<h2 id="{header_id}">[IVXLCDM]+\\.'
        if re.search(numeral_pattern, html):
            issues.append(f"❌ Header '{header_text}' still has Roman numerals")
        else:
            print(f"✅ Header '{header_text}' has no Roman numerals")
        
        # Check that back-to-top link is present
        back_to_top_pattern = f'<h2 id="{header_id}">[^<]*<a href="#top"[^>]*>\\[\\^\\]</a></h2>'
        if not re.search(back_to_top_pattern, html, re.DOTALL):
            issues.append(f"❌ Header '{header_text}' is missing back-to-top link")
        else:
            print(f"✅ Header '{header_text}' has back-to-top link")
    
    # Check TOC indentation
    toc_pattern = '<nav id="table-of-contents">'
    if toc_pattern not in html:
        issues.append("❌ Table of contents not found")
    else:
        # Check for toc-subheader class on H2 entries
        for header_id, header_text in h2_headers:
            toc_entry_pattern = f'<li class="toc-subheader"><a href="#{header_id}">'
            if toc_entry_pattern not in html:
                issues.append(f"❌ TOC entry for '{header_text}' is missing toc-subheader class")
            else:
                print(f"✅ TOC entry for '{header_text}' has toc-subheader class")
    
    # Check that header-6 (Monstrous Compendium) is semantic H2 (not H1)
    if '<h2 id="header-6-monstrous-compendium-1-and-2">' in html:
        print(f"✅ Header 'Monstrous Compendium 1 and 2' is using semantic <h2> tag")
    else:
        issues.append(f"❌ Header 'Monstrous Compendium 1 and 2' should be using semantic <h2> tag")
    
    # Check that subsequent H1 headers have correct Roman numerals
    # Note: header-6 is now an H2, so header-7 should have Roman numeral IV (not V)
    h1_renumbering = [
        ('header-7-wilderness-encounters', 'IV'),  # Renumbered from VII because Magic, Psionics, Plant-Based, and Monstrous Compendium are now H2
    ]
    
    for header_id, expected_numeral in h1_renumbering:
        # Pattern: <p id="header-7-...">IV.
        numeral_pattern = f'<p id="{header_id}">{expected_numeral}\\.'
        if not re.search(numeral_pattern, html):
            issues.append(f"❌ Header '{header_id}' should have Roman numeral '{expected_numeral}'")
        else:
            print(f"✅ Header '{header_id}' has correct Roman numeral '{expected_numeral}'")
    
    # Report results
    if issues:
        print("\n" + "=" * 80)
        print("ISSUES FOUND:")
        for issue in issues:
            print(issue)
        print("=" * 80)
        return False
    else:
        print("\n" + "=" * 80)
        print("✅ All Chapter 11 H2 header checks passed!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    import sys
    success = test_chapter_11_h2_headers()
    sys.exit(0 if success else 1)

