"""Table extraction for Chapter 10 (Treasure)."""

import logging
from typing import List, Optional
from .common import clean_whitespace, normalize_plain_text

logger = logging.getLogger(__name__)


def extract_lair_treasures_table(section_data: dict) -> None:
    """Extract and format the Lair Treasures table.
    
    The table has:
    - 7 columns: [Treasure Type, Bits, Ceramic, Silver, Gold, Gems, Magical Item]
    - 10 rows (A through J for treasure types)
    - Each cell (except Treasure Type) contains 1-2 lines:
      - Line 1: value (e.g., "200-2,000", "-", "Any 2", etc.)
      - Line 2 (optional): percentage (e.g., "30%")
    """
    logger.info("Extracting Lair Treasures table")
    
    # Find the page with "Lair Treasures" header
    target_page_idx = None
    lair_treasures_block_idx = None
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            if "Lair Treasures" == text.strip():
                target_page_idx = page_idx
                lair_treasures_block_idx = block_idx
                logger.info(f"Found 'Lair Treasures' header at page {page_idx}, block {block_idx}")
                break
        if target_page_idx is not None:
            break
    
    if target_page_idx is None:
        logger.warning("Could not find 'Lair Treasures' header")
        return
    
    # Mark "Lair Treasures" as H2
    page = section_data["pages"][target_page_idx]
    blocks = page["blocks"]
    lair_block = blocks[lair_treasures_block_idx]
    
    # Change the header to H2
    for line in lair_block.get("lines", []):
        for span in line.get("spans", []):
            if "Lair Treasures" in span.get("text", ""):
                # Mark as H2 by setting size larger than normal text
                span["size"] = 12.0  # H2 size
                logger.info("Marked 'Lair Treasures' as H2 header")
    
    # Now extract the table data from the blocks following the header
    # The table is complex and spans multiple pages
    # Extract cells from blocks based on spatial position
    
    # Define column headers
    column_headers = ["Treasure Type", "Bits", "Ceramic", "Silver", "Gold", "Gems", "Magical Item"]
    
    # Define treasure type rows (A through J)
    treasure_types = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    
    # Find the end of the table (for marking blocks)
    end_y = None
    for idx in range(lair_treasures_block_idx + 1, len(blocks)):
        text = normalize_plain_text(blocks[idx])
        if "Individual and Small Lair Treasures" in text:
            end_y = blocks[idx].get("bbox", [0, 0, 0, 0])[1]
            logger.info(f"Found table end at Y={end_y:.1f}")
            break
    
    if end_y is None:
        end_y = 999999
    
    # Also mark any tables in page.tables that fall in the Y-range for removal
    # IMPORTANT: Do this BEFORE extracting table data, so we can use end_y
    lair_bbox = lair_block.get("bbox", [60.0, 220.0, 556.0, 450.0])
    table_y_start = lair_bbox[3]  # Just after the "Lair Treasures" header
    table_y_end = end_y if end_y else 999999
    
    page_tables = page.get("tables", [])
    if page_tables:
        logger.info(f"Checking {len(page_tables)} page-level tables for removal")
        tables_marked = 0
        for table_idx, table in enumerate(page_tables):
            table_bbox = table.get("bbox", [0, 0, 0, 0])
            table_y = table_bbox[1]
            
            # Mark tables in the Lair Treasures Y-range
            if table_y_start < table_y < table_y_end:
                table["__skip_render"] = True
                tables_marked += 1
                logger.info(f"Marked page table {table_idx} (Y={table_y:.1f}) for removal")
        
        if tables_marked > 0:
            logger.info(f"Marked {tables_marked} page-level tables for removal")
    
    # Extract table data from PDF blocks
    table_data = _extract_table_cells_from_blocks(
        section_data, target_page_idx, lair_treasures_block_idx
    )
    
    # Create table structure
    header_row = {"cells": [{"text": col} for col in column_headers]}
    data_rows = []
    
    for treasure_type in treasure_types:
        if treasure_type in table_data:
            row_data = table_data[treasure_type]
            cells = [{"text": treasure_type}]  # First column is treasure type
            
            for col_name in column_headers[1:]:  # Skip "Treasure Type"
                cell_text = row_data.get(col_name, "-")
                # Clean whitespace in the cell text
                cell_text = clean_whitespace(cell_text)
                cells.append({"text": cell_text})
            
            data_rows.append({"cells": cells})
    
    all_rows = [header_row] + data_rows
    
    # Get the bbox from the Lair Treasures header
    lair_bbox = lair_block.get("bbox", [60.0, 220.0, 556.0, 450.0])
    table_bbox = [
        lair_bbox[0],  # Same left x
        lair_bbox[3] + 5.0,  # Start just below header
        lair_bbox[2],  # Same right x (full width)
        lair_bbox[3] + 100.0  # Extend downward
    ]
    
    table = {
        "rows": all_rows,
        "header_rows": 1,
        "bbox": table_bbox
    }
    
    # Attach the table to the Lair Treasures header block
    lair_block["__lair_treasures_table"] = table
    logger.info(f"Attached Lair Treasures table with {len(data_rows)} data rows")
    
    # Mark all blocks that contain table data for removal
    # This includes blocks in the Y-range of the table (from header Y to end Y)
    # regardless of their index position (left column blocks and right column blocks)
    table_y_start = lair_bbox[3]  # Just after the "Lair Treasures" header
    table_y_end = end_y if end_y else 999999
    
    logger.info(f"Marking blocks in Y-range {table_y_start:.1f} - {table_y_end:.1f} for removal")
    
    marked_count = 0
    for idx in range(lair_treasures_block_idx + 1, len(blocks)):
        block = blocks[idx]
        if block.get("type") != "text":
            continue
        
        # Check if this block is in the table Y-range
        block_bbox = block.get("bbox", [0, 0, 0, 0])
        block_y = block_bbox[1]
        
        # Skip if this is the end marker itself
        if "Individual and Small Lair Treasures" in normalize_plain_text(block):
            continue
        
        # Mark blocks that are in the table Y-range
        if table_y_start < block_y < table_y_end:
            block["__skip_render"] = True
            marked_count += 1
            logger.debug(f"Marked block {idx} (Y={block_y:.1f}) for removal")
    
    logger.info(f"Marked {marked_count} blocks for removal")
    
    # Also mark any tables in page.tables that fall in the Y-range for removal
    # These are auto-extracted tables that duplicate our custom table
    page_tables = page.get("tables", [])
    if page_tables:
        logger.info(f"Checking {len(page_tables)} page-level tables for removal")
        tables_marked = 0
        for table_idx, table in enumerate(page_tables):
            table_bbox = table.get("bbox", [0, 0, 0, 0])
            table_y = table_bbox[1]
            
            # Mark tables in the Lair Treasures Y-range
            if table_y_start < table_y < table_y_end:
                table["__skip_render"] = True
                tables_marked += 1
                logger.info(f"Marked page table {table_idx} (Y={table_y:.1f}) for removal")
        
        if tables_marked > 0:
            logger.info(f"Marked {tables_marked} page-level tables for removal")


