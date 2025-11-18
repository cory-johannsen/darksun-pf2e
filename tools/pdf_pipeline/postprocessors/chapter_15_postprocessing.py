"""Chapter 15 Postprocessing - New Spells

This module handles HTML postprocessing for Chapter 15 (New Spells).
Key responsibilities:
- Format spell stat blocks with proper line breaks
- Ensure paragraph breaks in spell descriptions
"""

import logging
import re
from pathlib import Path
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def postprocess(html_content: str) -> str:
    """Apply postprocessing to Chapter 15 HTML.
    
    Args:
        html_content: The HTML content to process
        
    Returns:
        The processed HTML content
    """
    logger.info("Applying Chapter 15 postprocessing")
    
    html_content = _format_spell_stat_blocks(html_content)
    html_content = _add_spell_paragraph_breaks(html_content)
    html_content = _merge_reversible_headers(html_content)
    html_content = _fix_spell_name_formatting(html_content)
    html_content = _fix_conjure_elemental_table(html_content)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html_content = convert_all_styled_headers_to_semantic(html_content)
    
    logger.info("Chapter 15 postprocessing complete")
    return html_content


def _format_spell_stat_blocks(html: str) -> str:
    """Format spell stat blocks with proper line breaks.
    
    Spell stat blocks contain 6-7 lines in the format:
    [Sphere: ...] Range: ... Components: ... Duration: ... Casting Time: ... Area of Effect: ... Saving Throw: ...
    (Sphere is optional)
    
    These should be formatted with line breaks between each stat.
    Additionally, any text after "Saving Throw: None" should be split into a new paragraph.
    """
    logger.info("Formatting spell stat blocks")
    
    # Pattern 1: Match spell stat blocks WITH Sphere (priest spells)
    # Looks for text containing Sphere + all 6 stat fields in a single paragraph
    stat_block_with_sphere_pattern = re.compile(
        r'<p>(Sphere:[^<]*?Range:[^<]*?Components:[^<]*?Duration:[^<]*?Casting Time:[^<]*?Area of Effect:[^<]*?Saving Throw:[^<]*?)</p>',
        re.DOTALL
    )
    
    # Pattern 2: Match spell stat blocks WITHOUT Sphere (wizard spells)
    # Looks for text containing all 6 stat fields in a single paragraph
    stat_block_pattern = re.compile(
        r'<p>(Range:[^<]*?Components:[^<]*?Duration:[^<]*?Casting Time:[^<]*?Area of Effect:[^<]*?Saving Throw:[^<]*?)</p>',
        re.DOTALL
    )
    
    def format_stat_block(match):
        """Format a single stat block with line breaks."""
        block_text = match.group(1)
        
        # Split on each stat field and add line breaks
        # Replace the separators with line breaks while keeping the field names
        formatted = block_text
        # Add break before each field (handles both Sphere and Range as first field)
        formatted = re.sub(r'\s+(Range:)', r'<br>\n\1', formatted)
        formatted = re.sub(r'\s+(Components:)', r'<br>\n\1', formatted)
        formatted = re.sub(r'\s+(Duration:)', r'<br>\n\1', formatted)
        formatted = re.sub(r'\s+(Casting Time:)', r'<br>\n\1', formatted)
        formatted = re.sub(r'\s+(Area of Effect:)', r'<br>\n\1', formatted)
        formatted = re.sub(r'\s+(Saving Throw:)', r'<br>\n\1', formatted)
        
        # Check if there's text after "Saving Throw: None" that should be a separate paragraph
        # Pattern: "Saving Throw: None This spell..." -> split into stat block and paragraph
        saving_throw_split = re.match(
            r'(.*Saving Throw:\s*None)\s+(.+)',
            formatted,
            re.DOTALL
        )
        
        if saving_throw_split:
            stats_part = saving_throw_split.group(1)
            description_part = saving_throw_split.group(2)
            # Wrap stats in div and put description in a separate paragraph
            return f'<div class="spell-stats">\n{stats_part}\n</div>\n<p>{description_part}</p>'
        
        # Wrap in a div with a special class for styling
        return f'<div class="spell-stats">\n{formatted}\n</div>'
    
    # Apply both patterns (order matters: with-sphere first to catch those, then without-sphere)
    html = stat_block_with_sphere_pattern.sub(format_stat_block, html)
    html = stat_block_pattern.sub(format_stat_block, html)
    
    logger.info("Spell stat blocks formatted")
    return html


