"""Chapter 2 HTML post-processing fixes.

This module contains detailed HTML-level fixes for Chapter 2 (Player Character Races).
These fixes handle complex table positioning, paragraph fragmentation, and text reordering
that result from PDF extraction artifacts.

Migrated from archived postprocess.py to the new pipeline framework.
"""

from __future__ import annotations

import re
from typing import Dict, Callable
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic


def _apply_subheader_styling(html: str) -> str:
    """Apply subheader styling to specific headers.
    
    Makes the following headers appear as subheaders (smaller font):
    - Racial Ability Requirements
    - Table 2: Ability Adjustments  
    - Table 3: Racial Class And Level Limits
    - Starting Age
    - Aging Effects
    - All "Roleplaying:" headers
    """
    import re
    
    # Pattern for headers that should be subheaders
    # Replace the span with a smaller font size
    subheader_patterns = [
        r'(<p[^>]*id="header-1-racial-ability-requirements"><span style="color: #ca5804">Racial Ability Requirements</span></p>)',
        r'(<p[^>]*id="header-3-table-2-ability-adjustments"><span style="color: #ca5804">Table 2: Ability Adjustments</span></p>)',
        r'(<p[^>]*id="header-6-table-3-racial-class-and-level-limits"><span style="color: #ca5804">Table 3: Racial Class And Level Limits</span></p>)',
        r'(<p[^>]*id="header-\d+-starting-age"><span style="color: #ca5804">Starting Age</span></p>)',
        r'(<p[^>]*id="header-\d+-aging-effects"><span style="color: #ca5804">Aging Effects</span></p>)',
        r'(<p[^>]*id="header-\d+-roleplaying-"><span style="color: #ca5804">Roleplaying: </span></p>)',
    ]
    
    for pattern in subheader_patterns:
        # Find all matches and replace with smaller font and CSS class
        html = re.sub(
            pattern,
            lambda m: m.group(1).replace('style="color: #ca5804"', 'class="header-h2" style="color: #ca5804; font-size: 0.9em"'),
            html
        )
    
    return html


