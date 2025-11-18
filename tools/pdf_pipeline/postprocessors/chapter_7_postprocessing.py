"""Chapter 7 (Magic) HTML postprocessing.

This module handles cleanup and formatting of Chapter 7 HTML after the main
transformation stage.
"""

import json
import logging
import re
from pathlib import Path
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def postprocess_chapter_7(html: str) -> str:
    """Apply Chapter 7-specific HTML postprocessing.
    
    Args:
        html: The rendered HTML content for Chapter 7
        
    Returns:
        The postprocessed HTML
    """
    logger.warning("===> POSTPROCESS_CHAPTER_7 CALLED <===")
    logger.info("Applying Chapter 7 HTML postprocessing")
    
    html = _remove_duplicate_tables(html)
    html = _fix_cosmos_spell_ordering(html)
    html = _fix_cosmos_sphere_paragraphs(html)
    html = _add_sphere_header_line_breaks(html)
    html = _remove_empty_spell_items(html)
    html = _fix_defiling_section_headers(html)
    html = _fix_trees_of_life_section(html)
    html = _fix_magic_items_section_headers(html)
    html = _build_armor_type_table(html)
    html = _build_metal_armor_table(html)
    
    # Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
    html = convert_all_styled_headers_to_semantic(html)
    
    return html


def _fix_cosmos_spell_ordering(html: str) -> str:
    """Fix the ordering of Sphere of the Cosmos spells that appear mixed in text.
    
    Due to PDF extraction issues, spells after "Animal Growth (5th)" are extracted
    as plain text mixed into paragraphs. This function:
    1. Extracts spell patterns from paragraph text
    2. Converts them to proper <li> elements
    3. Places them before the Wizardly Magic header
    """
    logger.warning("=== Starting _fix_cosmos_spell_ordering ===")
    try:
        # Find the Sphere of the Cosmos header
        cosmos_match = re.search(
            r'<p id="header-5-sphere-of-the-cosmos">',
            html
        )
        
        # Find the Wizardly Magic header
        wizardly_magic_match = re.search(
            r'<p id="header-6-wizardly-magic">',
            html
        )
        
        if not cosmos_match:
            logger.warning("Could not find Sphere of the Cosmos header")
            return html
        if not wizardly_magic_match:
            logger.warning("Could not find Wizardly Magic header")
            return html
        
        logger.warning(f"Found Cosmos header at pos {cosmos_match.start()}, Wizardly at pos {wizardly_magic_match.start()}")
        
        cosmos_pos = cosmos_match.end()
        wizardly_magic_pos = wizardly_magic_match.start()
        
        # Extract the section between Cosmos and Wizardly Magic
        cosmos_section = html[cosmos_pos:wizardly_magic_pos]
        after_wizardly_section = html[wizardly_magic_pos:]
        
        # Pattern to match spell names with levels embedded in text
        # Per [SPELL_FORMAT] rule: "spell_name (1st)", "spell_name (2nd)", "spell_name (3rd)", "spell_name (#th)"
        # Use negative lookbehind to avoid matching mid-spell (e.g., "Light Wounds" in "Cure Light Wounds")
        # Examples: "Animal Growth (5th)", "Commune With Nature (5th)", "Anti-Plant Shell (5th)"
        # Also handles Roman numerals: "Animal Summoning II (5th)", "Animal Summoning III (6th)"
        spell_pattern = r'(?:^|(?<=[^A-Za-z]))([A-Z][a-z]+(?:[\s\-\'&]+(?:or|and|of|with|to|from|the)?[\s\-\'&]*[A-Z][a-z]+|[\s\-\'&]*[IVX]+)*)\s+\(([567]th)\)'
        
        # Collect all spells from both the cosmos section and after wizardly magic
        extracted_spells = []
        
        # Function to extract spells from text while preserving non-spell content
        def extract_and_remove_spells(text):
            """Extract spells from text and return (cleaned_text, spells_list)."""
            spells_found = []
            
            # Find all spell matches
            for match in re.finditer(spell_pattern, text):
                spell_name = match.group(1).strip()
                spell_level = match.group(2)
                
                # Per [SPELL_FORMAT], spells are: "spell_name (level)"
                spell_with_level = f"{spell_name} ({spell_level})"
                
                # Get context to filter false positives
                start_pos = match.start()
                end_pos = match.end()
                context_before = text[max(0, start_pos-10):start_pos]
                context_after = text[end_pos:min(len(text), end_pos+20)]
                
                # Skip if lowercase letter immediately before (mid-word/sentence)
                if context_before and context_before[-1:].isalpha() and context_before[-1:].islower():
                    continue
                
                # Skip if followed by " level" (e.g., "magic (5th level)")
                if context_after.strip().startswith('level'):
                    continue
                
                # Skip common prose words that shouldn't be spell names
                # Also remove "Sphere" prefix if it got attached to spell name
                prose_prefixes = ['Those spells', 'These', 'All spells', 'Such spells', 'The']
                if any(spell_name.startswith(prefix) for prefix in prose_prefixes):
                    continue
                
                # Remove "Sphere " prefix if present (e.g., "Sphere Anti-Plant Shell" -> "Anti-Plant Shell")
                if spell_name.startswith('Sphere '):
                    spell_name = spell_name[7:]  # Remove "Sphere " (7 chars)
                    spell_with_level = f"{spell_name} ({spell_level})"
                
                # All other matches are valid spells per [SPELL_FORMAT]
                spells_found.append((spell_with_level, spell_name, spell_level, start_pos))
            
            # Remove spells from text (in reverse order to preserve positions)
            # We need to be careful to remove cleanly, replacing with a space
            for spell_with_level, spell_name, spell_level, start_pos in reversed(spells_found):
                # Find and replace the spell text
                if spell_with_level in text:
                    text = text.replace(spell_with_level, ' ', 1)
            
            return text, [(spell_with_level, spell_name, spell_level) for spell_with_level, spell_name, spell_level, _ in spells_found]
        
        # Do NOT check before Cosmos header - spells there belong to Fire/Water spheres
        # which legitimately appear before Cosmos in the document order
        before_cosmos_start = 0
        cleaned_before_cosmos = html[:cosmos_match.start()]
        before_spells = []
        
        # Extract spells from the cosmos section
        logger.warning(f"Cosmos section length: {len(cosmos_section)} chars")
        cleaned_cosmos, cosmos_spells = extract_and_remove_spells(cosmos_section)
        logger.warning(f"Found {len(cosmos_spells)} spells in cosmos section")
        extracted_spells.extend(cosmos_spells)
        
        # Extract spells from after wizardly magic (first 5000 chars to catch all misplaced cosmos spells)
        after_check_section = after_wizardly_section[:5000]
        logger.warning(f"After wizardly check section length: {len(after_check_section)} chars")
        cleaned_after_check, after_spells = extract_and_remove_spells(after_check_section)
        logger.warning(f"Found {len(after_spells)} spells in after-wizardly section")
        for spell_with_level, spell_name, spell_level in after_spells:
            logger.warning(f"  Misplaced spell AFTER Wizardly: {spell_name} ({spell_level})")
        extracted_spells.extend(after_spells)
        
        # Replace the checked portion of after_wizardly_section
        cleaned_after_wizardly = cleaned_after_check + after_wizardly_section[5000:]
        
        if not extracted_spells:
            logger.warning("No embedded cosmos spells found to extract")
            return html
        
        logger.warning(f"Extracted {len(extracted_spells)} embedded cosmos spells from paragraph text")
        logger.warning(f"  Before Cosmos: {len(before_spells)}")
        logger.warning(f"  Within Cosmos: {len(cosmos_spells)}")
        logger.warning(f"  After Wizardly: {len(after_spells)}")
        for spell_text, spell_name, spell_level in extracted_spells[:5]:
            logger.warning(f"  Example: {spell_name} ({spell_level})")
        
        # Update the JSON spell data file to include these extracted spells
        _update_spell_json_with_extracted_spells(extracted_spells)
        
        # Create <li> elements for extracted spells
        spell_items = []
        for full_match, spell_name, spell_level in extracted_spells:
            spell_items.append(f'<li class="spell-list-item">{spell_name} ({spell_level})</li>')
        
        # Wrap in <ul> tags
        spells_html = '<ul class="spell-list">\n' + '\n'.join(spell_items) + '\n</ul>\n'
        
        # Reconstruct HTML:
        # 1. Everything before the checked before-cosmos section
        # 2. Cleaned before-cosmos section
        # 3. Cosmos header
        # 4. Cleaned cosmos section
        # 5. Extracted spells as list items
        # 6. Cleaned after-wizardly section
        
        cosmos_header = html[cosmos_match.start():cosmos_match.end()]
        html = (
            html[:before_cosmos_start] +
            cleaned_before_cosmos +
            cosmos_header +
            cleaned_cosmos +
            spells_html +
            cleaned_after_wizardly
        )
        
        logger.warning(f"Created {len(spell_items)} spell list items from embedded text")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to fix cosmos spell ordering: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _fix_cosmos_sphere_paragraphs(html: str) -> str:
    """Fix the Sphere of the Cosmos section to properly separate prose paragraphs from spell lists.
    
    Due to the 2-column layout, two descriptive paragraphs:
    - "Clerics have major access to the sphere of the element they worship..."
    - "There are no deities in Dark Sun..."
    
    are mixed into the spell list. This function extracts these paragraphs and places
    them cleanly after the spell list but before the Wizardly Magic section.
    """
    try:
        # Find the Wizardly Magic header to determine where to insert the paragraphs
        wizardly_magic_match = re.search(
            r'<p id="header-6-wizardly-magic">',
            html
        )
        
        if not wizardly_magic_match:
            logger.warning("Could not find Wizardly Magic header, skipping cosmos paragraph fix")
            return html
        
        wizardly_magic_pos = wizardly_magic_match.start()
        
        # Extract the section between Sphere of the Cosmos header and Wizardly Magic
        cosmos_match = re.search(
            r'<p id="header-5-sphere-of-the-cosmos">',
            html
        )
        
        if not cosmos_match:
            logger.warning("Could not find Sphere of the Cosmos header, skipping paragraph fix")
            return html
        
        cosmos_section = html[cosmos_match.end():wizardly_magic_pos]
        
        # Try to find fragmented paragraphs first (old format)
        clerics_fragments = [
            r'<p>Clerics have major access to the sphere of the ele-</p>',
            r'<p>ment they worship, plus minor access to the Sphere</p>',
            r'<p>of the Cosmos\. Templars have major access to all spheres, but gain spells more slowly\.</p>'
        ]
        
        clerics_matches = []
        for fragment in clerics_fragments:
            match = re.search(fragment, html)
            if match:
                clerics_matches.append(match)
        
        deities_fragments = [
            r'<p>There are no deities in Dark Sun\. Those spells</p>',
            r'<p>that indicate some contact with a deity instead reflect contact with a powerful being of the elemental</p>',
            r'<p>planes\.</p>'
        ]
        
        deities_matches = []
        for fragment in deities_fragments:
            match = re.search(fragment, html)
            if match:
                deities_matches.append(match)
        
        # Try to find complete paragraphs (new format with extra whitespace)
        # These patterns use \s+ to match any amount of whitespace between words
        clerics_complete_pattern = r'<p>Clerics\s+have\s+major\s+access\s+to\s+the\s+sphere\s+of\s+the\s+ele\s+ment\s+they\s+worship,\s+plus\s+minor\s+access\s+to\s+the\s+Sphere\s+of\s+the\s+Cosmos\.\s+Templars\s+have\s+major\s+access\s+to\s+all\s+spheres,\s+but\s+gain\s+spells\s+more\s+slowly\.</p>'
        deities_complete_pattern = r'<p>\s*There\s+are\s+no\s+deities\s+in\s+Dark\s+Sun\.\s+Those\s+spells\s+that\s+indicate\s+some\s+contact\s+with\s+a\s+deity\s+instead\s+reflect\s+contact\s+with\s+a\s+powerful\s+being\s+of\s+the\s+elemental\s+planes\.</p>'
        
        clerics_complete_match = re.search(clerics_complete_pattern, html)
        deities_complete_match = re.search(deities_complete_pattern, html)
        
        # Determine which format we found
        if clerics_complete_match or deities_complete_match:
            logger.info("Found complete paragraphs embedded in spell list")
            # Add complete paragraph matches to the removal list
            if clerics_complete_match:
                clerics_matches.append(clerics_complete_match)
            if deities_complete_match:
                deities_matches.append(deities_complete_match)
        
        if len(clerics_matches) == 0 and len(deities_matches) == 0:
            logger.info("Cosmos sphere paragraphs appear to be correctly formatted")
            return html
        
        # Extract the full paragraph texts (normalized without extra whitespace)
        clerics_text = "Clerics have major access to the sphere of the element they worship, plus minor access to the Sphere of the Cosmos. Templars have major access to all spheres, but gain spells more slowly."
        deities_text = "There are no deities in Dark Sun. Those spells that indicate some contact with a deity instead reflect contact with a powerful being of the elemental planes."
        
        # Remove the paragraphs from their current locations (in reverse order to preserve positions)
        all_matches = clerics_matches + deities_matches
        all_matches.sort(key=lambda m: m.start(), reverse=True)
        
        logger.info(f"Removing {len(all_matches)} paragraph fragments/complete paragraphs from spell list")
        
        for match in all_matches:
            html = html[:match.start()] + html[match.end():]
        
        # Also remove any empty <p> tags that might be left behind
        html = re.sub(r'<p>\s*</p>', '', html)
        
        # Recalculate wizardly_magic_pos after all removals
        wizardly_magic_match = re.search(r'<p id="header-6-wizardly-magic">', html)
        wizardly_magic_pos = wizardly_magic_match.start() if wizardly_magic_match else len(html)
        
        # Create properly formatted paragraphs (without extra whitespace)
        formatted_paragraphs = f"\n<p>{clerics_text}</p>\n<p>{deities_text}</p>\n"
        
        # Insert the paragraphs before Wizardly Magic
        html = html[:wizardly_magic_pos] + formatted_paragraphs + html[wizardly_magic_pos:]
        
        logger.info("Fixed Sphere of the Cosmos paragraphs - separated from spell list")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to fix cosmos sphere paragraphs: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _remove_duplicate_tables(html: str) -> str:
    """Remove consecutive duplicate table elements.
    
    The raw PDF extraction for Chapter 7 creates many duplicate table structures
    that appear consecutively in the HTML. This function identifies and removes
    consecutive duplicates, keeping only the first occurrence.
    """
    try:
        # Find all <table>...</table> elements
        table_pattern = r'<table[^>]*>.*?</table>'
        tables = list(re.finditer(table_pattern, html, re.DOTALL))
        
        if len(tables) < 2:
            return html
        
        logger.debug(f"Found {len(tables)} tables total in Chapter 7")
        
        # Track which tables to remove (by their match object)
        tables_to_remove = []
        prev_table_content = None
        duplicate_count = 0
        
        for i, table_match in enumerate(tables):
            table_content = table_match.group(0)
            
            # Check if this table is identical to the previous one
            if prev_table_content and table_content == prev_table_content:
                tables_to_remove.append(table_match)
                duplicate_count += 1
            else:
                prev_table_content = table_content
        
        if not tables_to_remove:
            logger.debug("No duplicate tables found in Chapter 7")
            return html
        
        logger.info(f"Removing {duplicate_count} duplicate tables from Chapter 7")
        
        # Remove duplicates in reverse order to preserve positions
        for table_match in reversed(tables_to_remove):
            html = html[:table_match.start()] + html[table_match.end():]
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to remove duplicate tables: {e}")
        return html


