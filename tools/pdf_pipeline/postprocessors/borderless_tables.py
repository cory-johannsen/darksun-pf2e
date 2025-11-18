"""Post-processor for detecting and reconstructing borderless tables.

This module detects tables that don't have visible borders by analyzing
the alignment and spacing patterns of text blocks.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from ..models import Table, TableRow, TableCell
from ..utils.parallel import run_process_pool, should_parallelize, get_max_workers

logger = logging.getLogger(__name__)


def _detect_borderless_tables_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker function to detect borderless tables in a section file.
    
    Args:
        task: Dict with section_file path and config parameters
        
    Returns:
        Dict with items, warnings, errors, tables_detected, and modified flag
    """
    section_file = Path(task["section_file"])
    min_columns = task.get("min_columns", 3)
    min_rows = task.get("min_rows", 2)
    y_tolerance = task.get("y_tolerance", 5.0)
    
    warnings = []
    errors = []
    tables_detected = 0
    modified = False
    
    try:
        with open(section_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        # Helper functions from BorderlessTableDetector
        def get_block_text(block: Dict) -> str:
            lines = block.get('lines', [])
            text_parts = []
            for line in lines:
                for span in line.get('spans', []):
                    text_parts.append(span.get('text', ''))
            return ' '.join(text_parts).strip()
        
        def is_tabular_text(text: str) -> bool:
            if len(text) <= 20:
                return True
            if re.search(r'\d', text):
                return True
            if re.search(r'\d+/\d+|\d+d\d+', text):
                return True
            if len(text.split()) <= 3:
                return True
            return False
        
        def group_blocks_into_rows(blocks: List[Dict], y_tol: float) -> List[List[Dict]]:
            if not blocks:
                return []
            sorted_blocks = sorted(blocks, key=lambda b: b['bbox'][1])
            rows = []
            current_row = [sorted_blocks[0]]
            current_y = sorted_blocks[0]['bbox'][1]
            for block in sorted_blocks[1:]:
                block_y = block['bbox'][1]
                if abs(block_y - current_y) <= y_tol:
                    current_row.append(block)
                else:
                    current_row.sort(key=lambda b: b['bbox'][0])
                    rows.append(current_row)
                    current_row = [block]
                    current_y = block_y
            if current_row:
                current_row.sort(key=lambda b: b['bbox'][0])
                rows.append(current_row)
            return rows
        
        def looks_like_table(rows: List[List[Dict]], min_cols: int) -> bool:
            if len(rows) < 2:
                return False
            block_counts = [len(row) for row in rows[:min(5, len(rows))]]
            avg_blocks = sum(block_counts) / len(block_counts)
            similar_count = sum(1 for count in block_counts if abs(count - avg_blocks) <= 2)
            if similar_count < len(block_counts) * 0.7:
                return False
            tabular_patterns = 0
            total_blocks = 0
            for row in rows[:min(5, len(rows))]:
                for block in row:
                    text = get_block_text(block)
                    total_blocks += 1
                    if is_tabular_text(text):
                        tabular_patterns += 1
            return tabular_patterns >= total_blocks * 0.3
        
        # Process each page
        for page in section_data.get('pages', []):
            blocks = page.get('blocks', [])
            text_blocks = [b for b in blocks if b.get('type') == 'text' and b.get('lines')]
            
            if len(text_blocks) < min_columns * min_rows:
                continue
            
            rows = group_blocks_into_rows(text_blocks, y_tolerance)
            
            # Detect tables (simplified version)
            i = 0
            while i < len(rows):
                if len(rows[i]) >= min_columns and looks_like_table(rows[i:i+min_rows], min_columns):
                    # Found a potential table
                    table_rows = rows[i:i+min_rows]
                    
                    # Build minimal table structure
                    all_blocks = [block for row in table_rows for block in row]
                    min_x = min(b['bbox'][0] for b in all_blocks)
                    min_y = min(b['bbox'][1] for b in all_blocks)
                    max_x = max(b['bbox'][2] for b in all_blocks)
                    max_y = max(b['bbox'][3] for b in all_blocks)
                    
                    table = {
                        'bbox': [min_x, min_y, max_x, max_y],
                        'rows': [{'cells': [{'text': get_block_text(b), 'bbox': b['bbox']} for b in row]} for row in table_rows]
                    }
                    
                    if 'tables' not in page:
                        page['tables'] = []
                    page['tables'].append(table)
                    tables_detected += 1
                    modified = True
                    i += min_rows
                else:
                    i += 1
        
        # Save if modified
        if modified:
            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, ensure_ascii=False, indent=2)
        
        return {
            "items": 1 if modified else 0,
            "warnings": warnings,
            "errors": errors,
            "tables_detected": tables_detected,
            "modified": modified,
        }
    
    except Exception as e:
        error_msg = f"Failed to process {section_file.name}: {e}"
        errors.append(error_msg)
        return {
            "items": 0,
            "warnings": warnings,
            "errors": errors,
            "tables_detected": 0,
            "modified": False,
        }



