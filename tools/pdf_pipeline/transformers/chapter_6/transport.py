"""
Transport and animal table processing for Chapter 6.

This module handles extraction and processing of transport and animal tables.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from .common import normalize_plain_text, clean_whitespace, get_block_text, extract_table_cell_text

logger = logging.getLogger(__name__)


def extract_transport_table(section_data: dict) -> None:
    """Extract and build the Transport table.
    
    Table structure: 2 columns, 4 sections with varying row counts
    - Chariot: 3 rows
    - Howdah: 4 rows
    - Wagon, open: 4 rows
    - Wagon, enclosed: 5 rows (including armored caravan)
    
    Refactored to follow best practices - broken into focused helper functions.
    """
    logger.info("Starting Transport table extraction")
    logger.info(f"Section has {len(section_data.get('pages', []))} pages")
    
    if len(section_data.get("pages", [])) <= 3:
        logger.warning("Not enough pages for Transport table")
        return
    
    page = section_data["pages"][3]
    blocks = page.get("blocks", [])
    
    # Find header
    header_block_idx = _find_transport_header(blocks)
    if header_block_idx is None:
        logger.warning("Transport header not found")
        return
    
    # Extract transport data
    sections, blocks_to_skip = _extract_transport_data(blocks, header_block_idx)
    
    # Build table
    all_rows = _build_transport_rows(sections)
    if not all_rows:
        logger.warning("Transport table: no rows extracted")
        return
    
    # Create and attach table
    table_data = _create_transport_table(all_rows)
    _attach_transport_table(blocks, header_block_idx, blocks_to_skip, table_data, 3)


def _find_transport_header(blocks: List[dict]) -> Optional[int]:
    """Find the Transport header block index.
    
    Args:
        blocks: List of block dictionaries
        
    Returns:
        Block index or None if not found
    """
    for i, block in enumerate(blocks):
        if block.get("type") == "text":
            text = get_block_text(block).strip()
            if text == "Transport":
                logger.info(f"Found 'Transport' header at Block {i}")
                return i
    return None


def _extract_transport_data(blocks: List[dict], header_block_idx: int) -> Tuple[dict, list]:
    """Extract transport data from blocks following the header.
    
    Args:
        blocks: List of block dictionaries
        header_block_idx: Index of header block
        
    Returns:
        Tuple of (sections dict, blocks_to_skip list)
    """
    sections = {"Chariot": [], "Howdah": [], "Wagon, open": [], "Wagon, enclosed": []}
    current_section = None
    blocks_to_skip = []
    temp_data = []
    unmatched_prices = []
    
    for j in range(header_block_idx + 1, min(header_block_idx + 30, len(blocks))):
        data_block = blocks[j]
        if data_block.get("type") != "text":
            continue
        
        cleaned_text = _clean_transport_text(get_block_text(data_block).strip())
        
        # Check for section headers
        if cleaned_text in ["Chariot", "Howdah", "Wagon, open", "Wagon, enclosed"]:
            _finalize_previous_section(
                sections, current_section, temp_data, unmatched_prices
            )
            current_section = cleaned_text
            temp_data = []
            unmatched_prices = []
            blocks_to_skip.append(j)
            logger.debug(f"Starting section: {cleaned_text}")
        elif current_section:
            _process_transport_block(
                cleaned_text, sections, current_section,
                temp_data, unmatched_prices, j, blocks_to_skip
            )
        
        # Stop if all sections complete
        if _all_sections_complete(sections):
            logger.warning("Stopping early - all sections complete")
            break
    
    logger.warning(f"Final sections collected:")
    for section_name, rows in sections.items():
        logger.warning(f"  {section_name}: {len(rows)} rows = {rows}")
    
    return sections, blocks_to_skip


def _clean_transport_text(text: str) -> str:
    """Clean and normalize transport text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    cleaned = clean_whitespace(text)
    # Fix OCR errors: 'l sp' or 'lsp' → '1 sp'
    cleaned = re.sub(r'l\s*sp', '1 sp', cleaned)
    return cleaned


def _finalize_previous_section(
    sections: dict,
    current_section: str,
    temp_data: list,
    unmatched_prices: list
) -> None:
    """Finalize previous section by matching remaining data.
    
    Args:
        sections: Sections dictionary
        current_section: Current section name
        temp_data: Temporary descriptions
        unmatched_prices: Unmatched prices
    """
    if temp_data and unmatched_prices and current_section:
        num_to_match = min(len(temp_data), len(unmatched_prices))
        for idx in range(num_to_match):
            sections[current_section].append(
                [temp_data[idx], unmatched_prices[idx]]
            )
    if temp_data and current_section:
        logger.warning(
            f"WARNING: {current_section} has {len(temp_data)} unmatched entries"
        )


