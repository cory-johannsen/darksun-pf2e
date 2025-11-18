"""
Race-specific experience award processing for Chapter 8.

This module handles extraction of race-specific experience award tables.
"""

from __future__ import annotations

from .tables import extract_race_tables_from_page, insert_race_tables_into_blocks


def extract_race_award_tables(section_data: dict) -> None:
    """
    Extract and structure the Individual Race Awards tables.
    
    Similar to class award tables, but for races (Dwarf, Elf, Half-elf, etc.)
    Each race has a table with Action and Awards columns.
    """
    logger.info("Extracting Chapter 8 Individual Race Awards tables")
    
    with open('/tmp/chapter8_race_processing_debug.txt', 'w') as f:
        f.write("_extract_race_award_tables called\n")
        
        pages = section_data.get("pages", [])
        f.write(f"Found {len(pages)} pages\n")
        if not pages:
            f.write("No pages, returning\n")
            return
        
        # Search ALL pages for "Individual Race Awards"
        found_on_page = None
        for page_idx, page in enumerate(pages):
            blocks = page.get("blocks", [])
            for block_idx, block in enumerate(blocks):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if "Individual Race Awards" in text:
                            found_on_page = page_idx
                            f.write(f"Found 'Individual Race Awards' on page {page_idx}, block {block_idx}\n")
                            break
                if found_on_page is not None:
                    break
            if found_on_page is not None:
                break
        
        if found_on_page is None:
            f.write("ERROR: 'Individual Race Awards' not found on ANY page!\n")
            return
        
        # Process the page that contains the race awards
        f.write(f"Processing page {found_on_page} for race awards\n")
        blocks_before = len(pages[found_on_page].get('blocks', []))
        extract_race_tables_from_page(pages[found_on_page], page_num=found_on_page)
        blocks_after = len(pages[found_on_page].get('blocks', []))
        f.write(f"Page {found_on_page}: {blocks_before} blocks before, {blocks_after} blocks after\n")
        
        f.write("_extract_race_award_tables completed\n")




