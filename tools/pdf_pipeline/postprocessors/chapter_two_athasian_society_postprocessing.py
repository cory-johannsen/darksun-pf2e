"""
Chapter Two: Athasian Society HTML Postprocessing

Handles mid-paragraph breaks that can't be handled at the PDF extraction level.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def apply_intro_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the intro section before Barrenness.
    
    Breaks:
    - "On Athas, there are"
    - "Surprisingly, all of these"
    """
    logger.info("Applying intro section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "On Athas, there are"
        (r'(\. )(On Athas, there are)', r'\1</p>\n<p>\2'),
        # Break before "Surprisingly, all of these"
        (r'(\. )(Surprisingly, all of these)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied intro paragraph break: {pattern[:50]}...")
    
    return html


def apply_barrenness_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Barrenness section.
    
    Breaks (5 paragraphs total):
    - "Hunting tribes"
    - "The lives of"
    - "City dwellers"
    - "Given the importance"
    """
    logger.info("Applying Barrenness section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Hunting tribes"
        (r'(\. )(Hunting tribes)', r'\1</p>\n<p>\2'),
        # Break before "The lives of"
        (r'(\. )(The lives of)', r'\1</p>\n<p>\2'),
        # Break before "City dwellers"
        (r'(\. )(City dwellers)', r'\1</p>\n<p>\2'),
        # Break before "Given the importance"
        (r'(\. )(Given the importance)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Barrenness paragraph break: {pattern[:50]}...")
    
    return html


def apply_metal_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Metal section.
    
    Breaks (10 paragraphs total):
    - "Unfortunately, metals"
    - "The scarcity of metal"
    - "The scarcity of resources"
    - "In war, the advantages"
    - "Who can doubt that"
    - "As I have stated earlier"
    - "Still, lucky treasure"
    - "I have heard tales that suits"
    - "There are even rumors"
    """
    logger.info("Applying Metal section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Unfortunately, metals"
        (r'(\. )(Unfortunately, metals)', r'\1</p>\n<p>\2'),
        # Break before "The scarcity of metal"
        (r'(\. )(The scarcity of metal)', r'\1</p>\n<p>\2'),
        # Break before "The scarcity of resources"
        (r'(\. )(The scarcity of resources)', r'\1</p>\n<p>\2'),
        # Break before "In war, the advantages"
        (r'(\. )(In war, the advantages)', r'\1</p>\n<p>\2'),
        # Break before "Who can doubt that"
        (r'(! )(Who can doubt that)', r'!</p>\n<p>\2'),
        # Break before "As I have stated earlier"
        (r'(\. )(As I have stated earlier)', r'\1</p>\n<p>\2'),
        # Break before "Still, lucky treasure"
        (r'(\. )(Still, lucky treasure)', r'\1</p>\n<p>\2'),
        # Break before "I have heard tales that suits"
        (r'(\. )(I have heard tales that suits)', r'\1</p>\n<p>\2'),
        # Break before "There are even rumors"
        (r'(\. )(There are even rumors)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Metal paragraph break: {pattern[:50]}...")
    
    return html


def apply_psionics_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Psionics section.
    
    Breaks (5 paragraphs total):
    - "Each culture"
    - "Psionic powers"
    - "Considering the potential"
    - "Psionics has often"
    """
    logger.info("Applying Psionics section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Each culture"
        (r'(\. )(Each culture)', r'\1</p>\n<p>\2'),
        # Break before "Psionic powers"
        (r'(\. )(Psionic powers)', r'\1</p>\n<p>\2'),
        # Break before "Considering the potential"
        (r'(\. )(Considering the potential)', r'\1</p>\n<p>\2'),
        # Break before "Psionics has often"
        (r'(\. )(Psionics has often)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Psionics paragraph break: {pattern[:50]}...")
    
    return html


def apply_elven_merchants_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Elven Merchants section (header-49).
    
    Breaks (15 paragraphs total):
    - "Instead, the tribe"
    - "Most tribes"
    - "In most cities"
    - "Although elves sell"
    - "Despite the elves' expertise"
    - "Most templars will not"
    - "Usually, a tribe stays"
    - "By the time the tribe"
    - "Outside the city"
    - "In most cultures"
    - "I was once with an"
    - "These affairs continued"
    - "Lest anyone make"
    - "Elven caravans are"
    """
    logger.info("Applying Elven Merchants section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Instead, the tribe"
        (r'(\. )(Instead, the tribe)', r'\1</p>\n<p>\2'),
        # Break before "Most tribes"
        (r'(\. )(Most tribes)', r'\1</p>\n<p>\2'),
        # Break before "In most cities"
        (r'(\. )(In most cities)', r'\1</p>\n<p>\2'),
        # Break before "Although elves sell"
        (r'(\. )(Although elves sell)', r'\1</p>\n<p>\2'),
        # Break before "Despite the elves' expertise"  (note: elves' with apostrophe)
        (r'(\. )(Despite the elves)', r'\1</p>\n<p>\2'),
        # Break before "Most templars will not"
        (r'(\. )(Most templars will not)', r'\1</p>\n<p>\2'),
        # Break before "Usually, a tribe stays"
        (r'(\. )(Usually, a tribe stays)', r'\1</p>\n<p>\2'),
        # Break before "By the time the tribe"
        (r'(\. )(By the time the tribe)', r'\1</p>\n<p>\2'),
        # Break before "Outside the city"
        (r'(\. )(Outside the city)', r'\1</p>\n<p>\2'),
        # Break before "In most cultures"
        (r'(\. )(In most cultures)', r'\1</p>\n<p>\2'),
        # Break before "I was once with an"
        (r'(\. )(I was once with an)', r'\1</p>\n<p>\2'),
        # Break before "These affairs continued"
        (r'(\. )(These affairs continued)', r'\1</p>\n<p>\2'),
        # Break before "Lest anyone make" (note: exclamation mark before it)
        (r'(!\s+)(Lest anyone make)', r'!</p>\n<p>\2'),
        # Break before "Elven caravans are"
        (r'(\. )(Elven caravans are)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Elven Merchants paragraph break: {pattern[:50]}...")
    
    return html


def apply_nomadic_herdsmen_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Nomadic Herdsmen section (header-50).
    
    Breaks (9 paragraphs total):
    - "It is a practical impossibility"
    - "Most herders rely"
    - "The first time"
    - "Aside from their eggs"
    - "Considering the value"
    - "As you might expect"
    - "The douars are generally"
    - "Herdsmen have a deep"
    """
    logger.info("Applying Nomadic Herdsmen section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "It is a practical impossibility"
        (r'(\. )(It is a practical impossibility)', r'\1</p>\n<p>\2'),
        # Break before "Most herders rely"
        (r'(\. )(Most herders rely)', r'\1</p>\n<p>\2'),
        # Break before "The first time"
        (r'(\. )(The first time)', r'\1</p>\n<p>\2'),
        # Break before "Aside from their eggs"
        (r'(\. )(Aside from their eggs)', r'\1</p>\n<p>\2'),
        # Break before "Considering the value"
        (r'(\. )(Considering the value)', r'\1</p>\n<p>\2'),
        # Break before "As you might expect"
        (r'(\. )(As you might expect)', r'\1</p>\n<p>\2'),
        # Break before "The douars are generally"
        (r'(\. )(The douars are generally)', r'\1</p>\n<p>\2'),
        # Break before "Herdsmen have a deep"
        (r'(\. )(Herdsmen have a deep)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Nomadic Herdsmen paragraph break: {pattern[:50]}...")
    
    return html


def apply_elven_herdsmen_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Elven Herdsmen section (header-51).
    
    Breaks (9 paragraphs total):
    - "What other races"
    - "Admittedly,"
    - "This free-for-all"
    - "Whatever the sex"
    - "Elven tribes"
    - "Kanks can eat"
    - "Of course, there"
    - "Aside from its honey"
    """
    logger.info("Applying Elven Herdsmen section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "What other races"
        (r'(\. )(What other races)', r'\1</p>\n<p>\2'),
        # Break before "Admittedly,"
        (r'(! )(Admittedly,)', r'!</p>\n<p>\2'),
        # Break before "This free-for-all"
        (r'(\. )(This free-for-all)', r'\1</p>\n<p>\2'),
        # Break before "Whatever the sex"
        (r'(\. )(Whatever the sex)', r'\1</p>\n<p>\2'),
        # Break before "Elven tribes"
        (r'(\. )(Elven tribes)', r'\1</p>\n<p>\2'),
        # Break before "Kanks can eat"
        (r'(\. )(Kanks can eat)', r'\1</p>\n<p>\2'),
        # Break before "Of course, there"
        (r'(\. )(Of course, there)', r'\1</p>\n<p>\2'),
        # Break before "Aside from its honey"
        (r'(\. )(Aside from its honey)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Elven Herdsmen paragraph break: {pattern[:50]}...")
    
    return html


def apply_raiding_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Raiding Tribes section (header-52).
    
    Breaks (4 paragraphs total):
    - "Although raiders"
    - "Most raiders"
    - "Usually, the raiding"
    """
    logger.info("Applying Raiding Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Although raiders"
        (r'(\. )(Although raiders)', r'\1</p>\n<p>\2'),
        # Break before "Most raiders"
        (r'(\. )(Most raiders)', r'\1</p>\n<p>\2'),
        # Break before "Usually, the raiding"
        (r'(\. )(Usually, the raiding)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Raiding Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_slave_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Slave Tribes section (header-53).
    
    Breaks (5 paragraphs total):
    - "Though slave tribes"
    - "Slave tribes vary"
    - "Second, slave tribes"
    - "Finally, most raiding tribes"
    """
    logger.info("Applying Slave Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Though slave tribes"
        (r'(\. )(Though slave tribes)', r'\1</p>\n<p>\2'),
        # Break before "Slave tribes vary" (after exclamation mark)
        (r'(! )(Slave tribes vary)', r'!</p>\n<p>\2'),
        # Break before "Second, slave tribes"
        (r'(\. )(Second, slave tribes)', r'\1</p>\n<p>\2'),
        # Break before "Finally, most raiding tribes"
        (r'(\. )(Finally, most raiding tribes)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Slave Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_giant_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Giant Tribes section (header-54).
    
    Breaks (5 paragraphs total):
    - "Fortunately, giants"
    - "As a cautionary note"
    - "First, never assume"
    - "Second, never visit"
    """
    logger.info("Applying Giant Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Fortunately, giants"
        (r'(\. )(Fortunately, giants)', r'\1</p>\n<p>\2'),
        # Break before "As a cautionary note"
        (r'(\. )(As a cautionary note)', r'\1</p>\n<p>\2'),
        # Break before "First, never assume"
        (r'(<p>)(First, never assume)', r'\1\2'),  # Already at start of paragraph
        # Break before "Second, never visit"
        (r'(\. )(Second, never visit)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Giant Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_thri_kreen_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Thri-kreen Tribes section (header-55).
    
    Breaks (4 paragraphs total):
    - "The fact that they never"
    - "Most often, raiding"
    - "Thri-kreen are intelligent"
    """
    logger.info("Applying Thri-kreen Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "The fact that they never"
        (r'(\. )(The fact that they never)', r'\1</p>\n<p>\2'),
        # Break before "Most often, raiding"
        (r'(\. )(Most often, raiding)', r'\1</p>\n<p>\2'),
        # Break before "Thri-kreen are intelligent"
        (r'(\. )(Thri-kreen are intelligent)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Thri-kreen Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_halfling_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Halfling Tribes section (header-56).
    
    Breaks (4 paragraphs total):
    - "That does not change the effects"
    - "Such raiding parties"
    - "There are two other"
    """
    logger.info("Applying Halfling Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "That does not change the effects"
        (r'(\. )(That does not change the effects)', r'\1</p>\n<p>\2'),
        # Break before "Such raiding parties"
        (r'(\. )(Such raiding parties)', r'\1</p>\n<p>\2'),
        # Break before "There are two other"
        (r'(\. )(There are two other)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Halfling Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_elf_tribes_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Elf Tribes section (header-57).
    
    Breaks (3 paragraphs total):
    - "Attacks by elven"
    - "For more information"
    """
    logger.info("Applying Elf Tribes section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Attacks by elven"
        (r'(\. )(Attacks by elven)', r'\1</p>\n<p>\2'),
        # Break before "For more information"
        (r'(\. )(For more information)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Elf Tribes paragraph break: {pattern[:50]}...")
    
    return html


def apply_hunting_gathering_clans_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Hunting and Gathering Clans section (header-58).
    
    Breaks (3 paragraphs total):
    - "Their lifestyle is the most"
    - "Most hunting and gathering clans"
    """
    logger.info("Applying Hunting and Gathering Clans section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Their lifestyle is the most"
        (r'(\. )(Their lifestyle is the most)', r'\1</p>\n<p>\2'),
        # Break before "Most hunting and gathering clans"
        (r'(\. )(Most hunting and gathering clans)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Hunting and Gathering Clans paragraph break: {pattern[:50]}...")
    
    return html


def apply_thri_kreen_hunting_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Thri-kreen section under Hunting and Gathering Clans (header-59).
    
    Breaks (4 paragraphs total):
    - "The thri-kreen pack"
    - "This pack instinct can"
    - "Once it joins a group"
    """
    logger.info("Applying Thri-kreen (hunting) section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "The thri-kreen pack"
        (r'(\. )(The thri-kreen pack)', r'\1</p>\n<p>\2'),
        # Break before "This pack instinct can"
        (r'(\. )(This pack instinct can)', r'\1</p>\n<p>\2'),
        # Break before "Once it joins a group"
        (r'(\. )(Once it joins a group)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Thri-kreen (hunting) paragraph break: {pattern[:50]}...")
    
    return html


def apply_halflings_hunting_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Halflings section under Hunting and Gathering Clans (header-60).
    
    Breaks (5 paragraphs total):
    - "The halfling clans"
    - "When some disaster"
    - "Unfortunately for us"
    - "When away from their own kind"
    """
    logger.info("Applying Halflings (hunting) section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "The halfling clans"
        (r'(\. )(The halfling clans)', r'\1</p>\n<p>\2'),
        # Break before "When some disaster"
        (r'(\. )(When some disaster)', r'\1</p>\n<p>\2'),
        # Break before "Unfortunately for us"
        (r'(\. )(Unfortunately for us)', r'\1</p>\n<p>\2'),
        # Break before "When away from their own kind"
        (r'(\. )(When away from their own kind)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Halflings (hunting) paragraph break: {pattern[:50]}...")
    
    return html


def apply_hermits_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Hermits section (header-61).
    
    Breaks (5 paragraphs total):
    - "Usually, hermits live"
    - "Occasionally, if you"
    - "Some hermits are crazy"
    - "Of course, there are"
    """
    logger.info("Applying Hermits section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Usually, hermits live"
        (r'(\. )(Usually, hermits live)', r'\1</p>\n<p>\2'),
        # Break before "Occasionally, if you"
        (r'(\. )(Occasionally, if you)', r'\1</p>\n<p>\2'),
        # Break before "Some hermits are crazy"
        (r'(\. )(Some hermits are crazy)', r'\1</p>\n<p>\2'),
        # Break before "Of course, there are"
        (r'(\. )(Of course, there are)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Hermits paragraph break: {pattern[:50]}...")
    
    return html


def apply_psionic_masters_hermit_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Psionic Masters section under Hermits (header-62).
    
    Breaks (4 paragraphs total):
    - "Often, psionic masters"
    - "When this happens"
    - "Usually, a few"
    """
    logger.info("Applying Psionic Masters (hermit type) section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Often, psionic masters"
        (r'(\. )(Often, psionic masters)', r'\1</p>\n<p>\2'),
        # Break before "When this happens"
        (r'(\. )(When this happens)', r'\1</p>\n<p>\2'),
        # Break before "Usually, a few"
        (r'(\. )(Usually, a few)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Psionic Masters paragraph break: {pattern[:50]}...")
    
    return html


def apply_druids_hermit_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for the Druids section under Hermits (header-63).
    
    Breaks (4 paragraphs total):
    - "Obviously, a druid"
    - "Most druids have"
    - "Thankfully, druids do"
    """
    logger.info("Applying Druids (hermit type) section paragraph breaks")
    
    mid_para_breaks = [
        # Break before "Obviously, a druid"
        (r'(\. )(Obviously, a druid)', r'\1</p>\n<p>\2'),
        # Break before "Most druids have"
        (r'(\. )(Most druids have)', r'\1</p>\n<p>\2'),
        # Break before "Thankfully, druids do"
        (r'(\. )(Thankfully, druids do)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied Druids paragraph break: {pattern[:50]}...")
    
    return html


def fix_tribe_headers_styling(html: str) -> str:
    """
    Fix styling and remove Roman numerals from tribe headers.
    
    These headers should be H2 (h2-header class) without Roman numerals:
    - Slave Tribes (header-53)
    - Giant Tribes (header-54)
    - Halfling Tribes (header-56)
    """
    logger.info("Fixing tribe headers styling and removing Roman numerals")
    
    tribe_headers = [
        ("header-53-slave-tribes", "Slave Tribes"),
        ("header-54-giant-tribes", "Giant Tribes"),
        ("header-56-halfling-tribes", "Halfling Tribes"),
    ]
    
    for header_id, header_text in tribe_headers:
        # Pattern: <p id="header-ID">ROMAN.  <a href...>[^]</a> <span...>Header Text</span></p>
        # Replace with: <p class="h2-header" id="header-ID"><a href...>[^]</a> <span...>Header Text</span></p>
        # Roman numeral pattern: [IVXLCDM]+ matches all Roman numerals (I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{re.escape(header_text)}</span></p>'
        replacement = f'<p class="h2-header" id="{header_id}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Fixed styling for '{header_text}' - removed Roman numeral and added h2-header class")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def adjust_header_levels(html: str) -> str:
    """
    Adjust header levels for specified sections by adding CSS classes.
    
    H2 headers (subheaders with h2-header CSS class):
    - Life Energy and Magic
    - The Veiled Alliance (first occurrence)
    - The Worst Scourge
    - The Sorcerer Kings
    - The Templars
    - The Nobility
    - The Freemen
    - Merchants
    - Elven Merchants
    - Slaves
    - Wizards
    - Humans (under Race in the Cities)
    - Dwarves (under Race in the Cities)
    - Elves (under Race in the Cities)
    - Half-elves (under Race in the Cities)
    - Half-giants (under Race in the Cities)
    - Muls (under Race in the Cities)
    - Thri-kreen (under Race in the Cities AND under Hunting and Gathering Clans)
    - Halflings (under Race in the Cities AND under Hunting and Gathering Clans)
    - Client Villages (under Villages)
    - Slave Villages (under Villages)
    - Dwarven Villages (under Villages)
    - Halfling Villages (under Villages)
    - Headquarters (under Dynastic Merchant Houses)
    - Emporiums (under Dynastic Merchant Houses)
    - Outposts (under Dynastic Merchant Houses)
    - Caravans (under Dynastic Merchant Houses)
    - Employment Terms (under Dynastic Merchant Houses)
    - The Merchant Code (under Dynastic Merchant Houses)
    - Psionic Masters (under Hermits)
    - Druids (under Hermits)
    
    H3 headers (sub-subheaders with h3-header CSS class):
    - Gladiators
    - Artists
    - Soldier Slaves
    - Laborers
    - Farmers
    - Defilers
    - The Veiled Alliance (second occurrence under Wizards)
    """
    logger.info("Adjusting header levels for Chapter Two: Athasian Society")
    
    # Headers to convert to H2 (larger subheaders)
    h2_headers = [
        "Life Energy and Magic",
        "The Worst Scourge",
        "The Sorcerer Kings",
        "The Templars",
        "The Nobility",
        "The Freemen",
        "Merchants",
        "Elven Merchants",
        "Slaves",
        "Wizards",
        # Race in the Cities subsections
        "Humans",
        "Dwarves",
        "Elves",
        "Half-elves",
        "Half-giants",
        "Muls",
        "Thri-kreen",
        "Halflings",
        # Villages subsections
        "Client Villages",
        "Slave Villages",
        "Dwarven Villages",
        "Halfling Villages",
        # Dynastic Merchant Houses subsections
        "Headquarters",
        "Emporiums",
        "Outposts",
        "Caravans",
        "Employment Terms",
        "The Merchant Code",
        # Tribe subsections
        "Slave Tribes",
        "Giant Tribes",
        "Thri-kreen Tribes",
        "Halfling Tribes",
        "Elf Tribes",
        # Hermits subsections
        "Psionic Masters",
        "Druids",
    ]
    
    # Headers to convert to H3 (smaller subheaders)
    h3_headers = [
        "Gladiators",
        "Artists",
        "Soldier Slaves",
        "Laborers",
        "Farmers",
        "Defilers",
        # Employment Terms subsections
        "Family members",
        "Senior agents",
        "Regular agents",
        "Hirelings",
    ]
    
    # The first "The Veiled Alliance" should be H2, the second should be H3
    # We'll handle these specially
    
    # Add h2-header class to H2 headers and remove Roman numerals
    # Use a single regex substitution for all headers
    for header_text in h2_headers:
        # Pattern 1: Match headers without class attribute (need to add h2-header and potentially remove Roman numeral)
        # Roman numeral pattern: [IVXLCDM]+ matches all Roman numerals (I=1, V=5, X=10, L=50, C=100, D=500, M=1000)
        pattern1 = rf'(<p id="header-\d+-[^"]+">)([IVXLCDM]+\.\s+<a[^>]+>\[.\]</a>\s+)?(<span style="color: #cd490a">{re.escape(header_text)}</span></p>)'
        replacement1 = rf'<p class="h2-header" id="header-\3"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">{header_text}</span></p>'
        
        def replace_header(match):
            # Extract the ID from group 1
            id_match = re.search(r'id="([^"]+)"', match.group(1))
            if id_match:
                header_id = id_match.group(1)
                # Return replacement without Roman numeral
                return f'<p class="h2-header" id="{header_id}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">{header_text}</span></p>'
            return match.group(0)  # Return unchanged if no ID found
        
        # Replace headers without class attribute
        old_html = html
        html = re.sub(pattern1, replace_header, html)
        if html != old_html:
            logger.info(f"Processed '{header_text}'")
        
        # Pattern 2: Match headers that already have a class attribute but still have Roman numerals
        pattern2 = rf'<p class="[^"]*" id="(header-\d+-[^"]+)">([IVXLCDM]+\.\s+<a[^>]+>\[.\]</a>\s+)(<span style="color: #cd490a">{re.escape(header_text)}</span></p>)'
        replacement2 = rf'<p class="h2-header" id="\1"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> \3'
        
        old_html = html
        html = re.sub(pattern2, replacement2, html)
        if html != old_html:
            logger.info(f"Removed Roman numeral from '{header_text}' (already had class)")
    
    # Add h3-header class to H3 headers and remove Roman numerals
    for header_text in h3_headers:
        # Match the header pattern and add h3-header class
        # Remove Roman numeral prefix (group 2) since H3 headers don't get numerals
        # Use greedy match for the Roman numeral and link part
        # Pattern handles both with and without existing class attribute
        pattern = rf'<p\s+(?:class="[^"]*"\s+)?id="(header-\d+-[^"]+)">(.*?)<span style="color: #cd490a">{re.escape(header_text)}</span></p>'
        
        # Check if match contains Roman numeral to decide on replacement
        match = re.search(pattern, html)
        if match:
            # Check if group 2 starts with Roman numeral pattern
            if re.match(r'^\s*[IVXLCDM]+\.', match.group(2)):
                # Has Roman numeral, remove it
                replacement = f'<p class="h3-header" id="{match.group(1)}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">{header_text}</span></p>'
                html = html[:match.start()] + replacement + html[match.end():]
                logger.info(f"Added h3-header class to '{header_text}' and removed Roman numeral")
            else:
                # No Roman numeral, just add class
                replacement = f'<p class="h3-header" id="{match.group(1)}">{match.group(2)}<span style="color: #cd490a">{header_text}</span></p>'
                html = html[:match.start()] + replacement + html[match.end():]
                logger.info(f"Added h3-header class to '{header_text}'")
    
    # Handle "The Veiled Alliance" specially - first occurrence is H2, second is H3
    # Also remove Roman numerals from both since they are subheaders
    # Use greedy match for flexibility
    # Pattern handles both with and without existing class attribute
    veiled_pattern = r'<p\s+(?:class="[^"]*"\s+)?id="(header-\d+-the-veiled-alliance)">(.*?)<span style="color: #cd490a">The Veiled Alliance</span></p>'
    
    # Find all matches
    matches = list(re.finditer(veiled_pattern, html))
    if len(matches) >= 1:
        # First occurrence -> h2-header class (without Roman numeral)
        match = matches[0]
        replacement = f'<p class="h2-header" id="{match.group(1)}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">The Veiled Alliance</span></p>'
        html = html[:match.start()] + replacement + html[match.end():]
        logger.info("Added h2-header class to first 'The Veiled Alliance' and removed Roman numeral")
        
        # Re-find matches after first replacement
        matches = list(re.finditer(veiled_pattern, html))
        if len(matches) >= 1:
            # Second occurrence -> h3-header class (without Roman numeral)
            match = matches[0]
            replacement = f'<p class="h3-header" id="{match.group(1)}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a">The Veiled Alliance</span></p>'
            html = html[:match.start()] + replacement + html[match.end():]
            logger.info("Added h3-header class to second 'The Veiled Alliance' and removed Roman numeral")
    
    return html


def regenerate_toc(html: str) -> str:
    """
    Regenerate the table of contents to reflect updated header levels.
    
    This is necessary because header levels are adjusted in postprocessing,
    but the TOC was originally generated during the transformation stage.
    """
    logger.info("Regenerating table of contents for Chapter Two: Athasian Society")
    
    # Import the TOC generation function
    from tools.pdf_pipeline.transformers.journal_lib.toc import generate_table_of_contents
    
    # Extract the content section (everything after the TOC)
    content_match = re.search(r'<section class="content">.*', html, re.DOTALL)
    if not content_match:
        logger.warning("Could not find content section, skipping TOC regeneration")
        return html
    
    content_html = content_match.group(0)
    
    # Generate new TOC
    new_toc = generate_table_of_contents(content_html)
    
    # Replace old TOC with new one
    toc_pattern = r'<nav id="table-of-contents">.*?</nav>'
    html = re.sub(toc_pattern, new_toc, html, flags=re.DOTALL)
    
    logger.info("Table of contents regenerated successfully")
    return html


def fix_merchant_code_ordering(html: str) -> str:
    """
    Fix the ordering of The Merchant Code section content.
    
    Specifically, format the 7-item numbered list so each item appears on its own line.
    Currently they're merged into paragraphs.
    """
    logger.info("Fixing Merchant Code section ordering and list formatting")
    
    # Pattern for items 1-2 that are merged in one paragraph
    # "...tribe. 2. An oath...house."
    pattern0 = r'(1\. Recognition that by joining a merchant house, the agent forsakes citizenship in any city or membership in any tribe\.) (2\. An oath by all members of allegiance to the merchant house\.)'
    replacement0 = r'\1</p>\n<p>\2'
    html = re.sub(pattern0, replacement0, html)
    
    # Pattern for items 2-3-4 that are merged in one paragraph
    # "2. An oath...house. 3. A promise to perform...salary. 4. A promise to deal...alike."
    pattern1 = r'(2\. An oath by all members of allegiance to the merchant house\.) (3\. A promise to perform in the best interests of the merchant house in return for a specified salary\.) (4\. A promise to deal honestly with stranger, friend, and foe alike\.)'
    replacement1 = r'\1</p>\n<p>\2</p>\n<p>\3'
    html = re.sub(pattern1, replacement1, html)
    
    # Pattern for items 5-6-7 that are merged in one paragraph  
    # "5. A promise not to...house. 6. A promise to uphold...house. 7. A promise to cooperate...merchant."
    pattern2 = r'(<p>)(5\. A promise not to flaunt any wealth gained through employment with the house\.) (6\. A promise to uphold the laws of the city[^.]+down upon the house\.) (7\. A promise to cooperate with other merchants[^.]+any merchant\.)'
    replacement2 = r'\1\2</p>\n<p>\3</p>\n<p>\4'
    html = re.sub(pattern2, replacement2, html)
    
    logger.info("Applied numbered list formatting")
    return html


def postprocess_chapter_two_athasian_society(html: str) -> str:
    """
    Apply all HTML post-processing for Chapter Two: Athasian Society.
    """
    logger.info("Postprocessing Chapter Two: Athasian Society HTML")
    
    # Apply intro paragraph breaks
    html = apply_intro_paragraph_breaks(html)
    
    # Apply Barrenness paragraph breaks
    html = apply_barrenness_paragraph_breaks(html)
    
    # Apply Metal paragraph breaks
    html = apply_metal_paragraph_breaks(html)
    
    # Apply Psionics paragraph breaks
    html = apply_psionics_paragraph_breaks(html)
    
    # Apply Elven Merchants paragraph breaks
    html = apply_elven_merchants_paragraph_breaks(html)
    
    # Apply Nomadic Herdsmen paragraph breaks
    html = apply_nomadic_herdsmen_paragraph_breaks(html)
    
    # Apply Elven Herdsmen paragraph breaks
    html = apply_elven_herdsmen_paragraph_breaks(html)
    
    # Apply Raiding Tribes paragraph breaks
    html = apply_raiding_tribes_paragraph_breaks(html)
    
    # Apply Slave Tribes paragraph breaks
    html = apply_slave_tribes_paragraph_breaks(html)
    
    # Apply Giant Tribes paragraph breaks
    html = apply_giant_tribes_paragraph_breaks(html)
    
    # Apply Thri-kreen Tribes paragraph breaks
    html = apply_thri_kreen_tribes_paragraph_breaks(html)
    
    # Apply Halfling Tribes paragraph breaks
    html = apply_halfling_tribes_paragraph_breaks(html)
    
    # Apply Elf Tribes paragraph breaks
    html = apply_elf_tribes_paragraph_breaks(html)
    
    # Apply Hunting and Gathering Clans paragraph breaks
    html = apply_hunting_gathering_clans_paragraph_breaks(html)
    
    # Apply Thri-kreen (hunting) paragraph breaks
    html = apply_thri_kreen_hunting_paragraph_breaks(html)
    
    # Apply Halflings (hunting) paragraph breaks
    html = apply_halflings_hunting_paragraph_breaks(html)
    
    # Apply Hermits paragraph breaks
    html = apply_hermits_paragraph_breaks(html)
    
    # Apply Psionic Masters (hermit type) paragraph breaks
    html = apply_psionic_masters_hermit_paragraph_breaks(html)
    
    # Apply Druids (hermit type) paragraph breaks
    html = apply_druids_hermit_paragraph_breaks(html)
    
    # Fix tribe headers styling (remove Roman numerals, add h2-header class)
    html = fix_tribe_headers_styling(html)
    
    # Fix Merchant Code section ordering
    html = fix_merchant_code_ordering(html)
    
    # Adjust header levels
    html = adjust_header_levels(html)
    
    # Regenerate TOC to reflect the new header levels
    html = regenerate_toc(html)
    
    return html

