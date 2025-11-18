#!/usr/bin/env python3
"""
Test that Chapter 8 Individual Race Awards description intro has proper paragraph break.

This test verifies that the opening text for the Individual Race Awards descriptions
section (Roman numeral IV) has a paragraph break at "Judgement of good".

Expected structure:
- Paragraph 1: "Good roleplaying of the player character races in DARK SUN brings 
  with it substantial experience point awards. Conversely, poor roleplaying brings 
  drastic penalties, regardless of individual class awards."
- Paragraph 2: "Judgement of good roleplaying ultimately lies with the DM..."
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

def test_race_intro_paragraph_break():
    """Test that the race awards description intro has proper paragraph break."""
    
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-eight-experience.html"
    
    if not html_path.exists():
        print(f"❌ HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find the fourth H1 header (Roman numeral IV) for Individual Race Awards descriptions
    h1_headers = soup.find_all('p', id=lambda x: x and x.startswith('header-') and 'individual-race-awards' in x)
    
    if len(h1_headers) < 2:
        print(f"❌ Expected at least 2 'Individual Race Awards' headers, found {len(h1_headers)}")
        return False
    
    # The second occurrence is the descriptive section (Roman numeral IV)
    second_race_header = h1_headers[1]
    
    # Get all paragraphs after this header until the next H1 or H2 header
    paragraphs = []
    current = second_race_header.find_next_sibling()
    
    while current:
        # Stop at next header
        if current.name == 'p' and current.get('id', '').startswith('header-'):
            break
        
        if current.name == 'p' and not current.get('class'):
            # Regular paragraph (not a header)
            paragraphs.append(current.get_text(strip=True))
        
        current = current.find_next_sibling()
    
    if len(paragraphs) < 2:
        print(f"❌ Expected at least 2 paragraphs after 'Individual Race Awards' header, found {len(paragraphs)}")
        print(f"   Paragraphs found: {paragraphs}")
        return False
    
    # Check first paragraph contains the expected text
    first_para_text = paragraphs[0]
    expected_first_start = "Good roleplaying of the player character races"
    expected_first_end = "regardless of individual class awards"
    
    if not first_para_text.startswith(expected_first_start):
        print(f"❌ First paragraph doesn't start with expected text")
        print(f"   Expected start: {expected_first_start}")
        print(f"   Actual start: {first_para_text[:60]}...")
        return False
    
    if expected_first_end not in first_para_text:
        print(f"❌ First paragraph doesn't end with expected text")
        print(f"   Expected to contain: {expected_first_end}")
        print(f"   Actual text: {first_para_text}")
        return False
    
    # Check that "Judgement of good" is NOT in the first paragraph
    if "Judgement of good" in first_para_text:
        print(f"❌ First paragraph incorrectly contains 'Judgement of good'")
        print(f"   First paragraph should end at 'individual class awards'")
        print(f"   Actual: {first_para_text}")
        return False
    
    # Check second paragraph starts with "Judgement of good"
    second_para_text = paragraphs[1]
    expected_second_start = "Judgement of good"
    
    if not second_para_text.startswith(expected_second_start):
        print(f"❌ Second paragraph doesn't start with 'Judgement of good'")
        print(f"   Expected start: {expected_second_start}")
        print(f"   Actual start: {second_para_text[:60]}...")
        return False
    
    # Check second paragraph contains expected content
    expected_content = [
        "roleplaying ultimately lies with the DM",
        "familiar with all the nuances",
        "Athasian player character races",
        "never to forget the peculiarities",
        "emphasize the unique nature of Dark Sun"
    ]
    
    for content in expected_content:
        if content not in second_para_text:
            print(f"❌ Second paragraph missing expected content: '{content}'")
            print(f"   Actual text: {second_para_text[:200]}...")
            return False
    
    print("✅ Race awards description intro has proper paragraph break at 'Judgement of good'")
    return True

if __name__ == "__main__":
    success = test_race_intro_paragraph_break()
    sys.exit(0 if success else 1)