def _extract_table_cells_from_blocks(
    section_data: dict, start_page_idx: int, start_block_idx: int
) -> dict:
    """Extract table cells from blocks following the Lair Treasures header.
    
    The Lair Treasures table spans the FULL page width with 7 columns:
    [Treasure Type, Bits, Ceramic, Silver, Gold, Gems, Magical Item]
    
    The table is stored in column-major format, where each column (including
    its header and all values) is in a separate block. The table spans from
    X=60 to X=556 across the full page width.
    
    Args:
        section_data: The section data dictionary
        start_page_idx: The page index where "Lair Treasures" header was found
        start_block_idx: The block index of the "Lair Treasures" header
    
    Returns:
        A dictionary mapping treasure type (A-J) to column values
    """
    pages = section_data.get("pages", [])
    page = pages[start_page_idx]
    blocks = page.get("blocks", [])
    
    # Find the end of the table by looking for "Individual and Small Lair Treasures"
    end_block_idx = None
    end_y = None
    for idx in range(start_block_idx + 1, len(blocks)):
        text = normalize_plain_text(blocks[idx])
        if "Individual and Small Lair Treasures" in text:
            end_block_idx = idx
            end_y = blocks[idx].get("bbox", [0, 0, 0, 0])[1]
            logger.info(f"Found table end at block {idx}, Y={end_y:.1f}")
            break
    
    if end_block_idx is None:
        end_block_idx = len(blocks)
        end_y = 999999
    
    # Collect all cells from blocks in the table region
    # Important: Blocks are NOT sorted by Y-coordinate!
    # The right column blocks may come after the end marker block in the list,
    # but their Y-coordinates are before the end marker's Y-coordinate.
    # So we need to check ALL blocks and filter by Y-coordinate.
    cells = []
    for idx, block in enumerate(blocks):
        if idx <= start_block_idx:  # Skip blocks before the table
            continue
        if block.get("type") != "text":
            continue
        
        # Extract all text spans from this block with their positions
        for line in block.get("lines", []):
            bbox = line.get("bbox", [0, 0, 0, 0])
            # Only include cells in the table Y range (after header, before end)
            if 238 < bbox[1] < end_y:
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        cell = {
                            "text": text,
                            "x": bbox[0],
                            "y": bbox[1],
                            "block": idx,
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                        }
                        cells.append(cell)
    
    logger.info(f"Collected {len(cells)} potential table cells")
    
    # Now organize cells into the table structure
    table_data = _organize_cells_into_table(cells)
    
    return table_data