def _update_spell_json_with_extracted_spells(extracted_spells):
    """Update the spell JSON file with spells extracted from embedded text.
    
    Args:
        extracted_spells: List of tuples (spell_with_level, spell_name, spell_level)
    """
    try:
        spell_json_path = Path("data/processed/chapter-seven-spells.json")
        
        if not spell_json_path.exists():
            logger.warning(f"Spell JSON file not found at {spell_json_path}, cannot update")
            return
        
        # Load existing spell data
        with open(spell_json_path, 'r', encoding='utf-8') as f:
            spell_data = json.load(f)
        
        # Create a set of all spells from ALL spheres to detect cross-sphere duplicates
        all_spell_keys = set()
        for sphere_name, sphere_spells in spell_data["spheres"].items():
            for spell in sphere_spells:
                all_spell_keys.add((spell["name"], spell["level"]))
        
        # Add extracted spells to Sphere of the Cosmos
        cosmos_spells = spell_data["spheres"]["Sphere of the Cosmos"]
        existing_cosmos_keys = {(s["name"], s["level"]) for s in cosmos_spells}
        
        added_count = 0
        skipped_count = 0
        for spell_with_level, spell_name, spell_level in extracted_spells:
            # Skip if already in Cosmos
            if (spell_name, spell_level) in existing_cosmos_keys:
                continue
            
            # Skip if this spell exists in ANY other sphere (belongs elsewhere)
            if (spell_name, spell_level) in all_spell_keys:
                logger.warning(f"  SKIP: {spell_name} ({spell_level}) - already exists in another sphere")
                skipped_count += 1
                continue
            
            # Add the spell (only if not in any sphere)
            cosmos_spells.append({
                "name": spell_name,
                "level": spell_level,
                "sphere": "Sphere of the Cosmos",
                "page": -1,  # Unknown page, extracted from HTML
                "block": -1  # Unknown block, extracted from HTML
            })
            existing_cosmos_keys.add((spell_name, spell_level))
            all_spell_keys.add((spell_name, spell_level))
            added_count += 1
        
        # Update metadata
        spell_data["metadata"]["total_spells"] = sum(
            len(spells) for spells in spell_data["spheres"].values()
        )
        
        # Save updated spell data
        with open(spell_json_path, 'w', encoding='utf-8') as f:
            json.dump(spell_data, f, indent=2, ensure_ascii=False)
        
        logger.warning(f"Updated spell JSON: added {added_count} new spells, skipped {skipped_count} duplicates")
        logger.warning(f"Total Cosmos spells now: {len(cosmos_spells)}")
        
    except Exception as e:
        logger.error(f"Failed to update spell JSON: {e}")
        import traceback
        logger.error(traceback.format_exc())


