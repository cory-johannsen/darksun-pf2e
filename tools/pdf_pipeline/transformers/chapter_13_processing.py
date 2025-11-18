"""
Chapter 13 Processing - Vision and Light

This module handles the extraction and transformation of Chapter 13,
which contains visibility ranges and lighting conditions for Dark Sun.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def _merge_intro_paragraphs(pages: List[Dict[str, Any]]) -> None:
    """
    Merge the intro paragraph that spans across columns.
    
    The text "All of the conditions presented on the Visibility Ranges table 
    in the Player's Handbook exist on" (left column) and "Athas. However, there 
    are a number of conditions unique to Athas that should be added." (right column)
    should be merged into a single paragraph.
    """
    logger.info("Merging Chapter 13 intro paragraphs")
    
    if not pages:
        return
    
    page = pages[0]
    blocks = page.get("blocks", [])
    
    # Find the two blocks to merge
    left_block_idx = None
    right_block_idx = None
    
    for idx, block in enumerate(blocks):
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Get all text from the block
        block_text = ""
        for line in lines:
            for span in line.get("spans", []):
                block_text += span.get("text", "")
        
        # Check for the left column text
        if "All of the conditions presented" in block_text:
            left_block_idx = idx
            logger.debug(f"Found left block at index {idx}")
        
        # Check for the right column text
        if "Athas. However, there are a number" in block_text:
            right_block_idx = idx
            logger.debug(f"Found right block at index {idx}")
    
    if left_block_idx is not None and right_block_idx is not None:
        # Merge the text
        left_block = blocks[left_block_idx]
        right_block = blocks[right_block_idx]
        
        # Append right block lines to left block
        left_block["lines"].extend(right_block["lines"])
        
        # Update bbox to encompass both blocks
        left_bbox = left_block["bbox"]
        right_bbox = right_block["bbox"]
        left_block["bbox"] = [
            min(left_bbox[0], right_bbox[0]),
            min(left_bbox[1], right_bbox[1]),
            max(left_bbox[2], right_bbox[2]),
            max(left_bbox[3], right_bbox[3])
        ]
        
        # Remove the right block by zeroing its bbox
        blocks[right_block_idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]
        
        logger.info("Successfully merged intro paragraphs")


def _mark_visibility_ranges_as_h2(pages: List[Dict[str, Any]]) -> None:
    """
    Mark "Dark Sun Visibility Ranges" as an H2 header.
    """
    logger.info("Marking 'Dark Sun Visibility Ranges' as H2")
    
    if not pages:
        return
    
    page = pages[0]
    blocks = page.get("blocks", [])
    
    for block in blocks:
        lines = block.get("lines", [])
        for line in lines:
            spans = line.get("spans", [])
            for span in spans:
                if span.get("text", "") == "Dark Sun Visibility Ranges":
                    # Mark as H2 by setting a special flag
                    span["is_h2"] = True
                    # Increase size slightly to match H2
                    span["size"] = 12.0
                    logger.info("Marked 'Dark Sun Visibility Ranges' as H2")
                    return


def _extract_visibility_table(pages: List[Dict[str, Any]]) -> None:
    """
    Extract and reconstruct the Dark Sun Visibility Ranges table.
    
    The table has 6 columns: Condition, Movement, Spotted, Type, ID, Detail
    and 6 rows (including header).
    """
    logger.info("Extracting Dark Sun Visibility Ranges table")
    
    if not pages:
        return
    
    page = pages[0]
    blocks = page.get("blocks", [])
    
    # Find all blocks that contain table data
    # We need to collect: headers and data rows
    condition_block_idx = None
    movement_block_idx = None
    table_header_block_idx = None
    movement_column_idx = None
    data_columns_idx = None
    
    for idx, block in enumerate(blocks):
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check for header text
        for line in lines:
            spans = line.get("spans", [])
            for span in spans:
                text = span.get("text", "")
                
                # Find the Condition header (left side)
                if text == "Condition" and span.get("color") == "#ca5804":
                    condition_block_idx = idx
                    logger.debug(f"Found Condition header at block {idx}")
                
                # Find Movement header (might be with Condition or separate)
                if text == "Movement" and span.get("color") == "#ca5804":
                    movement_block_idx = idx
                    logger.debug(f"Found Movement header at block {idx}")
                
                # Find the other headers (Spotted, Type, ID, Detail) on right side
                if text in ["Spotted", "Type", "Detail"] or "I D" in text:
                    table_header_block_idx = idx
                    logger.debug(f"Found right-side headers at block {idx}")
    
    # Now reconstruct the table
    # The table structure in the PDF is:
    # - Left column: Condition values and Movement values
    # - Right columns: Spotted, Type, ID, Detail values
    
    # Find blocks with condition values (Sand, blowing; Sandstorm, mild; etc.)
    condition_values = []
    movement_values = []
    
    for idx, block in enumerate(blocks):
        lines = block.get("lines", [])
        for line in lines:
            spans = line.get("spans", [])
            for span in spans:
                text = span.get("text", "")
                color = span.get("color", "")
                
                # Condition values (contain comma and are black text)
                if "," in text and color == "#000000" and "blowing" in text:
                    condition_values.append(("Sand, blowing", line["bbox"][1]))
                elif "," in text and color == "#000000" and "Sandstorm" in text and "mild" in text:
                    condition_values.append(("Sandstorm, mild", line["bbox"][1]))
                elif "," in text and color == "#000000" and "Sandstorm" in text and "driving" in text:
                    condition_values.append(("Sandstorm, driving", line["bbox"][1]))
                elif "," in text and color == "#000000" and "Night" in text and "moons" in text:
                    condition_values.append(("Night, both moons", line["bbox"][1]))
                elif "," in text and color == "#000000" and "Silt Sea" in text and "calm" in text:
                    condition_values.append(("Silt Sea, calm", line["bbox"][1]))
                elif "," in text and color == "#000000" and "Silt Sea" in text and "rolling" in text:
                    condition_values.append(("Silt Sea, rolling", line["bbox"][1]))
    
    logger.info(f"Found {len(condition_values)} condition values")
    
    # Instead of reconstructing the table in the raw data, we'll handle this in postprocessing
    # Mark the blocks that need special handling
    for block in blocks:
        lines = block.get("lines", [])
        for line in lines:
            spans = line.get("spans", [])
            for span in spans:
                text = span.get("text", "")
                
                # Mark table header spans
                if text in ["Condition", "Movement", "Spotted", "Type", "Detail"] or "I D" in text:
                    if span.get("color") == "#ca5804":
                        span["is_table_header"] = True
                        # Remove these from regular rendering - they'll be in the table
                        span["__skip_render"] = True
                
                # Mark condition value spans
                if "," in text and any(cond in text for cond in 
                    ["Sand", "Sandstorm", "Night", "Silt Sea"]):
                    span["is_table_data"] = True
                    span["__skip_render"] = True
                
                # Mark numeric spans in table area (y > 244 and y < 322)
                bbox = line.get("bbox", [0, 0, 0, 0])
                if bbox[1] > 244 and bbox[1] < 322 and text.strip().isdigit():
                    span["is_table_data"] = True
                    span["__skip_render"] = True
    
    logger.info("Marked table elements for special handling")


def apply_chapter_13_adjustments(section_data: dict) -> None:
    """
    Apply all Chapter 13 specific adjustments to the section data.
    
    This function:
    1. Merges the intro paragraph that spans columns
    2. Marks "Dark Sun Visibility Ranges" as H2
    3. Extracts and prepares the visibility table data
    
    Args:
        section_data: The section data dictionary with 'pages' key
    """
    logger.info("=== apply_chapter_13_adjustments called ===")
    
    # Check if already adjusted
    if section_data.get("__chapter_13_adjusted"):
        logger.warning("Chapter 13 already adjusted, skipping")
        return
    
    pages = section_data.get("pages", [])
    if not pages:
        logger.warning("No pages found in Chapter 13")
        return
    
    logger.info(f"Chapter 13 has {len(pages)} page(s)")
    
    # Apply adjustments
    _merge_intro_paragraphs(pages)
    _mark_visibility_ranges_as_h2(pages)
    _extract_visibility_table(pages)
    
    # Mark as adjusted to prevent double-processing
    section_data["__chapter_13_adjusted"] = True
    
    logger.info("Chapter 13 adjustments complete")


def process_chapter_13(section_data: dict) -> dict:
    """
    Process Chapter 13: Vision and Light.
    
    This is the main entry point for Chapter 13 processing.
    
    Args:
        section_data: The raw section data
        
    Returns:
        The processed section data
    """
    logger.info("Processing Chapter 13: Vision and Light")
    
    apply_chapter_13_adjustments(section_data)
    
    return section_data