def _organize_cells_into_table(cells: List[dict]) -> dict:
    """Organize collected cells into table structure.
    
    The table is organized in COLUMN-MAJOR format in the PDF. Each column
    (including its header and all values) is stored vertically in a separate block.
    We need to:
    1. Extract each column's data separately
    2. Match rows by Y-coordinate using treasure type letters as anchors
    
    Column X-coordinate ranges (based on analysis):
    - Type: X=67-86
    - Bits: X=108-161  
    - Ceramic: X=189-242
    - Silver: X=268-312
    - Gold: X=343-388
    - Gems: X=420-470
    - Magical Item: X=481-556
    
    Args:
        cells: List of cell dictionaries with text and position
    
    Returns:
        Dictionary mapping treasure type (A-J) to column values
    """
    # Filter out column headers (they appear at Y~238-240)
    header_cells = [c for c in cells if 238 < c["y"] < 242]
    data_cells = [c for c in cells if c["y"] >= 242]
    
    logger.debug(f"Found {len(header_cells)} header cells, {len(data_cells)} data cells")
    
    # Identify treasure type cells (single letters A-J) to get row Y-coordinates
    treasure_type_cells = []
    for cell in data_cells:
        text = cell["text"].strip()
        if len(text) == 1 and text in "ABCDEFGHIJ":
            treasure_type_cells.append(cell)
    
    # Sort by Y-coordinate to get rows in order
    treasure_type_cells.sort(key=lambda c: c["y"])
    
    logger.info(f"Found {len(treasure_type_cells)} treasure type markers")
    for tt in treasure_type_cells:
        logger.debug(f"  {tt['text']} at Y={tt['y']:.1f}")
    
    # Define column X-coordinate ranges
    column_ranges = {
        "Bits": (108, 170),
        "Ceramic": (180, 250),
        "Silver": (260, 330),
        "Gold": (340, 410),
        "Gems": (415, 480),
        "Magical Item": (480, 600),
    }
    
    # Extract each column's data
    columns_data = {}
    for col_name, (x_min, x_max) in column_ranges.items():
        # Get all cells in this column
        col_cells = [c for c in data_cells if x_min <= c["x"] < x_max]
        # Skip header cells
        col_cells = [c for c in col_cells if c["text"] not in ["Bits", "Ceramic", "Silver", "Gold", "Gems", "Magical", "Item"]]
        # Sort by Y
        col_cells.sort(key=lambda c: c["y"])
        columns_data[col_name] = col_cells
        logger.debug(f"Column '{col_name}': {len(col_cells)} cells")
    
    # Now match cells to rows using treasure type Y-coordinates
    table_data = {}
    
    for i, tt_cell in enumerate(treasure_type_cells):
        treasure_type = tt_cell["text"]
        row_y = tt_cell["y"]
        
        # Determine the Y-range for this row
        # Each row has 2 lines: value (at treasure type Y) and percentage (~12 units below)
        # Rows are ~23 units apart
        # So we want to capture from treasure type Y to about 18 units below it
        y_min = row_y - 2  # Small buffer before treasure type
        
        if i < len(treasure_type_cells) - 1:
            next_y = treasure_type_cells[i + 1]["y"]
            # Use a point that's 80% of the way to the next row
            # This ensures we capture the percentage line without overlapping
            y_max = row_y + (next_y - row_y) * 0.8
        else:
            y_max = row_y + 20  # Last row, use a fixed range
        
        logger.debug(f"Row '{treasure_type}': Y range {y_min:.1f} - {y_max:.1f}")
        
        row_data = {}
        for col_name, col_cells in columns_data.items():
            # Find cells in this row's Y-range
            row_cells = [c for c in col_cells if y_min <= c["y"] < y_max]
            if row_cells:
                # Combine multiple cells with newline
                cell_text = "\n".join(c["text"] for c in row_cells)
                # Clean whitespace (e.g., "3 0 %" -> "30%")
                cell_text = clean_whitespace(cell_text)
                row_data[col_name] = cell_text
                logger.debug(f"  {col_name}: '{cell_text}' (from {len(row_cells)} cells)")
            else:
                row_data[col_name] = "-"
        
        table_data[treasure_type] = row_data
    
    logger.info(f"Organized table data for {len(table_data)} treasure types")
    
    return table_data


