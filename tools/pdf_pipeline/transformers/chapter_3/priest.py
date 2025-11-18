"""
Priest class (Cleric, Druid, Templar) specific processing for Chapter 3.

This module handles PDF-level adjustments for priest classes,
including table extraction and paragraph break forcing.
"""

from .common import normalize_plain_text, update_block_bbox


def extract_templar_spell_progression_table(page: dict) -> None:
    """Extract and format the Templar Spell Progression table on page 35.
    
    The table shows spell slots per level for templar priests.
    8 columns (Templar Level + 7 spell levels), 22 rows (2 header rows + 20 data rows).
    
    Correct header structure:
    - Row 1: "Templar Level" (rowspan=2, spans rows 1-2) | "Spell Level" (colspan=7, spans columns 2-8)
    - Row 2: "1" | "2" | "3" | "4" | "5" | "6" | "7" (first cell covered by rowspan from row 1)
    
    Identification: In the malformed source data, row 1 columns 1-8 are all "-", which helps identify this table.
    
    Source data issues:
    - Double digit level numbers (10-20) may include whitespace
    - There is a typo in the source: '17' appears instead of '19' for level 19
    
    Reference data (correct spell progression):
    Level 1: - - - - - - -    Level 11: 4 3 3 2 1 - -
    Level 2: 1 - - - - - -    Level 12: 4 4 3 3 1 - -
    Level 3: 1 1 - - - - -    Level 13: 4 4 4 3 2 - -
    Level 4: 2 1 - - - - -    Level 14: 5 5 4 4 2 1 -
    Level 5: 3 2 - - - - -    Level 15: 6 6 5 5 3 2 1
    Level 6: 3 2 1 - - - -    Level 16: 7 7 6 6 4 3 1
    Level 7: 3 2 2 - - - -    Level 17: 7 7 7 7 5 4 2
    Level 8: 3 3 2 1 - - -    Level 18: 8 8 8 8 6 4 2
    Level 9: 3 3 3 1 - - -    Level 19: 9 9 9 9 7 5 3
    Level 10: 3 3 3 2 - - -   Level 20: 9 9 9 9 9 6 4
    
    The borderless table detection creates tables in the old "tables" array format.
    """
    # Reference data: correct templar spell progression (authoritative source)
    TEMPLAR_SPELL_PROGRESSION = {
        1:  ["-", "-", "-", "-", "-", "-", "-"],
        2:  ["1", "-", "-", "-", "-", "-", "-"],
        3:  ["1", "1", "-", "-", "-", "-", "-"],
        4:  ["2", "1", "-", "-", "-", "-", "-"],
        5:  ["3", "2", "-", "-", "-", "-", "-"],
        6:  ["3", "2", "1", "-", "-", "-", "-"],
        7:  ["3", "2", "2", "-", "-", "-", "-"],
        8:  ["3", "3", "2", "1", "-", "-", "-"],
        9:  ["3", "3", "3", "1", "-", "-", "-"],
        10: ["3", "3", "3", "2", "-", "-", "-"],
        11: ["4", "3", "3", "2", "1", "-", "-"],
        12: ["4", "4", "3", "3", "1", "-", "-"],
        13: ["4", "4", "4", "3", "2", "-", "-"],
        14: ["5", "5", "4", "4", "2", "1", "-"],
        15: ["6", "6", "5", "5", "3", "2", "1"],
        16: ["7", "7", "6", "6", "4", "3", "1"],
        17: ["7", "7", "7", "7", "5", "4", "2"],
        18: ["8", "8", "8", "8", "6", "4", "2"],
        19: ["9", "9", "9", "9", "7", "5", "3"],
        20: ["9", "9", "9", "9", "9", "6", "4"]
    }
    
    # Find the existing malformed table in the tables array
    # Use the identification clue: look for a table with a row of all dashes
    if "tables" not in page or not page["tables"]:
        return
    
    # Find the Templar Spell Progression table by looking for rows with all dashes
    table_idx = None
    for idx, table in enumerate(page.get("tables", [])):
        rows = table.get("rows", [])
        # Look for a row where columns 1-8 are all "-"
        for row in rows[:5]:  # Check first few rows
            cells = row.get("cells", [])
            if len(cells) >= 8:
                # Check if columns 1-8 (indices 1-8) are all dashes or empty
                dash_count = sum(1 for i in range(1, min(8, len(cells))) 
                               if cells[i].get("text", "").strip() in ["-", ""])
                if dash_count >= 6:  # At least 6 out of 7 columns are dashes
                    table_idx = idx
                    break
        if table_idx is not None:
            break
    
    if table_idx is None:
        # Fall back to first table if identification fails
        table_idx = 0
    
    # We have the reference data, so we don't need to extract from the malformed source.
    # Just use the authoritative spell progression data.
    level_data = TEMPLAR_SPELL_PROGRESSION
    
    # Build the corrected table with proper headers and all 20 levels
    corrected_rows = []
    
    # Add header rows
    # Row 1: "Templar Level" (rowspan=2, spans rows 1-2) | "Spell Level" (colspan=7, spans columns 2-8)
    header_row_1 = {
        "cells": [
            {"text": "Templar Level", "rowspan": 2},  # Spans 2 rows (first column)
            {"text": "Spell Level", "colspan": 7}     # Spans 7 columns (columns 2-8), no empty cells needed
        ]
    }
    # Row 2: First cell is covered by rowspan, then spell levels 1-7
    header_row_2 = {
        "cells": [
            {"text": "1"},
            {"text": "2"},
            {"text": "3"},
            {"text": "4"},
            {"text": "5"},
            {"text": "6"},
            {"text": "7"}
        ]
    }
    corrected_rows.append(header_row_1)
    corrected_rows.append(header_row_2)
    
    # Add data rows for levels 1-20
    for level in range(1, 21):
        if level in level_data:
            spell_slots = level_data[level]
        else:
            # Missing level - use all dashes
            spell_slots = ["-", "-", "-", "-", "-", "-", "-"]
        
        data_row = {
            "cells": [{"text": str(level)}] + [{"text": slot} for slot in spell_slots]
        }
        corrected_rows.append(data_row)
    
    # Find the "Templar Spell Progression" header block to get its bbox
    # The table should appear after this header
    header_bbox = None
    header_block_idx = None
    blocks_to_clear = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            if "Templar Spell Progression" in all_text:
                header_bbox = block.get("bbox", [0, 0, 0, 0])
                header_block_idx = idx
                
                # Clean up the header text - remove "Templar Spell Level" part
                # Keep only "Templar Spell Progression"
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if "Templar Spell Progression" in text:
                            span["text"] = "Templar Spell Progression"
                        elif "Templar" in text or "Spell Level" in text:
                            span["text"] = ""
            
            # Clear other malformed table-related text blocks
            elif any(pattern in all_text for pattern in [
                "L e v e l",
                "Spell Level",
                "Templar Spell Level"
            ]):
                blocks_to_clear.append(idx)
    
    # Clear the malformed blocks
    for idx in blocks_to_clear:
        if idx < len(page["blocks"]):
            page["blocks"][idx]["lines"] = []
            page["blocks"][idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    # Set table bbox to appear after the header
    if header_bbox:
        # Place table just below the header
        table_bbox = [header_bbox[0], header_bbox[3] + 5, header_bbox[2], header_bbox[3] + 10]
    else:
        table_bbox = [0, 200, 500, 205]
    
    # Replace the existing table with the corrected one
    corrected_table = {
        "rows": corrected_rows,
        "header_rows": 2,
        "bbox": table_bbox
    }
    
    # CRITICAL FIX: Replace ALL tables with just the one corrected table
    # The borderless table detection often creates hundreds of malformed tables
    # from fragmented spell progression data. We only want the single corrected table.
    page["tables"] = [corrected_table]
    
    # Clear any remaining text blocks that look like table data remnants
    # These are blocks with patterns like "- - - - - -" or contain numbers and dashes
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text
            
            all_text = all_text.strip()
            
            if not all_text:
                continue
            
            # Check if this looks like table data remnants
            # Count dashes, numbers, and spaces
            dash_count = all_text.count("-")
            space_count = all_text.count(" ")
            digit_count = sum(1 for c in all_text if c.isdigit())
            total_chars = len(all_text)
            
            # Very short blocks of pure dashes (like "- - - - -")
            if len(all_text) < 50 and dash_count > 5:
                block["lines"] = []
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]
                continue
            
            # Longer blocks that are mostly dashes, spaces, and numbers
            if len(all_text) > 10 and (dash_count + space_count + digit_count) / total_chars > 0.8:
                # Additional check: should not contain common words
                if not any(word in all_text.lower() for word in ["the", "templars", "libraries", "spells", "newly"]):
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]




