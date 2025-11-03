"""Chapter 2 (Player Character Races) specific processing logic."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List, Sequence

# Use relative imports from the parent module
from .journal_v2 import (
    _normalize_plain_text,
    _collect_cells_from_blocks,
    _build_matrix_from_cells,
    _table_from_rows,
    _compute_bbox_from_cells,
    _join_fragments,
)


def _update_block_bbox(block: dict) -> None:
    """Update block bbox based on its lines."""
    lines = block.get("lines", [])
    if not lines:
        return
    x0 = min(float(line.get("bbox", [0, 0, 0, 0])[0]) for line in lines)
    y0 = min(float(line.get("bbox", [0, 0, 0, 0])[1]) for line in lines)
    x1 = max(float(line.get("bbox", [0, 0, 0, 0])[2]) for line in lines)
    y1 = max(float(line.get("bbox", [0, 0, 0, 0])[3]) for line in lines)
    block["bbox"] = [x0, y0, x1, y1]


def _find_block(page: dict, predicate) -> tuple[int, dict] | None:
    """Find a block in a page that matches the predicate."""
    for idx, block in enumerate(page.get("blocks", [])):
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if predicate(texts):
            return idx, block
    return None


def _process_table_2_ability_adjustments(page0: dict) -> None:
    """Process Table 2: Ability Adjustments on page 0."""
    found = _find_block(page0, lambda texts: any(text == "Table 2: Ability Adjustments" for text in texts))
    if not found:
        return
    
    heading_idx, heading_block = found
    next_heading = _find_block(page0, lambda texts: any(text == "Racial Ability Requirements" for text in texts))
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    y_min = heading_bbox[1] - 2.0
    y_max = (
        float(next_heading[1]["bbox"][1]) - 2.0
        if next_heading
        else float(page0.get("height", 0) or 0)
    )
    x_min = heading_bbox[0] - 10.0
    x_max = heading_bbox[2] + 160.0
    table_blocks = []
    for idx, block in enumerate(page0.get("blocks", [])):
        if idx == heading_idx:
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if not block.get("lines"):
            continue
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        if bbox[0] < x_min or bbox[2] > x_max:
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page0, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=2, row_tolerance=4.0)
    allowed = {
        "Race",
        "Dwarf",
        "Elf",
        "Half-Elf",
        "Half-Giant",
        "Halfling",
        "Mul",
        "Thri-kreen",
    }
    merged_rows: List[List[str]] = []
    for row in rows:
        if not row:
            continue
        key = row[0]
        if key in allowed:
            merged_rows.append(row[:])
            continue
        if merged_rows and (not key or key == ""):
            value = row[1] if len(row) > 1 else ""
            if value:
                combined = _join_fragments([merged_rows[-1][1], value])
                merged_rows[-1][1] = combined
    filtered_rows = []
    for row in merged_rows:
        if not row:
            continue
        row[1] = row[1].rstrip(",")
        filtered_rows.append(row)
    if len(filtered_rows) >= 2:
        bbox = _compute_bbox_from_cells(cells)
        table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
        page0.setdefault("tables", []).append(table)
        for idx in table_blocks:
            page0["blocks"][idx]["lines"] = []


def _process_racial_ability_requirements_table(page0: dict) -> None:
    """Process Racial Ability Requirements table on page 0."""
    header_match = _find_block(
        page0,
        lambda texts: "Ability" in texts and {"Dwarf", "Elf", "H-Elf", "H-giant", "Halfling", "Mul", "Thri-kreen"}.issubset(set(texts)),
    )
    if not header_match:
        return
    
    header_idx, header_block = header_match
    header_bbox = [float(coord) for coord in header_block.get("bbox", [0, 0, 0, 0])]
    y_min = header_bbox[1] - 2.0
    y_max = float(page0.get("height", 0) or 0)
    table_blocks = []
    for idx in range(header_idx, len(page0.get("blocks", []))):
        block = page0["blocks"][idx]
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if idx != header_idx and any(text.startswith("Table ") for text in texts):
            break
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page0, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=8, row_tolerance=4.0)
    allowed = {
        "Ability",
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    }
    filtered_rows = [row for row in rows if row and row[0] in allowed]
    if len(filtered_rows) < 2:
        return
    
    bbox = _compute_bbox_from_cells(cells)
    page_width = float(page0.get("width", 0) or 0)
    column_width = (
        max(header_bbox[2] - header_bbox[0], (page_width / 2) - 20.0)
        if page_width
        else header_bbox[2] - header_bbox[0]
    )
    bbox[0] = header_bbox[0]
    bbox[2] = bbox[0] + column_width
    if page_width:
        bbox[2] = min(bbox[2], page_width - 10.0)
    bbox[1] = max(bbox[1], header_bbox[3] + 2.0)
    bbox[3] = max(bbox[3], bbox[1] + 4.0)
    table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
    page0.setdefault("tables", []).append(table)
    for idx in table_blocks:
        if idx == header_idx:
            continue
        page0["blocks"][idx]["lines"] = []

    cleanup_labels = {
        "Ability",
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
        "Dwarf",
        "Elf",
        "H-Elf",
        "H-giant",
        "Halfling",
        "Mul",
        "Thri-kreen",
    }
    # Reposition the Racial Ability Requirements table and header to come before Racial Ability Adjustments
    # Find the target positions
    racial_req_header_idx = None
    racial_adj_header_idx = None
    for idx, block in enumerate(page0.get("blocks", [])):
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if any(text == "Racial Ability Requirements" for text in texts):
            racial_req_header_idx = idx
        elif any(text == "Racial Ability Adjustments" for text in texts):
            racial_adj_header_idx = idx
    
    if racial_req_header_idx is not None and racial_adj_header_idx is not None:
        # Get the requirements header block
        req_header_block = page0["blocks"][racial_req_header_idx]
        req_header_bbox = [float(c) for c in req_header_block.get("bbox", [0, 0, 0, 0])]
        
        # Get the adjustments header block
        adj_header_block = page0["blocks"][racial_adj_header_idx]
        adj_header_bbox = [float(c) for c in adj_header_block.get("bbox", [0, 0, 0, 0])]
        
        # Calculate new position for requirements header (just above adjustments header)
        new_req_y = adj_header_bbox[1] - 20.0  # Place it 20 pixels above adjustments
        
        # Update requirements header position
        height = req_header_bbox[3] - req_header_bbox[1]
        req_header_block["bbox"] = [req_header_bbox[0], new_req_y, req_header_bbox[2], new_req_y + height]
        for line in req_header_block.get("lines", []):
            line_bbox = [float(c) for c in line.get("bbox", [0, 0, 0, 0])]
            line_height = line_bbox[3] - line_bbox[1]
            line["bbox"] = [line_bbox[0], new_req_y, line_bbox[2], new_req_y + line_height]
        
        # Update the requirements table position if it exists
        for table in page0.get("tables", []):
            table_bbox = [float(c) for c in table.get("bbox", [0, 0, 0, 0])]
            # Identify requirements table by column count (8 columns)
            if table.get("rows") and len(table["rows"][0].get("cells", [])) == 8:
                table_height = table_bbox[3] - table_bbox[1]
                new_table_y = new_req_y + height + 4.0
                table["bbox"] = [table_bbox[0], new_table_y, table_bbox[2], new_table_y + table_height]
    
    # Sort tables on page 0 by Y-coordinate to ensure correct rendering order
    if page0.get("tables"):
        page0["tables"].sort(key=lambda t: float(t.get("bbox", [0, 0, 0, 0])[1]))
    
    for block in page0.get("blocks", []):
        lines = block.get("lines", [])
        if not lines:
            continue
        remaining = []
        for line in lines:
            text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            if text in cleanup_labels:
                continue
            remaining.append(line)
        if len(remaining) != len(lines):
            block["lines"] = remaining
            if remaining:
                _update_block_bbox(block)
            else:
                block["bbox"] = [0.0, 0.0, 0.0, 0.0]


def _process_table_3_racial_class_limits(page1: dict) -> None:
    """Process Table 3: Racial Class And Level Limits on page 1."""
    match = _find_block(
        page1,
        lambda texts: any(text == "Table 3: Racial Class And Level Limits" for text in texts),
    )
    if not match:
        return
    
    heading_idx, heading_block = match
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    page_width = float(page1.get("width", 0) or 0)
    y_min = heading_bbox[1] - 2.0

    def _is_footer(texts: Sequence[str]) -> bool:
        if not texts:
            return False
        first = texts[0]
        return first.startswith("U:") or first.startswith("Any #") or first.startswith("-:") or first.startswith("The Player")

    footer = None
    for idx in range(heading_idx + 1, len(page1.get("blocks", []))):
        block = page1["blocks"][idx]
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if _is_footer(texts):
            footer = block
            break

    y_max = float(footer.get("bbox", [0, 0, 0, page1.get("height", 0) or 0])[1]) - 2.0 if footer else float(page1.get("height", 0) or 0)

    table_blocks = []
    for idx, block in enumerate(page1.get("blocks", [])):
        if idx < heading_idx:
            continue
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if idx != heading_idx and any(text.startswith("Table ") for text in texts):
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page1, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=9, row_tolerance=4.0)
    allowed = {
        "Class",
        "Bard",
        "Cleric",
        "Defiler",
        "Druid",
        "Fighter",
        "Gladiator",
        "Illusionist",
        "Preserver",
        "Psionicist",
        "Ranger",
        "Templar",
        "Thief",
    }
    filtered_rows = [row for row in rows if row and (row[0] in allowed)]
    if len(filtered_rows) < 2:
        return
    
    bbox = _compute_bbox_from_cells(cells)
    table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
    page1.setdefault("tables", []).append(table)
    for idx in table_blocks:
        if idx == heading_idx:
            continue
        page1["blocks"][idx]["lines"] = []

    # Place the "Table 3" heading directly above the table
    heading_height = heading_bbox[3] - heading_bbox[1]
    heading_top = max(bbox[1] - heading_height - 2.0, 0.0)
    heading_bottom = heading_top + heading_height
    heading_block["bbox"] = [
        bbox[0],
        heading_top,
        bbox[0] + (heading_bbox[2] - heading_bbox[0]),
        heading_bottom,
    ]
    for line in heading_block.get("lines", []):
        line_height = float(line.get("bbox", [0, 0, 0, 0])[3]) - float(line.get("bbox", [0, 0, 0, 0])[1])
        line["bbox"] = [
            heading_block["bbox"][0],
            heading_bottom - line_height,
            heading_block["bbox"][2],
            heading_bottom,
        ]
    _update_block_bbox(heading_block)


def _fix_dwarves_section_text_ordering(page2: dict) -> None:
    """Fix text ordering in the Dwarves section on page 2.
    
    The sentence "The task to which a dwarf is presently committed" appears at the end
    but should be at the beginning of the paragraph starting with "is referred to as his focus".
    The ending "for compromise in the mind of a dwarf." should be appended to the paragraph 
    ending with "There is very little room".
    """
    # First pass: Find the relevant blocks
    focus_start_block = None  # Block with "is referred to as his focus"
    focus_end_block = None  # Block with "There is very little room"
    duplicate_block_idx = None
    ending_line_to_append = None
    
    for block_idx, block in enumerate(page2.get("blocks", [])):
        if not block.get("lines"):
            continue
        
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            for line in block.get("lines", [])
        ]
        combined = " ".join(texts)
        
        # Find the focus start block
        if combined.startswith("is referred to as his focus") or any(text.startswith("is referred to as his focus") for text in texts):
            focus_start_block = block
        
        # Find the focus end block
        if "There is very little room" in combined:
            focus_end_block = block
        
        # Find the duplicate block with both phrases
        if "The task to which a dwarf is presently committed" in combined and "for compromise in the mind of a dwarf" in combined:
            duplicate_block_idx = block_idx
            # Extract the ending line
            for line in block.get("lines", []):
                line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                # Only save the line with "for compromise" (not the "The task" line)
                if "for compromise in the mind of a dwarf" in line_text and "The task to which a dwarf is presently committed" not in line_text:
                    ending_line_to_append = deepcopy(line)
                    break
    
    # Second pass: Modify the blocks
    if focus_start_block and focus_end_block and ending_line_to_append:
        # Prepend "The task to which a dwarf is presently committed " to the focus start block
        if focus_start_block.get("lines"):
            first_line = focus_start_block["lines"][0]
            first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
            
            if first_line_text.startswith("is referred to as his focus"):
                # Modify the first span of this line
                if first_line.get("spans"):
                    first_span = first_line["spans"][0]
                    original_text = first_span.get("text", "")
                    # Only prepend if it hasn't been done already
                    if not original_text.startswith("The task to which a dwarf"):
                        first_span["text"] = "The task to which a dwarf is presently committed " + original_text
        
        # Append "for compromise in the mind of a dwarf." to the focus end block
        focus_end_block["lines"].append(ending_line_to_append)
        _update_block_bbox(focus_end_block)
    
    # Remove the duplicate block
    if duplicate_block_idx is not None and duplicate_block_idx < len(page2.get("blocks", [])):
        page2["blocks"].pop(duplicate_block_idx)


def _process_other_languages_table(page2: dict) -> None:
    """Process Other Languages table on page 2."""
    match = _find_block(page2, lambda texts: any(text == "Other Languages" for text in texts))
    if not match:
        return
    
    heading_idx, heading_block = match
    heading_bbox = [float(coord) for coord in heading_block.get("bbox", [0, 0, 0, 0])]
    y_min = heading_bbox[1] - 2.0
    next_heading = _find_block(page2, lambda texts: any(text == "Dwarves" for text in texts))
    y_max = float(next_heading[1]["bbox"][1]) - 2.0 if next_heading else float(page2.get("height", 0) or 0)

    table_blocks = []
    for idx in range(heading_idx + 1, len(page2.get("blocks", []))):
        block = page2["blocks"][idx]
        if not block.get("lines"):
            continue
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        if bbox[1] < y_min or bbox[1] > y_max:
            continue
        width = bbox[2] - bbox[0]
        if width > 140.0:
            continue
        table_blocks.append(idx)

    if not table_blocks:
        return
    
    cells = _collect_cells_from_blocks(page2, table_blocks)
    if not cells:
        return
    
    rows = _build_matrix_from_cells(cells, expected_columns=2, row_tolerance=4.0)
    allowed_first = {
        "Aarakocra*",
        "Belgoi",
        "Ettercap",
        "Giant",
        "Goblin Spider",
        "Jozhal*",
        "Meazel",
        "Yuan-ti",
    }
    allowed_second = {
        "Anakore",
        "Braxat",
        "Genie*",
        "Gith",
        "Halfling",
        "Kenku*",
        "Thri-kreen",
    }
    filtered_rows = []
    for row in rows:
        if not row:
            continue
        if len(row) >= 2 and (row[0] in allowed_first or row[1] in allowed_second):
            filtered_rows.append(row)
    if filtered_rows:
        bbox = _compute_bbox_from_cells(cells)
        table = _table_from_rows(filtered_rows, header_rows=0, bbox=bbox)
        page2.setdefault("tables", []).append(table)
        for idx in table_blocks:
            page2["blocks"][idx]["lines"] = []


def _fix_elves_section_paragraph_breaks(page3: dict) -> None:
    """Fix paragraph breaks in the Elves section on page 3.
    
    The Elves section has 11 paragraphs but they get merged into 1 huge paragraph
    due to the two-column layout. We need to add paragraph break hints based on
    sentence endings that should start new paragraphs.
    """
    # The Elves section starts with specific sentences that should be paragraph breaks.
    # We'll mark these blocks to force paragraph breaks in the renderer.
    
    paragraph_starts = [
        "The dunes and steppes of Athas",  # Para 1
        "Elves are all brethren",  # Para 2
        "Individually, tribal elves",  # Para 3
        "Elves use no beasts",  # Para 4
        "While most elven tribes",  # Para 5
        "Elven culture",  # Para 6
        "A player character elf",  # Para 7
        "Elves are masterful warriors",  # Para 8
        "Elves gain a bonus to surprise",  # Para 9
        "Elves have no special knowledge",  # Para 10
        "With nimble fingers",  # Para 11
    ]
    
    # Find blocks that start these paragraphs and mark them
    for block in page3.get("blocks", []):
        if not block.get("lines"):
            continue
        
        # Check first line of block
        first_line = block["lines"][0]
        first_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
        
        # If this block starts with one of our paragraph starts, mark it
        for para_start in paragraph_starts:
            if first_text.startswith(para_start):
                # Add a marker to force paragraph break
                block["__force_paragraph_break"] = True
                break


def _fix_elves_roleplaying_paragraph_breaks(page4: dict) -> None:
    """Fix paragraph breaks in the Roleplaying section after Elves on page 4.
    
    The Roleplaying section has 3 paragraphs but they get merged into 1.
    We need to force paragraph breaks at specific sentences.
    
    The 3 paragraphs should be:
    1. "Elves have no great love..."
    2. "When encountering outsiders...will be taking animal or magical transportation."
    3. "Elves never ride on beasts..."
    """
    paragraph_starts = [
        "When encountering outsiders",  # Para 2
        "Elves never ride on beasts",   # Para 3
    ]
    
    # Find the Roleplaying block and mark lines that should start new paragraphs
    for block in page4.get("blocks", []):
        if not block.get("lines"):
            continue
        
        # Check if this is the Roleplaying block (contains "Roleplaying:" at start)
        first_line = block["lines"][0]
        first_text = _normalize_plain_text("".join(span.get("text", "") for span in first_line.get("spans", []))).strip()
        
        if not first_text.startswith("Roleplaying:"):
            continue
        
        # Mark lines that should start new paragraphs
        for line in block["lines"]:
            line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
            for para_start in paragraph_starts:
                if line_text.startswith(para_start):
                    # Mark this line to force a paragraph break
                    line["__force_line_break"] = True
                    break
            
            # Special handling: If a line contains "transportation." followed by other content,
            # split it at that point
            if "will be taking animal or magical transportation." in line_text:
                # Check if there's content after "transportation." in the same line
                if line_text.index("transportation.") + len("transportation.") < len(line_text) - 1:
                    # There's more content after "transportation." - need to split mid-line
                    # Mark this line for splitting at "transportation."
                    line["__split_at_transportation"] = True



def _fix_half_elves_section_paragraph_breaks(pages: list) -> None:
    """Fix paragraph breaks in the Half-Elves section on pages 4-5.
    
    The Half-Elves section has 11 paragraphs but they get merged together.
    We need to force paragraph breaks at specific sentences.
    """
    paragraph_starts = [
        "Elves and humans travel",          # Para 1 - Introduction
        "A half-elf is generally tall",     # Para 2 - Physical description
        "A half-elf'salife is typically",   # Para 3 - Social hardships (note: typo in PDF, no space)
        # Para 4 handled separately - sentence starts mid-line: ". Rarely do half-"
        "Intolerance, however, has given",  # Para 5 - Self-reliance
        "The skills involved in survival",  # Para 6 - Survival skills
        "Coincidentally, faced with",       # Para 7 - Alien races
        "Also, some half-elves turn",       # Para 8 - Animal companions
        "Half-elves add one to their",      # Para 9 - Ability scores
        "A half-elf character can choose",  # Para 10 - Class options
        "A half-elf gains some benefits",   # Para 11 - Level benefits
    ]
    
    # Process pages 4 and 5
    for page_idx in [4, 5]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block in page.get("blocks", []):
            if not block.get("lines"):
                continue
            
            # Check each line in the block
            for line in block["lines"]:
                line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                
                # Check for regular paragraph starts
                for para_start in paragraph_starts:
                    if line_text.startswith(para_start):
                        # Mark this line to force a paragraph break
                        line["__force_line_break"] = True
                        break
                
                # Special case: "Rarely" starts mid-line after a period
                # The sentence ". Rarely do half-elves" spans pages 4-5
                if ". Rarely do half" in line_text:
                    # This line needs to be split - mark it for special handling
                    line["__split_at_rarely"] = True
                
                # Special case: "Also" starts mid-line after a period
                # The sentence ". Also, some half-elves turn" 
                if ". Also, some half-elves" in line_text:
                    # This line needs to be split - mark it for special handling
                    line["__split_at_also"] = True


def _fix_half_elves_roleplaying_paragraph_breaks(pages: list) -> None:
    """Fix paragraph breaks in the Half-elves Roleplaying section on pages 5-6.
    
    The Roleplaying section has 3 paragraphs but they get heavily fragmented
    across two-column layout. We need to mark blocks to prevent unwanted splits.
    
    Note: Due to PDF layout, "For example..." appears before the "Roleplaying:" header
    in the block order, so we need to handle it specially.
    """
    # Mark the specific blocks that should start new paragraphs
    paragraph_start_texts = [
        "For example, when a half-elf",     # Para 2
        "Despite their self-reliance",      # Para 3
    ]
    
    # First pass: find the Roleplaying section and mark all blocks
    roleplaying_start_idx = -1
    roleplaying_end_idx = -1
    for_example_idx = -1
    
    for page_idx in [5, 6]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            if not block.get("lines"):
                continue
            
            first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in block["lines"][0].get("spans", []))).strip()
            
            if "For example, when a half-elf" in first_line_text:
                for_example_idx = (page_idx, block_idx)
            elif "Roleplaying: Half-elves pride" in first_line_text:
                roleplaying_start_idx = (page_idx, block_idx)
            elif "Half-giants" in first_line_text:
                roleplaying_end_idx = (page_idx, block_idx)
                break
    
    # Second pass: mark the blocks
    in_roleplaying_section = False
    for page_idx in [5, 6]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            if not block.get("lines"):
                continue
            
            # Check if this is the "For example" block (special case before header)
            if for_example_idx and (page_idx, block_idx) == for_example_idx:
                block["__roleplaying_section"] = True
                block["__force_paragraph_break"] = True
                continue
            
            # Check if this is the start of the Roleplaying section
            if roleplaying_start_idx and (page_idx, block_idx) == roleplaying_start_idx:
                in_roleplaying_section = True
                block["__roleplaying_section"] = True
                continue
            
            # Check if we've reached the end
            if roleplaying_end_idx and (page_idx, block_idx) == roleplaying_end_idx:
                in_roleplaying_section = False
                break
            
            # If we're in the Roleplaying section, mark the block
            if in_roleplaying_section:
                block["__roleplaying_section"] = True
                
                # Check if this block should start a new paragraph
                first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in block["lines"][0].get("spans", []))).strip()
                for para_start in paragraph_start_texts:
                    if first_line_text.startswith(para_start):
                        block["__force_paragraph_break"] = True
                        break


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



def apply_chapter_2_adjustments(section_data: dict) -> None:
    """Apply all Chapter 2 (Player Character Races) specific adjustments.
    
    Args:
        section_data: The section data dictionary containing pages to process.
    """
    pages = section_data.get("pages", [])
    if not pages:
        return

    # Page 0: Table 2 and Racial Ability Requirements
    if len(pages) > 0:
        page0 = pages[0]
        _process_table_2_ability_adjustments(page0)
        _process_racial_ability_requirements_table(page0)

    # Page 1: Table 3 - Racial Class And Level Limits
    if len(pages) > 1:
        page1 = pages[1]
        _process_table_3_racial_class_limits(page1)

    # Page 2: Dwarves section text fix and Other Languages table
    if len(pages) > 2:
        page2 = pages[2]
        _fix_dwarves_section_text_ordering(page2)
        _process_other_languages_table(page2)

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

