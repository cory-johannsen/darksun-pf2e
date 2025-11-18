"""
Chapter 13 Post-Processing - Vision and Light

This module handles HTML post-processing for Chapter 13,
including table reconstruction and formatting.
"""

import logging
import re
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _insert_visibility_table(html: str) -> str:
    """
    Insert the properly formatted Dark Sun Visibility Ranges table.
    
    The table should appear after the "Dark Sun Visibility Ranges" H2 header
    and before any remaining content.
    
    Table structure:
    - 6 columns: Condition, Movement, Spotted, Type, ID, Detail
    - 6 rows (including header)
    - Movement, Spotted, Type, ID, Detail contain numbers
    - Condition contains text with commas
    """
    logger.info("Inserting Dark Sun Visibility Ranges table")
    
    # Define the table HTML
    table_html = """
<table class="visibility-ranges">
<thead>
<tr>
<th>Condition</th>
<th>Movement</th>
<th>Spotted</th>
<th>Type</th>
<th>ID</th>
<th>Detail</th>
</tr>
</thead>
<tbody>
<tr>
<td>Sand, blowing</td>
<td>100</td>
<td>50</td>
<td>25</td>
<td>15</td>
<td>10</td>
</tr>
<tr>
<td>Sandstorm, mild</td>
<td>50</td>
<td>25</td>
<td>15</td>
<td>10</td>
<td>5</td>
</tr>
<tr>
<td>Sandstorm, driving</td>
<td>10</td>
<td>10</td>
<td>5</td>
<td>5</td>
<td>3</td>
</tr>
<tr>
<td>Night, both moons</td>
<td>200</td>
<td>100</td>
<td>50</td>
<td>25</td>
<td>15</td>
</tr>
<tr>
<td>Silt Sea, calm</td>
<td>500</td>
<td>200</td>
<td>100</td>
<td>50</td>
<td>25</td>
</tr>
<tr>
<td>Silt Sea, rolling</td>
<td>100</td>
<td>50</td>
<td>25</td>
<td>10</td>
<td>5</td>
</tr>
</tbody>
</table>
"""
    
    # Find where to insert the table
    # It should come after the "Dark Sun Visibility Ranges" H2 header
    
    # First, remove any incorrectly rendered table elements
    # Remove individual header paragraphs (Condition, Movement, Type, Spotted, Detail)
    html = re.sub(
        r'<p id="header-\d+-condition">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-movement">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-type">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-spotted">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p id="header-\d+-detail">.*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Remove paragraphs containing table condition values mixed with numbers
    # These paragraphs have condition names followed by numbers
    html = re.sub(
        r'<p>(?:Sand, blowing|Sandstorm, mild|Sandstorm, driving|Night, both moons|Silt Sea, calm|Silt Sea, rolling).*?</p>',
        '',
        html,
        flags=re.DOTALL
    )
    
    # Find the Dark Sun Visibility Ranges header
    # It should be rendered as H2
    pattern = r'(<p id="header-\d+-dark-sun-visibility-ranges"[^>]*>.*?</p>)'
    match = re.search(pattern, html, re.DOTALL)
    
    if match:
        # Convert this to an H2 header
        header_html = match.group(1)
        h2_html = re.sub(
            r'<p id="(header-\d+-dark-sun-visibility-ranges)"[^>]*>',
            r'<h2 id="\1">',
            header_html
        )
        h2_html = re.sub(r'</p>', '</h2>', h2_html)
        
        # Remove the roman numeral from the header
        h2_html = re.sub(r'(II\.|III\.|IV\.|V\.|VI\.|VII\.)\s+', '', h2_html)
        
        # Insert the table after the H2 header
        html = html.replace(header_html, h2_html + table_html)
        
        logger.info("Successfully inserted visibility ranges table")
    else:
        logger.warning("Could not find 'Dark Sun Visibility Ranges' header to insert table")
    
    return html


def _fix_intro_paragraph(html: str) -> str:
    """
    Ensure the intro paragraph is properly formatted.
    
    The paragraph should read: "All of the conditions presented on the Visibility 
    Ranges table in the Player's Handbook exist on Athas. However, there are a 
    number of conditions unique to Athas that should be added."
    """
    logger.info("Fixing Chapter 13 intro paragraph")
    
    # The current HTML has the first part ending with "exist on" and
    # the second part starting with various condition names, then "Athas. However"
    
    # Pattern to find the first part of the intro
    first_part_pattern = r'(<p>All of the conditions presented.*?exist on</p>)'
    
    # Pattern to find the mixed paragraph with conditions and "However"
    # This paragraph incorrectly contains: "Sand, blowing Sandstorm, mild ... Athas. However, there are..."
    mixed_paragraph_pattern = r'<p>(?:Sand, blowing.*?)?Athas\. However, there are a number of conditions unique to Athas that should be added\.</p>'
    
    first_match = re.search(first_part_pattern, html, re.DOTALL)
    second_match = re.search(mixed_paragraph_pattern, html, re.DOTALL)
    
    if first_match and second_match:
        first_part_html = first_match.group(1)
        # Extract just the "Athas. However..." part from the mixed paragraph
        second_match_text = second_match.group(0)
        # Get the "Athas. However..." part
        athas_match = re.search(r'(Athas\. However, there are a number of conditions unique to Athas that should be added\.)', second_match_text)
        
        if athas_match:
            second_part_text = athas_match.group(1)
            
            # Create merged paragraph
            merged = first_part_html.replace('exist on</p>', f'exist on {second_part_text}</p>')
            
            # Replace in HTML
            html = html.replace(first_part_html, merged)
            # Remove the mixed paragraph entirely
            html = html.replace(second_match.group(0), '')
            
            logger.info("Successfully merged intro paragraph")
        else:
            logger.warning("Could not extract 'Athas. However' text from mixed paragraph")
    else:
        logger.warning("Could not find intro paragraph parts to merge")
        if not first_match:
            logger.warning("  - First part not found")
        if not second_match:
            logger.warning("  - Second part not found")
    
    return html


def _update_table_of_contents(html: str) -> str:
    """
    Update the table of contents to remove table-related entries
    and keep only the main sections.
    """
    logger.info("Updating Chapter 13 table of contents")
    
    # Remove TOC entries for Condition, Movement, Type, Spotted, Detail
    # These should not be in the TOC as they're table headers, not document sections
    html = re.sub(
        r'<li><a href="#header-\d+-condition">Condition</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-movement">Movement</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-type">Type</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-spotted">Spotted</a></li>',
        '',
        html
    )
    html = re.sub(
        r'<li><a href="#header-\d+-detail">Detail</a></li>',
        '',
        html
    )
    
    # Clean up any extra whitespace
    html = re.sub(r'</li>\s*</ul>', r'</li></ul>', html)
    
    logger.info("Updated table of contents")
    
    return html


def apply_chapter_13_content_fixes(html: str) -> str:
    """
    Apply all Chapter 13 HTML content fixes.
    
    This includes:
    1. Fixing the intro paragraph
    2. Inserting the visibility ranges table
    3. Updating the table of contents
    
    Args:
        html: The HTML content to fix
        
    Returns:
        The fixed HTML content
    """
    logger.info("Applying Chapter 13 content fixes")
    
    html = _fix_intro_paragraph(html)
    html = _insert_visibility_table(html)
    html = _update_table_of_contents(html)
    
    logger.info("Chapter 13 content fixes complete")
    
    return html

