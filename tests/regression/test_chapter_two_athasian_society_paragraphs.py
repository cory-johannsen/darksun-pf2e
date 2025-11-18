"""
Regression test for Chapter Two: Athasian Society paragraph breaks.

This test verifies that the intro, Barrenness, and Metal sections have proper
paragraph breaks as specified by the user.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_intro_paragraph_breaks():
    """Test that intro section has proper paragraph breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Check for paragraph breaks
    intro_breaks = [
        "On Athas, there are",
        "Surprisingly, all of these",
    ]
    
    failures = []
    for break_text in intro_breaks:
        # Check if the break text starts a paragraph
        if f"<p>{break_text}" not in content:
            failures.append(f"Missing paragraph break before: '{break_text}'")
    
    if failures:
        print("❌ FAIL: Intro section paragraph breaks")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ PASS: Intro section paragraph breaks are correct")
    return True


def test_barrenness_paragraph_breaks():
    """Test that Barrenness section has 5 paragraphs with proper breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Check for paragraph breaks
    barrenness_breaks = [
        "Hunting tribes",
        "The lives of",
        "City dwellers",
        "Given the importance",
    ]
    
    failures = []
    for break_text in barrenness_breaks:
        # Check if the break text starts a paragraph
        if f"<p>{break_text}" not in content:
            failures.append(f"Missing paragraph break before: '{break_text}'")
    
    if failures:
        print("❌ FAIL: Barrenness section paragraph breaks")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ PASS: Barrenness section has 5 paragraphs with correct breaks")
    return True


def test_metal_paragraph_breaks():
    """Test that Metal section has 10 paragraphs with proper breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Check for paragraph breaks
    metal_breaks = [
        "Unfortunately, metals",
        "The scarcity of metal",
        "The scarcity of resources",
        "In war, the advantages",
        "Who can doubt that",
        "As I have stated earlier",
        "Still, lucky treasure",
        "I have heard tales that suits",
        "There are even rumors",
    ]
    
    failures = []
    for break_text in metal_breaks:
        # Check if the break text starts a paragraph
        if f"<p>{break_text}" not in content:
            failures.append(f"Missing paragraph break before: '{break_text}'")
    
    if failures:
        print("❌ FAIL: Metal section paragraph breaks")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ PASS: Metal section has 10 paragraphs with correct breaks")
    return True


def test_psionics_paragraph_breaks():
    """Test that Psionics section has 5 paragraphs with proper breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Check for paragraph breaks
    psionics_breaks = [
        "Each culture",
        "Psionic powers",
        "Considering the potential",
        "Psionics has often",
    ]
    
    failures = []
    for break_text in psionics_breaks:
        # Check if the break text starts a paragraph
        if f"<p>{break_text}" not in content:
            failures.append(f"Missing paragraph break before: '{break_text}'")
    
    if failures:
        print("❌ FAIL: Psionics section paragraph breaks")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ PASS: Psionics section has 5 paragraphs with correct breaks")
    return True


def test_elven_merchants_paragraph_breaks():
    """Test that Elven Merchants section (header-49) has 15 paragraphs with proper breaks."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Check for paragraph breaks in the Elven Merchants section (header-49)
    elven_merchants_breaks = [
        "Instead, the tribe",
        "Most tribes",
        "In most cities",
        "Although elves sell",
        "Despite the elves",  # Note: may have apostrophe variants
        "Most templars will not",
        "Usually, a tribe stays",
        "By the time the tribe",
        "Outside the city",
        "In most cultures",
        "I was once with an",
        "These affairs continued",
        "Lest anyone make",
        "Elven caravans are",
    ]
    
    failures = []
    for break_text in elven_merchants_breaks:
        # Check if the break text starts a paragraph
        if f"<p>{break_text}" not in content:
            failures.append(f"Missing paragraph break before: '{break_text}'")
    
    if failures:
        print("❌ FAIL: Elven Merchants section paragraph breaks")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print("✅ PASS: Elven Merchants section has 15 paragraphs with correct breaks")
    return True


