"""
Class-specific experience award processing for Chapter 8.

This module handles extraction of class-specific experience award tables.
"""

from __future__ import annotations

from .tables import extract_tables_from_page, pair_table_columns, insert_tables_into_blocks


def extract_class_award_tables(section_data: dict) -> None:
    """
    Extract and structure the Individual Class Awards tables.
    
    The tables are embedded in the text as separate blocks. We need to:
    1. Identify class award headers (e.g., "All Warriors:")
    2. Group subsequent action/award text blocks into table rows
    3. Create proper table structures with markers for rendering
    """
    logger.info("Extracting Chapter 8 Individual Class Awards tables")
    
    with open('/tmp/chapter8_processing_debug.txt', 'w') as f:
        f.write("apply_chapter_8_adjustments called\n")
        
        pages = section_data.get("pages", [])
        f.write(f"Found {len(pages)} pages\n")
        if not pages:
            f.write("No pages, returning\n")
            return
        
        # Suppress ALL original PDF-extracted tables from ALL pages
        # These tables are malformed and incorrectly pair intro text with table data
        # We'll create our own properly structured tables instead
        for page_idx, page in enumerate(pages):
            tables = page.get("tables", [])
            for table in tables:
                table["__skip_render"] = True
            logger.info(f"Suppressed {len(tables)} original PDF tables on page {page_idx}")
            f.write(f"Suppressed {len(tables)} original PDF tables on page {page_idx}\n")
        
        # Process page 0 which contains the intro and first set of tables
        if len(pages) > 0:
            f.write("Processing page 0\n")
            blocks_before = len(pages[0].get('blocks', []))
            _extract_tables_from_page(pages[0], page_num=0)
            blocks_after = len(pages[0].get('blocks', []))
            f.write(f"Page 0: {blocks_before} blocks before, {blocks_after} blocks after\n")
        
        # Process page 1 which continues with more detailed explanations
        if len(pages) > 1:
            f.write("Processing page 1\n")
            blocks_before = len(pages[1].get('blocks', []))
            _extract_tables_from_page(pages[1], page_num=1)
            blocks_after = len(pages[1].get('blocks', []))
            f.write(f"Page 1: {blocks_before} blocks before, {blocks_after} blocks after\n")
        
        # Pages 2-4 contain the detailed explanations and should be preserved
        # They are not duplicates - they're the actual chapter content
        
        f.write("apply_chapter_8_adjustments completed\n")




