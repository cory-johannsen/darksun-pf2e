"""Utilities for converting styled <p> headers to semantic HTML headers.

This module provides utilities to convert from the legacy styled <p> tag approach
to proper semantic HTML headers (<h2>, <h3>, <h4>) for better accessibility, SEO,
and web standards compliance.

Legacy Format:
    <p id="header-1-name" class="h2-header">
        <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a>
        <span style="color: #cd490a; font-size: 0.9em">Header Name</span>
    </p>

Semantic Format:
    <h2 id="header-1-name">
        Header Name
        <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a>
    </h2>
"""

import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

HeaderLevel = Literal["h2", "h3", "h4"]


def convert_styled_p_to_semantic_header(
    html: str,
    header_id_pattern: str = r'header-\d+-[a-z0-9-]+',
    header_level: HeaderLevel = "h2"
) -> str:
    """
    Convert styled <p> tags to semantic HTML headers.
    
    Args:
        html: HTML content to process
        header_id_pattern: Regex pattern to match header IDs
        header_level: Target HTML header level (h2, h3, or h4)
    
    Returns:
        HTML with converted headers
    
    Example:
        >>> html = '<p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span style="color: #cd490a;">Test</span></p>'
        >>> result = convert_styled_p_to_semantic_header(html, r'header-\\d+-test', 'h2')
        >>> '<h2 id="header-1-test">Test <a href="#top"' in result
        True
    """
    # Pattern matches the common formats:
    # 1. <p id="HEADER_ID" class="h2-header"><a href="#top"...>[^]</a> <span...>TEXT</span></p>
    # 2. <p id="HEADER_ID" class="h3-header">...(similar structure)
    # 3. <p id="HEADER_ID" class="h4-header">...(similar structure)
    
    # More flexible pattern that handles variations in spacing and style attributes
    pattern = rf'<p\s+id="({header_id_pattern})"\s+class="h[234]-header"[^>]*>\s*<a\s+href="#top"[^>]*>\[\^\]</a>\s*<span[^>]*>(.*?)</span>\s*</p>'
    
    def replace_header(match):
        header_id = match.group(1)
        header_text = match.group(2).strip()
        # Put text first, then back-to-top link (per [HEADER_FORMAT])
        return f'<{header_level} id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></{header_level}>'
    
    old_html = html
    html = re.sub(pattern, replace_header, html, flags=re.DOTALL)
    
    # Count conversions
    old_count = old_html.count('class="h2-header"') + old_html.count('class="h3-header"') + old_html.count('class="h4-header"')
    new_count = html.count('class="h2-header"') + html.count('class="h3-header"') + html.count('class="h4-header"')
    conversions = old_count - new_count
    
    if conversions > 0:
        logger.info(f"Converted {conversions} styled <p> headers to <{header_level}> tags")
    
    return html


def convert_all_styled_headers_to_semantic(html: str) -> str:
    """
    Convert all styled header classes (h2-header, h3-header, h4-header) to semantic HTML.
    
    This function automatically detects the appropriate header level based on the CSS class
    and converts to the corresponding semantic tag.
    
    Args:
        html: HTML content to process
    
    Returns:
        HTML with all styled headers converted to semantic headers
    
    Example:
        >>> html = '<p id="header-1-main" class="h2-header"><a href="#top">[^]</a> <span>Main</span></p>'
        >>> html += '<p id="header-2-sub" class="h3-header"><a href="#top">[^]</a> <span>Sub</span></p>'
        >>> result = convert_all_styled_headers_to_semantic(html)
        >>> '<h2 id="header-1-main">' in result
        True
        >>> '<h3 id="header-2-sub">' in result
        True
    """
    # Convert in order: h4 -> h3 -> h2 -> h1 to avoid overlapping matches
    html = _convert_by_class(html, "h4-header", "h4")
    html = _convert_by_class(html, "h3-header", "h3")
    html = _convert_by_class(html, "h2-header", "h2")
    html = _convert_by_class(html, "h1-header", "h2")  # Convert H1 to H2 (chapter title is H1)
    
    return html


def _convert_by_class(html: str, css_class: str, header_level: str) -> str:
    """
    Internal helper to convert headers with a specific CSS class.
    
    Args:
        html: HTML content to process
        css_class: CSS class to match (e.g., "h2-header")
        header_level: Target header level (e.g., "h2")
    
    Returns:
        HTML with converted headers
    """
    # Pattern for headers with specific class
    # This pattern handles two formats:
    # 1. With roman numeral: <p id="..." class="h2-header">II. <span...>Text</span> <a href="#top">[^]</a></p>
    # 2. Without roman numeral: <p id="..." class="h3-header"> <a href="#top">[^]</a> <span...>Text</span></p>
    # Note: The anchor can be before or after the span depending on whether there's a roman numeral
    pattern = rf'<p\s+id="([^"]+)"\s+class="{css_class}"[^>]*>\s*(?:([IVXLCDM]+\.\s+))?<a\s+href="#top"[^>]*>\[\^\]</a>\s*(<span[^>]*>.*?</span>)\s*</p>'
    
    def replace_header(match):
        header_id = match.group(1)
        roman_prefix = match.group(2) or ""  # May be None if no roman numeral
        header_content = match.group(3)  # Preserve full span with styling
        # Keep roman numeral prefix and styled span in the output
        return f'<{header_level} id="{header_id}">{roman_prefix}{header_content} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></{header_level}>'
    
    old_html = html
    html = re.sub(pattern, replace_header, html, flags=re.DOTALL)
    
    conversions = old_html.count(f'class="{css_class}"') - html.count(f'class="{css_class}"')
    if conversions > 0:
        logger.info(f"Converted {conversions} {css_class} headers to <{header_level}> tags")
    
    return html


def update_toc_for_semantic_headers(html: str) -> str:
    """
    Update Table of Contents to work with semantic headers.
    
    This function is typically not needed as the TOC generator should already
    detect semantic headers. However, it can be used to ensure TOC entries
    maintain their indentation classes.
    
    Args:
        html: HTML content with TOC
    
    Returns:
        HTML with updated TOC
    """
    # The TOC generator in journal_lib.py should handle semantic headers automatically
    # This function is a placeholder for any additional TOC updates if needed
    logger.debug("TOC should automatically work with semantic headers")
    return html

