#!/usr/bin/env python3
"""
Regression test for Chapter 9 'Battling Undead in Dark Sun' paragraph structure.

This test verifies that the 'Battling Undead in Dark Sun' section has 4 properly
separated paragraphs with breaks at:
1. (intro) "On Athas, undead are still just that..."
2. "Mindless undead are corpses or skeletal remains..."
3. "Free-willed undead are usually very powerful creatures..."
4. "Quite often, free-willed undead have minions..."
"""

import json
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def extract_paragraphs_after_header(html_content: str, header_id: str) -> List[str]:
    """
    Extract paragraph text content after a specific header.
    Returns a list of paragraph texts until the next header is reached.
    """
    paragraphs = []
    
    # Find the header
    header_marker = f'id="{header_id}"'
    header_pos = html_content.find(header_marker)
    if header_pos == -1:
        return paragraphs
    
    # Find the end of the header tag
    header_end = html_content.find('</p>', header_pos)
    if header_end == -1:
        return paragraphs
    
    # Start searching for paragraphs after the header
    pos = header_end + 4  # Skip past </p>
    
    while True:
        # Find next <p> tag
        para_start = html_content.find('<p', pos)
        if para_start == -1:
            break
        
        # Check if this is a header (has an id attribute)
        tag_end = html_content.find('>', para_start)
        if tag_end == -1:
            break
        
        tag_content = html_content[para_start:tag_end]
        if ' id=' in tag_content:
            # This is another header, stop
            break
        
        # Find the closing tag
        para_end = html_content.find('</p>', tag_end)
        if para_end == -1:
            break
        
        # Extract the paragraph content
        para_content = html_content[tag_end + 1:para_end]
        
        # Strip HTML tags for comparison
        import re
        text_content = re.sub(r'<[^>]+>', '', para_content).strip()
        
        if text_content:
            paragraphs.append(text_content)
        
        pos = para_end + 4
    
    return paragraphs


def test_battling_undead_paragraphs():
    """
    Test that the 'Battling Undead in Dark Sun' section has 4 paragraphs.
    """
    html_path = project_root / "data" / "html_output" / "chapter-nine-combat.html"
    
    if not html_path.exists():
        print(f"❌ FAILED: HTML file not found: {html_path}")
        return False
    
    html_content = html_path.read_text(encoding='utf-8')
    
    # Extract paragraphs after the "Battling Undead in Dark Sun" header
    paragraphs = extract_paragraphs_after_header(html_content, 'header-12-battling-undead-in-dark-sun')
    
    # Expected number of paragraphs
    expected_count = 4
    actual_count = len(paragraphs)
    
    if actual_count != expected_count:
        print(f"❌ FAILED: Expected {expected_count} paragraphs, found {actual_count}")
        print("\nParagraphs found:")
        for i, para in enumerate(paragraphs, 1):
            print(f"  {i}. {para[:80]}...")
        return False
    
    # Verify the content of each paragraph
    expected_starts = [
        "On Athas, undead are still just that",
        "Mindless undead are corpses",
        "Free-willed undead are usually",
        "Quite often, free-willed undead have minions"
    ]
    
    all_correct = True
    for i, (para, expected_start) in enumerate(zip(paragraphs, expected_starts), 1):
        if not para.startswith(expected_start):
            print(f"❌ FAILED: Paragraph {i} does not start with expected text")
            print(f"  Expected: '{expected_start}...'")
            print(f"  Actual:   '{para[:80]}...'")
            all_correct = False
    
    if not all_correct:
        return False
    
    print("✅ PASSED: Chapter 9 'Battling Undead in Dark Sun' has correct paragraph structure")
    print(f"  Found {actual_count} paragraphs:")
    for i, para in enumerate(paragraphs, 1):
        print(f"    {i}. {para[:60]}...")
    return True


def main():
    """Run the test and exit with appropriate status code."""
    success = test_battling_undead_paragraphs()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

