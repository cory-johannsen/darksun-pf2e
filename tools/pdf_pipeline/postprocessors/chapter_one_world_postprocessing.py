"""
Chapter One: The World of Athas HTML Postprocessing

Handles mid-paragraph breaks that can't be handled at the PDF extraction level.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def apply_chapter_one_world_history_paragraph_breaks(html: str) -> str:
    """
    Apply paragraph breaks for mid-sentence breaks in the History section.
    
    The History section has some sentences that need to be split into separate
    paragraphs, but they appear mid-line in the source PDF. We handle them here
    in the HTML post-processing stage.
    """
    logger.info("Applying History section mid-paragraph breaks")
    
    # Break patterns that appear mid-paragraph
    # Format: (search_pattern, split_at_pattern)
    mid_para_breaks = [
        # "... some better world. Like men, the elves..." -> split before "Like men"
        (r'(\. )(Like men, the elves,)',  r'\1</p>\n<p>\2'),
        # "... noble progenitors. Even the plants," -> split before "Even the plants"
        (r'(\. )(Even the plants,)', r'\1</p>\n<p>\2'),
        # "... blanketed the land. The essence of every living thing," -> split before "The essence"
        (r'(\. )(The essence of every living thing,)', r'\1</p>\n<p>\2'),
    ]
    
    for pattern, replacement in mid_para_breaks:
        old_html = html
        html = re.sub(pattern, replacement, html)
        if html != old_html:
            logger.info(f"Applied mid-paragraph break: {pattern[:50]}...")
    
    return html


def postprocess_chapter_one_world(html: str) -> str:
    """
    Apply all HTML post-processing for Chapter One: The World of Athas.
    """
    logger.info("Postprocessing Chapter One: The World of Athas HTML")
    
    # Apply History paragraph breaks
    html = apply_chapter_one_world_history_paragraph_breaks(html)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html = convert_all_styled_headers_to_semantic(html)
    
    return html
