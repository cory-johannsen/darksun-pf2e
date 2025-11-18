"""Chapter 2 (Player Character Races) specific processing logic."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List, Sequence

# Use relative imports from the parent module
from .journal import (
    _normalize_plain_text,
    _collect_cells_from_blocks,
    _build_matrix_from_cells,
    _table_from_rows,
    _compute_bbox_from_cells,
    _join_fragments,
)

# Import extracted functions from chapter_2 sub-modules
from .chapter_2.common import (
    update_block_bbox as _update_block_bbox,
    find_block as _find_block,
)
from .chapter_2.tables import (
    process_table_2_ability_adjustments as _process_table_2_ability_adjustments,
    process_racial_ability_requirements_table as _process_racial_ability_requirements_table,
    process_table_3_racial_class_limits as _process_table_3_racial_class_limits,
    process_other_languages_table as _process_other_languages_table,
)
from .chapter_2.physical_tables import (
    process_height_weight_table as _process_height_weight_table,
    process_starting_age_table as _process_starting_age_table,
)
from .chapter_2.dwarves import fix_dwarves_section_text_ordering as _fix_dwarves_section_text_ordering
from .chapter_2.elves import (
    fix_elves_section_paragraph_breaks as _fix_elves_section_paragraph_breaks,
    fix_elves_roleplaying_paragraph_breaks as _fix_elves_roleplaying_paragraph_breaks,
)
from .chapter_2.half_elves import (
    fix_half_elves_section_paragraph_breaks as _fix_half_elves_section_paragraph_breaks,
    fix_half_elves_roleplaying_paragraph_breaks as _fix_half_elves_roleplaying_paragraph_breaks,
)
from .chapter_2.humans import force_human_paragraph_breaks as _force_human_paragraph_breaks
from .chapter_2.mul import (
    process_mul_exertion_table as _process_mul_exertion_table,
    force_mul_paragraph_breaks as _force_mul_paragraph_breaks,
    force_mul_roleplaying_paragraph_breaks as _force_mul_roleplaying_paragraph_breaks,
)
from .chapter_2.thri_kreen import (
    force_thri_kreen_paragraph_breaks as _force_thri_kreen_paragraph_breaks,
    force_thri_kreen_roleplaying_paragraph_breaks as _force_thri_kreen_roleplaying_paragraph_breaks,
)


# _update_block_bbox - MOVED to chapter_2/common.py


# _find_block - MOVED to chapter_2/common.py


# _process_table_2_ability_adjustments - MOVED to chapter_2/tables.py


# _process_racial_ability_requirements_table - MOVED to chapter_2/tables.py


# _process_table_3_racial_class_limits - MOVED to chapter_2/tables.py


# _fix_dwarves_section_text_ordering - MOVED to chapter_2/chapter_2.py

# _process_other_languages_table - MOVED to chapter_2/physical_tables.py


# _fix_elves_section_paragraph_breaks - MOVED to chapter_2/chapter_2.py


# _fix_elves_roleplaying_paragraph_breaks - MOVED to chapter_2/chapter_2.py


# _fix_half_elves_section_paragraph_breaks - MOVED to chapter_2/chapter_2.py


# _fix_half_elves_roleplaying_paragraph_breaks - MOVED to chapter_2/chapter_2.py


def _fix_half_giants_section_paragraph_breaks(pages: list) -> None:
    """Fix paragraph breaks in the Half-Giants section on pages 6-7.
    
    The Half-Giants section has 10 paragraphs but they get heavily fragmented.
    We use line-level markers for precise control over paragraph breaks.
    """
    paragraph_starts = [
        "Giants dominate many",              # Para 1 - Introduction
        "A half-giant is an enormous",       # Para 2 - Physical description
        "A half-giant character can be",     # Para 3 - Class options
        "Simply put, a half-giant gains",    # Para 4 - Heritage
        "Though no one knows for certain",   # Para 5 - Culture/history (rarely appears)
        "All personal items such as",        # Para 6 - Equipment costs
        "Half-giants sometimes collect",     # Para 7 - Communities
        "Half-giants can switch their",      # Para 8 - Alignment behavior
        "This is not to say",                # Para 9 - Behavioral clarification
        "Half-giant characters add four",    # Para 10 - Ability scores
    ]
    
    # Mid-sentence splits (like the Half-Elves section)
    mid_sentence_splits = [
        "die. Though no one knows for certain",  # Splits para 4
        "die. seem to be a fairly young race",   # Alternative text
    ]
    
    # Process pages 6 and 7
    in_section = False
    for page_idx in [6, 7]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block in page.get("blocks", []):
            if not block.get("lines"):
                continue
            
            first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in block["lines"][0].get("spans", []))).strip()
            
            # Check if entering Half-Giants section
            if "Half-giants" == first_line_text:
                in_section = True
                block["__half_giants_section"] = True
                continue
            
            # Check if leaving section (reached Halflings content)
            if in_section and ("Beyond the Ringing" in first_line_text or "flourish in rains" in first_line_text):
                in_section = False
                break
            
            # Process lines in the section
            if in_section:
                block["__half_giants_section"] = True
                
                for line in block["lines"]:
                    line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                    
                    # Check for paragraph starts at line beginnings
                    for para_start in paragraph_starts:
                        if line_text.startswith(para_start):
                            line["__force_line_break"] = True
                            break
                    
                    # Check for mid-sentence splits
                    for split_pattern in mid_sentence_splits:
                        if split_pattern in line_text and not line_text.startswith(split_pattern.split(". ")[1]):
                            # This line contains a mid-sentence split
                            line["__split_at_mid_sentence"] = split_pattern
                            break



def _merge_ability_scores_header(page: dict) -> None:
    """Merge 'Minimum and Maximum Ability' and 'Scores' into a single header.
    
    Args:
        page: The page data dictionary
    """
    for block in page.get('blocks', []):
        if block.get('type') != 'text':
            continue
        
        lines = block.get('lines', [])
        if len(lines) < 2:
            continue
        
        # Check if this block has the split header
        line0_text = ' '.join(span.get('text', '') for span in lines[0].get('spans', []))
        line1_text = ' '.join(span.get('text', '') for span in lines[1].get('spans', []))
        
        if line0_text.strip() == "Minimum and Maximum Ability" and line1_text.strip() == "Scores":
            # Merge the two lines into one
            merged_text = "Minimum and Maximum Ability Scores"
            
            # Create a merged line with the text from both
            merged_line = {
                'bbox': lines[0]['bbox'],  # Use first line's bbox
                'spans': [{
                    'text': merged_text,
                    'color': lines[0]['spans'][0].get('color', '#ca5804'),
                    'font': lines[0]['spans'][0].get('font', ''),
                    'size': lines[0]['spans'][0].get('size', 14.88)
                }]
            }
            
            # Replace the two lines with the merged line
            block['lines'] = [merged_line] + lines[2:]
            break


def _force_dwarves_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Dwarves section by splitting and marking blocks.
    
    The Dwarves section should have 4 paragraphs:
    1. Physical description (ends with "250 years")
    2. Toil and dedication (starts with "A dwarfs chief love")
    3. Focus mechanics (starts with "The task to which")
    4. Magic and social (starts with "By nature, dwarves")
    """
    blocks_to_insert = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts a new paragraph
        for line_idx, line in enumerate(lines):
            line_text = _normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            if (line_text.startswith("A dwarfs chief") or
                line_text.startswith("A dwarf's chief") or
                line_text.startswith("The task to which") or
                line_text.startswith("By nature, dwarves")):
                
                # Split this block at this line
                if line_idx > 0:
                    # First part: lines before this one
                    first_part_lines = lines[:line_idx]
                    # Second part: this line and after (with force break flag)
                    second_part_lines = lines[line_idx:]
                    
                    # Update current block to only have first part
                    block["lines"] = first_part_lines
                    _update_block_bbox(block)
                    
                    # Create new block for second part
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    _update_block_bbox(second_block)
                    
                    # Mark for insertion after current block
                    blocks_to_insert.append((idx + 1, second_block))
                    break
                else:
                    # This line is the first line, just mark the block
                    block["__force_paragraph_break"] = True
    
    # Insert new blocks
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)


