"""
Regression test for Chapter 11 header merging

Tests that "Wizard, Priest, and Psionicist" and "Encounters" are merged into
a single header in the Chapter 11 HTML output.

This is a regression test to prevent the headers from being split again in the future.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_chapter_11_header_merge():
    """
    Test that the Chapter 11 HTML output contains a single merged header
    for "Wizard, Priest, and Psionicist Encounters" instead of two separate headers.
    """
    html_file = project_root / "data" / "html_output" / "chapter-eleven-encounters.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML output file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Check that the merged header appears
    if "Wizard, Priest, and Psionicist Encounters" in html_content:
        print("✅ PASS: Found merged header 'Wizard, Priest, and Psionicist Encounters'")
    else:
        print("❌ FAIL: Could not find merged header 'Wizard, Priest, and Psionicist Encounters'")
        return False
    
    # Check that the split headers do NOT appear consecutively
    # (they might appear separately in the TOC or elsewhere, but not as consecutive headers)
    lines = html_content.split('\n')
    
    for i in range(len(lines) - 1):
        line = lines[i].strip()
        next_line = lines[i + 1].strip()
        
        # Look for the pattern where "Wizard, Priest, and Psionicist" is in a header
        # followed by "Encounters" in the next header
        if ('id="header-0-wizard-priest-and-psionicist"' in line and 
            'Wizard, Priest, and Psionicist</span></p>' in line and
            'Encounters' not in line):
            # Found the old pattern - this is bad
            if 'id="header-1-encounters"' in next_line:
                print("❌ FAIL: Found split headers - 'Wizard, Priest, and Psionicist' "
                      "followed by 'Encounters' as separate headers")
                print(f"  Line {i}: {line}")
                print(f"  Line {i+1}: {next_line}")
                return False
    
    # Additional check: Look at the TOC to see if it has the correct entry
    if 'href="#header-0-wizard-priest-and-psionicist-encounters">Wizard, Priest, and Psionicist Encounters</a>' in html_content:
        print("✅ PASS: TOC contains correct merged header link")
    else:
        # Try to find what the TOC actually contains
        import re
        toc_pattern = r'href="#header-0-[^"]*">([^<]+)</a>'
        match = re.search(toc_pattern, html_content)
        if match:
            print(f"⚠️  WARNING: TOC first header is '{match.group(1)}' "
                  f"(expected 'Wizard, Priest, and Psionicist Encounters')")
        else:
            print("⚠️  WARNING: Could not find TOC first header")
    
    # Check that there's only ONE header before "Encounters in City-States"
    # (The merged header should be the first, followed by "Encounters in City-States" as the second)
    import re
    header_pattern = r'<p id="header-(\d+)-[^"]*">.*?<span[^>]*>(.*?)</span>'
    headers = re.findall(header_pattern, html_content, re.DOTALL)
    
    if headers:
        print(f"\n📊 Found {len(headers)} headers in total")
        print("First 5 headers:")
        for idx, (header_num, header_text) in enumerate(headers[:5]):
            # Clean up the header text
            header_text = header_text.strip().replace('\n', ' ').replace('  ', ' ')
            print(f"  {header_num}: {header_text[:60]}")
        
        # Check the first header
        if headers[0][1].strip().startswith("Wizard, Priest, and Psionicist Encounters"):
            print("\n✅ PASS: First header is the merged 'Wizard, Priest, and Psionicist Encounters'")
        else:
            print(f"\n❌ FAIL: First header is not the merged header, got: '{headers[0][1].strip()[:60]}'")
            return False
    
    print("\n🎉 All checks passed!")
    return True


if __name__ == "__main__":
    success = test_chapter_11_header_merge()
    sys.exit(0 if success else 1)