def test_h2_headers():
    """Test that specified headers have h2-header CSS class."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Headers that should have h2-header class
    h2_headers = [
        "Life Energy and Magic",
        "The Veiled Alliance",  # First occurrence
        "The Worst Scourge",
        "The Sorcerer Kings",
        "The Templars",
        "The Nobility",
        "The Freemen",
        "Merchants",
        "Elven Merchants",
        "Slaves",
        "Wizards",
        # Race in the Cities subsections
        "Humans",
        "Dwarves",
        "Elves",
        "Half-elves",
        "Half-giants",
        "Muls",
        "Thri-kreen",
        "Halflings",
        # Villages subsections
        "Client Villages",
        "Slave Villages",
        "Dwarven Villages",
        "Halfling Villages",
        # Dynastic Merchant Houses subsections
        "Headquarters",
        "Emporiums",
        "Outposts",
        "Caravans",
        "Employment Terms",
        "The Merchant Code",
    ]
    
    failures = []
    for header in h2_headers:
        # Check if the header appears with h2-header class
        # Pattern: <p class="h2-header" id="...">...SPAN with header text...</p>
        if f'class="h2-header"' not in content or f'<span style="color: #cd490a">{header}</span>' not in content:
            # Check more specifically
            import re
            pattern = rf'<p class="h2-header"[^>]*>.*?<span style="color: #cd490a">{re.escape(header)}</span>'
            if not re.search(pattern, content, re.DOTALL):
                failures.append(f"'{header}' does not have h2-header class")
    
    if failures:
        print("❌ FAIL: H2 header classes")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print(f"✅ PASS: All {len(h2_headers)} specified headers have h2-header class")
    return True


def test_h3_headers():
    """Test that specified headers have h3-header CSS class."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Headers that should have h3-header class
    h3_headers = [
        "Gladiators",
        "Artists",
        "Soldier Slaves",
        "Laborers",
        "Farmers",
        "Defilers",
        # Second "The Veiled Alliance" should also have h3-header class
    ]
    
    failures = []
    import re
    for header in h3_headers:
        # Check if the header appears with h3-header class
        pattern = rf'<p class="h3-header"[^>]*>.*?<span style="color: #cd490a">{re.escape(header)}</span>'
        if not re.search(pattern, content, re.DOTALL):
            failures.append(f"'{header}' does not have h3-header class")
    
    # Check that there's a second "The Veiled Alliance" with h3-header class
    veiled_h3_pattern = r'<p class="h3-header"[^>]*>.*?<span style="color: #cd490a">The Veiled Alliance</span>'
    veiled_h3_count = len(re.findall(veiled_h3_pattern, content, re.DOTALL))
    if veiled_h3_count < 1:
        failures.append("Second 'The Veiled Alliance' does not have h3-header class")
    
    if failures:
        print("❌ FAIL: H3 header classes")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print(f"✅ PASS: All {len(h3_headers)} specified headers have h3-header class")
    return True


