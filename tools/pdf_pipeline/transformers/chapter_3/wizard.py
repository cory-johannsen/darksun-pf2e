"""
Wizard class (Defiler & Preserver) specific processing for Chapter 3.

This module handles PDF-level adjustments for Defiler and Preserver wizard classes,
including table extraction and paragraph break forcing.
"""

from .common import normalize_plain_text, update_block_bbox


def extract_defiler_experience_table(page: dict) -> None:
    """Extract and format the Defiler Experience Levels table on page 29.
    
    The table shows XP progression for defiler wizards (faster than preservers).
    """
    # TODO: Implement table extraction
    pass


def force_wizard_classes_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Wizard Classes overview section.
    
    This is for the "Wizard Classes" header section (pages 0-1), not the detailed "Wizard" section.
    """
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
            
            # These patterns are for the overview section only
            if (line_text.startswith("The preserver attempts to use magic") or
                line_text.startswith("The defiler is a wizard who activates") or
                line_text.startswith("The illusionist is a specialist wizard")):
                
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


def force_wizard_section_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the detailed Wizard class section.
    
    This is for the "Wizard" header section (page 7), which should have 6 paragraphs.
    Breaks at: "The preserver", "The defiler", "Illusionists,", "Wizards are restricted", "All wizards in Dark Sun"
    """
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
            # P2: "The preserver learns..." - starts paragraph 2
            # P3: "The defiler, on the other hand..." - starts paragraph 3
            # P4: "Illusionists, a specialized..." - starts paragraph 4
            # P5: "Wizards are restricted..." - starts paragraph 5
            # P6: "All wizards in Dark Sun..." - starts paragraph 6
            if (line_text.startswith("The preserver learns to tap magical") or
                line_text.startswith("The defiler, on the other hand, casts") or
                line_text.startswith("Illusionists, a specialized") or
                line_text.startswith("Wizards are restricted") or
                line_text.startswith("All wizards in Dark Sun")):
                
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


