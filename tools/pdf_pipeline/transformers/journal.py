"""Transform PDF section data to structured journal HTML.

This module coordinates the transformation of extracted PDF data into
structured HTML journal entries with proper formatting, tables, and TOC.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional

# Import all functions from sub-modules
from .journal_lib import (
    # Utilities
    normalize_plain_text,
    merge_fragments,
    join_fragments,
    sanitize_plain_text,
    cluster_positions,
    compute_bbox_from_cells,
    is_bold,
    is_italic,
    wrap_span,
    dehyphenate_text,
    # Blocks
    collect_cells_from_blocks,
    # Tables
    build_matrix_from_cells,
    table_from_rows,
    # Rendering
    merge_adjacent_paragraph_html,
    render_line,
    render_text_block,
    render_table,
    render_page,
    render_pages,
    # TOC
    generate_table_of_contents,
    fix_chapter_6_armor_headers_after_anchoring,
    apply_subheader_styling,
    add_header_anchors,
)

# Import with underscores for backward compatibility
_normalize_plain_text = normalize_plain_text
_merge_fragments = merge_fragments
_join_fragments = join_fragments
_sanitize_plain_text = sanitize_plain_text
_cluster_positions = cluster_positions
_collect_cells_from_blocks = collect_cells_from_blocks
_build_matrix_from_cells = build_matrix_from_cells
_table_from_rows = table_from_rows
_compute_bbox_from_cells = compute_bbox_from_cells
_is_bold = is_bold
_is_italic = is_italic
_wrap_span = wrap_span
_dehyphenate_text = dehyphenate_text
_merge_adjacent_paragraph_html = merge_adjacent_paragraph_html
_render_line = render_line
_render_text_block = render_text_block
_render_table = render_table
_render_page = render_page
_render_pages = render_pages
_generate_table_of_contents = generate_table_of_contents
_fix_chapter_6_armor_headers_after_anchoring = fix_chapter_6_armor_headers_after_anchoring
_apply_subheader_styling = apply_subheader_styling
_add_header_anchors = add_header_anchors

logger = logging.getLogger(__name__)


def transform(section_data: dict, config: dict | None = None) -> dict:
    config = config or {}
    # NOTE: pages will be extracted AFTER chapter-specific processing
    include_tables = config.get("include_tables", True)
    table_class = config.get("table_class")
    # [HTML_SINGLE_PAGE] Each chapter should be rendered as a single continuous page
    wrap_pages = config.get("wrap_pages", False)
    slug = section_data.get("slug")
    
    # Debug: Log which slug we're transforming
    logger.info(f"[JOURNAL TRANSFORM] Processing slug: {slug}")
    paragraph_breaks = list(config.get("paragraph_breaks", []))
    per_slug = config.get("paragraph_break_hints", {})
    if slug and isinstance(per_slug, dict):
        paragraph_breaks.extend(per_slug.get(slug, []))

    # Apply chapter-specific processing
    with open('/tmp/journal_slugs.txt', 'a') as f:
        f.write(f"Processing slug: {slug}\n")
    if slug == "chapter-one-the-world-of-athas":
        from . import chapter_one_world_processing
        chapter_one_world_processing.apply_chapter_one_world_adjustments(section_data)
    elif slug == "chapter-two-athasian-society":
        from . import chapter_two_athasian_society_processing
        chapter_two_athasian_society_processing.apply_chapter_two_athasian_society_adjustments(section_data)
    elif slug == "chapter-two-player-character-races":
        from . import chapter_2_processing
        chapter_2_processing.apply_chapter_2_adjustments(section_data)
        paragraph_breaks.extend(
            [
                "The player character races are no exception to this",
                # Dwarves section - 4 paragraphs  
                "A dwarfs chief",  # Matches the raw text without apostrophe
                "The task to which a dwarf",
                "By nature, dwarves are nonmagical",
            ]
        )
    elif slug == "chapter-three-player-character-classes":
        # Chapter 3 processing - apply table extractions and adjustments
        from . import chapter_3_processing
        chapter_3_processing.apply_chapter_3_adjustments(section_data)
    elif slug == "chapter-six-money-and-equipment":
        from . import chapter_6_processing
        chapter_6_processing.apply_chapter_6_adjustments(section_data)
        # Chapter 6 "What Things Are Worth" section - 7 paragraphs
        # Chapter 6 "Protracted Barter" section - 3 paragraphs
        # Chapter 6 "Starting Money" section - 2 paragraphs
        # Chapter 6 "Weapons" section - 4 paragraphs
        paragraph_breaks.extend(
            [
                # What Things Are Worth section
                "On Athas, the relative rarity",
                "All nonmetal items cost one percent",
                "All metal items cost the price listed",
                "Thus, the small canoe (a nonmetal item)",
                "If an item is typically a mixture of metal",
                "All prices listed in the",
                # Protracted Barter section
                "In the first round",
                "If Kyuln from the previous example",
                # Starting Money section
                "The following table indicates",
                # Weapons section (after Athasian Market: List of Provisions)
                "The following weapons,",
                "The remaining weapons",
                "The arquebus is unavailable",
                # Weapon Materials section - 3 paragraphs after table legend
                "In the game and in text",
                "Nonmetal weapons detract from",
                "Nonmetal weapons can be enchanted",
                # Breaking Weapons section - 2 paragraphs
                "Bruth is sent to the arena",
                # Metal Armor in Dark Sun section - 2 paragraphs
                "Likewise, the intense heat across",
            ]
        )
    elif slug == "chapter-five-monsters-of-athas":
        from . import chapter_5_processing
        chapter_5_processing.apply_chapter_5_adjustments(section_data)
    elif slug == "chapter-seven-magic":
        from . import chapter_7_processing
        chapter_7_processing.apply_chapter_7_adjustments(section_data)
    elif slug == "chapter-eight-experience":
        with open('/tmp/chapter8_debug.txt', 'w') as f:
            f.write("CHAPTER 8 BLOCK EXECUTED!\n")
            try:
                import logging
                logger_ch8 = logging.getLogger(__name__)
                from . import chapter_8_processing
                f.write("Module imported successfully\n")
                logger_ch8.info("=" * 60)
                logger_ch8.info("APPLYING CHAPTER 8 PROCESSING FOR EXPERIENCE TABLES")
                logger_ch8.info("=" * 60)
                f.write("About to call apply_chapter_8_adjustments\n")
                chapter_8_processing.apply_chapter_8_adjustments(section_data)
                f.write("apply_chapter_8_adjustments completed\n")
                logger_ch8.info("Chapter 8 processing complete")
            except Exception as e:
                f.write(f"ERROR: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
    elif slug == "chapter-nine-combat":
        # Chapter 9 processing is now handled in the extract stage via Chapter9TableFixer
        # No need to call apply_chapter_9_adjustments here as it would duplicate the processing
        # Arena Combats section - 3 paragraphs with breaks at:
        # 1. "Player characters" 
        # 2. "The customs of"
        paragraph_breaks.extend([
            "Player characters may well find themselves",
            "The customs of every arena",
        ])
        # Stables section - 4 paragraphs with breaks at:
        # 1. (intro) "Most noble and merchant houses"
        # 2. "Typical stables of slaves"
        # 3. "Every slave in a stable"
        # 4. "Every stable has its champion"
        paragraph_breaks.extend([
            "Typical stables of slaves",
            "Every slave in a stable",
            "Every stable has its champion",
        ])
    elif slug == "chapter-ten-treasure":
        logger.warning("=" * 80)
        logger.warning(f"!!! CHAPTER 10 PROCESSING INVOKED FOR SLUG: {slug} !!!")
        logger.warning("=" * 80)
        from . import chapter_10_processing
        logger.warning(f"!!! Imported chapter_10_processing module !!!")
        chapter_10_processing.apply_chapter_10_adjustments(section_data)
        logger.warning(f"!!! Finished apply_chapter_10_adjustments !!!")
        logger.warning("=" * 80)
        
        # Debug: Check pages after processing
        logger.warning(f"CHAPTER 10 DEBUG: Section has {len(section_data.get('pages', []))} pages")
        for page_idx, page in enumerate(section_data.get('pages', [])):
            blocks = page.get('blocks', [])
            logger.warning(f"  Page {page_idx}: {len(blocks)} blocks")
            for block_idx, block in enumerate(blocks):
                if '__gem_table' in block:
                    logger.warning(f"    Block {block_idx}: HAS __gem_table marker!")
                if '__magical_item_entry' in block:
                    logger.warning(f"    Block {block_idx}: HAS __magical_item_entry={block['__magical_item_entry']}")
                # Check for Gem Table header
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        if 'Gem Table' in span.get('text', ''):
                            logger.warning(f"    Block {block_idx}: Contains 'Gem Table' text")
                        if 'gem variations' in span.get('text', '').lower():
                            logger.warning(f"    Block {block_idx}: Contains 'gem variations' text")
    elif slug == "chapter-eleven-encounters":
        logger.warning("=" * 80)
        logger.warning(f"!!! CHAPTER 11 PROCESSING INVOKED FOR SLUG: {slug} !!!")
        logger.warning("=" * 80)
        from . import chapter_11_processing
        logger.warning(f"!!! Imported chapter_11_processing module !!!")
        chapter_11_processing.apply_chapter_11_adjustments(section_data)
        logger.warning(f"!!! Finished apply_chapter_11_adjustments !!!")
        logger.warning("=" * 80)
    elif slug == "chapter-twelve-npcs":
        # Chapter 12: Paragraph breaks in "Spellcasters as NPCs" section
        paragraph_breaks.extend([
            "Druid NPCs",
            "Wizard NPCs",
            "Rare instances",
            "One notable",
        ])
        # Chapter 12: Paragraph breaks in "Templars as NPCs" section
        paragraph_breaks.extend([
            "Templars perform three vital functions",
            "One final,",
            "Templar soldiers are",
            "In the administration of the",
            "These are only a sampling",
            "Technically, the sorcerer-king",
            "The DM must keep two things",
        ])
    elif slug == "chapter-thirteen-vision-and-light":
        logger.info("=" * 80)
        logger.info("!!! CHAPTER 13 PROCESSING INVOKED FOR SLUG: %s !!!", slug)
        logger.info("=" * 80)
        from . import chapter_13_processing
        logger.info("!!! Imported chapter_13_processing module !!!")
        chapter_13_processing.apply_chapter_13_adjustments(section_data)
        logger.info("!!! Finished apply_chapter_13_adjustments !!!")
        logger.info("=" * 80)
    elif slug == "chapter-fourteen-time-and-movement":
        logger.info("=" * 80)
        logger.info("!!! CHAPTER 14 PROCESSING INVOKED FOR SLUG: %s !!!", slug)
        logger.info("=" * 80)
        from . import chapter_14_processing
        logger.info("!!! Imported chapter_14_processing module !!!")
        chapter_14_processing.apply_chapter_14_adjustments(section_data)
        logger.info("!!! Finished apply_chapter_14_adjustments !!!")
        logger.info("=" * 80)
    elif slug == "chapter-fifteen-new-spells":
        logger.info("=" * 80)
        logger.info("!!! CHAPTER 15 PROCESSING INVOKED FOR SLUG: %s !!!", slug)
        logger.info("=" * 80)
        from . import chapter_15_processing
        logger.info("!!! Imported chapter_15_processing module !!!")
        chapter_15_processing.apply_chapter_15_adjustments(section_data)
        logger.info("!!! Finished apply_chapter_15_adjustments !!!")
        logger.info("=" * 80)


    # Extract pages AFTER chapter-specific processing to get any modifications
    pages = section_data.get("pages", [])
    
    
    # Debug for chapter 10: Check page structure before rendering
    if slug == "chapter-ten-treasure":
        logger.warning("=" * 80)
        logger.warning("BEFORE RENDERING: Checking page structure")
        logger.warning("=" * 80)
        for page_idx, page in enumerate(pages):
            blocks = page.get('blocks', [])
            logger.warning(f"Page {page_idx}: {len(blocks)} blocks")
            if page_idx == 1:
                for block_idx, block in enumerate(blocks[:10]):  # Show first 10 blocks
                    text = ""
                    has_gem_table = '__gem_table' in block
                    skip = block.get('__skip_render', False)
                    for line in block.get('lines', [])[:1]:  # First line only
                        for span in line.get('spans', [])[:1]:  # First span only
                            text = span.get('text', '')[:50]
                    logger.warning(f"  Block {block_idx}: __gem_table={has_gem_table}, __skip_render={skip}, text='{text}'")

    
    # Debug: Check if legend blocks are in pages for chapter 8
    if slug == "chapter-eight-experience":
        with open('/tmp/chapter8_transform_debug.txt', 'a') as f:
            f.write(f"\n=== Checking extracted pages before rendering ===\n")
            f.write(f"Total pages: {len(pages)}\n")
            for page_idx, page in enumerate(pages):
                blocks = page.get('blocks', [])
                f.write(f"Page {page_idx}: {len(blocks)} blocks\n")
                # Check for legend or table blocks
                for block_idx, block in enumerate(page.get('blocks', [])):
                    if '__class_award_table' in block:
                        header = block.get('__table_header', 'UNKNOWN')
                        f.write(f"  Block {block_idx}: TABLE '{header}'\n")
                    # Check if block has lines with legend text
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            text = span.get('text', '')
                            if text.startswith('*For gladiators') or text.startswith('**The thief'):
                                skip_value = block.get('__skip_render', 'NOT_SET')
                                bbox_value = block.get('bbox', 'NOT_SET')
                                f.write(f"  Block {block_idx}: LEGEND TEXT __skip_render={skip_value}, bbox={bbox_value}, text='{text[:60]}'\n")
    
    # Debug: Check if Initial Character Funds table marker is in pages
    if slug == "chapter-six-money-and-equipment":
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"\n=== Checking extracted pages before rendering ===\n")
            f.write(f"Total pages: {len(pages)}\n")
            for page_idx, page in enumerate(pages):
                for block_idx, block in enumerate(page.get('blocks', [])):
                    if '__initial_character_funds_table' in block:
                        f.write(f"  FOUND __initial_character_funds_table in page {page_idx}, block {block_idx}\n")

    html_content = _render_pages(
        pages,
        include_tables=include_tables,
        table_class=table_class,
        wrap_pages=wrap_pages,
        paragraph_breaks=paragraph_breaks,
    )

    # Apply post-processing to the rendered HTML
    # TODO: Re-enable chapter-specific post-processing if needed
    # if slug:
    #     from ..postprocess import postprocess_chapter_2_html
    #     html_content = postprocess_chapter_2_html(html_content, slug)
    
    # [TOC_FORMAT] Apply subheader styling BEFORE TOC generation
    html_content = _apply_subheader_styling(html_content, slug)
    
    # Chapter 2 specific: remove stray aggregated race paragraph between Aging Effects header and first table
    if slug == "chapter-two-player-character-races":
        import re as _re
        try:
            # Locate Aging Effects subheader paragraph
            ae = _re.search(r'(<p[^>]*><span[^>]*>Aging Effects</span></p>)', html_content)
            if ae:
                start = ae.end()
                # Find first table after Aging Effects
                tbl = _re.search(r'<table', html_content[start:])
                if tbl:
                    mid = html_content[start:start+tbl.start()]
                    # Remove the first non-empty paragraph that looks like an aggregated race list
                    def _strip_aggregated(pblock: str) -> str:
                        paras = _re.findall(r'(<p[^>]*>.*?</p>)', pblock, _re.DOTALL)
                        new_blocks = []
                        removed_once = False
                        for p in paras:
                            text = _re.sub(r'<[^>]+>', '', p)
                            # Heuristic: many proper-case tokens and contains at least one known race anchor
                            caps = _re.findall(r'\b[A-Z][A-Za-z-]*\b', text)
                            if (not removed_once) and len(caps) >= 5 and ("Dwarf" in text or "Elf" in text or "Thri" in text):
                                removed_once = True
                                continue
                            new_blocks.append(p)
                        # Rebuild segment with removed paragraph (if any)
                        # Note: Keep any trailing content not matched as <p> verbatim
                        end_tail = _re.sub(r'(<p[^>]*>.*?</p>)', '', pblock, flags=_re.DOTALL)
                        return "".join(new_blocks) + end_tail
                    cleaned_mid = _strip_aggregated(mid)
                    html_content = html_content[:start] + cleaned_mid + html_content[start+tbl.start():]
            # Ensure "Height and Weight" table appears immediately after its header
            hw_header = _re.search(r'(<p[^>]*><span[^>]*>\s*Height and Weight\s*</span></p>)', html_content, _re.IGNORECASE)
            hw_table = _re.search(
                r'(<table[^>]*>.*?<th[^>]*>\s*Height in Inches\s*</th>.*?<th[^>]*>\s*Weight in Pounds\s*</th>.*?</table>)',
                html_content,
                _re.IGNORECASE | _re.DOTALL,
            )
            if hw_header and hw_table and hw_header.start() < hw_table.start():
                # Remove the table from its current position
                before = html_content[:hw_table.start()]
                after = html_content[hw_table.end():]
                html_without_table = before + after
                # Insert table immediately after the header paragraph
                insert_at = hw_header.end()
                html_content = html_without_table[:insert_at] + hw_table.group(1) + html_without_table[insert_at:]
        except Exception:
            # Best-effort; do not fail transformation
            pass
    
    # Add header anchors and generate TOC (Rule #32) - MUST run before Chapter 6 armor fix
    html_content = _add_header_anchors(html_content)
    
    # Chapter 6 specific: fix armor headers (AFTER anchoring so merged headers get anchors too)
    if slug == "chapter-six-money-and-equipment":
        html_content = _fix_chapter_6_armor_headers_after_anchoring(html_content)
    # After anchoring, ensure H&W table is directly after its header (anchored id present now)
    if slug == "chapter-two-player-character-races":
        import re as _re2
        try:
            anchored_hw = _re2.search(r'(<p id="header-\d+-height-and-weight">.*?</p>)', html_content, _re2.IGNORECASE | _re2.DOTALL)
            hw_tbl = _re2.search(
                r'(<table[^>]*>.*?<th[^>]*>\s*Height in Inches\s*</th>.*?<th[^>]*>\s*Weight in Pounds\s*</th>.*?</table>)',
                html_content,
                _re2.IGNORECASE | _re2.DOTALL,
            )
            if anchored_hw and hw_tbl and anchored_hw.start() < hw_tbl.start():
                # Excise table and reinsert immediately after header
                content_wo_tbl = html_content[:hw_tbl.start()] + html_content[hw_tbl.end():]
                insert_point = anchored_hw.end()
                html_content = content_wo_tbl[:insert_point] + hw_tbl.group(1) + content_wo_tbl[insert_point:]
        except Exception:
            pass
    
    # Chapter 6: Move Common Wages table to correct position after header; also move New Equipment tables under their headers
    if slug == "chapter-six-money-and-equipment":
        import re as _re3
        try:
            # Find the Common Wages header (after anchoring)
            cw_header = _re3.search(r'(<p id="header-\d+-common-wages">.*?</p>)', html_content, _re3.IGNORECASE | _re3.DOTALL)
            # Find the Common Wages table (has Title, Daily, Weekly, Monthly columns and Military/Professional sections)
            cw_table = _re3.search(
                r'(<table[^>]*>.*?<th[^>]*>\s*Title\s*</th>.*?<th[^>]*>\s*Daily\s*</th>.*?<th[^>]*>\s*Weekly\s*</th>.*?<th[^>]*>\s*Monthly\s*</th>.*?</table>)',
                html_content,
                _re3.IGNORECASE | _re3.DOTALL,
            )
            if cw_header and cw_table and cw_header.start() < cw_table.start():
                # Table appears after the header, but we need to move it immediately after
                # Remove the table from its current position
                content_wo_tbl = html_content[:cw_table.start()] + html_content[cw_table.end():]
                # Insert table, legend, and payment paragraph immediately after Common Wages header
                insert_point = cw_header.end()
                legend_html = '<p style="font-size: 0.9em;">*available only in some city-states<br/>**available only in cities with organized militaries</p>'
                payment_paragraph = '<p>A character may receive payment for his services in other services, goods, or coins, depending upon the situation.</p>'
                html_content = content_wo_tbl[:insert_point] + cw_table.group(1) + legend_html + payment_paragraph + content_wo_tbl[insert_point:]
                
                # Now remove the legend text from Protracted Barter paragraph where it's incorrectly embedded
                html_content = _re3.sub(
                    r'\*available only in some city-states \*\*available only in cities with organized militaries ',
                    '',
                    html_content
                )
               
        except Exception:
            pass
        
        # Move New Equipment tables (best-effort; ensures tables sit under their specific headers)
        try:
            def _move_table_after_header(html: str, header_regex: str, table_matcher) -> str:
                hdr = _re3.search(header_regex, html, _re3.IGNORECASE | _re3.DOTALL)
                if not hdr:
                    return html
                # Find all tables; pick the first that matches
                for m in _re3.finditer(r'(<table[^>]*>.*?</table>)', html, _re3.DOTALL):
                    tbl_html = m.group(1)
                    if table_matcher(tbl_html):
                        # Remove the table and insert after header
                        html_wo = html[:m.start()] + html[m.end():]
                        insert_at = hdr.end()
                        return html_wo[:insert_at] + tbl_html + html_wo[insert_at:]
                return html

            # Household Provisions: 2 columns Item/Price (3 rows inc header)
            html_content = _move_table_after_header(
                html_content,
                r'(<p id="header-\d+-household-provisions">.*?</p>)',
                lambda t: ('<th>Item</th>' in t and '<th>Price</th>' in t and t.count('<tr>') == 3),
            )
            # Barding: 3 columns Type/Price/Weight and includes animal types
            html_content = _move_table_after_header(
                html_content,
                r'(<p id="header-\d+-barding">.*?</p>)',
                lambda t: ('<th>Type</th>' in t and '<th>Price</th>' in t and '<th>Weight</th>' in t and any(x in t for x in ['Inix', 'Kank', 'Mekillot'])),
            )
            # Transport/Transportation: 2 columns Type/Price and includes Chariot/Howdah section labels
            # Prefer earliest 'Transport' header under New Equipment (avoid later 'Transportation' under Equipment Descriptions)
            html_content = _move_table_after_header(
                html_content,
                r'(<p id="header-\d+-transport">.*?</p>)',
                lambda t: ('<th>Type</th>' in t and '<th>Price</th>' in t and '&lt;strong&gt;Chariot&lt;/strong&gt;' in t and '&lt;strong&gt;Howdah&lt;/strong&gt;' in t),
            )
        except Exception:
            pass
        
        # Add Weapon Materials Table legend with proper styling
        try:
            # Find the Weapon Materials Table
            wm_table = _re3.search(
                r'(<table[^>]*>.*?<th[^>]*>\s*Material\s*</th>.*?<th[^>]*>\s*Cost\s*</th>.*?<th[^>]*>\s*Wt\.\s*</th>.*?<th[^>]*>\s*Dmg\*\s*</th>.*?<th[^>]*>\s*Hit\s+Prob\.\*\*\s*</th>.*?</table>)',
                html_content,
                _re3.IGNORECASE | _re3.DOTALL,
            )
            if wm_table:
                # Add legend immediately after the table
                insert_point = wm_table.end()
                legend_html = '<p style="font-size: 0.9em;">*The damage modifier subtracts from the damage normally done by that weapon, with a minimum of one point.<br/>** this does not apply to missile weapons.</p>'
                html_content = html_content[:insert_point] + legend_html + html_content[insert_point:]
                
                # Remove any partial legend text that might have been rendered from the block
                html_content = _re3.sub(
                    r'<p>normally done by that weapon, with a minimum of one point\.</p>',
                    '',
                    html_content
                )
        except Exception:
            pass
        
        # Enforce New Equipment placement: ensure tables sit under New Equipment headers only
        try:
            # Helper to move a specific table body from a later duplicate header to an earlier header
            import re as _re4
            def _relocate_table_between_headers(html: str, source_header_pat: str, target_header_pat: str, table_matcher) -> str:
                src = _re4.search(source_header_pat, html, _re4.IGNORECASE | _re4.DOTALL)
                tgt = _re4.search(target_header_pat, html, _re4.IGNORECASE | _re4.DOTALL)
                if not tgt:
                    return html
                # Find a matching table anywhere after src (if src exists), otherwise anywhere
                tbl_iter = list(_re4.finditer(r'(<table[^>]*>.*?</table>)', html, _re4.DOTALL))
                src_pos = src.end() if src else 0
                chosen = None
                for m in tbl_iter:
                    if m.start() >= src_pos and table_matcher(m.group(1)):
                        chosen = m
                        break
                if not chosen:
                    return html
                # Remove chosen table
                html_wo = html[:chosen.start()] + html[chosen.end():]
                # Insert after target header
                insert_at = tgt.end()
                return html_wo[:insert_at] + chosen.group(1) + html_wo[insert_at:]
            
            # 1) Household Provisions: move any Item/Price table from later header-40 to earlier header-26
            html_content = _relocate_table_between_headers(
                html_content,
                r'(<p id="header-40-household-provisions">.*?</p>)',   # later duplicate
                r'(<p id="header-26-household-provisions">.*?</p>)',   # New Equipment
                lambda t: ('<th>Item</th>' in t and '<th>Price</th>' in t)
            )
            # If both early (26) and late (40) have the table, remove the later one to prevent duplication
            early = _re4.search(r'(<p id="header-26-household-provisions">.*?</p>)(.{0,2000})', html_content, _re4.DOTALL|_re4.IGNORECASE)
            late  = _re4.search(r'(<p id="header-40-household-provisions">.*?</p>)(.{0,2000})', html_content, _re4.DOTALL|_re4.IGNORECASE)
            if early and late:
                early_has = '<table' in (early.group(2) or '')
                late_has  = '<table' in (late.group(2) or '')
                if early_has and late_has:
                    # Remove the table immediately after header-40 only
                    # Find the first table after header-40
                    tail = html_content[late.end():]
                    tblm = _re4.search(r'(<table[^>]*>.*?</table>)', tail, _re4.DOTALL)
                    if tblm:
                        # excise that table
                        start = late.end() + tblm.start()
                        end   = late.end() + tblm.end()
                        html_content = html_content[:start] + html_content[end:]
            # 2) Barding: ensure 3-col table under early barding (the one before transport)
            html_content = _relocate_table_between_headers(
                html_content,
                r'(<p id="header-48-barding">.*?</p>)',                 # later duplicate
                r'(<p id="header-\d+-barding">.*?</p>)',                # first barding anchor
                lambda t: ('<th>Type</th>' in t and '<th>Price</th>' in t and '<th>Weight</th>' in t)
            )
            # 3) Transport: move Type/Price sectioned table to early Transport (not Transportation)
            html_content = _relocate_table_between_headers(
                html_content,
                r'(<p id="header-49-transportation">.*?</p>)',          # later duplicate
                r'(<p id="header-28-transport">.*?</p>)',               # New Equipment
                lambda t: ('<th>Type</th>' in t and '<th>Price</th>' in t and '&lt;strong&gt;Chariot&lt;/strong&gt;' in t)
            )
        except Exception:
            # best-effort enforcement
            pass
    
    toc_html = _generate_table_of_contents(html_content)
    if toc_html:
        html_content = toc_html + html_content

    return {
        "entity_type": "journal",
        "slug": section_data.get("slug"),
        "title": section_data.get("title"),
        "content": html_content,
        "source_pages": [section_data.get("start_page"), section_data.get("end_page")],
        "metadata": {
            "parent_slugs": section_data.get("parent_slugs", []),
            "level": section_data.get("level"),
            "layout": "structured",
        },
    }


