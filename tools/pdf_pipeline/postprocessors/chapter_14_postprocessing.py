"""
Chapter 14 HTML Post-Processing

This module handles HTML-level fixes for Chapter 14 content after initial rendering.
"""

import logging
import re
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def postprocess_chapter_14_html(html: str) -> str:
    """
    Post-process Chapter 14 HTML to fix table placement and formatting.
    
    Args:
        html: The input HTML string
        
    Returns:
        The processed HTML string
    """
    logger.info("Post-processing Chapter 14 HTML")
    
    html = _insert_athasian_calendar_table(html)
    html = _remove_calendar_table_headers_from_toc(html)
    html = _fix_calendar_paragraph_breaks(html)
    html = _clean_up_table_fragments(html)
    html = _fix_dehydration_table(html)
    html = _fix_overland_movement_section(html)
    html = _fix_movement_by_night_paragraphs(html)
    html = _fix_whitespace_issues(html)
    
    logger.info("Chapter 14 HTML post-processing complete")
    return html


def _insert_athasian_calendar_table(html: str) -> str:
    """
    Insert the properly formatted Athasian Calendar table.
    
    The table should appear after the paragraph ending "a year of Guthay's Agitation."
    and before the paragraph beginning "Superstition and folklore".
    """
    logger.info("Inserting Athasian Calendar table")
    
    # Create the properly formatted table
    calendar_table = '''
<table class="ds-table">
<thead>
<tr>
<th>The Endlean Cycle</th>
<th>The Seofean Cycle</th>
</tr>
</thead>
<tbody>
<tr><td>Ral</td><td>Fury</td></tr>
<tr><td>Friend</td><td>Contemplation</td></tr>
<tr><td>Desert</td><td>Vengeance</td></tr>
<tr><td>Priest</td><td>Slumber</td></tr>
<tr><td>Wind</td><td>Defiance</td></tr>
<tr><td>Dragon</td><td>Reverence</td></tr>
<tr><td>Mountain</td><td>Agitation</td></tr>
<tr><td>King</td><td></td></tr>
<tr><td>Silt</td><td></td></tr>
<tr><td>Enemy</td><td></td></tr>
<tr><td>Guthay</td><td></td></tr>
</tbody>
</table>
'''
    
    # Find the insertion point after "a year of Guthay's Agitation."
    # and before any incorrectly rendered headers
    pattern = r"(a year of Guthay(?:&#x27;|')s Agitation\.)</p>"
    
    # Check if the table already exists
    if '<th>The Endlean Cycle</th>' in html:
        logger.debug("Athasian Calendar table already exists, skipping insertion")
        return html
    
    # Insert the table
    replacement = r"\1</p>" + calendar_table
    html_new = re.sub(pattern, replacement, html)
    
    if html_new != html:
        logger.info("Successfully inserted Athasian Calendar table")
    else:
        logger.warning("Could not find insertion point for Athasian Calendar table")
    
    return html_new


def _fix_calendar_paragraph_breaks(html: str) -> str:
    """
    Fix paragraph breaks in The Athasian Calendar section.
    
    The section should have 6 paragraphs with breaks at:
    1. After "Every 77 years..." ending with "...a new year of Ral's Fury."
    2. After "So, the first year..." ending with "...a year of Guthay's Agitation."
    3. At "Superstition and folklore..." (usually already correct after table insertion)
    4. At "Each year is made up..."
    5. At "Days are kept track of in a variety of ways..."
    """
    logger.info("Fixing calendar paragraph breaks")
    
    # Break 1: After "Every 77 years...a new year of Ral's Fury."
    html = re.sub(
        r'(a new year of Ral&#x27;s Fury\.) (Each 77-year cycle)',
        r'\1</p><p>\2',
        html
    )
    
    # Break 2: After "So, the first year...a year of Guthay's Agitation."
    html = re.sub(
        r'(a year of Guthay&#x27;s Agitation\.)(</p><table)',
        r'\1</p>\2',
        html
    )
    
    # Break 3: After "the list goes on." before "Each year is made up"
    html = re.sub(
        r'(the list goes on\.) (Each year is made up)',
        r'\1</p><p>\2',
        html
    )
    
    # Break 4: After the sentence ending with "nighttime ceremonies)." before "Days are kept track"
    html = re.sub(
        r'(in nighttime ceremonies\)\.) (Days are kept track)',
        r'\1</p><p>\2',
        html
    )
    
    logger.info("Fixed calendar paragraph breaks")
    return html


