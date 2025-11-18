"""
Formatting and structure adjustments for Chapter 8.

This module handles header sizing, paragraph breaks, and structural
formatting for both class and race descriptions.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple

from .common import normalize_plain_text, update_block_bbox

logger = logging.getLogger(__name__)


def set_header_sizes(section_data: dict) -> None:
    """Set font sizes for class and race award headers to ensure they render as H2."""
    pages = section_data.get("pages", [])
    
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if is_class_award_header(text) or is_race_award_header(text):
                        # Set size to H2 level (12.96 is used elsewhere for H2)
                        span["size"] = 12.96
                        logger.debug(f"Set header size for '{text}' to 12.96 (H2)")




def mark_race_description_headers(section_data: dict) -> None:
    """
    Mark race name headers in the descriptive section as H2 headers.
    
    The second "Individual Race Awards" section contains descriptive text about each race.
    Each race starts with a header like "Dwarf:", "Elf:", etc. These should be H2 headers.
    
    If a block contains both a header span and content spans, split them into separate blocks.
    """
    logger.info("Marking race description headers as H2")
    
    # Race names to look for (without colon, we'll match with colon)
    race_names = ["Dwarf", "Elf", "Half-elf", "Half-Giant", "Halfling", "Mul", "Thri-kreen"]
    
    pages = section_data.get("pages", [])
    
    # Track if we've found the second "Individual Race Awards" section
    found_second_race_section = False
    first_race_section_count = 0
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        block_idx = 0
        
        while block_idx < len(blocks):
            block = blocks[block_idx]
            
            if block.get("type") != "text":
                block_idx += 1
                continue
            
            # Check if this block contains "Individual Race Awards"
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if "Individual Race Awards" in text:
                        first_race_section_count += 1
                        if first_race_section_count == 2:
                            found_second_race_section = True
                            logger.info(f"Found second 'Individual Race Awards' section on page {page_idx}, block {block_idx}")
                        break
            
            # Once we've found the second race section, look for race name headers
            if found_second_race_section:
                lines = block.get("lines", [])
                if lines:
                    first_line = lines[0]
                    spans = first_line.get("spans", [])
                    
                    # Check if the first line has multiple spans where the first span is a race header
                    if len(spans) > 1:
                        first_span_text = spans[0].get("text", "").strip()
                        
                        for race_name in race_names:
                            if first_span_text.startswith(f"{race_name}:"):
                                logger.info(f"Found race header '{race_name}:' with additional content in same block at page {page_idx}, block {block_idx}")
                                
                                # Don't split the block - instead mark it for special rendering
                                # The journal transformer will extract the header and render it separately
                                block["__render_as_race_description_h2_with_content"] = True
                                block["__race_name"] = race_name
                                logger.info(f"Marked '{race_name}' header at block {block_idx} for header extraction")
                                break
                    else:
                        # Single span - check if it's a race header
                        block_text = ""
                        for line in lines:
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if text:
                                    block_text = text
                                    break
                            if block_text:
                                break
                        
                        # Check if block starts with any race name followed by colon
                        for race_name in race_names:
                            if block_text.startswith(f"{race_name}:"):
                                # Mark this block to render as H2
                                block["__render_as_race_description_h2"] = True
                                block["__race_name"] = race_name
                                logger.info(f"Marked '{race_name}' header on page {page_idx}, block {block_idx} as H2")
                                break
            
            block_idx += 1




def mark_trust_test_sections(section_data: dict) -> None:
    """
    Mark the elf trust test sections as H3 headers with lists.
    
    Identifies:
    - "Subtle tests of trust include the following:" -> H3
    - Following 4 items (entrusting, leaving, arranging, asking) -> list items
    - "Life-threatening tests of trust include the following" -> H3
    - Following 4 items (letting, faking, making, challenging) -> list items
    """
    logger.info("Marking trust test sections in Chapter 8")
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section_data for trust test marking")
        return
    
    logger.info(f"Searching {len(pages)} pages for trust test sections")
    
    # Search for the trust test sections
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        logger.debug(f"Page {page_idx} has {len(blocks)} blocks")
        i = 0
        while i < len(blocks):
            block = blocks[i]
            
            # Check for the header texts
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    
                    # Check for "Subtle tests of trust include the following:"
                    if text == "Subtle tests of trust include the following:":
                        logger.info(f"Found 'Subtle tests of trust' header at page {page_idx}, block {i}")
                        
                        # Collect the 4 list items (starting with specific texts)
                        # Start from the current block since the first item may be on a later line in this block
                        list_starts = ["entrusting", "leaving", "arranging", "asking"]
                        list_items = collect_list_items_after_header(blocks, i, list_starts, page_idx)
                        
                        logger.info(f"Collected {len(list_items)} list items for Subtle tests")
                        
                        # Store header and list items together
                        block["__render_as_h3_with_list"] = True
                        block["__h3_text"] = text
                        block["__list_items"] = list_items
                        break
                    
                    # Check for "Life-threatening tests of trust include the following"
                    elif "Life-threatening tests of trust include the following" in text:
                        logger.info(f"Found 'Life-threatening tests of trust' header at page {page_idx}, block {i}")
                        
                        # Collect the 4 list items (starting with specific texts)
                        # Start from the current block since the first item may be on a later line in this block
                        list_starts = ["letting", "faking", "making", "challenging"]
                        list_items = collect_list_items_after_header(blocks, i, list_starts, page_idx)
                        
                        logger.info(f"Collected {len(list_items)} list items for Life-threatening tests")
                        
                        # Store header and list items together
                        block["__render_as_h3_with_list"] = True
                        block["__h3_text"] = "Life-threatening tests of trust include the following:"
                        block["__list_items"] = list_items
                        break
            
            i += 1
    
    logger.info("Trust test section marking complete")




def collect_list_items_after_header(blocks: List[dict], start_idx: int, list_starts: List[str], page_idx: int) -> List[str]:
    """
    Collect list items after a header and mark them for skipping.
    
    The header block itself may contain the first list item on a subsequent line,
    so we need to check all lines in each block, not just the first line.
    
    Args:
        blocks: List of blocks to search
        start_idx: Index to start searching from (the header block itself)
        list_starts: List of text prefixes that identify list items
        page_idx: Page index for logging
    
    Returns:
        List of text strings for each list item
    """
    found_items = []
    found_count = 0
    blocks_to_skip = set()  # Track which blocks to mark for skipping
    i = start_idx
    
    logger.info(f"Collecting list items starting from block {start_idx}, looking for {len(list_starts)} items")
    
    while i < len(blocks) and found_count < len(list_starts):
        block = blocks[i]
        
        # Check each line in the block for list item starts
        for line_idx, line in enumerate(block.get("lines", [])):
            # Get the text from this line, cleaning bullet points and other markers
            line_text = ""
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip() and text.strip() not in [" ", "i n g :", "\x95", "•"]:
                    line_text += text
            
            # Clean up bullet points and extra spaces
            line_text = line_text.strip().lstrip("\x95•").strip()
            
            # Check if this line starts with one of our expected list item prefixes
            for expected_start in list_starts:
                if line_text.lower().startswith(expected_start):
                    logger.info(f"Found list item starting with '{expected_start}' at block {i}, line {line_idx}")
                    
                    # Collect the full text for this list item across possibly multiple blocks
                    full_item_text, consumed_blocks = collect_full_list_item_text(blocks, i, line_idx, page_idx)
                    
                    found_items.append(full_item_text)
                    found_count += 1
                    
                    # Mark blocks that were consumed by this list item to skip rendering
                    blocks_to_skip.update(consumed_blocks)
                    break
        
        i += 1
    
    # Mark all consumed blocks with __skip_render, EXCEPT the header block itself
    # The header block (start_idx) contains the __render_as_h3_with_list marker and shouldn't be skipped
    for block_idx in blocks_to_skip:
        if block_idx != start_idx:  # Don't skip the header block
            blocks[block_idx]["__skip_render"] = True
            logger.info(f"Marked block {block_idx} to skip rendering")
    
    logger.info(f"Collected {len(found_items)} list items, marked {len(blocks_to_skip) - (1 if start_idx in blocks_to_skip else 0)} blocks to skip")
    return found_items




def collect_full_list_item_text(blocks: List[dict], start_block_idx: int, start_line_idx: int, page_idx: int) -> tuple:
    """
    Collect the full text of a list item that may span multiple lines or blocks.
    
    Args:
        blocks: List of blocks
        start_block_idx: Block index where the list item starts
        start_line_idx: Line index within the block where the list item starts
        page_idx: Page index for logging
    
    Returns:
        Tuple of (full_text, consumed_block_indices)
    """
    full_text = ""
    consumed_blocks = {start_block_idx}  # Track which blocks were consumed
    
    # Start with the starting line
    block = blocks[start_block_idx]
    lines = block.get("lines", [])
    
    # Collect text from the starting line onwards in the starting block
    for line_idx in range(start_line_idx, len(lines)):
        for span in lines[line_idx].get("spans", []):
            text = span.get("text", "")
            # Skip bullet points and other markers
            if text.strip() and text.strip() not in [" ", "i n g :", "\x95", "•"]:
                # Remove bullet points from the beginning of text
                cleaned_text = text.lstrip("\x95•").lstrip()
                if cleaned_text:
                    if full_text and not full_text.endswith(" "):
                        full_text += " "
                    full_text += cleaned_text
    
    # Check if the next block continues the list item (same indentation, no new list item start)
    next_idx = start_block_idx + 1
    while next_idx < len(blocks):
        next_block = blocks[next_idx]
        next_lines = next_block.get("lines", [])
        
        if not next_lines:
            break
        
        # Get the first significant text from the next block
        first_text = ""
        for line in next_lines:
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if text and text not in [" ", "i n g :", "\x95", "•"]:
                    # Remove bullet points from the beginning
                    first_text = text.lstrip("\x95•").lstrip()
                    break
            if first_text:
                break
        
        # If the next block starts with a new list item indicator or looks like a new paragraph, stop
        list_starts_any = ["entrusting", "leaving", "arranging", "asking", "letting", "faking", "making", "challenging"]
        if any(first_text.lower().startswith(start) for start in list_starts_any):
            break
        
        # If it looks like continuation (lowercase start, or starts with comma), include it
        if first_text and (first_text[0].islower() or first_text.startswith(",")):
            for line in next_lines:
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    # Skip bullet points and other markers
                    if text.strip() and text.strip() not in ["\x95", "•"]:
                        cleaned_text = text.lstrip("\x95•").lstrip()
                        if cleaned_text:
                            if full_text and not full_text.endswith(" "):
                                full_text += " "
                            full_text += cleaned_text
            consumed_blocks.add(next_idx)
            next_idx += 1
        else:
            break
    
    return full_text.strip(), consumed_blocks




def mark_class_description_paragraph_breaks(section_data: dict) -> None:
    """
    Mark paragraph breaks in Individual Class Awards descriptions section.
    
    Specifically handles:
    - Cleric: 2 paragraphs with break at "However,"
    - Templar: 5 paragraphs with breaks at ["DMs should", "Similarly,", "Note that", "Pleasing the"]
    
    The description text is often fragmented across multiple blocks in the PDF,
    so we need to search through subsequent blocks until we find the next header.
    """
    logger.info("Marking paragraph breaks in class descriptions")
    
    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'w') as f:
        f.write("_mark_class_description_paragraph_breaks called\n")
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section_data for paragraph break marking")
        with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
            f.write("No pages found\n")
        return
    
    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
        f.write(f"Found {len(pages)} pages\n")
    
    # Define class-specific paragraph break points
    # Each entry: (class_name, [list of break points])
    class_paragraph_breaks = {
        "Cleric:": ["However,"],
        "Templar:": ["DMs should", "Similarly,", "Note that", "Pleasing the"],
    }
    
    # Define race description intro paragraph break point
    race_intro_break = "Judgement of good"
    
    # List of all class headers to detect the end of a description
    class_headers = ["Fighter:", "Gladiator:", "Ranger:", "Preserver:", "Defiler:", 
                     "Cleric:", "Druid:", "Templar:", "Rogues:", "Thief:", "Bard:"]
    
    # Search all pages for class description headers followed by descriptive text
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
            f.write(f"Processing page {page_idx} with {len(blocks)} blocks\n")
        
        i = 0
        while i < len(blocks):
            block = blocks[i]
            
            if block.get("type") != "text":
                i += 1
                continue
            
            # Check if this block starts with a class name we're interested in
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        block_text = text
                        break
                if block_text:
                    break
            
            # Debug: log blocks that contain "Cleric" or "Templar"
            if "Cleric" in block_text or "Templar" in block_text:
                with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                    f.write(f"Page {page_idx}, block {i}: Found text with target: '{block_text[:60]}'\n")
                    f.write(f"  Checking startswith for keys: {list(class_paragraph_breaks.keys())}\n")
                    for class_key in class_paragraph_breaks.keys():
                        f.write(f"    '{block_text}'.startswith('{class_key}') = {block_text.startswith(class_key)}\n")
            
            # Check if this is a class description header we need to handle
            class_name = None
            for class_key in class_paragraph_breaks.keys():
                if block_text.startswith(class_key):
                    class_name = class_key
                    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                        f.write(f"MATCHED: Page {page_idx}, block {i}: class_name={class_name}\n")
                    break
            
            if class_name:
                logger.info(f"Found class description header: {class_name} at page {page_idx}, block {i}")
                
                with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                    f.write(f"Processing class {class_name} starting from block {i}\n")
                
                # Get the break points for this class
                break_points = class_paragraph_breaks[class_name]
                
                # Search through subsequent blocks until we find the break points or next header
                for j in range(i + 1, len(blocks)):
                    desc_block = blocks[j]
                    
                    if desc_block.get("type") != "text":
                        continue
                    
                    # Check if this block is a new header (stop searching)
                    is_next_header = False
                    for line in desc_block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if any(text.startswith(h) for h in class_headers):
                                is_next_header = True
                                with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                                    f.write(f"  Block {j}: Found next header, stopping search\n")
                                break
                        if is_next_header:
                            break
                    
                    if is_next_header:
                        break
                    
                    # Check each line in this block for break points
                    lines = desc_block.get("lines", [])
                    for line_idx, line in enumerate(lines):
                        line_text = normalize_plain_text(
                            "".join(span.get("text", "") for span in line.get("spans", []))
                        )
                        
                        # Check if this line starts with any break point
                        for break_text in break_points:
                            if line_text.startswith(break_text):
                                logger.info(f"Found break point '{break_text}' at page {page_idx}, block {j}, line {line_idx}")
                                
                                with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                                    f.write(f"  Block {j}, line {line_idx}: FOUND BREAK POINT '{break_text}'\n")
                                    f.write(f"    Line text: {line_text[:80]}\n")
                                
                                # Mark this line to start a new paragraph
                                if line_idx == 0:
                                    # Entire block should start a new paragraph
                                    desc_block["__force_paragraph_break"] = True
                                    logger.info(f"Marked block {j} with __force_paragraph_break")
                                    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                                        f.write(f"    Marked block {j} with __force_paragraph_break\n")
                                else:
                                    # Need to split this block
                                    first_part_lines = lines[:line_idx]
                                    second_part_lines = lines[line_idx:]
                                    
                                    desc_block["lines"] = first_part_lines
                                    update_block_bbox(desc_block)
                                    
                                    second_block = {
                                        "type": "text",
                                        "lines": second_part_lines,
                                        "__force_paragraph_break": True
                                    }
                                    update_block_bbox(second_block)
                                    
                                    # Insert the new block
                                    page["blocks"].insert(j + 1, second_block)
                                    logger.info(f"Split block {j} and inserted new block at {j + 1}")
                                    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                                        f.write(f"    Split block {j} and inserted new block at {j + 1}\n")
                                break
            
            i += 1
    
    # Now handle the Individual Race Awards description intro paragraph break
    # This section starts with "Good roleplaying of the player character races"
    # and needs a break at "Judgement of good"
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            # Check each line for the break point
            lines = block.get("lines", [])
            for line_idx, line in enumerate(lines):
                line_text = normalize_plain_text(
                    "".join(span.get("text", "") for span in line.get("spans", []))
                )
                
                # Check if this line starts with "Judgement of good"
                if line_text.startswith(race_intro_break):
                    logger.info(f"Found race intro break point at page {page_idx}, block {block_idx}, line {line_idx}")
                    
                    with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                        f.write(f"Race intro BREAK POINT at page {page_idx}, block {block_idx}, line {line_idx}\n")
                        f.write(f"  Line text: {line_text[:80]}\n")
                    
                    # Mark this line to start a new paragraph
                    if line_idx == 0:
                        # Entire block should start a new paragraph
                        block["__force_paragraph_break"] = True
                        logger.info(f"Marked block {block_idx} with __force_paragraph_break")
                        with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                            f.write(f"  Marked block {block_idx} with __force_paragraph_break\n")
                    else:
                        # Need to split this block
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        # Insert the new block
                        page["blocks"].insert(block_idx + 1, second_block)
                        logger.info(f"Split block {block_idx} and inserted new block at {block_idx + 1}")
                        with open('/tmp/chapter8_paragraph_breaks_debug.txt', 'a') as f:
                            f.write(f"  Split block {block_idx} and inserted new block at {block_idx + 1}\n")
                    break
    
    logger.info("Class description paragraph break marking complete")




def mark_race_description_paragraph_breaks(section_data: dict) -> None:
    """
    Mark paragraph breaks in Individual Race Awards descriptions section.
    
    Specifically handles:
    - Elf: 2 paragraphs with break at "With regards to se f-reliance,"
    - Half-elf: 3 paragraphs with breaks at "In extreme" and "Winning such"
    - Half-Giant: 3 paragraphs with breaks at "Sometimes a" and "When Half-Giant"
    - Halfling: 2 paragraphs with break at "Halflings are honor"
    - Thri-kreen: 2 paragraphs with break at "Each creature slain and"
    
    The description text is often fragmented across multiple blocks in the PDF,
    so we need to search through subsequent blocks until we find the next race header.
    """
    logger.info("Marking paragraph breaks in race descriptions")
    
    with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'w') as f:
        f.write("_mark_race_description_paragraph_breaks called\n")
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section_data for race paragraph break marking")
        with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
            f.write("No pages found\n")
        return
    
    with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
        f.write(f"Found {len(pages)} pages\n")
    
    # Define race-specific paragraph break points
    race_paragraph_breaks = {
        "Elf:": ["With regards to se f-reliance,"],
        "Half-elf:": ["In extreme", "Winning such"],
        "Half-Giant:": ["Sometimes a", "When a half-giant character shifts"],
        "Halfling:": ["Halflings are honor"],
        "Thri-kreen:": ["Each creature slain and"],
    }
    
    # List of all race headers to detect boundaries
    race_headers = ["Dwarf:", "Elf:", "Half-elf:", "Half-Giant:", "Halfling:", "Mul:", "Thri-kreen:"]
    
    # Search all pages for race description headers followed by descriptive text
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
            f.write(f"Processing page {page_idx} with {len(blocks)} blocks\n")
        
        i = 0
        while i < len(blocks):
            block = blocks[i]
            
            if block.get("type") != "text":
                i += 1
                continue
            
            # Check if this block starts with a race name we're interested in
            block_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        block_text = text
                        break
                if block_text:
                    break
            
            # Check if this is a race description header we need to handle
            current_race = None
            for race_name, break_points in race_paragraph_breaks.items():
                if block_text.startswith(race_name):
                    current_race = race_name
                    break
            
            if current_race:
                with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                    f.write(f"Found race header '{current_race}' at page {page_idx}, block {i}\n")
                
                # Search for break points in subsequent blocks until we hit the next race header
                break_points = race_paragraph_breaks[current_race]
                j = i + 1
                
                while j < len(blocks):
                    next_block = blocks[j]
                    
                    if next_block.get("type") != "text":
                        j += 1
                        continue
                    
                    # Check if we've hit the next race header
                    next_block_text = ""
                    for line in next_block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                next_block_text = text
                                break
                        if next_block_text:
                            break
                    
                    # Stop if we've reached another race header
                    if any(next_block_text.startswith(rh) for rh in race_headers):
                        with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                            f.write(f"  Reached next race header at block {j}, stopping search\n")
                        break
                    
                    # Check each line in this block for break points
                    lines = next_block.get("lines", [])
                    for line_idx, line in enumerate(lines):
                        line_text = ""
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.strip():
                                line_text += text
                        
                        line_text = line_text.strip()
                        
                        with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                            f.write(
                                f"  Checking line at page {page_idx}, block {j}, line {line_idx}: '{line_text[:60]}'\n"
                            )
                        
                        # Check if this line starts with any of the break points
                        for break_point in break_points:
                            if line_text.startswith(break_point):
                                logger.info(f"Found race break point '{break_point}' at page {page_idx}, block {j}, line {line_idx}")
                                
                                with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                                    f.write(f"  BREAK POINT '{break_point}' at page {page_idx}, block {j}, line {line_idx}\n")
                                    f.write(f"    Line text: {line_text[:80]}\n")
                                
                                # Mark this line to start a new paragraph
                                if line_idx == 0:
                                    # Entire block should start a new paragraph
                                    next_block["__force_paragraph_break"] = True
                                    logger.info(f"Marked block {j} with __force_paragraph_break")
                                    with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                                        f.write(f"    Marked block {j} with __force_paragraph_break\n")
                                else:
                                    # Need to split this block
                                    first_part_lines = lines[:line_idx]
                                    second_part_lines = lines[line_idx:]
                                    
                                    next_block["lines"] = first_part_lines
                                    update_block_bbox(next_block)
                                    
                                    second_block = {
                                        "type": "text",
                                        "lines": second_part_lines,
                                        "__force_paragraph_break": True
                                    }
                                    update_block_bbox(second_block)
                                    
                                    # Insert the new block
                                    page["blocks"].insert(j + 1, second_block)
                                    logger.info(f"Split block {j} and inserted new block at {j + 1}")
                                    with open('/tmp/chapter8_race_paragraph_breaks_debug.txt', 'a') as f:
                                        f.write(f"    Split block {j} and inserted new block at {j + 1}\n")
                                
                                break
                    
                    j += 1
            
            i += 1
    
    logger.info("Race description paragraph break marking complete")


def apply_chapter_8_adjustments(section_data: dict) -> None:
    """
    Apply all Chapter 8 specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    logger.info("Applying Chapter 8 adjustments")
    
    # Extract and structure the Individual Class Awards tables
    _extract_class_award_tables(section_data)
    
    # Extract and structure the Individual Race Awards tables
    _extract_race_award_tables(section_data)
    
    # Set header sizes for class and race names
    _set_header_sizes(section_data)
    
    # Mark race description headers as H2
    _mark_race_description_headers(section_data)
    
    # Mark trust test sections as H3 with lists
    _mark_trust_test_sections(section_data)
    
    # Mark paragraph breaks in class descriptions
    _mark_class_description_paragraph_breaks(section_data)
    
    # Mark paragraph breaks in race descriptions
    _mark_race_description_paragraph_breaks(section_data)
    
    logger.info("Chapter 8 adjustments complete")



