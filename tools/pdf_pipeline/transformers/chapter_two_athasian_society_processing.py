"""
Chapter Two: Athasian Society PDF Processing

Handles extraction of content that spans page breaks in the merchant houses section.
"""

import logging

logger = logging.getLogger(__name__)


def _fix_merchant_code_content(section_data: dict) -> None:
    """
    Fix The Merchant Code section content on page 127.
    
    Problem: Page 127 has content in both columns at similar y-positions:
    - RIGHT column (y=250-650): Regular agents, Hirelings, The Merchant Code + content
    - LEFT column (y=407-650): Employment Terms, Family members, Senior agents
    
    The standard 2-column layout reads left-before-right, causing the right
    column content to be processed out of order or skipped.
    
    Solution: Mark the right column blocks on page 127 (y=250-650, x>300) to be
    processed BEFORE the left column blocks at the same y-range.
    """
    logger.info("Fixing Merchant Code content extraction on page 127")
    
    pages = section_data.get("pages", [])
    
    # Find page 127
    page_127 = None
    page_127_idx = None
    
    for idx, page in enumerate(pages):
        page_num = page.get("page_number")
        if page_num == 127:
            page_127 = page
            page_127_idx = idx
            break
    
    if not page_127:
        logger.warning("Could not find page 127 for Merchant Code processing")
        return
    
    logger.info(f"Found page 127 at index {page_127_idx}")
    
    # Identify ALL blocks in right and left columns
    # Page 127 has content that needs special ordering:
    # - Right column (x > 300): Regular agents, Hirelings, The Merchant Code + all its content
    # - Left column (x < 300): Employment Terms, Family members, Senior agents
    #
    # We need to process ALL right column blocks before ANY left column blocks
    right_col_blocks = []
    left_col_blocks = []
    blocks = page_127.get("blocks", [])
    
    for block_idx, block in enumerate(blocks):
        bbox = block.get("bbox", [])
        if not bbox or len(bbox) < 4:
            continue
        
        x_center = (bbox[0] + bbox[2]) / 2
        y_top = bbox[1]
        
        # Skip page number and other very low y-values
        if y_top > 700:
            continue
        
        # Determine which column this block belongs to
        if x_center > 300:
            # Right column
            right_col_blocks.append((block_idx, y_top, block))
            
            # Log what we found
            first_text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    first_text += span.get("text", "")[:50]
                if first_text:
                    break
            
            logger.info(f"Right column block {block_idx} at y={y_top:.1f}: {first_text}...")
        else:
            # Left column - but only reorder blocks in the overlapping y-range
            # where content from both columns might be interleaved
            # The right column starts at y=250 (Regular agents), so only reorder
            # left column blocks that are >= 400 (where Employment Terms starts)
            if y_top >= 400:
                left_col_blocks.append((block_idx, y_top, block))
                
                first_text = ""
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        first_text += span.get("text", "")[:50]
                    if first_text:
                        break
                
                logger.info(f"Left column block {block_idx} at y={y_top:.1f}: {first_text}...")
    
    if not right_col_blocks:
        logger.warning("No right column blocks found")
        return
    
    # Sort by y-position
    right_col_blocks.sort(key=lambda x: x[1])
    left_col_blocks.sort(key=lambda x: x[1])
    
    logger.info(f"Found {len(right_col_blocks)} right column blocks, {len(left_col_blocks)} left column blocks to reorder")
    
    # Strategy: Physically reorder the blocks in the page data structure
    # This is more reliable than marking with __force_sequential_order
    #
    # Create new block list: right column first, then left column, then everything else
    new_blocks = []
    reordered_indices = set()
    
    # Add right column blocks first (in y-order)
    for block_idx, y_pos, block in right_col_blocks:
        new_blocks.append(block)
        reordered_indices.add(block_idx)
        logger.info(f"Added right col block {block_idx} (y={y_pos:.1f}) to position {len(new_blocks)-1}")
    
    # Add left column blocks after right column (in y-order)
    for block_idx, y_pos, block in left_col_blocks:
        new_blocks.append(block)
        reordered_indices.add(block_idx)
        logger.info(f"Added left col block {block_idx} (y={y_pos:.1f}) to position {len(new_blocks)-1}")
    
    # Add any remaining blocks that weren't reordered (preserve original order)
    for block_idx, block in enumerate(blocks):
        if block_idx not in reordered_indices:
            new_blocks.append(block)
    
    # Replace the page's block list with our reordered version
    page_127["blocks"] = new_blocks
    logger.info(f"Reordered page 127 blocks: {len(new_blocks)} total blocks")


def apply_chapter_two_athasian_society_adjustments(section_data: dict) -> None:
    """
    Apply all Chapter Two: Athasian Society specific adjustments.
    
    Args:
        section_data: The section data dictionary containing pages to process.
    """
    logger.info("Applying Chapter Two: Athasian Society adjustments")
    
    # Fix The Merchant Code section content extraction
    _fix_merchant_code_content(section_data)
    
    logger.info("Chapter Two: Athasian Society adjustments complete")