def _add_sphere_header_line_breaks(html: str) -> str:
    """Add line breaks above Sphere of Air, Fire, Water, and Cosmos headers.
    
    Inserts <br> tags before these sphere headers to visually separate them from
    the preceding spell lists. Sphere of Earth is not included as it immediately
    follows the Priestly Magic header.
    """
    try:
        # Define sphere headers that need line breaks (not Earth as it's the first)
        sphere_headers = [
            ('header-2-sphere-of-air', 'Sphere of Air'),
            ('header-3-sphere-of-fire', 'Sphere of Fire'),
            ('header-4-sphere-of-water', 'Sphere of Water'),
            ('header-5-sphere-of-the-cosmos', 'Sphere of the Cosmos')
        ]
        
        modified_count = 0
        
        for header_id, header_name in sphere_headers:
            # Pattern to match the sphere header paragraph
            # Example: <p id="header-2-sphere-of-air"> <a href="#top"...>[^]</a> <span class="header-h3"...>Sphere of Air</span></p>
            pattern = rf'(<p id="{header_id}">)'
            
            # Check if pattern exists and doesn't already have a <br> before it
            if re.search(pattern, html):
                # Check if there's already a <br> immediately before this header
                check_pattern = rf'<br>\s*<p id="{header_id}">'
                if not re.search(check_pattern, html):
                    # Add <br> before the header
                    html = re.sub(pattern, r'<br>\n\1', html)
                    modified_count += 1
                    logger.debug(f"Added line break before {header_name}")
        
        if modified_count > 0:
            logger.info(f"Added {modified_count} line breaks before sphere headers")
        else:
            logger.debug("No line breaks needed for sphere headers (already present or headers not found)")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to add sphere header line breaks: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _remove_empty_spell_items(html: str) -> str:
    """Remove empty spell list items from the HTML.
    
    Sometimes the extraction creates empty <li> elements with only whitespace.
    This function removes them to keep the spell lists clean.
    """
    try:
        # Pattern to match empty spell list items (with only whitespace)
        empty_item_pattern = r'<ul class="spell-list"><li class="spell-list-item">\s*</li></ul>'
        
        # Count how many we're removing
        count_before = len(re.findall(empty_item_pattern, html))
        
        # Remove empty spell list items
        html = re.sub(empty_item_pattern, '', html)
        
        if count_before > 0:
            logger.info(f"Removed {count_before} empty spell list items")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to remove empty spell items: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _fix_defiling_section_headers(html: str) -> str:
    """Fix the defiling section headers and paragraph breaks.
    
    This function:
    1. Converts "Casting Multiple Spells from the Same Location:" to H3
    2. Ensures "If a defiler casts more" starts a new paragraph
    3. Ensures "For example, the defiler Grifyan" starts a new paragraph
    4. Converts "Effects on Living Creatures:" from H1 to H3
    """
    try:
        # Fix 1: Convert "Casting Multiple Spells from the Same Location:" to H3
        # Currently it's: <p><span style="color: #ca5804">Casting Multiple Spells from the Same Location:</span> If a defiler casts more...
        # Need to make it: <p id="..."> <a href="#top">[^]</a> <span class="header-h3" ...>Casting Multiple Spells...</span></p><p>If a defiler...
        
        casting_pattern = r'<p><span style="color: #ca5804">Casting Multiple Spells from the Same Location:</span>\s*If a defiler casts more'
        
        if re.search(casting_pattern, html):
            # Find the next available header ID by counting existing headers
            header_matches = re.findall(r'id="header-(\d+)-', html)
            if header_matches:
                next_header_num = max(int(m) for m in header_matches) + 1
            else:
                next_header_num = 100  # Fallback
            
            header_id = f"header-{next_header_num}-casting-multiple-spells-from-the-same-location"
            
            # Replace the pattern with proper H3 header + new paragraph
            replacement = (
                f'<p id="{header_id}"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
                f'<span class="header-h3" style="color: #ca5804; font-size: 0.8em">Casting Multiple Spells from the Same Location:</span></p>'
                f'<p>If a defiler casts more'
            )
            
            html = re.sub(casting_pattern, replacement, html)
            logger.info("Converted 'Casting Multiple Spells from the Same Location:' to H3 header")
        
        # Fix 2: Ensure "For example, the defiler Grifyan" starts a new paragraph
        # Look for patterns where this text is in the middle of a paragraph without a <p> tag before it
        example_pattern = r'(\(Spells equal to the highest level spell are treated as additional spells\)\.\s*)For example, the defiler Grifyan'
        
        if re.search(example_pattern, html):
            replacement = r'\1</p><p>For example, the defiler Grifyan'
            html = re.sub(example_pattern, replacement, html)
            logger.info("Ensured 'For example, the defiler Grifyan' starts a new paragraph")
        
        # Fix 3: Convert "Effects on Living Creatures:" from H1 to H3
        # Currently it has a roman numeral like "III." which indicates H1
        # Pattern: <p id="header-10-effects-on-living-creatures">III.  <a href="#top"...>[^]</a> <span style="color: #ca5804">Effects on Living Creatures:</span></p>
        # Need: <p id="header-10-effects-on-living-creatures"> <a href="#top"...>[^]</a> <span class="header-h3" style="color: #ca5804; font-size: 0.8em">Effects on Living Creatures:</span></p>
        
        # More flexible pattern that handles potential HTML entity encoding
        effects_pattern = r'(<p id="header-\d+-effects-on-living-creatures">)[IVX]+\.\s+(<a href="#top"[^>]*>\[.?\]</a>)\s+<span style="color: #ca5804">Effects on Living Creatures:</span>'
        
        if re.search(effects_pattern, html):
            replacement = r'\1 \2 <span class="header-h3" style="color: #ca5804; font-size: 0.8em">Effects on Living Creatures:</span>'
            html = re.sub(effects_pattern, replacement, html)
            logger.info("Converted 'Effects on Living Creatures:' from H1 to H3")
        else:
            logger.warning("Could not find 'Effects on Living Creatures:' pattern to convert to H3")
        
        # Fix 4: Remove extraneous line break in "the radius of destroyed vegetation expands around him"
        # Pattern: </p><p>around him
        # Need to merge these into one continuous sentence
        line_break_pattern = r'the radius of destroyed vegetation expands</p>\s*<p>around him'
        
        if re.search(line_break_pattern, html):
            replacement = r'the radius of destroyed vegetation expands around him'
            html = re.sub(line_break_pattern, replacement, html)
            logger.info("Removed extraneous line break in 'expands around him' sentence")
        
        # Fix 5: Remove extraneous line break in ",a 5th-level spell. Since this is the highest-level"
        # These should be a single paragraph
        spell_level_pattern = r',a 5th-level spell\.</p>\s*<p>Since this is the highest-level'
        
        if re.search(spell_level_pattern, html):
            replacement = r',a 5th-level spell. Since this is the highest-level'
            html = re.sub(spell_level_pattern, replacement, html)
            logger.info("Removed extraneous line break in '5th-level spell. Since' sentence")
        
        # Fix 6: Convert "Ash:" from H1 to H3
        # Pattern: <p id="header-11-ash">IV.  <a href="#top"...>[^]</a> <span style="color: #ca5804">Ash:</span></p>
        # Need: <p id="header-11-ash"> <a href="#top"...>[^]</a> <span class="header-h3" style="color: #ca5804; font-size: 0.8em">Ash:</span></p>
        
        ash_pattern = r'(<p id="header-\d+-ash">)[IVX]+\.\s+(<a href="#top"[^>]*>\[.?\]</a>)\s+<span style="color: #ca5804">Ash:</span>'
        
        if re.search(ash_pattern, html):
            replacement = r'\1 \2 <span class="header-h3" style="color: #ca5804; font-size: 0.8em">Ash:</span>'
            html = re.sub(ash_pattern, replacement, html)
            logger.info("Converted 'Ash:' from H1 to H3")
        else:
            logger.warning("Could not find 'Ash:' pattern to convert to H3")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to fix defiling section headers: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _fix_trees_of_life_section(html: str) -> str:
    """Fix the Trees of Life section formatting.
    
    This function:
    1. Splits the intro paragraph at "tree of life is, in essence, a living magical item"
    2. Converts "Special Powers:" from H1 to H2
    3. Extracts "Destroying a Tree of Life:" from inline text and makes it H2
    4. Converts "Regeneration:" from H1 to H2
    5. Removes corrupt table data mixed into the paragraphs
    """
    try:
        # Find the Trees of Life section
        trees_header_match = re.search(r'<p id="header-12-trees-of-life">', html)
        if not trees_header_match:
            logger.warning("Could not find Trees of Life header")
            return html
        
        # Find the next major section (Magical Items)
        next_section_match = re.search(r'<p id="header-15-magical-items">', html)
        if not next_section_match:
            logger.warning("Could not find Magical Items header")
            return html
        
        # Extract sections
        before_trees = html[:trees_header_match.start()]
        section = html[trees_header_match.start():next_section_match.start()]
        after_section = html[next_section_match.start():]
        
        # Fix 1: Split the intro paragraph at "tree of life is, in essence, a living magical item"
        # Pattern: Find the paragraph containing this phrase and split it
        # The text is: "A tree of life is, in essence, a living magical item. It stores and channels energies from all four elemental planes..."
        intro_split_pattern = r'(<p>A\s*tree\s+of\s*life\s*is.*?tree\s+of\s+life\s*is,\s+in\s+essence,\s+a\s+living\s+magical\s+item\.)(\s+It\s+stores.*?)</p>'
        intro_match = re.search(intro_split_pattern, section, re.DOTALL)
        
        if intro_match:
            first_part = intro_match.group(1)
            second_part = intro_match.group(2).strip()
            
            # Remove the old paragraph and replace with two paragraphs
            section = section[:intro_match.start()] + \
                     first_part + '</p>\n<p>' + second_part + '</p>' + \
                     section[intro_match.end():]
            logger.info("Split Trees of Life intro paragraph at 'living magical item'")
        else:
            logger.warning("Could not find intro paragraph pattern to split")
        
        # Fix 2: Convert "Special Powers:" from H1 to H2 (if not already H2)
        # Pattern: <p id="header-13-special-powers"> <a href="#top"...>[^]</a> <span style="color: #ca5804">Special Powers:</span></p>
        # OR: <p id="header-13-special-powers">VI.  <a href="#top"...>[^]</a> <span style="color: #ca5804">Special Powers:</span></p>
        # Need: <p id="header-13-special-powers"> <a href="#top"...>[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Special Powers:</span></p>
        
        # Check if it's already H2 (has header-h2 class)
        if '<p id="header-13-special-powers">' in section and 'class="header-h2"' not in section:
            # Remove the roman numeral if present
            special_powers_pattern = r'(<p id="header-13-special-powers">)([IVX]+\.\s+)?(<a href="#top"[^>]*>\[.?\]</a>)\s+<span style="color: #ca5804">Special Powers:</span>'
            
            if re.search(special_powers_pattern, section):
                replacement = r'\1 \3 <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Special Powers:</span>'
                section = re.sub(special_powers_pattern, replacement, section)
                logger.info("Converted 'Special Powers:' from H1 to H2 (removed roman numeral)")
        else:
            logger.info("'Special Powers:' is already H2 or not found")
        
        # Fix 3: Extract "Destroying a Tree of Life:" from inline text and make it H2
        # Currently it's embedded as: <span style="color: #ca5804">Destroying a</span><span style="color: #ca5804">Tree of Life:</span>Atree of lifehas two
        # Note: text may have spacing issues like "Atree" instead of "A tree" and "lifehas" instead of "life has"
        # Need to: Extract it, create a proper H2 header, and start a new paragraph with "A tree of life has two"
        # More flexible pattern that handles concatenated words
        destroying_inline_pattern = r'<span style="color: #ca5804">Destroying a</span>\s*<span style="color: #ca5804">Tree of Life:</span>\s*A\s*tree\s*of\s*life\s*has\s*two'
        destroying_inline_pattern_no_spaces = r'<span style="color: #ca5804">Destroying a</span>\s*<span style="color: #ca5804">Tree of Life:</span>Atreeof\s*life(?:has|)\s*two'
        
        if re.search(destroying_inline_pattern, section):
            # Create the H2 header
            destroying_header = '<p id="header-13a-destroying-a-tree-of-life"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Destroying a Tree of Life:</span></p>'
            
            # Replace the inline span with the header and new paragraph
            replacement = destroying_header + '\n<p>A tree of life has two'
            section = re.sub(destroying_inline_pattern, replacement, section)
            logger.info("Extracted 'Destroying a Tree of Life:' as H2 header (spaced version)")
        elif re.search(destroying_inline_pattern_no_spaces, section):
            # Handle the case with concatenated words
            destroying_header = '<p id="header-13a-destroying-a-tree-of-life"> <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Destroying a Tree of Life:</span></p>'
            
            # Replace the inline span with the header and new paragraph
            replacement = destroying_header + '\n<p>A tree of life has two'
            section = re.sub(destroying_inline_pattern_no_spaces, replacement, section)
            logger.info("Extracted 'Destroying a Tree of Life:' as H2 header (concatenated version)")
        else:
            logger.warning("Could not find 'Destroying a Tree of Life:' inline pattern to extract")
        
        # Fix 3b: Merge "A tree of life has two" and "distinct parts:" paragraphs
        # These appear as separate paragraphs but should be merged
        # Pattern: <p>A tree of life has two</p><p>distinct parts:
        # Or: <p>Atree of lifehas two</p><p>distinct parts:
        merge_two_distinct_pattern1 = r'<p>A tree of life has two</p>\s*<p>distinct parts:'
        merge_two_distinct_pattern2 = r'<p>Atree\s*of\s*life\s*has\s*two</p>\s*<p>distinct parts:'
        
        if re.search(merge_two_distinct_pattern1, section):
            section = re.sub(merge_two_distinct_pattern1, '<p>A tree of life has two distinct parts:', section)
            logger.info("Merged 'A tree of life has two' with 'distinct parts:' paragraph (spaced version)")
        elif re.search(merge_two_distinct_pattern2, section):
            section = re.sub(merge_two_distinct_pattern2, '<p>A tree of life has two distinct parts:', section)
            logger.info("Merged 'A tree of life has two' with 'distinct parts:' paragraph (concatenated version)")
        
        # Fix 3c: Ensure proper paragraph breaks in "Destroying a Tree of Life" section
        # The section should have paragraphs starting at:
        # 1. "A tree of life has two distinct parts..." (already handled above)
        # 2. "Destroying the tree's life force is much more difficult..."
        # 3. "Defiler magic also affects a tree's life force..."
        # 4. "The life force of a tree of life is completely snuffed..."
        
        # Find where we need to insert paragraph breaks
        # Pattern: Look for sentences that should start new paragraphs but are currently mid-paragraph
        
        # Break before "Destroying the tree's life force"
        destroying_force_pattern = r'(\.\s+)Destroying the tree'
        if re.search(destroying_force_pattern, section):
            section = re.sub(destroying_force_pattern, r'.</p>\n<p>Destroying the tree', section)
            logger.info("Inserted paragraph break before 'Destroying the tree's life force'")
        
        # Break before "Defiler magic also affects"
        defiler_affects_pattern = r'(\.\s+)Defiler magic also affects'
        if re.search(defiler_affects_pattern, section):
            section = re.sub(defiler_affects_pattern, r'.</p>\n<p>Defiler magic also affects', section)
            logger.info("Inserted paragraph break before 'Defiler magic also affects'")
        
        # Break before "The life force of a tree of life is completely"
        # The pattern should match variations with or without spaces in "tree of life"
        life_force_snuffed_pattern = r'(\.\s+)The life force of a\s*tree\s*of\s*life\s*is completely'
        if re.search(life_force_snuffed_pattern, section):
            section = re.sub(life_force_snuffed_pattern, r'.</p>\n<p>The life force of a tree of life is completely', section)
            logger.info("Inserted paragraph break before 'The life force of a tree of life is completely'")
        
        # Fix 4: Convert "Regeneration:" from H1 to H2 (if not already H2)
        # Pattern: <p id="header-14-regeneration">VII.  <a href="#top"...>[^]</a> <span style="color: #ca5804">Regeneration:</span></p>
        # Need: <p id="header-14-regeneration"> <a href="#top"...>[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Regeneration:</span></p>
        
        # Check if the Regeneration header exists and if it's already H2
        regeneration_header_pattern = r'<p id="header-14-regeneration">.*?</p>'
        regeneration_header_match = re.search(regeneration_header_pattern, section, re.DOTALL)
        
        if regeneration_header_match:
            regeneration_header_text = regeneration_header_match.group(0)
            
            # Check if it's already H2 (has header-h2 class in THIS specific header)
            if 'class="header-h2"' not in regeneration_header_text:
                regeneration_pattern = r'(<p id="header-14-regeneration">)([IVX]+\.\s+)?(<a href="#top"[^>]*>\[.?\]</a>)\s+<span style="color: #ca5804">Regeneration:</span>'
                
                if re.search(regeneration_pattern, section):
                    replacement = r'\1 \3 <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Regeneration:</span>'
                    section = re.sub(regeneration_pattern, replacement, section)
                    logger.info("Converted 'Regeneration:' from H1 to H2 (removed roman numeral)")
                else:
                    logger.warning("Found Regeneration header but pattern didn't match")
            else:
                logger.info("'Regeneration:' is already H2")
        else:
            logger.warning("Could not find 'Regeneration:' header")
        
        # Fix 4b: Split the Regeneration paragraph at "The life force of a tree of life regenerates"
        # Pattern: ...in four weeks. The life force of atree of liferegenerates...
        # Need: ...in four weeks.</p><p>The life force of a tree of life regenerates...
        regen_split_pattern = r'(in four weeks\.\s*)The life force of a\s*tree\s*of\s*life\s*regenerates'
        
        if re.search(regen_split_pattern, section):
            replacement = r'\1</p>\n<p>The life force of a tree of life regenerates'
            section = re.sub(regen_split_pattern, replacement, section)
            logger.info("Split Regeneration paragraph at 'The life force of a tree of life regenerates'")
        else:
            logger.warning("Could not find pattern to split Regeneration paragraph at 'The life force'")
        
        # Fix 5: Remove corrupt table data
        # These tables contain armor type data that doesn't belong in the Trees of Life section
        # Pattern 1: Tables with "Hide Leather", "Padded", etc.
        corrupt_table_pattern1 = r'<table class="ds-table"><tr><td>nally created by wizards.*?</table>'
        section = re.sub(corrupt_table_pattern1, '', section, flags=re.DOTALL)
        
        corrupt_table_pattern2 = r'<table class="ds-table"><tr><td>their defiling spells.*?</table>'
        section = re.sub(corrupt_table_pattern2, '', section, flags=re.DOTALL)
        
        corrupt_table_pattern3 = r'<table class="ds-table"><tr><td>tained\. Thus, defilers.*?</table>'
        section = re.sub(corrupt_table_pattern3, '', section, flags=re.DOTALL)
        
        corrupt_table_pattern4 = r'<table class="ds-table"><tr><td>desperate measure.*?</table>'
        section = re.sub(corrupt_table_pattern4, '', section, flags=re.DOTALL)
        
        logger.info("Removed corrupt table data from Trees of Life section")
        
        # Fix 6: Clean up the "Trees of life in the World of Athas" section
        # The text is fragmented across multiple paragraphs and needs to be merged
        # Expected text: "Though originally created by wizards to combat the destruction of nature, 
        # trees of life are now heavily exploited by defilers, who use the trees' powerful life forces 
        # to charge their defiling spells. Sorcerer-kings often have large gardens within their cities, 
        # even within their palaces, where groves of trees of life are tended and maintained. Thus, 
        # defilers can exercise evil magic from their citadels without decimating the cities below—
        # a desperate measure to keep their tiny verdant belts as plentiful as possible."
        
        # Define the complete paragraphs we want to insert
        para1 = "Though originally created by wizards to combat the destruction of nature, trees of life are now heavily exploited by defilers, who use the trees' powerful life forces to charge their defiling spells."
        para2 = "Sorcerer-kings often have large gardens within their cities, even within their palaces, where groves of trees of life are tended and maintained. Thus, defilers can exercise evil magic from their citadels without decimating the cities below—a desperate measure to keep their tiny verdant belts as plentiful as possible."
        
        # Step 1: Remove the "Though origi-" fragment from the end of Regeneration paragraph
        athas_fragment_end_pattern = r'Trees\s*of\s*life\s*in\s+the\s+World\s+of\s+Athas:\s+Though\s+origi-</p>'
        if re.search(athas_fragment_end_pattern, section):
            section = re.sub(athas_fragment_end_pattern, '</p>', section)
            logger.info("Removed 'Though origi-' fragment")
        
        # Step 2: Remove any fragmented paragraphs that start with "nally created"
        fragment_nally_pattern = r'<p>nally\s+created.*?</p>'
        if re.search(fragment_nally_pattern, section, re.DOTALL):
            section = re.sub(fragment_nally_pattern, '', section, flags=re.DOTALL)
            logger.info("Removed 'nally created' fragment")
        
        # Step 3: Remove fragmented paragraph about "their defiling spells"
        fragment_their_pattern = r'<p>their\s+defiling\s+spells.*?verdant\s+belts\s+as</p>'
        if re.search(fragment_their_pattern, section, re.DOTALL):
            section = re.sub(fragment_their_pattern, '', section, flags=re.DOTALL)
            logger.info("Removed 'their defiling spells' fragment")
        
        # Step 4: Remove orphaned "plentiful as possible." fragment
        plentiful_pattern = r'<p>\s*plentiful\s+as\s+possible\.\s*</p>'
        if re.search(plentiful_pattern, section):
            section = re.sub(plentiful_pattern, '', section)
            logger.info("Removed 'plentiful as possible' fragment")
        
        # Step 5: Check if complete paragraphs already exist, if not insert them
        if "Though originally created by wizards" not in section:
            # The Magical Items header is in 'after_section', not in 'section'
            # So we need to append the paragraphs to the end of 'section'
            section = section + f'\n<p>{para1}</p>\n<p>{para2}</p>\n'
            logger.info("Inserted complete 'Trees of life in the World of Athas' paragraphs at end of section")
        else:
            logger.info("Complete 'Trees of life in the World of Athas' paragraphs already exist")
        
        logger.info("Completed 'Trees of life in the World of Athas' section cleanup")
        
        # Reconstruct the HTML
        html = before_trees + section + after_section
        
        logger.info("Completed Trees of Life section fixes")
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to fix Trees of Life section: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _fix_magic_items_section_headers(html: str) -> str:
    """Fix the Magic Items section headers to be H2 instead of H1.
    
    This function:
    1. Merges "Rings, Rods, Staves, Wands, and Miscellaneous" and "Magic:" into a single header
    2. Converts the following headers from H1 (with roman numerals) to H2:
       - "Potions and Oils:"
       - "Scrolls:"
       - "Rings, Rods, Staves, Wands, and Miscellaneous Magic:"
       - "ARMOR TYPE"
       - "METAL ARMOR"
       - "Weapons:"
    
    These are subsections under the "Magical Items" H1 header, so they should be H2.
    """
    try:
        # First, merge "Rings, Rods, Staves, Wands, and Miscellaneous" and "Magic:" headers
        # These may be either already H2 (from previous conversion) or still H1 (with roman numerals)
        
        # Pattern 1: Both already H2
        merge_pattern_h2 = (
            r'<p id="header-18-rings-rods-staves-wands-and-miscellaneous">.*?'
            r'<span class="header-h2"[^>]*>Rings, Rods, Staves, Wands, and Miscellaneous</span></p>'
            r'<p id="header-19-magic">.*?<span class="header-h2"[^>]*>Magic:</span></p>'
        )
        
        # Pattern 2: Both still H1 (with roman numerals)
        merge_pattern_h1 = (
            r'<p id="header-18-rings-rods-staves-wands-and-miscellaneous">[IVX]+\.\s+.*?'
            r'<span style="color: #ca5804">Rings, Rods, Staves, Wands, and Miscellaneous</span></p>'
            r'<p id="header-19-magic">[IVX]+\.\s+.*?<span style="color: #ca5804">Magic:</span></p>'
        )
        
        merged_header = (
            '<p id="header-18-rings-rods-staves-wands-and-miscellaneous"> '
            '<a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
            '<span class="header-h2" style="color: #ca5804; font-size: 0.9em">Rings, Rods, Staves, Wands, and Miscellaneous Magic:</span></p>'
        )
        
        # Try both patterns
        if re.search(merge_pattern_h2, html, re.DOTALL):
            html = re.sub(merge_pattern_h2, merged_header, html, flags=re.DOTALL)
            logger.info("Merged H2 'Rings, Rods, Staves, Wands, and Miscellaneous' and 'Magic:' into single header")
        elif re.search(merge_pattern_h1, html, re.DOTALL):
            html = re.sub(merge_pattern_h1, merged_header, html, flags=re.DOTALL)
            logger.info("Merged H1 'Rings, Rods, Staves, Wands, and Miscellaneous' and 'Magic:' into single header")
        
        # Fix 2: Split the Scrolls paragraph at "The process of setting a spell to a scroll"
        # Pattern: Find the Scrolls paragraph and split it into two paragraphs
        # Match: header + paragraph containing "The process of setting a spell to a scroll"
        scrolls_split_pattern = (
            r'(<p id="header-17-scrolls">.*?</p>)'
            r'<p>(.*?)\s+'
            r'(The process of setting a spell to a scroll.*?)</p>'
        )
        
        if re.search(scrolls_split_pattern, html, re.DOTALL):
            # Split into two paragraphs
            def split_scrolls(match):
                header = match.group(1)      # The header paragraph
                first_part = match.group(2)  # Text before "The process..."
                second_part = match.group(3) # Text from "The process..." onward
                
                # Reconstruct with paragraph break
                return f'{header}<p>{first_part}</p>\n<p>{second_part}</p>'
            
            html = re.sub(scrolls_split_pattern, split_scrolls, html, flags=re.DOTALL)
            logger.info("Split Scrolls section into two paragraphs at 'The process of setting a spell to a scroll'")
        
        # Define the headers that need to be converted from H1 to H2
        # Format: (header_id, header_text)
        # Note: header-19-magic is now removed (merged into header-18)
        # If the merge already happened, header-18 will have "...Miscellaneous Magic:"
        # If not yet merged, it will still have just "...Miscellaneous"
        magic_item_h2_headers = [
            ('header-16-potions-and-oils', 'Potions and Oils:'),
            ('header-17-scrolls', 'Scrolls:'),
            ('header-18-rings-rods-staves-wands-and-miscellaneous', 'Rings, Rods, Staves, Wands, and Miscellaneous'),  # Before merge
            ('header-20-armor-type', 'ARMOR TYPE'),
            ('header-23-metal-armor', 'METAL ARMOR'),
            ('header-26-weapons', 'Weapons:')
        ]
        
        modified_count = 0
        
        for header_id, header_text in magic_item_h2_headers:
            # Pattern to match the header with roman numeral (H1 format)
            # Example: <p id="header-16-potions-and-oils">IX.  <a href="#top"...>[^]</a> <span style="color: #ca5804">Potions and Oils:</span></p>
            # Need: <p id="header-16-potions-and-oils"> <a href="#top"...>[^]</a> <span class="header-h2" style="color: #ca5804; font-size: 0.9em">Potions and Oils:</span></p>
            
            # Escape special regex characters in header_text
            escaped_header_text = re.escape(header_text)
            
            # Check if this header is currently H1 (has roman numeral and no header-h2 class)
            h1_pattern = rf'(<p id="{header_id}">)([IVX]+\.\s+)?(<a href="#top"[^>]*>\[.?\]</a>)\s+<span style="color: #ca5804">{escaped_header_text}</span>'
            
            if re.search(h1_pattern, html):
                # Convert to H2
                h2_replacement = rf'\1 \3 <span class="header-h2" style="color: #ca5804; font-size: 0.9em">{header_text}</span>'
                html = re.sub(h1_pattern, h2_replacement, html)
                modified_count += 1
                logger.info(f"Converted '{header_text}' from H1 to H2 (removed roman numeral)")
            else:
                # Check if already H2 (has header-h2 class)
                h2_check_pattern = rf'<p id="{header_id}">.*?class="header-h2".*?{escaped_header_text}'
                if re.search(h2_check_pattern, html, re.DOTALL):
                    logger.debug(f"'{header_text}' is already H2")
                else:
                    logger.warning(f"Could not find '{header_text}' with header ID '{header_id}' to convert")
        
        if modified_count > 0:
            logger.info(f"Converted {modified_count} Magic Items subsection headers from H1 to H2")
        else:
            logger.debug("No Magic Items subsection headers needed conversion (already H2 or not found)")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to fix Magic Items section headers: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _build_armor_type_table(html: str) -> str:
    """Build a proper HTML table for the ARMOR TYPE section.
    
    The ARMOR TYPE section is currently extracted as separate headers and paragraph text.
    This function converts it into a proper 2-column, 11-row table with:
    - Column 1: d20 Roll (die roll ranges like "1", "2-5", "6-8", etc.)
    - Column 2: Armor (armor types like "Brigandine", "Hide", etc.)
    """
    try:
        # Define the table data based on the source PDF
        # Row format: (d20_roll, armor_type)
        armor_type_data = [
            ("1", "Brigandine"),
            ("2-5", "Hide"),
            ("6-8", "Leather"),
            ("9", "Padded"),
            ("10", "Ring Mail"),
            ("11-12", "Scale Mail"),
            ("13-17", "Shield"),
            ("18", "Studded Leather"),
            ("19-20", "Metal Armor"),
            ("00", "Special")
        ]
        
        # Build the HTML table
        table_html = '<table class="ds-table">\n'
        
        # Header row
        table_html += '<tr><th>d20 Roll</th><th>Armor</th></tr>\n'
        
        # Data rows
        for d20_roll, armor in armor_type_data:
            table_html += f'<tr><td>{d20_roll}</td><td>{armor}</td></tr>\n'
        
        table_html += '</table>'
        
        # Pattern to match the ARMOR TYPE section:
        # - header-20-armor-type with "ARMOR TYPE"
        # - header-21-d20-roll with "d20 Roll"  
        # - header-22-armor with "Armor"
        # - paragraph with the data
        pattern = (
            r'<p id="header-20-armor-type">.*?ARMOR TYPE</span></p>'
            r'<p id="header-21-d20-roll">.*?d20 Roll</span></p>'
            r'<p id="header-22-armor">.*?Armor</span></p>'
            r'<p>.*?</p>'
        )
        
        # Replacement: Keep the ARMOR TYPE header, remove the other headers, add table
        replacement = (
            r'<p id="header-20-armor-type"> '
            r'<a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
            r'<span class="header-h2" style="color: #ca5804; font-size: 0.9em">ARMOR TYPE</span></p>\n'
            + table_html
        )
        
        if re.search(pattern, html, re.DOTALL):
            html = re.sub(pattern, replacement, html, flags=re.DOTALL)
            logger.info("Built ARMOR TYPE table from paragraph data")
        else:
            logger.warning("Could not find ARMOR TYPE section pattern to convert to table")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to build ARMOR TYPE table: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html


