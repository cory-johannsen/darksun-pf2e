"""
Common utility functions for Chapter 6 processing.

This module contains shared utility functions used across all Chapter 6 processors.
"""

from __future__ import annotations

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)


def normalize_plain_text(text: str) -> str:
    """Normalize text by replacing special characters."""
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u2018', "'")  # Left single quotation mark
    text = text.replace('\u201c', '"')  # Left double quotation mark
    text = text.replace('\u201d', '"')  # Right double quotation mark
    text = text.replace('\u2013', '-')  # En dash
    text = text.replace('\u2014', '--')  # Em dash
    text = text.replace('\xad', '')  # Soft hyphen
    # Remove extraneous whitespace (e.g., "D a i l y" -> "Daily")
    text = re.sub(r'(?<=[A-Za-z])\s+(?=[A-Za-z])', lambda m: '' if len(m.group(0).strip()) == 0 and all(len(word) == 1 for word in m.string[max(0, m.start()-5):m.end()+5].split()) else m.group(0), text)
    return text




def clean_whitespace(text: str) -> str:
    """Clean extraneous whitespace from text."""
    # Remove spaces between single letters (e.g., "D a i l y" -> "Daily")
    text = re.sub(r'\b([A-Za-z])\s+(?=[A-Za-z]\b)', r'\1', text)
    # Remove spaces in numbers with units (e.g., "1 c p" -> "1 cp")
    text = re.sub(r'(\d+)\s+([a-z])\s+([a-z])\b', r'\1 \2\3', text)
    # Remove space before p in "c p" -> "cp"
    text = re.sub(r'\bc\s+p\b', 'cp', text)
    # Remove space before p in "s p" -> "sp"
    text = re.sub(r'\bs\s+p\b', 'sp', text)
    return text.strip()