def _fix_half_elves_roleplaying_paragraphs(html: str) -> str:
    """Fix paragraph structure in Half-elves Roleplaying section.
    
    The section should have exactly 3 paragraphs:
    1. Self-reliance introduction
    2. Example of half-elf behavior (starts with "For example")
    3. Acceptance seeking behavior (starts with "Despite their self-reliance")
    """
    # Find the Roleplaying section for Half-elves
    pattern = r'(<p id="header-13-roleplaying-">.*?</p>)(.*?)(<p id="header-14-half-giants">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Extract all paragraph text from the content, ignoring section tags
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text and split into 3 proper paragraphs
    full_text = ' '.join(paragraphs_text)
    
    # Find the split points
    # Paragraph 1 ends before "For example"
    para1_end = full_text.find('For example')
    # Paragraph 2 ends before "Despite their self-reliance"
    para2_end = full_text.find('Despite their self-reliance')
    
    if para1_end == -1 or para2_end == -1:
        # Can't find the markers, return unchanged
        return html
    
    para1 = full_text[:para1_end].strip()
    para2 = full_text[para1_end:para2_end].strip()
    para3 = full_text[para2_end:].strip()
    
    # Reconstruct with 3 clean paragraphs
    new_content = f'\n<p>{para1}</p>\n<p>{para2}</p>\n<p>{para3}</p>\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_half_giants_main_section(html: str) -> str:
    """Fix paragraph structure in Half-Giants main section.
    
    The section should have exactly 10 paragraphs before the Roleplaying subsection.
    """
    # Find the Half-Giants section (before Roleplaying)
    pattern = r'(<p id="header-14-half-giants">.*?</p>)(.*?)(<p id="header-15-roleplaying-">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    roleplaying_header = match.group(3)
    
    # Extract all text from paragraphs
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 10 paragraph split points based on content
    splits = [
        "A half-giant is an enormous individual",  # Para 2
        "A half-giant character can be a cleric",  # Para 3
        "Simply put, a half-giant gains terrific size",  # Para 4
        "Though no one knows for certain",  # Para 5
        "Half-giants sometimes collect into communities",  # Para 6
        "Half-giants can switch their attitudes",  # Para 7
        "Half-giant characters add four",  # Para 8 (attribute modifiers)
        "Half-giants double their hit die rolls",  # Para 9 (hit die)
        "All personal items such as clothes",  # Para 10 (costs paragraph)
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with proper paragraph count (should be 10)
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + roleplaying_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_half_giants_roleplaying_paragraphs(html: str) -> str:
    """Fix paragraph structure in Half-Giants Roleplaying section.
    
    The section should have exactly 4 paragraphs.
    """
    # Find the Roleplaying section for Half-Giants
    pattern = r'(<p id="header-15-roleplaying-">.*?</p>)(.*?)(<p id="header-16-halflings">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 4 paragraph split points
    splits = [
        "For example, a half-giant character",  # Para 2 (example)
        "This is not to say, however",  # Para 3
        "Remember, though, that due to size alone",  # Para 4
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 4 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_halflings_main_section(html: str) -> str:
    """Fix paragraph structure in Halflings main section.
    
    The section should have exactly 9 paragraphs before the Roleplaying subsection.
    """
    # Find the Halflings section (before Roleplaying)
    pattern = r'(<p id="header-16-halflings">.*?</p>)(.*?)(<p id="header-17-roleplaying-">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    roleplaying_header = match.group(3)
    
    # Extract all text from paragraphs
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 9 paragraph split points based on content
    splits = [
        "Halflings possess a great deal of racial unity",  # Para 2
        "Halfling culture is fabulously diverse",  # Para 3
        "Oddly, the richness of the land",  # Para 4
        "Halfling characters have the same high resistance",  # Para 5
        "Due to their small size",  # Para 6
        "Also, their introverted nature",  # Para 7
        "However, halflings are possessed of tremendous speed",  # Para 8
        "Finally, their pious unity",  # Para 9
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with proper paragraph count (should be 9)
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + roleplaying_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_halflings_roleplaying_paragraphs(html: str) -> str:
    """Fix paragraph structure in Halflings Roleplaying section.
    
    The section should have exactly 5 paragraphs.
    """
    # Find the Roleplaying section for Halflings
    pattern = r'(<p id="header-17-roleplaying-">.*?</p>)(.*?)(<p id="header-18-human">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 5 paragraph split points
    splits = [
        "This is not to say that a halfling character will adopt these customs",  # Para 2
        "The accomplishments that are normally held",  # Para 3
        "Also, whereas many other races",  # Para 4
        "When among others of his kind",  # Para 5
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 5 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_human_section(html: str) -> str:
    """Fix paragraph structure in Human section.
    
    The section should have exactly 5 paragraphs.
    """
    # Find the Human section - search for actual paragraph markers, not just headers
    # Use a more specific pattern that only matches the content section
    pattern = r'(<p id="header-18-human"><span[^>]*>Human</span></p>)(.*?)(<p id="header-19-mul"><span[^>]*>Mul</span></p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        # If not found, return unchanged
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Safety check: ensure we actually have content
    if not content or len(content.strip()) < 100:
        return html
    
    # Extract all text from paragraphs
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 5 paragraph split points based on content
    # Note: text may be merged without spaces (e.g., "AsinotherAD" instead of "As in other AD")
    splits = [
        "An average human male stands between 6",  # Para 2 (physical description)
        "On Athas, centuries of abusive magic",  # Para 3 (appearance alterations)
        "The children of humans",  # Para 4 (half-races)
        "campaign worlds, humans are generally tolerant",  # Para 5 (tolerance) - use unique middle text
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with proper paragraph count (should be 5)
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_mul_main_section(html: str) -> str:
    """Fix paragraph structure in Mul main section.
    
    The section should have exactly 8 paragraphs before the Roleplaying subsection.
    """
    # Find the Mul section - use specific pattern that matches the full closing tag
    # to avoid matching "Roleplaying:" in the table of contents
    pattern = r'(<p id="header-19-mul"><span[^>]*>Mul</span></p>)(.*?)(<p id="header-22-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    roleplaying_header = match.group(3)
    
    # Safety check: ensure we actually have content
    if not content or len(content.strip()) < 100:
        return html
    
    # Extract all text from paragraphs (skip table headers but extract text after table data)
    paragraphs_text = []
    for p_match in re.finditer(r'<p[^>]*>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        # Check if this is a table header paragraph
        if 'id="header-20' in p_match.group(0) or 'id="header-21' in p_match.group(0):
            continue
        # If paragraph starts with table data, extract the text after it
        if text.startswith('Heavy Labor'):
            # Find where the actual content starts (after "Normal Activity...")
            match = re.search(r'Normal Activity \([^)]+\)\s+(.+)', text, re.DOTALL)
            if match:
                paragraphs_text.append(match.group(1))
        elif text and not text.startswith('24 + Con hours'):
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 8 paragraph split points based on content
    splits = [
        "A full-grown mul stands",  # Para 2 (physical description)
        "Born as they are to lives of",  # Para 3 (personality)
        "Many slave muls have either",  # Para 4 (freedom/careers)
        "A player character mul may become",  # Para 5 (available classes)
        "A mul character adds two to",  # Para 6 (attribute modifiers)
        "Mules are able to",  # Para 7 (exertion intro)
        "Regardless of the preceding type",  # Para 8 (exertion details)
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with proper paragraph count (should be 8)
    # Note: We'll need to preserve the table headers that appear in this section
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Re-insert table headers (they appear between paragraphs 7 and 8)
    # We'll add them after reconstruction
    table_headers = (
        '<p id="header-20-mul-exertion-table"><span style="color: #ca5804">Mul Exertion Table</span></p>\n'
        '<p id="header-21-type-of-exertion"><span style="color: #ca5804">Type of Exertion</span></p>\n'
    )
    
    # Insert table headers before the exertion paragraph (last paragraph)
    paragraphs_html = [f'<p>{p}</p>' for p in paragraphs if p]
    if len(paragraphs_html) >= 8:
        # Insert table headers before the last paragraph
        final_content = '\n' + '\n'.join(paragraphs_html[:7]) + '\n' + table_headers + paragraphs_html[7] + '\n'
    else:
        final_content = new_content
    
    # Replace in HTML
    replacement = header + final_content + roleplaying_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_mul_roleplaying_paragraphs(html: str) -> str:
    """Fix paragraph structure in Mul Roleplaying section.
    
    The section should have exactly 2 paragraphs.
    """
    # Find the Mul Roleplaying section - use specific pattern
    pattern = r'(<p id="header-22-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)(.*?)(<p id="header-23-thri-kreen"><span[^>]*>Thri-kreen</span></p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Safety check: ensure we actually have content
    if not content or len(content.strip()) < 50:
        return html
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Define 2 paragraph split point (user-specified)
    splits = [
        "Like their dwarven parent,",  # Para 2
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 2 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_mul_main_section_v2(html: str) -> str:
    """Fix paragraph structure in Mul main section (v2 - safe from TOC corruption).
    
    The section should have exactly 8 paragraphs.
    Uses specific pattern matching to avoid TOC corruption.
    """
    # The Mul section has content before AND after the table
    # Pattern: Mul header -> content -> table header+table -> more content -> Roleplaying header
    pattern = r'(<p id="header-19-mul"><span[^>]*>Mul</span></p>)(.*?)(<p id="header-20-mul-exertion-table">.*?</table>)(.*?)(<p id="header-21-roleplaying-")'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content_before_table = match.group(2)
    table_section = match.group(3)  # includes table header and table
    content_after_table = match.group(4)
    roleplaying_header = match.group(5)
    
    # Combine content before and after table
    combined_content = content_before_table + content_after_table
    
    # Safety check: if content is too long (>15000 chars), something is wrong
    # This indicates we might be matching TOC content
    if len(combined_content) > 15000:
        return html  # Don't process to avoid corruption
    
    # Extract all paragraph text, excluding table-related headers
    paragraphs_text = []
    for p_match in re.finditer(r'<p[^>]*>(.*?)</p>', combined_content, re.DOTALL):
        text = p_match.group(1).strip()
        # Skip table headers
        if 'id="header-20' in text or 'id="header-21' in text:
            continue
        if text and not text.startswith('<span'):
            paragraphs_text.append(text)
        elif '<span' in text:
            # Extract text from span
            span_text = re.sub(r'<[^>]+>', '', text)
            if span_text.strip():
                paragraphs_text.append(span_text.strip())
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Safety check: ensure we have the expected content
    if "A mul (pronounced:" not in full_text or len(full_text) < 1000:
        return html  # Don't process incomplete content
    
    # Define 8 paragraph split points based on user-specified breaks
    splits = [
        "A full-grown mul stands",  # Para 2
        "Born as they are to lives of",  # Para 3
        "Many slave muls have either",  # Para 4
        "A player character mul may become",  # Para 5
        "A mul character adds two to",  # Para 6
        "Mules are able to work longer",  # Para 7
        "Regardless of the preceding type",  # Para 8
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 8 paragraphs, placing table after paragraph 6
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML - insert table after the content
    replacement = header + new_content + table_section + '\n' + roleplaying_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_mul_roleplaying_paragraphs_v2(html: str) -> str:
    """Fix paragraph structure in Mul Roleplaying section (v2 - safe from TOC corruption).
    
    The section should have exactly 2 paragraphs.
    Uses specific pattern matching to avoid TOC corruption.
    """
    # Use very specific pattern that matches full header structure
    pattern = r'(<p id="header-21-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)(.*?)(<p id="header-22-thri-kreen"><span[^>]*>Thri-kreen</span></p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Safety check: if content is too long (>5000 chars), something is wrong
    if len(content) > 5000:
        return html  # Don't process to avoid corruption
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Safety check: ensure we have the expected content
    if "Muls are slaves" not in full_text or len(full_text) < 200:
        return html  # Don't process incomplete content
    
    # Define 2 paragraph split point
    split_text = "Like their dwarven parent"
    split_pos = full_text.find(split_text)
    
    if split_pos > 0:
        para1 = full_text[:split_pos].strip()
        para2 = full_text[split_pos:].strip()
        paragraphs = [para1, para2]
    else:
        # If split not found, keep as is
        paragraphs = [full_text]
    
    # Reconstruct with 2 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def apply_chapter_2_fixes(html: str) -> str:
    """Apply all Chapter 2 HTML post-processing fixes.
    
    Args:
        html: The HTML content to post-process
        
    Returns:
        Post-processed HTML with all fixes applied
    """
    # Apply fixes in order
    html = _fix_table_3_position(html)
    html = _fix_other_languages_incomplete_sentence(html)
    html = _fix_other_languages_table_intro(html)
    # Subheader styling now done in transformation stage (journal.py)
    # before TOC generation so the TOC can detect subheaders
    # html = _apply_subheader_styling(html)
    html = _fix_half_elves_roleplaying_paragraphs(html)
    html = _fix_half_giants_main_section(html)
    html = _fix_half_giants_roleplaying_paragraphs(html)
    html = _fix_halflings_main_section(html)
    html = _fix_halflings_roleplaying_paragraphs(html)
    html = _fix_human_section(html)
    # Disable _fix_chapter_two_races as it's causing corruption in Mul sections
    # html = _fix_chapter_two_races(html)
    html = _fix_mul_main_section_v2(html)
    html = _fix_mul_roleplaying_paragraphs_v2(html)
    html = _fix_thri_kreen_main_section(html)
    html = _fix_thri_kreen_roleplaying_paragraphs(html)
    html = _fix_height_weight_table(html)
    html = _fix_age_table(html)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html = convert_all_styled_headers_to_semantic(html)
    html = _fix_aging_effects_table(html)
    return html


def _fix_other_languages_incomplete_sentence(html: str) -> str:
    """Complete the incomplete sentence in Other Languages section.
    
    The sentence 'Other languages, including common or other racial languages, must be assigned'
    is missing 'proficiency slots.' due to column-break extraction issues.
    """
    # Pattern: incomplete sentence followed by the language table
    pattern = r'(<p>All other languages.*?must be assigned)(</p>\s*<table class="ds-table">)'
    replacement = r'\1 proficiency slots.\2'
    
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    return html


def _fix_other_languages_table_intro(html: str) -> str:
    """Move the table introduction paragraph to the correct location.
    
    The paragraph "The following is a list of possible languages..." should appear
    BEFORE the language table in the Other Languages section, not after it.
    """
    # Simple approach: Find the "The following is a list" paragraph and the language table,
    # then swap their positions
    
    # Pattern: match the table followed by the intro paragraph
    pattern = r'(<table class="ds-table"><tr><td>Aarakocra\*</td>.*?</table>)\s*(<p>The following is a list of possible languages.*?</p>)'
    
    # Check if the pattern exists
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return html
    
    table_html = match.group(1)
    intro_para = match.group(2)
    
    # Swap them: intro paragraph first, then table
    replacement = intro_para + '\n' + table_html
    html = re.sub(pattern, replacement, html, flags=re.DOTALL)
    
    return html


def _fix_table_3_position(html: str) -> str:
    """Reorder sections for better readability: Class Restrictions → Table 3 → Languages."""
    
    # Step 1: Extract the Class Restrictions paragraph (ends with "DARK SUN campaign.")
    class_restrictions_para_pattern = r'(<p>Just as in the traditional AD&amp;D ® game.*?DARK SUN campaign\.</p>)'
    class_restrictions_match = re.search(class_restrictions_para_pattern, html, re.DOTALL)
    
    if not class_restrictions_match:
        return html
    
    class_restrictions_para = class_restrictions_match.group(1)
    
    # Step 2: Extract Table 3 header
    table3_header_pattern = r'(<p[^>]*id="header-6[^"]*"><span[^>]*>Table 3: Racial Class And Level Limits</span></p>)'
    table3_header_match = re.search(table3_header_pattern, html)
    
    if not table3_header_match:
        return html
    
    table3_header = table3_header_match.group(1)
    
    # Step 3: Extract Table 3 table
    table_pattern = r'(<table[^>]*><tr><th>Class</th><th>Human</th>.*?</table>)'
    table_match = re.search(table_pattern, html, re.DOTALL)
    
    if not table_match:
        return html
    
    table_html = table_match.group(1)
    
    # Step 4: Define clean legend lines (extraction gives malformed legends, so we create clean ones)
    legends_html = (
        '<p><strong>U:</strong> The character has unlimited advancement potential in the given class.</p>'
        '<p><strong>Any #:</strong> A player character can advance to the maximum possible level in a given class. The Player\'s Handbook gives rules for advancing the player characters to 20th level.</p>'
        '<p><strong>-:</strong> A player character cannot belong to the listed class.</p>'
    )
    
    # Remove any malformed legend text (merged or truncated versions from PDF extraction)
    html = re.sub(r'<p>book gives rules for advancing[^<]*?</p>', '', html, flags=re.DOTALL)
    html = re.sub(r'<p>Any #: A player character can advance[^<]*?</p>', '', html, flags=re.DOTALL)
    
    # Step 5: Extract Languages header
    languages_header_pattern = r'(<p[^>]*id="header-5[^"]*"><span[^>]*>Languages</span></p>)'
    languages_header_match = re.search(languages_header_pattern, html)
    
    if not languages_header_match:
        return html
    
    languages_header = languages_header_match.group(1)
    
    # Step 6: Extract both parts of the Languages intro paragraph
    # Part 1: "Athas is a world...lan-"
    languages_part1_pattern = r'(<p>Athas is a world where the intelligent races.*?lan-</p>)'
    languages_part1_match = re.search(languages_part1_pattern, html, re.DOTALL)
    
    # Part 2: "guage and communication..."
    languages_part2_pattern = r'(<p>guage and communication\..*?AD&amp;D game\.</p>)'
    languages_part2_match = re.search(languages_part2_pattern, html, re.DOTALL)
    
    if not languages_part1_match or not languages_part2_match:
        return html
    
    # Merge the two parts into a complete paragraph
    languages_complete_para = '<p>Athas is a world where the intelligent races come from a wide variety of species -- the humans and demihumans are very different than the insectmen and beastmen. Each intelligent race has its own language, sometimes even its own approach to language and communication. For instance, the thrikreen language is a combination of clicks and whines that come very natural to their pincered mouths-humans find it very difficult to reproduce these sounds, but the task is not impossible. DARK SUN adventures are not quite as language friendly as other AD&amp;D® campaign worlds-characters will tend to rely more heavily upon magic or interpreters for communication. As a reminder, the DARK SUN campaign assumes that players and DMs are making use of the optional proficiency system detailed in the AD&amp;D game.</p>'
    
    # Step 7: Remove all the pieces from their current positions
    html = html.replace(languages_part1_match.group(1), '', 1)
    html = html.replace(languages_part2_match.group(1), '', 1)
    html = html.replace(table3_header, '', 1)
    html = html.replace(table_html, '', 1)
    html = html.replace(legends_html, '', 1)
    html = html.replace(languages_header, '', 1)
    
    # Step 8: Reconstruct in the desired order after Class Restrictions paragraph
    new_order = (
        class_restrictions_para +
        table3_header +
        table_html +
        legends_html +
        languages_header +
        languages_complete_para
    )
        
    # Replace the Class Restrictions paragraph with the full reconstructed section
    html = html.replace(class_restrictions_para, new_order, 1)
    
    return html


def _fix_chapter_two_races(html: str) -> str:
    """Fix paragraph issues in the Player Character Races section."""
    
    # Fix: Dwarves section - split into 4 paragraphs
    dwarves_pattern = r'<p[^>]*><span[^>]*>Dwarves</span></p>\s*<p>(.*?)</p>\s*<p>(.*?)</p>'
    dwarves_match = re.search(dwarves_pattern, html, re.DOTALL)
    
    if dwarves_match:
        para1_text = dwarves_match.group(1)
        para2_text = dwarves_match.group(2)
        
        # Split para 2 into paras 2, 3, and 4
        if "An Athasian dwarf takes notice" in para2_text:
            idx2_3 = para2_text.index("An Athasian dwarf takes notice")
            para2_part1 = para2_text[:idx2_3].strip()
            rest = para2_text[idx2_3:]
            
            if "If, however, the other being" in rest:
                idx3_4 = rest.index("If, however, the other being")
                para3_part = rest[:idx3_4].strip()
                para4_part = rest[idx3_4:].strip()
                
                # Reconstruct with 4 paragraphs
                new_dwarves = f'<p><span style="color: #ca5804">Dwarves</span></p>'
                new_dwarves += f'<p>{para1_text}</p>'
                new_dwarves += f'<p>{para2_part1}</p>'
                new_dwarves += f'<p>{para3_part}</p>'
                new_dwarves += f'<p>{para4_part}</p>'
                
                html = html[:dwarves_match.start()] + new_dwarves + html[dwarves_match.end():]
    
    return html


def _fix_thri_kreen_main_section(html: str) -> str:
    """Fix paragraph structure in Thri-kreen main section.
    
    The section should have exactly 15 paragraphs.
    Uses specific pattern matching to avoid TOC corruption.
    """
    # Find the Thri-kreen section (from header to Roleplaying)
    pattern = r'(<p id="header-22-thri-kreen"><span[^>]*>Thri-kreen</span></p>)(.*?)(<p id="header-23-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        # Try alternative header ID
        pattern = r'(<p id="header-23-thri-kreen"><span[^>]*>Thri-kreen</span></p>)(.*?)(<p id="header-\d+-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)'
        match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    roleplaying_header = match.group(3)
    
    # Safety check: if content is too long (>30000 chars), something is wrong
    if len(content) > 30000:
        return html  # Don't process to avoid corruption
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p[^>]*>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        # Skip headers
        if 'id="header-' in p_match.group(0):
            continue
        if text and not text.startswith('<span'):
            paragraphs_text.append(text)
        elif '<span' in text:
            # Extract text from span
            span_text = re.sub(r'<[^>]+>', '', text)
            if span_text.strip():
                paragraphs_text.append(span_text.strip())
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Safety check: ensure we have the expected content
    if "Hulking insect-men" not in full_text or len(full_text) < 2000:
        return html  # Don't process incomplete content
    
    # Define 15 paragraph split points based on user-specified breaks
    # Note: HTML entities like &#x27; (apostrophe) need to be handled
    splits = [
        "The individual thri-kreen is a six-limbed creature",  # Para 2
        "A thri-kreen&#x27;s head has two large eyes",  # Para 3 (with HTML entity)
        "Thri-kreen have no need of sleep",  # Para 4
        "Thri-kreen make and use a variety of weapons",  # Para 5
        "Thri-kreen can use most magical items such as",  # Para 6
        "The pack is the single unit of organization among",  # Para 7
        "Thri-kreen are carnivores and the pack is con",  # Para 8
        "Thri-kreen player characters can become clerics",  # Para 9
        "A thri-kreen has formidable natural attacks",  # Para 10
        "A thri-kreen can leap up and forward when he",  # Para 11
        "A thri-kreen can use a venomous saliva against",  # Para 12
        "A thri-kreen masters the use of the chatkcha",  # Para 13
        "A thri-kreen can dodge missiles fired at it on a roll",  # Para 14
        "Thri-kreen add one to their initial Wisdom score",  # Para 15
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 15 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + roleplaying_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_thri_kreen_roleplaying_paragraphs(html: str) -> str:
    """Fix paragraph structure in Thri-kreen Roleplaying section.
    
    The section should have exactly 4 paragraphs.
    Uses specific pattern matching to avoid TOC corruption.
    """
    # Find the Thri-kreen Roleplaying section
    # Pattern needs to match up to the next major section (Other Characteristics)
    pattern = r'(<p id="header-23-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)(.*?)(<p id="header-24-other-characteristics">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        # Try alternative header IDs
        pattern = r'(<p id="header-\d+-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)(.*?)(<p id="header-\d+-other-characteristics">)'
        match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    content = match.group(2)
    next_header = match.group(3)
    
    # Safety check: if content is too long (>10000 chars), something is wrong
    if len(content) > 10000:
        return html  # Don't process to avoid corruption
    
    # Extract all paragraph text
    paragraphs_text = []
    for p_match in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
        text = p_match.group(1).strip()
        if text:
            paragraphs_text.append(text)
    
    # Join all text
    full_text = ' '.join(paragraphs_text)
    
    # Safety check: ensure we have the expected content
    if "obsession is the hunt" not in full_text or len(full_text) < 500:
        return html  # Don't process incomplete content
    
    # Define 4 paragraph split points
    splits = [
        "From birth, all thri-kreen are involved in the",  # Para 2
        "To outsiders, thri-kreen sometimes seem overly",  # Para 3
        "Their pack intelligence also makes them protect",  # Para 4
    ]
    
    paragraphs = []
    start_pos = 0
    
    for split_text in splits:
        split_pos = full_text.find(split_text, start_pos)
        if split_pos > start_pos:
            paragraphs.append(full_text[start_pos:split_pos].strip())
            start_pos = split_pos
    
    # Add the last paragraph
    if start_pos < len(full_text):
        paragraphs.append(full_text[start_pos:].strip())
    
    # Reconstruct with 4 paragraphs
    new_content = '\n' + '\n'.join(f'<p>{p}</p>' for p in paragraphs if p) + '\n'
    
    # Replace in HTML
    replacement = header + new_content + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_height_weight_table(html: str) -> str:
    """Fix Height/Weight table formatting.
    
    Creates a properly structured 5-column, 10-row table.
    """
    # Find the section containing the Height and Weight content
    pattern = r'(<p id="header-25-height-and-weight">.*?</p>)(.*?)(<p id="header-30-age">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    next_header = match.group(3)
    
    # Create the properly structured table
    table_html = '''
<table class="ds-table">
<tr><th>Race</th><th>Height Base (inches)</th><th>Height Modifier</th><th>Weight Base (lbs)</th><th>Weight Modifier</th></tr>
<tr><td>Dwarf</td><td>50 (male) / 48 (female)</td><td>2d4</td><td>180 / 170</td><td>4d10</td></tr>
<tr><td>Elf</td><td>70 / 68</td><td>2d6</td><td>160 / 130</td><td>3d10</td></tr>
<tr><td>Half-elf</td><td>70 / 68</td><td>2d6</td><td>120 / 75</td><td>3d12</td></tr>
<tr><td>Half-giant</td><td>70 / 68</td><td>3d10</td><td>1500 / 1450</td><td>3d100</td></tr>
<tr><td>Halfling</td><td>36 / 34</td><td>1d8</td><td>50 / 46</td><td>5d4</td></tr>
<tr><td>Human</td><td>60 / 57</td><td>2d8</td><td>140 / 100</td><td>6d10</td></tr>
<tr><td>Mul</td><td>66 / 65</td><td>2d6</td><td>220 / 180</td><td>5d20</td></tr>
<tr><td>Thri-kreen*</td><td>82 / 82</td><td>1d4</td><td>450 / 450</td><td>1d20</td></tr>
</table>
<p>*Thri-kreen are 48 inches longer than they are tall.</p>
'''
    
    # Replace the section
    replacement = header + '\n' + table_html + '\n' + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_age_table(html: str) -> str:
    """Fix Starting Age table formatting.
    
    Creates a properly structured 4-column, 9-row table.
    """
    # Find the section containing the Starting Age content
    pattern = r'(<p id="header-31-starting-age">.*?</p>)(.*?)(<p id="header-34-aging-effects">)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    next_header = match.group(3)
    
    # Create the properly structured table
    table_html = '''
<table class="ds-table">
<tr><th>Race</th><th>Base Age</th><th>Variable</th><th>Maximum Age Range</th></tr>
<tr><td>Dwarf</td><td>25</td><td>4d6</td><td>200 + 3d20</td></tr>
<tr><td>Elf</td><td>15</td><td>3d4</td><td>100 + 2d20</td></tr>
<tr><td>Half-elf</td><td>15</td><td>2d4</td><td>90 + 2d20</td></tr>
<tr><td>Half-giant</td><td>20</td><td>5d4</td><td>120 + 1d100</td></tr>
<tr><td>Halfling</td><td>25</td><td>3d6</td><td>90 + 4d12</td></tr>
<tr><td>Human</td><td>15</td><td>1d8</td><td>80 + 2d20</td></tr>
<tr><td>Mul</td><td>15</td><td>1d6</td><td>80 + 1d10</td></tr>
<tr><td>Thri-kreen</td><td>6</td><td>1d10</td><td>25 + 1d10</td></tr>
</table>
'''
    
    # Replace the section
    replacement = header + '\n' + table_html + '\n' + next_header
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html


def _fix_aging_effects_table(html: str) -> str:
    """Fix Aging Effects table formatting.
    
    Creates a properly structured 4-column, 9-row table with legend.
    """
    # Find the section containing the Aging Effects content
    # Match from Aging Effects header to the end of the section
    pattern = r'(<p id="header-34-aging-effects">.*?</p>)(.*?)(</section>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if not match:
        return html
    
    header = match.group(1)
    section_end = match.group(3)
    
    # Create the properly structured table
    table_html = '''
<table class="ds-table">
<tr><th>Race</th><th>Middle Age*</th><th>Old Age**</th><th>Venerable***</th></tr>
<tr><td>Dwarf</td><td>100</td><td>133</td><td>200</td></tr>
<tr><td>Elf</td><td>50</td><td>67</td><td>120</td></tr>
<tr><td>Half-elf</td><td>45</td><td>60</td><td>80</td></tr>
<tr><td>Half-giant</td><td>60</td><td>80</td><td>100</td></tr>
<tr><td>Halfling</td><td>45</td><td>60</td><td>70</td></tr>
<tr><td>Human</td><td>40</td><td>53</td><td>80</td></tr>
<tr><td>Mul</td><td>40</td><td>53</td><td>80</td></tr>
<tr><td>Thri-kreen****</td><td>-</td><td>25</td><td>-</td></tr>
</table>
<p>* -1 Str/Con; +1 Int/Wis</p>
<p>** -2 Str/Dex, -1 Con; +1 Wis</p>
<p>*** -1 Str/Dex/Con; +1 Int/Wis</p>
<p>**** Thri-kreen suffer no aging effects until they reach venerable age, when they suffer -1 Str/Dex.</p>
'''
    
    # Replace the section
    replacement = header + '\n' + table_html + '\n' + section_end
    html = html[:match.start()] + replacement + html[match.end():]
    
    return html