def test_no_roman_numerals_on_subheaders():
    """Test that H2 and H3 headers do NOT have Roman numerals."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # All headers that should NOT have Roman numerals (H2 and H3)
    subheaders = [
        "Life Energy and Magic",
        "The Worst Scourge",
        "The Sorcerer Kings",
        "The Templars",
        "The Nobility",
        "The Freemen",
        "Merchants",
        "Elven Merchants",
        "Slaves",
        "Wizards",
        # Race in the Cities subsections (H2)
        "Humans",
        "Dwarves",
        "Elves",
        "Half-elves",
        "Half-giants",
        "Muls",
        "Thri-kreen",
        "Halflings",
        # Villages subsections (H2)
        "Client Villages",
        "Slave Villages",
        "Dwarven Villages",
        "Halfling Villages",
        # Dynastic Merchant Houses subsections (H2)
        "Headquarters",
        "Emporiums",
        "Outposts",
        "Caravans",
        "Employment Terms",
        "The Merchant Code",
        # H3 headers
        "Gladiators",
        "Artists",
        "Soldier Slaves",
        "Laborers",
        "Farmers",
        "Defilers",
    ]
    
    failures = []
    import re
    for header in subheaders:
        # Check if Roman numeral appears before the header
        # Pattern: Roman numeral followed by period and back-to-top link before the header
        pattern = rf'[IVX]+\.\s+<a[^>]+>\[\^\]</a>\s+<span[^>]*>{re.escape(header)}</span>'
        if re.search(pattern, content):
            failures.append(f"'{header}' incorrectly has a Roman numeral")
    
    # Check both "The Veiled Alliance" instances
    veiled_with_roman = re.findall(r'[IVX]+\.\s+<a[^>]+>\[\^\]</a>\s+<span[^>]*>The Veiled Alliance</span>', content)
    if veiled_with_roman:
        failures.append(f"Found {len(veiled_with_roman)} 'The Veiled Alliance' headers with Roman numerals (should be 0)")
    
    if failures:
        print("❌ FAIL: Subheaders should not have Roman numerals")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print(f"✅ PASS: All {len(subheaders)} subheaders correctly have no Roman numerals")
    return True


def test_toc_structure():
    """Test that TOC correctly identifies H2 and H3 headers with proper indentation."""
    html_file = project_root / "data" / "html_output" / "chapter-two-athasian-society.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found at {html_file}")
        return False
    
    content = html_file.read_text(encoding="utf-8")
    
    # Extract the TOC section
    import re
    toc_match = re.search(r'<nav id="table-of-contents">.*?</nav>', content, re.DOTALL)
    if not toc_match:
        print("❌ FAIL: Table of contents not found")
        return False
    
    toc = toc_match.group(0)
    
    # H2 headers should have class="toc-subheader"
    h2_in_toc = [
        "Life Energy and Magic",
        "The Veiled Alliance",  # First occurrence
        "The Worst Scourge",
        "The Sorcerer Kings",
        "The Templars",
        "The Nobility",
        "The Freemen",
        "Merchants",
        "Elven Merchants",
        "Slaves",
        "Wizards",
        # Race in the Cities subsections
        "Humans",
        "Dwarves",
        "Elves",
        "Half-elves",
        "Half-giants",
        "Muls",
        "Thri-kreen",
        "Halflings",
        # Villages subsections
        "Client Villages",
        "Slave Villages",
        "Dwarven Villages",
        "Halfling Villages",
        # Dynastic Merchant Houses subsections
        "Headquarters",
        "Emporiums",
        "Outposts",
        "Caravans",
        "Employment Terms",
        "The Merchant Code",
    ]
    
    # H3 headers should have class="toc-subsubheader"
    h3_in_toc = [
        "Gladiators",
        "Artists",
        "Soldier Slaves",
        "Laborers",
        "Farmers",
        "Defilers",
        # Employment Terms subsections
        "Family members",
        "Senior agents",
        "Regular agents",
        "Hirelings",
    ]
    
    failures = []
    
    for header in h2_in_toc:
        # Check for TOC subheader class
        pattern = rf'<li class="toc-subheader">.*?{re.escape(header)}.*?</li>'
        if not re.search(pattern, toc, re.DOTALL):
            failures.append(f"'{header}' not found in TOC with toc-subheader class")
    
    for header in h3_in_toc:
        # Check for TOC subsubheader class
        pattern = rf'<li class="toc-subsubheader">.*?{re.escape(header)}.*?</li>'
        if not re.search(pattern, toc, re.DOTALL):
            failures.append(f"'{header}' not found in TOC with toc-subsubheader class")
    
    if failures:
        print("❌ FAIL: TOC structure incorrect")
        for failure in failures:
            print(f"  - {failure}")
        return False
    
    print(f"✅ PASS: TOC correctly shows {len(h2_in_toc)} H2 and {len(h3_in_toc)} H3 headers with proper indentation")
    return True


def main():
    """Run all tests."""
    print("=" * 80)
    print("Chapter Two: Athasian Society Tests")
    print("=" * 80)
    
    tests = [
        test_intro_paragraph_breaks,
        test_barrenness_paragraph_breaks,
        test_metal_paragraph_breaks,
        test_psionics_paragraph_breaks,
        test_elven_merchants_paragraph_breaks,
        test_h2_headers,
        test_h3_headers,
        test_no_roman_numerals_on_subheaders,
        test_toc_structure,
    ]
    
    results = []
    for test in tests:
        print()
        results.append(test())
    
    print()
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