def _process_transport_block(
    cleaned_text: str,
    sections: dict,
    current_section: str,
    temp_data: list,
    unmatched_prices: list,
    block_idx: int,
    blocks_to_skip: list
) -> None:
    """Process a transport data block.
    
    Args:
        cleaned_text: Cleaned block text
        sections: Sections dictionary
        current_section: Current section name
        temp_data: Temporary descriptions list
        unmatched_prices: Unmatched prices list
        block_idx: Block index
        blocks_to_skip: List of blocks to skip
    """
    if re.search(r'\d+\s*[cs]p', cleaned_text):
        # Price line
        _process_price_line(
            cleaned_text, sections, current_section,
            temp_data, unmatched_prices
        )
        blocks_to_skip.append(block_idx)
    else:
        # Description line
        _process_description_line(cleaned_text, temp_data)
        blocks_to_skip.append(block_idx)


def _process_price_line(
    cleaned_text: str,
    sections: dict,
    current_section: str,
    temp_data: list,
    unmatched_prices: list
) -> None:
    """Process a line containing prices.
    
    Args:
        cleaned_text: Cleaned text
        sections: Sections dictionary
        current_section: Current section name
        temp_data: Descriptions list
        unmatched_prices: Unmatched prices list
    """
    prices = re.findall(r'\d+\s*[cs]p', cleaned_text)
    all_prices = unmatched_prices + prices
    unmatched_prices.clear()
    
    logger.warning(
        f"Found {len(prices)} prices, temp_data has {len(temp_data)} entries"
    )
    
    if temp_data:
        num_to_match = min(len(all_prices), len(temp_data))
        for idx in range(num_to_match):
            sections[current_section].append([temp_data[idx], all_prices[idx]])
        temp_data[:] = temp_data[num_to_match:]
        if len(all_prices) > num_to_match:
            unmatched_prices.extend(all_prices[num_to_match:])
    elif all_prices:
        unmatched_prices.extend(all_prices)


def _process_description_line(cleaned_text: str, temp_data: list) -> None:
    """Process a line containing descriptions.
    
    Args:
        cleaned_text: Cleaned text
        temp_data: Descriptions list
    """
    if "Wagon, armored caravan" in cleaned_text:
        if "pound capacity" in cleaned_text:
            caps = re.findall(r'[\d,]+\s+pound capacity', cleaned_text)
            temp_data.extend(caps)
        temp_data.append("Wagon, armored caravan")
    elif "pound capacity" in cleaned_text:
        caps = re.findall(r'[\d,]+\s+pound capacity', cleaned_text)
        temp_data.extend(caps)
    elif "kank" in cleaned_text and "warrior" in cleaned_text:
        parts = re.split(r'warrior(?=[a-z])', cleaned_text)
        cleaned_parts = [
            p.strip() + (' warrior' if i < len(parts) - 1 or not p.strip().endswith('warrior') else '')
            for i, p in enumerate(parts) if p.strip()
        ]
        temp_data.extend(cleaned_parts if cleaned_parts else [cleaned_text])
    elif re.search(r'\b(inix|mekillot)\b', cleaned_text):
        if cleaned_text in ["inix", "inix, war", "mekillot", "mekillot, war"]:
            temp_data.append(cleaned_text)
        else:
            parts = re.split(r'(?=\b(?:inix|mekillot)\b)', cleaned_text)
            temp_data.extend([p.strip() for p in parts if p.strip()])


def _all_sections_complete(sections: dict) -> bool:
    """Check if all sections have expected row counts.
    
    Args:
        sections: Sections dictionary
        
    Returns:
        True if all sections complete
    """
    expected = [("Chariot", 3), ("Howdah", 4), ("Wagon, open", 4), ("Wagon, enclosed", 5)]
    return all(len(sections[s]) >= exp for s, exp in expected)


def _build_transport_rows(sections: dict) -> list:
    """Build transport table rows from sections.
    
    Args:
        sections: Sections dictionary
        
    Returns:
        List of all rows
    """
    all_rows = []
    for section_name in ["Chariot", "Howdah", "Wagon, open", "Wagon, enclosed"]:
        rows = sections[section_name]
        if rows:
            all_rows.append({"section_header": True, "name": section_name})
            all_rows.extend(rows)
    return all_rows


def _create_transport_table(all_rows: list) -> dict:
    """Create transport table structure.
    
    Args:
        all_rows: List of all rows
        
    Returns:
        Table data dictionary
    """
    table_rows = [{"cells": [{"text": "Type"}, {"text": "Price"}]}]
    
    for r in all_rows:
        if isinstance(r, dict) and r.get("section_header"):
            table_rows.append({
                "cells": [{"text": r["name"], "bold": True}, {"text": ""}]
            })
        else:
            table_rows.append({
                "cells": [{"text": r[0]}, {"text": r[1]}]
            })
    
    return {"rows": table_rows, "header_rows": 1}


