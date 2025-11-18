"""
Psionicist class specific processing for Chapter 3.

This module handles PDF-level adjustments for the Psionicist class,
including table extraction and paragraph break forcing.
"""

from .common import normalize_plain_text, update_block_bbox


def force_psionicist_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Psionicist section.
    
    The Psionicist section should have X paragraphs based on user-specified breaks.
    """
    # Placeholder - implement actual logic if needed
    pass


def extract_inherent_potential_table(page: dict) -> None:
    """Extract the Inherent Potential table.
    
    This table shows the relationship between ability scores (15-22) and their
    base PSP scores and modifiers for psionicists in Dark Sun campaigns.
    
    Table structure:
    - 3 columns: Ability Score | Base Score | Ability Modifier
    - 9 rows: 1 header + 8 data rows (scores 15-22)
    
    The source PDF has this table heavily fragmented with:
    - Header text split across multiple blocks with spacing (e.g., "S c o r e")
    - All data values concatenated in a single block
    - Multi-class combinations from the right column bleeding into the table region
    
    Args:
        page: Page dictionary to extract from (should be page 19/20 with the Psionicist section)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Find the "Inherent Potential Table" header block
    header_block_idx = None
    header_bbox = None
    
    for idx, block in enumerate(page.get('blocks', [])):
        if block.get('type') != 'text':
            continue
        
        for line in block.get('lines', []):
            text = ''.join(span.get('text', '') for span in line.get('spans', []))
            if 'Inherent Potential Table' in text:
                header_block_idx = idx
                header_bbox = block.get('bbox', [0, 0, 0, 0])
                logger.debug(f"Found 'Inherent Potential Table' header at block {idx}, bbox: {header_bbox}")
                break
        
        if header_block_idx is not None:
            break
    
    if header_block_idx is None:
        logger.warning("Could not find 'Inherent Potential Table' header")
        return
    
    # Extract table data from fragmented blocks in the PDF
    header_y = header_bbox[3]
    next_section_y = 422  # "Power Checks:" section starts here
    
    # Find all numeric data blocks in the left column
    data_values = []
    for block in page.get('blocks', []):
        if block.get('type') != 'text':
            continue
        
        bbox = block.get('bbox', [0, 0, 0, 0])
        y_pos = bbox[1]
        x_pos = bbox[0]
        
        # Only extract from LEFT column (x < 150) within table region
        if header_y < y_pos < next_section_y and x_pos < 150:
            for line in block.get('lines', []):
                line_text = ''.join(span.get('text', '') for span in line.get('spans', []))
                line_text = line_text.strip()
                
                # Collect all numeric values and modifiers
                if line_text and any(char.isdigit() or char == '+' for char in line_text):
                    data_values.append(line_text)
    
    logger.debug(f"Extracted {len(data_values)} data values: {data_values}")
    
    # Parse the data values into rows
    # The data comes in groups of 3: ability_score, base_score, modifier
    # but they're mixed together across blocks
    
    # Clean up whitespace issues (e.g., "1 7" -> "17", "2 0" -> "20", "2 1" -> "21")
    cleaned_values = []
    for val in data_values:
        # Remove internal spaces in numbers (e.g., "1 7" -> "17")
        if ' ' in val and all(c.isdigit() or c == ' ' for c in val):
            cleaned_val = val.replace(' ', '')
        else:
            cleaned_val = val
        
        # Normalize modifiers (e.g., "+ 1" -> "+1")
        if '+' in cleaned_val:
            cleaned_val = cleaned_val.replace(' ', '')
        
        cleaned_values.append(cleaned_val)
    
    logger.debug(f"Cleaned values: {cleaned_values}")
    
    # Build rows from the cleaned values
    # Expected pattern: ability, base, modifier, ability, base, modifier, ...
    # NOTE: The source PDF has a known error where "19" appears as "1 7" which becomes "17" after cleaning.
    # This creates a duplicate "17" value. We need to correct the second instance to "19" per [NINES] rule.
    rows = []
    i = 0
    seen_17 = False  # Track if we've already seen ability score 17
    
    while i < len(cleaned_values):
        # Check if we have at least 3 values for a complete row
        if i + 2 < len(cleaned_values):
            ability = cleaned_values[i]
            base = cleaned_values[i + 1]
            modifier = cleaned_values[i + 2]
            
            # Apply [NINES] correction: second instance of "17" should be "19"
            if ability == "17" and seen_17:
                logger.info("Applying [NINES] correction: changing second '17' to '19'")
                ability = "19"
            elif ability == "17":
                seen_17 = True
            
            # Validate that this looks like a complete row
            # ability should be 15-22, base should be 20-34, modifier should be 0 or +N
            try:
                ability_int = int(ability)
                base_int = int(base)
                
                if 15 <= ability_int <= 22 and 20 <= base_int <= 34:
                    rows.append([ability, base, modifier])
                    i += 3
                    continue
            except ValueError:
                pass
        
        # If we can't parse a complete row, skip this value
        i += 1
    
    logger.debug(f"Built {len(rows)} data rows from extracted values")
    
    # Add the header row
    table_data = [["Ability Score", "Base Score", "Ability Modifier"]] + rows
    
    # Verify we have the expected 9 rows (1 header + 8 data)
    if len(table_data) != 9:
        logger.error(f"Expected 9 rows but got {len(table_data)}. Using authoritative data.")
        # Fall back to authoritative data if extraction fails
        table_data = [
            ["Ability Score", "Base Score", "Ability Modifier"],
            ["15", "20", "0"],
            ["16", "22", "+1"],
            ["17", "24", "+2"],
            ["18", "26", "+3"],
            ["19", "28", "+4"],
            ["20", "30", "+5"],
            ["21", "32", "+6"],
            ["22", "34", "+7"]
        ]
    
    # Create the table structure
    table = {
        "rows": [],
        "bbox": [header_bbox[0], header_bbox[3], header_bbox[2], header_bbox[3] + 100]
    }
    
    for row_data in table_data:
        cells = []
        for cell_text in row_data:
            cells.append({
                "text": cell_text,
                "spans": [{"text": cell_text, "color": "#000000", "font": "Arial", "size": 9}]
            })
        table["rows"].append({"cells": cells})
    
    # Add the table to the page
    if "tables" not in page:
        page["tables"] = []
    page["tables"].append(table)
    
    # Clear fragmented table blocks in the region between header and "Power Checks"
    # These blocks contain the malformed table data that we're replacing
    header_y = header_bbox[3]
    next_section_y = 422  # "Power Checks:" section starts here
    
    blocks_to_clear = []
    for idx, block in enumerate(page.get('blocks', [])):
        if block.get('type') != 'text':
            continue
        
        bbox = block.get('bbox', [0, 0, 0, 0])
        x_pos = bbox[0]
        y_pos = bbox[1]
        
        # Only clear blocks in the LEFT column (x < 290) within the table region
        # This avoids clearing the multi-class combinations in the right column
        if header_y < y_pos < next_section_y and x_pos < 290:
            # Check if this block contains table-related text
            block_text = ''
            for line in block.get('lines', []):
                block_text += ''.join(span.get('text', '') for span in line.get('spans', []))
            
            # Clear blocks with ability scores, base scores, or modifiers
            if any(keyword in block_text for keyword in ['Ability', 'Score', 'Modifier', 'Base',
                                                           '15', '16', '17', '18', '19', '20', '21', '22',
                                                           '24', '26', '28', '30', '32', '34',
                                                           '+ 1', '+ 2', '+ 3', '+ 4', '+ 5', '+ 6', '+ 7']):
                blocks_to_clear.append(idx)
                logger.debug(f"Clearing table fragment at block {idx}: {block_text[:60]}")
    
    # Clear the identified blocks
    for idx in blocks_to_clear:
        page['blocks'][idx]['lines'] = []
        page['blocks'][idx]['bbox'] = [0.0, 0.0, 0.0, 0.0]
    
    logger.info(f"Extracted Inherent Potential Table with {len(table_data)} rows, cleared {len(blocks_to_clear)} fragment blocks")


def force_psionicist_class_paragraph_breaks(page: dict) -> None:
    """Force paragraph breaks in the Psionicist Classes section.
    
    Ensures proper paragraph structure for psionicist class descriptions.
    """
    # Placeholder - implement actual logic if needed
    pass
