#!/usr/bin/env python3
"""Regression test for Chapter 7 Regeneration section paragraph breaks.

This test ensures that the Regeneration: section under "Trees of Life" has proper
paragraph breaks and is not rendered as a single long paragraph.

The section should have:
1. A paragraph about physical form regeneration ending with "in four weeks"
2. A separate paragraph starting with "The life force of a tree of life regenerates"
3. Additional paragraphs about trees of life in the world

This test prevents regression of the fix for the paragraph break issue reported
on 2025-11-13.
"""

import re
import sys
from pathlib import Path


def test_regeneration_paragraph_breaks():
    """Test that the Regeneration section has proper paragraph breaks."""
    
    html_file = Path("data/html_output/chapter-seven-magic.html")
    
    if not html_file.exists():
        print(f"❌ FAIL: {html_file} not found")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find the Regeneration header
    regen_header_pattern = r'<p id="header-14-regeneration">'
    regen_match = re.search(regen_header_pattern, html)
    
    if not regen_match:
        print("❌ FAIL: Could not find Regeneration header")
        return False
    
    # Extract the section from Regeneration to the next major section
    # Look for the next H1 header (Magical Items)
    next_section_pattern = r'<p id="header-15-magical-items">'
    next_section_match = re.search(next_section_pattern, html)
    
    if not next_section_match:
        print("❌ FAIL: Could not find Magical Items header (next section)")
        return False
    
    # Extract the Regeneration section
    section = html[regen_match.end():next_section_match.start()]
    
    # Test 1: Check that "in four weeks." ends a paragraph (not in the middle)
    # Pattern: ...in four weeks.</p>
    if not re.search(r'in four weeks\.\s*</p>', section):
        print("❌ FAIL: 'in four weeks.' does not end a paragraph")
        print("  Expected: ...in four weeks.</p>")
        return False
    
    # Test 2: Check that "The life force of a tree of life regenerates" starts a new paragraph
    # Pattern: <p>The life force of a tree of life regenerates
    if not re.search(r'<p>The life force of a\s*tree\s*of\s*life\s*regenerates', section):
        print("❌ FAIL: 'The life force of a tree of life regenerates' does not start a new paragraph")
        print("  Expected: <p>The life force of a tree of life regenerates...")
        return False
    
    # Test 3: Count paragraphs in the section (should be at least 3)
    # 1. Physical form regeneration paragraph
    # 2. Life force regeneration paragraph  
    # 3. Trees of life in the world paragraphs
    paragraph_count = len(re.findall(r'<p>', section))
    
    if paragraph_count < 3:
        print(f"❌ FAIL: Expected at least 3 paragraphs in Regeneration section, found {paragraph_count}")
        return False
    
    # Test 4: Ensure the paragraph about physical form regeneration doesn't contain
    # "The life force of a tree of life regenerates" (they should be in separate paragraphs)
    physical_form_pattern = r'<p>Both a\s*tree\s*of\s*life.*?</p>'
    physical_form_match = re.search(physical_form_pattern, section, re.DOTALL)
    
    if physical_form_match:
        physical_form_paragraph = physical_form_match.group(0)
        if 'The life force of a tree of life regenerates' in physical_form_paragraph or 'The life force of atree of liferegenerates' in physical_form_paragraph:
            print("❌ FAIL: Physical form and life force regeneration are in the same paragraph")
            print("  These should be in separate paragraphs")
            return False
    
    print("✅ SUCCESS: Regeneration section has proper paragraph breaks")
    print(f"  - Physical form paragraph ends at 'in four weeks.'")
    print(f"  - Life force paragraph starts with 'The life force of a tree of life regenerates'")
    print(f"  - Total paragraphs in section: {paragraph_count}")
    
    return True


def main():
    """Run the regression test."""
    print("Testing Chapter 7 Regeneration section paragraph breaks...")
    print("=" * 60)
    
    success = test_regeneration_paragraph_breaks()
    
    print("=" * 60)
    
    if success:
        print("✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("❌ TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()

