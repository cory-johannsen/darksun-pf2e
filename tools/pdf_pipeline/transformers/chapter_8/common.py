"""
Common utility functions for Chapter 8 processing.

This module contains shared utility functions used across all Chapter 8 processors.
"""

from __future__ import annotations

import re


def normalize_plain_text(text: str) -> str:
    """Normalize text for comparison by removing extra whitespace."""
    return re.sub(r'\s+', ' ', text.strip())




def update_block_bbox(block: dict) -> None:
    """Update a block's bounding box based on its lines."""
    lines = block.get("lines", [])
    if not lines:
        return
    
    # Calculate bbox from all lines
    x0 = min(line["bbox"][0] for line in lines)
    y0 = min(line["bbox"][1] for line in lines)
    x1 = max(line["bbox"][2] for line in lines)
    y1 = max(line["bbox"][3] for line in lines)
    block["bbox"] = [x0, y0, x1, y1]




def is_class_award_header(text: str) -> bool:
    """Check if text is one of the class award headers."""
    return text.strip() in CLASS_AWARD_HEADERS




def is_race_award_header(text: str) -> bool:
    """Check if text is one of the race award headers.
    
    Checks if text starts with a race header, since some headers like "Mul:"
    are combined with following text in the PDF.
    """
    text = text.strip()
    # First try exact match for backwards compatibility
    if text in RACE_AWARD_HEADERS:
        return True
    # Then try "starts with" for headers combined with text
    for header in RACE_AWARD_HEADERS:
        if text.startswith(header):
            return True
    return False




def is_column_header(text: str) -> bool:
    """Check if text is a table column header (Action or Awards)."""
    text = text.strip()
    return text in ["Action", "Awards"]




def is_xp_value(text: str) -> bool:
    """Check if text looks like an XP/awards value."""
    text = text.strip()
    # Match patterns like: "10 XP/level", "50 XP/day", "100 XP", "XP value", etc.
    xp_patterns = [
        r'\d+\s*XP/level',
        r'\d+\s*XP/day',
        r'\d+\s*XP/spell\s+level',
        r'\d+\s*XP',
        r'XP\s+value',
        r'\d+\s*XP/cp\s+value',
        r'\d+\s*XP\s*/\s*PSP',
        r'Hit\s+Dice',
        r'\d+\s*XP\s*x\s*level',
    ]
    for pattern in xp_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False




def clean_xp_text(text: str) -> str:
    """
    Clean up excessive whitespace in XP values.
    
    Examples:
        "1 0  X P / P S P" -> "10 XP/PSP"
        "2 0 0  X P" -> "200 XP"
        "7 5 0  X P" -> "750 XP"
    """
    # Remove spaces between letters in XP and PSP first (before digit cleanup)
    text = re.sub(r'X\s+P', 'XP', text)
    text = re.sub(r'P\s+S\s+P', 'PSP', text)
    # Remove ALL spaces between digits (loop until no more matches)
    while re.search(r'(\d)\s+(\d)', text):
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    # Remove extra spaces around slashes and operators
    text = re.sub(r'\s*/\s*', '/', text)
    text = re.sub(r'\s+x\s+', ' x ', text)
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()




