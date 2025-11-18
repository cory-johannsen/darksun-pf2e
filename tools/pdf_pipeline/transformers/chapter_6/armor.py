"""
Armor table processing for Chapter 6.

This module handles extraction and processing of armor-related tables,
including barding (animal armor).
"""

from __future__ import annotations

import logging
import re
from typing import List

from .common import normalize_plain_text, clean_whitespace, get_block_text, extract_table_cell_text

logger = logging.getLogger(__name__)


def extract_barding_table(section_data: dict) -> None:
    """Extract and build the Barding table.
    
    Table structure: 6 rows (incl header), 3 columns (Type, Price, Weight)
    Data is on Page 3, Blocks 34-37
    
    NOTE: There are TWO "Barding" entries in the PDF:
    - First: plain text "Barding" after H2 "Tack and Harness" (New Equipment section) - converted to H3 by _adjust_header_sizes
    - Second: "Barding: " in Equipment Descriptions section - already a header
    
    This function attaches the table to the FIRST occurrence (the H3 in New Equipment section).
    """
    import logging
    import re
    logger = logging.getLogger(__name__)
    
    logger.warning("Starting Barding table extraction")
    logger.warning(f"Section has {len(section_data.get('pages', []))} pages")
    
    # Look through all pages for the "Barding" H3 header (size 9.6, color #ca5804)
    header_block = None
    header_page = None
    header_block_idx = None
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        for i, block in enumerate(blocks):
            if block.get("type") == "text":
                text = get_block_text(block).strip()
                # Look for "Barding" that has been styled as H3 (size 9.6, color #ca5804)
                if text == "Barding":
                    # Check if this span has been styled as H3
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip() == "Barding":
                                size = span.get("size", 0)
                                color = span.get("color", "")
                                # Match H3 styling (size 9.6, header color)
                                if abs(size - 9.6) < 0.1 and color == "#ca5804":
                                    header_block = block
                                    header_page = page
                                    header_block_idx = i
                                    logger.warning(f"Found styled 'Barding' H3 header at Page {page_idx}, Block {i}")
                                    break
                        if header_block:
                            break
            if header_block:
                break
        if header_block:
            break
    
    if header_block is None:
        logger.warning("Could not find styled 'Barding' H3 header")
        return
    
    # Now collect data from blocks following the header
    blocks = header_page.get("blocks", [])
    rows = []
    blocks_to_skip = []
    
    # Look at next ~5 blocks for barding data
    for j in range(header_block_idx + 1, min(header_block_idx + 6, len(blocks))):
        data_block = blocks[j]
        if data_block.get("type") != "text":
            continue
        
        data_text = get_block_text(data_block).strip()
        logger.warning(f"Barding block {j}: {data_text[:80]}")
        
        # Stop if we hit the Transport header (size 10.8, color #ca5804)
        is_transport_header = False
        for line in data_block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("text", "").strip() == "Transport":
                    size = span.get("size", 0)
                    color = span.get("color", "")
                    if abs(size - 10.8) < 0.1 and color == "#ca5804":
                        is_transport_header = True
                        break
            if is_transport_header:
                break
        
        if is_transport_header:
            logger.warning("Hit Transport header, stopping")
            break
        
        # Parse barding rows
        # Format: "Inix, leather 35 sp 240 lb"
        # Or: "Inix, leather 35 sp 240 lb Inix, chitin 50 sp 400 lb" (multiple rows in one block)
        cleaned_text = clean_whitespace(data_text)
        
        # Match patterns like "Inix, leather 35 sp 240 lb" - flexible with whitespace
        pattern = r'([A-Z][a-z]+(?:,\s*[a-z]+)?)\s*(\d+\s*[sc]p)\s*(\d+\s*lb)'
        matches = re.findall(pattern, cleaned_text)
        logger.warning(f"  Matches found: {len(matches)}")
        
        if matches:
            for match in matches:
                animal_type = match[0].strip()
                price = match[1].strip()
                weight = match[2].strip()
                rows.append([animal_type, price, weight])
            
            blocks_to_skip.append(j)
    
    if len(rows) == 6:
        # Build table structure
        # Build _render_table-compatible structure
        table_rows = [
            {"cells": [{"text": "Type"}, {"text": "Price"}, {"text": "Weight"}]}
        ] + [
            {"cells": [{"text": r[0]}, {"text": r[1]}, {"text": r[2]}]} for r in rows
        ]
        table_data = {
            "rows": table_rows,
            "header_rows": 1
        }
        
        # Attach table to the H3 "Barding" header
        header_block["__barding_table"] = table_data
        
        # Mark data blocks to skip rendering
        for j in blocks_to_skip:
            blocks[j]["__skip_render"] = True
        
        logger.warning(f"Barding table attached to styled H3 header with {len(rows)} rows")
        return
    else:
        logger.warning(f"Barding table: expected 6 rows, found {len(rows)}")




