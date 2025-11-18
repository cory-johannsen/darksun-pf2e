#!/usr/bin/env python3
"""
Chapter 12 HTML Post-Processing

This module handles post-processing for Chapter 12 (NPCs), specifically:
1. Splitting the Templars as NPCs mega-paragraph into 8 proper paragraphs
2. Restructuring the "Typical Administrative Templar Positions" table
3. Positioning the table after all Templars text content
4. Converting table headers to proper table structure
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _split_templars_paragraph(html: str) -> str:
    """
    Split the massive Templars paragraph into 8 distinct paragraphs.
    
    The breaks should occur at:
    1. "Templars perform three vital functions"
    2. "One final,"
    3. "Templar soldiers are"
    4. "In the administration of the"
    5. "These are only a sampling"
    6. "Technically, the sorcerer-king"
    7. "The DM must keep two things"
    """
    logger.info("Splitting Templars paragraph into 8 paragraphs...")
    
    # Find the Templars section
    templars_match = re.search(
        r'(<p id="header-1-templars-as-npcs">.*?</p>)\s*<p>(.*?)</p>\s*<p id="header-2-typical-administrative',
        html,
        re.DOTALL
    )
    
    if not templars_match:
        logger.warning("Could not find Templars section to split")
        return html
    
    templars_header = templars_match.group(1)
    templars_text = templars_match.group(2)
    
    # Split at each break point
    # Use positive lookahead to keep the break text
    splits = [
        r'(Templars perform three vital functions)',
        r'(One final,)',
        r'(Templar soldiers are)',
        r'(In the administration of the)',
        r'(These are only a sampling)',
        r'(Technically, the sorcerer-king)',
        r'(The DM must keep two things)',
    ]
    
    # Split the text into paragraphs
    paragraphs = [templars_text]
    for split_pattern in splits:
        new_paragraphs = []
        for para in paragraphs:
            parts = re.split(split_pattern, para, maxsplit=1)
            if len(parts) == 3:  # Successfully split
                # parts[0] is before, parts[1] is the match, parts[2] is after
                if parts[0].strip():
                    new_paragraphs.append(parts[0].strip())
                new_paragraphs.append(parts[1] + parts[2])  # Combine match with after
            else:
                new_paragraphs.append(para)
        paragraphs = new_paragraphs
    
    # Rebuild HTML with proper paragraphs
    new_section = templars_header + '\n'
    for para in paragraphs:
        if para.strip():
            new_section += f'<p>{para.strip()}</p>\n'
    
    # Replace in HTML
    html = re.sub(
        r'<p id="header-1-templars-as-npcs">.*?</p>\s*<p>.*?</p>\s*(?=<p id="header-2-typical-administrative)',
        new_section,
        html,
        flags=re.DOTALL
    )
    
    logger.info(f"Split Templars text into {len(paragraphs)} paragraphs")
    
    return html


def _merge_admin_paragraph(html: str) -> str:
    """
    Merge the "In the administration of the city states, templar" fragment
    with the "NPCs occupy all positions" paragraph.
    """
    logger.info("Merging split administration paragraph...")
    
    # Find paragraphs ending with "templar" and starting with "NPCs occupy"
    # The problem is that we may have nested <p> tags, so we need to properly close the first one
    html = re.sub(
        r'(<p>[^<]*In the administration of the city states, templar)\s+<p>(NPCs occupy)',
        r'\1 \2',
        html,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    return html


def _restructure_templar_table(html: str) -> str:
    """
    Build the proper 3-column x 8-row table for Templar positions.
    All position names come from the source PDF.
    """
    logger.info("Building Templar positions table...")
    
    # Define table based on source material
    # These positions all appear in pages 84-85 of the PDF
    table_html = '<h4 class="table-title">Typical Administrative Templar Positions</h4>\n'
    table_html += '<table class="ds-table table-templar-positions">\n'
    
    # Header row
    table_html += '<thead>\n<tr>\n'
    table_html += '<th class="table-header">Low Level (1-4)</th>\n'
    table_html += '<th class="table-header">Mid Level (5-8)</th>\n'
    table_html += '<th class="table-header">High Level (9 +)</th>\n'
    table_html += '</tr>\n</thead>\n<tbody>\n'
    
    # Data rows - from source PDF pages 84-85
    # All columns specified by user
    rows = [
        ["Removers of Waste", "Tax Collection", "Coin Distribution"],
        ["Movers of Grain", "Major Construction", "Construction Planning"],
        ["Minor Construction", "Slave Control", "Mayor of the City"],
        ["Disease Control", "Grain Distribution", "Governor of the Farmlands"],
        ["Maintenance of Gardens", "Gate Monitor", "Aid to the King"],
        ["Maintenance of Roads", "Assigner of Permits", ""],
        ["Maintenance of Walls", "Riot Control", ""],
    ]
    
    for row in rows:
        table_html += '<tr>\n'
        for cell in row:
            table_html += f'<td>{cell}</td>\n'
        table_html += '</tr>\n'
    
    table_html += '</tbody>\n</table>\n'
    
    return table_html


def _remove_old_structure(html: str) -> str:
    """
    Remove the old headers and fragmented tables.
    """
    logger.info("Removing old table structure...")
    
    # Remove "Typical Administrative Templar Positions" header (III)
    html = re.sub(
        r'<p id="header-2-typical-administrative-templar-positions">.*?</p>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove "Low Level (1-4)" header (IV)
    html = re.sub(
        r'<p id="header-3-low-level-1-4">.*?</p>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove "Mid Level (5-8)" header (V)
    html = re.sub(
        r'<p id="header-4-mid-level-5-8">.*?</p>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove "High Level (9 +)" header (VI)
    html = re.sub(
        r'<p id="header-5-high-level-9-\+">.*?</p>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove paragraph with list of positions
    html = re.sub(
        r'<p>Tax Collection Removers of Waste.*?Maintenance of Walls</p>\s*',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Merge the fragmented last paragraph
    # The text "Coin Distribution..." that was removed needs to be merged back
    # into the DM paragraph. Find paragraph starting with "a task such as" and merge 
    # it into the previous paragraph
    html = re.sub(
        r'</p>\s*<p>a task such as',
        ' a task such as',
        html,
        flags=re.DOTALL
    )
    
    # Remove old fragmented tables at the end
    html = re.sub(
        r'<table class="ds-table">.*?</table>\s*(?=</section>)',
        '',
        html,
        flags=re.DOTALL
    )
    
    return html


def _insert_table_after_templars(html: str) -> str:
    """
    Insert the table after the last Templars paragraph and before Druids.
    """
    logger.info("Inserting table after Templars section...")
    
    table_html = _restructure_templar_table(html)
    
    # Find the last paragraph before "Druids as NPCs"
    # Should be the paragraph starting with "The DM must keep two things"
    match = re.search(
        r'(</p>)\s*(?=<p id="header-\d+-druids-as-npcs">)',
        html
    )
    
    if match:
        # Insert table before Druids header
        insertion_point = match.end()
        html = html[:insertion_point] + '\n' + table_html + html[insertion_point:]
        logger.info("✅ Inserted table after Templars section")
    else:
        logger.warning("Could not find insertion point for table")
    
    return html


def _split_druids_paragraph(html: str) -> str:
    """
    Split the Druids as NPCs paragraph into 2 paragraphs.
    
    Break should occur at "Irresponsible use of his guarded".
    """
    logger.info("Splitting Druids paragraph into 2 paragraphs...")
    
    # Find the Druids section and split at the specified point
    html = re.sub(
        r'(<p id="header-\d+-druids-as-npcs">.*?</p>)\s*<p>(.*?)(Irresponsible use of his guarded.*?)</p>',
        r'\1\n<p>\2</p>\n<p>\3</p>',
        html,
        flags=re.DOTALL
    )
    
    logger.info("✅ Split Druids paragraph into 2 paragraphs")
    
    return html


def apply_chapter_12_content_fixes(html: str) -> str:
    """
    Apply all Chapter 12-specific HTML post-processing fixes.
    
    Args:
        html: The HTML content to process
        
    Returns:
        The processed HTML content
    """
    logger.info("=" * 80)
    logger.info("Applying Chapter 12 HTML post-processing fixes")
    logger.info("=" * 80)
    
    # Step 1: Split the massive Templars paragraph
    html = _split_templars_paragraph(html)
    
    # Step 2: Merge the fragmented administration paragraph
    html = _merge_admin_paragraph(html)
    
    # Step 3: Remove old structure (headers, fragmented tables, position lists)
    html = _remove_old_structure(html)
    
    # Step 4: Insert new table after Templars text
    html = _insert_table_after_templars(html)
    
    # Step 5: Split Druids paragraph
    html = _split_druids_paragraph(html)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html = convert_all_styled_headers_to_semantic(html)
    
    logger.info("Chapter 12 HTML post-processing complete")
    
    return html