def _force_half_elves_roleplaying_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Half-elves Roleplaying section.
    
    The Half-elves Roleplaying section should have 3 paragraphs:
    1. Self-reliance introduction
    2. Example of half-elf behavior  
    3. Acceptance seeking behavior (starts with "Despite their self-reliance")
    """
    blocks_to_insert = []
    
    for idx, block in enumerate(page.get("blocks", [])):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check if any line starts the third paragraph
        for line_idx, line in enumerate(lines):
            line_text = _normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if this line should start a new paragraph
            if line_text.startswith("Despite their self-reliance"):
                # Split this block at this line
                if line_idx > 0:
                    # First part: lines before this one
                    first_part_lines = lines[:line_idx]
                    # Second part: this line and after (with force break flag)
                    second_part_lines = lines[line_idx:]
                    
                    # Update current block to only have first part
                    block["lines"] = first_part_lines
                    _update_block_bbox(block)
                    
                    # Create new block for second part
                    second_block = {
                        "type": "text",
                        "lines": second_part_lines,
                        "__force_paragraph_break": True
                    }
                    _update_block_bbox(second_block)
                    
                    # Mark for insertion after current block
                    blocks_to_insert.append((idx + 1, second_block))
                    break
                else:
                    # This line is the first line, just mark the block
                    block["__force_paragraph_break"] = True
    
    # Insert new blocks
    for offset, (insert_idx, new_block) in enumerate(blocks_to_insert):
        page["blocks"].insert(insert_idx + offset, new_block)


# _force_human_paragraph_breaks - MOVED to chapter_2/humans.py


# _process_mul_exertion_table - MOVED to chapter_2/mul.py


# _force_mul_paragraph_breaks - MOVED to chapter_2/mul.py


# _force_mul_roleplaying_paragraph_breaks - MOVED to chapter_2/mul.py


# _force_thri_kreen_paragraph_breaks - MOVED to chapter_2/thri_kreen.py


# _force_thri_kreen_roleplaying_paragraph_breaks - MOVED to chapter_2/thri_kreen.py


# _process_height_weight_table - MOVED to chapter_2/physical_tables.py


# _process_starting_age_table - MOVED to chapter_2/physical_tables.py


def _process_aging_effects_table(page: dict) -> None:
    """Process Aging Effects table programmatically (4 columns, 1 header row)."""
    def _line_text(line: dict) -> str:
        return _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
    
    # Section bounds: from "Aging Effects" to the next major header or page end
    start_match = _find_block(page, lambda texts: any("Aging Effects" in t for t in texts))
    if not start_match:
        return
    _, start_block = start_match
    y_min = float(start_block.get("bbox", [0, 0, 0, 0])[3]) + 2.0
    # Try to cap by next colored header if present; otherwise to page bottom
    y_max = float(page.get("height", 0) or 0)

    # If an aging effects table already exists, still remove header label lines within the section bounds
    for table in page.get("tables", []):
        rows = table.get("rows", [])
        if not rows:
            continue
        header = rows[0].get("cells", [])
        if header and header[0].get("text", "").startswith("Race") and any("Middle Age" in c.get("text", "") for c in header):
            # Cleanup header label lines so they don't render as document headers
            header_labels = {"Race", "R a c e", "Middle Age*", "Old Age**", "Venerable***"}
            # Collect race names from this existing table for aggregated line detection
            race_names_lower = []
            for r in rows[1:]:
                cells = r.get("cells", [])
                if cells:
                    nm = (cells[0].get("text") or "").strip().lower()
                    if nm:
                        race_names_lower.append(nm)
            for block in page.get("blocks", []):
                if block.get("type") != "text":
                    continue
                remaining = []
                changed = False
                for line in block.get("lines", []):
                    x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                    if y0 <= y_min or y0 >= y_max:
                        remaining.append(line)
                        continue
                    txt = _line_text(line)
                    if txt in header_labels:
                        changed = True
                        continue
                    # Remove aggregated race list lines using race names from table
                    tlow = txt.lower()
                    matches = sum(1 for rn in race_names_lower if rn and rn in tlow)
                    if matches >= 3:
                        changed = True
                        continue
                    remaining.append(line)
                if changed:
                    block["lines"] = remaining
                    if remaining:
                        _update_block_bbox(block)
                    else:
                        block["bbox"] = [0.0, 0.0, 0.0, 0.0]
            return
    
    # Find column header positions
    race_block = _find_block(page, lambda texts: any(t.strip().lower().replace(" ", "") == "race" or t == "R a c e" for t in texts))
    mid_block = _find_block(page, lambda texts: any("Middle Age" in t for t in texts))
    old_block = _find_block(page, lambda texts: any("Old Age" in t for t in texts))
    ven_block = _find_block(page, lambda texts: any("Venerable" in t for t in texts))
    
    if not (race_block and mid_block and old_block and ven_block):
        return
    
    race_split_x = float(race_block[1]["bbox"][2]) + 5.0
    def _header_center(block: dict, target: str) -> float | None:
        for line in block.get("lines", []):
            txt = _line_text(line)
            if txt == target:
                x0, _, x1, _ = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                return (x0 + x1) / 2.0
        return None
    mid_cx = _header_center(mid_block[1], "Middle Age*")
    old_cx = _header_center(old_block[1], "Old Age**")
    ven_cx = _header_center(ven_block[1], "Venerable***")
    if mid_cx is None or old_cx is None or ven_cx is None:
        return
    
    y_tol = 3.5
    # Build potential row y positions from mid/old/ven numeric cells
    candidate_y: List[float] = []
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            y_center = (y0 + y1) / 2.0
            if y_center <= y_min or y_center >= y_max:
                continue
            cx = (x0 + x1) / 2.0
            txt = _line_text(line)
            # Accept numbers or '-' under any of the three numeric columns
            if (abs(cx - mid_cx) <= 40.0 or abs(cx - old_cx) <= 40.0 or abs(cx - ven_cx) <= 40.0):
                if txt and (txt.isdigit() or txt == "-" or txt in {"25", "30", "67", "40", "60", "80", "100", "120", "140", "160", "185", "200"}):
                    # The constants above are only filters for numeric-like content; not hardcoded mapping
                    candidate_y.append(y_center)
    if not candidate_y:
        return
    candidate_y.sort()
    unique_y: List[float] = []
    for y_c in candidate_y:
        if not unique_y or all(abs(y_c - y_prev) > y_tol for y_prev in unique_y):
            unique_y.append(y_c)
    
    def _find_near(x_target: float, y_center: float, *, allow_dash: bool = False) -> str:
        best_txt = ""
        best_dx = 1e9
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                if abs(((ly0 + ly1) / 2.0) - y_center) > y_tol:
                    continue
                cx = (lx0 + lx1) / 2.0
                dx = abs(cx - x_target)
                if dx < best_dx:
                    txt = _line_text(line)
                    if not txt:
                        continue
                    if txt == "-" and not allow_dash:
                        continue
                    if not (txt.isdigit() or (allow_dash and txt == "-")):
                        continue
                    best_dx = dx
                    best_txt = txt
        return best_txt
    
    def _find_race(y_center: float) -> str:
        best = ""
        best_x = 1e9
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                lx0, ly0, lx1, ly1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
                if abs(((ly0 + ly1) / 2.0) - y_center) > y_tol:
                    continue
                if lx1 >= race_split_x:
                    continue
                txt = _line_text(line)
                if not txt or any(k in txt for k in ["Race", "Middle Age", "Old Age", "Venerable", "*"]):
                    continue
                if lx0 < best_x:
                    best_x = lx0
                    best = txt
        return best
    
    header_row = {
        "cells": [
            {"text": "Race"},
            {"text": "Middle Age*"},
            {"text": "Old Age**"},
            {"text": "Venerable***"},
        ]
    }
    data_rows: List[dict] = []
    for y_c in unique_y:
        race = _find_race(y_c)
        if not race:
            continue
        middle = _find_near(mid_cx, y_c, allow_dash=True)
        old = _find_near(old_cx, y_c, allow_dash=True)
        venerable = _find_near(ven_cx, y_c, allow_dash=True)
        if any([middle, old, venerable]):
            data_rows.append({"cells": [{"text": race}, {"text": middle or "-"}, {"text": old or "-"}, {"text": venerable or "-"}]})
    
    if not data_rows:
        return
    
    # Compute a stable bbox anchored just below the "Aging Effects" header
    col_xs = [
        float(race_block[1]["bbox"][0]), float(race_block[1]["bbox"][2]),
        float(mid_block[1]["bbox"][0]), float(mid_block[1]["bbox"][2]),
        float(old_block[1]["bbox"][0]), float(old_block[1]["bbox"][2]),
        float(ven_block[1]["bbox"][0]), float(ven_block[1]["bbox"][2]),
    ]
    ax_left = max(0.0, min(col_xs) - 8.0)
    ax_right = min(float(page.get("width", 612.0) or 612.0), max(col_xs) + 8.0)
    astart_y = float(start_block.get("bbox", [0, 0, 0, 0])[3]) + 6.0
    alast_row_y = max(unique_y) if unique_y else astart_y + 20.0
    aend_y = min(y_max, alast_row_y + 18.0)
    bbox = [ax_left, astart_y, ax_right, aend_y]
    
    table = {"rows": [header_row] + data_rows, "header_rows": 1, "bbox": bbox}
    # Remove any pre-existing malformed tables in this section bounds
    cleaned_tables = []
    for t in page.get("tables", []):
        tb = [float(c) for c in t.get("bbox", [0, 0, 0, 0])]
        ty0, ty1 = tb[1], tb[3]
        if ty1 < y_min - 5.0 or ty0 > y_max + 5.0:
            cleaned_tables.append(t)
    page["tables"] = cleaned_tables
    page.setdefault("tables", []).append(table)

    # Remove header label lines within the section bounds so they don't render as document headers
    # This includes: "Race"/"R a c e", "Middle Age*", "Old Age**", "Venerable***"
    header_labels = {"Race", "R a c e", "Middle Age*", "Old Age**", "Venerable***"}
    for block in page.get("blocks", []):
        if block.get("type") != "text":
            continue
        remaining = []
        changed = False
        for line in block.get("lines", []):
            x0, y0, x1, y1 = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            if y0 <= y_min or y0 >= y_max:
                remaining.append(line)
                continue
            txt = _line_text(line)
            if txt in header_labels:
                changed = True
                continue
            remaining.append(line)
        if changed:
            block["lines"] = remaining
            if remaining:
                _update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]

def apply_chapter_2_adjustments(section_data: dict) -> None:
    """Apply all Chapter 2 (Player Character Races) specific adjustments.
    
    Args:
        section_data: The section data dictionary containing pages to process.
    """
    pages = section_data.get("pages", [])
    if not pages:
        return

    # Page 0: Merge ability scores header, Table 2 and Racial Ability Requirements
    if len(pages) > 0:
        page0 = pages[0]
        _merge_ability_scores_header(page0)
        _process_table_2_ability_adjustments(page0)
        _process_racial_ability_requirements_table(page0)

    # Page 1: Table 3 - Racial Class And Level Limits
    if len(pages) > 1:
        page1 = pages[1]
        _process_table_3_racial_class_limits(page1)
    
    # Page 2: Force paragraph breaks in Dwarves section
    if len(pages) > 2:
        page2 = pages[2]
        _force_dwarves_paragraph_breaks(page2)

    # Page 2: Dwarves section text fix and Other Languages table
    if len(pages) > 2:
        page2 = pages[2]
        _fix_dwarves_section_text_ordering(page2)
        _process_other_languages_table(page2)  # Process the language list table
    
    # Page 4: Force paragraph breaks in Half-elves Roleplaying section
    if len(pages) > 4:
        page4 = pages[4]
        _force_half_elves_roleplaying_paragraph_breaks(page4)

    # Page 3: Elves section paragraph breaks
    if len(pages) > 3:
        page3 = pages[3]
        _fix_elves_section_paragraph_breaks(page3)

    # Page 4: Elves Roleplaying section paragraph breaks
    if len(pages) > 4:
        page4 = pages[4]
        _fix_elves_roleplaying_paragraph_breaks(page4)

    # Pages 4-5: Half-Elves section paragraph breaks
    _fix_half_elves_section_paragraph_breaks(pages)

    # Pages 5-6: Half-Elves Roleplaying section paragraph breaks
    _fix_half_elves_roleplaying_paragraph_breaks(pages)

    # Pages 6-7: Half-Giants section paragraph breaks
    _fix_half_giants_section_paragraph_breaks(pages)
    
    # Page 10: Human and Mul section paragraph breaks
    # Page 10 (page_number=15): Human section paragraph breaks
    if len(pages) > 10:
        page10 = pages[10]
        _force_human_paragraph_breaks(page10)
    
    # Pages 11-12 (page_number=16-17): Mul section paragraph breaks and table
    # Mul content spans two pages, so we need to process both
    if len(pages) > 11:
        page11 = pages[11]
        _process_mul_exertion_table(page11)
        _force_mul_paragraph_breaks(page11)
    
    if len(pages) > 12:
        page12 = pages[12]
        _process_mul_exertion_table(page12)
        _force_mul_paragraph_breaks(page12)
        _force_mul_roleplaying_paragraph_breaks(page12)
        _force_thri_kreen_paragraph_breaks(page12)
        _force_thri_kreen_roleplaying_paragraph_breaks(page12)
    
    # Pages 13-14 (page_number=18-19): Thri-kreen section paragraph breaks
    # Thri-kreen content may span multiple pages
    if len(pages) > 13:
        page13 = pages[13]
        _force_thri_kreen_paragraph_breaks(page13)
        _force_thri_kreen_roleplaying_paragraph_breaks(page13)
    
    if len(pages) > 14:
        page14 = pages[14]
        _force_thri_kreen_paragraph_breaks(page14)
        _force_thri_kreen_roleplaying_paragraph_breaks(page14)
    
    # Locate and process "Other Characteristics" sub-tables by header text rather than fixed indices
    targets = {
        "Height and Weight": _process_height_weight_table,
        "Starting Age": _process_starting_age_table,
        "Aging Effects": _process_aging_effects_table,
    }
    for page in pages:
        if not page.get("blocks"):
            continue
        # Collect normalized block texts on this page
        page_texts = []
        for block in page.get("blocks", []):
            for line in block.get("lines", []):
                page_texts.append(
                    _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                )
        # Apply processors when their headers are present
        for header, processor in targets.items():
            if any(header in t for t in page_texts):
                processor(page)

    # Final normalization: ensure Age section has exactly two separate tables
    for page in pages:
        if not page.get("blocks"):
            continue
        has_age = any(
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))) == "Age"
            for block in page.get("blocks", [])
            for line in block.get("lines", [])
        )
        if not has_age:
            continue
        # Identify y-range from Age H1 to end of page (subsections included)
        age_blocks = [
            block for block in page.get("blocks", [])
            if any(_normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))) == "Age"
                   for line in block.get("lines", []))
        ]
        if not age_blocks:
            continue
        age_y_min = float(age_blocks[0].get("bbox", [0, 0, 0, 0])[1]) - 2.0
        age_y_max = float(page.get("height", 0) or 0)
        # Keep only the two intended tables within this y-range
        kept_tables = []
        for t in page.get("tables", []):
            tb = [float(c) for c in t.get("bbox", [0, 0, 0, 0])]
            ty0, ty1 = tb[1], tb[3]
            if ty1 < age_y_min or ty0 > age_y_max:
                kept_tables.append(t)
                continue
            # Inside Age region: keep only tables with expected headers
            rows = t.get("rows", [])
            if not rows:
                continue
            header_cells = [c.get("text", "") for c in rows[0].get("cells", [])]
            header_joined = " ".join(header_cells).lower()
            is_starting_age = (
                "race" in header_joined
                and "base age" in header_joined
                and "variable" in header_joined
                and "max age range (base + variable)" in header_joined
            )
            is_aging_effects = (
                "race" in header_joined
                and "middle age" in header_joined
                and "old age" in header_joined
                and "venerable" in header_joined
            )
            if is_starting_age or is_aging_effects:
                kept_tables.append(t)
        page["tables"] = kept_tables

    # Final cleanup: remove stray table label headers that may have flowed across page boundaries
    age_label_texts = {"Base Age", "Race", "Variable", "(Base + Variable)", "Maximum Age Range"}
    for page in pages:
        if not page.get("blocks"):
            continue
        # Only consider pages that contain Age-related content
        page_has_age_content = any(
            any(token in _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
                for token in ("Age", "Starting Age", "Aging Effects"))
            for block in page.get("blocks", [])
            for line in block.get("lines", [])
        )
        if not page_has_age_content:
            continue
        # Remove any colored header lines matching the age label texts
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            remaining = []
            changed = False
            for line in block.get("lines", []):
                txt = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                if txt in age_label_texts:
                    changed = True
                    continue
                # Remove aggregated race list paragraphs in Age region (heuristic)
                import re as _re
                caps = _re.findall(r"\b[A-Z][A-Za-z-]*\b", txt)
                if len(caps) >= 5:
                    changed = True
                    continue
                remaining.append(line)
            if changed:
                block["lines"] = remaining
                if remaining:
                    _update_block_bbox(block)
                else:
                    block["bbox"] = [0.0, 0.0, 0.0, 0.0]