def _add_spell_paragraph_breaks(html: str) -> str:
    """Add paragraph breaks in spell descriptions.
    
    Spell descriptions often have multiple logical paragraphs that get merged together.
    This function splits them at key transition points.
    """
    logger.info("Adding spell paragraph breaks")
    
    # Fix Air Lens paragraphs - merge the fragmented middle section
    html = _fix_air_lens_paragraphs(html)
    
    # Common patterns where paragraph breaks should occur in spell descriptions
    # These typically indicate transitions to new information
    break_patterns = [
        (r'(\. )(At level)', r'\1</p>\n<p>\2'),  # "At level" often starts a new paragraph
        (r'(\. )(Casters who)', r'\1</p>\n<p>\2'),  # "Casters who" indicates level-based effects
        (r'(\. )(Casters of level)', r'\1</p>\n<p>\2'),  # More level-based effects
        (r'(\. )(Finally,)', r'\1</p>\n<p>\2'),  # "Finally" indicates the last paragraph
        (r'(\. )(In DARK SUN)', r'\1</p>\n<p>\2'),  # Dark Sun specific notes
        (r'(\. )(The material component)', r'\1</p>\n<p>\2'),  # Material components often end descriptions
        (r'(\. )(The affected)', r'\1</p>\n<p>\2'),  # Target descriptions
        (r'(\. )(An army)', r'\1</p>\n<p>\2'),  # Specific to certain spells
        (r'(\. )(The elemental)', r'\1</p>\n<p>\2'),  # Conjuration spells
        (r'(\. )(Should the army)', r'\1</p>\n<p>\2'),  # Conditional effects
        (r'(\. )(The casting of the spell)', r'\1</p>\n<p>\2'),  # Raze spell - casting effects
        (r'(\. )(The ash created)', r'\1</p>\n<p>\2'),  # Raze spell - ash effects
        (r'(\. )(The reverse of this spell)', r'\1</p>\n<p>\2'),  # Reverse spell effects
        (r'(\. )(This spell turns)', r'\1</p>\n<p>\2'),  # Transmutation effects
        (r'(\. )(In either case)', r'\1</p>\n<p>\2'),  # Rejuvenate spell - area of effect
        (r'(\. )(The duration of the spell)', r'\1</p>\n<p>\2'),  # Rejuvenate spell - duration
        (r'( )(Defilers cannot)', r'</p>\n<p>\2'),  # Rejuvenate spell - defiler restriction
    ]
    
    for pattern, replacement in break_patterns:
        html = re.sub(pattern, replacement, html)
    
    logger.info("Spell paragraph breaks added")
    return html


def _fix_air_lens_paragraphs(html: str) -> str:
    """Fix Air Lens spell paragraph structure.
    
    Air Lens should have 3 paragraphs:
    1. Main description (starts with "By means of this spell") - ends before "The spell can also"
    2. Ignition effects (starts with "The spell can also")
    3. Material component (starts with "The material component")
    
    The issue is that all the text is in one paragraph that needs to be split.
    """
    # Simplest approach: direct string replacement
    # Split the first paragraph into two: before and after "The spell can also"
    old_text = "half damage. The spell can also"
    new_text = "half damage.</p>\n<p>The spell can also"
    
    if old_text in html:
        air_lens_split = html.replace(old_text, new_text, 1)  # Only replace first occurrence
        logger.info("Fixed Air Lens paragraph structure (split into 3 paragraphs)")
        return air_lens_split
    
    logger.info("Air Lens split point not found, skipping fix")
    return html