def extract_individual_treasures_table(section_data: dict) -> None:
    """Extract and format the Individual and Small Lair Treasures table.
    
    The table has:
    - 7 columns: [Treasure Type, Bits, Ceramic, Silver, Gold, Gems, Magical Item]
    - 17 rows (J through Z for treasure types)
    - Each cell (except Treasure Type) contains 1-2 lines following formats:
      - "-"
      - "#-#"
      - "#-#\n#%"
      - "#-# potions"
      - "#-# scrolls"
      - "Any #\n#%"
      - "Any # potions\n#%"
      - "Any #+# potion\n#%"
      - "Any #+# scroll\n#%"
      - "Any # except weapons\n#%"
      - "Armor Weapon\n#%"
    """
    logger.info("Extracting Individual and Small Lair Treasures table")
    
    # Find the page with "Individual and Small Lair Treasures" header
    target_page_idx = None
    header_block_idx = None
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            if "Individual and Small Lair Treasures" == text.strip():
                target_page_idx = page_idx
                header_block_idx = block_idx
                logger.info(f"Found 'Individual and Small Lair Treasures' header at page {page_idx}, block {block_idx}")
                break
        if target_page_idx is not None:
            break
    
    if target_page_idx is None:
        logger.warning("Could not find 'Individual and Small Lair Treasures' header")
        return
    
    # Mark "Individual and Small Lair Treasures" as H2
    page = section_data["pages"][target_page_idx]
    blocks = page["blocks"]
    header_block = blocks[header_block_idx]
    
    # Change the header to H2
    for line in header_block.get("lines", []):
        for span in line.get("spans", []):
            if "Individual and Small Lair Treasures" in span.get("text", ""):
                # Mark as H2 by setting size larger than normal text
                span["size"] = 12.0  # H2 size
                logger.info("Marked 'Individual and Small Lair Treasures' as H2 header")
    
    # Define column headers (shared with Lair Treasures table)
    column_headers = ["Treasure Type", "Bits", "Ceramic", "Silver", "Gold", "Gems", "Magical Item"]
    
    # Define treasure type rows (J through Z)
    treasure_types = ["J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    
    # Find the end of the table (next header: "Coins")
    end_y = None
    for idx in range(header_block_idx + 1, len(blocks)):
        text = normalize_plain_text(blocks[idx])
        if "Coins" == text.strip():
            end_y = blocks[idx].get("bbox", [0, 0, 0, 0])[1]
            logger.info(f"Found table end (Coins header) at Y={end_y:.1f}")
            break
    
    if end_y is None:
        # If no "Coins" header found, check next page
        if target_page_idx + 1 < len(section_data.get("pages", [])):
            next_page = section_data["pages"][target_page_idx + 1]
            for block in next_page.get("blocks", []):
                text = normalize_plain_text(block)
                if "Coins" == text.strip():
                    # Use a large Y value to capture rest of current page
                    end_y = 999999
                    logger.info("Found Coins header on next page")
                    break
    
    if end_y is None:
        end_y = 999999
    
    # Extract table data from PDF blocks
    table_data = _extract_individual_table_cells_from_blocks(
        section_data, target_page_idx, header_block_idx, end_y
    )
    
    # Create table structure
    header_row = {"cells": [{"text": col} for col in column_headers]}
    data_rows = []
    
    for treasure_type in treasure_types:
        if treasure_type in table_data:
            row_data = table_data[treasure_type]
            cells = [{"text": treasure_type}]  # First column is treasure type
            
            for col_name in column_headers[1:]:  # Skip "Treasure Type"
                cell_text = row_data.get(col_name, "-")
                # Clean whitespace in the cell text
                cell_text = clean_whitespace(cell_text)
                cells.append({"text": cell_text})
            
            data_rows.append({"cells": cells})
    
    all_rows = [header_row] + data_rows
    
    # Get the bbox from the header
    header_bbox = header_block.get("bbox", [60.0, 464.0, 556.0, 475.0])
    table_bbox = [
        header_bbox[0],  # Same left x
        header_bbox[3] + 5.0,  # Start just below header
        header_bbox[2],  # Same right x (full width)
        header_bbox[3] + 100.0  # Extend downward
    ]
    
    table = {
        "rows": all_rows,
        "header_rows": 1,
        "bbox": table_bbox
    }
    
    # Attach the table to the header block
    header_block["__individual_treasures_table"] = table
    logger.info(f"Attached Individual and Small Lair Treasures table with {len(data_rows)} data rows")
    
    # Mark all blocks that contain table data for removal
    table_y_start = header_bbox[3]  # Just after the header
    table_y_end = end_y if end_y else 999999
    
    logger.info(f"Marking blocks in Y-range {table_y_start:.1f} - {table_y_end:.1f} for removal")
    
    marked_count = 0
    for idx in range(header_block_idx + 1, len(blocks)):
        block = blocks[idx]
        if block.get("type") != "text":
            continue
        
        # Check if this block is in the table Y-range
        block_bbox = block.get("bbox", [0, 0, 0, 0])
        block_y = block_bbox[1]
        
        # Skip if this is the end marker itself
        if "Coins" == normalize_plain_text(block).strip():
            continue
        
        # Mark blocks that are in the table Y-range
        if table_y_start < block_y < table_y_end:
            block["__skip_render"] = True
            marked_count += 1
            logger.debug(f"Marked block {idx} (Y={block_y:.1f}) for removal")
    
    logger.info(f"Marked {marked_count} blocks for removal")
    
    # Also mark any tables in page.tables that fall in the Y-range for removal
    page_tables = page.get("tables", [])
    if page_tables:
        logger.info(f"Checking {len(page_tables)} page-level tables for removal")
        tables_marked = 0
        for table_idx, table in enumerate(page_tables):
            table_bbox = table.get("bbox", [0, 0, 0, 0])
            table_y = table_bbox[1]
            
            # Mark tables in the Individual Treasures Y-range
            if table_y_start < table_y < table_y_end:
                table["__skip_render"] = True
                tables_marked += 1
                logger.info(f"Marked page table {table_idx} (Y={table_y:.1f}) for removal")
        
        if tables_marked > 0:
            logger.info(f"Marked {tables_marked} page-level tables for removal")


def _extract_individual_table_cells_from_blocks(
    section_data: dict, start_page_idx: int, start_block_idx: int, end_y: float
) -> dict:
    """Extract table cells from blocks following the Individual and Small Lair Treasures header.
    
    The Individual and Small Lair Treasures table spans the FULL page width with 7 columns:
    [Treasure Type, Bits, Ceramic, Silver, Gold, Gems, Magical Item]
    
    Like the Lair Treasures table, this is stored in column-major format.
    
    Args:
        section_data: The section data dictionary
        start_page_idx: The page index where header was found
        start_block_idx: The block index of the header
        end_y: The Y-coordinate where the table ends
    
    Returns:
        A dictionary mapping treasure type (J-Z) to column values
    """
    pages = section_data.get("pages", [])
    page = pages[start_page_idx]
    blocks = page.get("blocks", [])
    
    # Collect all cells from blocks in the table region
    # The header is at Y~464, and table starts at Y~484
    table_y_start = 475.0  # Just after header
    
    cells = []
    for idx, block in enumerate(blocks):
        if idx <= start_block_idx:  # Skip blocks before the table
            continue
        if block.get("type") != "text":
            continue
        
        # Extract all text spans from this block with their positions
        for line in block.get("lines", []):
            bbox = line.get("bbox", [0, 0, 0, 0])
            # Only include cells in the table Y range (after header, before end)
            if table_y_start < bbox[1] < end_y:
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if text:
                        cell = {
                            "text": text,
                            "x": bbox[0],
                            "y": bbox[1],
                            "block": idx,
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                        }
                        cells.append(cell)
    
    logger.info(f"Collected {len(cells)} potential table cells")
    
    # Now organize cells into the table structure
    table_data = _organize_individual_cells_into_table(cells)
    
    return table_data


def _organize_individual_cells_into_table(cells: List[dict]) -> dict:
    """Organize collected cells into Individual and Small Lair Treasures table structure.
    
    The table is organized in COLUMN-MAJOR format in the PDF. Each column
    (including its header and all values) is stored vertically in a separate block.
    
    Treasure types J-Z are arranged as single letters that anchor each row.
    
    Column X-coordinate ranges (similar to Lair Treasures table):
    - Type: X=67-86
    - Bits: X=108-170  
    - Ceramic: X=180-250
    - Silver: X=260-330
    - Gold: X=340-410
    - Gems: X=415-480
    - Magical Item: X=480-600
    
    Args:
        cells: List of cell dictionaries with text and position
    
    Returns:
        Dictionary mapping treasure type (J-Z) to column values
    """
    # Identify treasure type cells (single letters J-Z) to get row Y-coordinates
    treasure_type_cells = []
    for cell in cells:
        text = cell["text"].strip()
        if len(text) == 1 and text in "JKLMNOPQRSTUVWXYZ":
            treasure_type_cells.append(cell)
    
    # Sort by Y-coordinate to get rows in order
    treasure_type_cells.sort(key=lambda c: c["y"])
    
    logger.info(f"Found {len(treasure_type_cells)} treasure type markers")
    for tt in treasure_type_cells:
        logger.debug(f"  {tt['text']} at Y={tt['y']:.1f}")
    
    # Define column X-coordinate ranges (same as Lair Treasures)
    column_ranges = {
        "Bits": (108, 170),
        "Ceramic": (180, 250),
        "Silver": (260, 330),
        "Gold": (340, 410),
        "Gems": (415, 480),
        "Magical Item": (480, 600),
    }
    
    # Extract each column's data
    columns_data = {}
    for col_name, (x_min, x_max) in column_ranges.items():
        # Get all cells in this column
        col_cells = [c for c in cells if x_min <= c["x"] < x_max]
        # Skip header cells and letter markers
        col_cells = [c for c in col_cells if c["text"] not in ["Bits", "Ceramic", "Silver", "Gold", "Gems", "Magical", "Item"] and len(c["text"]) > 1]
        # Sort by Y
        col_cells.sort(key=lambda c: c["y"])
        columns_data[col_name] = col_cells
        logger.debug(f"Column '{col_name}': {len(col_cells)} cells")
    
    # Now match cells to rows using treasure type Y-coordinates
    table_data = {}
    
    for i, tt_cell in enumerate(treasure_type_cells):
        treasure_type = tt_cell["text"]
        row_y = tt_cell["y"]
        
        # Determine the Y-range for this row
        # Each row can have 1-2 lines
        y_min = row_y - 2  # Small buffer before treasure type
        
        if i < len(treasure_type_cells) - 1:
            next_y = treasure_type_cells[i + 1]["y"]
            # Use a point that's 80% of the way to the next row
            y_max = row_y + (next_y - row_y) * 0.8
        else:
            y_max = row_y + 20  # Last row, use a fixed range
        
        logger.debug(f"Row '{treasure_type}': Y range {y_min:.1f} - {y_max:.1f}")
        
        row_data = {}
        for col_name, col_cells in columns_data.items():
            # Find cells in this row's Y-range
            row_cells = [c for c in col_cells if y_min <= c["y"] < y_max]
            if row_cells:
                # Combine multiple cells with newline
                cell_text = "\n".join(c["text"] for c in row_cells)
                # Clean whitespace (e.g., "3 0 %" -> "30%", "5 0 %" -> "50%")
                cell_text = clean_whitespace(cell_text)
                row_data[col_name] = cell_text
                logger.debug(f"  {col_name}: '{cell_text}' (from {len(row_cells)} cells)")
            else:
                row_data[col_name] = "-"
        
        table_data[treasure_type] = row_data
    
    logger.info(f"Organized table data for {len(table_data)} treasure types")
    
    return table_data


def extract_gem_table(section_data: dict) -> None:
    """Extract and format the Gem Table.
    
    The table has:
    - 3 columns: [D100 Roll, Base Value, Class]
    - 6 rows of data
    - D100 Roll format: "#-#" or "#" (e.g., "01-2", "26-50", "00")
    - Base Value format: "# cp" or "# sp" or "# gp" (e.g., "15 cp", "75 sp")
    - Class format: Gem class names (may contain hyphens, e.g., "semi-precious")
    
    Following the table is a paragraph beginning with "The gem variations".
    """
    logger.warning("=" * 80)
    logger.warning("EXTRACTING GEM TABLE")
    logger.warning("=" * 80)
    
    # Find the page with "Gem Table" header
    target_page_idx = None
    header_block_idx = None
    
    logger.warning(f"Section has {len(section_data.get('pages', []))} pages")
    
    for page_idx, page in enumerate(section_data.get("pages", [])):
        logger.warning(f"Checking page {page_idx} with {len(page.get('blocks', []))} blocks")
        for block_idx, block in enumerate(page.get("blocks", [])):
            if block.get("type") != "text":
                continue
            
            text = normalize_plain_text(block)
            logger.warning(f"  Block {block_idx}: '{text[:50]}'...")
            if "Gem Table" == text.strip():
                target_page_idx = page_idx
                header_block_idx = block_idx
                logger.warning(f"Found 'Gem Table' header at page {page_idx}, block {block_idx}")
                break
        if target_page_idx is not None:
            break
    
    if target_page_idx is None:
        logger.warning("Could not find 'Gem Table' header")
        return
    
    # Get the page and blocks
    page = section_data["pages"][target_page_idx]
    blocks = page["blocks"]
    header_block = blocks[header_block_idx]
    
    # The Gem Table data is in the very next block after the header
    # It contains all the table data in one large block with multiple lines
    # The table structure based on source PDF analysis:
    # - Headers at Y~492-515: "D 100", "Base", "Roil", "Value", "Cl ass"
    # - Row 1 at Y~519: "01-2", "15 cp", "Ornamental"
    # - Row 2 at Y~533: "26-50", "75 cp", "semi-precious"
    # - Row 3 at Y~546: "51-70", "15 sp", "Fancy"
    # - Row 4 at Y~559: "71-90", "75 sp", "Precious"
    # - Row 5 at Y~573: "91-99", "15 gp", "Gems"
    # - Row 6 at Y~586: "00", "75 gp", "Jewels"
    # - Paragraph at Y~599: "The gem variations..."
    
    # Define the table data (extracted from source PDF)
    gem_table_data = [
        ("01-2", "15 cp", "Ornamental"),
        ("26-50", "75 cp", "semi-precious"),
        ("51-70", "15 sp", "Fancy"),
        ("71-90", "75 sp", "Precious"),
        ("91-99", "15 gp", "Gems"),
        ("00", "75 gp", "Jewels"),
    ]
    
    # Build table structure
    column_headers = ["D100 Roll", "Base Value", "Class"]
    header_row = {"cells": [{"text": col} for col in column_headers]}
    
    data_rows = []
    for d100_roll, base_value, gem_class in gem_table_data:
        cells = [
            {"text": d100_roll},
            {"text": base_value},
            {"text": gem_class}
        ]
        data_rows.append({"cells": cells})
    
    all_rows = [header_row] + data_rows
    
    # Get the bbox from the header
    header_bbox = header_block.get("bbox", [295.0, 467.0, 372.0, 480.0])
    table_bbox = [
        header_bbox[0],  # Same left x
        header_bbox[3] + 5.0,  # Start just below header
        header_bbox[2] + 100.0,  # Extend to the right to accommodate table
        header_bbox[3] + 150.0  # Extend downward
    ]
    
    table = {
        "rows": all_rows,
        "header_rows": 1,
        "bbox": table_bbox
    }
    
    # Attach the table to the header block
    header_block["__gem_table"] = table
    logger.warning(f"✅ Attached Gem Table with {len(data_rows)} data rows to block at page {target_page_idx}, block {header_block_idx}")
    logger.warning(f"Header block now has keys: {list(header_block.keys())}")
    logger.warning(f"__gem_table value type: {type(header_block.get('__gem_table'))}")
    
    # Mark the block immediately after the header for removal
    # This block contains the fragmented table data
    # BUT it may also contain the "gem variations" paragraph at the end
    # We need to extract and preserve that paragraph
    if header_block_idx + 1 < len(blocks):
        table_data_block = blocks[header_block_idx + 1]
        if table_data_block.get("type") == "text":
            # Check if this block contains table data (D 100, Base, etc.)
            block_text = normalize_plain_text(table_data_block)
            logger.warning(f"Checking block {header_block_idx + 1} for table data: '{block_text[:100]}'")
            if "D 1 0 0" in block_text or "Base" in block_text or "Ornamental" in block_text:
                # This block contains table data - mark it for removal
                table_data_block["__skip_render"] = True
                logger.warning(f"✓ Marked table data block {header_block_idx + 1} for removal")
                
                # BUT check if it also contains the "gem variations" paragraph
                # If so, we need to extract and create a new block for it
                if "gem variations" in block_text.lower():
                    logger.warning(f"⚠️  Block {header_block_idx + 1} contains BOTH table data AND 'gem variations' paragraph!")
                    logger.warning(f"Need to extract and preserve the paragraph...")
                    
                    # Find the lines that contain "gem variations" and subsequent text
                    gem_var_lines = []
                    found_gem_var = False
                    for line in table_data_block.get("lines", []):
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        
                        if "gem variations" in line_text.lower():
                            found_gem_var = True
                        
                        if found_gem_var:
                            gem_var_lines.append(line)
                    
                    if gem_var_lines:
                        # Create a new block with just the paragraph
                        new_paragraph_block = {
                            "bbox": gem_var_lines[0].get("bbox", [0, 0, 0, 0]),
                            "type": "text",
                            "lines": gem_var_lines,
                            "image": None
                        }
                        
                        # Insert it after the table data block
                        blocks.insert(header_block_idx + 2, new_paragraph_block)
                        logger.warning(f"✅ Created new block {header_block_idx + 2} with 'gem variations' paragraph ({len(gem_var_lines)} lines)")
            else:
                logger.warning(f"✗ NOT marking block {header_block_idx + 1} (doesn't match table data pattern)")

    
    # Also mark any page-level tables in this region for removal
    page_tables = page.get("tables", [])
    if page_tables:
        logger.info(f"Checking {len(page_tables)} page-level tables for removal")
        table_y_start = header_bbox[3]
        table_y_end = header_bbox[3] + 150
        tables_marked = 0
        for table_idx, table in enumerate(page_tables):
            table_bbox = table.get("bbox", [0, 0, 0, 0])
            table_y = table_bbox[1]
            
            # Mark tables in the Gem Table Y-range
            if table_y_start < table_y < table_y_end:
                table["__skip_render"] = True
                tables_marked += 1
                logger.info(f"Marked page table {table_idx} (Y={table_y:.1f}) for removal")
        
        if tables_marked > 0:
            logger.info(f"Marked {tables_marked} page-level tables for removal")



