"""
Chapter Five: Monsters of Athas - Monster Manual Page Reconstruction

This module handles reconstruction of scattered monster stat blocks into 
proper AD&D 2E monster manual pages with tables and structured descriptions.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


# Valid values for each monster stat field (used for intelligent line break insertion)
# 
# LINE BREAK RECONSTRUCTION RULE:
# For rows with documented valid value ranges, any text that does NOT match those 
# valid values/patterns is NOT part of that row and requires a line break.
# This allows intelligent splitting of merged text by detecting value boundaries.
#
# Example: "TablelandsUncommonTribe" becomes:
#   CLIMATE/TERRAIN: Tablelands  ← valid value
#   FREQUENCY: Uncommon          ← "Uncommon" not valid for CLIMATE/TERRAIN, insert break
#   ORGANIZATION: Tribe          ← "Tribe" not valid for FREQUENCY, insert break
#
VALID_VALUES = {
    "CLIMATE/TERRAIN": [
        "Any", "Tablelands", "Tablelands, Mountains, and Hinterlands",
        "Any sandy region", "Sands, stony barrens, rocky badlands, and islands",
        "Sea of Silt Islands, Tablelands", "Tablelands, Mountains",
        "Tablelands and Hinterlands", "Badlands", "Tablelands and mountains"
    ],
    "FREQUENCY": ["Uncommon", "Rare", "Very Rare", "Unique"],
    "ORGANIZATION": ["Tribe", "Solitary", "Small Tribes", "Clans", "Tribal", "Family", "Pack"],
    "ACTIVITY CYCLE": ["Night", "Any", "Day", "Day/Night", "Nocturnal"],
    "DIET": ["Omnivore", "Carnivore"],
    "ALIGNMENT": [
        "Neutral evil", "Lawful evil", "Varies by individual", 
        "Chaotic", "Chaotic neutral", "Neutral"
    ],
    "MAGIC RESISTANCE": ["Nil"],  # Also "#%" patterns
}


# Monster definitions with boundaries for extraction
MONSTERS = [
    {
        "name": "Belgoi",
        "id_pattern": r'header-\d+-belgoi',
        "next_marker": r'<p><span[^>]*><strong>Braxat</strong></span></p>',
        "description_start": "At first sight",
        "has_psionics": True
    },
    {
        "name": "Braxat",
        "id_pattern": r'<p><span[^>]*><strong>Braxat</strong></span></p>',
        "next_marker": r'<p id="header-\d+-dragon-of-tyr">',
        "description_start": "It is difficult to tell",
        "has_psionics": True
    },
    {
        "name": "Dragon of Tyr",
        "id_pattern": r'header-\d+-dragon-of-tyr',
        "next_marker": r'<p id="header-\d+-dune-freak-anakore">',
        "description_start": "Fortunately, there is only",
        "has_psionics": True
    },
    {
        "name": "Dune Freak (Anakore)",
        "id_pattern": r'header-\d+-dune-freak-anakore',
        "next_marker": r'<p><span[^>]*><strong>Gaj</strong></span></p>',
        "description_start": "The anakore are",
        "has_psionics": False
    },
    {
        "name": "Gaj",
        "id_pattern": r'<p><span[^>]*><strong>Gaj</strong></span></p>',
        "next_marker": r'<p id="header-\d+-giant-athasian">',
        "description_start": "The gaj is a psionic",
        "has_psionics": True
    },
    {
        "name": "Giant, Athasian",
        "id_pattern": r'header-\d+-giant-athasian',
        "next_marker": r'<p><span[^>]*><strong>Gith</strong></span></p>',
        "description_start": "Athasian giants come",
        "has_psionics": True  # Special case
    },
    {
        "name": "Gith",
        "id_pattern": r'<p><span[^>]*><strong>Gith</strong></span></p>',
        "next_marker": r'<p><span[^>]*><strong>Jozhal</strong></span></p>',
        "description_start": "The gith are a race",
        "has_psionics": True
    },
    {
        "name": "Jozhal",
        "id_pattern": r'<p><span[^>]*><strong>Jozhal</strong></span></p>',
        "next_marker": r'<p id="header-\d+-silk-wyrm">',
        "description_start": "Standing about four feet",
        "has_psionics": True
    },
    {
        "name": "Silk Wyrm",
        "id_pattern": r'header-\d+-silk-wyrm',
        "next_marker": r'<p id="header-\d+-tembo">',
        "description_start": "The silk wyrm is a snake",
        "has_psionics": True
    },
    {
        "name": "Tembo",
        "id_pattern": r'header-\d+-tembo',
        "next_marker": r'</section>',  # End of chapter
        "description_start": "The tembo is a despicable",
        "has_psionics": True
    }
]


def _extract_plain_text(html: str) -> str:
    """
    Extract plain text from HTML, removing tags and normalizing whitespace.
    Handles extraneous spaces like "N i l" -> "Nil".
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Normalize multiple spaces
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def _split_merged_value(raw_value: str, current_field: str, next_field: str = None) -> Tuple[str, str]:
    """
    Split merged values using the line break reconstruction rule:
    "For rows with documented valid value ranges, any text that does NOT match 
    those valid values/patterns is NOT part of that row."
    
    Args:
        raw_value: The raw extracted value that may contain merged fields
        current_field: The name of the current field (e.g., "CLIMATE/TERRAIN")
        next_field: The name of the next field (e.g., "FREQUENCY")
        
    Returns:
        Tuple of (current_field_value, remaining_text)
    """
    if not raw_value:
        return ("", "")
    
    # Check if current field has known valid values
    if current_field in VALID_VALUES:
        valid_values = VALID_VALUES[current_field]
        
        # Try to find the longest matching valid value from the start
        best_match = ""
        remaining = raw_value
        
        # Sort by length descending to try longest matches first
        for valid_value in sorted(valid_values, key=len, reverse=True):
            if raw_value.startswith(valid_value):
                # Found a valid match
                best_match = valid_value
                remaining = raw_value[len(valid_value):].strip()
                break
        
        if best_match:
            return (best_match, remaining)
    
    # If no valid value list, try to detect boundary using next field's valid values
    if next_field and next_field in VALID_VALUES:
        next_valid_values = VALID_VALUES[next_field]
        
        # Find where the next field's value starts
        for valid_value in sorted(next_valid_values, key=len, reverse=True):
            if valid_value in raw_value:
                idx = raw_value.index(valid_value)
                if idx > 0:
                    # Split at the boundary
                    current_value = raw_value[:idx].strip()
                    remaining = raw_value[idx:].strip()
                    return (current_value, remaining)
    
    # Default: return the whole value as-is
    return (raw_value, "")


