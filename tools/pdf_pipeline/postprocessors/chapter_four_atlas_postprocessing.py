"""
Chapter Four: Atlas of the Tyr Region HTML Post-Processing

This module handles paragraph breaks for Chapter Four: Atlas of the Tyr Region.
The PDF extraction merges paragraphs due to the 2-column layout, and this
postprocessor splits them at the correct locations.
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _find_content_between(html: str, start_pattern: str, end_pattern: str) -> Optional[Tuple[int, int, str]]:
    """
    Find content between two patterns.
    
    Args:
        html: The HTML string to search
        start_pattern: Regex pattern marking the start
        end_pattern: Regex pattern marking the end
        
    Returns:
        Tuple of (start_index, end_index, content) or None if not found
    """
    start_match = re.search(start_pattern, html, re.DOTALL)
    if not start_match:
        logger.debug(f"Could not find start pattern: {start_pattern}")
        return None
    
    end_match = re.search(end_pattern, html[start_match.end():], re.DOTALL)
    if not end_match:
        logger.debug(f"Could not find end pattern after start: {end_pattern}")
        return None
    
    start_idx = start_match.end()
    end_idx = start_match.end() + end_match.start()
    content = html[start_idx:end_idx]
    
    return (start_idx, end_idx, content)


def _split_paragraph_at_markers(content: str, markers: List[str]) -> List[str]:
    """
    Split content into paragraphs at specified markers.
    
    Args:
        content: The HTML content to split
        markers: List of text markers where splits should occur
        
    Returns:
        List of paragraph strings
    """
    # Normalize HTML entities for matching
    normalized = content.replace("&#x27;", "'").replace("&quot;", '"').replace("&amp;", "&")
    
    paragraphs = []
    start = 0
    
    for marker in markers:
        # Find the marker in normalized text
        pos = normalized.find(marker, start)
        
        if pos == -1:
            logger.debug(f"Could not find marker: '{marker}'")
            continue
        
        # Add the text up to this marker as a paragraph
        if pos > start:
            chunk = normalized[start:pos].strip()
            if chunk:
                paragraphs.append(chunk)
        
        # Move start position to the marker
        start = pos
    
    # Add the remaining content
    if start < len(normalized):
        chunk = normalized[start:].strip()
        if chunk:
            paragraphs.append(chunk)
    
    return paragraphs


def _wrap_paragraphs(paragraphs: List[str]) -> str:
    """
    Wrap paragraph text in <p> tags.
    
    Args:
        paragraphs: List of paragraph text strings
        
    Returns:
        HTML string with paragraphs wrapped
    """
    wrapped = []
    for para in paragraphs:
        if para.strip():
            wrapped.append(f"<p>{para}</p>")
    return "\n".join(wrapped)


def _split_main_intro(html: str) -> str:
    """
    Split the main intro section (before "Cities" header) into 5 paragraphs.
    
    Break points:
    - "That won't"
    - "Despite these"
    - "In honor of"
    - "The Tyr region"
    """
    logger.info("Splitting main intro section")
    
    result = _find_content_between(
        html,
        r'<a id="top"></a>',
        r'<p id="header-0-cities">'
    )
    
    if not result:
        logger.warning("Could not locate main intro section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract just the paragraph content (strip opening <p> and closing </p>)
    para_match = re.search(r'<p>(.*?)</p>', content, re.DOTALL)
    if not para_match:
        logger.warning("Could not extract intro paragraph content")
        return html
    
    para_content = para_match.group(1)
    
    # Split at markers
    markers = [
        "That won't",
        "Despite these",
        "In honor of",
        "The Tyr region"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 5:
        logger.warning(f"Expected 5 intro paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split main intro into {len(paragraphs)} paragraphs")
    return html


def _split_cities_section(html: str) -> str:
    """
    Split the "Cities" section into 2 paragraphs.
    
    Break point:
    - "Of course,"
    """
    logger.info("Splitting Cities section")
    
    result = _find_content_between(
        html,
        r'<p id="header-0-cities">.*?</p>',
        r'<p id="header-1-balic">'
    )
    
    if not result:
        logger.warning("Could not locate Cities section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract paragraph content
    para_match = re.search(r'<p>(.*?)</p>', content, re.DOTALL)
    if not para_match:
        logger.warning("Could not extract Cities paragraph content")
        return html
    
    para_content = para_match.group(1)
    
    # Split at marker
    markers = ["Of course,"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Cities paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Cities section into {len(paragraphs)} paragraphs")
    return html


def _split_balic_section(html: str) -> str:
    """
    Split the "Balic" section into 7 paragraphs.
    
    Break points:
    - "On the rare"
    - "Andropinis lives"
    - "Balic's templars"
    - "The nobles of"
    - "Balic's Merchant"
    - "Balic's secluded"
    """
    logger.info("Splitting Balic section")
    
    result = _find_content_between(
        html,
        r'<p id="header-1-balic">.*?</p>',
        r'<p id="header-2-draj">'
    )
    
    if not result:
        logger.warning("Could not locate Balic section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content (Balic section has multiple <p> tags already)
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "On the rare",
        "Andropinis lives",
        "Balic's templars",
        "The nobles of",
        "Balic's Merchant",
        "Balic's secluded"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 7:
        logger.warning(f"Expected 7 Balic paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Balic section into {len(paragraphs)} paragraphs")
    return html


def _split_draj_section(html: str) -> str:
    """
    Split the "Draj" section into 9 paragraphs (8 breaks + 1 initial = 9 total).
    
    Break points:
    - "Be that as"
    - "No one seems"
    - "This last claim"
    - "Because Draj"
    - "Nevertheless,"
    - "Captives are"
    - "On a day"
    - "Despite its warlike"
    """
    logger.info("Splitting Draj section")
    
    result = _find_content_between(
        html,
        r'<p id="header-2-draj">.*?</p>',
        r'<p id="header-3-gulg">'
    )
    
    if not result:
        logger.warning("Could not locate Draj section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "Be that as",
        "No one seems",
        "This last claim",
        "Because Draj",
        "Nevertheless,",
        "Captives are",
        "On a day",
        "Despite its warlike"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 9:
        logger.warning(f"Expected 9 Draj paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Draj section into {len(paragraphs)} paragraphs")
    return html


def _split_gulg_section(html: str) -> str:
    """
    Split the "Gulg" section into 8 paragraphs.
    
    Break points:
    - "Lalali-Puy is perhaps"
    - "Gulg is not"
    - "While most of"
    - "Her templars,"
    - "In Gulg,"
    - "Like all property"
    - "The warriors of"
    """
    logger.info("Splitting Gulg section")
    
    result = _find_content_between(
        html,
        r'<p id="header-3-gulg">.*?</p>',
        r'<p id="header-4-nibenay">'
    )
    
    if not result:
        logger.warning("Could not locate Gulg section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "Lalali-Puy is perhaps",
        "Gulg is not",
        "While most of",
        "Her templars,",
        "In Gulg,",
        "Like all property",
        "The warriors of"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 8:
        logger.warning(f"Expected 8 Gulg paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Gulg section into {len(paragraphs)} paragraphs")
    return html


def _split_nibenay_section(html: str) -> str:
    """
    Split the "Nibenay" section into 7 paragraphs.
    
    Break points:
    - "The Shadow King lives"
    - "Nibenay's templars are"
    - "This is completely"
    - "Nibenay sits"
    - "Nibenay's merchant trade"
    - "The core of"
    """
    logger.info("Splitting Nibenay section")
    
    result = _find_content_between(
        html,
        r'<p id="header-4-nibenay">.*?</p>',
        r'<p id="header-5-raam">'
    )
    
    if not result:
        logger.warning("Could not locate Nibenay section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "The Shadow King lives",
        "Nibenay's templars are",
        "This is completely",
        "Nibenay sits",
        "Nibenay's merchant trade",
        "The core of"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 7:
        logger.warning(f"Expected 7 Nibenay paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Nibenay section into {len(paragraphs)} paragraphs")
    return html


def _split_raam_section(html: str) -> str:
    """
    Split the "Raam" section into 6 paragraphs.
    
    Break points:
    - "Abalach-Re professes"
    - "This is one of"
    - "As a consequence"
    - "Of course,"
    - "The only thing"
    """
    logger.info("Splitting Raam section")
    
    result = _find_content_between(
        html,
        r'<p id="header-5-raam">.*?</p>',
        r'<p id="header-6-t-y-r">'
    )
    
    if not result:
        logger.warning("Could not locate Raam section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "Abalach-Re professes",
        "This is one of",
        "As a consequence",
        "Of course,",
        "The only thing"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 6:
        logger.warning(f"Expected 6 Raam paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Raam section into {len(paragraphs)} paragraphs")
    return html


def _split_tyr_section(html: str) -> str:
    """
    Split the "Tyr" section into 8 paragraphs.
    
    Break points:
    - "If Kalak's"
    - "The Tyrant of Tyr"
    - "Of late,"
    - "Kalak has also"
    - "To make matters"
    - "Can it be"
    - "When the final battle"
    """
    logger.info("Splitting Tyr section")
    
    result = _find_content_between(
        html,
        r'<p id="header-6-t-y-r">.*?</p>',
        r'<p id="header-7-urik">'
    )
    
    if not result:
        logger.warning("Could not locate Tyr section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "If Kalak's",
        "The Tyrant of Tyr",
        "Of late,",
        "Kalak has also",
        "To make matters",
        "Can it be",
        "When the final battle"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 8:
        logger.warning(f"Expected 8 Tyr paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Tyr section into {len(paragraphs)} paragraphs")
    return html


def _split_urik_section(html: str) -> str:
    """
    Split the "Urik" section into 9 paragraphs.
    
    The first 3 paragraphs are Hamanu's block quote and should be
    wrapped in a <blockquote> tag with italic styling. There's an intro
    paragraph before the block quote that says "Perhaps King Hamanu...".
    
    Break points:
    - (intro paragraph before blockquote)
    - "I am Hamanu, King" (blockquote start)
    - "The Great Spirits" (blockquote)
    - "I am Hamanu of" (blockquote)
    - "As you"
    - "Hamanu's palace"
    - "One of the most"
    - "Urik's economy"
    - "As a final note"
    """
    logger.info("Splitting Urik section")
    
    result = _find_content_between(
        html,
        r'<p id="header-7-urik">.*?</p>',
        r'<p id="header-8-villages">'
    )
    
    if not result:
        logger.warning("Could not locate Urik section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers - note that the intro paragraph comes before "I am Hamanu, King"
    markers = [
        "I am Hamanu, King",
        "The Great Spirits",
        "I am Hamanu of",
        "As you",
        "Hamanu's palace",
        "One of the most",
        "Urik's economy",
        "As a final note"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 9:
        logger.warning(f"Expected 9 Urik paragraphs, got {len(paragraphs)}")
    
    # The structure is:
    # - Paragraph 0: "Perhaps King Hamanu..." (intro, before blockquote)
    # - Paragraphs 1-3: Block quote ("I am Hamanu, King", "The Great Spirits", "I am Hamanu of")
    # - Paragraphs 4-8: Regular paragraphs
    if len(paragraphs) >= 4:
        intro_para = paragraphs[0]  # "Perhaps King Hamanu..."
        blockquote_paras = paragraphs[1:4]  # The 3 "I am Hamanu" paragraphs
        remaining_paras = paragraphs[4:]  # Everything after
        
        # Wrap intro paragraph
        intro_html = f'<p>{intro_para}</p>\n' if intro_para.strip() else ''
        
        # Wrap block quote paragraphs in <blockquote> with <p><em> tags
        blockquote_html = '<blockquote style="margin: 1em 2em; font-style: italic;">\n'
        for para in blockquote_paras:
            if para.strip():
                blockquote_html += f'<p><em>{para}</em></p>\n'
        blockquote_html += '</blockquote>'
        
        # Wrap remaining paragraphs normally
        remaining_html = _wrap_paragraphs(remaining_paras)
        
        new_content = intro_html + blockquote_html + '\n' + remaining_html
    else:
        # Fallback: just wrap all paragraphs normally if we don't have enough
        new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Urik section into {len(paragraphs)} paragraphs (intro + 3 blockquote + {len(paragraphs)-4} regular)")
    return html


def _convert_cities_to_h2(html: str) -> str:
    """
    Convert city names to h2-header styled format (matching other chapters).
    
    Cities: Balic, Draj, Gulg, Nibenay, Raam, Tyr, Urik
    """
    logger.info("Converting city names to h2-header styled format")
    
    cities = [
        ("header-1-balic", "Balic"),
        ("header-2-draj", "Draj"),
        ("header-3-gulg", "Gulg"),
        ("header-4-nibenay", "Nibenay"),
        ("header-5-raam", "Raam"),
        ("header-6-t-y-r", "T y r"),
        ("header-7-urik", "Urik"),
    ]
    
    for header_id, header_text in cities:
        # Pattern: <p id="header-ID">ROMAN.  <a href...>[^]</a> <span...>City Name</span></p>
        # Replace with: <p id="header-ID" class="h2-header"><a href...>[^]</a> <span style...>City Name</span></p>
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{re.escape(header_text)}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def _remove_duplicate_salt_view_header(html: str) -> str:
    """
    Remove the duplicate styled Salt View header that appears before the H2 version.
    
    The original has: <p id="header-12-salt-view">XIII. ... Salt View</span></p>
    This needs to be removed since we create an H2 version.
    """
    logger.info("Removing duplicate Salt View header")
    
    # Remove the styled <p> header for Salt View
    pattern = r'<p id="header-12-salt-view">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>Salt View</span></p>'
    html = re.sub(pattern, '', html)
    
    logger.info("Removed duplicate Salt View header")
    return html


def _convert_villages_to_h2(html: str) -> str:
    """
    Convert village names to h2-header styled format (matching other chapters).
    
    Villages: Altaruk, Makla, North and South Ledopolus, Salt View, Ogo, Walis
    """
    logger.info("Converting village names to h2-header styled format")
    
    villages = [
        ("header-9-altaruk", "Altaruk"),
        ("header-10-makla", "Makla"),
        ("header-11-north-and-south-ledopolus", "North and South Ledopolus"),
        ("header-12-salt-view", "Salt View"),
        ("header-13-ogo", "Ogo"),
        ("header-14-walis", "Walis"),
    ]
    
    for header_id, header_text in villages:
        # Pattern: <p id="header-ID">ROMAN.  <a href...>[^]</a> <span...>Village Name</span></p>
        # Replace with: <p id="header-ID" class="h2-header"><a href...>[^]</a> <span style...>Village Name</span></p>
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{re.escape(header_text)}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def _fix_malformed_headers(html: str) -> str:
    """
    Fix malformed H2 headers that have extra <p> tags inside them.
    
    Pattern: <h2 id="..."><p>Text...</h2>
    Should be: <h2 id="...">Text...</h2>
    """
    logger.info("Fixing malformed headers")
    
    # Find all malformed headers for debugging
    malformed = re.findall(r'<h2[^>]*><p>', html)
    if malformed:
        logger.warning(f"Found {len(malformed)} malformed H2 headers with <p> tags inside")
        for match in malformed[:3]:
            logger.warning(f"  Example: {match}...")
    
    # Simple approach: just remove "<p>" that immediately follows "<h2 ...>"
    # This handles cases like: <h2 id="header-9-altaruk"><p>Altaruk <a...></h2>
    pattern = r'(<h2[^>]*>)<p>'
    replacement = r'\1'
    old_html = html
    html = re.sub(pattern, replacement, html)
    
    if html != old_html:
        logger.info(f"Fixed malformed headers: removed {old_html.count('<h2') - html.count('<h2')} <p> tags")
    else:
        logger.info("No malformed headers found to fix")
    
    return html


def _split_altaruk_section(html: str) -> str:
    """
    Split the "Altaruk" section into 3 paragraphs.
    
    Break points:
    - "This contingent"
    - "Despite its"
    """
    logger.info("Splitting Altaruk section")
    
    result = _find_content_between(
        html,
        r'<p id=\"header-9-altaruk\"[^>]*>',
        r'<p id=\"header-10-makla\"[^>]*>'
    )
    
    if not result:
        logger.warning("Could not locate Altaruk section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = [
        "This contingent",
        "Despite its"
    ]
    
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 3:
        logger.warning(f"Expected 3 Altaruk paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Altaruk section into {len(paragraphs)} paragraphs")
    return html


def _split_ledopolus_section(html: str) -> str:
    """
    Split the "North and South Ledopolus" section into 2 paragraphs.
    
    Break point:
    - "Occassionally,"
    """
    logger.info("Splitting North and South Ledopolus section")
    
    result = _find_content_between(
        html,
        r'<p id=\"header-11-north-and-south-ledopolus\"[^>]*>',
        r'<p id=\"header-12-salt-view\"[^>]*>'
    )
    
    if not result:
        logger.warning("Could not locate North and South Ledopolus section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["Occassionally,"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Ledopolus paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split North and South Ledopolus section into {len(paragraphs)} paragraphs")
    return html


def _split_ogo_section(html: str) -> str:
    """
    Split the "Ogo" section into 2 paragraphs.
    
    Break point:
    - "Ogo is unique"
    """
    logger.info("Splitting Ogo section")
    
    result = _find_content_between(
        html,
        r'<p id=\"header-13-ogo\"[^>]*>',
        r'<p id=\"header-14-walis\"[^>]*>'
    )
    
    if not result:
        logger.warning("Could not locate Ogo section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["Ogo is unique"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Ogo paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Ogo section into {len(paragraphs)} paragraphs")
    return html


def _split_walis_section(html: str) -> str:
    """
    Split the "Walis" section into 2 paragraphs.
    
    Break point:
    - "The reason for all"
    """
    logger.info("Splitting Walis section")
    
    # Find the next header after Walis - need to check what comes next
    # For now, let's try to find content up to the next header pattern
    result = _find_content_between(
        html,
        r'<p id=\"header-14-walis\"[^>]*>',
        r'<h2 id="header-'  # Next header
    )
    
    if not result:
        # Try alternative: content until end of section or next major header
        result = _find_content_between(
            html,
            r'<p id=\"header-14-walis\"[^>]*>',
            r'<p id="header-'  # Or a styled header
        )
    
    if not result:
        logger.warning("Could not locate Walis section")
        return html
    
    start_idx, end_idx, content = result
    
    # Extract all paragraph content
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["The reason for all"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Walis paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Walis section into {len(paragraphs)} paragraphs")
    return html


def _split_oases_section(html: str) -> str:
    """Split Oases section into 2 paragraphs."""
    logger.info("Splitting Oases section")
    
    # Find the Oases section (starts with header, ends before Bitter Well header)
    pattern = r'(<p id="header-15-oases">.*?</p>)(.*?)(<p id="header-16-bitter-well">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Oases section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["The largest and most reliable"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Oases paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Oases section into {len(paragraphs)} paragraphs")
    return html


def _split_bitter_well_section(html: str) -> str:
    """Split Bitter Well section into 2 paragraphs."""
    logger.info("Splitting Bitter Well section")
    
    # Find the Bitter Well section (starts with <p>, ends before Black Waters header)
    pattern = r'(<p id="header-16-bitter-well"[^>]*>.*?</p>)(.*?)(<p id="header-17-black-waters"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Bitter Well section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["I would advise"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Bitter Well paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Bitter Well section into {len(paragraphs)} paragraphs")
    return html


def _split_lake_pit_section(html: str) -> str:
    """Split Lake Pit section into 2 paragraphs."""
    logger.info("Splitting Lake Pit section")
    
    # Find the Lake Pit section (starts with <p>, ends before Lake of Golden Dreams header)
    pattern = r'(<p id="header-18-lake-pit"[^>]*>.*?</p>)(.*?)(<p id="header-19-lake-of-golden-dreams"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Lake Pit section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["In either case"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Lake Pit paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Lake Pit section into {len(paragraphs)} paragraphs")
    return html


def _split_mud_palace_section(html: str) -> str:
    """Split The Mud Palace section into 2 paragraphs."""
    logger.info("Splitting The Mud Palace section")
    
    # Find the Mud Palace section (starts with <h2>, ends before Islands header)
    pattern = r'(<p id="header-23-the-mud-palace"[^>]*>.*?</p>)(.*?)(<p id="header-24-islands">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find The Mud Palace section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["At the center"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Mud Palace paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Mud Palace section into {len(paragraphs)} paragraphs")
    return html


def _convert_oases_to_h2(html: str) -> str:
    """Convert oases names to h2-header styled format (matching other chapters)."""
    logger.info("Converting oases names to h2-header styled format")
    
    oases = [
        ("header-16-bitter-well", "Bitter Well"),
        ("header-17-black-waters", "Black Waters"),
        ("header-18-lake-pit", "Lake Pit"),
        ("header-19-lake-of-golden-dreams", "Lake of Golden Dreams"),
        ("header-20-silver-spring", "Silver Spring"),
        ("header-21-grak&#x27;s-pool", "Grak&#x27;s Pool"),  # Apostrophe is HTML-encoded
        ("header-22-lost-oasis", "Lost Oasis"),
        ("header-23-the-mud-palace", "The Mud Palace"),
    ]
    
    for header_id, header_text in oases:
        # Pattern to match the styled <p> tag with Roman numeral
        # Need to escape special characters in header_text (but not HTML entities)
        escaped_text = re.escape(header_text).replace(r'\&', '&')  # Allow HTML entities
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{escaped_text}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def _split_islands_section(html: str) -> str:
    """Split Islands section into 2 paragraphs."""
    logger.info("Splitting Islands section")
    
    # Find the Islands section (starts with header, ends before Ledo header)
    pattern = r'(<p id="header-24-islands">.*?</p>)(.*?)(<p id="header-25-l-e-d-o">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Islands section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["I have learned"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Islands paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Islands section into {len(paragraphs)} paragraphs")
    return html


def _split_dragons_palate_section(html: str) -> str:
    """Split Dragon's Palate section into 3 paragraphs."""
    logger.info("Splitting Dragon's Palate section")
    
    # Find the Dragon's Palate section (starts with <p>, ends before Siren's Song header)
    pattern = r'(<p id="header-26-dragon&#x27;s-palate"[^>]*>.*?</p>)(.*?)(<p id="header-27-siren&#x27;s-song"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Dragon's Palate section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = ["The giants", "I should warn"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 3:
        logger.warning(f"Expected 3 Dragon's Palate paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Dragon's Palate section into {len(paragraphs)} paragraphs")
    return html


def _split_sirens_song_section(html: str) -> str:
    """Split Siren's Song section into 2 paragraphs."""
    logger.info("Splitting Siren's Song section")
    
    # Find the Siren's Song section (starts with <p>, ends before Waverly header)
    pattern = r'(<p id="header-27-siren&#x27;s-song"[^>]*>.*?</p>)(.*?)(<p id="header-28-waverly"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Siren's Song section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["Some claim"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Siren's Song paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Siren's Song section into {len(paragraphs)} paragraphs")
    return html


def _split_waverly_section(html: str) -> str:
    """Split Waverly section into 2 paragraphs."""
    logger.info("Splitting Waverly section")
    
    # Find the Waverly section (starts with <p>, ends before Lake Island header)
    pattern = r'(<p id="header-28-waverly"[^>]*>.*?</p>)(.*?)(<p id="header-29-lake-island"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Waverly section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["According to"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Waverly paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Waverly section into {len(paragraphs)} paragraphs")
    return html


def _split_lake_island_section(html: str) -> str:
    """Split Lake Island section into 2 paragraphs."""
    logger.info("Splitting Lake Island section")
    
    # Find the Lake Island section (starts with <h2>, ends before Ruins header)
    pattern = r'(<p id="header-29-lake-island"[^>]*>.*?</p>)(.*?)(<p id="header-30-ruins">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Lake Island section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["In the crater"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Lake Island paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Lake Island section into {len(paragraphs)} paragraphs")
    return html


def _convert_islands_to_h2(html: str) -> str:
    """Convert island names to h2-header styled format (matching other chapters)."""
    logger.info("Converting island names to h2-header styled format")
    
    islands = [
        ("header-25-l-e-d-o", "L e d o"),
        ("header-26-dragon&#x27;s-palate", "Dragon&#x27;s Palate"),  # Apostrophe is HTML-encoded
        ("header-27-siren&#x27;s-song", "Siren&#x27;s Song"),  # Apostrophe is HTML-encoded
        ("header-28-waverly", "Waverly"),
        ("header-29-lake-island", "Lake Island"),
    ]
    
    for header_id, header_text in islands:
        # Pattern to match the styled <p> tag with Roman numeral
        # Need to escape special characters in header_text (but not HTML entities)
        escaped_text = re.escape(header_text).replace(r'\&', '&')  # Allow HTML entities
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{escaped_text}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def _split_arkhold_section(html: str) -> str:
    """Split Arkhold section into 2 paragraphs."""
    logger.info("Splitting Arkhold section")
    
    # Find the Arkhold section (starts with <p>, ends before Kalidnay header)
    pattern = r'(<p id="header-32-arkhold"[^>]*>.*?</p>)(.*?)(<p id="header-33-kalidnay"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Arkhold section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["As for the castle"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Arkhold paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Arkhold section into {len(paragraphs)} paragraphs")
    return html


def _split_bodach_section(html: str) -> str:
    """Split Bodach section into 3 paragraphs."""
    logger.info("Splitting Bodach section")
    
    # Find the Bodach section (starts with <p>, ends before Giustenal header)
    pattern = r'(<p id="header-34-bodach"[^>]*>.*?</p>)(.*?)(<p id="header-35-giustenal"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Bodach section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = ["Unfortunately", "I have talked"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 3:
        logger.warning(f"Expected 3 Bodach paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Bodach section into {len(paragraphs)} paragraphs")
    return html


def _split_giustenal_section(html: str) -> str:
    """Split Giustenal section into 3 paragraphs."""
    logger.info("Splitting Giustenal section")
    
    # Find the Giustenal section (starts with <p>, ends before Yaramuke header)
    pattern = r'(<p id="header-35-giustenal"[^>]*>.*?</p>)(.*?)(<p id="header-36-yaramuke"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Giustenal section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at markers
    markers = ["Giustenal appears", "I have never"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 3:
        logger.warning(f"Expected 3 Giustenal paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Giustenal section into {len(paragraphs)} paragraphs")
    return html


def _convert_ruins_to_h2(html: str) -> str:
    """Convert ruins names to h2-header styled format (matching other chapters)."""
    logger.info("Converting ruins names to h2-header styled format")
    
    ruins = [
        ("header-31-bleak-tower", "Bleak Tower"),
        ("header-32-arkhold", "Arkhold"),
        ("header-33-kalidnay", "Kalidnay"),
        ("header-34-bodach", "Bodach"),
        ("header-35-giustenal", "Giustenal"),
        ("header-36-yaramuke", "Yaramuke"),
    ]
    
    for header_id, header_text in ruins:
        # Pattern to match the styled <p> tag with Roman numeral
        escaped_text = re.escape(header_text)
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{escaped_text}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def _split_dragons_bowl_section(html: str) -> str:
    """Split Dragon's Bowl section into 2 paragraphs."""
    logger.info("Splitting Dragon's Bowl section")
    
    # Find the Dragon's Bowl section (starts with <p>, ends before Mekillot Mountains header)
    pattern = r'(<p id="header-38-dragon&#x27;s-bowl"[^>]*>.*?</p>)(.*?)(<p id="header-39-mekillot-mountains"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Dragon's Bowl section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["Perhaps this"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Dragon's Bowl paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Dragon's Bowl section into {len(paragraphs)} paragraphs")
    return html


def _split_mekillot_mountains_section(html: str) -> str:
    """Split Mekillot Mountains section into 2 paragraphs."""
    logger.info("Splitting Mekillot Mountains section")
    
    # Find the Mekillot Mountains section (starts with <p>, ends before Estuary header)
    pattern = r'(<p id="header-39-mekillot-mountains"[^>]*>.*?</p>)(.*?)(<p id="header-40-estuary-of-the-forked-tongue"[^>]*>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Mekillot Mountains section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_section = match.group(3)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["It is well"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Mekillot Mountains paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Mekillot Mountains section into {len(paragraphs)} paragraphs")
    return html


def _split_dragons_crown_mountain_section(html: str) -> str:
    """Split Dragon's Crown Mountain section into 2 paragraphs."""
    logger.info("Splitting Dragon's Crown Mountain section")
    
    # Find the Dragon's Crown Mountain section (starts with <h2>, ends at end of content or next major header)
    # This is the last section in the chapter, so we need to be careful with the ending pattern
    pattern = r'(<p id="header-41-dragon&#x27;s-crown-mountain"[^>]*>.*?</p>)(.*?)(?=</body>|$)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        logger.warning("Could not find Dragon's Crown Mountain section to split")
        return html
    
    header = match.group(1)
    content = match.group(2)
    start_idx = match.start(2)
    end_idx = match.end(2)
    
    # Extract text from all <p> tags
    para_content = re.sub(r'</?p>', '', content).strip()
    
    # Split at marker
    markers = ["If you make"]
    paragraphs = _split_paragraph_at_markers(para_content, markers)
    
    if len(paragraphs) != 2:
        logger.warning(f"Expected 2 Dragon's Crown Mountain paragraphs, got {len(paragraphs)}")
    
    # Wrap in <p> tags
    new_content = _wrap_paragraphs(paragraphs)
    
    # Replace in original HTML
    html = html[:start_idx] + new_content + html[end_idx:]
    
    logger.info(f"Split Dragon's Crown Mountain section into {len(paragraphs)} paragraphs")
    return html


def _convert_landmarks_to_h2(html: str) -> str:
    """Convert landmark names to h2-header styled format (matching other chapters)."""
    logger.info("Converting landmark names to h2-header styled format")
    
    landmarks = [
        ("header-38-dragon&#x27;s-bowl", "Dragon&#x27;s Bowl"),  # Apostrophe is HTML-encoded
        ("header-39-mekillot-mountains", "Mekillot Mountains"),
        ("header-40-estuary-of-the-forked-tongue", "Estuary of the Forked Tongue"),
        ("header-41-dragon&#x27;s-crown-mountain", "Dragon&#x27;s Crown Mountain"),  # Apostrophe is HTML-encoded
    ]
    
    for header_id, header_text in landmarks:
        # Pattern to match the styled <p> tag with Roman numeral
        # Need to escape special characters in header_text (but not HTML entities)
        escaped_text = re.escape(header_text).replace(r'\&', '&')  # Allow HTML entities
        pattern = rf'<p id="{header_id}">[IVXLCDM]+\.\s+<a href="#top"[^>]*>\[\^\]</a>\s+<span[^>]*>{escaped_text}</span></p>'
        replacement = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">{header_text}</span></p>'
        
        old_html = html
        html = re.sub(pattern, replacement, html)
        
        if html != old_html:
            logger.info(f"Converted '{header_text}' to h2-header format")
        else:
            logger.warning(f"Could not find pattern for '{header_text}'")
    
    return html


def postprocess_chapter_four_atlas(html: str) -> str:
    """
    Apply all paragraph break fixes for Chapter Four: Atlas of the Tyr Region.
    
    Args:
        html: The HTML content to process
        
    Returns:
        Processed HTML with proper paragraph breaks and H2 headers
    """
    logger.info("Postprocessing Chapter Four: Atlas of the Tyr Region")
    
    # Split paragraphs first (before converting to H2, since split functions expect <p> tags)
    html = _split_main_intro(html)
    html = _split_cities_section(html)
    html = _split_balic_section(html)
    html = _split_draj_section(html)
    html = _split_gulg_section(html)
    html = _split_nibenay_section(html)
    html = _split_raam_section(html)
    html = _split_tyr_section(html)
    html = _split_urik_section(html)
    html = _split_oases_section(html)  # Oases intro section
    html = _split_islands_section(html)  # Islands intro section
    
    # Convert cities, villages, oases, islands, ruins, and landmarks to H2 headers
    html = _convert_cities_to_h2(html)
    html = _convert_villages_to_h2(html)  # Convert all village headers
    html = _convert_oases_to_h2(html)  # Convert all oases headers
    html = _convert_islands_to_h2(html)  # Convert all island headers
    html = _convert_ruins_to_h2(html)  # Convert all ruins headers
    html = _convert_landmarks_to_h2(html)  # Convert all landmarks headers
    html = _fix_malformed_headers(html)  # Clean up any malformed H2 tags
    html = _remove_duplicate_salt_view_header(html)  # Remove duplicate Salt View styled header
    
    # Split village paragraphs (after converting to H2, since these functions expect <h2> tags)
    html = _split_altaruk_section(html)
    html = _split_ledopolus_section(html)
    html = _split_ogo_section(html)
    html = _split_walis_section(html)
    
    # Split oases paragraphs (after converting to H2, since these functions expect <h2> tags)
    html = _split_bitter_well_section(html)
    html = _split_lake_pit_section(html)
    html = _split_mud_palace_section(html)
    
    # Split islands paragraphs (after converting to H2, since these functions expect <h2> tags)
    html = _split_dragons_palate_section(html)
    html = _split_sirens_song_section(html)
    html = _split_waverly_section(html)
    html = _split_lake_island_section(html)
    
    # Split ruins paragraphs (after converting to H2, since these functions expect <h2> tags)
    html = _split_arkhold_section(html)
    html = _split_bodach_section(html)
    html = _split_giustenal_section(html)
    
    # Split landmarks paragraphs (after converting to H2, since these functions expect <h2> tags)
    html = _split_dragons_bowl_section(html)
    html = _split_mekillot_mountains_section(html)
    html = _split_dragons_crown_mountain_section(html)
    
    # Final cleanup pass to catch any remaining malformed headers
    html = _fix_malformed_headers(html)
    
    logger.info("Chapter Four: Atlas postprocessing complete")
    return html

