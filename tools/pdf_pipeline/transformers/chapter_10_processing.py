"""Chapter 10 Processing - Treasure

This module handles extraction and formatting for Chapter 10 (Treasure).
Key responsibilities:
- Merge split paragraphs across page boundaries
- Mark headers as appropriate levels (H2, etc.)
- Extract and format the Lair Treasures table (7 columns x 10 rows)
"""

import logging
from typing import Dict

# Import functions from chapter_10 sub-modules
from .chapter_10.common import (
    normalize_plain_text,
    is_header_block,
    merge_paragraph_fragments,
)
from .chapter_10.tables import (
    extract_lair_treasures_table,
    extract_individual_treasures_table,
    extract_gem_table,
)

logger = logging.getLogger(__name__)


def apply_chapter_10_adjustments(section_data: dict) -> None:
    """Apply all Chapter 10 specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    logger.info("=" * 60)
    logger.info("CHAPTER 10 ADJUSTMENTS CALLED!")
    logger.info("=" * 60)
    logger.info("Applying Chapter 10 adjustments")
    
    # Merge split paragraphs
    merge_paragraph_fragments(
        section_data,
        "Since Athas is a metal-poor",
        "priate for coins found"
    )
    
    # Extract and format the Lair Treasures table
    extract_lair_treasures_table(section_data)
    
    # Extract and format the Individual and Small Lair Treasures table
    extract_individual_treasures_table(section_data)
    
    # Extract and format the Gem Table
    extract_gem_table(section_data)
    
    # Mark paragraph breaks in the Coins section
    _mark_coins_paragraph_breaks(section_data)
    
    # Mark paragraph breaks in the Potions section (BEFORE magical items to avoid index issues)
    _mark_potions_paragraph_breaks(section_data)
    
    # Mark paragraph breaks in the Magical Items section
    _mark_magical_items_paragraph_breaks(section_data)
    
    # Mark New Magical Items section items as H2 headers
    _mark_new_magical_items_headers(section_data)
    
    logger.info("Chapter 10 adjustments complete")


def _mark_coins_paragraph_breaks(section_data: dict) -> None:
    """Mark lines in the Coins section that should start new paragraphs.
    
    The Coins section should have 4 paragraphs with breaks at:
    1. "Because metal coins..." (first paragraph)
    2. "No platinum or electrum..."
    3. "Bits are one-tenth..."
    4. "Ceramic, silver, and gold..."
    """
    found_coins_header = False
    
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            # Check if this is the Coins header
            text = normalize_plain_text(block)
            if text.strip() == "Coins":
                found_coins_header = True
                logger.debug("Found Coins header")
                continue
            
            # The next block after Coins header contains the content
            if found_coins_header:
                # Check if this block contains "No platinum" text
                if "No platinum" in text:
                    logger.info("Found Coins content block, marking paragraph breaks")
                    
                    # Mark lines that should start new paragraphs
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        line_text = line_text.strip()
                        
                        # Check if this line starts a new paragraph
                        if line_text.startswith("No platinum"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Bits are"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Ceramic, silver"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                    
                    return  # Only process the first matching block
                    
                # If we hit the Gems header, stop looking
                elif text.strip() == "Gems":
                    logger.debug("Reached Gems header without finding Coins content")
                    return


def _mark_magical_items_paragraph_breaks(section_data: dict) -> None:
    """Mark lines in the Magical Items section that should start new paragraphs.
    
    The Magical Items section should have 5 paragraphs with breaks at:
    1. First paragraph: "The nature of magical items..." (through "...traditional pantheon of giants.")
    2. "If a Dark Sun DM rolls up..."
    3. "Other magical items in the DMG..."
    4. "A final group of items..."
    5. "The following items are changed..." ending with "campaigns:"
    
    Followed by a list of 9 items in "name: description" format, each in its own paragraph.
    """
    logger.info("Processing Magical Items section")
    found_magical_items_header = False
    found_following_items = False
    
    # List of all 9 items to look for (each starts with a space/bullet)
    item_names = [
        "Potion of Giant Control",
        "Potion of Giant Strength",
        "Potion of Undead Control",
        "Rod of Resurrection",
        "Boots of Varied Tracks",
        "Candle of Invocation",
        "Deck of Illusions",
        "Figurines of Wondrous Power",
        "Necklace of Prayer Beads"
    ]
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            # Check if this is the Magical Items header
            text = normalize_plain_text(block)
            if "Magical Items" == text.strip():
                found_magical_items_header = True
                logger.debug("Found Magical Items header")
                continue
            
            # Process blocks after the Magical Items header
            if found_magical_items_header:
                # Debug: log every block we're checking
                if page_idx >= 1 and block_idx < 5:  # Only log first few blocks of pages after header
                    logger.info(f"🔍 Checking page {page_idx}, block {block_idx}: {text[:50]}...")
                
                # Check for paragraph breaks in the main text
                if "If a Dark Sun" in text or "Other magical items" in text or "A final group" in text or "The following items" in text:
                    logger.info("Found Magical Items content block, marking paragraph breaks")
                    
                    # Mark lines that should start new paragraphs
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        line_text = line_text.strip()
                        
                        # Check if this line starts a new paragraph
                        if line_text.startswith("If a Dark Sun"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Other magical items"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("A final group"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("The following items"):
                            line["__force_line_break"] = True
                            found_following_items = True
                            logger.debug(f"Marked paragraph break at: {line_text[:40]}")
                
                # Check if we've found "The following items" - now we need to collect and parse the list
                if found_following_items and not found_magical_items_header:
                    continue
                    
                # Check if this block contains "campaigns:" - that's where the list starts
                if "campaigns:" in text:
                    logger.info("Found 'campaigns:' - starting list extraction")
                    # Extract the complete list across all subsequent blocks
                    _extract_magical_items_list(section_data, page_idx, block_idx, item_names)
                    return
                    
                # If we hit the Potions header, stop looking
                if text.strip() == "Potions":
                    logger.debug("Reached Potions header")
                    return


def _mark_potions_paragraph_breaks(section_data: dict) -> None:
    """Mark lines in the Potions section that should start new paragraphs.
    
    The Potions section should have multiple paragraphs with breaks at:
    1. First paragraph: intro text before "Any juicy"
    2. "Any juicy berry or fruit..." (includes "type of fruit chosen" and "Once the skin")
    3. "Whereas normal fruits..."
    4. "The entire fruit must be eaten..."
    5. "Potion fruits cannot be identified..."
    6. "Potion fruits can be combined..." (second occurrence)
    7. "Fruits may be enchanted..." paragraph before Magical Enchantment
    
    H3 Headers:
    - "Magical Enchantment:" should be marked as H3
    - "Botanical Enchantment:" should be marked as H3
    
    Botanical Enchantment paragraph breaks:
    - "The original potion fruit..." (first paragraph)
    - "If a permanency spell..." (second paragraph)
    - "Botanical enchantment is somewhat..." (third paragraph)
    """
    print("🔵 _mark_potions_paragraph_breaks called!")
    logger.info("Processing Potions section")
    found_potions_header = False
    
    # STEP 0: Reorder blocks to fix 2-column reading order issue
    # The problem: "Magical Enchantment" (block 48, X=320, Y=460) is in the RIGHT column
    # at the same Y-coordinate as block 17 (Y=461), but it should appear AFTER
    # the "Potions" header (block 18, Y=502) which is in the LEFT column.
    print(f"🔄 Step 0: Reordering blocks to fix 2-column reading order...")
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        
        # Find "Potions" header and enchantment blocks
        potions_header_idx = None
        potions_header_y = None
        magical_enchantment_idx = None
        magical_enchantment_y = None
        botanical_enchantment_idx = None
        last_potions_content_idx = None
        
        for block_idx in range(len(blocks)):
            block = blocks[block_idx]
            if block.get("type") == "text":
                text = normalize_plain_text(block)
                bbox = block.get("bbox", [0, 0, 0, 0])
                x = bbox[0]
                y = bbox[1]
                
                if text.strip() == "Potions":
                    potions_header_idx = block_idx
                    potions_header_y = y
                    print(f"  🎯 Found 'Potions' header at block {block_idx}, Y={y:.2f}")
                elif text.strip().startswith("Magical Enchantment:"):
                    magical_enchantment_idx = block_idx
                    magical_enchantment_y = y
                    print(f"  🎯 Found 'Magical Enchantment' at block {block_idx} (X={x:.2f}, Y={y:.2f})")
                elif text.strip().startswith("Botanical Enchantment:"):
                    botanical_enchantment_idx = block_idx
                    print(f"  🎯 Found 'Botanical Enchantment' at block {block_idx} (X={x:.2f}, Y={y:.2f})")
                elif "Fruits may be enchanted" in text:
                    # This is the last line before the enchantment blocks
                    # Actually, we need the NEXT block after this one
                    last_potions_content_idx = block_idx + 1  # Use block 47 (the continuation)
                    print(f"  🎯 Found 'Fruits may be enchanted' at block {block_idx}, using {last_potions_content_idx} as insertion point")
        
        # If we found all the blocks, reorder them
        if (potions_header_idx is not None and magical_enchantment_idx is not None and 
            botanical_enchantment_idx is not None and last_potions_content_idx is not None):
            
            print(f"  ✅ Found all required blocks:")
            print(f"     Potions header: {potions_header_idx} (Y={potions_header_y:.2f})")
            print(f"     Magical Enchantment: {magical_enchantment_idx} (Y={magical_enchantment_y:.2f})")
            print(f"     Botanical Enchantment: {botanical_enchantment_idx}")
            print(f"     Last Potions content: {last_potions_content_idx}")
            
            # Check if Magical Enchantment appears ABOVE Potions header in the visual layout (wrong order)
            # Use Y-coordinates: lower Y = higher on the page
            if magical_enchantment_y < potions_header_y:
                print(f"  ⚠️ Magical Enchantment (Y={magical_enchantment_y:.2f}) appears ABOVE Potions (Y={potions_header_y:.2f}) in the visual layout!")
                print(f"  🔧 Reordering blocks to fix reading order...")
                
                # Extract blocks that need to be moved (enchantment blocks and their content)
                # Find all blocks from Magical Enchantment through Botanical Enchantment + content
                # We need to find the block AFTER "botanical enchantment is the process..." which is
                # "The original potion fruit"
                end_enchantment_idx = botanical_enchantment_idx
                for idx in range(botanical_enchantment_idx + 1, min(botanical_enchantment_idx + 5, len(blocks))):
                    b = blocks[idx]
                    if b.get("type") == "text":
                        t = normalize_plain_text(b)
                        if "The original potion fruit" in t:
                            end_enchantment_idx = idx - 1  # Stop before "The original"
                            break
                        elif t.strip() and not t.strip().startswith("cleric,") and not t.strip().startswith("tanical"):
                            end_enchantment_idx = idx - 1
                            break
                
                print(f"  📦 Moving blocks {magical_enchantment_idx}-{end_enchantment_idx} to after block {last_potions_content_idx}")
                
                # Extract the blocks to move
                blocks_to_move = blocks[magical_enchantment_idx:end_enchantment_idx + 1]
                
                # Mark the entire page to use single-column rendering to preserve block order
                # This prevents Y-coordinate-based sorting from breaking the logical reading order
                page["__force_single_column"] = True
                print(f"  🎯 Marked page for single-column rendering to preserve block order")
                
                # Remove them from their current position
                for _ in range(len(blocks_to_move)):
                    blocks.pop(magical_enchantment_idx)
                
                # Adjust insertion point (since we removed blocks before it)
                if last_potions_content_idx > magical_enchantment_idx:
                    last_potions_content_idx -= len(blocks_to_move)
                
                # Insert them after the last Potions content
                insert_pos = last_potions_content_idx + 1
                for i, block in enumerate(blocks_to_move):
                    blocks.insert(insert_pos + i, block)
                
                print(f"  ✅ Reordered {len(blocks_to_move)} blocks and marked for sequential rendering")
    
    # First pass: merge blocks that belong together
    # - All blocks between "Any juicy" and "Any potion" belong with "Any juicy"
    # - "Once the skin" and following blocks belong with "Any potion"
    print(f"🔍 First pass: searching through {len(section_data.get('pages', []))} pages")
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        print(f"  Page {page_idx}: {len(blocks)} blocks")
        
        # Find the blocks we need
        any_juicy_block_idx = None
        any_potion_block_idx = None
        
        for block_idx in range(len(blocks)):
            block = blocks[block_idx]
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            
            # Find the "Any juicy" block
            if "Any juicy berry" in text:
                any_juicy_block_idx = block_idx
                print(f"  📍 Found 'Any juicy' block at index {block_idx}")
            
            # Find the "Any potion" block
            if "Any potion listed" in text:
                any_potion_block_idx = block_idx
                print(f"  📍 Found 'Any potion' block at index {block_idx}")
                break  # Stop searching once we find "Any potion"
        
        # Merge all blocks between "Any juicy" and "Any potion" into "Any juicy"
        if any_juicy_block_idx is not None and any_potion_block_idx is not None:
            print(f"  🔧 Merging blocks {any_juicy_block_idx+1} to {any_potion_block_idx-1} into 'Any juicy'...")
            any_juicy_block = blocks[any_juicy_block_idx]
            
            # Get Y-coordinate for continuity
            if any_juicy_block.get("lines"):
                last_line = any_juicy_block["lines"][-1]
                base_y = last_line.get("bbox", [0, 0, 0, 0])[1]
                line_height = 13.0
                
                # Merge all blocks between juicy and potion
                blocks_to_remove = []
                for merge_idx in range(any_juicy_block_idx + 1, any_potion_block_idx):
                    merge_block = blocks[merge_idx]
                    if merge_block.get("type") == "text":
                        # Adjust Y-coordinates
                        for line in merge_block["lines"]:
                            base_y += line_height
                            old_bbox = line.get("bbox", [0, 0, 0, 0])
                            line["bbox"] = [old_bbox[0], base_y, old_bbox[2], base_y + 9]
                        
                        any_juicy_block["lines"].extend(merge_block["lines"])
                        blocks_to_remove.append(merge_idx)
                        print(f"    ✅ Merged block {merge_idx}")
                
                # Remove merged blocks (in reverse order)
                for merge_idx in reversed(blocks_to_remove):
                    blocks.pop(merge_idx)
                    print(f"    ✅ Removed block {merge_idx}")
                    # Adjust any_potion_block_idx since we're removing blocks before it
                    any_potion_block_idx -= 1
        
        # Merge "Once the skin" blocks into "Any potion"
        if any_potion_block_idx is not None:
            # Re-find any_potion_block_idx in case it changed
            for block_idx in range(len(blocks)):
                block = blocks[block_idx]
                if block.get("type") == "text":
                    text = normalize_plain_text(block)
                    if "Any potion listed" in text:
                        any_potion_block_idx = block_idx
                        break
            
            any_potion_block = blocks[any_potion_block_idx]
            
            # Find "Once the skin" and merge it
            for block_idx in range(any_potion_block_idx + 1, min(any_potion_block_idx + 5, len(blocks))):
                block = blocks[block_idx]
                if block.get("type") == "text":
                    text = normalize_plain_text(block)
                    if text.strip().startswith("Once the skin"):
                        print(f"  🔧 Merging 'Once the skin' block {block_idx} into 'Any potion' block {any_potion_block_idx}...")
                        
                        # Get Y-coordinate
                        if any_potion_block.get("lines"):
                            last_line = any_potion_block["lines"][-1]
                            base_y = last_line.get("bbox", [0, 0, 0, 0])[1]
                            line_height = 13.0
                            
                            # Adjust Y-coordinates
                            for line in block["lines"]:
                                base_y += line_height
                                old_bbox = line.get("bbox", [0, 0, 0, 0])
                                line["bbox"] = [old_bbox[0], base_y, old_bbox[2], base_y + 9]
                            
                            any_potion_block["lines"].extend(block["lines"])
                            blocks.pop(block_idx)
                            print(f"    ✅ Merged and removed block {block_idx}")
                        break
    
    # Second pass: mark paragraph breaks at specific phrases and set header levels
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            # Check if this is the Potions header
            text = normalize_plain_text(block)
            if "Potions" == text.strip():
                found_potions_header = True
                logger.debug("Found Potions header")
                continue
            
            # Process blocks after the Potions header
            if found_potions_header:
                # Mark "Magical Enchantment:" as H3 header
                if text.strip().startswith("Magical Enchantment:"):
                    # Create a new block for the paragraph text after the header
                    # The line contains both "Magical Enchantment: " and "Any wizard, cleric, or"
                    if block.get("lines") and len(block["lines"]) > 0:
                        line = block["lines"][0]
                        spans = line.get("spans", [])
                        
                        # Find the header span and non-header spans
                        header_span = None
                        text_spans = []
                        for span in spans:
                            if span.get("text", "").strip() == "Magical Enchantment:":
                                header_span = span
                            else:
                                text_spans.append(span)
                        
                        if text_spans:
                            # Create a new block for the paragraph text
                            new_block = {
                                "type": "text",
                                "bbox": block["bbox"].copy() if "bbox" in block else [0, 0, 0, 0],
                                "lines": [{
                                    "bbox": line["bbox"].copy() if "bbox" in line else [0, 0, 0, 0],
                                    "spans": text_spans
                                }]
                            }
                            # Insert the new block right after the current block
                            page["blocks"].insert(block_idx + 1, new_block)
                            logger.debug(f"  Created new block with paragraph text: '{text_spans[0].get('text', '')}'")
                    
                    # Mark the current block as a section header
                    block["__section_header"] = True
                    block["__header_text"] = "Magical Enchantment:"
                    block["__header_level"] = 3  # H3
                    logger.info("✅ Marked 'Magical Enchantment:' as H3 header and created paragraph block")
                    continue
                
                # Mark "Botanical Enchantment:" as H3 header
                if text.strip().startswith("Botanical Enchantment:"):
                    # Create a new block for the paragraph text after the header
                    # The line contains both "Botanical Enchantment: " and "Any wizard, ranger,"
                    if block.get("lines") and len(block["lines"]) > 0:
                        line = block["lines"][0]
                        spans = line.get("spans", [])
                        
                        # Find the header span and non-header spans
                        header_span = None
                        text_spans = []
                        for span in spans:
                            if span.get("text", "").strip() == "Botanical Enchantment:":
                                header_span = span
                            else:
                                text_spans.append(span)
                        
                        if text_spans:
                            # Create a new block for the paragraph text
                            new_block = {
                                "type": "text",
                                "bbox": block["bbox"].copy() if "bbox" in block else [0, 0, 0, 0],
                                "lines": [{
                                    "bbox": line["bbox"].copy() if "bbox" in line else [0, 0, 0, 0],
                                    "spans": text_spans
                                }]
                            }
                            # Insert the new block right after the current block
                            page["blocks"].insert(block_idx + 1, new_block)
                            logger.debug(f"  Created new block with paragraph text: '{text_spans[0].get('text', '')}'")
                    
                    # Mark the current block as a section header
                    block["__section_header"] = True
                    block["__header_text"] = "Botanical Enchantment:"
                    block["__header_level"] = 3  # H3
                    logger.info("✅ Marked 'Botanical Enchantment:' as H3 header and created paragraph block")
                    continue
                
                # Check for paragraph break phrases in other blocks
                needs_marking = (
                    "Any juicy" in text or
                    "Whereas normal" in text or
                    "The entire fruit" in text or
                    "Potion fruits" in text or
                    "Fruits may" in text or
                    "The original potion fruit" in text or
                    "If a permanency" in text or
                    "Botanical enchantment is somewhat" in text
                )
                
                if needs_marking:
                    logger.info(f"Found Potions content block on page {page_idx}, marking paragraph breaks")
                    
                    # Mark lines that should start new paragraphs
                    for line in block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        line_text = line_text.strip()
                        
                        # Check if this line starts a new paragraph
                        if line_text.startswith("Any juicy"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Whereas normal"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("The entire fruit"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Potion fruits"):
                            # Mark BOTH occurrences of "Potion fruits"
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Fruits may"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("The original potion fruit"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("If a permanency"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                        elif line_text.startswith("Botanical enchantment is somewhat"):
                            line["__force_line_break"] = True
                            logger.debug(f"✅ Marked paragraph break at: {line_text[:40]}")
                
                # If we hit the "New Magical Items" header, stop looking
                if "New Magical Items" in text:
                    logger.debug("Reached New Magical Items header")
                    return


def _extract_magical_items_list(section_data: dict, start_page_idx: int, start_block_idx: int, item_names: list) -> None:
    """Extract the magical items list and create properly formatted blocks.
    
    The list starts with "campaigns:" and continues until "Potions" header.
    Each item starts with " ItemName:" (space + name + colon).
    """
    logger.info("Extracting magical items list")
    
    # Collect all text from blocks until we hit "Potions"
    all_text = ""
    blocks_to_skip = []
    
    # Start from the current block
    for page_idx in range(start_page_idx, len(section_data.get("pages", []))):
        page = section_data["pages"][page_idx]
        start_idx = start_block_idx if page_idx == start_page_idx else 0
        
        for block_idx in range(start_idx, len(page.get("blocks", []))):
            block = page["blocks"][block_idx]
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            
            # Stop at Potions header
            if text.strip() == "Potions":
                logger.info("Reached end of list at Potions header")
                break
            
            # Add this block's text
            all_text += text + " "
            blocks_to_skip.append((page_idx, block_idx))
        else:
            continue
        break
    
    logger.debug(f"Collected text: {all_text[:200]}...")
    
    # Parse out "campaigns:" as a separate paragraph
    if "campaigns:" in all_text:
        campaigns_idx = all_text.find("campaigns:")
        campaigns_text = all_text[:campaigns_idx + len("campaigns:")]
        remaining_text = all_text[campaigns_idx + len("campaigns:"):]
    else:
        campaigns_text = ""
        remaining_text = all_text
    
    # Parse each item from the remaining text
    items = []
    for item_name in item_names:
        # Look for " ItemName:" (space + name + colon)
        pattern = f" {item_name}:"
        if pattern in remaining_text:
            start_idx = remaining_text.find(pattern)
            
            # Find where this item ends (either at next item or end of text)
            end_idx = len(remaining_text)
            for next_item in item_names:
                if next_item == item_name:
                    continue
                next_pattern = f" {next_item}:"
                if next_pattern in remaining_text[start_idx + 1:]:
                    next_idx = remaining_text.find(next_pattern, start_idx + 1)
                    if next_idx < end_idx:
                        end_idx = next_idx
            
            # Extract this item's text
            item_text = remaining_text[start_idx:end_idx].strip()
            
            # Clean up the text (remove line breaks, extra spaces)
            item_text = " ".join(item_text.split())
            
            items.append({
                "name": item_name,
                "text": item_text
            })
            logger.info(f"Extracted item: {item_name} ({len(item_text)} chars)")
        else:
            logger.warning(f"Could not find {item_name} in text")
    
    # Mark all original blocks to skip
    for page_idx, block_idx in blocks_to_skip:
        section_data["pages"][page_idx]["blocks"][block_idx]["__skip_render"] = True
    
    # Create new blocks for campaigns and each item
    target_page_idx = start_page_idx
    target_block_idx = start_block_idx
    
    # Get a reference bbox from the first block on this page to use for positioning
    ref_bbox = [100, 100, 500, 120]  # Default bbox
    if section_data["pages"][target_page_idx]["blocks"]:
        first_block = section_data["pages"][target_page_idx]["blocks"][0]
        if "bbox" in first_block:
            ref_bbox = first_block["bbox"][:] # Copy it
    
    # Insert "campaigns:" block
    if campaigns_text:
        campaigns_block = {
            "type": "text",
            "bbox": ref_bbox,  # Use reference bbox instead of [0,0,0,0]
            "lines": [{
                "spans": [{"text": campaigns_text.strip()}],
                "bbox": ref_bbox
            }],
            "__inserted_campaigns": True
        }
        section_data["pages"][target_page_idx]["blocks"].insert(target_block_idx, campaigns_block)
        target_block_idx += 1
        logger.info("Inserted 'campaigns:' block")
    
    # Insert blocks for each item
    for item in items:
        item_block = {
            "type": "text",
            "bbox": ref_bbox,  # Use reference bbox instead of [0,0,0,0]
            "lines": [{
                "spans": [{"text": item["text"]}],
                "bbox": ref_bbox
            }],
            "__magical_item_entry": item["name"],
            "__force_paragraph_break": True
        }
        section_data["pages"][target_page_idx]["blocks"].insert(target_block_idx, item_block)
        target_block_idx += 1
        logger.info(f"Inserted block for {item['name']}")
    
    logger.info(f"Insertion complete! Inserted {len(items) + (1 if campaigns_text else 0)} blocks")


def _mark_new_magical_items_headers(section_data: dict) -> None:
    """Mark headers in the New Magical Items section as H2.
    
    The New Magical Items section contains headers for specific items that should be H2:
    - Amulet of Psionic Interference
    - Oil of Feather Falling
    - Ring of Life
    - Rod of Divining
    
    Each of these is followed by "XP Value: #" and then a paragraph of text.
    The item name and content are in the same block, so we need to split them.
    """
    logger.info("Processing New Magical Items section headers")
    
    # List of item names that should be H2 headers
    item_names = [
        "Amulet of Psionic Interference",
        "Oil of Feather Falling",
        "Ring of Life",
        "Rod of Divining"
    ]
    
    found_new_magical_items = False
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        # We need to process blocks and potentially insert new ones, so we iterate backwards
        # to avoid index issues when inserting
        blocks = page.get("blocks", [])
        
        # First pass: find blocks that need splitting
        blocks_to_process = []
        for block_idx in range(len(blocks)):
            block = blocks[block_idx]
            if block.get("type") != "text":
                continue
            
            # Get block text
            text = normalize_plain_text(block)
            
            # Check if we've reached the New Magical Items section
            if "New Magical Items" == text.strip():
                found_new_magical_items = True
                logger.debug("Found New Magical Items header")
                continue
            
            # Process blocks after the New Magical Items header
            if found_new_magical_items:
                # Check if this block contains one of the item names
                for item_name in item_names:
                    if text.strip().startswith(item_name):
                        logger.info(f"✅ Found block containing '{item_name}'")
                        blocks_to_process.append((block_idx, item_name))
                        break
        
        # Second pass: split the blocks (in reverse order to avoid index issues)
        for block_idx, item_name in reversed(blocks_to_process):
            block = blocks[block_idx]
            text = normalize_plain_text(block)
            
            logger.info(f"Splitting block {block_idx} with item '{item_name}'")
            logger.debug(f"  Original text: {text[:100]}...")
            
            # Find where the item name ends
            # The format is: "Item Name XP Value: ### Description text..."
            xp_value_pos = text.find("XP Value:")
            if xp_value_pos == -1:
                logger.warning(f"Could not find 'XP Value:' in block for {item_name}")
                continue
            
            # Split the text at "XP Value:"
            header_text = text[:xp_value_pos].strip()
            remaining_text = text[xp_value_pos:].strip()
            
            # Now split the remaining text into "XP Value: #" and the description
            # Find where the XP Value line ends (look for common starting patterns)
            description_patterns = [
                "This item scrambles",
                "Crushing such a fruit",
                "This item protects",
                "This item is a small"
            ]
            
            xp_value_text = remaining_text
            description_text = ""
            
            for pattern in description_patterns:
                pattern_pos = remaining_text.find(pattern)
                if pattern_pos != -1:
                    xp_value_text = remaining_text[:pattern_pos].strip()
                    description_text = remaining_text[pattern_pos:].strip()
                    break
            
            logger.debug(f"  Header: {header_text}")
            logger.debug(f"  XP Value: {xp_value_text[:40]}...")
            logger.debug(f"  Description: {description_text[:40]}...")
            
            # Create a header block with orange color and H2 size
            # The orange color (#ca5804) will make it be recognized as a header
            # The size will be used to determine it's an H2 (not H1)
            header_block = {
                "type": "text",
                "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0],
                "lines": [{
                    "spans": [{
                        "text": header_text,
                        "color": "#ca5804",  # Orange color for headers
                        "size": 10.8,  # H2 font size (smaller than H1)
                        "font": "BCDEEE+HelveticaNeueLTStd-Bd",  # Bold font
                        "flags": 20  # Bold flag
                    }],
                    "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0]
                }],
                "__section_header": True,
                "__header_text": header_text,
                "__header_level": 2  # H2
            }
            
            # Create XP Value block
            xp_value_block = {
                "type": "text",
                "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0],
                "lines": [{
                    "spans": [{"text": xp_value_text}],
                    "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0]
                }]
            }
            
            # Create description block
            description_block = {
                "type": "text",
                "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0],
                "lines": [{
                    "spans": [{"text": description_text}],
                    "bbox": block.get("bbox", [0, 0, 0, 0]).copy() if "bbox" in block else [0, 0, 0, 0]
                }]
            }
            
            # Replace the original block with the header block
            blocks[block_idx] = header_block
            
            # Insert the XP Value block right after the header
            blocks.insert(block_idx + 1, xp_value_block)
            
            # Insert the description block after the XP Value block
            blocks.insert(block_idx + 2, description_block)
            
            logger.info(f"✅ Split block {block_idx} into header, XP value, and description blocks")
    
    logger.info("Completed marking New Magical Items headers")