def _normalize_stat_labels(text: str) -> str:
    """
    Normalize stat labels by removing extraneous spaces.
    Handles cases like "MOR A L E" -> "MORALE", "N i l" -> "Nil", etc.
    """
    # List of labels to normalize (remove spaces within these words)
    labels_to_normalize = [
        "CLIMATE/TERRAIN", "FREQUENCY", "ORGANIZATION", "ACTIVITY CYCLE", "DIET",
        "INTELLIGENCE", "TREASURE", "ALIGNMENT", "NO. APPEARING", "ARMOR CLASS",
        "MOVEMENT", "HIT DICE", "THAC0", "NO. OF ATTACKS", "DAMAGE/ATTACK",
        "SPECIAL ATTACKS", "SPECIAL DEFENSES", "MAGIC RESISTANCE", "SIZE",
        "MORALE", "XP VALUE", "PSIONICS SUMMARY", "Nil", "Combat", "Habitat", "Ecology"
    ]
    
    normalized = text
    for label in labels_to_normalize:
        # Create pattern that matches the label with optional spaces between each character
        pattern_chars = []
        for char in label:
            if char.isalnum() or char in './-':
                pattern_chars.append(f'{re.escape(char)}\\s*')
            elif char == ' ':
                pattern_chars.append(r'\s+')
            else:
                pattern_chars.append(re.escape(char))
        
        spaced_pattern = ''.join(pattern_chars).rstrip(r'\s*')  # Remove trailing \s*
        
        # Replace spaced version with normalized version
        normalized = re.sub(spaced_pattern, label, normalized, flags=re.IGNORECASE)
    
    return normalized


