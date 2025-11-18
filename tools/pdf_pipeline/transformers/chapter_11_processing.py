"""
Chapter 11 Processing - Encounters

This module handles chapter-specific processing for Chapter 11.

Key processing:
- Merge "Wizard, Priest, and Psionicist" and "Encounters" headers into a single header
- Add paragraph breaks in sections
"""

import logging

logger = logging.getLogger(__name__)


def _merge_compendium_header_spans(pages: list) -> None:
    """
    Merge multi-span compendium headers into single spans.
    
    Headers like "Forgotten Realms® (MC3)" and "Dragonlance® (MC4)" are often split
    across multiple spans in the PDF. This prevents them from being recognized as headers
    during TOC generation. This function merges these multi-span headers into single spans.
    """
    logger.warning("Merging compendium header spans...")
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        logger.debug(f"Page {page_idx}: {len(blocks)} blocks")
        
        for block_idx, block in enumerate(blocks):
            lines = block.get("lines", [])
            if not lines:
                continue
            
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                if len(spans) <= 1:
                    continue
                
                # Check if this is a compendium header by looking at the full text
                full_text = "".join(span.get("text", "") for span in spans)
                
                # Check if this matches a compendium header pattern
                if any(marker in full_text for marker in ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]):
                    logger.debug(f"Page {page_idx}, Block {block_idx}, Line {line_idx}: Found potential header '{full_text}' with {len(spans)} spans")
                    
                    # Check if all spans have the same color (header color)
                    colors = [span.get("color") for span in spans]
                    logger.debug(f"  Colors: {colors}")
                    
                    if colors and all(c == colors[0] for c in colors):
                        logger.warning(f"Merging header spans for: '{full_text}' at page {page_idx}, block {block_idx}")
                        logger.warning(f"  BEFORE merge: {len(spans)} spans")
                        
                        # Merge all spans into the first span
                        first_span = spans[0]
                        first_span["text"] = full_text
                        
                        # Update bbox to cover all spans (skip spans without bbox)
                        bboxes = [span.get("bbox") for span in spans if span.get("bbox")]
                        if bboxes:
                            min_x0 = min(bbox[0] for bbox in bboxes)
                            min_y0 = min(bbox[1] for bbox in bboxes)
                            max_x1 = max(bbox[2] for bbox in bboxes)
                            max_y1 = max(bbox[3] for bbox in bboxes)
                            first_span["bbox"] = [min_x0, min_y0, max_x1, max_y1]
                        
                        # Keep only the first span
                        line["spans"] = [first_span]
                        
                        logger.warning(f"  AFTER merge: {len(line['spans'])} spans, text='{first_span['text']}'")
                        logger.warning(f"  Block {block_idx} now has merged header")
                    else:
                        logger.debug(f"  Skipping - not all spans have the same color")


def _mark_compendium_headers_as_h2(pages: list) -> None:
    """
    Mark campaign setting headers as H2 (MC3, MC4, MC5, MC6).
    
    The headers "Forgotten Realms® (MC3)", "Dragonlance® (MC4)", "Greyhawk® (MC5)",
    and "Kara-Tur (MC6)" should be rendered as H2 headers (subheaders under "Monsters").
    This function adds the CSS class and font-size styling to mark them as H2.
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Marking compendium headers (MC3, MC4, MC5, MC6) as H2...")
    
    compendium_markers = ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]
    headers_found = []
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            lines = block.get("lines", [])
            for line_idx, line in enumerate(lines):
                spans = line.get("spans", [])
                
                for span in spans:
                    text = span.get("text", "")
                    
                    # Check if this is a campaign setting header
                    if any(marker in text for marker in compendium_markers):
                        logger.warning(f"Found compendium header at page {page_idx}, block {block_idx}: '{text}'")
                        
                        # Log all block properties
                        logger.warning(f"  Block has {len(lines)} lines, {len(spans)} spans in first line")
                        logger.warning(f"  Block __skip_render before: {block.get('__skip_render', False)}")
                        
                        # Mark the block as H2
                        block["__render_as_h2"] = True
                        block["__header_text"] = text
                        
                        # Prevent this block from being processed in column layout
                        # This ensures it's rendered as-is without being split or merged
                        block["__column_assigned"] = True
                        
                        # DON'T mark the span to skip - let the block render handle it
                        # The render_text_block function will see __render_as_h2 and render only the header
                        
                        headers_found.append(text)
                        logger.warning(f"  ✓ Marked as H2: '{text}'")
                        logger.warning(f"  Block __skip_render after: {block.get('__skip_render', False)}")
    
    logger.warning(f"Marked {len(headers_found)} compendium headers as H2: {headers_found}")



def apply_chapter_11_adjustments(section_data: dict) -> None:
    """
    Apply Chapter 11-specific adjustments to the section data.
    
    Args:
        section_data: The section data dictionary to modify
    """
    # Check if adjustments have already been applied (prevent double-processing)
    if section_data.get("__chapter_11_adjusted"):
        logger.warning("Chapter 11 adjustments already applied, skipping")
        return
    
    logger.warning("=" * 80)
    logger.warning("Applying Chapter 11 adjustments (Encounters)")
    logger.warning("=" * 80)
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in section data")
        return
    
    # Find and merge the "Wizard, Priest, and Psionicist" + "Encounters" headers
    _merge_wizard_priest_encounters_headers(pages)
    
    # Merge multi-span compendium headers (MC3, MC4) into single spans
    logger.warning("🔄 About to merge compendium header spans...")
    try:
        _merge_compendium_header_spans(pages)
        logger.warning("🔄 Finished merging compendium header spans")
    except Exception as e:
        logger.error(f"❌ Exception in merge function: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # Verify the merge worked
    logger.warning("🔍 Verifying header span merges...")
    for page_idx, page in enumerate(pages):
        for block_idx, block in enumerate(page.get("blocks", [])):
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if len(spans) == 1:
                    text = spans[0].get("text", "")
                    if any(marker in text for marker in ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]):
                        logger.warning(f"  ✓ Page {page_idx}, Block {block_idx}: '{text}' has 1 span (MERGED)")
                elif len(spans) > 1:
                    full_text = "".join(span.get("text", "") for span in spans)
                    if any(marker in full_text for marker in ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]):
                        logger.warning(f"  ✗ Page {page_idx}, Block {block_idx}: '{full_text}' still has {len(spans)} spans (NOT MERGED!)")
    
    # Mark campaign setting headers as H2 (MC3, MC4, MC5, MC6)
    _mark_compendium_headers_as_h2(pages)
    
    # Extract and create the Forgotten Realms monster list
    _extract_forgotten_realms_list(pages)
    
    # Extract and create the Dragonlance monster list
    _extract_dragonlance_list(pages)
    
    # Extract and create the Greyhawk monster list
    _extract_greyhawk_list(pages)
    
    # Extract and create the Kara-Tur monster list
    _extract_kara_tur_list(pages)
    
    # Handle the two-column monster list under "Monstrous Compendium 1 and 2"
    _extract_monstrous_compendium_list(pages)
    
    # Merge Plant-Based Monsters text into single paragraph
    _merge_plant_based_monsters_text(section_data)
    
    # Extract and reconstruct wilderness encounter tables
    _extract_wilderness_encounter_tables(section_data)
    
    # Mark paragraph breaks
    _mark_wizard_priest_psionicist_paragraph_breaks(section_data)
    _mark_city_states_paragraph_breaks(section_data)
    
    # Mark as adjusted to prevent double-processing
    section_data["__chapter_11_adjusted"] = True
    
    logger.warning("Chapter 11 adjustments complete")


def _merge_wizard_priest_encounters_headers(pages: list) -> None:
    """
    Merge the "Wizard, Priest, and Psionicist" and "Encounters" headers into a single header.
    
    These appear in the source as two lines within the same block and should be combined.
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Merging 'Wizard, Priest, and Psionicist' + 'Encounters' headers")
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        
        for block_idx, block in enumerate(blocks):
            lines = block.get("lines", [])
            
            # Look for a block with multiple lines where the first line is
            # "Wizard, Priest, and Psionicist" and the second is "Encounters"
            if len(lines) >= 2:
                first_line_text = _get_line_text(lines[0])
                second_line_text = _get_line_text(lines[1]) if len(lines) > 1 else ""
                
                if (first_line_text == "Wizard, Priest, and Psionicist" and 
                    second_line_text == "Encounters"):
                    
                    logger.warning(f"Found header to merge at page {page_idx}, block {block_idx}")
                    logger.warning(f"  Line 1: '{first_line_text}'")
                    logger.warning(f"  Line 2: '{second_line_text}'")
                    
                    # Merge the two lines into a single line
                    # Keep the first line and append the second line's text
                    first_span = lines[0]["spans"][0]
                    first_span["text"] = "Wizard, Priest, and Psionicist Encounters"
                    
                    # Update the bbox to encompass both lines
                    if "bbox" in lines[1]:
                        # Extend the bbox to include the second line
                        block["bbox"][3] = lines[1]["bbox"][3]  # Update bottom y-coordinate
                        lines[0]["bbox"][3] = lines[1]["bbox"][3]
                    
                    # Remove the second line
                    lines.pop(1)
                    
                    logger.warning(f"  Merged to: '{first_span['text']}'")
                    return  # Only need to do this once
    
    logger.warning("Could not find the 'Wizard, Priest, and Psionicist' + 'Encounters' headers to merge")