def force_defiler_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Defiler section.
    
    The Defiler section should have 4 paragraphs with breaks at:
    "A defiler who has an intelligence score", "Just like preservers, defilers can", "The actual amount of damage"
    """
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
            if (line_text.startswith("A defiler who has an intelligence score") or
                line_text.startswith("Just like preservers, defilers can") or
                line_text.startswith("The actual amount of damage")):
                
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
    
    # After applying breaks, merge "Just like preservers" with "Specialist defilers" blocks
    # They should be part of the same paragraph
    blocks = page.get("blocks", [])
    for idx in range(len(blocks) - 1):
        if blocks[idx].get("type") != "text":
            continue
        lines = blocks[idx].get("lines", [])
        text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        
        if "Just like preservers, defilers can opt to specialize" in text:
            # Check if the next block is "Specialist defilers..."
            next_block = blocks[idx + 1]
            if next_block.get("type") == "text":
                next_lines = next_block.get("lines", [])
                next_text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in next_lines)
                
                if "Specialist defilers are treated" in next_text:
                    # Merge the next block into this one
                    blocks[idx]["lines"].extend(next_lines)
                    update_block_bbox(blocks[idx])
                    # Clear the next block
                    blocks[idx + 1]["lines"] = []
                    blocks[idx + 1]["bbox"] = [0.0, 0.0, 0.0, 0.0]
                    break


def extract_defiler_experience_levels_table(page: dict) -> None:
    """Extract the Defiler Experience Levels table.
    
    This table has 3 columns and 21 rows (including header row).
    """
    blocks = page.get("blocks", [])
    
    # Find the "Defiler Experience Levels" header and make it a subheader
    header_idx = None
    for idx, block in enumerate(blocks):
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        if not lines:
            continue
        
        text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        
        if "Defiler Experience Levels" in text:
            header_idx = idx
            # Make it a subheader by setting font size to 8.88
            for line in lines:
                for span in line.get("spans", []):
                    span["size"] = 8.88
            break
    
    if header_idx is None:
        return
    
    # The table data should be in subsequent blocks
    # We need to collect the experience points, levels, and hit dice
    # Based on the pattern, this is likely an existing malformed table that needs reconstruction
    
    # Define the correct table data (20 data rows + 1 header row)
    table_data = [
        ["Level", "XP", "Hit Dice (d4)"],
        ["1", "0", "1"],
        ["2", "1,750", "2"],
        ["3", "3,500", "3"],
        ["4", "7,000", "4"],
        ["5", "14,000", "5"],
        ["6", "28,000", "6"],
        ["7", "42,000", "7"],
        ["8", "63,000", "8"],
        ["9", "94,500", "9"],
        ["10", "180,000", "10"],
        ["11", "270,000", "10+1"],
        ["12", "540,000", "10+2"],
        ["13", "820,000", "10+3"],
        ["14", "1,080,000", "10+4"],
        ["15", "1,350,000", "10+5"],
        ["16", "1,620,000", "10+6"],
        ["17", "1,870,000", "10+7"],
        ["18", "2,160,000", "10+8"],
        ["19", "2,430,000", "10+9"],
        ["20", "2,700,000", "10+10"]
    ]
    
    # Create the table
    table = {
        "bbox": [50, blocks[header_idx].get("bbox", [0, 0, 0, 0])[1] + 20, 500, 400],
        "rows": [{"cells": [{"text": cell} for cell in row]} for row in table_data],
        "header_rows": 1
    }
    
    # Add the table to the page
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table)
    
    # Clear any existing malformed text blocks that contain this data
    # Look for blocks with level numbers, XP values, or hit dice
    # Also clear the duplicate column headers that appear before the table
    for block in blocks[header_idx + 1:]:
        if block.get("type") != "text":
            continue
        lines = block.get("lines", [])
        text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
        text_stripped = text.strip()
        
        # Clear duplicate column headers (either as separate blocks or concatenated)
        if (text_stripped in ["Level", "Hit Dice (d4)", "Defiler"] or
            ("Level" in text and "Defiler" in text and "Hit Dice" in text and len(text) < 50)):
            block["lines"] = []
            block["bbox"] = [0.0, 0.0, 0.0, 0.0]
            continue
        
        # Check if this block contains table data fragments
        # Look for XP values or hit dice patterns
        if (any(xp in text for xp in ["1,750", "3,500", "7,000", "14,000", "28,000", "42,000", "63,000", 
                                       "94,500", "180,000", "270,000", "540,000", "820,000", "1,080,000", 
                                       "1,350,000", "1,620,000", "1,870,000", "2,160,000", "2,430,000", "2,700,000"]) or
            ("1 0 + 2" in text or "1 0 + 3" in text or "1 0 + 4" in text)):
            block["lines"] = []
            block["bbox"] = [0.0, 0.0, 0.0, 0.0]


def force_preserver_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Preserver section.
    
    The Preserver section should have 2 paragraphs with break at:
    "Dark Sun preservers are treated"
    
    Strategy: Merge the first 6 blocks (up to "environment.") into one,
    then split at "Dark Sun preservers are treated".
    """
    blocks_to_insert = []
    blocks = page.get("blocks", [])
    
    # Find the first text block after the Preserver header (should be block 1)
    first_text_idx = None
    for idx, block in enumerate(blocks):
        if block.get("type") == "text":
            lines = block.get("lines", [])
            text = "".join("".join(span.get("text", "") for span in line.get("spans", [])) for line in lines)
            if "wizard of the old" in text.lower():
                first_text_idx = idx
                break
    
    if first_text_idx is None:
        return
    
    # Merge blocks 1-6 (up to and including "to the nearby environment.")
    # These should all be part of the first paragraph
    merged_lines = []
    blocks_to_clear = []
    
    for idx in range(first_text_idx, min(first_text_idx + 6, len(blocks))):
        if blocks[idx].get("type") == "text":
            merged_lines.extend(blocks[idx].get("lines", []))
            if idx > first_text_idx:
                blocks_to_clear.append(idx)
    
    # Update the first block with all merged lines
    blocks[first_text_idx]["lines"] = merged_lines
    update_block_bbox(blocks[first_text_idx])
    
    # Clear the other blocks
    for idx in blocks_to_clear:
        blocks[idx]["lines"] = []
        blocks[idx]["bbox"] = [0.0, 0.0, 0.0, 0.0]
    
    # Now find and split at "Dark Sun preservers are treated"
    for idx, block in enumerate(list(blocks)):
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
            if line_text.startswith("Dark Sun preservers are treated"):
                
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

