"""Validation processor: TableHeaderValidationProcessor.

This module contains the TableHeaderValidationProcessor for the Dark Sun PDF pipeline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...base import BaseProcessor
from ...domain import ExecutionContext, ProcessorInput, ProcessorOutput


class TableHeaderValidationProcessor(BaseProcessor):
    """Processor for validating table header metadata.
    
    Ensures that tables with header rows have the header_rows metadata set correctly.
    This prevents tables from rendering with <td> tags in header rows instead of <th> tags.
    
    Also checks for specific tables that must exist in certain chapters.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Validate table headers in structured data.
        
        Args:
            input_data: Input containing sections directory
            context: Execution context
            
        Returns:
            ProcessorOutput with validation results
        """
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        html_dir = Path(self.config.get("html_dir", "data/html_output"))
        
        errors = []
        warnings = []
        tables_checked = 0
        tables_with_issues = 0
        
        # Check all section files
        for section_file in sections_dir.glob("*.json"):
            with open(section_file, 'r', encoding='utf-8') as f:
                section_data = json.load(f)
            
            section_name = section_file.stem
            
            for page_idx, page in enumerate(section_data.get('pages', [])):
                page_num = page.get('page_number', page_idx)
                
                for table_idx, table in enumerate(page.get('tables', [])):
                    tables_checked += 1
                    rows = table.get('rows', [])
                    
                    if len(rows) < 2:
                        # Too few rows to validate
                        continue
                    
                    # Check if first row looks like a header
                    first_row = rows[0]
                    if not isinstance(first_row, dict) or 'cells' not in first_row:
                        continue
                    
                    cells = first_row.get('cells', [])
                    if len(cells) < 2:
                        continue
                    
                    # Heuristic: check if first row cells are short text (likely headers)
                    cell_texts = [cell.get('text', '').strip() for cell in cells]
                    avg_length = sum(len(text) for text in cell_texts) / len(cell_texts) if cell_texts else 0
                    
                    # If cells are short and don't contain special characters (likely headers)
                    looks_like_header = (
                        avg_length < 20 and
                        all(len(text) < 50 for text in cell_texts if text) and
                        not any('/' in text or text.isdigit() for text in cell_texts[:3] if text)
                    )
                    
                    if looks_like_header and 'header_rows' not in table:
                        tables_with_issues += 1
                        error_msg = (
                            f"Table in {section_name}, page {page_num}, table {table_idx} "
                            f"appears to have a header row (first cells: {cell_texts[:3]}) "
                            f"but is missing 'header_rows' metadata. This will cause headers "
                            f"to render as data cells."
                        )
                        errors.append(error_msg)
        
        # Check HTML output for critical tables and paragraph structure
        chapter2_html = html_dir / "chapter-two-player-character-races.html"
        if chapter2_html.exists():
            with open(chapter2_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            import re
            
            # Check for Other Languages table
            if 'header-8-other-languages' in html_content:
                # Find the section and check if it contains a table
                other_lang_section = re.search(
                    r'<p id="header-8-other-languages">.*?(<table|<p id="header-9)',
                    html_content,
                    re.DOTALL
                )
                if other_lang_section and '<table' not in other_lang_section.group(0):
                    tables_with_issues += 1
                    error_msg = (
                        "Other Languages section in Chapter 2 is missing its language table. "
                        "The language list should be formatted as a 2-column table, not plain text."
                    )
                    errors.append(error_msg)
            
            # Check Half-elves Roleplaying paragraph count
            if 'header-13-roleplaying-' in html_content:
                # Find the Half-elves Roleplaying section
                roleplaying_section = re.search(
                    r'<p id="header-13-roleplaying-">.*?</p>(.*?)<p id="header-14-half-giants">',
                    html_content,
                    re.DOTALL
                )
                if roleplaying_section:
                    content = roleplaying_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 3:
                        tables_with_issues += 1
                        error_msg = (
                            f"Half-elves Roleplaying section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 3: (1) self-reliance introduction, "
                            f"(2) example behavior, (3) acceptance seeking."
                        )
                        errors.append(error_msg)
            
            # Check Half-Giants main section paragraph count
            if 'header-14-half-giants' in html_content:
                # Find the Half-Giants main section (before Roleplaying)
                half_giants_section = re.search(
                    r'<p id="header-14-half-giants">.*?</p>(.*?)<p id="header-15-roleplaying-">',
                    html_content,
                    re.DOTALL
                )
                if half_giants_section:
                    content = half_giants_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 10:
                        tables_with_issues += 1
                        error_msg = (
                            f"Half-Giants main section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 10: (1) origins, (2) physical description, "
                            f"(3) available classes, (4) traits/personality, (5) culture/history, "
                            f"(6) communities, (7) alignment flexibility, (8) attribute modifiers, "
                            f"(9) hit die rolls, (10) equipment costs."
                        )
                        errors.append(error_msg)
            
            # Check Half-Giants Roleplaying paragraph count
            if 'header-15-roleplaying-' in html_content:
                # Find the Half-Giants Roleplaying section
                half_giants_roleplaying = re.search(
                    r'<p id="header-15-roleplaying-">.*?</p>(.*?)<p id="header-16-halflings">',
                    html_content,
                    re.DOTALL
                )
                if half_giants_roleplaying:
                    content = half_giants_roleplaying.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 4:
                        tables_with_issues += 1
                        error_msg = (
                            f"Half-Giants Roleplaying section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 4: (1) friendly introduction, "
                            f"(2) example behavior, (3) qualifications about imitation, "
                            f"(4) roleplay advice about size."
                        )
                        errors.append(error_msg)
            
            # Check Halflings main section paragraph count
            if 'header-16-halflings' in html_content:
                # Find the Halflings main section (before Roleplaying)
                halflings_section = re.search(
                    r'<p id="header-16-halflings">.*?</p>(.*?)<p id="header-17-roleplaying-">',
                    html_content,
                    re.DOTALL
                )
                if halflings_section:
                    content = halflings_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 9:
                        tables_with_issues += 1
                        error_msg = (
                            f"Halflings main section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 9: (1) jungle habitat/physical description, "
                            f"(2) racial unity, (3) culture/values, (4) relationship with land, "
                            f"(5) abilities/resistances, (6) Strength penalties, "
                            f"(7) Charisma penalties, (8) Dexterity/Wisdom bonuses, "
                            f"(9) exceptional strength limitations."
                        )
                        errors.append(error_msg)
            
            # Check Halflings Roleplaying paragraph count
            if 'header-17-roleplaying-' in html_content:
                # Find the Halflings Roleplaying section
                halflings_roleplaying = re.search(
                    r'<p id="header-17-roleplaying-">.*?</p>(.*?)<p id="header-18-human">',
                    html_content,
                    re.DOTALL
                )
                if halflings_roleplaying:
                    content = halflings_roleplaying.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 5:
                        tables_with_issues += 1
                        error_msg = (
                            f"Halflings Roleplaying section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 5: (1) comfortable in groups/curious about customs, "
                            f"(2) alien view of accomplishments, (3) response to size comments, "
                            f"(4) loyalty to brethren."
                        )
                        errors.append(error_msg)
            
            # Check Human section paragraph count
            if 'header-18-human' in html_content:
                # Find the Human section
                human_section = re.search(
                    r'<p id="header-18-human">.*?</p>(.*?)<p id="header-19-mul">',
                    html_content,
                    re.DOTALL
                )
                if human_section:
                    content = human_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 5:
                        tables_with_issues += 1
                        error_msg = (
                            f"Human section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 5: (1) predominant race/class access, "
                            f"(2) physical description, (3) appearance alterations, "
                            f"(4) half-races info, (5) tolerance of other races."
                        )
                        errors.append(error_msg)
            
            # Check Mul main section paragraph count
            if 'header-19-mul' in html_content:
                # Find the Mul main section (before Roleplaying)
                mul_section = re.search(
                    r'<p id="header-19-mul">.*?</p>(.*?)<p id="header-22-roleplaying-">',
                    html_content,
                    re.DOTALL
                )
                if mul_section:
                    content = mul_section.group(1)
                    # Count <p> tags (paragraphs), excluding table headers
                    # Find all <p> tags with their full tag and content
                    all_p_tags = re.findall(r'(<p[^>]*>.*?</p>)', content, re.DOTALL)
                    # Filter out table headers (header-20 and header-21) by checking the full tag
                    paragraph_count = sum(1 for p in all_p_tags 
                                         if 'id="header-20' not in p and 'id="header-21' not in p)
                    
                    if paragraph_count != 8:
                        tables_with_issues += 1
                        error_msg = (
                            f"Mul main section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 8: (1) origins/sterility, (2) physical description, "
                            f"(3) personality/upbringing, (4) freedom/careers, (5) available classes, "
                            f"(6) attribute modifiers, (7) exertion intro, (8) exertion details."
                        )
                        errors.append(error_msg)
            
            # Check Mul Roleplaying paragraph count
            if 'header-21-roleplaying-' in html_content or 'header-22-roleplaying-' in html_content:
                # Find the Mul Roleplaying section (try both possible header IDs)
                mul_roleplaying = re.search(
                    r'<p id="header-21-roleplaying-">.*?</p>(.*?)<p id="header-22-thri-kreen">',
                    html_content,
                    re.DOTALL
                )
                if not mul_roleplaying:
                    mul_roleplaying = re.search(
                        r'<p id="header-22-roleplaying-">.*?</p>(.*?)<p id="header-23-thri-kreen">',
                        html_content,
                        re.DOTALL
                    )
                if mul_roleplaying:
                    content = mul_roleplaying.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 2:
                        tables_with_issues += 1
                        error_msg = (
                            f"Mul Roleplaying section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 2: (1) pampered slaves/treatment, "
                            f"(2) dwarven stubbornness/trading."
                        )
                        errors.append(error_msg)
            
            # Check Thri-kreen main section paragraph count
            if 'header-22-thri-kreen' in html_content or 'header-23-thri-kreen' in html_content:
                # Find the Thri-kreen main section (before Roleplaying)
                thri_kreen_section = re.search(
                    r'<p id="header-22-thri-kreen">.*?</p>(.*?)<p id="header-23-roleplaying-">',
                    html_content,
                    re.DOTALL
                )
                if not thri_kreen_section:
                    thri_kreen_section = re.search(
                        r'<p id="header-23-thri-kreen">.*?</p>(.*?)<p id="header-\d+-roleplaying-">',
                        html_content,
                        re.DOTALL
                    )
                if thri_kreen_section:
                    content = thri_kreen_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 15:
                        tables_with_issues += 1
                        error_msg = (
                            f"Thri-kreen main section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 15: physical description, anatomy, sleep, weapons, "
                            f"items, organization, carnivores, classes, attacks, leaping, venom, chatkcha, "
                            f"dodge, attributes."
                        )
                        errors.append(error_msg)
            
            # Check Thri-kreen Roleplaying paragraph count
            if 'thri-kreen' in html_content.lower():
                # Find the Thri-kreen Roleplaying section
                thri_kreen_roleplaying = re.search(
                    r'<p id="header-23-roleplaying-">.*?</p>(.*?)<p id="header-24-other-characteristics">',
                    html_content,
                    re.DOTALL
                )
                if not thri_kreen_roleplaying:
                    thri_kreen_roleplaying = re.search(
                        r'<p id="header-\d+-roleplaying-">.*?</p>(.*?)<p id="header-\d+-other-characteristics">',
                        html_content,
                        re.DOTALL
                    )
                if thri_kreen_roleplaying:
                    content = thri_kreen_roleplaying.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 4:
                        tables_with_issues += 1
                        error_msg = (
                            f"Thri-kreen Roleplaying section in Chapter 2 has {paragraph_count} paragraphs "
                            f"but should have exactly 4: (1) obsession/hunt, (2) birth/training, "
                            f"(3) outsiders/behavior, (4) pack intelligence/protectiveness."
                        )
                        errors.append(error_msg)
            
            # Check Chapter 3: Warrior Classes section paragraph count
            chapter_3_html_file = html_dir / "chapter-three-player-character-classes.html"
            if chapter_3_html_file.exists():
                with open(chapter_3_html_file, 'r', encoding='utf-8') as f:
                    ch3_html_content = f.read()
                
                # Find the Warrior Classes section (between Warrior Classes header and Wizard Classes header)
                warrior_section = re.search(
                    r'<p id="header-1-warrior-classes">.*?</p>(.*?)<p id="header-2-wizard-classes">',
                    ch3_html_content,
                    re.DOTALL
                )
                if warrior_section:
                    content = warrior_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 5:
                        tables_with_issues += 1
                        error_msg = (
                            f"Warrior Classes section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 5: (1) intro about three classes, "
                            f"(2) fighter description, (3) ranger description, (4) gladiator description, "
                            f"(5) no paladins note."
                        )
                        errors.append(error_msg)
                
                # Find the detailed Wizard section (between Wizard header and Defiler header)
                wizard_section = re.search(
                    r'<p id="header-22-wizard">.*?</p>(.*?)<p id="header-23-defiler">',
                    ch3_html_content,
                    re.DOTALL
                )
                if wizard_section:
                    content = wizard_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 6:
                        tables_with_issues += 1
                        error_msg = (
                            f"Wizard section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 6: (1) wizard intro/magic & ecosystem, "
                            f"(2) preserver description, (3) defiler description, "
                            f"(4) illusionist description, (5) wizard restrictions, "
                            f"(6) Dark Sun specific rules."
                        )
                        errors.append(error_msg)
                
                # Find the Defiler section (between Defiler header and Defiler Experience Levels header)
                defiler_section = re.search(
                    r'<p id="header-23-defiler">.*?</p>(.*?)<p id="header-24-defiler-experience-levels">',
                    ch3_html_content,
                    re.DOTALL
                )
                if defiler_section:
                    content = defiler_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 4:
                        tables_with_issues += 1
                        error_msg = (
                            f"Defiler section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 4"
                        )
                        errors.append(error_msg)
                
                # Validate Defiler Experience Levels table
                defiler_exp_match = re.search(
                    r'<p id="header-24-defiler-experience-levels">.*?</p>\s*(<table[^>]*>.*?</table>)',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if defiler_exp_match:
                    defiler_table = defiler_exp_match.group(1)
                    # Count rows
                    defiler_rows = re.findall(r'<tr>', defiler_table)
                    
                    # Should have 21 rows (1 header + 20 data rows)
                    if len(defiler_rows) != 21:
                        error_msg = (
                            f"Defiler Experience Levels table has {len(defiler_rows)} rows but should have 21 "
                            f"(1 header + 20 data rows)"
                        )
                        errors.append(error_msg)
                    
                    # Count columns in the header row
                    header_row_match = re.search(r'<tr>(.*?)</tr>', defiler_table, re.DOTALL)
                    if header_row_match:
                        header_cells = re.findall(r'<th>', header_row_match.group(1))
                        if len(header_cells) != 3:
                            error_msg = (
                                f"Defiler Experience Levels table has {len(header_cells)} columns but should have 3"
                            )
                            errors.append(error_msg)
                
                # Find the Preserver section (between Preserver header and Illusionist header)
                preserver_section = re.search(
                    r'<p id="header-\d+-preserver">.*?</p>(.*?)<p id="header-\d+-illusionist">',
                    ch3_html_content,
                    re.DOTALL
                )
                if preserver_section:
                    content = preserver_section.group(1)
                    
                    # Count <p> tags (paragraphs), excluding the ability table
                    # Remove table content first
                    content_without_table = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL)
                    paragraph_count = len(re.findall(r'<p>', content_without_table))
                    
                    if paragraph_count != 2:
                        tables_with_issues += 1
                        error_msg = (
                            f"Preserver section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 2"
                        )
                        errors.append(error_msg)
                    
                    # Check for malformed page number "2 7"
                    if "2 7" in content:
                        tables_with_issues += 1
                        error_msg = (
                            f"Preserver section in Chapter 3 contains malformed page number '2 7' "
                            f"that should be removed"
                        )
                        errors.append(error_msg)
                
                # Find the detailed Priest section (between Priest header and Spheres of Magic header)
                priest_section = re.search(
                    r'<p id="header-\d+-priest">.*?</p>(.*?)<p id="header-\d+-spheres-of-magic">',
                    ch3_html_content,
                    re.DOTALL
                )
                if priest_section:
                    content = priest_section.group(1)
                    
                    # Count <p> tags (paragraphs), excluding tables
                    content_without_table = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL)
                    paragraph_count = len(re.findall(r'<p>', content_without_table))
                    
                    if paragraph_count != 6:
                        tables_with_issues += 1
                        error_msg = (
                            f"Priest section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 6"
                        )
                        errors.append(error_msg)
                
                # Find the Spheres of Magic section (between Spheres of Magic header and Cleric header)
                spheres_section = re.search(
                    r'<p id="header-\d+-spheres-of-magic">.*?</p>(.*?)<p id="header-\d+-cleric">',
                    ch3_html_content,
                    re.DOTALL
                )
                if spheres_section:
                    content = spheres_section.group(1)
                    
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 3:
                        tables_with_issues += 1
                        error_msg = (
                            f"Spheres of Magic section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 3"
                        )
                        errors.append(error_msg)
                
                # Find the Cleric section (between Cleric header and Cleric Weapons Restrictions header)
                cleric_section = re.search(
                    r'<p id="header-\d+-cleric">.*?</p>(.*?)<p id="header-\d+-cleric-weapons-restrictions">',
                    ch3_html_content,
                    re.DOTALL
                )
                if cleric_section:
                    content = cleric_section.group(1)
                    
                    # Count <p> tags (paragraphs), excluding the ability table
                    content_without_table = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL)
                    paragraph_count = len(re.findall(r'<p>', content_without_table))
                    
                    if paragraph_count != 4:
                        tables_with_issues += 1
                        error_msg = (
                            f"Cleric section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 4"
                        )
                        errors.append(error_msg)
                    
                    # Check for malformed page number "2 9"
                    if "2 9" in content:
                        tables_with_issues += 1
                        error_msg = (
                            f"Cleric section in Chapter 3 contains malformed page number '2 9' "
                            f"that should be removed"
                        )
                        errors.append(error_msg)
                
                # Find the Cleric powers section (after Elemental Plane of Water and before Druid)
                cleric_powers_section = re.search(
                    r'<p id="header-\d+-elemental-plane-of-water">.*?</p>.*?<p>Those who worship.*?</p>.*?<p>Therefore.*?</p>(.*?)<p id="header-\d+-druid">',
                    ch3_html_content,
                    re.DOTALL
                )
                if cleric_powers_section:
                    content = cleric_powers_section.group(1)
                    
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 10:
                        tables_with_issues += 1
                        error_msg = (
                            f"Cleric powers section (after Elemental Plane of Water) in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 10"
                        )
                        errors.append(error_msg)
                    
                    # Check for malformed page number "3 0"
                    if "3 0" in content:
                        tables_with_issues += 1
                        error_msg = (
                            f"Cleric powers section in Chapter 3 contains malformed page number '3 0' "
                            f"that should be removed"
                        )
                        errors.append(error_msg)
                
                # Find the Druid section (between Druid table and "Possible Guardian Lands" header)
                druid_section = re.search(
                    r'<p id="header-\d+-druid">.*?</p>\s*<table[^>]*>.*?</table>(.*?)<p id="header-\d+-possible-guardian-lands">',
                    ch3_html_content,
                    re.DOTALL
                )
                if druid_section:
                    content = druid_section.group(1)
                    
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 8:
                        tables_with_issues += 1
                        error_msg = (
                            f"Druid section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 8"
                        )
                        errors.append(error_msg)
                
                # Find the Druid granted powers section (starting from "When in his guarded lands" to Templar)
                druid_powers_section = re.search(
                    r'<p>When in his guarded lands(.*?)<p id="header-\d+-templar">',
                    ch3_html_content,
                    re.DOTALL
                )
                if druid_powers_section:
                    # The content starts after the opening <p>When in his guarded lands
                    # So we need to count that paragraph plus the ones that follow
                    full_content = '<p>When in his guarded lands' + druid_powers_section.group(1)
                    # Count <p> tags (paragraphs) - should be 7
                    paragraph_count = len(re.findall(r'<p>', full_content))
                    
                    if paragraph_count != 7:
                        tables_with_issues += 1
                        error_msg = (
                            f"Druid granted powers section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 7 (starting with 'When in his guarded lands')"
                        )
                        errors.append(error_msg)
                
                # Find the Templar class details section (between Templar table and Templar Spell Progression)
                templar_section = re.search(
                    r'<p id="header-\d+-templar">.*?</table>(.*?)<p id="header-\d+-templar-spell-progression">',
                    ch3_html_content,
                    re.DOTALL
                )
                if templar_section:
                    content = templar_section.group(1)
                    # Count <p> tags (paragraphs) - should be 2
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 2:
                        tables_with_issues += 1
                        error_msg = (
                            f"Templar class details section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 2 (break at 'Templars gain levels as do clerics,')"
                        )
                        errors.append(error_msg)
                
                # Validate Templar abilities section (after Spell Progression table to Rogue header)
                templar_abilities_section = re.search(
                    r'<p>(The libraries of the templars.*?)</p>.*?(?=<p id="header-\d+-rogue">)',
                    ch3_html_content,
                    re.DOTALL
                )
                if templar_abilities_section:
                    # Count content paragraphs (not headers)
                    paragraphs = re.findall(r'<p[^>]*>(?!.*id="header)(.*?)</p>', templar_abilities_section.group(0), re.DOTALL)
                    content_paras = [p for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip() and len(re.sub(r'<[^>]+>', '', p).strip()) > 20]
                    
                    if len(content_paras) != 19:
                        tables_with_issues += 1
                        error_msg = (
                            f"Templar abilities section in Chapter 3 has {len(content_paras)} paragraphs "
                            f"but should have exactly 19 (starting with 'The libraries of the templars')"
                        )
                        errors.append(error_msg)
                
                # Validate Bard class details section (after Bard ability table)
                bard_section = re.search(
                    r'<p id="header-\d+-bard">.*?</table>(.*?)(?=<p id="header-|<table class="ds-table">.*?Poison)',
                    ch3_html_content,
                    re.DOTALL
                )
                if bard_section:
                    # Count content paragraphs (not headers or tables)
                    paragraphs = re.findall(r'<p[^>]*>(?!.*id="header)(.*?)</p>', bard_section.group(1), re.DOTALL)
                    content_paras = [p for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip() and len(re.sub(r'<[^>]+>', '', p).strip()) > 20]
                    
                    if len(content_paras) != 11:
                        tables_with_issues += 1
                        error_msg = (
                            f"Bard class details section in Chapter 3 has {len(content_paras)} paragraphs "
                            f"but should have exactly 11 (with breaks at 'As described in', etc.)"
                        )
                        errors.append(error_msg)
                
                # Validate Thief class details paragraph breaks
                thief_section = re.search(
                    r'<p id="header-\d+-thief">.*?</p>.*?<table.*?</table>(.*?)(<p id="header-|<table)',
                    ch3_html_content,
                    re.DOTALL
                )
                if thief_section:
                    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', thief_section.group(1), re.DOTALL)
                    content_paras = [p for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip() and len(re.sub(r'<[^>]+>', '', p).strip()) > 50]
                    
                    if len(content_paras) != 5:
                        tables_with_issues += 1
                        error_msg = (
                            f"Thief class details section in Chapter 3 has {len(content_paras)} paragraphs "
                            f"but should have exactly 5 (with breaks at 'A thiefs prime requisite', 'A thief can choose any', etc.)"
                        )
                        errors.append(error_msg)
                    else:
                        # Validate that paragraphs start with expected text
                        expected_starts = [
                            "Athasian thieves",
                            "A thiefs prime requisite",
                            "A thief can choose any",
                            "A thiefs selection",
                            "A thiefs skills"
                        ]
                        for i, para in enumerate(content_paras):
                            clean_text = re.sub(r'<[^>]+>', '', para).strip()
                            if not clean_text.startswith(expected_starts[i]):
                                tables_with_issues += 1
                                error_msg = (
                                    f"Thief paragraph {i+1} should start with '{expected_starts[i]}' "
                                    f"but starts with '{clean_text[:30]}...'"
                                )
                                errors.append(error_msg)
                
                # Validate Thieving Dexterity table and paragraphs
                dex_section = re.search(
                    r'<p id="header-\d+-thieving-skill-exceptional-dexterity-adjustments">.*?</p>(.*?)<p id="header',
                    ch3_html_content,
                    re.DOTALL
                )
                if dex_section:
                    section_content = dex_section.group(1)
                    
                    # Check for table
                    table_match = re.search(r'<table[^>]*>(.*?)</table>', section_content, re.DOTALL)
                    if table_match:
                        table_html = table_match.group(0)
                        rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
                        
                        if len(rows) != 6:
                            tables_with_issues += 1
                            error_msg = (
                                f"Thieving Dexterity table has {len(rows)} rows but should have 6 "
                                f"(1 header + 5 data rows for Dex 18-22)"
                            )
                            errors.append(error_msg)
                        
                        # Check header
                        if rows:
                            header_cells = re.findall(r'<th[^>]*>(.*?)</th>', rows[0], re.DOTALL)
                            if len(header_cells) != 6:
                                tables_with_issues += 1
                                error_msg = (
                                    f"Thieving Dexterity table has {len(header_cells)} columns but should have 6"
                                )
                                errors.append(error_msg)
                        
                        # Check paragraphs after table
                        after_table = section_content[table_match.end():]
                        paras = re.findall(r'<p(?![^>]*id="header")[^>]*>(.*?)</p>', after_table, re.DOTALL)
                        content_paras = [p for p in paras if len(re.sub(r'<[^>]+>', '', p).strip()) > 50]
                        
                        if len(content_paras) < 3:
                            tables_with_issues += 1
                            error_msg = (
                                f"Thieving Dexterity section has {len(content_paras)} paragraphs after table "
                                f"but should have at least 3"
                            )
                            errors.append(error_msg)
                    else:
                        tables_with_issues += 1
                        errors.append("Thieving Dexterity table not found in Chapter 3")
                
                # Validate Thieving Racial Adjustments table
                racial_section = re.search(
                    r'<p id="header-\d+-thieving-skill-racial-adjustments">.*?</p>(.*?)<p id="header',
                    ch3_html_content,
                    re.DOTALL
                )
                if racial_section:
                    section_content = racial_section.group(1)
                    
                    # Check for table
                    table_match = re.search(r'<table[^>]*>(.*?)</table>', section_content, re.DOTALL)
                    if table_match:
                        table_html = table_match.group(0)
                        rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
                        
                        if len(rows) != 9:
                            tables_with_issues += 1
                            error_msg = (
                                f"Thieving Racial Adjustments table has {len(rows)} rows but should have 9 "
                                f"(1 header + 8 skill rows)"
                            )
                            errors.append(error_msg)
                        
                        # Check header
                        if rows:
                            header_cells = re.findall(r'<th[^>]*>(.*?)</th>', rows[0], re.DOTALL)
                            if len(header_cells) != 6:
                                tables_with_issues += 1
                                error_msg = (
                                    f"Thieving Racial Adjustments table has {len(header_cells)} columns but should have 6"
                                )
                                errors.append(error_msg)
                    else:
                        tables_with_issues += 1
                        errors.append("Thieving Racial Adjustments table not found in Chapter 3")
                
                # Validate Psionicist section paragraphs
                psionicist_section = re.search(
                    r'<p id="header-\d+-psionicist">.*?</p>.*?<table.*?</table>(.*?)(<p id="header-|$)',
                    ch3_html_content,
                    re.DOTALL
                )
                if psionicist_section:
                    section_content = psionicist_section.group(1)
                    paras = re.findall(r'<p(?![^>]*id="header")[^>]*>(.*?)</p>', section_content, re.DOTALL)
                    
                    content_paras = []
                    for p in paras:
                        clean = re.sub(r'<[^>]+>', '', p).strip()
                        if len(clean) > 20:  # Lower threshold to catch all paragraphs
                            content_paras.append(clean)
                    
                    # Expecting exactly 3 paragraphs now that we've properly split the line
                    if len(content_paras) != 3:
                        errors.append(
                            f"Psionicist section has {len(content_paras)} paragraphs but should have 3"
                        )
                    else:
                        # Check for expected paragraph starts (text has been fixed for spacing)
                        expected_starts = [
                            "All intelligent creatures",
                            "In Dark Sun there are no racial restrictions",
                            "Inherent Potential:",  # Stands alone now
                        ]
                        
                        for i, start in enumerate(expected_starts, 1):
                            if not any(p.startswith(start) for p in content_paras):
                                errors.append(
                                    f"Psionicist paragraph {i} doesn't start with expected text \"{start[:30]}...\""
                                )
                        
                        # Check that paragraph 3 starts with "Inherent Potential:" and ONLY contains that
                        para3 = content_paras[2] if len(content_paras) > 2 else ""
                        if not (para3.startswith("Inherent Potential:") and len(para3) < 50):
                            errors.append(
                                f'Psionicist paragraph 3 should be just "Inherent Potential:" header, got: {para3[:60]}'
                            )
                
                # Validate Inherent Potential Table and subsections
                inherent_header_match = re.search(
                    r'<p id="header-\d+-inherent-potential-table">',
                    ch3_html_content
                )
                if not inherent_header_match:
                    errors.append("Inherent Potential Table header not found in HTML")
                else:
                    # Check for tables in the section between header and next header
                    section_match = re.search(
                        r'<p id="header-\d+-inherent-potential-table">.*?</p>(.*?)<p id="header-\d+-non-player-characters',
                        ch3_html_content,
                        re.DOTALL
                    )
                    if section_match:
                        section_content = section_match.group(1)
                        tables_in_section = re.findall(r'<table[^>]*>.*?</table>', section_content, re.DOTALL)
                        
                        if len(tables_in_section) == 0:
                            errors.append("Inherent Potential Table header found but NO table in section")
                        elif len(tables_in_section) > 1:
                            errors.append(f"Inherent Potential Table section has {len(tables_in_section)} tables but should have only 1")
                        
                        # Check for Power Checks and Wild Talents as H2 subheaders
                        power_checks_header = re.search(r'<p id="header-\d+-power-checks-">', section_content)
                        wild_talents_header = re.search(r'<p id="header-\d+-wild-talents-">', section_content)
                        
                        if not power_checks_header:
                            errors.append("'Power Checks:' should be an H2 subheader but not found")
                        if not wild_talents_header:
                            errors.append("'Wild Talents:' should be an H2 subheader but not found")
                        
                        # Check that Power Checks and Wild Talents are NOT inline in paragraphs
                        non_header_paras = re.findall(r'<p(?![^>]*id="header")[^>]*>(.*?)</p>', section_content, re.DOTALL)
                        for para in non_header_paras:
                            clean = re.sub(r'<[^>]+>', '', para).strip()
                            if clean.startswith("Power Checks:"):
                                errors.append("'Power Checks:' is inline in a paragraph but should be an H2 subheader")
                            if clean.startswith("Wild Talents:"):
                                errors.append("'Wild Talents:' is inline in a paragraph but should be an H2 subheader")
                    
                    # Get the first table for validation
                    inherent_table_match = re.search(
                        r'<p id="header-\d+-inherent-potential-table">.*?</p>\s*(<table[^>]*>.*?</table>)',
                        ch3_html_content,
                        re.DOTALL
                    )
                    if not inherent_table_match:
                        errors.append("Inherent Potential Table exists as header but table not immediately after it")
                
                if inherent_header_match and inherent_table_match:
                    table_html = inherent_table_match.group(1)
                    
                    # Count rows
                    rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
                    if len(rows) != 9:
                        errors.append(
                            f"Inherent Potential Table has {len(rows)} rows but should have 9 (1 header + 8 data)"
                        )
                    
                    # Count columns (check first row)
                    if rows:
                        first_row = rows[0]
                        cells = re.findall(r'<t[hd][^>]*>.*?</t[hd]>', first_row, re.DOTALL)
                        if len(cells) != 3:
                            errors.append(
                                f"Inherent Potential Table has {len(cells)} columns but should have 3"
                            )
                        
                        # Check header row content
                        header_texts = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                        expected_headers = ["Ability Score", "Base Score", "Ability Modifier"]
                        if header_texts != expected_headers:
                            errors.append(
                                f"Inherent Potential Table headers are {header_texts} but should be {expected_headers}"
                            )
                    
                    # Check for extra whitespace in values (e.g., "+ 2" instead of "+2")
                    if "+ 1" in table_html or "+ 2" in table_html or "+ 3" in table_html:
                        errors.append(
                            "Inherent Potential Table contains values with extra whitespace (e.g., '+ 2' instead of '+2')"
                        )
                
                # Validate Templar Spell Progression table
                templar_table_match = re.search(
                    r'<p id="header-\d+-templar-spell-progression">.*?</p>\s*(<table[^>]*>.*?</table>)',
                    ch3_html_content,
                    re.DOTALL
                )
                if templar_table_match:
                    table_html = templar_table_match.group(1)
                    rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
                    
                    if len(rows) != 22:
                        tables_with_issues += 1
                        error_msg = (
                            f"Templar Spell Progression table has {len(rows)} rows but should have 22 "
                            f"(2 header rows + 20 data rows)"
                        )
                        errors.append(error_msg)
                    else:
                        # Check first row for correct column count
                        first_row = rows[0]
                        cols = re.findall(r'<th[^>]*>.*?</th>|<td[^>]*>.*?</td>', first_row, re.DOTALL)
                        
                        if len(cols) != 8:
                            tables_with_issues += 1
                            error_msg = (
                                f"Templar Spell Progression table has {len(cols)} columns but should have 8 "
                                f"(Templar + 7 spell levels)"
                            )
                            errors.append(error_msg)
                        
                        # Check for rowspan in first cell (should contain "Templar")
                        if 'rowspan="2"' not in first_row:
                            tables_with_issues += 1
                            errors.append("Templar Spell Progression table first cell should have rowspan=2")
                        
                        # Check for colspan in second cell (should contain "Spell Level")
                        if 'colspan="7"' not in first_row:
                            tables_with_issues += 1
                            errors.append("Templar Spell Progression table second cell should have colspan=7")
                        
                        # Verify header content
                        if "Templar Level" not in first_row or "Spell Level" not in first_row:
                            tables_with_issues += 1
                            errors.append("Templar Spell Progression table headers should be 'Templar Level' and 'Spell Level'")
                
                # Find the Priest Classes section (between Priest Classes header and Rogue Classes header)
                priest_section = re.search(
                    r'<p id="header-3-priest-classes">.*?</p>(.*?)<p id="header-4-rogue-classes">',
                    ch3_html_content,
                    re.DOTALL
                )
                if priest_section:
                    content = priest_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 4:
                        tables_with_issues += 1
                        error_msg = (
                            f"Priest Classes section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 4: (1) intro about three types of priests, "
                            f"(2) cleric description, (3) templar description, (4) druid description."
                        )
                        errors.append(error_msg)
                
                # Find the Rogue Classes section (between Rogue Classes header and Psionicist Class header)
                rogue_section = re.search(
                    r'<p id="header-4-rogue-classes">.*?</p>(.*?)<p id="header-5-the-psionicist-class">',
                    ch3_html_content,
                    re.DOTALL
                )
                if rogue_section:
                    content = rogue_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 3:
                        tables_with_issues += 1
                        error_msg = (
                            f"Rogue Classes section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 3: (1) intro about corruption and rogue success, "
                            f"(2) thief description, (3) bard description."
                        )
                        errors.append(error_msg)
                
                # Find The Psionicist Class section (between Psionicist Class header and next section)
                # Need to find what comes after - checking for "Character Abilities" or similar
                psionicist_section = re.search(
                    r'<p id="header-5-the-psionicist-class">.*?</p>(.*?)(?:<p id="header-|<h2>|$)',
                    ch3_html_content,
                    re.DOTALL
                )
                if psionicist_section:
                    content = psionicist_section.group(1)
                    # Count <p> tags (paragraphs)
                    paragraph_count = len(re.findall(r'<p>', content))
                    
                    if paragraph_count != 2:
                        tables_with_issues += 1
                        error_msg = (
                            f"The Psionicist Class section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 2: (1) intro about psionicists, "
                            f"(2) character requirements."
                        )
                        errors.append(error_msg)
                
                # Find the Fighter section (between Fighter header and ability table)
                fighter_section = re.search(
                    r'<p id="header-17-fighter">.*?</p>\s*<table[^>]*>.*?</table>(.*?)<p id="header-18',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if fighter_section:
                    # Count paragraphs in the Fighter section
                    paragraph_count = len(re.findall(r'<p>(?!<span)', fighter_section.group(1)))
                    
                    if paragraph_count != 7:
                        error_msg = (
                            f"Fighter section in Chapter 3 has {paragraph_count} paragraphs "
                            f"but should have exactly 7: (1) intro, (2) alignments/items, (3) experience/reputation, "
                            f"(4) followers structure, (5) first unit, (6) subsequent units, (7) cannot avoid followers."
                        )
                        errors.append(error_msg)
                
                # Validate Fighter benefits section (after Fighters Followers table and legend)
                fighter_benefits_section = re.search(
                    r'<p><strong>Special:</strong>[^<]+</p>(.*?)<p id="header-[0-9]+-gladiator">',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if fighter_benefits_section:
                    # Count paragraphs in the Fighter benefits section
                    benefits_paragraph_count = len(re.findall(r'<p>(?!<span)', fighter_benefits_section.group(1)))
                    
                    if benefits_paragraph_count != 10:
                        error_msg = (
                            f"Fighter benefits section in Chapter 3 has {benefits_paragraph_count} paragraphs "
                            f"but should have exactly 10."
                        )
                        errors.append(error_msg)
                
                # Validate Gladiator section
                gladiator_section = re.search(
                    r'<p id="header-[0-9]+-gladiator">.*?</p>\s*<table[^>]*>.*?</table>(.*?)<p id="header-[0-9]+-ranger">',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if gladiator_section:
                    # Count paragraphs in the Gladiator section
                    gladiator_paragraph_count = len(re.findall(r'<p>(?!<span)', gladiator_section.group(1)))
                    
                    if gladiator_paragraph_count != 10:
                        error_msg = (
                            f"Gladiator section in Chapter 3 has {gladiator_paragraph_count} paragraphs "
                            f"but should have exactly 10: (1) intro, (2) prime requisite bonus, (3) alignment, "
                            f"(4) magical items, (5) special benefits intro, (6) weapon proficiency, (7) specialization, "
                            f"(8) unarmed combat, (9) armor optimization, (10) followers."
                        )
                        errors.append(error_msg)
                
                # Validate Ranger Ability Requirements table
                ranger_table_match = re.search(
                    r'<p id="header-[0-9]+-ranger">.*?</p>\s*(<table[^>]*>.*?</table>)',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if ranger_table_match:
                    ranger_table = ranger_table_match.group(1)
                    # Count rows
                    ranger_rows = re.findall(r'<tr>', ranger_table)
                    
                    if len(ranger_rows) != 3:
                        error_msg = (
                            f"Ranger Ability Requirements table has {len(ranger_rows)} rows but should have 3"
                        )
                        errors.append(error_msg)
                    
                    # Validate content
                    if "Strength 13 Dexterity 13 Constitution 14 Wisdom 14" not in ranger_table:
                        errors.append("Ranger table missing correct ability requirements")
                    
                    if "Strength, Dexterity, Wisdom" not in ranger_table:
                        errors.append("Ranger table missing correct prime requisites")
                    
                    if "Human, Elf, Half-elf, Halfling, Thri-kreen" not in ranger_table:
                        errors.append("Ranger table missing correct races allowed")
                
                # Check for duplicate race text after the Ranger table
                ranger_with_context = re.search(
                    r'<p id="header-[0-9]+-ranger">.*?</p>\s*<table[^>]*>.*?</table>(.*?<p>.*?</p>)',
                    ch3_html_content,
                    re.DOTALL
                )
                if ranger_with_context:
                    context_after_table = ranger_with_context.group(1)
                    if "dom Human" in context_after_table or (
                        "Halfling" in context_after_table and "Thri-kreen" in context_after_table 
                        and context_after_table.index("Halfling") < context_after_table.index("Though Athas") if "Though Athas" in context_after_table else True
                    ):
                        errors.append("Ranger section has duplicate race text fragments after table")
                
                # Validate Ranger section paragraph count
                # The Ranger section ends at "rangers-followers" header or "wizard" header
                ranger_section = re.search(
                    r'<p id="header-[0-9]+-ranger">.*?</p>\s*<table[^>]*>.*?</table>(.*?)<p id="header-[0-9]+-(rangers-followers|wizard)">',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if ranger_section:
                    # Count paragraphs in the Ranger section
                    ranger_paragraph_count = len(re.findall(r'<p>(?!<span)', ranger_section.group(1)))
                    
                    if ranger_paragraph_count != 9:
                        error_msg = (
                            f"Ranger section in Chapter 3 has {ranger_paragraph_count} paragraphs "
                            f"but should have exactly 9: (1) intro, (2) motivations, (3) weapons/armor, "
                            f"(4) tracking/stealth, (5) species enemy, (6) animal handling, "
                            f"(7) clerical spells, (8) potions, (9) followers."
                        )
                        errors.append(error_msg)
                
                # Validate Rangers Followers table
                rangers_followers_match = re.search(
                    r'<p id="header-[0-9]+-rangers-followers">.*?</p>\s*(<table[^>]*>.*?</table>)',
                    ch3_html_content,
                    re.DOTALL
                )
                
                if rangers_followers_match:
                    rangers_table = rangers_followers_match.group(1)
                    # Count rows
                    rangers_rows = re.findall(r'<tr>', rangers_table)
                    
                    # Should have 24 rows (1 header + 23 data rows)
                    if len(rangers_rows) != 24:
                        error_msg = (
                            f"Rangers Followers table has {len(rangers_rows)} rows but should have 24 "
                            f"(1 header + 23 data rows)"
                        )
                        errors.append(error_msg)
                    
                    # Validate it's a d100 table
                    if "d100 Roll" not in rangers_table:
                        errors.append("Rangers Followers table missing 'd100 Roll' header")
                    
                    if "Follower Type" not in rangers_table:
                        errors.append("Rangers Followers table missing 'Follower Type' header")
                
                # Validate Class Ability Requirements table
                class_ability_table_match = re.search(
                    r'<p[^>]*>\s*<span[^>]*>Class Ability Requirements</span>\s*</p>\s*(<table[^>]*>.*?</table>)',
                    ch3_html_content,
                    re.DOTALL
                )
                if class_ability_table_match:
                    table_html = class_ability_table_match.group(1)
                    rows = re.findall(r'<tr[^>]*>.*?</tr>', table_html, re.DOTALL)
                    
                    if len(rows) != 5:
                        tables_with_issues += 1
                        error_msg = (
                            f"Class Ability Requirements table has {len(rows)} rows but should have 5 "
                            f"(1 header + 4 data rows: Gladiator, Defiler, Templar, Psionicist)"
                        )
                        errors.append(error_msg)
                    elif rows:
                        # Check columns in first row
                        first_row = rows[0]
                        cols = len(re.findall(r'<t[hd][^>]*>', first_row))
                        if cols != 7:
                            tables_with_issues += 1
                            error_msg = (
                                f"Class Ability Requirements table has {cols} columns but should have 7 "
                                f"(Class, Str, Dex, Con, Cha, Int, Wis)"
                            )
                            errors.append(error_msg)
                else:
                    tables_with_issues += 1
                    errors.append("Class Ability Requirements table not found after the subheader")
                
                # Validate individual class ability tables (2 columns, 3 rows each)
                # These tables appear beneath each class name (Fighter, Gladiator, Ranger, etc.)
                class_names = [
                    "Fighter", "Gladiator", "Ranger", "Defiler", "Preserver", "Illusionist",
                    "Cleric", "Druid", "Templar", "Bard", "Thief", "Psionicist"
                ]
                
                for class_name in class_names:
                    # Find the class header in the HTML
                    class_pattern = re.compile(
                        rf'<p[^>]*>\s*<span[^>]*>{class_name}</span>\s*</p>\s*(<table[^>]*>.*?</table>|<p>)',
                        re.DOTALL
                    )
                    class_match = class_pattern.search(ch3_html_content)
                    
                    if class_match:
                        next_element = class_match.group(1)
                        
                        if next_element.startswith('<table'):
                            # Found a table, validate it
                            rows = re.findall(r'<tr[^>]*>.*?</tr>', next_element, re.DOTALL)
                            
                            if len(rows) != 3:
                                tables_with_issues += 1
                                error_msg = (
                                    f"{class_name} ability requirements table has {len(rows)} rows "
                                    f"but should have 3 (Ability Requirements, Prime Requisite, Races Allowed)"
                                )
                                errors.append(error_msg)
                            elif rows:
                                # Check columns in first row
                                first_row = rows[0]
                                cols = len(re.findall(r'<td[^>]*>', first_row))
                                if cols != 2:
                                    tables_with_issues += 1
                                    error_msg = (
                                        f"{class_name} ability requirements table has {cols} columns "
                                        f"but should have 2 (Label, Value)"
                                    )
                                    errors.append(error_msg)
                        else:
                            # No table found after class header
                            tables_with_issues += 1
                            errors.append(f"{class_name} class ability requirements table not found after class header")
                
                # [HEADER_FORMAT] Validate that back-to-top links [^] appear inline with headers
                # Headers should have structure: <p id="header-..."><span ...>Header Text</span> <a ...>[^]</a></p>
                # If there's a newline between </span> and <a>, the link will appear on a separate line
                header_pattern = r'<p id="header-[^"]+"><span[^>]*>([^<]+)</span>\s*<a[^>]*>\[\^?\]</a></p>'
                headers_with_link = re.findall(header_pattern, ch3_html_content)
                
                # Check for headers where the link might be on a separate line (more than one space/newline)
                improper_inline_pattern = r'<p id="header-[^"]+"><span[^>]*>([^<]+)</span>\s*\n\s*<a[^>]*>\[\^?\]</a></p>'
                headers_with_newline = re.findall(improper_inline_pattern, ch3_html_content)
                
                if headers_with_newline:
                    tables_with_issues += 1
                    error_msg = (
                        f"Found {len(headers_with_newline)} headers in Chapter 3 where [^] link appears "
                        f"on a separate line instead of inline. Headers should have format: "
                        f"'<span>Header</span> <a>[^]</a>' without newlines between elements. "
                        f"Check CSS: span[style*=\"color\"] should have display: inline, not display: block."
                    )
                    errors.append(error_msg)
                elif headers_with_link:
                    # All headers have inline links - success
                    pass
                
                # Validate that "Multi-Class and Dual-Class Characters" is a single H1 header,
                # independent of specific header IDs.
                header_matches = re.findall(
                    r'<p id="(header-\d+-[^"]+)"><span([^>]*)>([^<]+)</span>',
                    ch3_html_content
                )
                
                def _is_h1(span_attrs: str) -> bool:
                    return ('font-size: 0.9em' not in span_attrs) and ('font-size: 0.8em' not in span_attrs)
                
                def _strip_roman_prefix(text: str) -> str:
                    return re.sub(r'^[IVXLCDM]+\.\s+', '', text).strip()
                
                h1_headers = [(hid, attrs, text) for hid, attrs, text in header_matches if _is_h1(attrs)]
                normalized_h1_texts = [(_strip_roman_prefix(text), hid, attrs) for hid, attrs, text in h1_headers]
                
                mc_h1 = [(text, hid, attrs) for text, hid, attrs in normalized_h1_texts
                         if text == "Multi-Class and Dual-Class Characters"]
                
                if not mc_h1:
                    tables_with_issues += 1
                    errors.append('Multi-Class and Dual-Class Characters H1 header not found')
                elif len(mc_h1) > 1:
                    tables_with_issues += 1
                    errors.append('Multiple "Multi-Class and Dual-Class Characters" H1 headers found')
                
                # Ensure there is no separate H1 header that is just "Characters"
                stray_characters_h1 = any(text == "Characters" for text, _, _ in normalized_h1_texts)
                if stray_characters_h1:
                    tables_with_issues += 1
                    errors.append(
                        '"Characters" appears as a standalone H1 header; it must be merged into '
                        '"Multi-Class and Dual-Class Characters"'
                    )
                
                # Validate that the paragraph between "Multi-Class Combinations" and "Dwarf" is complete
                # This paragraph was being split across multiple blocks, including a fragment appearing after Elf table
                # Find IDs dynamically for 'Multi-Class Combinations' and the next race header 'Dwarf'
                mc_comb_match = re.search(
                    r'<p id="(header-\d+-[^"]+)"><span[^>]*>[^<]*Multi-Class Combinations[^<]*</span>',
                    ch3_html_content
                )
                dwarf_header_match = re.search(
                    r'<p id="(header-\d+-[^"]+)"><span[^>]*>[^<]*Dwarf[^<]*</span>',
                    ch3_html_content
                )
                
                intro_para_match = None
                if dwarf_header_match:
                    # Determine start header: prefer 'Multi-Class Combinations' if present, else H1 'Multi-Class and Dual-Class Characters'
                    start_id = None
                    if mc_comb_match:
                        start_id = mc_comb_match.group(1)
                    else:
                        # Find the H1 header ID for Multi-Class and Dual-Class Characters
                        h1_mc_match = None
                        for hid, attrs, text in header_matches:
                            if _is_h1(attrs) and _strip_roman_prefix(text) == "Multi-Class and Dual-Class Characters":
                                h1_mc_match = hid
                                break
                        if h1_mc_match:
                            start_id = h1_mc_match
                    
                    if start_id:
                        mc_id = re.escape(start_id)
                    dwarf_id = re.escape(dwarf_header_match.group(1))
                    intro_para_match = re.search(
                        rf'<p id="{mc_id}">.*?</p>(.*?)<p id="{dwarf_id}"',
                        ch3_html_content,
                        re.DOTALL
                    )
                
                if intro_para_match:
                    para_content = intro_para_match.group(1).strip()
                    para_text = re.sub(r'<[^>]+>', ' ', para_content).strip()
                    para_text = re.sub(r'\s+', ' ', para_text)
                    
                    # Check for complete sentence with all parts
                    required_parts = [
                        'Any demihuman character',
                        'requirements may elect',
                        'The following chart lists the possible character class combinations available',
                        'based upon the race of the character'
                    ]
                    
                    missing_parts = [part for part in required_parts if part not in para_text]
                    if missing_parts:
                        tables_with_issues += 1
                        errors.append(
                            f"The paragraph 'Any demihuman character...' between Multi-Class Combinations "
                            f"and Dwarf is incomplete. Missing: {', '.join(missing_parts)}"
                        )
                else:
                    tables_with_issues += 1
                    errors.append("Multi-Class Combinations introductory paragraph not found")
                
                # Validate multi-class combination tables for all 6 races
                multi_class_races = [
                    ("Dwarf", 4),
                    ("Elf or Half-elf", 10),
                    ("Half-giant", 2),
                    ("Halfling", 6),
                    ("Mul", 4),
                    ("Thri-kreen", 2)
                ]
                
                for race_name, expected_rows in multi_class_races:
                    # Find the specific header by text (ID-agnostic)
                    header_match = re.search(
                        rf'<p id="(header-\d+-[^"]+)"[^>]*>.*?<span([^>]*)>[^<]*{re.escape(race_name)}[^<]*</span>.*?</p>',
                        ch3_html_content,
                        re.DOTALL | re.IGNORECASE
                    )
                    
                    if not header_match:
                        tables_with_issues += 1
                        errors.append(f"Multi-class {race_name} header not found")
                        continue
                    
                    # Check for duplicates of this header anywhere in the document
                    header_all = re.findall(
                        rf'<p id="(header-\d+-[^"]+)"[^>]*>.*?<span[^>]*>[^<]*{re.escape(race_name)}[^<]*</span>.*?</p>',
                        ch3_html_content,
                        re.DOTALL | re.IGNORECASE
                    )
                    if len(header_all) > 1:
                        tables_with_issues += 1
                        errors.append(f"Duplicate multi-class header detected for '{race_name}' ({len(header_all)} instances)")
                    
                    race_header_id = header_match.group(1)
                    race_header_span_attrs = header_match.group(2)
                    
                    # Special validation for Half-giant: must be H2 subheader, not H1
                    if race_name == "Half-giant":
                        # Should have subheader font size (0.9em) and no H1 roman numerals
                        if 'font-size: 0.9em' not in race_header_span_attrs:
                            tables_with_issues += 1
                            errors.append("Half-giant header should have subheader styling (font-size: 0.9em)")
                    
                    # Find the table after the header
                    section_pattern = rf'<p id="{re.escape(race_header_id)}"[^>]*>.*?{re.escape(race_name)}.*?</p>(.*?)<p id="header-\d+'
                    section_match = re.search(section_pattern, ch3_html_content, re.DOTALL | re.IGNORECASE)
                    
                    if section_match:
                        section_content = section_match.group(1)
                        tables = re.findall(r'<table[^>]*>(.*?)</table>', section_content, re.DOTALL)
                        
                        if not tables:
                            tables_with_issues += 1
                            errors.append(f"Multi-class {race_name} table not found after its header")
                        else:
                            # Validate row count
                            table_html = tables[0]
                            rows = re.findall(r'<tr>', table_html)
                            
                            if len(rows) != expected_rows:
                                tables_with_issues += 1
                                errors.append(
                                    f"Multi-class {race_name} table has {len(rows)} rows but should have {expected_rows}"
                                )
                            
                            # Check that table has multi-class content (Fighter/, Cleric/, etc.)
                            has_multiclass_content = bool(re.search(r'>Fighter/|>Cleric/|>Mage/', table_html))
                            if not has_multiclass_content:
                                tables_with_issues += 1
                                errors.append(
                                    f"Multi-class {race_name} table found but contains no multi-class combinations"
                                )
                    else:
                        tables_with_issues += 1
                        errors.append(f"Could not find section content for multi-class {race_name} table")
        
        context.items_processed = tables_checked
        
        if errors:
            context.errors.extend(errors)
        
        if warnings:
            context.warnings.extend(warnings)
        
        return ProcessorOutput(
            data={
                "tables_checked": tables_checked,
                "tables_with_issues": tables_with_issues,
                "errors": errors,
                "warnings": warnings,
                "success": len(errors) == 0
            },
            metadata={
                "tables_checked": tables_checked,
                "tables_with_issues": tables_with_issues,
                "error_count": len(errors),
                "warning_count": len(warnings)
            }
        )