def _parse_stat_block(html_fragment: str) -> Dict[str, str]:
    """
    Parse monster statistics from scattered HTML paragraphs.
    Uses intelligent value splitting to handle merged rows.
    
    Args:
        html_fragment: HTML containing the stat block paragraphs
        
    Returns:
        Dict mapping stat labels to values
    """
    text = _extract_plain_text(html_fragment)
    
    # Normalize stat labels (remove extraneous spaces like "MOR A L E" -> "MORALE")
    text = _normalize_stat_labels(text)
    
    # Define the 21 stat labels in order (PSIONICS removed - now in separate Psionics Summary)
    stats_order = [
        "CLIMATE/TERRAIN",
        "FREQUENCY",
        "ORGANIZATION",
        "ACTIVITY CYCLE",
        "DIET",
        "INTELLIGENCE",
        "TREASURE",
        "ALIGNMENT",
        "NO. APPEARING",
        "ARMOR CLASS",
        "MOVEMENT",
        "HIT DICE",
        "THAC0",
        "NO. OF ATTACKS",
        "DAMAGE/ATTACK",
        "SPECIAL ATTACKS",
        "SPECIAL DEFENSES",
        "MAGIC RESISTANCE",
        "SIZE",
        "MORALE",
        "XP VALUE"
    ]
    
    # STEP 1: Extract values
    # Two possible formats:
    #   A) "LABEL: VALUE" (standard)
    #   B) "VALUE LABEL:" (reverse - value before label)
    raw_stats = {}
    
    logger.debug(f"Stat block text (first 500 chars): {text[:500]}")
    
    # Find positions of all labels
    label_positions = []
    for label in stats_order:
        # Create flexible pattern to match label variations (with optional trailing spaces, colon or semicolon)
        # Also try singular/plural variations for SPECIAL ATTACKS/DEFENSES
        patterns_to_try = [label]
        
        # Add singular variant if label ends with 'S'
        if label.endswith('S'):
            patterns_to_try.append(label[:-1])
        
        match = None
        for pattern_label in patterns_to_try:
            label_pattern = pattern_label.replace('/', r'\s*/\s*').replace(' ', r'\s+')
            pattern = rf'{label_pattern}\s*[:;]'
            
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                logger.debug(f"  Found label '{label}' (as '{pattern_label}') at position {match.start()}")
                break
        
        if match:
            label_positions.append((label, match.start(), match.end()))
        else:
            logger.debug(f"  Label '{label}' NOT FOUND")
    
    # Detect format by checking if first label is near the start of text
    if label_positions:
        first_label_pos = label_positions[0][1]
        # If first label is within first 50 chars (excluding header), it's format A (LABEL: VALUE)
        # Otherwise, it's format B (VALUE LABEL:)
        header_end = text.rfind('[^]')
        effective_start = header_end + 50 if header_end != -1 else 50
        
        is_format_a = first_label_pos < effective_start
        logger.debug(f"Format detection: first_label_pos={first_label_pos}, effective_start={effective_start}, is_format_a={is_format_a}")
        
        if is_format_a:
            # Format A: "LABEL: VALUE"  - value comes AFTER label
            logger.debug("Using Format A (LABEL: VALUE)")
            for i, (label, start_pos, end_pos) in enumerate(label_positions):
                if i < len(label_positions) - 1:
                    # Value is between current label and next label
                    value_end = label_positions[i+1][1]
                else:
                    # Last field: value extends to end markers
                    end_markers = ['PSIONICS SUMMARY', 'Combat:', 'Habitat', 'Ecology']
                    value_end = len(text)
                    for marker in end_markers:
                        marker_pos = text.find(marker, end_pos)
                        if marker_pos != -1 and marker_pos < value_end:
                            value_end = marker_pos
                
                value = text[end_pos:value_end].strip()
                raw_stats[label] = value
                logger.debug(f"  [{label}] = '{value[:50]}'")
        else:
            # Format B: "VALUE LABEL:" - value comes BEFORE label
            logger.debug("Using Format B (VALUE LABEL:)")
            for i, (label, start_pos, end_pos) in enumerate(label_positions):
                if i == 0:
                    # First field: skip header
                    value_start = 0
                    header_end = text[:start_pos].rfind('[^]')
                    if header_end != -1:
                        value_start = header_end + 3
                        # Skip monster name
                        while value_start < start_pos and not text[value_start].isalnum():
                            value_start += 1
                        while value_start < start_pos and text[value_start].isalnum():
                            value_start += 1
                else:
                    # Value is from end of previous label to current label
                    value_start = label_positions[i-1][2]
                
                value = text[value_start:start_pos].strip()
                raw_stats[label] = value
                logger.debug(f"  [{label}] = '{value[:50]}'")
    
    # Handle missing labels
    for label in stats_order:
        if label not in raw_stats:
            raw_stats[label] = ""
            logger.debug(f"  [{label}] = '' (label not found)")
    
    # STEP 2: Semantic value matching using VALID_VALUES
    # Instead of relying on label positions, search the entire text for valid values
    logger.debug(f"\n=== STEP 2: Semantic value matching ===")
    stats = {}
    used_text_ranges = []  # Track which parts of text we've already assigned
    
    # Build a searchable text corpus from all raw values
    all_text = " ".join([raw_stats.get(label, "") for label in stats_order])
    logger.debug(f"All text to parse: {all_text[:200]}")
    
    for label in stats_order:
        if label in VALID_VALUES:
            # Try to find a valid value for this field
            valid_values = VALID_VALUES[label]
            best_match = None
            best_match_pos = -1
            
            # Sort by length descending to prefer longer matches
            for valid_value in sorted(valid_values, key=len, reverse=True):
                # Look for this value in the text
                pos = all_text.find(valid_value)
                if pos != -1:
                    # Check if this text range hasn't been used yet
                    end_pos = pos + len(valid_value)
                    overlaps = any(start <= pos < end or start < end_pos <= end 
                                  for start, end in used_text_ranges)
                    if not overlaps:
                        best_match = valid_value
                        best_match_pos = pos
                        break
            
            if best_match:
                stats[label] = best_match
                used_text_ranges.append((best_match_pos, best_match_pos + len(best_match)))
                logger.debug(f"  [{label}] = '{best_match}' (semantic match)")
            else:
                # No valid value found, use raw extraction
                stats[label] = raw_stats.get(label, "")
                logger.debug(f"  [{label}] = '{stats[label][:30]}' (raw fallback)")
        else:
            # No valid values defined, use raw extraction
            stats[label] = raw_stats.get(label, "")
            if stats[label]:
                logger.debug(f"  [{label}] = '{stats[label][:30]}' (no valid values)")
            else:
                logger.debug(f"  [{label}] = '' (EMPTY - EXTRACTION FAILURE)")
    
    # Count non-empty values
    filled_count = sum(1 for v in stats.values() if v)
    empty_count = 21 - filled_count
    logger.debug(f"\n📊 Results: {filled_count}/21 filled, {empty_count}/21 empty")
    
    if empty_count > 0:
        logger.warning(f"⚠️  {empty_count} empty cells detected - parsing failure per spec!")
    
    return stats