def adjust_header_sizes(section_data: dict) -> None:
    """Adjust header font sizes for Monetary Systems section headers.
    
    Adjustments:
    - Barter:, Simple Barter:, Protracted Barter: -> H2 (size 10.8)
    - Common Wages -> H3 (size 9.6)
    - Service: -> H2 (size 10.8, also needs to be separated from surrounding text)
    - Initial Character Funds -> H2 (size 10.8)
    - Weapons (after Athasian Market) -> H2 (size 10.8)
    - Armor section headers -> H2 (size 10.8)
    - Household Provisions -> H2 (size 10.8)
    - Tack and Harness -> H2 (size 10.8)
    - Transport -> H2 (size 10.8)
    - Barding (first occurrence after Tack and Harness) -> H3 (size 9.6)
    - Barding: (second occurrence in descriptions) -> keep as is (size 8.88, colored)
    - Tun of Water: -> H3 (size 9.6) in Equipment Descriptions
    - Fire Kit: -> H3 (size 9.6) in Equipment Descriptions
    - Chariot:, Howdah: -> H3 (size 9.6) in Equipment Descriptions > Transportation
    - Erdlu:, Inix:, Kank:, Mekillot: -> H3 (size 9.6) in Equipment Descriptions > Animals
    - Chatkcha:, Gythka:, Impaler:, Quabone:, Wrist Razor: -> H3 (size 9.6) in Equipment Descriptions > Weapons
    """
    found_athasian_market = False
    found_animals_h2 = False
    found_tack_and_harness_h2 = False
    found_equipment_descriptions = False
    found_household_provisions_h2_in_descriptions = False
    found_transportation_h2_in_descriptions = False
    found_animals_h2_in_descriptions = False
    found_weapons_in_descriptions = False
    barding_h3_applied = False
    
    # List of armor headers that should be H2
    armor_h2_headers = [
        "Alternate Materials:",
        "Shields:",
        "Leather Armor:",
        "Padded Armor:",
        "Hide Armor:",
        "Studded Leather, Ring Mail, Brigandine, and Scale Mail Armor:",
        "Chain, Splint, Banded, Bronze Plate, or Plate Mail; Field Plate and Full Plate Armor:"
    ]
    
    # New Equipment section H2 headers
    new_equipment_h2_headers = [
        "Household Provisions",
        "Tack and Harness",
        "Transport",
        "Animals"
    ]
    
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = normalize_plain_text(span.get("text", ""))
                    
                    # Track when we pass the Athasian Market header
                    if "Athasian Market" in text and "Provisions" in text:
                        found_athasian_market = True
                    
                    # Track when we pass the H2 "Animals" header (size 10.8)
                    if text.strip() == "Animals" and abs(span.get("size", 0) - 10.8) < 0.1:
                        found_animals_h2 = True
                    
                    # Track when we pass the H2 "Tack and Harness" header (size 10.8)
                    if text.strip() == "Tack and Harness" and abs(span.get("size", 0) - 10.8) < 0.1:
                        found_tack_and_harness_h2 = True
                    
                    # Track when we reach the Equipment Descriptions section
                    if "Equipment Descriptions" in text:
                        found_equipment_descriptions = True
                    
                    # Track when we reach Household Provisions in Equipment Descriptions
                    # Note: This header has size 8.88, not 10.8
                    if found_equipment_descriptions and text.strip() == "Household Provisions":
                        found_household_provisions_h2_in_descriptions = True
                    
                    # Track when we reach Transportation in Equipment Descriptions
                    if found_equipment_descriptions and text.strip() == "Transportation":
                        found_transportation_h2_in_descriptions = True
                    
                    # Track when we reach Animals in Equipment Descriptions
                    # (second occurrence of Animals, the H2 after Transportation)
                    if found_equipment_descriptions and found_transportation_h2_in_descriptions and text.strip() == "Animals":
                        found_animals_h2_in_descriptions = True
                    
                    # Track when we reach Weapons in Equipment Descriptions
                    # (third occurrence of Weapons, after Animals in Equipment Descriptions)
                    if found_equipment_descriptions and found_animals_h2_in_descriptions and text.strip() == "Weapons":
                        found_weapons_in_descriptions = True
                    
                    # Adjust headers that should be H2 (10.8) - exact match
                    if text.strip() in ["Barter:", "Simple Barter:", "Protracted Barter:", "Common Wages", "Initial Character Funds", "Metal Armor in Dark Sun:"] + armor_h2_headers + new_equipment_h2_headers:
                        span["size"] = 10.8
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust "Barding" (without colon) to H3 ONLY if it appears after H2 "Tack and Harness"
                    # and we haven't already applied this adjustment
                    elif text.strip() == "Barding" and found_tack_and_harness_h2 and not barding_h3_applied:
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                        barding_h3_applied = True
                    
                    # Adjust headers that should be H3 (9.6) - exact match
                    elif text.strip() in ["Common Wages", "Barding:"]:
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust Tun of Water: and Fire Kit: to H3 when in Equipment Descriptions > Household Provisions
                    # Note: text may have trailing space after colon
                    # This adjustment is no longer necessary as the HTML rendering handles it via pattern matching
                    # in _apply_subheader_styling(), but we keep it for consistency with the intent
                    elif found_household_provisions_h2_in_descriptions and (text.strip() in ["Tun of Water:", "Fire Kit:"] or text.startswith(("Tun of Water:", "Fire Kit:"))):
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust Chariot: and Howdah: to H3 when in Equipment Descriptions > Transportation
                    elif found_transportation_h2_in_descriptions and (text.strip() in ["Chariot:", "Howdah:"] or text.startswith(("Chariot:", "Howdah:"))):
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust Erdlu:, Inix:, Kank:, Mekillot: to H3 when in Equipment Descriptions > Animals
                    elif found_animals_h2_in_descriptions and (text.strip() in ["Erdlu:", "Inix:", "Kank:", "Mekillot:"] or text.startswith(("Erdlu:", "Inix:", "Kank:", "Mekillot:"))):
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust Chatkcha:, Gythka:, Impaler:, Quabone:, Wrist Razor: to H3 when in Equipment Descriptions > Weapons
                    elif found_weapons_in_descriptions and (text.strip() in ["Chatkcha:", "Gythka:", "Impaler:", "Quabone:", "Wrist Razor:"] or text.startswith(("Chatkcha:", "Gythka:", "Impaler:", "Quabone:", "Wrist Razor:"))):
                        span["size"] = 9.6
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Armor headers that start with these patterns (for headers with content after colon)
                    elif any(text.strip().startswith(header) for header in ["Hide Armor:", "Leather Armor:", "Padded Armor:"]):
                        span["size"] = 10.8
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Adjust "Weapons" header after Athasian Market to H2 (first occurrence)
                    elif text.strip() == "Weapons" and found_athasian_market and not found_animals_h2 and abs(span.get("size", 0) - 11.76) < 0.1:
                        span["size"] = 10.8
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                        found_athasian_market = False  # Reset so we don't adjust other "Weapons" headers
                    
                    # Adjust "Weapons" header after Animals to H2 (second occurrence)
                    elif text.strip() == "Weapons" and found_animals_h2 and abs(span.get("size", 0) - 11.76) < 0.1:
                        span["size"] = 10.8
                        span["font"] = "MSTT31c501"  # Header font
                        span["color"] = "#ca5804"     # Header color to ensure anchoring
                    
                    # Handle Service: which is embedded in text
                    elif text.startswith("Service: "):
                        # Split this span into two: header and content
                        split_service_header(line, span)
                    
                    # Handle Shields: which is embedded in text after "Alternate Materials:"
                    elif "Shields:" in text and text.strip().startswith("Shields:"):
                        # Split this span into two: header and content
                        split_shields_header(line, span)




