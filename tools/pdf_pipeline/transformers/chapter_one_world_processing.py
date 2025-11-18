"""
Chapter One: The World of Athas processing

Handles paragraph breaking for the History section and other sections in Chapter One: The World of Athas.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def normalize_plain_text(text: str) -> str:
    """Normalize text by collapsing whitespace"""
    return " ".join(text.split())


def update_block_bbox(block: dict) -> None:
    """Update block bbox based on its lines"""
    if not block.get("lines"):
        return
    
    first_line = block["lines"][0]
    last_line = block["lines"][-1]
    
    block["bbox"] = [
        first_line["bbox"][0],  # left
        first_line["bbox"][1],  # top
        last_line["bbox"][2],   # right
        last_line["bbox"][3]    # bottom
    ]


def force_history_paragraph_breaks(page: dict) -> None:
    """
    Force paragraph breaks within the History section blocks.
    
    The History section should have 14 paragraphs, but several of them are within 
    single text blocks and need to be split at specific break points.
    """
    logger.info("Forcing History section paragraph breaks")
    
    # Break points that may occur mid-block
    break_points = [
        "Still, we can",
        "As incredible as",
        "Yet, the sorcerer",
        "Turning from political",
        "These ballads sing",
        "Most Athasians regard",
        "The world abounds",
        "If you have ever",
        ". Like men, the",  # Mid-line break
        ". Even the plants,",  # Mid-line break
        ". The essence of",  # Mid-line break
        "I have no idea",
        "If we can discover"
    ]
    
    blocks_to_insert: List[Tuple[int, dict]] = []
    
    blocks = page.get("blocks", [])
    
    for idx, block in enumerate(list(blocks)):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line to see if it contains a break point
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if line starts with break point OR contains mid-line break point
            starts_with_break = any(line_text.startswith(bp) for bp in break_points if not bp.startswith("."))
            contains_mid_break = any(bp in line_text for bp in break_points if bp.startswith("."))
            
            # For start-of-line breaks, split the block at this line if not the first line
            if starts_with_break and line_idx > 0:
                # Split this block at this line
                first_part_lines = lines[:line_idx]
                second_part_lines = lines[line_idx:]
                
                logger.info(f"Splitting block at line {line_idx}: '{line_text[:60]}...'")
                
                # Update the current block to only contain the first part
                block["lines"] = first_part_lines
                update_block_bbox(block)
                
                # Create a new block for the second part
                second_block = {
                    "type": "text",
                    "lines": second_part_lines,
                    "__force_paragraph_break": True
                }
                update_block_bbox(second_block)
                
                # Schedule this new block to be inserted
                blocks_to_insert.append((idx + 1, second_block))
                
                # Don't process more lines in this block, move to next block
                break
    
    # Insert all new blocks (in reverse order to maintain indices)
    for offset, (insert_idx, new_block) in enumerate(sorted(blocks_to_insert, reverse=True)):
        page["blocks"].insert(insert_idx, new_block)
        logger.info(f"Inserted new paragraph block at index {insert_idx}")
    
    logger.info(f"History paragraph breaks complete: split {len(blocks_to_insert)} blocks")


def apply_chapter_one_world_adjustments(section_data: Dict) -> None:
    """
    Apply all adjustments for Chapter One: The World of Athas
    """
    logger.info("=== apply_chapter_one_world_adjustments called ===")
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section data")
        return
    
    logger.info(f"Chapter One: The World of Athas has {len(pages)} pages")
    
    # The History section is on pages 3-4 (0-indexed)
    # Apply paragraph breaking to those pages
    for page_idx in [3, 4]:
        if page_idx < len(pages):
            logger.info(f"Applying History paragraph breaks to page {page_idx}")
            force_history_paragraph_breaks(pages[page_idx])
        else:
            logger.warning(f"Page {page_idx} not found in section")
    
    logger.info("=== Chapter One: The World of Athas adjustments complete ===")