def _build_metal_armor_table(html: str) -> str:
    """Build a proper HTML table for the METAL ARMOR section.
    
    The METAL ARMOR section is currently extracted as separate headers and paragraph text.
    This function converts it into a proper 2-column, 10-row table with:
    - Column 1: d100 Roll (percentile roll ranges like "01-15", "16-23", etc.)
    - Column 2: Armor (metal armor types)
    """
    try:
        # Define the table data based on the source PDF
        # Row format: (d100_roll, armor_type)
        metal_armor_data = [
            ("01-15", "Banded Mail"),
            ("16-23", "Bronze Plate Mail"),
            ("24-45", "Chain Mail"),
            ("46-50", "Field Plate"),
            ("51-55", "Full Plate"),
            ("56-65", "Plate Mail"),
            ("66-75", "Splint Mail"),
            ("76-99", "Metal Shield"),
            ("00", "Special")
        ]
        
        # Build the HTML table
        table_html = '<table class="ds-table">\n'
        
        # Header row
        table_html += '<tr><th>d100 Roll</th><th>Armor</th></tr>\n'
        
        # Data rows
        for d100_roll, armor in metal_armor_data:
            table_html += f'<tr><td>{d100_roll}</td><td>{armor}</td></tr>\n'
        
        table_html += '</table>'
        
        # Pattern to match the METAL ARMOR section:
        # - header-23-metal-armor with "METAL ARMOR"
        # - header-24-di00-roll with "dI00 roll" (note the capital I instead of lowercase l)
        # - header-25-armor with "Armor"
        # - paragraph with the data
        # - paragraph with explanation text
        pattern = (
            r'<p id="header-23-metal-armor">.*?METAL ARMOR</span></p>'
            r'<p id="header-24-di00-roll">.*?d[Il]00 roll</span></p>'
            r'<p id="header-25-armor">.*?Armor</span></p>'
            r'<p>.*?</p>'
            r'(<p>Magical adjustment to Armor Class.*?</p>)'
        )
        
        # Replacement: Keep the METAL ARMOR header, remove the other headers, add table and explanation
        def replace_metal_armor(match):
            explanation = match.group(1)
            return (
                '<p id="header-23-metal-armor"> '
                '<a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
                '<span class="header-h2" style="color: #ca5804; font-size: 0.9em">METAL ARMOR</span></p>\n'
                + table_html + '\n'
                + explanation
            )
        
        if re.search(pattern, html, re.DOTALL):
            html = re.sub(pattern, replace_metal_armor, html, flags=re.DOTALL)
            logger.info("Built METAL ARMOR table from paragraph data")
        else:
            logger.warning("Could not find METAL ARMOR section pattern to convert to table")
        
        return html
        
    except Exception as e:
        logger.error(f"Chapter 7: Failed to build METAL ARMOR table: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return html