def split_service_header(line: dict, span: dict) -> None:
    """Split 'Service: ...' text into separate header and content spans."""
    text = span.get("text", "")
    if not text.startswith("Service: "):
        return
    
    # Find all spans in the line
    spans = line.get("spans", [])
    span_idx = spans.index(span)
    
    # Split the text
    header_text = "Service:"
    content_text = text[len("Service:"):]  # Keep the space and rest of text
    
    # Create new header span
    header_span = {
        "text": header_text,
        "font": "MSTT31c501",  # Header font
        "size": 10.8,  # H2 size
        "flags": 4,
        "color": "#ca5804",  # Header color
        "ascender": 0.800000011920929,
        "descender": -0.20000000298023224
    }
    
    # Update the original span to only contain content
    span["text"] = content_text
    
    # Insert the header span before the content span
    spans.insert(span_idx, header_span)




def split_shields_header(line: dict, span: dict) -> None:
    """Split 'Shields: ...' text into separate header and content spans."""
    text = span.get("text", "")
    if not text.strip().startswith("Shields:"):
        return
    
    # Find all spans in the line
    spans = line.get("spans", [])
    span_idx = spans.index(span)
    
    # Split the text
    header_text = "Shields:"
    content_text = text[text.index("Shields:") + len("Shields:"):]  # Keep the space and rest of text
    
    # Create new header span
    header_span = {
        "text": header_text,
        "font": "MSTT31c576",  # Bold font
        "size": 10.8,  # H2 size
        "flags": 4,
        "color": "#ca5804",  # Header color
        "ascender": 0.800000011920929,
        "descender": -0.20000000298023224
    }
    
    # Update the original span to only contain content
    span["text"] = content_text
    
    # Insert the header span before the content span
    spans.insert(span_idx, header_span)




def get_block_text(block: dict) -> str:
    """Get all text from a block."""
    text = ""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            text += span.get("text", "")
    return text




def merge_studded_leather_header(blocks: List[dict], start_idx: int, page: dict) -> None:
    """Merge 'Studded Leather...' + 'Scale' + 'Mail' + 'Armor:' into single header."""
    # Create merged header text
    merged_text = "Studded Leather, Ring Mail, Brigandine, and Scale Mail Armor:"
    
    # Get the first block's line and span structure
    first_block = blocks[start_idx]
    if not first_block.get("lines"):
        return
    
    first_line = first_block["lines"][0]
    if not first_line.get("spans"):
        return
    
    # Update the first span with the merged text
    first_span = first_line["spans"][0]
    first_span["text"] = merged_text
    first_span["size"] = 10.8  # H2 size
    first_span["font"] = "MSTT31c501"  # Header font
    
    # Remove the next 3 blocks (Scale, Mail, Armor:)
    for _ in range(min(3, len(blocks) - start_idx - 1)):
        if start_idx + 1 < len(blocks):
            blocks.pop(start_idx + 1)