def force_priest_section_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the detailed Priest section.
    
    The Priest section should have 6 paragraphs with breaks at:
    "Templars worship the sorcerer-kings ", "Clerics worship one of the four elemental planes:",
    "The spells available to a cleric depend upon his", "The spells themselves are received directly from",
    "Druids associate themselves with the spirits"
    """
    breaks = [
        "Templars worship the sorcerer-kings",
        "Clerics worship one of the four elemental planes:",
        "The spells available to a cleric depend upon his",
        "The spells themselves are received directly from",
        "Druids associate themselves with the spirits"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text):
                    if line_idx > 0:
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
                    else:
                        block["__force_paragraph_break"] = True
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_spheres_of_magic_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Spheres of Magic section.
    
    The Spheres of Magic section should have 3 paragraphs with breaks at:
    "Otherwise, priest characters are created and used",
    "The use of priestly magic never adversely affects"
    """
    breaks = [
        "Otherwise, priest characters are created and used",
        "The use of priestly magic never adversely affects"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text):
                    if line_idx > 0:
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
                    else:
                        block["__force_paragraph_break"] = True
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_cleric_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Cleric section.
    
    The Cleric section should have 4 paragraphs with breaks at:
    "A cleric must have a Wisdom score of 3",
    "Every cleric must choose one elemental plane as",
    "Clerics concentrate their efforts on magical and"
    """
    breaks = [
        "A cleric must have a Wisdom score of 3",
        "Every cleric must choose one elemental plane as",
        "Clerics concentrate their efforts on magical and"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text):
                    if line_idx > 0:
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
                    else:
                        block["__force_paragraph_break"] = True
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_cleric_powers_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Cleric powers section following Elemental Plane of Water.
    
    This section should have 10 paragraphs with breaks at:
    "Clerics are not strictly forbidden from using",
    "Clerics have power over undead, just as described",
    "Athasian clerics never gain followers simply as a",
    "Clerics do gain certain powers with regard to their",
    "A cleric can gate material directly from his",
    "Air so gated comes in the form of a terrific wind,",
    "The shape of the gated material may be dictated",
    "Though not a granted power, a cleric can conjure",
    "In all cases where the rules here"
    """
    breaks = [
        "Clerics are not strictly forbidden from using",
        "Clerics have power over undead, just as described",
        "Athasian clerics never gain followers simply as a",
        "Clerics do gain certain powers with regard to their",
        "A cleric can gate material directly from his",
        "Air so gated comes in the form of a terrific wind,",
        "The shape of the gated material may be dictated",
        "Though not a granted power, a cleric can conjure",
        "In all cases where the rules here"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text):
                    if line_idx > 0:
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
                    else:
                        block["__force_paragraph_break"] = True
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_druid_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Druid section.
    
    The Druid section should have 8 paragraphs with breaks at:
    "Every druid must choose one geographic feature",
    "Lower-level druids may travel widely in the world.",
    "Upon reaching 12th level, the druid",
    "Druids tend not to bother or even encounter",
    "A druid who has both a Wisdom and Charisma",
    "Druids have no restrictions as to what weapons",
    "A druid has major access to spells from any"
    
    Note: Need to merge blocks so "Lower-level druids" and "During their time of wandering"
    are in the same paragraph.
    """
    # First, merge the blocks that should be together
    # Find "Lower-level druids" block and merge it with subsequent blocks until "Upon reaching"
    lower_level_idx = None
    upon_reaching_idx = None
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        all_text = "".join(
            "".join(span.get("text", "") for span in line.get("spans", []))
            for line in block.get("lines", [])
        )
        
        if "Lower-level druids may travel" in all_text:
            lower_level_idx = idx
        if "Upon reaching 12th level" in all_text:
            upon_reaching_idx = idx
            break
    
    # Merge blocks between lower_level_idx and upon_reaching_idx
    if lower_level_idx is not None and upon_reaching_idx is not None and lower_level_idx < upon_reaching_idx:
        merged_lines = []
        for idx in range(lower_level_idx, upon_reaching_idx):
            block = page["blocks"][idx]
            if block.get("type") == "text":
                merged_lines.extend(block.get("lines", []))
                if idx > lower_level_idx:
                    # Clear this block
                    block["lines"] = []
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]
        
        # Update the first block with all merged lines
        if lower_level_idx < len(page["blocks"]):
            page["blocks"][lower_level_idx]["lines"] = merged_lines
            update_block_bbox(page["blocks"][lower_level_idx])
    
    # Now apply paragraph breaks
    breaks = [
        "Every druid must choose one geographic feature",
        "Lower-level druids may travel widely in the world.",
        "Upon reaching 12th level, the druid",
        "Druids tend not to bother or even encounter",
        "A druid who has both a Wisdom and Charisma",
        "Druids have no restrictions as to what weapons",
        "A druid has major access to spells from any"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text):
                    if line_idx > 0:
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
                    else:
                        block["__force_paragraph_break"] = True
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_druid_granted_powers_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Druid granted powers section.
    
    The section beginning "When in his guarded lands" should have 7 paragraphs with breaks at:
    "When in his guarded lands",
    "A druid can remain concealed from others while",
    "A druid may speak with animals",
    "A druid may speak with plants",
    "A druid can live without water",
    "A druid can shapechange",
    "In all cases where the rules"
    """
    breaks = [
        "When in his guarded lands",
        "A druid can remain concealed from others while",
        "A druid may speak with animals",
        "A druid may speak with plants",
        "A druid can live without water",
        "A druid can shapechange",
        "In all cases where the rules"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line to see if it should start a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            for break_text in breaks:
                if line_text.startswith(break_text) or break_text in line_text:
                    # If this is the first line, just mark the block
                    if line_idx == 0:
                        block["__force_paragraph_break"] = True
                        break
                    else:
                        # Need to split this block
                        first_part_lines = lines[:line_idx]
                        second_part_lines = lines[line_idx:]
                        
                        block["lines"] = first_part_lines
                        update_block_bbox(block)
                        
                        second_block = {
                            "type": "text",
                            "lines": second_part_lines,
                            "__force_paragraph_break": True
                        }
                        update_block_bbox(second_block)
                        
                        blocks_to_insert.append((idx + 1, second_block))
                        break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def fix_templar_ability_table(page: dict) -> None:
    """Fix the Templar ability requirements table by appending "Half-elf" to Races Allowed.
    
    The "Half-elf" text appears in a separate block after the Templar header and should be
    part of the Races Allowed row in the ability table.
    
    The table is stored in the page["tables"] array (old format from _create_class_ability_table).
    """
    # Find the Templar ability table in the tables array
    templar_table = None
    templar_table_idx = None
    
    for idx, table in enumerate(page.get("tables", [])):
        rows = table.get("rows", [])
        if len(rows) >= 3:
            # Check first row for "Wisdom" and "Intelligence 10" - Templar's requirements
            first_row_text = str(rows[0].get("cells", []))
            if "Wisdom" in first_row_text and "Intelligence" in first_row_text:
                templar_table = table
                templar_table_idx = idx
                break
    
    if not templar_table:
        return
    
    # Find the "Half-elf" block that follows the Templar header
    # Look for it after the "Templar" header block
    half_elf_block_idx = None
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") == "text":
            all_text = ""
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                all_text += line_text + " "
            
            all_text = all_text.strip()
            if all_text == "Half-elf":
                half_elf_block_idx = idx
                break
    
    if half_elf_block_idx is None:
        return
    
    # Append "Half-elf" to the Races Allowed row (row 2, cell 1)
    rows = templar_table.get("rows", [])
    
    if len(rows) >= 3:
        cells = rows[2].get("cells", [])
        if len(cells) >= 2:
            # Third row is Races Allowed - append ", Half-elf" to the value
            current_races = cells[1].get("text", "")
            if "Half-elf" not in current_races:
                cells[1]["text"] = current_races.rstrip(",").rstrip() + ", Half-elf"
    
    # Clear the original "Half-elf" block
    if half_elf_block_idx < len(page["blocks"]):
        page["blocks"][half_elf_block_idx]["lines"] = []
        page["blocks"][half_elf_block_idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]




def force_templar_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Templar class details section.
    
    Two sections need paragraph breaks:
    1. The initial description - break at "Templars gain levels as do clerics,"
    2. The abilities section (starting with "The libraries of the templars") - multiple breaks
    """
    # Break points for the abilities section
    ability_breaks = [
        "A templar character may be either neutral or",
        "Templars are initially trained as warriors and, at",
        "Templars have power over undead, but only to",
        "As a templar advances in level, he gains certain",
        "A templar can call upon a slave to do whatever he",
        "A templar can pass judgement upon a slave at",
        "A templar can legally enter the house of a",
        "A templar can requisition soldiers when he",
        "A templar can accuse a freeman of disloyalty or",
        "A templar can gain access to all areas in palaces",
        "A templar can draw upon the city treasury for",
        "At templar can pass judgement on a freeman",  # Note: typo "At" instead of "A"
        "A templar can pass judgement on a freeman",  # Also check correct version
        "A templar can accuse a noble when he reaches",
        "A templar can grant a pardon to any condemned",
        "As a rule, a templar can have no more than one",
        "The templar hierarchy is measured strictly by",
        "Templars never gain followers as do clerics"
    ]
    
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line for break points
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line contains any break point
            should_break = False
            
            # Check the first break point
            if "Templars gain levels as do clerics" in line_text:
                should_break = True
            
            # Check ability section breaks (startswith to handle line continuations)
            for break_text in ability_breaks:
                if line_text.startswith(break_text):
                    should_break = True
                    break
            
            if should_break:
                # If this is the first line, just mark the block
                if line_idx == 0:
                    block["__force_paragraph_break"] = True
                    break
                else:
                    # Need to split this block
                    first_part_lines = lines[:line_idx]
                    second_part_lines = lines[line_idx:]
                    
                    block["lines"] = first_part_lines
                    update_block_bbox(block)
                    
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    update_block_bbox(second_block)
                    
                    blocks_to_insert.append((idx + 1, second_block))
                    break
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




def force_priest_classes_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Priest Classes section by splitting and marking blocks.
    
    The Priest Classes section should have 4 paragraphs based on user-specified breaks.
    """
    blocks_to_insert = []
    
    for idx, block in enumerate(list(page.get("blocks", []))):  # Use list() to avoid mutation issues
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph (user-specified breaks)
            # P2: "The cleric..." - starts paragraph 2 (cleric description)
            # P3: "The templar..." - starts paragraph 3 (templar description)
            # P4: "The druid..." - starts paragraph 4 (druid description)
            if (line_text.startswith("The cleric is a free-willed priest, tending the needs") or
                line_text.startswith("The templar is a regimented priest devoted to a") or
                line_text.startswith("The druid is a priest tied to a particular feature or")):
                
                # Split this block at this line
                if line_idx > 0:
                    first_part_lines = lines[:line_idx]
                    second_part_lines = lines[line_idx:]
                    
                    block["lines"] = first_part_lines
                    update_block_bbox(block)
                    
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    update_block_bbox(second_block)
                    
                    blocks_to_insert.append((idx + 1, second_block))
                    break
                else:
                    block["__force_paragraph_break"] = True
    
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)




