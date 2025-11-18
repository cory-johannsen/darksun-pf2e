"""
Chapter 5: Monsters of Athas - Data Processing

Reconstructs monster stat tables from fragmented text blocks during transformation.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Monster names to detect
MONSTER_NAMES = [
    "Belgoi", "Braxat", "Dragon of Tyr", "Dune Freak (Anakore)",
    "Gaj", "Giant, Athasian", "Gith", "Jozhal", "Silk Wyrm", "Tembo"
]

# Monster stats labels in order (21 rows)
MONSTER_STATS_LABELS = [
    "CLIMATE/TERRAIN",
    "FREQUENCY",
    "ORGANIZATION",
    "ACTIVITY CYCLE",
    "DIET",
    "INTELLIGENCE",
    "TREASURE",
    "ALIGNMENT",
    "NO. APPEARING",
    "ARMOR CLASS",
    "MOVEMENT",
    "HIT DICE",
    "THAC0",
    "NO. OF ATTACKS",
    "DAMAGE/ATTACK",
    "SPECIAL ATTACKS",
    "SPECIAL DEFENSES",
    "MAGIC RESISTANCE",
    "SIZE",
    "MORALE",
    "XP VALUE"
]


def _extract_text_from_blocks(blocks: List[Dict]) -> str:
    """Extract plain text from a list of blocks."""
    text_parts = []
    for block in blocks:
        if block.get("type") == "text":
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text_parts.append(span.get("text", ""))
    return " ".join(text_parts)


def _is_monster_stat_block(block: Dict) -> bool:
    """Check if a block contains monster stat labels."""
    text = _extract_text_from_blocks([block])
    # Check for at least 3 stat labels
    label_count = sum(1 for label in MONSTER_STATS_LABELS[:10] if label in text)
    return label_count >= 3


def _find_monster_on_page(page: Dict) -> Optional[str]:
    """
    Check if this page contains a monster manual entry.
    
    Returns:
        Monster name if found, None otherwise
    """
    text = _extract_text_from_blocks(page.get("blocks", []))
    
    for monster_name in MONSTER_NAMES:
        if monster_name in text:
            return monster_name
    
    return None


def _find_monster_stat_blocks(page: Dict) -> List[Tuple[int, int]]:
    """
    Find ranges of blocks that contain monster stats.
    
    If a monster name is found on the page, treats all text blocks
    up to the description as potential stat blocks.
    
    Returns:
        List of (start_idx, end_idx) tuples for monster stat block ranges
    """
    monster_name = _find_monster_on_page(page)
    
    if not monster_name:
        return []
    
    print(f"  🐉 Found monster: {monster_name}")
    
    blocks = page.get("blocks", [])
    
    # Find where the description starts (usually after stats)
    desc_markers = ["At first sight", "It is difficult to tell", "Fortunately, there is only",
                    "The anakore are", "The gaj is a psionic", "Athasian giants come",
                    "The gith are a race", "This small lizard", "The silk wyrm is a snake",
                    "The tembo is a despicable"]
    
    desc_start_idx = None
    for idx, block in enumerate(blocks):
        block_text = _extract_text_from_blocks([block])
        for marker in desc_markers:
            if marker in block_text:
                desc_start_idx = idx
                break
        if desc_start_idx is not None:
            break
    
    # If description found, stats are everything before it
    # Otherwise, take first N blocks (stats are typically at top of page)
    if desc_start_idx:
        print(f"  📍 Description starts at block {desc_start_idx}")
        return [(0, desc_start_idx)]
    else:
        # Take first 20 blocks as likely stats area
        print(f"  📍 No description marker found, using first 20 blocks")
        return [(0, min(20, len(blocks)))]


def _parse_monster_stats_from_text(text: str) -> Dict[str, str]:
    """
    Parse monster stats from text using regex patterns.
    Handles both "LABEL: VALUE" and "VALUE LABEL:" formats.
    """
    stats = {}
    
    # Normalize common spacing issues
    text = re.sub(r'MOR\s+A\s+L\s+E', 'MORALE', text)
    text = re.sub(r'TRE\s+AS\s+U\s+R\s+E', 'TREASURE', text)
    
    for i, label in enumerate(MONSTER_STATS_LABELS):
        # Create pattern that matches the label with optional colon/semicolon
        label_pattern = label.replace('/', r'\s*/\s*').replace(' ', r'\s+')
        
        # Try to find the value after the label
        if i < len(MONSTER_STATS_LABELS) - 1:
            next_label = MONSTER_STATS_LABELS[i + 1]
            next_pattern = next_label.replace('/', r'\s*/\s*').replace(' ', r'\s+')
            # Match everything between this label and the next
            pattern = rf'{label_pattern}\s*[:;]?\s*(.*?)(?={next_pattern}\s*[:;]?|$)'
        else:
            # Last stat - match until description starts
            pattern = rf'{label_pattern}\s*[:;]?\s*(.*?)(?=PSIONICS\s+SUMMARY|Combat:|Habitat|Ecology|$)'
        
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Clean up the value
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = re.sub(r'[:;]\s*$', '', value)  # Remove trailing colons
            stats[label] = value
        else:
            stats[label] = ""
    
    return stats


def _create_monster_stats_table(stats: Dict[str, str]) -> Dict:
    """
    Create a table structure from parsed monster stats.
    
    Returns:
        Table dict with rows and cells
    """
    rows = []
    
    for label in MONSTER_STATS_LABELS:
        value = stats.get(label, "")
        rows.append({
            "cells": [
                {"text": f"{label}:", "bold": True},
                {"text": value, "bold": False}
            ]
        })
    
    return {
        "bbox": [0, 0, 0, 0],  # Placeholder bbox
        "rows": rows,
        "header_rows": 0
    }


def _reconstruct_monster_stat_tables(page: Dict) -> None:
    """
    Find monster stat blocks in a page and convert them to table structures.
    Modifies the page dict in place.
    """
    blocks = page.get("blocks", [])
    if not blocks:
        return
    
    # Find ranges of blocks that contain monster stats
    stat_ranges = _find_monster_stat_blocks(page)
    
    if not stat_ranges:
        return
    
    logger.info(f"Found {len(stat_ranges)} monster stat block ranges on page {page.get('page_number')}")
    
    # Process ranges in reverse to avoid index shifting
    for start_idx, end_idx in reversed(stat_ranges):
        # Extract text from all blocks in this range
        stat_blocks = blocks[start_idx:end_idx]
        text = _extract_text_from_blocks(stat_blocks)
        
        logger.debug(f"Processing monster stats from blocks {start_idx}-{end_idx}")
        logger.debug(f"Extracted text (first 200 chars): {text[:200]}")
        
        # Parse the stats
        stats = _parse_monster_stats_from_text(text)
        
        # Count non-empty stats
        filled_count = sum(1 for v in stats.values() if v)
        logger.info(f"Parsed {filled_count}/21 monster stats")
        
        # Create table structure
        table = _create_monster_stats_table(stats)
        
        # Attach the table to the first block in the range
        # This is the pattern used by other chapters (e.g., Rangers Followers table)
        first_block = stat_blocks[0]
        first_block["__monster_stats_table"] = table
        
        print(f"  ✅ Attached table to block at index {start_idx}")
        print(f"     Block type: {first_block.get('type')}")
        print(f"     Block has lines: {bool(first_block.get('lines'))}")
        print(f"     Table marker present: {'__monster_stats_table' in first_block}")
        print(f"     Table has {len(table['rows'])} rows")
        
        # Mark other blocks in the range to skip rendering
        for block in stat_blocks[1:]:
            block["__skip_render"] = True
        
        logger.info(f"✅ Attached monster stats table to block {start_idx}, marked {len(stat_blocks)-1} blocks to skip")


def apply_chapter_5_adjustments(section_data: Dict) -> None:
    """
    Apply Chapter 5 specific adjustments to section data.
    
    Reconstructs monster stat tables from fragmented text blocks.
    """
    print("\n" + "="*80)
    print("🐉 CHAPTER 5 PROCESSING STARTED")
    print("="*80)
    logger.info("Applying Chapter 5 (Monsters of Athas) adjustments")
    
    pages = section_data.get("pages", [])
    print(f"Processing {len(pages)} pages")
    
    for page in pages:
        print(f"Processing page {page.get('page_number')}")
        _reconstruct_monster_stat_tables(page)
    
    logger.info("✅ Completed Chapter 5 adjustments")
    print("="*80)
    print("✅ CHAPTER 5 PROCESSING COMPLETE")
    print("="*80 + "\n")