def merge_chain_splint_header(blocks: List[dict], start_idx: int, page: dict) -> None:
    """Merge 'Chain, Splint...' + 'Mail; Field Plate...' into single header."""
    # Create merged header text
    merged_text = "Chain, Splint, Banded, Bronze Plate, or Plate Mail; Field Plate and Full Plate Armor:"
    
    # Get the first block's line and span structure
    first_block = blocks[start_idx]
    if not first_block.get("lines"):
        return
    
    first_line = first_block["lines"][0]
    if not first_line.get("spans"):
        return
    
    # Update the first span with the merged text
    first_span = first_line["spans"][0]
    first_span["text"] = merged_text
    first_span["size"] = 10.8  # H2 size
    first_span["font"] = "MSTT31c501"  # Header font
    
    # Remove the next block (Mail; Field Plate...)
    if start_idx + 1 < len(blocks):
        blocks.pop(start_idx + 1)




def extract_table_cell_text(blocks: List[dict], start_idx: int, end_idx: int) -> List[List[str]]:
    """Extract table cell text from blocks, cleaning up whitespace."""
    rows = []
    for idx in range(start_idx, min(end_idx, len(blocks))):
        block = blocks[idx]
        if block.get("type") != "text":
            continue
        
        for line in block.get("lines", []):
            row_cells = []
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                # Clean up whitespace issues
                text = clean_whitespace(text)
                if text:
                    row_cells.append(text)
            if row_cells:
                rows.append(row_cells)
    return rows




def merge_armor_headers(section_data: dict) -> None:
    """Merge fragmented armor headers into single H2 headers."""
    with open('/tmp/chapter6_debug.txt', 'a') as f:
        f.write(f"\n=== merge_armor_headers called ===\n")
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        blocks = page.get("blocks", [])
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"  Page {page_idx}: {len(blocks)} blocks\n")
        
        i = 0
        while i < len(blocks):
            if blocks[i].get("type") != "text":
                i += 1
                continue
            
            text1 = get_block_text(blocks[i]).strip()
            
            # Debug: Log all headers we find
            if blocks[i].get("lines") and blocks[i]["lines"][0].get("spans"):
                first_span = blocks[i]["lines"][0]["spans"][0]
                if first_span.get("color") == "#ca5804":  # Header color
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"    Found header at block {i}: '{text1[:50]}'\n")
            
            # Check for "Studded Leather, Ring Mail, Brigandine, and" + "Scale" + "Mail" + "Armor:"
            if i + 3 < len(blocks):
                text2 = get_block_text(blocks[i+1]).strip() if i+1 < len(blocks) else ""
                text3 = get_block_text(blocks[i+2]).strip() if i+2 < len(blocks) else ""
                text4 = get_block_text(blocks[i+3]).strip() if i+3 < len(blocks) else ""
                
                if ("Studded Leather, Ring Mail, Brigandine, and" in text1 and
                    "Scale" in text2 and
                    "Mail" in text3):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"    MERGING Studded Leather header at block {i}\n")
                    # Merge these into one header
                    merge_studded_leather_header(blocks, i, page)
                    continue
            
            # Check for "Chain, Splint, Banded, Bronze Plate, or Plate" + "Mail; Field Plate and Full Plate Armor:"
            if i + 1 < len(blocks):
                text2 = get_block_text(blocks[i+1]).strip() if i+1 < len(blocks) else ""
                
                if ("Chain, Splint, Banded, Bronze Plate, or Plate" in text1 and
                    "Mail; Field Plate and Full Plate Armor:" in text2):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"    MERGING Chain Splint header at block {i}\n")
                    # Merge these into one header
                    merge_chain_splint_header(blocks, i, page)
                    continue
            
            i += 1




