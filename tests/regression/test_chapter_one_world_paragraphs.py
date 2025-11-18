"""
Test that Chapter One: The World of Athas has correct paragraph breaks.

This test verifies that:
1. "The Wanderer's Journal" section has 3 paragraphs with breaks at:
   - "This is a land of blood"
   - "This is my home"

2. "Overview of the World" section has 10 paragraphs with breaks at:
   - "From the first"
   - "A man cannot drink"
   - "The wind does"
   - "Breezes on"
   - "As dangerous"
   - "I have already"
   - "At night"
   - "As far I"
   - "Though the picture"
"""

import os
import re
from bs4 import BeautifulSoup


def test_wanderers_journal_paragraphs():
    """Test that The Wanderer's Journal section has correct paragraph breaks."""
    html_path = "/Users/cjohannsen/git/darksun-pf2e/data/html_output/chapter-one-the-world-of-athas.html"
    
    assert os.path.exists(html_path), f"HTML file not found: {html_path}"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the Wanderer's Journal section (it's an h2 tag in Chapter 1)
    wanderer_header = None
    overview_header = None
    for tag in soup.find_all('h2'):
        if "Wanderer" in tag.get_text() and "Journal" in tag.get_text():
            wanderer_header = tag
        if "Overview of the World" in tag.get_text():
            overview_header = tag
    
    assert wanderer_header is not None, "Could not find 'The Wanderer's Journal' header"
    
    # Collect paragraphs between the two headers
    paragraphs = []
    current = wanderer_header.find_next_sibling()
    
    while current and current != overview_header:
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                paragraphs.append(text)
        current = current.find_next_sibling()
    
    # The Wanderer's Journal should have 3 paragraphs
    assert len(paragraphs) == 3, f"Expected 3 paragraphs in The Wanderer's Journal, found {len(paragraphs)}"
    
    # Check that the paragraph breaks are at the correct locations
    # Paragraph 1 should end with or before "This is a land of blood"
    # Paragraph 2 should start with "This is a land of blood" and end with or before "This is my home"
    # Paragraph 3 should start with "This is my home"
    
    assert "This is a land of blood" in paragraphs[1], \
        "Second paragraph should contain 'This is a land of blood'"
    assert "This is my home" in paragraphs[2], \
        "Third paragraph should contain 'This is my home'"
    
    print("✅ The Wanderer's Journal has correct paragraph breaks (3 paragraphs)")
    print(f"   - Paragraph 1: {len(paragraphs[0])} chars")
    print(f"   - Paragraph 2: {len(paragraphs[1])} chars")
    print(f"   - Paragraph 3: {len(paragraphs[2])} chars")


def test_overview_of_world_paragraphs():
    """Test that Overview of the World section has correct paragraph breaks."""
    html_path = "/Users/cjohannsen/git/darksun-pf2e/data/html_output/chapter-one-the-world-of-athas.html"
    
    assert os.path.exists(html_path), f"HTML file not found: {html_path}"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the Overview of the World section (it's an h2 tag in Chapter 1)
    overview_header = None
    geography_header = None
    for tag in soup.find_all('h2'):
        if "Overview of the World" in tag.get_text():
            overview_header = tag
        if "General Geography" in tag.get_text():
            geography_header = tag
    
    assert overview_header is not None, "Could not find 'Overview of the World' header"
    
    # Collect paragraphs between the two headers
    paragraphs = []
    current = overview_header.find_next_sibling()
    
    while current and current != geography_header:
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                paragraphs.append(text)
        current = current.find_next_sibling()
    
    # Overview of the World should have 10 paragraphs
    assert len(paragraphs) == 10, f"Expected 10 paragraphs in Overview of the World, found {len(paragraphs)}"
    
    # Check that the paragraph breaks are at the correct locations
    expected_starts = [
        "Athas is a desert",  # Paragraph 1 starts with this
        "From the first",     # Paragraph 2
        "A man cannot drink", # Paragraph 3
        "The wind does",      # Paragraph 4
        "Breezes on",         # Paragraph 5
        "As dangerous",       # Paragraph 6
        "I have already",     # Paragraph 7
        "At night",           # Paragraph 8
        "As far I",           # Paragraph 9
        "Though the picture", # Paragraph 10
    ]
    
    for i, expected_start in enumerate(expected_starts):
        assert paragraphs[i].startswith(expected_start), \
            f"Paragraph {i+1} should start with '{expected_start}', but starts with: {paragraphs[i][:50]}"
    
    print("✅ Overview of the World has correct paragraph breaks (10 paragraphs)")
    for i, para in enumerate(paragraphs):
        print(f"   - Paragraph {i+1}: starts with '{para[:30]}...' ({len(para)} chars)")


if __name__ == "__main__":
    print("Testing Chapter One: The World of Athas paragraph breaks...\n")
    
    try:
        test_wanderers_journal_paragraphs()
    except AssertionError as e:
        print(f"❌ The Wanderer's Journal test failed: {e}")
        exit(1)
    
    try:
        test_overview_of_world_paragraphs()
    except AssertionError as e:
        print(f"❌ Overview of the World test failed: {e}")
        exit(1)
    
    print("\n✅ All tests passed!")

