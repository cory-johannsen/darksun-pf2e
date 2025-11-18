#!/usr/bin/env python3
"""
Regression Test: Chapter 10 Coins Section Paragraph Structure

This test verifies that the Coins section in Chapter 10 renders as 4 separate
paragraphs with proper breaks.

Issue: The source PDF has the Coins section content that should be split into
4 distinct paragraphs, but the merge logic was incorrectly combining them.

Required paragraph breaks at:
1. "Because metal coins are more valuable on Athas..." (first paragraph)
2. "No platinum or electrum pieces are regularly minted..."
3. "Bits are one-tenth pie pieces of a ceramic piece..."
4. "Ceramic, silver, and gold pieces weigh in at 50 to the pound..."
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_coins_section_four_paragraphs():
    """Verify that the Coins section has 4 separate paragraphs."""
    html_file = project_root / "data" / "html_output" / "chapter-ten-treasure.html"
    
    if not html_file.exists():
        print(f"❌ FAIL: HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the Coins header
    coins_header = soup.find(id='header-3-coins')
    if not coins_header:
        print("❌ FAIL: Coins header not found (id='header-3-coins')")
        return False
    
    print("✅ Found Coins header")
    
    # Count paragraphs between Coins header and the next header
    paragraphs = []
    current = coins_header.find_next_sibling()
    
    while current and current.name == 'p':
        # Stop if we hit another header
        if current.get('id', '').startswith('header-'):
            break
        paragraphs.append(current)
        current = current.find_next_sibling()
    
    print(f"\n📊 Found {len(paragraphs)} paragraph(s) in Coins section")
    
    # Verify we found exactly 4 paragraphs
    if len(paragraphs) != 4:
        print(f"❌ FAIL: Expected 4 paragraphs, but found {len(paragraphs)}")
        for i, para in enumerate(paragraphs, 1):
            text = para.get_text()
            print(f"\n   Paragraph {i} ({len(text)} chars):")
            print(f"   Starts: {text[:80]}...")
        return False
    
    print(f"\n✅ Correct number of paragraphs (4)")
    
    # Verify each paragraph starts with the expected text
    expected_starts = [
        "Because metal coins are more valuable",
        "No platinum",
        "Bits are",
        "Ceramic, silver"
    ]
    
    all_correct = True
    for i, (para, expected_start) in enumerate(zip(paragraphs, expected_starts), 1):
        para_text = para.get_text().strip()
        if para_text.startswith(expected_start):
            print(f"   ✅ Paragraph {i} starts correctly: '{expected_start}'")
        else:
            print(f"   ❌ Paragraph {i} - Expected start: '{expected_start}'")
            print(f"      Actual start: '{para_text[:50]}'")
            all_correct = False
    
    if not all_correct:
        return False
    
    # Verify specific paragraph content
    para1_text = paragraphs[0].get_text()
    if "be used to." not in para1_text:
        print(f"\n❌ FAIL: Paragraph 1 doesn't end correctly")
        return False
    
    para2_text = paragraphs[1].get_text()
    if "placed by the DM." not in para2_text:
        print(f"\n❌ FAIL: Paragraph 2 doesn't end correctly")
        return False
        
    para3_text = paragraphs[2].get_text()
    if "partially broken coins." not in para3_text:
        print(f"\n❌ FAIL: Paragraph 3 doesn't end correctly")
        return False
    
    para4_text = paragraphs[3].get_text()
    if "Five hundred bits weigh 1 pound." not in para4_text:
        print(f"\n❌ FAIL: Paragraph 4 doesn't end correctly")
        return False
    
    print(f"\n✅ All paragraphs have correct content and endings")
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Coins section has 4 properly separated paragraphs")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_coins_section_four_paragraphs()
    sys.exit(0 if success else 1)