def _extract_forgotten_realms_list(pages: list) -> None:
    """
    Extract and create a list of Forgotten Realms monsters under the Forgotten Realms® (MC3) header.
    
    These monsters appear in the right column of page 80, between the Plant-Based Monsters content
    and the Monstrous Compendium 1 and 2 header. They were being skipped by the MC list extraction.
    
    The Forgotten Realms list should contain:
    - Bhaergala*
    - Meazel*
    - Rhaumbusun
    - Strider, Giant
    - Thessalmonster
    - Thri-kreen*
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Processing Forgotten Realms® (MC3) monster list")
    
    # Find the Forgotten Realms header on page 80
    forgotten_realms_page_idx = None
    forgotten_realms_block_idx = None
    
    for page_idx, page in enumerate(pages):
        if page.get("page_number") != 80:
            continue
            
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            if "Forgotten Realms" in text and "(MC3)" in text:
                forgotten_realms_page_idx = page_idx
                forgotten_realms_block_idx = block_idx
                logger.warning(f"Found 'Forgotten Realms® (MC3)' at page {page_idx}, block {block_idx}")
                break
        
        if forgotten_realms_page_idx is not None:
            break
    
    if forgotten_realms_page_idx is None:
        logger.warning("Could not find 'Forgotten Realms® (MC3)' header")
        return
    
    # Define the expected Forgotten Realms monsters
    forgotten_realms_monsters = [
        "Bhaergala*",
        "Meazel*",
        "Rhaumbusun",
        "Strider, Giant",
        "Thessalmonster",
        "Thri-kreen*"
    ]
    
    # Find these monsters in the blocks and mark them for skipping in their current location
    page_80 = pages[forgotten_realms_page_idx]
    blocks = page_80.get("blocks", [])
    
    found_monsters = []
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this block contains one of the Forgotten Realms monsters
        for monster in forgotten_realms_monsters:
            # Match with or without spaces (e.g., "M e a z e l" -> "Meazel")
            monster_normalized = monster.replace('*', '').strip()
            text_normalized = text.replace('*', '').strip().replace(' ', '')
            monster_match = monster_normalized.replace(' ', '')
            
            if text_normalized.lower() == monster_match.lower():
                logger.warning(f"Found Forgotten Realms monster: '{text}' (matches {monster})")
                found_monsters.append(text)
                # Mark for skipping in current location
                block["__skip_render"] = True
                break
    
    logger.warning(f"Found {len(found_monsters)} Forgotten Realms monsters: {found_monsters}")
    
    # Create a new block after the Forgotten Realms header with the list
    # Insert it right after the header block
    forgotten_realms_block = blocks[forgotten_realms_block_idx]
    
    # Create the list text with all monsters
    list_text = "\n".join(forgotten_realms_monsters)
    
    # Create a new block with the list
    new_list_block = {
        "type": "text",
        "bbox": forgotten_realms_block.get("bbox", [0, 0, 0, 0]),
        "__format_as_html_list": True,
        "lines": [{
            "spans": [{
                "text": list_text,
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # Insert the new block after the header
    blocks.insert(forgotten_realms_block_idx + 1, new_list_block)
    logger.warning(f"Created Forgotten Realms list block with {len(forgotten_realms_monsters)} monsters")


def _extract_dragonlance_list(pages: list) -> None:
    """
    Extract and create a list of Dragonlance monsters under the Dragonlance® (MC4) header.
    
    These monsters appear in the right column of page 80, potentially mixed with other content
    due to column alignment. They were being skipped by the MC list extraction.
    
    The Dragonlance list should contain:
    - Fire Minion*
    - Hatori
    - Horax
    - Insect Swarm
    - Skrit
    - Slig*
    - Tylor*
    - Wyndlass
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Processing Dragonlance® (MC4) monster list")
    
    # Find the Dragonlance header on page 80
    dragonlance_page_idx = None
    dragonlance_block_idx = None
    
    for page_idx, page in enumerate(pages):
        if page.get("page_number") != 80:
            continue
            
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            if "Dragonlance" in text and "(MC4)" in text:
                dragonlance_page_idx = page_idx
                dragonlance_block_idx = block_idx
                logger.warning(f"Found 'Dragonlance® (MC4)' at page {page_idx}, block {block_idx}")
                break
        
        if dragonlance_page_idx is not None:
            break
    
    if dragonlance_page_idx is None:
        logger.warning("Could not find 'Dragonlance® (MC4)' header")
        return
    
    # Define the expected Dragonlance monsters
    dragonlance_monsters = [
        "Fire Minion*",
        "Hatori",
        "Horax",
        "Insect Swarm",
        "Skrit",
        "Slig*",
        "Tylor*",
        "Wyndlass"
    ]
    
    # Find these monsters in the blocks and mark them for skipping in their current location
    page_80 = pages[dragonlance_page_idx]
    blocks = page_80.get("blocks", [])
    
    found_monsters = []
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this block contains one of the Dragonlance monsters
        for monster in dragonlance_monsters:
            # Match with or without spaces (e.g., "F i r e   M i n i o n" -> "Fire Minion")
            monster_normalized = monster.replace('*', '').strip()
            text_normalized = text.replace('*', '').strip().replace(' ', '')
            monster_match = monster_normalized.replace(' ', '')
            
            if text_normalized.lower() == monster_match.lower():
                logger.warning(f"Found Dragonlance monster: '{text}' (matches {monster})")
                found_monsters.append(text)
                # Mark for skipping in current location
                block["__skip_render"] = True
                break
    
    logger.warning(f"Found {len(found_monsters)} Dragonlance monsters: {found_monsters}")
    
    # BEFORE inserting the new list block, mark any orphaned text blocks
    # that contain MC1&2 content between Dragonlance and Greyhawk
    for block_idx in range(dragonlance_block_idx + 1, len(blocks)):
        block = blocks[block_idx]
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this is the next header (Greyhawk)
        if "Greyhawk" in text or "MC5" in text:
            break
        
        # Check if this block contains MC1&2 monster names
        # (e.g., "A n t Ant Lion, Giant Basilisk...")
        mc_monsters = ["Ant", "Ant Lion", "Basilisk", "Bat", "Beetle", "Behir", "Bulette", 
                      "Cats, Great", "Cave Fisher", "Centipede", "Dragonne"]
        # Count how many MC monsters appear in this block
        monster_count = sum(1 for monster in mc_monsters if monster.lower() in text.lower())
        
        # If this block contains multiple MC1&2 monsters, it's likely a duplicate
        if monster_count >= 3:
            logger.warning(f"Marking orphaned MC1&2 content after Dragonlance: '{text[:80]}...'")
            block["__skip_render"] = True
    
    # Create a new block after the Dragonlance header with the list
    # Insert it right after the header block
    dragonlance_block = blocks[dragonlance_block_idx]
    
    # Create the list text with all monsters
    list_text = "\n".join(dragonlance_monsters)
    
    # Create a new block with the list
    new_list_block = {
        "type": "text",
        "bbox": dragonlance_block.get("bbox", [0, 0, 0, 0]),
        "__format_as_html_list": True,
        "lines": [{
            "spans": [{
                "text": list_text,
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # Insert the new block after the header
    blocks.insert(dragonlance_block_idx + 1, new_list_block)
    logger.warning(f"Created Dragonlance list block with {len(dragonlance_monsters)} monsters")


def _extract_greyhawk_list(pages: list) -> None:
    """
    Extract and create a list of Greyhawk monsters under the Greyhawk® (MC5) header.
    
    These monsters appear in the right column of page 80, potentially mixed with other content
    due to column alignment.
    
    The Greyhawk list should contain:
    - Beetle
    - Bonesnapper
    - Dragonfly, Giant
    - Dragonnel
    - Horgar
    - Plant, Carnivorous (Cactus, Vampire)
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Processing Greyhawk® (MC5) monster list")
    
    # Find the Greyhawk header on page 80
    greyhawk_page_idx = None
    greyhawk_block_idx = None
    
    for page_idx, page in enumerate(pages):
        if page.get("page_number") != 80:
            continue
            
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            if "Greyhawk" in text and "(MC5)" in text:
                greyhawk_page_idx = page_idx
                greyhawk_block_idx = block_idx
                logger.warning(f"Found 'Greyhawk® (MC5)' at page {page_idx}, block {block_idx}")
                break
        
        if greyhawk_page_idx is not None:
            break
    
    if greyhawk_page_idx is None:
        logger.warning("Could not find 'Greyhawk® (MC5)' header")
        return
    
    # Define the expected Greyhawk monsters
    greyhawk_monsters = [
        "Beetle",
        "Bonesnapper",
        "Dragonfly, Giant",
        "Dragonnel",
        "Horgar",
        "Plant, Carnivorous (Cactus, Vampire)"
    ]
    
    # Find these monsters in the blocks and mark them for skipping in their current location
    page_80 = pages[greyhawk_page_idx]
    blocks = page_80.get("blocks", [])
    
    found_monsters = []
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this block contains one of the Greyhawk monsters
        for monster in greyhawk_monsters:
            # Match with or without spaces (e.g., "D r a g o n f l y" -> "Dragonfly")
            # Also handle variations like "Plant, Carnivorous(Cactus, Vampire)" vs "Plant, Carnivorous (Cactus, Vampire)"
            # Also match partial names like "Plant, Carnivorous" matching "Plant, Carnivorous (Cactus, Vampire)"
            monster_normalized = monster.replace(',', '').replace('(', '').replace(')', '').strip().replace(' ', '')
            text_normalized = text.replace(',', '').replace('(', '').replace(')', '').strip().replace(' ', '')
            
            # Check for exact match OR if the text is a prefix of the monster name
            if (text_normalized.lower() == monster_normalized.lower() or
                monster_normalized.lower().startswith(text_normalized.lower())):
                logger.warning(f"Found Greyhawk monster: '{text}' (matches {monster})")
                found_monsters.append(text)
                # Mark for skipping in current location
                block["__skip_render"] = True
                break
    
    logger.warning(f"Found {len(found_monsters)} Greyhawk monsters: {found_monsters}")
    
    # BEFORE inserting the new list block, mark any orphaned text blocks
    # that contain MC1&2 content between Greyhawk and Kara-Tur
    for block_idx in range(greyhawk_block_idx + 1, len(blocks)):
        block = blocks[block_idx]
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this is the next header (Kara-Tur)
        if "Kara-Tur" in text or "MC6" in text:
            break
        
        # Check if this block contains MC1&2 monster names
        # (e.g., "Elementals, all Ettercap* Ettin*...")
        mc_monsters = ["Elementals", "Ettercap", "Ettin", "Genie", "Giant-kin", 
                      "Cyclops", "Golem", "Plant, Carnivorous"]
        # Count how many MC monsters appear in this block
        monster_count = sum(1 for monster in mc_monsters if monster.lower() in text.lower())
        
        # If this block contains multiple MC1&2 monsters, it's likely a duplicate
        if monster_count >= 3:
            logger.warning(f"Marking orphaned MC1&2 content after Greyhawk: '{text[:80]}...'")
            block["__skip_render"] = True
    
    # Create a new block after the Greyhawk header with the list
    # Insert it right after the header block
    greyhawk_block = blocks[greyhawk_block_idx]
    
    # Create the list text with all monsters
    list_text = "\n".join(greyhawk_monsters)
    
    # Create a new block with the list
    new_list_block = {
        "type": "text",
        "bbox": greyhawk_block.get("bbox", [0, 0, 0, 0]),
        "__format_as_html_list": True,
        "lines": [{
            "spans": [{
                "text": list_text,
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # Insert the new block after the header
    blocks.insert(greyhawk_block_idx + 1, new_list_block)
    logger.warning(f"Created Greyhawk list block with {len(greyhawk_monsters)} monsters")


def _extract_kara_tur_list(pages: list) -> None:
    """
    Extract and create a list of Kara-Tur monsters under the Kara-Tur (MC6) header.
    
    These monsters appear mixed with legend text and additional paragraphs.
    
    The Kara-Tur list should contain:
    - Goblin Spider *
    - Jishin Mushi
    
    Followed by:
    - Legend: "*indicates possible psionic wild power"
    - Paragraph starting with "No creatures"
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Processing Kara-Tur (MC6) monster list")
    
    # Find the Kara-Tur header on page 80 or 81 (might span pages)
    kara_tur_page_idx = None
    kara_tur_block_idx = None
    
    for page_idx, page in enumerate(pages):
        page_num = page.get("page_number")
        if page_num not in [80, 81]:
            continue
            
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            if "Kara-Tur" in text and "(MC6)" in text:
                kara_tur_page_idx = page_idx
                kara_tur_block_idx = block_idx
                logger.warning(f"Found 'Kara-Tur (MC6)' at page {page_idx}, block {block_idx}")
                break
        
        if kara_tur_page_idx is not None:
            break
    
    if kara_tur_page_idx is None:
        logger.warning("Could not find 'Kara-Tur (MC6)' header")
        return
    
    # Define the expected Kara-Tur monsters
    kara_tur_monsters = [
        "Goblin Spider *",
        "Jishin Mushi"
    ]
    
    # Find these monsters in the blocks and mark them for skipping in their current location
    page = pages[kara_tur_page_idx]
    blocks = page.get("blocks", [])
    
    found_monsters = []
    blocks_to_skip = []
    
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this block contains one of the Kara-Tur monsters
        for monster in kara_tur_monsters:
            # Match with or without spaces
            monster_normalized = monster.replace('*', '').strip().replace(' ', '')
            text_normalized = text.replace('*', '').strip().replace(' ', '')
            
            if text_normalized.lower() == monster_normalized.lower():
                logger.warning(f"Found Kara-Tur monster: '{text}' (matches {monster})")
                found_monsters.append(text)
                blocks_to_skip.append(block_idx)
                break
    
    logger.warning(f"Found {len(found_monsters)} Kara-Tur monsters: {found_monsters}")
    
    # Now find blocks that contain the mixed content (monsters + legend + paragraph)
    # These need to be split up
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        text = _get_block_text(block).strip()
        
        # Check if this block contains multiple pieces we need to separate
        has_goblin_spider = "Goblin" in text and "Spider" in text
        has_jishin = "Jishin" in text and "Mushi" in text
        has_legend = "*indicates" in text or "indicates possible" in text
        has_no_creatures = "No creatures" in text
        
        # If this block has multiple components, mark it for skipping
        # We'll create separate blocks for each component
        if (has_goblin_spider or has_jishin) and (has_legend or has_no_creatures):
            logger.warning(f"Found mixed content block at {block_idx}: '{text[:100]}...'")
            blocks_to_skip.append(block_idx)
    
    # Mark all identified blocks for skipping
    for block_idx in set(blocks_to_skip):
        if block_idx < len(blocks):
            blocks[block_idx]["__skip_render"] = True
            logger.debug(f"Marked block {block_idx} for skipping")
    
    # Create new blocks after the Kara-Tur header
    kara_tur_block = blocks[kara_tur_block_idx]
    insertion_point = kara_tur_block_idx + 1
    
    # 1. Create the monster list block
    list_text = "\n".join(kara_tur_monsters)
    list_block = {
        "type": "text",
        "bbox": kara_tur_block.get("bbox", [0, 0, 0, 0]),
        "__format_as_html_list": True,
        "lines": [{
            "spans": [{
                "text": list_text,
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # 2. Create the legend text block
    legend_block = {
        "type": "text",
        "bbox": kara_tur_block.get("bbox", [0, 0, 0, 0]),
        "lines": [{
            "spans": [{
                "text": "*indicates possible psionic wild power",
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # 3. Create the "No creatures" paragraph block
    no_creatures_text = ("No creatures from the SPELLJAMMER Monstrous Compendiums live on Athas. "
                        "Fiends from the Outer Planes Appendix (MC10) can travel to and from Athas at will, "
                        "but do so rarely, only when summoned by dragons or great wizards.")
    no_creatures_block = {
        "type": "text",
        "bbox": kara_tur_block.get("bbox", [0, 0, 0, 0]),
        "lines": [{
            "spans": [{
                "text": no_creatures_text,
                "size": 10,
                "color": "#000000"
            }]
        }]
    }
    
    # Insert the new blocks in order
    blocks.insert(insertion_point, list_block)
    blocks.insert(insertion_point + 1, legend_block)
    blocks.insert(insertion_point + 2, no_creatures_block)
    
    logger.warning(f"Created Kara-Tur list block with {len(kara_tur_monsters)} monsters, legend, and paragraph")


def _find_monstrous_compendium_header(pages: list) -> tuple:
    """Find the Monstrous Compendium 1 and 2 header on page 80.
    
    Returns:
        tuple: (page_idx, block_idx, y_pos) or (None, None, None) if not found
    """
    for page_idx, page in enumerate(pages):
        if page.get("page_number") != 80:
            continue
            
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
                
            text = _get_block_text(block)
            if "Monstrous Compendium 1 and 2" in text:
                y_pos = block.get("bbox", [0, 0, 0, 0])[1]
                logger.warning(f"Found 'Monstrous Compendium 1 and 2' at page {page_idx}, block {block_idx}, y={y_pos}")
                return page_idx, block_idx, y_pos
    
    logger.warning("Could not find 'Monstrous Compendium 1 and 2' header")
    return None, None, None


def _is_section_header_block(block: dict, text: str) -> bool:
    """Check if a block is a section header (e.g., Forgotten Realms MC3).
    
    Args:
        block: Block dictionary
        text: Block text
        
    Returns:
        bool: True if this is a section header
    """
    # Check if marked as H2 header
    if block.get("__render_as_h2"):
        return True
    
    # Check for MC3/MC4/MC5/MC6 markers with realm names
    mc_markers = ["MC3", "MC4", "MC5", "MC6"]
    realms = ["Forgotten Realms", "Dragonlance", "Greyhawk", "Kara-Tur"]
    
    if any(mc_marker in text for mc_marker in mc_markers) and any(realm in text for realm in realms):
        return True
    
    # Check font properties (headers have special color/size)
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            if span.get("color") == "#ca5804" or span.get("size", 0) > 10:
                return True
    
    return False


def _should_skip_mc12_block(block: dict, text: str) -> bool:
    """Determine if a block should be skipped (not part of MC1&2 list).
    
    Args:
        block: Block dictionary
        text: Block text
        
    Returns:
        bool: True if block should be skipped
    """
    # Don't skip section headers
    if _is_section_header_block(block, text):
        return False
    
    # Skip known non-MC1&2 content
    text_clean = text.replace('*', '').strip()
    skip_texts = [
        "indicates possible psionic", "SPELLJAMMER", "Fiends from the Outer",
        "Bhaergala", "Meazel", "Rhaumbusun", "Strider, Giant",
        "Thessalmonster", "Thri-kreen", "Jishin Mushi"
    ]
    
    return any(skip_text in text_clean for skip_text in skip_texts)


def _clean_ocr_spacing(text: str) -> str:
    """Fix OCR spacing issues like 'A n t' -> 'Ant'.
    
    Args:
        text: Text with potential OCR spacing issues
        
    Returns:
        str: Cleaned text
    """
    words = text.split()
    if len(words) < 2:
        return text
    
    # Calculate metrics
    avg_len = sum(len(w) for w in words) / len(words)
    single_char_count = sum(1 for w in words if len(w) == 1)
    single_char_ratio = single_char_count / len(words)
    
    # Check for properly capitalized multi-char words (e.g., "Aerial Servant")
    proper_words = [w for w in words if len(w) > 2 and w[0].isupper()]
    has_proper_words = len(proper_words) >= 2
    
    # If low avg length or many single chars, and no proper words, likely OCR issue
    if (avg_len <= 2.0 or single_char_ratio >= 0.5) and not has_proper_words:
        cleaned = text.replace(' ', '')
        logger.debug(f"Fixed OCR spacing: '{text}' -> '{cleaned}'")
        return cleaned
    
    return text


def _split_space_star_pattern(text: str) -> list:
    """Split text on ' *' pattern (space before asterisk).
    
    Args:
        text: Text to split
        
    Returns:
        list: Split items
    """
    import re
    
    result = []
    parts = re.split(r'(\s+\*)', text)
    for i in range(0, len(parts), 2):
        if i < len(parts):
            item = parts[i]
            if i+1 < len(parts):
                item += parts[i+1].strip()  # Add the asterisk
            if item.strip():
                result.append(item.strip())
    
    return result if len(result) > 1 else [text]


def _split_camelcase_items(items: list) -> list:
    """Split concatenated CamelCase monster names.
    
    Args:
        items: List of items to process
        
    Returns:
        list: Split items
    """
    import re
    
    result = []
    for item in items:
        # Items with spaces are legitimate multi-word names
        if ' ' in item:
            result.append(item)
            continue
        
        # Split before uppercase letter following lowercase
        split_items = re.split(r'(?<=[a-z])(?=[A-Z])', item)
        
        # Handle very long concatenated items
        for subitem in split_items:
            if len(subitem) > 15 and ' ' not in subitem and ',' not in subitem:
                parts = re.findall(r'[A-Z][a-z]*\*?', subitem)
                if len(parts) > 1:
                    result.extend(parts)
                else:
                    result.append(subitem)
            else:
                result.append(subitem)
    
    return result


def _collect_mc12_column_items(blocks: list, header_block_idx: int, header_y: float) -> tuple:
    """Collect monster list items from left and right columns.
    
    Args:
        blocks: List of blocks
        header_block_idx: Index of MC1&2 header
        header_y: Y-coordinate of header
        
    Returns:
        tuple: (left_column_items, right_column_items)
    """
    left_items = []
    right_items = []
    
    for block_idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        
        bbox = block.get("bbox", [0, 0, 0, 0])
        x_start = bbox[0]
        y_start = bbox[1]
        text = _get_block_text(block).strip()
        
        # Skip empty, header, page numbers, and short artifacts
        if not text or "Monstrous Compendium 1 and 2" in text:
            continue
        if text.isdigit() or (len(text) <= 3 and any(c.isdigit() for c in text)):
            continue
        if len(text) < 2:
            continue
        
        # Skip non-MC1&2 content
        if _should_skip_mc12_block(block, text):
            block["__skip_render"] = True
            continue
        
        # Right column before header - misplaced MC1&2 items
        if x_start >= 300 and y_start < header_y:
            if not any(mc in text for mc in ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]):
                if 2 <= len(text) < 50:
                    logger.debug(f"Found right-column list item: '{text}' at y={y_start}")
                    right_items.append((y_start, text, block_idx))
                    block["__skip_render"] = True
                    
                    # Special handling for duplicate "Plant, Carnivorous"
                    if "Plant" in text and "Carnivorous" in text:
                        logger.debug(f"Marking 'Plant, Carnivorous' to skip (block {block_idx})")
            else:
                logger.debug(f"Preserving section header: '{text}'")
        
        # Right column after header - not MC1&2
        elif x_start >= 300 and y_start >= header_y:
            if not any(mc in text for mc in ["(MC3)", "(MC4)", "(MC5)", "(MC6)"]):
                if 2 <= len(text) < 50:
                    logger.debug(f"Skipping right-column after header: '{text}'")
                    block["__skip_render"] = True
            else:
                logger.debug(f"Preserving section header: '{text}'")
        
        # Left column after header - MC1&2 items
        elif x_start < 300 and y_start > header_y:
            if 2 <= len(text) < 50:
                logger.debug(f"Found left-column list item: '{text}' at y={y_start}")
                left_items.append((y_start, text, block_idx))
    
    # Sort by Y-coordinate
    left_items.sort(key=lambda item: item[0])
    right_items.sort(key=lambda item: item[0])
    
    return left_items, right_items


def _process_column_items(column_items: list) -> list:
    """Process column items: clean OCR, split concatenations.
    
    Args:
        column_items: List of (y_pos, text, block_idx) tuples
        
    Returns:
        list: Processed item names
    """
    result = []
    
    for y_pos, text, block_idx in column_items:
        clean_text = _clean_ocr_spacing(text.strip())
        
        # Skip page numbers
        if clean_text.isdigit():
            continue
        
        # Split on ' *' pattern
        items_to_process = _split_space_star_pattern(clean_text)
        
        # Split CamelCase concatenations
        split_items = _split_camelcase_items(items_to_process)
        result.extend(split_items)
    
    return result


def _merge_known_multiword_monsters(items: list) -> list:
    """Merge known two-word monster names like 'Aerial' + 'Servant'.
    
    Args:
        items: List of item names
        
    Returns:
        list: Merged items
    """
    merged = []
    i = 0
    
    while i < len(items):
        current = items[i].strip()
        
        # Check for "Aerial Servant"
        if current == "Aerial" and i + 1 < len(items) and items[i + 1].strip() == "Servant":
            merged_name = f"{current} {items[i + 1].strip()}"
            logger.debug(f"Merging: '{current}' + '{items[i + 1]}' -> '{merged_name}'")
            merged.append(merged_name)
            i += 2
            continue
        
        merged.append(current)
        i += 1
    
    return merged


def _split_camelcase_with_comma(items: list) -> list:
    """Split items with comma like 'BuletteCats, Great' -> ['Bulette', 'Cats, Great'].
    
    Args:
        items: List of items
        
    Returns:
        list: Split items
    """
    import re
    
    result = []
    for item in items:
        if ',' in item and not item.startswith(','):
            # Split at CamelCase boundaries
            parts = re.split(r'(?<=[a-z])(?=[A-Z])', item)
            if len(parts) > 1:
                logger.debug(f"Splitting CamelCase with comma: '{item}' -> {parts}")
                result.extend(parts)
            else:
                result.append(item)
        else:
            result.append(item)
    
    return result


def _filter_non_mc12_items(items: list) -> list:
    """Filter out items from other compendium sections.
    
    Args:
        items: List of items
        
    Returns:
        list: Filtered items
    """
    skip_texts = [
        "Forgotten Realms", "MC3", "MC4", "MC5", "MC6",
        "Meazel", "Dragonlance", "Greyhawk", "Kara-Tur"
    ]
    
    filtered = []
    for item in items:
        # Skip non-MC1&2 items
        if any(skip_text in item for skip_text in skip_texts):
            logger.debug(f"Filtering out: '{item}'")
            continue
        
        # Skip empty or very short
        if len(item.strip()) < 2:
            continue
        
        filtered.append(item.strip())
    
    return filtered


def _create_mc12_list_block(items: list, header_block_idx: int, header_y: float) -> dict:
    """Create a new block with the consolidated monster list.
    
    Args:
        items: List of monster names
        header_block_idx: Index of MC1&2 header
        header_y: Y-coordinate of header
        
    Returns:
        dict: New list block
    """
    # Format as bulleted list
    list_items = [f"• {item}" for item in items]
    list_text = "\n".join(list_items)
    
    logger.warning(f"Creating combined monster list with {len(items)} items")
    logger.debug(f"List items: {items[:10]}...")
    
    return {
        "type": "text",
        "bbox": [49.0, header_y + 20, 250.0, header_y + 100],
        "lines": [{
            "bbox": [49.0, header_y + 20, 250.0, header_y + 30],
            "spans": [{
                "text": list_text,
                "font": "MSTT31c50d",
                "size": 8.880000114440918,
                "flags": 4,
                "color": "#000000",
                "ascender": 0.800000011920929,
                "descender": -0.20000000298023224
            }]
        }],
        "image": None,
        "__monstrous_compendium_list": True,
        "__format_as_html_list": True
    }


def _mark_mc12_blocks_to_skip(blocks: list, left_items: list, right_items: list) -> None:
    """Mark original list blocks to skip rendering.
    
    Args:
        blocks: List of blocks
        left_items: Left column items (y, text, block_idx)
        right_items: Right column items (y, text, block_idx)
    """
    blocks_to_skip = set()
    
    for y_pos, text, block_idx in left_items + right_items:
        blocks_to_skip.add(block_idx)
    
    for block_idx in blocks_to_skip:
        if block_idx < len(blocks):
            blocks[block_idx]["__skip_render"] = True
            logger.debug(f"Marked block {block_idx} to skip")
    
    # Extra check for "Plant, Carnivorous" duplication
    for block_idx, block in enumerate(blocks):
        if block.get("type") == "text":
            text = _get_block_text(block).strip()
            if text == "Plant, Carnivorous":
                if not block.get("__skip_render"):
                    logger.warning(f"⚠️  EXTRA: Marking 'Plant, Carnivorous' block {block_idx} to skip")
                    block["__skip_render"] = True
                else:
                    logger.debug(f"✓ 'Plant, Carnivorous' block {block_idx} already marked")
    
    logger.warning(f"Marked {len(blocks_to_skip)} blocks to skip")


def _extract_monstrous_compendium_list(pages: list) -> None:
    """Extract and reconstruct the two-column Monstrous Compendium 1 and 2 list.
    
    The MC1&2 header introduces an alphabetical list spanning two columns.
    Right column items appear earlier in Y-coordinates, causing intermixing.
    
    Refactored to follow best practices - broken into focused helper functions.
    
    Args:
        pages: List of page dictionaries
    """
    logger.warning("Processing Monstrous Compendium two-column list")
    
    # Find header
    page_idx, header_block_idx, header_y = _find_monstrous_compendium_header(pages)
    if page_idx is None:
        return
    
    # Get page and blocks
    page_80 = pages[page_idx]
    blocks = page_80.get("blocks", [])
    
    # Collect items from both columns
    left_items, right_items = _collect_mc12_column_items(blocks, header_block_idx, header_y)
    
    # Process items from both columns
    left_processed = _process_column_items(left_items)
    right_processed = _process_column_items(right_items)
    
    # Combine: left first, then right
    combined_list = left_processed + right_processed
    
    if not combined_list:
        logger.warning("No MC1&2 list items found")
        return
    
    # Post-processing: merge, split, filter
    merged = _merge_known_multiword_monsters(combined_list)
    split_with_comma = _split_camelcase_with_comma(merged)
    final_list = _filter_non_mc12_items(split_with_comma)
    
    if not final_list:
        logger.warning("No items after filtering")
        return
    
    # Create and insert list block
    new_block = _create_mc12_list_block(final_list, header_block_idx, header_y)
    blocks.insert(header_block_idx + 1, new_block)
    
    # Mark original blocks to skip
    _mark_mc12_blocks_to_skip(blocks, left_items, right_items)
    
    logger.warning(f"MC1&2 list complete: {len(left_items)} left, {len(right_items)} right → {len(final_list)} final")



def _get_line_text(line: dict) -> str:
    """
    Extract text from a line dictionary.
    
    Args:
        line: Line dictionary containing spans
        
    Returns:
        Combined text from all spans in the line
    """
    spans = line.get("spans", [])
    return "".join(span.get("text", "") for span in spans)


def _mark_wizard_priest_psionicist_paragraph_breaks(section_data: dict) -> None:
    """Mark lines in the Wizard, Priest, and Psionicist Encounters section that should start new paragraphs.
    
    This section should have 2 paragraphs with break at:
    1. First paragraph starts with "Spellcasters and psionicists..."
    2. "At times, an encounter..." (new paragraph)
    """
    logger.info("Processing Wizard, Priest, and Psionicist Encounters paragraph breaks")
    found_header = False
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            # Check if this is the merged header
            text = _get_block_text(block)
            
            if "Wizard, Priest, and Psionicist Encounters" in text:
                found_header = True
                logger.debug("Found Wizard, Priest, and Psionicist Encounters header")
                continue
            
            # The next text block after the header contains the content
            if found_header:
                # Check if this block contains the paragraph break marker
                if "At times," in text:
                    logger.info("Found Wizard, Priest, and Psionicist content block, marking paragraph breaks")
                    
                    # Mark the line that starts with "At times,"
                    for line_idx, line in enumerate(block.get("lines", [])):
                        line_text = _get_line_text(line).strip()
                        
                        if line_text.startswith("At times,"):
                            line["__force_line_break"] = True
                            logger.debug(f"Marked paragraph break at line {line_idx}")
                    
                    return  # Only process the first matching block
                
                # If we hit the next header, stop looking
                elif "Encounters in City-States" in text:
                    logger.debug("Reached next header without finding paragraph break")
                    return


def _mark_city_states_paragraph_breaks(section_data: dict) -> None:
    """Mark lines in the Encounters in City-States section that should start new paragraphs.
    
    This section should have 3 paragraphs with breaks at:
    1. First paragraph: "Athasian city states are usually very crowded..."
    2. "When dealing with encounters..." (new paragraph)
    3. "Specific encounters should be set up..." (new paragraph)
    """
    logger.info("Processing Encounters in City-States paragraph breaks")
    found_header = False
    marked_when_dealing = False
    marked_specific = False
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            # Check if this is the header
            text = _get_block_text(block)
            
            if "Encounters in City-States" == text.strip():
                found_header = True
                logger.debug("Found Encounters in City-States header")
                continue
            
            # Process blocks after the header until we find the next header
            if found_header:
                # If we hit the next header, stop looking
                if "Monsters" == text.strip():
                    logger.debug("Reached Monsters header - stopping")
                    return
                
                # Check if this block contains "When dealing"
                if "When dealing" in text and not marked_when_dealing:
                    logger.debug(f"Found block with 'When dealing' at block {block_idx}")
                    
                    # Mark lines that start with "When dealing"
                    for line_idx, line in enumerate(block.get("lines", [])):
                        line_text = _get_line_text(line).strip()
                        
                        if line_text.startswith("When dealing"):
                            line["__force_line_break"] = True
                            marked_when_dealing = True
                            logger.debug(f"Marked paragraph break at line {line_idx} (When dealing)")
                
                # Check if this block contains "Specific encounters"
                if "Specific encounters" in text and not marked_specific:
                    logger.debug(f"Found block with 'Specific encounters' at block {block_idx}")
                    
                    # Mark lines that start with "Specific encounters"
                    for line_idx, line in enumerate(block.get("lines", [])):
                        line_text = _get_line_text(line).strip()
                        
                        if line_text.startswith("Specific encounters"):
                            line["__force_line_break"] = True
                            marked_specific = True
                            logger.debug(f"Marked paragraph break at line {line_idx} (Specific encounters)")
                
                # If we've marked both, we can stop
                if marked_when_dealing and marked_specific:
                    logger.info("Successfully marked both paragraph breaks")
                    return


def _merge_plant_based_monsters_text(section_data: dict) -> None:
    """
    Merge the Plant-Based Monsters text into a single paragraph.
    
    The Plant-Based Monsters section has text that spans multiple blocks in the source:
    - Block 13: "Plant-Based Monsters: Defiling magic destroys"
    - Block 14: "all plant-life within its area of effect without excep-"
    - Block 15: "tion. A plant-based monster can thus be destroyed"
    - Block 16: "(or injured if it isn't wholly contained within the area"
    - Block 17: "of effect), with no save allowed."
    
    This should all be rendered as a single paragraph following the header.
    """
    logger.info("Merging Plant-Based Monsters text into single paragraph")
    
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        plant_based_idx = None
        
        # Find the Plant-Based Monsters header block
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            text = _get_block_text(block)
            if "Plant-Based Monsters:" in text:
                plant_based_idx = block_idx
                logger.debug(f"Found Plant-Based Monsters header at page {page_idx}, block {block_idx}")
                break
        
        if plant_based_idx is None:
            continue
        
        # Merge all the continuation blocks into the header block
        header_block = blocks[plant_based_idx]
        header_lines = header_block.get("lines", [])
        
        # Collect all the text spans that should be in this paragraph
        # Start with the continuation text from the header block (after "Plant-Based Monsters:")
        all_spans = []
        
        # DON'T collect spans from the header line - they're part of the header
        # The actual paragraph text starts in the next blocks
        
        # Now collect spans from all subsequent blocks until we hit the next header
        blocks_to_skip = []
        for block_idx in range(plant_based_idx + 1, len(blocks)):
            next_block = blocks[block_idx]
            next_text = _get_block_text(next_block)
            
            # Stop if we hit a header (next header will be "Monstrous Compendium 1 and 2")
            if (next_text.strip() and 
                ("Monstrous Compendium" in next_text or 
                 "__is_h2_header" in next_block or
                 "__is_monster_list" in next_block)):
                logger.debug(f"Stopping at block {block_idx} - found next header or list")
                break
            
            # Skip if this is already a skipped block
            if next_block.get("__skip_render"):
                continue
            
            # If the text looks like continuation (starts with lowercase or contains key phrases)
            if (next_text.strip() and 
                (next_text.strip()[0].islower() or 
                 "all plant-life" in next_text or 
                 "tion. A plant-based" in next_text or
                 "(or injured" in next_text or
                 "of effect)" in next_text)):
                
                logger.debug(f"Merging continuation block at index {block_idx}: {next_text[:50]}...")
                
                # Add all lines from this continuation block
                for line in next_block.get("lines", []):
                    for span in line.get("spans", []):
                        all_spans.append(span.copy())
                
                # Mark this block to be skipped during rendering
                blocks_to_skip.append(block_idx)
            else:
                # Stop if we hit text that doesn't look like continuation
                break
        
        # Mark all continuation blocks to skip
        for idx in blocks_to_skip:
            blocks[idx]["__skip_render"] = True
            logger.debug(f"Marked block {idx} to skip rendering")
        
        # Now create a single line with all the collected spans
        # Replace the lines in the header block with the header + merged paragraph
        if all_spans:
            # Keep the original header line as-is
            header_line = header_lines[0] if header_lines else {"bbox": [0, 0, 0, 0], "spans": []}
            
            # Create a new line with all the paragraph spans
            new_paragraph_line = {
                "bbox": header_line["bbox"].copy() if "bbox" in header_line else [0, 0, 0, 0],
                "spans": all_spans,
                "__merged_paragraph": True
            }
            
            # Keep both the header line AND the merged paragraph line
            header_block["lines"] = [header_line, new_paragraph_line]
            
            logger.info(f"Merged Plant-Based Monsters text into single paragraph with {len(all_spans)} spans, marked {len(blocks_to_skip)} blocks to skip")


def _get_block_text(block: dict) -> str:
    """
    Extract all text from a block dictionary.
    
    Args:
        block: Block dictionary containing lines
        
    Returns:
        Combined text from all lines in the block
    """
    text = ""
    for line in block.get("lines", []):
        text += _get_line_text(line)
    return text


def _extract_wilderness_encounter_tables(section_data: dict) -> None:
    """
    Extract and reconstruct wilderness encounter tables using reference data.
    
    The tables in the PDF are heavily fragmented and merged. We use reference data
    to properly reconstruct them with the correct die rolls and creatures.
    
    Reference data source: User-provided accurate table data
    """
    logger.warning("=" * 80)
    logger.warning("EXTRACTING WILDERNESS ENCOUNTER TABLES (Using Reference Data)")
    logger.warning("=" * 80)
    
    pages = section_data.get("pages", [])
    
    # Define the reference data for each table
    # This ensures 100% accuracy as per [REQUIREMENTS]
    table_references = {
        "Stoney Barrens": [
            ("2", "gai"),
            ("3", "bulette"),
            ("4", "roc"),
            ("5", "genie, dao"),
            ("6", "ankheg"),
            ("7", "wyvern"),
            ("8", "basilisk, lesser"),
            ("7", "spider huge"),
            ("10", "gith"),
            ("11", "ettercap/ behir"),
            ("12", "centipede, giant"),
            ("13", "beetle, boring"),
            ("14", "baazrag"),
            ("15", "tembo"),
            ("16", "braxat"),
            ("16", "bat, huge"),
            ("17", "ettin"),
            ("18", "basilisk, greater"),
            ("19", "ant, swarm"),
        ],
        "Sandy Wastes": [
            ("2", "genie, djinn"),
            ("3", "basilisk, dracolisk"),
            ("4", "spotted lion"),
            ("5", "lizard, minotaur"),
            ("6", "wasp"),
            ("7", "snake, giant constrictor"),
            ("8", "snake, constrictor"),
            ("9", "sandling"),
            ("10", "elves/gith"),
            ("11", "kank"),
            ("12", "scorpion, huge"),
            ("13", "slaves"),
            ("14", "inix"),
            ("15", "anakore"),
            ("16", "jozhal"),
            ("17", "spider, phase"),
            ("18", "centipede, megalo-"),
            ("17", "yuan-ti"),
            ("20", "dragonne"),
        ],
        "Mountains": [
            ("2", "lizard, fire"),
            ("3", "ettin"),
            ("4", "roc"),
            ("5", "ant, giant"),
            ("6", "giant-kin, cyclops"),
            ("7", "lizard, giant"),
            ("8", "leopard"),
            ("9", "beetle, fire"),
            ("10", "bat, common"),
            ("11", "halflings/dwarves"),
            ("12", "gith"),
            ("13", "slaves"),
            ("14", "kenku"),
            ("15", "spider, giant"),
            ("16", "ettercap"),
            ("17", "zombie"),
            ("18", "aarakocra"),
            ("17", "pseudodragon"),
            ("20", "bulette"),
        ],
        "Scrub Plains": [
            ("2", "genie, jann"),
            ("3", "remorhaz"),
            ("4", "behir"),
            ("5", "ant lion, giant"),
            ("6", "mekillot"),
            ("7", "silk wyrm"),
            ("8", "cheetah"),
            ("9", "erdlu"),
            ("10", "gith"),
            ("11", "elves/slaves"),
            ("12", "kank"),
            ("13", "rat, giant"),
            ("14", "jaguar"),
            ("15", "scorpion, large"),
            ("16", "spider, giant"),
            ("17", "bat, huge"),
            ("18", "plant, carnivorous, man trap"),
            ("19", "pseudodragon"),
            ("20", "gaj"),
        ],
        "Rocky Badlands": [
            ("2", "aarakocra"),
            ("3", "dragonne"),
            ("4", "giant-kin, cyclops"),
            ("5", "roc"),
            ("6", "ankheg"),
            ("7", "belgoi"),
            ("8", "lizard, giant"),
            ("9", "beetle, fire"),
            ("10", "spider, large"),
            ("11", "gith/dwarves"),
            ("12", "kluzd"),
            ("13", "rat, giant"),
            ("14", "common lion"),
            ("15", "hornet"),
            ("16", "bat, huge"),
            ("17", "braxat"),
            ("18", "giant"),
            ("19", "genie, efreeti"),
            ("20", "ant, swarm"),
        ],
        "Salt Flats": [
            ("2", "basilisk, dracolisk"),
            ("3", "zombie, juju"),
            ("4", "snake, spitting"),
            ("5", "ant, giant"),
            ("6", "wasp"),
            ("7", "wyvern"),
            ("8", "hornet"),
            ("9", "skeleton"),
            ("10", "scorpion, huge"),
            ("11", "zombie"),
            ("12", "centipede, giant"),
            ("13", "spider, large"),
            ("14", "lizard, giant"),
            ("15", "bat, large"),
            ("16", "skeleton"),
            ("17", "spider, phase"),
            ("18", "zombie, monster"),
            ("19", "remorhaz"),
            ("20", "gaj"),
        ],
    }
    
    for table_header, reference_data in table_references.items():
        logger.warning(f"🔍 Processing table: {table_header}")
        _create_wilderness_table_from_reference(pages, table_header, reference_data)
    
    logger.warning("Wilderness encounter table extraction complete")


def _create_wilderness_table_from_reference(pages: list, table_header: str, reference_data: list) -> None:
    """
    Create a wilderness encounter table using reference data.
    
    This ensures 100% extraction accuracy by using authoritative reference data
    rather than attempting to parse the heavily fragmented PDF layout.
    
    Args:
        pages: List of page dictionaries
        table_header: The header text to search for (e.g., "Stoney Barrens")
        reference_data: List of (die_roll, creature) tuples
    """
    # Find the page and block containing the table header
    header_page_idx = None
    header_block_idx = None
    
    for page_idx, page in enumerate(pages):
        blocks = page.get("blocks", [])
        for block_idx, block in enumerate(blocks):
            if block.get("type") != "text":
                continue
            
            text = _get_block_text(block).strip()
            if text == table_header:
                header_page_idx = page_idx
                header_block_idx = block_idx
                logger.warning(f"✓ Found '{table_header}' at page {page_idx}, block {block_idx}")
                break
        
        if header_page_idx is not None:
            break
    
    if header_page_idx is None:
        logger.warning(f"⚠️  Could not find header '{table_header}'")
        return
    
    # Get the page and blocks
    page = pages[header_page_idx]
    blocks = page.get("blocks", [])
    
    # Find all blocks after the header until the next section
    # Mark them all to skip rendering since we're replacing them with the table
    blocks_to_skip = []
    for block_idx in range(header_block_idx + 1, len(blocks)):
        block = blocks[block_idx]
        block_type = block.get("type")
        
        # Stop at the next section header
        if block_type == "text":
            text = _get_block_text(block).strip()
            # Check if this is another table header or major section
            if text in ["Stoney Barrens", "Sandy Wastes", "Boulder Fields", 
                       "Verdant Belts", "Mudflats", "Salt Flats", "Mountains",
                       "Scrub Plains", "Rocky Badlands"]:
                logger.debug(f"Stopping at next section: {text}")
                break
            
            # Mark this block to skip if it's in the table area
            bbox = block.get("bbox", [])
            if bbox:
                y = bbox[1]
                # If we're within the table Y-range, skip it
                # Table typically starts ~20 pixels below header
                header_bbox = blocks[header_block_idx].get("bbox", [])
                if header_bbox and y > header_bbox[3]:
                    blocks_to_skip.append(block_idx)
        
        # Limit how far we look (tables are typically ~30-40 blocks)
        if len(blocks_to_skip) > 40:
            break
    
    # Create the table structure using reference data
    rows = []
    for die_roll, creature in reference_data:
        rows.append({"die_roll": die_roll, "creature": creature})
    
    logger.warning(f"Table '{table_header}' created with {len(rows)} rows from reference data")
    
    # Create the table block
    if rows:
        _create_wilderness_table_block(blocks, header_block_idx, rows)
        
        # Mark all the table area blocks to skip rendering
        for idx in blocks_to_skip:
            if idx < len(blocks):
                blocks[idx]["__skip_render"] = True
        
        logger.warning(f"✅ Created table for '{table_header}' with {len(rows)} rows, marked {len(blocks_to_skip)} blocks to skip")


def _parse_wilderness_column_data(column_blocks: list) -> list:
    """
    Parse wilderness table data from a single PDF column.
    
    Args:
        column_blocks: List of (block_idx, block, y_coord, text) tuples
        
    Returns:
        List of row dictionaries with "die_roll" and "creature" keys
    """
    if not column_blocks:
        return []
    
    # Sort by Y-coordinate (top to bottom)
    column_blocks.sort(key=lambda x: x[2])
    
    # Skip header rows (Die Roll, Creature)
    # These are typically the first 1-2 blocks
    data_blocks = []
    for idx, block, y_coord, text in column_blocks:
        # Skip if this looks like a header
        if text in ["Die Roll", "Die Roll2", "Creature", "Creature3", "C r e a t u r e"]:
            logger.debug(f"Skipping header text: {text}")
            continue
        data_blocks.append((idx, block, y_coord, text))
    
    # Parse the data blocks into rows
    # Algorithm:
    # 1. Identify die roll values (pure numeric or range like "5-6" or "11-12")
    # 2. Following blocks are creature names until the next die roll
    
    rows = []
    current_die_roll = None
    current_creatures = []
    
    for idx, block, y_coord, text in data_blocks:
        # Clean the text (remove extra spaces)
        text = text.replace(" ", "")
        
        # Check if this is a die roll (numeric or range)
        is_die_roll = False
        if text.isdigit():
            is_die_roll = True
        elif "-" in text:
            # Check if it's a range like "5-6" or "11-12"
            parts = text.split("-")
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                is_die_roll = True
        
        if is_die_roll:
            # Save the previous row if we have one
            if current_die_roll and current_creatures:
                creature_text = ", ".join(current_creatures)
                rows.append({"die_roll": current_die_roll, "creature": creature_text})
                logger.debug(f"Parsed row: {current_die_roll} -> {creature_text}")
            
            # Start a new row
            current_die_roll = text
            current_creatures = []
        else:
            # This is a creature name
            if current_die_roll:
                # Clean up creature text
                # Handle cases like "ankhegwyvern" -> split by lowercase-uppercase transition
                creature_text = _split_merged_creature_names(text)
                current_creatures.append(creature_text)
            else:
                logger.warning(f"⚠️  Found creature text without die roll: {text}")
    
    # Don't forget the last row
    if current_die_roll and current_creatures:
        creature_text = ", ".join(current_creatures)
        rows.append({"die_roll": current_die_roll, "creature": creature_text})
        logger.debug(f"Parsed row: {current_die_roll} -> {creature_text}")
    
    return rows


def _split_merged_creature_names(text: str) -> str:
    """
    Split creature names that are merged together.
    
    Examples:
    - "ankhegwyvern" -> "ankheg/wyvern"
    - "gaibuletteroc" -> "gaibul/etteroc"
    - "ettercap/behircentipede,giantbeetle,boring" -> "ettercap/behir/centipede, giant/beetle, boring"
    
    Args:
        text: The merged creature name text
        
    Returns:
        The split and formatted creature name
    """
    # First, handle existing slashes and commas
    if "/" in text or "," in text:
        # Split by existing delimiters
        parts = []
        for part in text.replace("/", ",").split(","):
            # Check if this part has merged words
            split_part = _split_camel_case(part)
            parts.append(split_part)
        return "/".join(parts)
    
    # Otherwise, try to split by case transitions
    return _split_camel_case(text)


def _split_camel_case(text: str) -> str:
    """
    Split camelCase or merged words by detecting lowercase-to-uppercase transitions.
    
    Examples:
    - "ankhegwyvern" -> "ankheg/wyvern"
    - "giantbeetle" -> "giant/beetle"
    
    Args:
        text: The text to split
        
    Returns:
        The split text with "/" separator
    """
    if not text:
        return text
    
    result = [text[0]]
    for i in range(1, len(text)):
        prev_char = text[i-1]
        curr_char = text[i]
        
        # Insert "/" before uppercase letter if previous was lowercase
        if prev_char.islower() and curr_char.isupper():
            result.append("/")
        
        result.append(curr_char)
    
    return "".join(result)


def _create_wilderness_table_block(blocks: list, header_block_idx: int, rows: list) -> None:
    """
    Create a table block structure for the wilderness encounter table.
    
    Args:
        blocks: List of blocks in the page
        header_block_idx: Index of the header block
        rows: List of row dictionaries with "die_roll" and "creature" keys
    """
    # Create table rows
    table_rows = []
    
    # Header row
    header_row = {
        "cells": [
            {"text": "Die Roll"},
            {"text": "Creature"}
        ]
    }
    table_rows.append(header_row)
    
    # Data rows
    for row_data in rows:
        data_row = {
            "cells": [
                {"text": row_data["die_roll"]},
                {"text": row_data["creature"]}
            ]
        }
        table_rows.append(data_row)
    
    # Create the table structure
    header_block = blocks[header_block_idx]
    header_bbox = header_block.get("bbox", [44.0, 600.0, 300.0, 610.0])
    
    table_bbox = [
        header_bbox[0],  # Same left x
        header_bbox[3] + 5.0,  # Start just below header
        header_bbox[2] + 200.0,  # Extend to the right
        header_bbox[3] + 15.0 * len(table_rows)  # Extend downward based on row count
    ]
    
    table = {
        "rows": table_rows,
        "header_rows": 1,
        "bbox": table_bbox
    }
    
    # Attach the table to the header block
    header_block["__wilderness_encounter_table"] = table
    logger.warning(f"✅ Attached wilderness encounter table with {len(rows)} data rows")


