#!/usr/bin/env python3
"""
Regression test for HTML structure validation.

This test ensures that the HTML output from the journal transformation
contains the expected structural elements:
- Table of Contents (TOC)
- Proper paragraph tags (<p>)
- Header tags with proper hierarchy
- Header IDs for linking
- Back-to-top links
"""

import json
import re
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_html_structure():
    """Test that transformed HTML has proper structure."""
    
    # Load a sample chapter's processed JSON
    json_file = PROJECT_ROOT / "data/processed/journals/chapter-one-ability-scores.json"
    
    if not json_file.exists():
        print(f"❌ FAIL: Test file not found: {json_file}")
        return False
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    content = data.get('data', {}).get('content', '')
    
    if not content:
        print("❌ FAIL: No content found in JSON")
        return False
    
    print(f"📊 Testing HTML structure for chapter-one-ability-scores")
    print(f"   Content length: {len(content)} characters")
    
    failures = []
    
    # Test 1: Check for paragraph tags
    p_count = content.count('<p>')
    if p_count == 0:
        failures.append("No <p> tags found - content should be wrapped in paragraphs")
    else:
        print(f"   ✅ Found {p_count} paragraph tags")
    
    # Test 2: Check for Table of Contents
    if '<nav id="table-of-contents"' not in content:
        failures.append("No Table of Contents (<nav>) found")
    else:
        print(f"   ✅ Table of Contents present")
    
    # Test 3: Check for header IDs (for TOC linking)
    header_id_pattern = r'id="header-\d+-'
    header_ids = re.findall(header_id_pattern, content)
    if not header_ids:
        failures.append("No header IDs found (pattern: id=\"header-N-...\")")
    else:
        print(f"   ✅ Found {len(header_ids)} header IDs")
    
    # Test 4: Check for header classes (header-h2, header-h3, header-h4)
    if 'header-h2' not in content and 'header-h3' not in content:
        failures.append("No header CSS classes found (header-h2, header-h3, header-h4)")
    else:
        h2_count = content.count('header-h2')
        h3_count = content.count('header-h3')
        h4_count = content.count('header-h4')
        print(f"   ✅ Found header classes: H2={h2_count}, H3={h3_count}, H4={h4_count}")
    
    # Test 5: Check for back-to-top links
    if '[^]' not in content:
        failures.append("No back-to-top links found ([^])")
    else:
        back_links = content.count('[^]')
        print(f"   ✅ Found {back_links} back-to-top links")
    
    # Test 6: Verify content is not just a single giant text node
    # There should be multiple closing </p> tags
    closing_p_count = content.count('</p>')
    if closing_p_count < 3:
        failures.append(f"Too few closing paragraph tags ({closing_p_count}) - content appears to be a single block")
    else:
        print(f"   ✅ Found {closing_p_count} separate paragraphs")
    
    # Test 7: Headers should not be inline spans without proper wrapping
    # Bad: <span style="color: #ca5804">Header Text</span>
    # Good: <p id="header-1-..."><span class="header-h2" ...>Header Text</span></p>
    inline_colored_spans = re.findall(r'<span style="color: #ca5804">([^<]+)</span>', content)
    unwrapped_headers = []
    for span_text in inline_colored_spans:
        # Check if this span is within a proper paragraph structure
        # This is a simplified check - in reality we'd need proper HTML parsing
        if len(span_text) > 10 and span_text[0].isupper():
            # Likely a header
            pattern = f'<p[^>]*>.*?{re.escape(span_text)}.*?</p>'
            if not re.search(pattern, content, re.DOTALL):
                unwrapped_headers.append(span_text[:50])
    
    if unwrapped_headers:
        failures.append(f"Found {len(unwrapped_headers)} headers not wrapped in <p> tags")
        for header in unwrapped_headers[:3]:
            print(f"      Example: {header}...")
    
    # Report results
    print()
    if failures:
        print("❌ HTML STRUCTURE TEST FAILED")
        print("=" * 60)
        for i, failure in enumerate(failures, 1):
            print(f"{i}. {failure}")
        print("=" * 60)
        return False
    else:
        print("✅ HTML STRUCTURE TEST PASSED")
        print("=" * 60)
        return True


def test_multiple_chapters():
    """Test HTML structure for multiple chapters."""
    
    chapters = [
        "chapter-one-ability-scores",
        "chapter-two-player-character-races",
        "chapter-three-player-character-classes",
    ]
    
    results = {}
    
    for chapter in chapters:
        json_file = PROJECT_ROOT / f"data/processed/journals/{chapter}.json"
        
        if not json_file.exists():
            results[chapter] = "SKIP"
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        content = data.get('data', {}).get('content', '')
        
        # Quick checks
        has_p_tags = '<p>' in content
        has_toc = '<nav id="table-of-contents"' in content
        has_headers = 'header-h2' in content or 'header-h3' in content
        
        if has_p_tags and has_toc and has_headers:
            results[chapter] = "PASS"
        else:
            results[chapter] = f"FAIL (p={has_p_tags}, toc={has_toc}, headers={has_headers})"
    
    print("\n" + "=" * 60)
    print("MULTI-CHAPTER TEST RESULTS")
    print("=" * 60)
    
    for chapter, result in results.items():
        status = "✅" if result == "PASS" else "❌" if result.startswith("FAIL") else "⏭️"
        print(f"{status} {chapter}: {result}")
    
    all_passed = all(r == "PASS" for r in results.values() if r != "SKIP")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    print("🧪 HTML STRUCTURE REGRESSION TEST")
    print("=" * 60)
    print()
    
    # Test single chapter in detail
    single_test_passed = test_html_structure()
    print()
    
    # Test multiple chapters
    multi_test_passed = test_multiple_chapters()
    print()
    
    # Exit with appropriate code
    if single_test_passed and multi_test_passed:
        print("🎉 ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("💥 SOME TESTS FAILED")
        sys.exit(1)