def _remove_calendar_table_headers_from_toc(html: str) -> str:
    """
    Remove "The Endlean Cycle" and "The Seofean Cycle" from the table of contents
    and from appearing as document headers.
    """
    logger.info("Removing calendar table headers from TOC")
    
    # Count occurrences before removal
    end_cycle_matches_before = len(re.findall(r'the-endlean-cycle', html))
    seo_cycle_matches_before = len(re.findall(r'the-seofean-cycle', html))
    logger.info(f"Before removal: {end_cycle_matches_before} 'endlean' matches, {seo_cycle_matches_before} 'seofean' matches")
    
    # Remove from TOC - match the full list item with link
    html = re.sub(
        r'<li><a href="#header-\d+-the-endlean-cycle">The Endlean Cycle</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-the-seofean-cycle">The Seofean Cycle</a></li>',
        '',
        html
    )
    
    # Remove the header paragraphs themselves
    html = re.sub(
        r'<p id="header-\d+-the-endlean-cycle">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-the-seofean-cycle">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Count occurrences after removal
    end_cycle_matches_after = len(re.findall(r'the-endlean-cycle', html))
    seo_cycle_matches_after = len(re.findall(r'the-seofean-cycle', html))
    logger.info(f"After removal: {end_cycle_matches_after} 'endlean' matches, {seo_cycle_matches_after} 'seofean' matches")
    
    # Remove the incorrectly rendered paragraph containing the table data
    # This paragraph starts immediately after "a year of Guthay's Agitation." and contains
    # "Fury Ral Friend Contemplation..." before "Superstition and folklore"
    pattern = r'(<p>Fury Ral Friend Contemplation.*?King Silt Enemy Guthay )(Superstition and folklore.*?</p>)'
    replacement = r'<p>\2'
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    
    logger.info("Removed calendar table headers from TOC and document")
    return html


def _clean_up_table_fragments(html: str) -> str:
    """
    Clean up incorrectly rendered table fragments.
    
    There are several malformed tables at various points in the document
    that need to be removed.
    """
    logger.info("Cleaning up table fragments")
    
    # Remove the extraneous table fragments after "Starting the Campaign"
    # These contain text like "night one can read by the messengers light"
    pattern = r'<table class="ds-table"><tr><td>Ral</td><td>Fury</td><td>night one can read by.*?</table>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    pattern = r'<table class="ds-table"><tr><td>Friend Desert</td><td>Contemplation Vengeance</td>.*?</table>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    pattern = r'<table class="ds-table"><tr><td>Priest</td><td>Slumber</td><td>years to deliver.*?</table>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    pattern = r'<table class="ds-table"><tr><td>W i n d Dragon</td><td>Defiance Reverence</td>.*?</table>'
    html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    logger.info("Cleaned up table fragments")
    return html


def _fix_dehydration_table(html: str) -> str:
    """
    Fix the Dehydration Effects table which may have header issues.
    """
    logger.info("Fixing dehydration table")
    
    # Remove the incorrectly rendered "Amount of Water" and "Constitution Loss" headers
    # These should be table column headers, not document headers
    html = re.sub(
        r'<p id="header-\d+-amount-of-water">.*?Amount of Water.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-constitution-loss">.*?Constitution Loss.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove from TOC
    html = re.sub(
        r'<li><a href="#header-\d+-amount-of-water">Amount of Water</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-constitution-loss">Constitution Loss</a></li>',
        '',
        html
    )
    
    # Insert properly formatted dehydration table
    # Find the "Dehydration Effects Table" header and add table after it
    dehydration_table = '''
<table class="ds-table">
<thead>
<tr>
<th>Amount of Water</th>
<th>Constitution Loss</th>
</tr>
</thead>
<tbody>
<tr><td>Full requirement</td><td>None</td></tr>
<tr><td>Half or more of requirement</td><td>1d4</td></tr>
<tr><td>Less than half of requirement</td><td>1d6</td></tr>
</tbody>
</table>
'''
    
    # Check if table already exists
    if '<th>Amount of Water</th>' not in html:
        # Insert after "Dehydration Effects Table" header
        pattern = r'(<p id="header-\d+-dehydration-effects-table">.*?Dehydration Effects Table.*?</p>)'
        replacement = r'\1' + dehydration_table
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)
        logger.info("Inserted dehydration effects table")
    
    # Remove the incorrectly rendered table data
    # The raw data has the values reversed from what they should be
    pattern = r'<p>None Full requirement Half or more of requirement 1d4 Less than half of requirement 1d6</p>'
    html = re.sub(pattern, '', html)
    
    logger.info("Fixed dehydration table")
    return html


def _fix_overland_movement_section(html: str) -> str:
    """
    Fix the Overland Movement section to ensure proper paragraph breaks and table placement.
    
    The section should have:
    1. A paragraph ending with "forced march."
    2. A second paragraph starting with "The races of Dark Sun" and ending with "these differences."
    3. The Race/Movement Points/Force March table
    4. The legend paragraph with *, **, ***
    
    Additionally, removes incorrect headers for "Race", "Movement Points", "Force March", 
    "Movement Cost", and "Terrain Type" which should be table column headers, not document headers.
    """
    logger.info("Fixing Overland Movement section")
    
    # Remove "Movement Points" and "Force March" as document headers from TOC
    # Use flexible regex to match any header number
    html = re.sub(
        r'<li><a href="#header-\d+-movement-points">Movement Points</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-force-march">Force March</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-movement-cost">Movement Cost</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-terrain-type">Terrain Type</a></li>',
        '',
        html
    )
    
    # Remove the header elements themselves
    html = re.sub(
        r'<p id="header-\d+-movement-points">.*?Movement Points.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-force-march">.*?Force March.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-movement-cost">.*?Movement Cost.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-terrain-type">.*?Terrain Type.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove malformed paragraph with race names
    # Match the exact text as it appears in the HTML
    # Note: _fix_letter_spacing may partially fix "M u l" to "Mu l" with a space
    html = re.sub(
        r'<p>Human Dwarf Elf Half-elf Half-giant Halfling Mu\s*l \* \* Thri-kreen\*\*\*</p>',
        '',
        html
    )
    
    # Remove malformed tables that mix unrelated text with race data
    # The main one appears RIGHT after the legend paragraph
    # Note: Letter-spacing may not be fixed yet, so handle "E l f" and "Elf"
    patterns_to_remove = [
        # Big malformed table with Elf and Half-elf data - appears immediately after legend
        # This is the primary culprit - with letter spacing
        r'<table class="ds-table"><tr><td>need\s+I/8\s+gallon; small animals need ½ gallon; man-</td><td>E\s*l\s*f\s+24</td><td>30</td></tr><tr><td>sized animals need 1 gallon; larger than man-sized animals need 4 gallons; huge animals need 8 gal-</td><td>Half-elf 24</td><td>30</td></tr></table>',
        # Same table but without letter spacing (in case _fix_letter_spacing runs before)
        r'<table class="ds-table"><tr><td>need\s+I/8\s+gallon; small animals need ½ gallon; man-</td><td>Elf 24</td><td>30</td></tr><tr><td>sized animals need 1 gallon; larger than man-sized animals need 4 gallons; huge animals need 8 gal-</td><td>Half-elf 24</td><td>30</td></tr></table>',
        # Table with "Animals and Dehydration" mixed with race data
        r'<table class="ds-table"><tr><td>Animals and Dehydration</td><td>Human 24</td><td>30 15</td></tr>.*?</table>',
        # Table with dehydration text and Dwarf data
        r'<table class="ds-table"><tr><td>Animals also suffer dehydration\. Tiny animals</td><td>Dwarf 12</td></tr></table>',
        # Other malformed variations
        r'<table class="ds-table"><tr><td>need\s+I/8\s+gallon[^<]*</td><td>E\s*l\s*f\s+24</td>.*?</table>',
        r'<table class="ds-table"><tr><td>need\s+I/8\s+gallon[^<]*</td><td>Elf 24</td>.*?</table>',
        r'<table class="ds-table"><tr><td>sized animals need 1 gallon[^<]*</td><td>Half-elf 24</td>.*?</table>',
        # Table with gallon amounts and Halfling/Mul data
        r'<table class="ds-table"><tr><td>lons; gargantuan animals need 16 gallons of water</td><td>Halfling 12</td><td>15</td></tr>.*?</table>',
        # Tables after Kank section
        r'<table class="ds-table"><tr><td>or 30 \(his forced march rate\) to determine his actual movement in miles \(or points\) per day\.</td><td>Inix</td><td>15 9</td></tr>.*?</table>',
        r'<table class="ds-table"><tr><td>Mountains</td><td>8 2</td><td>those used on other AD&amp;D campaign worlds\. A</td></tr>.*?</table>',
    ]
    
    for pattern in patterns_to_remove:
        html = re.sub(pattern, '', html, flags=re.DOTALL)
    
    # Split the legend into three separate paragraphs
    # The legend is currently one paragraph with *, **, and ***
    legend_pattern = r'<p>\* For overland movement, an elf may add his Constitution score to 24 \(his normal movement rate\) or 30 \(his forced march rate\) to determine his actual movement in miles \(or points\) per day\. \*\* This is for a normal 10-hour marching day\. A mul can move for 20 hours per day on each of three consecutive days\. The fourth day, however, must be one of rest in which the character only travels for 10 hours\. A "resting" mul can still force march\. \*\*\* This is for a normal 10-hour marching day\. A thri-kreen can always move for 20 hours per day\.</p>'
    
    legend_replacement = '''<p>* For overland movement, an elf may add his Constitution score to 24 (his normal movement rate) or 30 (his forced march rate) to determine his actual movement in miles (or points) per day.</p>
<p>** This is for a normal 10-hour marching day. A mul can move for 20 hours per day on each of three consecutive days. The fourth day, however, must be one of rest in which the character only travels for 10 hours. A "resting" mul can still force march.</p>
<p>*** This is for a normal 10-hour marching day. A thri-kreen can always move for 20 hours per day.</p>'''
    
    html = re.sub(legend_pattern, legend_replacement, html)
    
    # Remove duplicate legend paragraph (appears after malformed content)
    # The correct legend is "</table><p>* For overland..." (with space after *)
    # The duplicate is "<p>*For overland..." (no space after *)
    # Remove only the duplicate that appears AFTER the malformed content
    html = re.sub(
        r'<p>\*For overland movement, an elf may add his Constitution score to 24 \(his normal movement rate\) or 30 \(his forced march rate\) to determine his actual movement in miles \(or points\) per day\. \*\* This is for a normal 10-hour marching day\. A mul can move for 20 hours per day on each of three consecutive days\. The fourth day, however, must be one of rest in which the character only travels for 10 hours\. A &quot;resting&quot; mul can still force march\. \*\*\* This is for a normal 10-hour marching day\. A thri-kreen can always move for 20 hours per day\.</p>',
        '',
        html
    )
    
    # Remove duplicate terrain list after Terrain Costs table
    # This is a line of text that duplicates the terrain types already in the table
    html = re.sub(
        r'<p>Sandy Wastes Rocky Badlands Mountains Scrub Plains Forest Salt Flats Boulder Fields</p>',
        '',
        html
    )
    
    # Remove "Mount" as a document header (it's a table column header, not a section header)
    html = re.sub(
        r'<p id="header-\d+-mount">.*?<span[^>]*>Mount</span>.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove from TOC
    html = re.sub(
        r'<li><a href="#header-\d+-mount">Mount</a></li>',
        '',
        html
    )
    
    # Remove the paragraph with just mount names (should be in table instead)
    html = re.sub(
        r'<p>Kank Inix Mekillot</p>',
        '',
        html
    )
    
    # Insert the Mounted Movement table after "most common mounts." 
    # The table should appear between that sentence and "These overland"
    mounted_table_html = '''<table class="ds-table">
<tr><th>Mount</th><th>Movement Points</th></tr>
<tr><td>Kank</td><td>12</td></tr>
<tr><td>Inix</td><td>15</td></tr>
<tr><td>Mekillot</td><td>9</td></tr>
</table>
'''
    
    # Find the location to insert the table
    # It should be after "most common mounts.</p>" and before "<p>These overland"
    mounted_section_pattern = r'(most common mounts\.</p>)\s*(<p>These overland)'
    mounted_replacement = r'\1\n' + mounted_table_html + r'\n\2'
    
    html = re.sub(mounted_section_pattern, mounted_replacement, html)
    
    # Fix paragraph breaks in Kank section (should have 3 paragraphs)
    # First, merge the split sentence about green honey
    html = re.sub(
        r'(it can be eaten by all the player)</p>\s*<p>(character races)',
        r'\1 \2',
        html
    )
    
    # Break at "All kank mounts are of"
    html = re.sub(
        r'(to avoid dehydration\.) (All kank mounts are of)',
        r'\1</p>\n<p>\2',
        html
    )
    # Break at "A kank pushed to"
    html = re.sub(
        r'(does not produce honey\.) (A kank pushed to)',
        r'\1</p>\n<p>\2',
        html
    )
    
    # Fix paragraph breaks in Inix section (should have 2 paragraphs)
    # Break at "An inix can be pushed"
    html = re.sub(
        r'(to dehydration\.) (An inix can be pushed)',
        r'\1</p>\n<p>\2',
        html
    )
    
    # Fix paragraph breaks in Mekillot section (should have 3 paragraphs)
    # Break at "When in use as a pack"
    html = re.sub(
        r'(per day\.) (When in use as a pack)',
        r'\1</p>\n<p>\2',
        html
    )
    # Break at "A mekillot cannot be pushed"
    html = re.sub(
        r'(to attack\.) (A mekillot)',
        r'\1</p>\n<p>\2',
        html
    )
    
    # Fix paragraph breaks in Use of Vehicles section (should have 5 paragraphs)
    # Break at "Wagons can be easily broken"
    html = re.sub(
        r'(animal handling proficiency\.) (Wagons can be easily broken)',
        r'\1</p>\n<p>\2',
        html
    )
    # Break at "A wagon moves at the speed"
    html = re.sub(
        r'(engineering proficiency\.) (A wagon moves at the speed)',
        r'\1</p>\n<p>\2',
        html
    )
    # Break at "Chariots are just as described"
    html = re.sub(
        r'(pulling a wagon\.) (Chariots)',
        r'\1</p>\n<p>\2',
        html
    )
    # Break at "Howdahs are are small structures"
    html = re.sub(
        r'(at high speeds\.) (Howdahs)',
        r'\1</p>\n<p>\2',
        html
    )
    
    logger.info("Fixed Overland Movement section")
    return html


def _fix_movement_by_night_paragraphs(html: str) -> str:
    """
    Fix paragraph breaks in the "Movement by Night" section.
    
    The text "The draw back to such plans is that good rest under the blistering sun..."
    should be one continuous paragraph with "drawback" as one word.
    """
    logger.info("Fixing Movement by Night paragraph breaks")
    
    # Fix "The draw back" -> "The drawback" (one word)
    html = re.sub(
        r'The draw back',
        'The drawback',
        html
    )
    
    logger.info("Fixed Movement by Night paragraph breaks")
    return html


def _fix_whitespace_issues(html: str) -> str:
    """
    Fix whitespace issues in Chapter 14 HTML that weren't caught during extraction.
    
    Examples:
    - "M u l" should be "Mul"
    - "E l f" should be "Elf"
    - "R a c e" should be "Race"
    - "Fo r" should be "For"
    - "Wi n d" should be "Wind"
    """
    logger.info("Fixing whitespace issues in HTML")
    
    # Fix "M u l" -> "Mul"
    html = re.sub(r'\bM u l\b', 'Mul', html)
    
    # Fix "E l f" -> "Elf"
    html = re.sub(r'\bE l f\b', 'Elf', html)
    
    # Fix "R a c e" -> "Race" (but not in ID attributes)
    html = re.sub(r'<span[^>]*>R a c e</span>', '<span style="color: #ca5804">Race</span>', html)
    html = re.sub(r'>R a c e<', '>Race<', html)
    
    # Fix "Fo r" -> "For" in all contexts (text, headers, and IDs)
    html = re.sub(r'Fo r', 'For', html)
    # Also fix the ID which has "f-o-r" with hyphens (generated from "Fo r" -> slug becomes "f-o-r")
    html = re.sub(r'f-o-r-overland', 'for-overland', html)
    
    # Fix "Wi n d" -> "Wind"
    html = re.sub(r'\bWi n d\b', 'Wind', html)
    
    logger.info("Fixed whitespace issues")
    return html

