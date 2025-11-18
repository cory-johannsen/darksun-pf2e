"""Chapter 10 HTML Postprocessing

This module applies post-processing fixes to Chapter 10 HTML output.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def postprocess_chapter_10_html(html_content: str) -> str:
    """Apply Chapter 10 specific HTML postprocessing.
    
    Args:
        html_content: The raw HTML content
        
    Returns:
        The processed HTML content
    """
    logger.info("Applying Chapter 10 HTML postprocessing")
    
    # Fix the New Magical Items section headers
    # These should be H2 headers without Roman numerals:
    # - Amulet of Psionic Interference
    # - Oil of Feather Falling
    # - Ring of Life
    # - Rod of Divining
    
    item_names = [
        "Amulet of Psionic Interference",
        "Oil of Feather Falling",
        "Ring of Life",
        "Rod of Divining"
    ]
    
    for item_name in item_names:
        # Pattern to match the current H1 format with Roman numerals
        # Example: <p id="header-10-amulet-of-psionic-interference">V.  <a href="#top"...><span style="color: #ca5804">Amulet of Psionic Interference</span></p>
        # We need to:
        # 1. Remove the Roman numeral (e.g., "V.  ")
        # 2. Change from <p> with colored span to <h2>
        # 3. Keep the ID and back-to-top link
        
        # Create the slug from the item name
        slug = item_name.lower().replace(' ', '-').replace("'", "")
        
        # Pattern to match the current format
        # Captures: (1) header ID, (2) Roman numeral + spaces, (3) back-to-top link, (4) span content
        pattern = rf'<p id="(header-\d+-{re.escape(slug)})">([IVXLCDM]+\.\s+)(<a href="#top"[^>]*>\[\^\]</a>)\s*<span style="color: #ca5804">({re.escape(item_name)})</span></p>'
        
        # Replace with H2 format without Roman numerals
        # Keep ID, back-to-top link, and item name
        replacement = rf'<h2 id="\1">\4 \3</h2>'
        
        html_content = re.sub(pattern, replacement, html_content)
        logger.debug(f"Fixed header for: {item_name}")
    
    # Also split the XP Value and description into separate paragraphs
    # Pattern: <p>XP Value: ### Description text...</p>
    # Split into: <p>XP Value: ###</p><p>Description text...</p>
    
    # For each item, find the paragraph after the H2 and split it
    description_patterns = [
        ("Amulet of Psionic Interference", "This item scrambles"),
        ("Oil of Feather Falling", "Crushing such a fruit"),
        ("Ring of Life", "This item protects"),
        ("Rod of Divining", "This item is a small")
    ]
    
    for item_name, description_start in description_patterns:
        slug = item_name.lower().replace(' ', '-').replace("'", "")
        
        # Pattern to match: <h2 id="header-...-slug">Item Name [^]</h2><p>XP Value: ### Description...</p>
        # Captures: (1) h2 element, (2) XP Value part, (3) Description part
        pattern = rf'(<h2 id="header-\d+-{re.escape(slug)}">{re.escape(item_name)} <a [^>]+>\[\^\]</a></h2>)<p>(XP Value: [^<]+?)({re.escape(description_start)}[^<]+)</p>'
        
        # Replace with separate paragraphs
        replacement = rf'\1<p>\2</p><p>\3</p>'
        
        html_content = re.sub(pattern, replacement, html_content)
        logger.debug(f"Split XP Value and description for: {item_name}")
    
    logger.info("Chapter 10 HTML postprocessing complete")
    return html_content

