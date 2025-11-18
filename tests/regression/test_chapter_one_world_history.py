"""
Test for Chapter One: The World of Athas - History section paragraph breaks

Validates that the History section has exactly 14 paragraphs with correct break points.
"""

import os
import pytest
from bs4 import BeautifulSoup


def test_history_paragraph_count():
    """Test that History section has exactly 14 paragraphs"""
    
    # Read the generated HTML
    html_path = "data/html_output/chapter-one-the-world-of-athas.html"
    assert os.path.exists(html_path), f"HTML file not found: {html_path}"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the History header (it's an h2 tag in Chapter 1)
    history_header = soup.find('h2', id='header-8-history')
    
    assert history_header is not None, "History header not found"
    
    # Get all paragraphs after History header until the next section or end
    paragraphs = []
    current = history_header.find_next_sibling()
    
    while current:
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                paragraphs.append(text)
        elif current.name == 'h2':
            # Stop at next header
            break
        current = current.find_next_sibling()
    
    # Should have exactly 14 paragraphs
    assert len(paragraphs) == 14, f"Expected 14 paragraphs in History section, found {len(paragraphs)}"


def test_history_paragraph_starts():
    """Test that History paragraphs start with the correct text"""
    
    html_path = "data/html_output/chapter-one-the-world-of-athas.html"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the History header (it's an h2 tag in Chapter 1)
    history_header = soup.find('h2', id='header-8-history')
    
    # Get all paragraphs after History header
    paragraphs = []
    current = history_header.find_next_sibling()
    
    while current:
        if current.name == 'p':
            text = current.get_text(strip=True)
            if text:
                paragraphs.append(text)
        elif current.name == 'h2':
            break
        current = current.find_next_sibling()
    
    # Expected paragraph starts
    expected_starts = [
        "What generally passes",  # Paragraph 1
        "Still,",                  # Paragraph 2
        "As incredible",           # Paragraph 3
        "Yet, the",                # Paragraph 4
        "Turning from",            # Paragraph 5
        "These ballads",           # Paragraph 6
        "Most Athasians",          # Paragraph 7
        "The world abounds",       # Paragraph 8
    ]
    
    # Verify key paragraph starts (first 8 paragraphs)
    for i, expected_start in enumerate(expected_starts):
        if i < len(paragraphs):
            actual_text = paragraphs[i].strip()
            assert actual_text.startswith(expected_start), \
                f"Paragraph {i+1} should start with '{expected_start}', but starts with '{actual_text[:50]}...'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

