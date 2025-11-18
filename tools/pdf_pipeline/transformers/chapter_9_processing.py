"""
Chapter 9 Processing - Arena Combats
This module handles header level adjustments for the Arena Combats section.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Headers that should be H3 (subheaders under Arena Combats)
ARENA_GAME_TYPES_H3 = [
    "Games:",
    "Matinee:",
    "Grudge Match:",
    "Trial by Combat:",
    "Matched Pairs:",
    "Bestial Combat:",
    "Test of Champions:",
    "Advanced Games:",
]

# Headers that should be H2
ARENA_SECTIONS_H2 = [
    "Stables:",
    "Wagering:",
    "Trading of Gladiators:",
]

# Headers in "Turning and Controlling Undead" section that should be H2
TURNING_UNDEAD_SECTIONS_H2 = [
    "Turning Undead:",
    "Commanding Undead:",
]

# Headers that should be H2 (combat-related sections)
COMBAT_SECTIONS_H2 = [
    "Followers",
    "Followers:",  # Also check with colon
]

# Headers in "Piecemeal Armor" section that should be H2
PIECEMEAL_ARMOR_SECTIONS_H2 = [
    "Important Considerations",
]

# Headers in "Piecemeal Armor" section that should be H3
PIECEMEAL_ARMOR_SECTIONS_H3 = [
    "Bonus to AC Per Type of Piece",
]

# Headers that are table column headers and should be removed/skipped
PIECEMEAL_ARMOR_TABLE_HEADERS = [
    "Armor Type",
    "Full Suit",
    "Breast Plate",
    "Two Arms",
    "One Arm",
    "Two Legs",
    "One Leg",
]


def _merge_hovering_on_deaths_door_header(section_data: Dict) -> None:
    """
    Merge "Hovering on Deaths Door" and "(Optional Rule)" into a single H2 header.
    These are currently two separate lines but should be one header.
    """
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            for line_idx in range(len(lines) - 1):  # Check all but last line
                current_line = lines[line_idx]
                next_line = lines[line_idx + 1]
                
                # Get text from current and next lines
                current_spans = current_line.get("spans", [])
                next_spans = next_line.get("spans", [])
                
                if not current_spans or not next_spans:
                    continue
                
                current_text = current_spans[0].get("text", "").strip()
                next_text = next_spans[0].get("text", "").strip()
                
                # Check if we found the pattern (handle various apostrophe types: \x92, ', or no apostrophe)
                # The source PDF contains \x92 (RIGHT SINGLE QUOTATION MARK)
                if (("Hovering on Death" in current_text and "Door" in current_text) and 
                    next_text == "(Optional Rule)"):
                    logger.info(f"Found '{current_text}' followed by '(Optional Rule)' at page {page_idx}, block {block_idx}")
                    
                    # Merge the text in the first span (preserve the original text)
                    current_spans[0]["text"] = f"{current_text} (Optional Rule)"
                    
                    # Mark as H2
                    current_spans[0]["size"] = 14.88
                    current_spans[0]["header_level"] = 2
                    
                    # Remove the second line
                    lines.pop(line_idx + 1)
                    
                    logger.debug("Merged into single H2 header")
                    break


def _adjust_header_levels(section_data: Dict) -> None:
    """
    Adjust header levels in the Arena Combats section and Turning Undead section.
    - Games through Advanced Games should be H3
    - Stables, Wagering, Trading of Gladiators should be H2
    - Turning Undead, Commanding Undead should be H2
    - Followers should be H2
    - Important Considerations should be H2
    - Bonus to AC Per Type of Piece should be H3
    - Table column headers (Armor Type, Full Suit, etc.) should be skipped
    """
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                for span_idx, span in enumerate(spans):
                    text = span.get("text", "").strip()
                    
                    # Check if this span is one of the game type headers that should be H3
                    if text in ARENA_GAME_TYPES_H3:
                        # Mark as H3 by setting size smaller than H2
                        # H2 typically uses size 14.88, H3 should use something smaller like 12
                        original_size = span.get("size", 14.88)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Adjusting '{text}' from size {original_size} to H3 size (12)")
                        span["size"] = 12.0
                        span["header_level"] = 3
                    
                    # Check if this span is one of the H2 headers (Arena sections)
                    elif text in ARENA_SECTIONS_H2:
                        # Ensure it's marked as H2
                        original_size = span.get("size", 14.88)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Ensuring '{text}' is H2 with size {original_size}")
                        span["size"] = 14.88
                        span["header_level"] = 2
                    
                    # Check if this span is one of the Turning Undead H2 headers
                    elif text in TURNING_UNDEAD_SECTIONS_H2:
                        # Ensure it's marked as H2
                        original_size = span.get("size", 14.88)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Ensuring '{text}' is H2 with size {original_size}")
                        span["size"] = 14.88
                        span["header_level"] = 2
                    
                    # Check if this span is one of the combat sections that should be H2
                    elif text in COMBAT_SECTIONS_H2:
                        # Ensure it's marked as H2
                        original_size = span.get("size", 14.88)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Ensuring '{text}' is H2 with size {original_size} -> 14.88")
                        span["size"] = 14.88
                        span["header_level"] = 2
                    
                    # Check if this span is one of the piecemeal armor sections that should be H2
                    elif text in PIECEMEAL_ARMOR_SECTIONS_H2:
                        # Ensure it's marked as H2
                        original_size = span.get("size", 14.88)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Ensuring '{text}' is H2 with size {original_size} -> 14.88")
                        span["size"] = 14.88
                        span["header_level"] = 2
                    
                    # Check if this span is one of the piecemeal armor sections that should be H3
                    elif text in PIECEMEAL_ARMOR_SECTIONS_H3:
                        # Ensure it's marked as H3
                        original_size = span.get("size", 12.0)
                        logger.info(f"Page {page_idx}, Block {block_idx}: Ensuring '{text}' is H3 with size {original_size} -> 12.0")
                        span["size"] = 12.0
                        span["header_level"] = 3
                    
                    # Check if this span is a table column header that should be skipped
                    elif text in PIECEMEAL_ARMOR_TABLE_HEADERS:
                        # Mark the block to skip rendering
                        logger.info(f"Page {page_idx}, Block {block_idx}: Marking table column header '{text}' to skip")
                        block["__skip_render"] = True


def _prevent_stables_paragraph_break(section_data: Dict) -> None:
    """
    Prevent "Slaves who have survived" from starting a new paragraph in the Stables section.
    This sentence should continue the paragraph that starts with "Every slave in a stable".
    """
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with "Slaves who have survived", mark it to merge with previous paragraph
            if text.startswith("Slaves who have survived"):
                logger.debug(f"Found 'Slaves who have survived' at page {page_idx}, block {block_idx}")
                
                # Modify the first line to start with lowercase to trigger merge logic
                # Store the original capitalization in a marker
                first_span["__original_text"] = first_span.get("text", "")
                
                # Change the first character to lowercase
                original_text = first_span.get("text", "")
                if original_text and original_text[0].isupper():
                    # Make it lowercase so the merge logic will pick it up
                    modified_text = original_text[0].lower() + original_text[1:]
                    first_span["text"] = modified_text
                    logger.debug(f"Changed first character to lowercase to enable paragraph merge")
                
                break  # Found and processed, no need to check other blocks


def _force_battling_undead_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Battling Undead in Dark Sun" section.
    
    The section should have 4 paragraphs with breaks at:
    1. (intro) "On Athas, undead are still just that..."
    2. "Mindless undead are corpses or skeletal remains..."
    3. "Free-willed undead are usually very powerful creatures..."
    4. "Quite often, free-willed undead have minions..."
    """
    paragraph_starts = [
        "Mindless undead are corpses",
        "Free-willed undead are usually",
        "Quite often, free-willed undead have minions",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with one of our paragraph starts, mark it for a paragraph break
            for para_start in paragraph_starts:
                if text.startswith(para_start):
                    logger.debug(f"Found '{para_start}...' at page {page_idx}, block {block_idx} - marking for paragraph break")
                    block["__force_paragraph_break"] = True
                    break


def _force_turning_undead_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Turning Undead" section.
    
    The "Turning Undead" section should have 2 paragraphs with a break at:
    1. (intro) "A cleric on Athas wishing to turn undead..."
    2. "Turned undead flee as described in the Player's Handbook..."
    """
    paragraph_starts = [
        "Turned undead flee",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with one of our paragraph starts, mark it for a paragraph break
            for para_start in paragraph_starts:
                if text.startswith(para_start):
                    logger.debug(f"Found '{para_start}...' at page {page_idx}, block {block_idx} - marking for paragraph break")
                    block["__force_paragraph_break"] = True
                    break


def _force_waging_wars_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Waging Wars" section.
    
    The section should have 3 paragraphs with breaks at:
    1. (intro) "The sands of Athas have been stained red..."
    2. "Player characters will eventually be called upon..."
    3. "Once player characters must deal with large numbers..."
    """
    paragraph_starts = [
        "Player characters will eventually",
        "Once player characters must deal",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with one of our paragraph starts, mark it for a paragraph break
            for para_start in paragraph_starts:
                if text.startswith(para_start):
                    logger.debug(f"Found '{para_start}...' at page {page_idx}, block {block_idx} - marking for paragraph break")
                    block["__force_paragraph_break"] = True
                    break


def _force_followers_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Followers" section.
    
    The section should have 2 paragraphs with a break at:
    1. (intro) "Though fighters and gladiators automatically gain followers..."
    2. "A warrior's followers almost never arrive with all of their equipment..."
    """
    paragraph_starts = [
        "A warrior's followers almost never",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with one of our paragraph starts, mark it for a paragraph break
            for para_start in paragraph_starts:
                if text.startswith(para_start):
                    logger.debug(f"Found '{para_start}...' at page {page_idx}, block {block_idx} - marking for paragraph break")
                    block["__force_paragraph_break"] = True
                    break


def _force_hovering_on_deaths_door_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Hovering on Death's Door (Optional Rule)" section.
    
    The section should have 6 paragraphs with breaks at:
    1. (intro) "DMs may find that their DARK SUN campaign..."
    2. "Thereafter, he automatically loses 1 hit point each..."
    3. "If the only action is to bind his wounds..."
    4. "If a cure spell of some type is cast upon him..."
    5. "If a heal spell is cast on the character..."
    6. (final) Continues after heal spell paragraph
    """
    paragraph_starts = [
        "Thereafter, he automatically",
        "If the only action",
        "If a",  # Will match "If acure" and "If aheal" (no space in source)
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        blocks_to_add = []  # New blocks to insert (from splits)
        indices_to_remove = []  # Blocks to remove after splitting
        
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check if this block needs to be split
            split_indices = []  # Line indices where we need to split
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                if not spans:
                    continue
                    
                text = spans[0].get("text", "").strip()
                
                for para_start in paragraph_starts:
                    if text.startswith(para_start):
                        if line_idx == 0:
                            # Mark the block for paragraph break
                            logger.info(f"Found '{para_start}...' at page {page_idx}, block {block_idx}, line 0 - marking for paragraph break")
                            block["__force_paragraph_break"] = True
                        else:
                            # Need to split this block at this line
                            logger.info(f"Found '{para_start}...' at page {page_idx}, block {block_idx}, line {line_idx} - will split block")
                            if line_idx not in split_indices:
                                split_indices.append(line_idx)
                        break
            
            # If we need to split this block
            if split_indices:
                split_indices.sort()
                indices_to_remove.append(block_idx)
                
                # Create new blocks from the split
                current_line_idx = 0
                for split_at in split_indices + [len(lines)]:  # Include end of block
                    if current_line_idx < split_at:
                        # Create a block with lines from current_line_idx to split_at
                        new_block = block.copy()
                        new_block["lines"] = lines[current_line_idx:split_at]
                        
                        # Mark splits as paragraph breaks (except the first chunk if it starts at 0)
                        if current_line_idx > 0:
                            new_block["__force_paragraph_break"] = True
                            logger.debug(f"Created split block starting at line {current_line_idx} with __force_paragraph_break")
                        
                        blocks_to_add.append((block_idx, new_block))
                        current_line_idx = split_at
        
        # Apply the splits by removing old blocks and inserting new ones
        # Process in reverse order to maintain indices
        for idx in sorted(indices_to_remove, reverse=True):
            del blocks[idx]
        
        # Insert new blocks at their original positions
        # Sort by index only (first element of tuple)
        for idx, new_block in sorted(blocks_to_add, key=lambda x: x[0]):
            # Adjust index for already-removed blocks
            adjusted_idx = idx - sum(1 for removed_idx in indices_to_remove if removed_idx < idx)
            blocks.insert(adjusted_idx, new_block)


def _force_piecemeal_armor_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Piecemeal Armor" section.
    
    The section should have 3 paragraphs with breaks at:
    1. (intro) "Dark Sun characters seldom (if ever) wear complete suits..."
    2. "Determining the correct Armor Class for someone..."
    3. "No more than one piece of armor may be worn..."
    """
    paragraph_starts = [
        "Determining the correct",
        "No more than",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        blocks_to_add = []  # New blocks to insert (from splits)
        indices_to_remove = []  # Blocks to remove after splitting
        
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check if this block needs to be split
            split_indices = []  # Line indices where we need to split
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                if not spans:
                    continue
                    
                text = spans[0].get("text", "").strip()
                
                for para_start in paragraph_starts:
                    if text.startswith(para_start):
                        if line_idx == 0:
                            # Mark the block for paragraph break
                            logger.info(f"Found '{para_start}...' at page {page_idx}, block {block_idx}, line 0 - marking for paragraph break")
                            block["__force_paragraph_break"] = True
                        else:
                            # Need to split this block at this line
                            # First, move lines before the split to the previous block (if it exists and is text)
                            if block_idx > 0 and blocks[block_idx - 1].get("type") == "text":
                                prev_block = blocks[block_idx - 1]
                                lines_to_move = lines[:line_idx]
                                if lines_to_move:
                                    logger.info(f"Moving {len(lines_to_move)} lines from block {block_idx} to previous block {block_idx-1}")
                                    if "lines" not in prev_block:
                                        prev_block["lines"] = []
                                    prev_block["lines"].extend(lines_to_move)
                            
                            logger.info(f"Found '{para_start}...' at page {page_idx}, block {block_idx}, line {line_idx} - will split block")
                            if line_idx not in split_indices:
                                split_indices.append(line_idx)
                        break
            
            # If we need to split this block
            if split_indices:
                split_indices.sort()
                indices_to_remove.append(block_idx)
                
                # Create new blocks from the split (only from split point onwards)
                for split_at in split_indices:
                    # Create a block with lines from split_at onwards
                    new_block = block.copy()
                    new_block["lines"] = lines[split_at:]
                    new_block["__force_paragraph_break"] = True
                    logger.debug(f"Created new block starting at line {split_at} with __force_paragraph_break")
                    blocks_to_add.append((block_idx, new_block))
        
        # Apply the splits by removing old blocks and inserting new ones
        # Process in reverse order to maintain indices
        for idx in sorted(indices_to_remove, reverse=True):
            del blocks[idx]
        
        # Insert new blocks at their original positions
        for idx, new_block in sorted(blocks_to_add, key=lambda x: x[0]):
            # Adjust index for already-removed blocks
            adjusted_idx = idx - sum(1 for removed_idx in indices_to_remove if removed_idx < idx)
            blocks.insert(adjusted_idx, new_block)


def _force_important_considerations_paragraph_breaks(section_data: Dict) -> None:
    """
    Force paragraph breaks in the "Important Considerations" section.
    
    The section should have 2 paragraphs with a break at:
    1. (intro) "Although piecemeal armor is lighter than full suits of armor..."
    2. "Characters wearing piecemeal metal armor are also subject..."
    """
    paragraph_starts = [
        "Characters wearing",
    ]
    
    pages = section_data.get("pages", [])
    if not pages:
        return

    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue

            lines = block.get("lines", [])
            if not lines:
                continue
                
            # Check the first line of the block
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
                
            # Get the text from the first span
            first_span = spans[0]
            text = first_span.get("text", "").strip()
            
            # If this block starts with one of our paragraph starts, mark it for a paragraph break
            for para_start in paragraph_starts:
                if text.startswith(para_start):
                    logger.debug(f"Found '{para_start}...' at page {page_idx}, block {block_idx} - marking for paragraph break")
                    block["__force_paragraph_break"] = True
                    break


def _extract_and_reconstruct_bonus_ac_table(section_data: Dict) -> None:
    """Extract and reconstruct the Bonus to AC Per Type of Piece table.
    
    The table should have 7 columns:
    - Armor Type, Full Suit, Breast Plate, Two Arms, One Arm, Two Legs, One Leg
    
    And approximately 14 rows of armor types with their AC bonuses.
    
    The table is currently fragmented across multiple detected tables and text blocks.
    We need to extract the data from the source and reconstruct it properly.
    
    Refactored to follow best practices - broken into focused helper functions.
    """
    logger.info("Starting Bonus to AC table extraction")
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section data")
        return
    
    # Find the header
    header_info = _find_bonus_ac_header(pages)
    if not header_info:
        logger.warning("Could not find 'Bonus to AC Per Type of Piece' header")
        return
    
    page_idx, block_idx, block = header_info
    page = pages[page_idx]
    tables = page.get("tables", [])
    
    logger.info(f"Found {len(tables)} tables on page {page_idx}")
    
    # Extract and reconstruct data
    armor_types_ordered = _get_ordered_armor_types()
    armor_full_suit_map = _extract_armor_full_suit_values(tables)
    all_numeric_values = _extract_remaining_numeric_values(tables)
    
    # Build the reconstructed table
    table_rows = _reconstruct_armor_rows(
        armor_types_ordered, armor_full_suit_map, all_numeric_values
    )
    
    if not table_rows:
        logger.warning("Could not extract armor table data from source")
        return
    
    # Create and insert the final table
    formatted_table = _create_formatted_table(table_rows, block)
    page["tables"] = [formatted_table]
    logger.info(f"Replaced all tables on page {page_idx} with reconstructed table")
    
    # Clean up fragmented blocks
    skip_count = _mark_fragmented_blocks_to_skip(page, block_idx)
    logger.info(f"Marked {skip_count} fragmented text blocks to skip rendering")


def _find_bonus_ac_header(pages: List[Dict]) -> Optional[Tuple[int, int, Dict]]:
    """Find the 'Bonus to AC Per Type of Piece' header block.
    
    Args:
        pages: List of page dictionaries
        
    Returns:
        Tuple of (page_idx, block_idx, block) or None if not found
    """
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            if not lines:
                continue
            
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
            
            text = spans[0].get("text", "").strip()
            
            if text == "Bonus to AC Per Type of Piece":
                logger.info(
                    f"Found 'Bonus to AC Per Type of Piece' header at "
                    f"page {page_idx}, block {block_idx}"
                )
                return (page_idx, block_idx, block)
    
    return None


def _get_ordered_armor_types() -> List[str]:
    """Get the ordered list of armor types.
    
    Returns:
        List of armor type names in alphabetical order
    """
    return [
        "Banded Mail",
        "Brigandine",
        "Bronze Plate",
        "Chain Mail",
        "Field Plate",
        "Full Plate",
        "Hide Armor",
        "Leather Armor",
        "Padded Armor",
        "Plate Mail",
        "Ring Mail",
        "Scale Mail",
        "Splint Mail",
        "Studded Leather",
    ]


def _extract_armor_full_suit_values(tables: List[Dict]) -> Dict[str, str]:
    """Extract armor names and their Full Suit values from tables.
    
    Args:
        tables: List of table dictionaries
        
    Returns:
        Dictionary mapping armor names to full suit values
    """
    import re
    
    logger.info("Extracting armor names and Full Suit values from all tables")
    
    armor_pattern = re.compile(r'([A-Za-z\s]+?)\s+(\d)\s')
    armor_full_suit_map = {}
    
    for table in tables:
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                cell_text = cell.get("text", "")
                
                # Look for cells with armor names (letters + numbers)
                if any(c.isalpha() for c in cell_text) and any(c.isdigit() for c in cell_text):
                    matches = armor_pattern.findall(cell_text + " ")
                    for armor_name, full_suit_value in matches:
                        armor_name = armor_name.strip()
                        # Normalize whitespace
                        armor_name = re.sub(r'\s+', ' ', armor_name)
                        armor_full_suit_map[armor_name] = full_suit_value
                        logger.debug(f"  Found: {armor_name} = {full_suit_value}")
    
    logger.info(f"Total armor types found: {len(armor_full_suit_map)}")
    return armor_full_suit_map


def _extract_remaining_numeric_values(tables: List[Dict]) -> List[str]:
    """Extract numeric values (non-armor-name cells) from tables.
    
    Args:
        tables: List of table dictionaries
        
    Returns:
        List of numeric values
    """
    logger.info("Collecting numeric values from all tables")
    
    all_values = []
    
    for table in tables:
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                cell_text = cell.get("text", "").strip()
                if not cell_text:
                    continue
                
                # Skip cells with armor names (have both letters and numbers)
                if any(c.isalpha() for c in cell_text) and any(c.isdigit() for c in cell_text):
                    continue
                
                # Extract single-digit numeric values
                tokens = cell_text.split()
                for token in tokens:
                    if token.isdigit() and len(token) == 1:
                        all_values.append(token)
    
    logger.info(f"Collected {len(all_values)} numeric values")
    return all_values


def _reconstruct_armor_rows(
    armor_types: List[str],
    full_suit_map: Dict[str, str],
    numeric_values: List[str]
) -> List[List[str]]:
    """Reconstruct armor table rows from extracted data.
    
    Args:
        armor_types: Ordered list of armor type names
        full_suit_map: Map of armor names to full suit values
        numeric_values: List of remaining numeric values
        
    Returns:
        List of table rows (each row is a list of cell values)
    """
    logger.info("Reconstructing armor rows")
    
    table_rows = []
    value_idx = 0
    
    for armor_name in armor_types:
        full_suit = full_suit_map.get(armor_name, "0")
        row_values = [armor_name, full_suit]
        
        # Get next 5 values for other columns
        for _ in range(5):
            if value_idx < len(numeric_values):
                row_values.append(numeric_values[value_idx])
                value_idx += 1
            else:
                row_values.append("0")
        
        table_rows.append(row_values)
        logger.debug(f"  {armor_name}: {row_values[1:]}")
    
    logger.info(f"Reconstructed {len(table_rows)} armor rows")
    return table_rows


def _create_formatted_table(table_rows: List[List[str]], header_block: Dict) -> Dict:
    """Create formatted table structure for rendering.
    
    Args:
        table_rows: List of table rows
        header_block: Header block for bbox reference
        
    Returns:
        Formatted table dictionary
    """
    header_row = [
        "Armor Type", "Full Suit", "Breast Plate",
        "Two Arms", "One Arm", "Two Legs", "One Leg"
    ]
    
    formatted_rows = []
    
    # Header row
    formatted_rows.append({
        "cells": [{"text": cell} for cell in header_row]
    })
    
    # Data rows
    for row in table_rows:
        formatted_rows.append({
            "cells": [{"text": cell} for cell in row]
        })
    
    return {
        "bbox": header_block.get("bbox", [0, 0, 0, 0]),
        "header_rows": 1,
        "rows": formatted_rows
    }


def _mark_fragmented_blocks_to_skip(page: Dict, header_block_idx: int) -> int:
    """Mark fragmented text blocks after table to skip rendering.
    
    Args:
        page: Page dictionary
        header_block_idx: Index of the header block
        
    Returns:
        Number of blocks marked to skip
    """
    blocks = page.get("blocks", [])
    skip_count = 0
    
    for block_idx in range(header_block_idx + 1, len(blocks)):
        block = blocks[block_idx]
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        first_line = lines[0]
        spans = first_line.get("spans", [])
        if not spans:
            continue
        
        text = spans[0].get("text", "").strip()
        
        # Stop at continuation text
        if "plate from a suit" in text.lower():
            logger.debug(
                f"Reached continuation text at block {block_idx}, "
                f"stopping skip marking"
            )
            break
        
        block["__skip_render"] = True
        skip_count += 1
    
    return skip_count


def _reorder_bonus_ac_table_after_important_considerations(section_data: Dict) -> None:
    """
    Move the "Bonus to AC Per Type of Piece" header and table to after the 
    "Important Considerations" section.
    
    This improves readability by keeping the table separate from the 
    interrupted paragraph text in "Piecemeal Armor".
    """
    logger.info("=" * 60)
    logger.info("STARTING BONUS AC TABLE REORDERING")
    logger.info("=" * 60)
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section data")
        return
    
    logger.info(f"Section has {len(pages)} pages")
    
    # Find the "Bonus to AC Per Type of Piece" header block
    bonus_ac_header = None
    bonus_ac_page_idx = None
    bonus_ac_block_idx = None
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            if not lines:
                continue
            
            first_line = lines[0]
            spans = first_line.get("spans", [])
            if not spans:
                continue
            
            text = spans[0].get("text", "").strip()
            
            if text == "Bonus to AC Per Type of Piece":
                bonus_ac_header = block
                bonus_ac_page_idx = page_idx
                bonus_ac_block_idx = block_idx
                logger.info(f"Found 'Bonus to AC Per Type of Piece' at page {page_idx}, block {block_idx}")
                break
        
        if bonus_ac_header:
            break
    
    if not bonus_ac_header:
        logger.warning("Could not find 'Bonus to AC Per Type of Piece' header for reordering")
        return
    
    # Find the table associated with this header (should be on the same page)
    bonus_ac_table = None
    bonus_page = pages[bonus_ac_page_idx]
    tables = bonus_page.get("tables", [])
    
    if tables:
        # The reconstructed table should be the only/first table on this page
        bonus_ac_table = tables[0]
        logger.info(f"Found Bonus to AC table with {len(bonus_ac_table.get('rows', []))} rows")
    
    # Find the last block of the "Important Considerations" section
    # The section contains two paragraphs: one about weight, one about heat effects
    important_considerations_page_idx = None
    important_considerations_end_block_idx = None
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        found_important_considerations = False
        last_paragraph_idx = None
        
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            if not lines:
                continue
            
            # Get all text in the block
            block_text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            
            # Check if we found the Important Considerations header
            if "Important Considerations" in block_text and block_text.strip() == "Important Considerations":
                found_important_considerations = True
                important_considerations_page_idx = page_idx
                logger.info(f"Found 'Important Considerations' at page {page_idx}, block {block_idx}")
                continue
            
            # If we found Important Considerations, track paragraphs that contain relevant text
            # The last paragraph talks about heat effects and Athas/Dark Sun
            if found_important_considerations:
                # Look for content about heat effects (the last paragraph)
                if ("Dark Sun" in block_text or "Athas" in block_text or "hot climate" in block_text or "savage heat" in block_text):
                    last_paragraph_idx = block_idx
                    logger.debug(f"Found potential end paragraph at block {block_idx}: {block_text[:50]}")
        
        # If we found a last paragraph, use it
        if last_paragraph_idx is not None:
            important_considerations_end_block_idx = last_paragraph_idx
            logger.info(f"Found end of 'Important Considerations' section at page {page_idx}, block {last_paragraph_idx}")
            break
    
    if important_considerations_page_idx is None or important_considerations_end_block_idx is None:
        logger.warning("Could not find 'Important Considerations' section end for reordering")
        return
    
    # Now we need to:
    # 1. Remove the "Bonus to AC Per Type of Piece" header from its current location
    # 2. Remove the table from its current location  
    # 3. Insert them after the Important Considerations section
    
    # Store a copy of the header before removing it
    removed_header = dict(bonus_ac_header)
    
    # Remove the header block from its current location by marking it to skip
    pages[bonus_ac_page_idx]["blocks"][bonus_ac_block_idx]["__skip_render"] = True
    logger.info(f"Marked 'Bonus to AC Per Type of Piece' header to skip at page {bonus_ac_page_idx}, block {bonus_ac_block_idx}")
    
    # Store the table before removing it
    removed_table = None
    if bonus_ac_table:
        removed_table = dict(bonus_ac_table)
        # Clear the tables list on the original page
        pages[bonus_ac_page_idx]["tables"] = []
        logger.info(f"Removed Bonus to AC table from page {bonus_ac_page_idx}")
    
    # Insert the header and table after the Important Considerations section
    # We need to insert after the last block of Important Considerations
    insert_page = pages[important_considerations_page_idx]
    
    # Insert position is after the end block
    insert_position = important_considerations_end_block_idx + 1
    
    # Get the Y-coordinate of the LAST paragraph of Important Considerations
    # We need to set the moved header's Y-coordinate to be after all the content
    end_block = insert_page["blocks"][important_considerations_end_block_idx]
    end_block_y = end_block.get("bbox", [0, 0, 0, 0])[3]  # Bottom Y of the last paragraph
    
    # Update the moved header's bbox to place it after Important Considerations
    # This is crucial because the HTML renderer sorts blocks by Y-coordinate
    # Set the width to span the full page so it's treated as full-width
    # Use a very high Y-coordinate to ensure it comes last
    removed_header["bbox"] = [
        47.0,  # Left edge (standard left margin)
        600.0,  # Very high Y to ensure it comes after everything
        565.0,  # Right edge (full page width minus margin)
        620.0   # Set bottom Y
    ]
    # Mark as section header so it's treated as full-width by the HTML renderer
    # This prevents it from being placed in a column bucket
    # Also set the header text and level (H3) so it renders correctly
    removed_header["__section_header"] = True
    removed_header["__header_text"] = "Bonus to AC Per Type of Piece"
    removed_header["__header_level"] = 3  # H3 subheader
    logger.info(f"Updated moved header bbox to Y={end_block_y + 10} and marked as H3 section header")
    
    # Insert the header block
    insert_page["blocks"].insert(insert_position, removed_header)
    logger.info(f"Inserted 'Bonus to AC Per Type of Piece' header at page {important_considerations_page_idx}, block {insert_position}")
    
    # Add the table to the page's tables (it will be rendered after the header)
    if removed_table:
        if "tables" not in insert_page:
            insert_page["tables"] = []
        # Update the table's Y position to match the header's Y
        # This ensures they render together in the correct position when sorted by Y
        if "bbox" in removed_table:
            removed_table["bbox"] = [
                removed_table["bbox"][0],
                610.0,  # After the header at Y=600
                removed_table["bbox"][2],
                800.0  # Give it some height
            ]
        insert_page["tables"].append(removed_table)
        logger.info(f"Added Bonus to AC table to page {important_considerations_page_idx} with Y=610")


def apply_chapter_9_adjustments(section_data: Dict) -> None:
    """
    Apply all Chapter 9 specific processing.
    
    Args:
        section_data: The raw section data dictionary
    """
    slug = section_data.get("slug", "")
    logger.info(f"=" * 60)
    logger.info(f"APPLYING CHAPTER 9 PROCESSING")
    logger.info(f"Slug: {slug}")
    logger.info(f"=" * 60)
    
    _merge_hovering_on_deaths_door_header(section_data)
    _adjust_header_levels(section_data)
    _prevent_stables_paragraph_break(section_data)
    _force_battling_undead_paragraph_breaks(section_data)
    _force_turning_undead_paragraph_breaks(section_data)
    _force_hovering_on_deaths_door_paragraph_breaks(section_data)
    _force_waging_wars_paragraph_breaks(section_data)
    _force_followers_paragraph_breaks(section_data)
    _force_piecemeal_armor_paragraph_breaks(section_data)
    _force_important_considerations_paragraph_breaks(section_data)
    _extract_and_reconstruct_bonus_ac_table(section_data)
    _reorder_bonus_ac_table_after_important_considerations(section_data)
    
    logger.debug("Chapter 9 processing complete")