def _merge_reversible_headers(html: str) -> str:
    """Merge "(Reversible)" headers with the preceding spell header.
    
    Some spells have "(Reversible)" as a separate header when it should be
    part of the spell name on the same line.
    """
    logger.info("Merging (Reversible) headers")
    
    # Pattern to match a spell header followed by a "(Reversible)" header
    # Match: <p id="header-X-...">NUMERAL. [^] <span>Spell Name</span></p><p id="header-Y-reversible">NUMERAL. [^] <span>(Reversible)</span></p>
    reversible_pattern = re.compile(
        r'(<p id="header-\d+-[^"]+">.*?<span[^>]*>)([^<]+)(</span></p>)'
        r'(<p id="header-\d+-(?:\-)?reversible">.*?<span[^>]*>)\(\s*Reversible\s*\)(</span></p>)',
        re.IGNORECASE | re.DOTALL
    )
    
    def merge_reversible(match):
        """Merge the (Reversible) notation into the spell name."""
        before_spell = match.group(1)
        spell_name = match.group(2)
        after_spell = match.group(3)
        # Skip the entire second <p> tag - we're merging it into the first
        
        # Add (Reversible) to the spell name
        merged = f'{before_spell}{spell_name} (Reversible){after_spell}'
        return merged
    
    html = reversible_pattern.sub(merge_reversible, html)
    
    # Also remove orphaned "(Reversible)" entries from the TOC
    # Pattern: <li><a href="#header-XX-reversible">Reversible</a></li> or similar (with or without parens)
    toc_reversible_pattern = re.compile(
        r'<li[^>]*><a href="#header-\d+-(?:\-)?reversible(?:\-)?"\s*[^>]*>\s*\(?\s*Reversible\s*\)?\s*</a></li>',
        re.IGNORECASE
    )
    html = toc_reversible_pattern.sub('', html)
    
    logger.info("(Reversible) headers merged")
    return html


def _fix_spell_name_formatting(html: str) -> str:
    """Fix spell name formatting issues.
    
    Fixes:
    - "MercifulShadows" -> "Merciful Shadows"
    - "CharmPersonorMammal" -> "Charm Person or Mammal"
    - "Sandto Stone" -> "Sand to Stone"  
    - "( Alteration )" -> "(Alteration)" (remove extra spaces)
    """
    logger.info("Fixing spell name formatting")
    
    # Fix "MercifulShadows" -> "Merciful Shadows"
    html = re.sub(
        r'MercifulShadows',
        'Merciful Shadows',
        html
    )
    
    # Fix "CharmPersonorMammal" -> "Charm Person or Mammal"
    html = re.sub(
        r'CharmPersonorMammal',
        'Charm Person or Mammal',
        html
    )
    
    # Fix "TransmuteSandtoStone" -> "Transmute Sand to Stone"
    # Also fix "Transmute Sandto Stone" -> "Transmute Sand to Stone"
    html = re.sub(
        r'Transmute\s*Sandto\s*Stone',
        'Transmute Sand to Stone',
        html,
        flags=re.IGNORECASE
    )
    
    # Fix extra spaces around parentheses in spell types like "( Alteration )"
    # Pattern: ( followed by optional spaces, word(s), optional spaces, )
    html = re.sub(
        r'\(\s+([A-Za-z\s,/]+?)\s+\)',
        r'(\1)',
        html
    )
    
    logger.info("Spell name formatting fixed")
    return html


def _fix_conjure_elemental_table(html: str) -> str:
    """Fix Conjure Elemental spell table.
    
    The Hit Dice table for Conjure Elemental is malformed as an H3 header followed
    by a paragraph. This function converts it to a proper HTML table.
    
    The table should have:
    - 2 columns: Roll, Hit Dice
    - 3 rows with data:
      - 01-65: 8
      - 66-90: 12
      - 91-00: 16
    """
    logger.info("Fixing Conjure Elemental table")
    
    # Pattern to match the malformed header and following paragraph
    # <h3 id="header-r-o-l-l-hit-dice-01-65-8-66-90-12">R o l l Hit Dice 01-65 8 66-90 12 ...</h3><p>91-00</p>
    malformed_pattern = re.compile(
        r'<h3[^>]*id="header-r-o-l-l-hit-dice[^"]*"[^>]*>.*?</h3>\s*<p>91-00</p>',
        re.DOTALL | re.IGNORECASE
    )
    
    if not malformed_pattern.search(html):
        logger.info("Conjure Elemental malformed table not found, skipping fix")
        return html
    
    # Create the proper table HTML
    table_html = '''<table class="ds-table">
<thead>
<tr>
<th>Roll</th>
<th>Hit Dice</th>
</tr>
</thead>
<tbody>
<tr>
<td>01-65</td>
<td>8</td>
</tr>
<tr>
<td>66-90</td>
<td>12</td>
</tr>
<tr>
<td>91-00</td>
<td>16</td>
</tr>
</tbody>
</table>'''
    
    # Replace the malformed content with the table
    html = malformed_pattern.sub(table_html, html)
    
    logger.info("Fixed Conjure Elemental table")
    return html
