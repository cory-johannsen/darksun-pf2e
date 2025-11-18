#!/usr/bin/env python3
"""
Regression test for Elven Herdsmen section paragraph breaks.

Ensures the Elven Herdsmen section in Chapter Two: Athasian Society
has 9 paragraphs with proper breaks.
"""

import sys
import os
import re

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)


def test_elven_herdsmen_paragraphs():
    """
    Test that the Elven Herdsmen section has exactly 9 paragraphs
    with breaks at the specified locations.
    """
    html_file = os.path.join(project_root, 'data', 'html_output', 'chapter-two-athasian-society.html')
    
    if not os.path.exists(html_file):
        print(f"❌ ERROR: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract the Elven Herdsmen section
    # Find from header-51-elven-herdsmen to header-52-raiding-tribes
    pattern = r'<p id="header-51-elven-herdsmen">.*?(?=<p id="header-52-raiding-tribes">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        print("❌ ERROR: Could not find Elven Herdsmen section")
        return False
    
    section = match.group(0)
    
    # Count paragraphs (excluding the header paragraph)
    # Remove the header paragraph first
    section_without_header = re.sub(r'<p id="header-51-elven-herdsmen">.*?</p>', '', section, count=1)
    
    # Count <p> tags
    paragraphs = re.findall(r'<p>.*?</p>', section_without_header, re.DOTALL)
    paragraph_count = len(paragraphs)
    
    print(f"📊 Found {paragraph_count} paragraphs in Elven Herdsmen section")
    
    # Expected paragraph breaks
    expected_breaks = [
        "What other races",
        "Admittedly,",
        "This free-for-all",
        "Whatever the sex",
        "Elven tribes",
        "Kanks can eat",
        "Of course, there",
        "Aside from its honey",
    ]
    
    # Expected: 9 paragraphs total (1 intro + 8 breaks = 9 paragraphs)
    expected_count = 9
    
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
    
    print("✅ PASSED: Elven Herdsmen section has correct paragraph structure")
    print(f"   - {paragraph_count} paragraphs")
    print(f"   - All {len(expected_breaks)} expected breaks present")
    return True


if __name__ == '__main__':
    success = test_elven_herdsmen_paragraphs()
    sys.exit(0 if success else 1)