def _extract_description_sections(html_fragment: str) -> Dict[str, str]:
    """
    Extract Combat, Habitat/Society, and Ecology description sections.
    
    Args:
        html_fragment: HTML containing the description sections
        
    Returns:
        Dict with keys 'combat', 'habitat', 'ecology' containing extracted text
    """
    sections = {}
    
    # Extract Combat section (starts with "Combat:" ends at "Habitat/Society:")
    combat_match = re.search(
        r'<span[^>]*>Combat:</span>(.*?)(?=<span[^>]*>Habitat/Society:</span>|$)',
        html_fragment,
        re.DOTALL | re.IGNORECASE
    )
    if combat_match:
        combat_html = combat_match.group(1)
        # Extract paragraphs
        paragraphs = re.findall(r'<span[^>]*>(.*?)</span>', combat_html, re.DOTALL)
        combat_text = ' '.join(_extract_plain_text(p) for p in paragraphs)
        sections['combat'] = combat_text
    else:
        sections['combat'] = ""
    
    # Extract Habitat/Society section
    habitat_match = re.search(
        r'<span[^>]*>Habitat/Society:</span>(.*?)(?=<span[^>]*>Ecology:</span>|$)',
        html_fragment,
        re.DOTALL | re.IGNORECASE
    )
    if habitat_match:
        habitat_html = habitat_match.group(1)
        paragraphs = re.findall(r'<span[^>]*>(.*?)</span>', habitat_html, re.DOTALL)
        habitat_text = ' '.join(_extract_plain_text(p) for p in paragraphs)
        sections['habitat'] = habitat_text
    else:
        sections['habitat'] = ""
    
    # Extract Ecology section
    ecology_match = re.search(
        r'<span[^>]*>Ecology:</span>(.*?)$',
        html_fragment,
        re.DOTALL | re.IGNORECASE
    )
    if ecology_match:
        ecology_html = ecology_match.group(1)
        paragraphs = re.findall(r'<span[^>]*>(.*?)</span>', ecology_html, re.DOTALL)
        ecology_text = ' '.join(_extract_plain_text(p) for p in paragraphs)
        sections['ecology'] = ecology_text
    else:
        sections['ecology'] = ""
    
    return sections


