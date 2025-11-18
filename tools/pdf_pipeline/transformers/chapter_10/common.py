"""Common utilities for Chapter 10 processing."""

import re
from typing import Optional


def normalize_plain_text(block: dict) -> str:
    """Extract plain text from a block, joining all spans."""
    if block.get("type") != "text":
        return ""
    text_parts = []
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            text_parts.append(span.get("text", ""))
    return " ".join(text_parts).strip()


def is_header_block(block: dict, expected_text: str) -> bool:
    """Check if a block contains a specific header text."""
    if block.get("type") != "text":
        return False
    
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            text = span.get("text", "").strip()
            if expected_text in text:
                return True
    return False


def clean_whitespace(text: str) -> str:
    """Remove extraneous whitespace from text.
    
    Examples:
    - "% 1" becomes "%1"
    - "M u l e" becomes "Mule"
    - "3 0 %" becomes "30%"
    - "1 - 10" becomes "1-10"
    
    Note: This preserves newlines (\n) in the text.
    """
    # Remove spaces (but not newlines) around dashes in number ranges
    text = re.sub(r'(\d)[ \t]*-[ \t]*(\d)', r'\1-\2', text)
    # Remove spaces (but not newlines) between digits and %
    text = re.sub(r'(\d)[ \t]+%', r'\1%', text)
    # Remove spaces (but not newlines) within numbers
    text = re.sub(r'(\d)[ \t]+(\d)', r'\1\2', text)
    # Remove spaces between letters that appear to be part of words
    # Only do this for single-char separations (but not newlines)
    text = re.sub(r'([a-zA-Z])[ \t]([a-zA-Z])\b', r'\1\2', text)
    return text


def get_block_bbox(block: dict) -> Optional[list]:
    """Extract the bounding box from a block."""
    return block.get("bbox")


def merge_paragraph_fragments(section_data: dict, fragment1: str, fragment2: str) -> None:
    """Merge two paragraph fragments across pages.
    
    Args:
        section_data: The section data dictionary with 'pages' key
        fragment1: The first fragment to find (e.g., "Since Athas is a metal-poor")
        fragment2: The second fragment to find (e.g., "priate for coins found")
    """
    import logging
    logger = logging.getLogger(__name__)
    
    first_block = None
    first_page_idx = None
    first_block_idx = None
    second_block = None
    second_page_idx = None
    second_block_idx = None
    
    # Find both fragments
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            
            if fragment1 in text and first_block is None:
                first_block = block
                first_page_idx = page_idx
                first_block_idx = block_idx
                logger.info(f"Found first fragment at page {page_idx}, block {block_idx}: {text[:50]}")
            
            if fragment2 in text and second_block is None:
                second_block = block
                second_page_idx = page_idx
                second_block_idx = block_idx
                logger.info(f"Found second fragment at page {page_idx}, block {block_idx}: {text[:50]}")
    
    if first_block and second_block:
        # Merge the text: combine the two fragments
        # We need to find the actual span with the hyphenated text in the first block
        for line in first_block.get("lines", []):
            for span in line.get("spans", []):
                text = span.get("text", "")
                if "inappro-" in text or fragment1 in text:
                    # Replace the hyphenated ending with the complete word
                    span["text"] = text.replace("inappro-", "inappropriate")
                    logger.info(f"Merged paragraph fragments: {span['text'][:50]}...")
        
        # Mark the second block for removal
        second_block["__skip_render"] = True
        logger.info(f"Marked second fragment block for removal")

