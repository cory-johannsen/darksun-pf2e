#!/usr/bin/env python3
"""
Regression test for Raiding Tribes section paragraph breaks and tribe headers.

Ensures:
1. Raiding Tribes section has 4 paragraphs with proper breaks
2. Tribe headers (Slave, Giant, Thri-kreen, Halfling, Elf) are H2
"""

import sys
import os
import re

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


def test_raiding_tribes_paragraphs():
    """
    Test that the Raiding Tribes section has exactly 4 paragraphs
    with breaks at the specified locations.
    """
    html_file = os.path.join(project_root, 'data', 'html_output', 'chapter-two-athasian-society.html')
    
    if not os.path.exists(html_file):
        print(f"❌ ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract the Raiding Tribes section
    # Find from header-52-raiding-tribes to header-53-slave-tribes
    pattern = r'<p id="header-52-raiding-tribes">.*?(?=<p [^>]*id="header-53-slave-tribes">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        print("❌ ERROR: Could not find Raiding Tribes section")
        return False
    
    section = match.group(0)
    
    # Count paragraphs (excluding the header paragraph)
    section_without_header = re.sub(r'<p id="header-52-raiding-tribes">.*?</p>', '', section, count=1)
    
    # Count <p> tags
    paragraphs = re.findall(r'<p>.*?</p>', section_without_header, re.DOTALL)
    paragraph_count = len(paragraphs)
    
    print(f"📊 Found {paragraph_count} paragraphs in Raiding Tribes section")
    
    # Expected paragraph breaks
    expected_breaks = [
        "Although raiders",
        "Most raiders",
        "Usually, the raiding",  # Note: may have period after "Usually" in source
    ]
    
    # Expected: 4 paragraphs total (1 intro + 3 breaks = 4 paragraphs)
    expected_count = 4
    
    if paragraph_count != expected_count:
        print(f"❌ FAILED: Expected {expected_count} paragraphs, found {paragraph_count}")
        return False
    
    # Verify each expected break exists at the start of a paragraph
    failures = []
    for break_text in expected_breaks:
        # Check if this text starts a paragraph
        break_pattern = rf'<p>{re.escape(break_text)}'
        if not re.search(break_pattern, section):
            failures.append(break_text)
            print(f"❌ Missing paragraph break at: '{break_text}'")
    
    if failures:
        print(f"❌ FAILED: {len(failures)} expected paragraph breaks not found")
        return False
    
    print("✅ PASSED: Raiding Tribes section has correct paragraph structure")
    print(f"   - {paragraph_count} paragraphs")
    print(f"   - All {len(expected_breaks)} expected breaks present")
    return True


def test_tribe_headers_are_h2():
    """
    Test that specific tribe headers are marked as H2 and have no Roman numerals.
    """
    html_file = os.path.join(project_root, 'data', 'html_output', 'chapter-two-athasian-society.html')
    
    if not os.path.exists(html_file):
        print(f"❌ ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Headers that should be H2 (only the ones that actually exist in this chapter)
    h2_headers = [
        ("header-53-slave-tribes", "Slave Tribes"),
        ("header-54-giant-tribes", "Giant Tribes"),
        ("header-56-halfling-tribes", "Halfling Tribes"),
    ]
    
    failures = []
    
    for header_id, header_text in h2_headers:
        # Check if header has h2-header class
        # Pattern: <p class="h2-header" id="header-ID"><a href="#top"...>[^]</a> <span...>Header Text</span></p>
        pattern = rf'<p class="h2-header" id="{header_id}"><a[^>]*>\[\^\]</a>\s*<span[^>]*>{re.escape(header_text)}</span></p>'
        
        if not re.search(pattern, html, re.DOTALL):
            failures.append(header_text)
            print(f"❌ Header '{header_text}' is not marked as H2 with correct format")
            
            # Check if header exists at all
            if header_id in html:
                print(f"   Header ID '{header_id}' exists but format is wrong")
                # Show what format it has
                header_match = re.search(rf'<p[^>]*id="{header_id}"[^>]*>([^<]*)', html)
                if header_match:
                    print(f"   Current format: {header_match.group(0)[:100]}")
            else:
                print(f"   Header ID '{header_id}' not found in HTML")
        
        # Also check that it doesn't have Roman numerals
        roman_pattern = rf'<p[^>]*id="{header_id}"[^>]*>[IVXLCDM]+\.'
        if re.search(roman_pattern, html):
            failures.append(f"{header_text} (still has Roman numerals)")
            print(f"❌ Header '{header_text}' still has Roman numerals")
    
    if failures:
        print(f"❌ FAILED: {len(failures)} issues found with headers")
        return False
    
    print(f"✅ PASSED: All {len(h2_headers)} tribe headers are marked as H2 without Roman numerals")
    return True


if __name__ == '__main__':
    print("=" * 80)
    print("Testing Raiding Tribes Paragraphs...")
    print("=" * 80)
    success1 = test_raiding_tribes_paragraphs()
    
    print("\n" + "=" * 80)
    print("Testing Tribe Headers are H2...")
    print("=" * 80)
    success2 = test_tribe_headers_are_h2()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    sys.exit(0 if (success1 and success2) else 1)