def _build_monster_stats_table(stats: Dict[str, str]) -> str:
    """
    Build HTML table for monster statistics (21 rows, PSIONICS not included).
    
    Args:
        stats: Dict mapping stat labels to values
        
    Returns:
        HTML table string
    """
    stats_order = [
        "CLIMATE/TERRAIN",
        "FREQUENCY",
        "ORGANIZATION",
        "ACTIVITY CYCLE",
        "DIET",
        "INTELLIGENCE",
        "TREASURE",
        "ALIGNMENT",
        "NO. APPEARING",
        "ARMOR CLASS",
        "MOVEMENT",
        "HIT DICE",
        "THAC0",
        "NO. OF ATTACKS",
        "DAMAGE/ATTACK",
        "SPECIAL ATTACKS",
        "SPECIAL DEFENSES",
        "MAGIC RESISTANCE",
        "SIZE",
        "MORALE",
        "XP VALUE"
    ]
    
    html = '<table class="monster-stats">\n'
    
    for label in stats_order:
        value = stats.get(label, "")
        html += '  <tr>\n'
        html += f'    <td class="stat-label"><strong>{label}:</strong></td>\n'
        html += f'    <td class="stat-value">{value}</td>\n'
        html += '  </tr>\n'
    
    html += '</table>\n'
    
    return html