class BorderlessTableDetector(BaseProcessor):
    """Detects and reconstructs borderless tables from aligned text blocks.
    
    Borderless tables are detected by:
    1. Finding groups of text blocks with similar Y-coordinates (rows)
    2. Detecting columns by consistent X-positions across rows
    3. Reconstructing table structure from the aligned blocks
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Detect borderless tables in extracted sections.
        
        Args:
            input_data: Input from previous stage
            context: Execution context
            
        Returns:
            ProcessorOutput with enhanced table detection
        """
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        min_columns = self.config.get("min_columns", 3)
        min_rows = self.config.get("min_rows", 2)
        y_tolerance = self.config.get("y_tolerance", 5.0)
        
        # Parallel config
        global_parallel = context.metadata.get("parallel", False)
        use_parallel = should_parallelize(self.config, global_parallel)
        
        # Build task list
        tasks = []
        for section_file in sorted(sections_dir.glob("*.json")):
            task = {
                "section_file": str(section_file),
                "min_columns": min_columns,
                "min_rows": min_rows,
                "y_tolerance": y_tolerance,
            }
            tasks.append(task)
        
        # Process (parallel or sequential)
        tables_detected = 0
        if use_parallel and len(tasks) > 1:
            max_workers = get_max_workers(self.config, default=4)
            chunksize = int(self.config.get("chunksize", 1))
            
            logger.info(f"Detecting borderless tables in {len(tasks)} files in parallel with {max_workers} workers")
            result = run_process_pool(
                tasks,
                _detect_borderless_tables_task,
                max_workers=max_workers,
                chunksize=chunksize,
                desc="borderless table detection"
            )
            
            context.items_processed = result["items_processed"]
            context.warnings.extend(result["warnings"])
            context.errors.extend(result["errors"])
            tables_detected = sum(r.get("tables_detected", 0) for r in result["results"])
        
        else:
            # Sequential processing
            logger.info(f"Detecting borderless tables in {len(tasks)} files sequentially")
            for task in tasks:
                result = _detect_borderless_tables_task(task)
                context.items_processed += result["items"]
                context.warnings.extend(result["warnings"])
                context.errors.extend(result["errors"])
                tables_detected += result.get("tables_detected", 0)
        
        return ProcessorOutput(
            data={
                "sections_processed": context.items_processed,
                "tables_detected": tables_detected,
            },
            metadata={
                "borderless_tables_detected": tables_detected,
                "parallel": use_parallel,
            }
        )
    
    def _detect_borderless_tables(
        self, 
        page: Dict, 
        min_columns: int = 3,
        min_rows: int = 2,
        y_tolerance: float = 5.0
    ) -> List[Dict]:
        """Detect borderless tables from text blocks on a page.
        
        Args:
            page: Page data containing blocks
            min_columns: Minimum number of columns to consider as table
            min_rows: Minimum number of rows to consider as table
            y_tolerance: Y-coordinate tolerance for row detection
            
        Returns:
            List of detected table dictionaries
        """
        blocks = page.get('blocks', [])
        text_blocks = [b for b in blocks if b.get('type') == 'text' and b.get('lines')]
        
        if len(text_blocks) < min_columns * min_rows:
            return []
        
        # Group blocks into potential rows by Y-coordinate
        rows = self._group_blocks_into_rows(text_blocks, y_tolerance)
        
        # Find sequences of rows that form tables
        tables = []
        i = 0
        while i < len(rows):
            table_data = self._extract_table_from_rows(rows[i:], min_columns, min_rows)
            if table_data:
                tables.append(table_data)
                i += len(table_data['rows'])
            else:
                i += 1
        
        return tables
    
    def _group_blocks_into_rows(
        self, 
        blocks: List[Dict], 
        y_tolerance: float
    ) -> List[List[Dict]]:
        """Group text blocks into rows based on Y-coordinate alignment.
        
        Args:
            blocks: List of text blocks
            y_tolerance: Tolerance for Y-coordinate matching
            
        Returns:
            List of rows, where each row is a list of blocks
        """
        if not blocks:
            return []
        
        # Sort blocks by Y-coordinate
        sorted_blocks = sorted(blocks, key=lambda b: b['bbox'][1])
        
        rows = []
        current_row = [sorted_blocks[0]]
        current_y = sorted_blocks[0]['bbox'][1]
        
        for block in sorted_blocks[1:]:
            block_y = block['bbox'][1]
            
            # If block is on roughly the same Y-coordinate, add to current row
            if abs(block_y - current_y) <= y_tolerance:
                current_row.append(block)
            else:
                # Sort current row by X-coordinate
                current_row.sort(key=lambda b: b['bbox'][0])
                rows.append(current_row)
                
                # Start new row
                current_row = [block]
                current_y = block_y
        
        # Add last row
        if current_row:
            current_row.sort(key=lambda b: b['bbox'][0])
            rows.append(current_row)
        
        return rows
    
    def _extract_table_from_rows(
        self, 
        rows: List[List[Dict]], 
        min_columns: int,
        min_rows: int
    ) -> Dict | None:
        """Extract a table from a sequence of rows.
        
        Args:
            rows: List of rows to analyze
            min_columns: Minimum columns required
            min_rows: Minimum rows required
            
        Returns:
            Table dictionary if detected, None otherwise
        """
        if len(rows) < min_rows:
            return None
        
        # Check if first row could be a header (has multiple cells)
        if len(rows[0]) < min_columns:
            return None
        
        # Check if this looks like tabular data
        if not self._looks_like_table(rows, min_columns):
            return None
        
        # Extract column positions from all rows
        column_positions = self._extract_column_positions(rows)
        
        if len(column_positions) < min_columns:
            return None
        
        # Build table structure
        table_rows = []
        rows_used = 0
        
        for row_blocks in rows:
            # Assign blocks to columns
            row_cells = self._assign_blocks_to_columns(row_blocks, column_positions)
            
            if not row_cells or len(row_cells) < min_columns:
                # Stop if row doesn't match table structure
                if rows_used >= min_rows:
                    break
                else:
                    return None
            
            table_rows.append({
                'cells': row_cells
            })
            rows_used += 1
        
        if rows_used < min_rows:
            return None
        
        # Calculate table bounding box
        all_blocks = [block for row in rows[:rows_used] for block in row]
        min_x = min(b['bbox'][0] for b in all_blocks)
        min_y = min(b['bbox'][1] for b in all_blocks)
        max_x = max(b['bbox'][2] for b in all_blocks)
        max_y = max(b['bbox'][3] for b in all_blocks)
        
        # Check if first row should be a header
        # A row is likely a header if cells contain single words or short phrases
        # and are different from typical data rows
        header_rows = 0
        if table_rows:
            first_row_texts = [cell.get('text', '').strip() for cell in table_rows[0].get('cells', [])]
            # Heuristic: if first row has mostly short text (likely column names), mark as header
            if all(len(text) < 30 and not any(char in text for char in ['/', '+', '-']) for text in first_row_texts if text):
                header_rows = 1
        
        table_dict = {
            'bbox': [min_x, min_y, max_x, max_y],
            'rows': table_rows
        }
        
        # Only set header_rows if detected
        if header_rows > 0:
            table_dict['header_rows'] = header_rows
        
        return table_dict
    
    def _looks_like_table(self, rows: List[List[Dict]], min_columns: int) -> bool:
        """Check if rows look like they form a table.
        
        Args:
            rows: List of rows to check
            min_columns: Minimum columns expected
            
        Returns:
            True if rows appear to be a table
        """
        if len(rows) < 2:
            return False
        
        # Check if rows have similar number of blocks (columns)
        block_counts = [len(row) for row in rows[:min(5, len(rows))]]
        avg_blocks = sum(block_counts) / len(block_counts)
        
        # Most rows should have similar number of blocks
        similar_count = sum(1 for count in block_counts if abs(count - avg_blocks) <= 2)
        
        if similar_count < len(block_counts) * 0.7:
            return False
        
        # Check if blocks contain tabular data patterns
        # (short text, numbers, ratios, etc.)
        tabular_patterns = 0
        total_blocks = 0
        
        for row in rows[:min(5, len(rows))]:
            for block in row:
                text = self._get_block_text(block)
                total_blocks += 1
                
                # Check for tabular patterns
                if self._is_tabular_text(text):
                    tabular_patterns += 1
        
        # At least 30% of blocks should have tabular patterns
        return tabular_patterns >= total_blocks * 0.3
    
    def _is_tabular_text(self, text: str) -> bool:
        """Check if text looks like tabular data.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be tabular data
        """
        # Short text (common in tables)
        if len(text) <= 20:
            return True
        
        # Contains numbers
        if re.search(r'\d', text):
            return True
        
        # Contains ratio patterns (e.g., "10/20", "3d6")
        if re.search(r'\d+/\d+|\d+d\d+', text):
            return True
        
        # Single words or short phrases
        if len(text.split()) <= 3:
            return True
        
        return False
    
    def _get_block_text(self, block: Dict) -> str:
        """Extract text from a block.
        
        Args:
            block: Block dictionary
            
        Returns:
            Extracted text
        """
        lines = block.get('lines', [])
        text_parts = []
        
        for line in lines:
            for span in line.get('spans', []):
                text_parts.append(span.get('text', ''))
        
        return ' '.join(text_parts).strip()
    
    def _split_block_into_cells(self, block: Dict) -> List[str]:
        """Split a text block into individual cell values.
        
        For blocks containing multiple column values (e.g., "10/20 5/20 8/20"),
        split them into separate values.
        
        Args:
            block: Block dictionary
            
        Returns:
            List of cell text values
        """
        text = self._get_block_text(block)
        
        # Check if text contains ratio patterns that indicate multiple columns
        # Pattern: numbers/numbers separated by spaces
        if re.search(r'\d+/\d+(\s+\d+/\d+)+', text):
            # Split by whitespace to separate ratio values
            values = re.findall(r'\d+/\d+', text)
            return values
        
        # Check if text contains multiple short words (potential column headers)
        words = text.split()
        if len(words) > 1 and all(len(w) <= 15 for w in words):
            return words
        
        # Single value
        return [text] if text else []
    
    def _extract_column_positions(self, rows: List[List[Dict]]) -> List[float]:
        """Extract column X-positions from rows.
        
        For borderless tables, we determine the number of columns by counting
        the maximum number of cell values across all rows after splitting blocks.
        
        Args:
            rows: List of rows
            
        Returns:
            List of column X-positions (dummy values for column count)
        """
        # Find the maximum number of cells in any row
        max_cells = 0
        
        for row in rows:
            total_cells = 0
            for block in row:
                cell_values = self._split_block_into_cells(block)
                total_cells += len(cell_values)
            max_cells = max(max_cells, total_cells)
        
        # Return dummy column positions (just the count)
        # The actual positions don't matter since we're splitting based on content
        return [float(i) for i in range(max_cells)]
    
    def _assign_blocks_to_columns(
        self, 
        blocks: List[Dict], 
        column_positions: List[float]
    ) -> List[Dict]:
        """Assign blocks to table columns.
        
        Handles blocks that contain multiple cell values by splitting them.
        
        Args:
            blocks: Row blocks to assign
            column_positions: List of column X-positions
            
        Returns:
            List of cell dictionaries
        """
        all_cell_values = []
        
        # Collect all cell values from all blocks, maintaining left-to-right order
        for block in blocks:
            cell_values = self._split_block_into_cells(block)
            for value in cell_values:
                all_cell_values.append({
                    'text': value,
                    'bbox': block['bbox'],
                    'rowspan': 1,
                    'colspan': 1
                })
        
        # If we have the right number of cells, use them directly
        if len(all_cell_values) == len(column_positions):
            return all_cell_values
        
        # If we have fewer cells than columns, pad with empty cells
        while len(all_cell_values) < len(column_positions):
            all_cell_values.append({
                'text': '',
                'bbox': [0, 0, 0, 0],
                'rowspan': 1,
                'colspan': 1
            })
        
        # If we have more cells than columns, take first n cells
        if len(all_cell_values) > len(column_positions):
            return all_cell_values[:len(column_positions)]
        
        return all_cell_values