def _attach_transport_table(
    blocks: List[dict],
    header_block_idx: int,
    blocks_to_skip: list,
    table_data: dict,
    page_idx: int
) -> None:
    """Attach transport table to header and mark blocks to skip.
    
    Args:
        blocks: List of blocks
        header_block_idx: Header block index
        blocks_to_skip: Blocks to skip list
        table_data: Table data
        page_idx: Page index
    """
    blocks[header_block_idx]["__transport_table"] = table_data
    
    for j in blocks_to_skip:
        if j < len(blocks):
            blocks[j]["__skip_render"] = True
    
    logger.warning(
        f"Transport table attached to page {page_idx} header with "
        f"{len(table_data['rows'])} total rows"
    )




def extract_animals_table(section_data: dict) -> None:
    """Extract and build the Animals table.
    
    Table structure: 2 columns (Animal, Price), 6 rows
    Special handling: "Kank" row is a section divider with sub-items "Trained" and "Untrained"
    
    Data rows:
    - Erdlu: 10 cp
    - Inix: 10 sp
    - Kank (section divider)
      - Trained: 12 sp
      - Untrained: 5 sp
    - Mekillot: 20 sp
    """
    import logging
    import re
    logger = logging.getLogger(__name__)
    
    logger.warning("Starting Animals table extraction")
    logger.warning(f"Section has {len(section_data.get('pages', []))} pages")
    
    # Look through all pages for the "Animals" H2 header (size 10.8, color #ca5804)
    header_block = None
    header_page_idx = None
    header_block_idx = None
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        for i, block in enumerate(blocks):
            if block.get("type") == "text":
                text = get_block_text(block).strip()
                # Look for "Animals" that has been styled as H2 (size 10.8, color #ca5804)
                if text == "Animals":
                    # Check if this span has been styled as H2
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip() == "Animals":
                                size = span.get("size", 0)
                                color = span.get("color", "")
                                # Match H2 styling (size 10.8, header color)
                                if abs(size - 10.8) < 0.1 and color == "#ca5804":
                                    header_block = block
                                    header_page_idx = page_idx
                                    header_block_idx = i
                                    logger.warning(f"Found styled 'Animals' H2 header at Page {page_idx}, Block {i}")
                                    break
                        if header_block:
                            break
            if header_block:
                break
        if header_block:
            break
    
    if header_block is None:
        logger.warning("Could not find styled 'Animals' H2 header")
        return
    
    # Now find all data blocks following the header until the next header
    page = section_data["pages"][header_page_idx]
    blocks = page.get("blocks", [])
    
    # Mark all blocks between the Animals header and the next header (Weapons) to skip rendering
    # These blocks contain the fragmented animal data: Erdlu, 10 cp, Inix, Kank, etc.
    blocks_to_skip = []
    for idx in range(header_block_idx + 1, len(blocks)):
        block = blocks[idx]
        if block.get("type") != "text":
            continue
        
        block_text = get_block_text(block).strip()
        
        # Check if this is the start of the next section (Weapons)
        # Look for headers by checking font color and size
        is_header = False
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                # Headers have color #ca5804 and specific sizes
                if span.get("color") == "#ca5804":
                    is_header = True
                    break
            if is_header:
                break
        
        if is_header:
            logger.warning(f"Found next header at block {idx}: {block_text[:50]}")
            break
        
        # This is a data block, mark it to skip
        blocks_to_skip.append(idx)
        logger.warning(f"Marking block {idx} to skip: {block_text[:50]}")
    
    # Mark all data blocks to skip rendering
    for idx in blocks_to_skip:
        blocks[idx]["__skip_render"] = True
    
    # Build the table rows from source specification
    table_rows = [
        {"cells": [{"text": "Animal"}, {"text": "Price"}]},
        {"cells": [{"text": "Erdlu"}, {"text": "10 cp"}]},
        {"cells": [{"text": "Inix"}, {"text": "10 sp"}]},
        {"cells": [{"text": "Kank", "bold": True}, {"text": ""}]},  # Section divider
        {"cells": [{"text": "  Trained"}, {"text": "12 sp"}]},  # Indented under Kank
        {"cells": [{"text": "  Untrained"}, {"text": "5 sp"}]},  # Indented under Kank
        {"cells": [{"text": "Mekillot"}, {"text": "20 sp"}]},
    ]
    
    table_data = {
        "rows": table_rows,
        "header_rows": 1
    }
    
    # Attach table to the H2 "Animals" header
    header_block["__animals_table"] = table_data
    
    logger.warning(f"Animals table attached to H2 header with {len(table_rows)} rows, marked {len(blocks_to_skip)} blocks to skip")