def reconstruct_monster_page(html: str, monster_config: Dict) -> str:
    """
    Reconstruct a single monster manual page from scattered HTML.
    
    Args:
        html: Full chapter HTML
        monster_config: Configuration dict for the monster
        
    Returns:
        Updated HTML with reconstructed monster page
    """
    monster_name = monster_config['name']
    print(f"  🔍 Attempting to reconstruct: {monster_name}")
    logger.info(f"Reconstructing {monster_name} monster manual page")
    
    try:
        # Find the monster section boundaries
        if '<' in monster_config['id_pattern'] or '>' in monster_config['id_pattern']:
            # This is a full HTML pattern (e.g., '<p><span...>')
            print(f"    - Using full HTML pattern: {monster_config['id_pattern'][:50]}...")
            header_match = re.search(monster_config['id_pattern'], html)
        else:
            # This is just an ID, need to wrap it (e.g., 'header-\d+-belgoi')
            print(f"    - Using ID pattern: {monster_config['id_pattern']}")
            header_match = re.search(rf'<p id="{monster_config["id_pattern"]}">', html)
        
        if not header_match:
            print(f"    ❌ Could not find header for {monster_name}")
            logger.warning(f"Could not find {monster_name} header")
            return html
        
        print(f"    ✓ Found header at position {header_match.start()}")
        
        section_start = header_match.start()
        
        # Find section end (next monster or end marker)
        # Note: markers might have been reconstructed already, so check for both patterns
        print(f"    - Looking for end marker: {monster_config['next_marker'][:50]}...")
        next_match = re.search(monster_config['next_marker'], html[section_start + len(header_match.group(0)):])
        
        # If not found, try alternate patterns (reconstructed headers)
        if not next_match:
            if '<p id="header-' in monster_config['next_marker']:
                # Try reconstructed pattern: <h2 id="..."> instead of <p id="...">
                alt_pattern = monster_config['next_marker'].replace('<p id="', '<h2 id="')
                print(f"    - Trying alternate pattern 1: {alt_pattern[:50]}...")
                next_match = re.search(alt_pattern, html[section_start + len(header_match.group(0)):])
            elif '<p><span[^>]*><strong>' in monster_config['next_marker']:
                # Extract monster name from pattern like '<p><span[^>]*><strong>Jozhal</strong></span></p>'
                name_match = re.search(r'<strong>([^<]+)</strong>', monster_config['next_marker'])
                if name_match:
                    target_name = name_match.group(1)
                    # Generate slug like the reconstruction does
                    slug = target_name.lower().replace(' ', '-').replace(',', '').replace('(', '').replace(')', '')
                    alt_pattern = rf'<h2 id="monster-{slug}">'
                    print(f"    - Trying alternate pattern 2 for '{target_name}': {alt_pattern}...")
                    next_match = re.search(alt_pattern, html[section_start + len(header_match.group(0)):])
        
        if not next_match:
            print(f"    ❌ Could not find end marker for {monster_name}")
            logger.warning(f"Could not find end marker for {monster_name}")
            return html
        
        print(f"    ✓ Found end marker at relative position {next_match.start()}")
        section_end = section_start + len(header_match.group(0)) + next_match.start()
        section_html = html[section_start:section_end]
        print(f"    - Section length: {len(section_html)} chars")
        
        # Extract header ID if present
        header_id_match = re.search(r'id="([^"]+)"', header_match.group(0))
        if header_id_match:
            header_id = header_id_match.group(1)
            print(f"    - Using existing ID: {header_id}")
        else:
            # Generate a slug for monsters without IDs
            header_id = f"monster-{monster_name.lower().replace(' ', '-').replace(',', '').replace('(', '').replace(')', '')}"
            print(f"    - Generated new ID: {header_id}")
        
        # Find where the stat block ends (at description_start text)
        print(f"    - Looking for description start: '{monster_config['description_start'][:30]}...'")
        desc_start_match = re.search(
            rf'<[^>]+>{monster_config["description_start"]}',
            section_html
        )
        
        if desc_start_match:
            print(f"    ✓ Found description start at position {desc_start_match.start()}")
            stat_block_html = section_html[len(header_match.group(0)):desc_start_match.start()]
            description_html = section_html[desc_start_match.start():]
            print(f"    - Stat block: {len(stat_block_html)} chars, Description: {len(description_html)} chars")
        else:
            print(f"    ❌ Could not find description start for {monster_name}")
            logger.warning(f"Could not find description start for {monster_name}")
            stat_block_html = section_html[len(header_match.group(0)):]
            description_html = ""
        
        # Parse stat block
        print(f"    - Parsing stat block...")
        stats = _parse_stat_block(stat_block_html)
        print(f"    - Extracted {len([v for v in stats.values() if v])} stats with values")
        
        # Extract description sections
        print(f"    - Extracting description sections...")
        sections = _extract_description_sections(description_html)
        print(f"    - Found sections: {list(sections.keys())}")
        
        # Build reconstructed page
        print(f"    - Building reconstructed HTML...")
        reconstructed = f'<h2 id="{header_id}">{monster_name} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>\n\n'
        
        # Add stats table
        reconstructed += _build_monster_stats_table(stats)
        reconstructed += '\n'
        
        # Add psionics summary if present (for now, skip - will be Phase 2)
        # TODO: Extract and format psionics summary
        
        # Extract general description (text before "Combat:")
        desc_intro_match = re.search(
            rf'{monster_config["description_start"]}.*?(?=Combat:|$)',
            _extract_plain_text(description_html),
            re.DOTALL
        )
        if desc_intro_match:
            desc_intro = desc_intro_match.group(0).strip()
            if desc_intro:
                reconstructed += f'<p>{desc_intro}</p>\n\n'
        
        # Add description sections
        if sections.get('combat'):
            reconstructed += f'<p><strong>Combat:</strong> {sections["combat"]}</p>\n\n'
        
        if sections.get('habitat'):
            reconstructed += f'<p><strong>Habitat/Society:</strong> {sections["habitat"]}</p>\n\n'
        
        if sections.get('ecology'):
            reconstructed += f'<p><strong>Ecology:</strong> {sections["ecology"]}</p>\n\n'
        
        print(f"    - Reconstructed HTML length: {len(reconstructed)} chars")
        print(f"    - Replacing section from {section_start} to {section_end}")
        
        # Replace the section
        html = html[:section_start] + reconstructed + html[section_end:]
        
        print(f"    ✅ Successfully reconstructed {monster_name}")
        logger.info(f"✅ Successfully reconstructed {monster_name}")
        return html
        
    except Exception as e:
        logger.error(f"Failed to reconstruct {monster_name}: {e}", exc_info=True)
        return html


def reconstruct_all_monster_pages(html: str) -> str:
    """
    Reconstruct all monster manual pages in Chapter Five.
    
    Args:
        html: Full chapter HTML
        
    Returns:
        HTML with all monster pages reconstructed
    """
    print("=" * 80)
    print("!!! MONSTER RECONSTRUCTION CALLED !!!")
    print(f"Starting reconstruction for {len(MONSTERS)} monsters")
    print("=" * 80)
    logger.info("Reconstructing all monster manual pages")
    
    # Process monsters in reverse order to avoid position shifting issues
    # (later replacements don't affect earlier positions in the HTML)
    for i, monster_config in enumerate(reversed(MONSTERS), 1):
        print(f"\n>>> Processing monster {i}/{len(MONSTERS)}: {monster_config['name']} (REVERSE ORDER)")
        html = reconstruct_monster_page(html, monster_config)
    
    print("\n✅ Completed all monster reconstructions")
    logger.info("✅ Completed reconstruction of all monster manual pages")
    return html

