"""Chapter 10 Postprocessing - Treasure

This module handles HTML postprocessing for Chapter 10 (Treasure).
Key responsibilities:
- Fix hyphenated words that were split across lines in the source PDF
"""

import logging
import re
from pathlib import Path
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def postprocess(html_content: str) -> str:
    """Apply postprocessing to Chapter 10 HTML.
    
    Args:
        html_content: The HTML content to process
        
    Returns:
        The processed HTML content
    """
    logger.info("=" * 80)
    logger.info("CHAPTER 10 POSTPROCESSING CALLED!")
    logger.info("=" * 80)
    logger.info(f"HTML content length: {len(html_content)}")
    
    html_content = _fix_hyphenated_words(html_content)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html_content = convert_all_styled_headers_to_semantic(html_content)
    
    logger.info("Chapter 10 postprocessing complete")
    logger.info("=" * 80)
    return html_content


def _fix_hyphenated_words(html: str) -> str:
    """Fix hyphenated words that were split across lines.
    
    The source PDF has several words that were hyphenated across line breaks
    but should be merged into single words.
    """
    logger.info("Fixing hyphenated words")
    
    # List of hyphenated words that need to be fixed
    # Format: (pattern to find, replacement)
    fixes = [
        (r'equiva-\s*l(?=ent)', 'equival'),  # equiva- lent -> equivalent
        (r'cam-\s*p(?=aign)', 'camp'),       # cam- paign -> campaign
        (r'nor-\s*m(?=ally)', 'norm'),       # nor- mally -> normally
        (r'gladi-\s*a(?=tor)', 'gladia'),    # gladi- ator -> gladiator
        (r'thri-\s*k(?=reen)', 'thrik'),     # thri- kreen -> thri-kreen
        (r'ani-\s*m(?=al)', 'anim'),         # ani- mal -> animal
        (r'pan-\s*t(?=heons)', 'pant'),      # pan- theons -> pantheons
        (r'fig-\s*u(?=rines)', 'figu'),      # fig- urines -> figurines
        (r'sum-\s*m(?=ons)', 'summ'),        # sum- mons -> summons
    ]
    
    for pattern, replacement in fixes:
        original = html
        html = re.sub(pattern, replacement, html)
        if html != original:
            logger.info(f"  Fixed hyphenation: {pattern} -> {replacement}")
    
    logger.info("Hyphenated words fixed")
    return html

