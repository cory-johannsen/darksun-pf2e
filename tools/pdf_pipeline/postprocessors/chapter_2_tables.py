"""Post-processor for Chapter 2 specific table fixes.

Handles special cases like the Racial Ability Requirements table that have
unusual structure not caught by general-purpose detectors.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..base import BaseProcessor, BasePostProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
import logging


class Chapter2TableFixer(BaseProcessor):
    """Fixes specific table issues in Chapter 2: Player Character Races.
    
    Handles:
    - Racial Ability Requirements table reconstruction
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Fix Chapter 2 tables.
        
        Args:
            input_data: Output from previous processor
            context: Execution context
            
        Returns:
            ProcessorOutput with fixed tables
        """
        logger = logging.getLogger(__name__)
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        
        # Find the Chapter 2 races section file
        chapter_2_file = None
        for file in sections_dir.glob("*chapter-two-player-character-races.json"):
            chapter_2_file = file
            break
        
        if not chapter_2_file or not chapter_2_file.exists():
            # Chapter 2 file not found, return unchanged
            return input_data
        
        # Load the section
        with open(chapter_2_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        modified = False
        
        # Process each page
        for page in section_data.get('pages', []):
            if page['page_number'] == 5:
                # Fix the Racial Ability Requirements table on page 5
                if self._fix_racial_ability_requirements_table(page):
                    modified = True
            elif page['page_number'] == 6:
                # Fix Table 3: Racial Class And Level Limits on page 6
                if self._fix_table_3_header_rows(page):
                    modified = True
            elif page['page_number'] == 7:
                # Ensure Other Languages table exists on page 7
                if self._ensure_other_languages_table(page):
                    modified = True
        
        # Save if modified
        if modified:
            logger.debug("Chapter 2 tables modified; saving %s", chapter_2_file)
            with open(chapter_2_file, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, ensure_ascii=False, indent=2)
            
            context.items_processed = 1
        
        return ProcessorOutput(
            data={"tables_fixed": 1 if modified else 0},
            metadata={"chapter_2_tables_fixed": modified}
        )
    
    def _fix_racial_ability_requirements_table(self, page: Dict) -> bool:
        """Fix the Racial Ability Requirements table structure.
        
        Args:
            page: Page data
            
        Returns:
            True if table was fixed
        """
        blocks = page.get('blocks', [])
        
        # Find the key blocks for this table and track indices to remove
        header_left = None  # "Ability Dwarf Elf"
        header_right = None  # "H-Elf H-giant Halfling Mul Thri-kreen"
        data_left = None  # First 3 columns of ratio data
        data_right = None  # Last 5 columns of ratio data
        row_labels = []  # Strength, Dexterity, etc.
        blocks_to_remove = []  # Indices of blocks that are part of the table
        
        for i, block in enumerate(blocks):
            if block.get('type') != 'text' or not block.get('lines'):
                continue
            
            text = self._get_block_text(block).strip()
            bbox = block['bbox']
            
            # Identify blocks and mark them for removal
            if text == "Ability Dwarf Elf":
                header_left = text
                blocks_to_remove.append(i)
            elif text == "H-Elf H-giant Halfling Mul Thri-kreen":
                header_right = text
                blocks_to_remove.append(i)
            elif text.startswith("10/20 5/20") and len(text) > 40:
                # This is the consolidated data for left columns
                data_left = text
                blocks_to_remove.append(i)
            elif text.startswith("5/20 17/20") and len(text) > 40:
                # This is the consolidated data for right columns
                data_right = text
                blocks_to_remove.append(i)
            elif text in ["Strength", "Wisdom", "Charisma"]:
                row_labels.append(text)
                blocks_to_remove.append(i)
            elif "Dexterity Constitution Intelligence" in text:
                # Split this into individual labels
                for label in ["Dexterity", "Constitution", "Intelligence"]:
                    row_labels.append(label)
                blocks_to_remove.append(i)
        
        # Check if we found all necessary components
        if not (header_left and header_right and data_left and data_right and len(row_labels) >= 6):
            return False
        
        # Reconstruct the table
        table = self._reconstruct_ability_requirements_table(
            header_left, header_right, data_left, data_right, row_labels
        )
        
        if table:
            # Remove the blocks that were part of the broken table
            # Remove in reverse order to maintain indices
            for idx in sorted(blocks_to_remove, reverse=True):
                page['blocks'].pop(idx)
            
            # Remove any existing detected tables that overlap with this one
            if 'tables' not in page:
                page['tables'] = []
            
            # Remove incorrectly detected versions of this table
            page['tables'] = [t for t in page['tables'] if t['bbox'][1] < 550 or t['bbox'][1] > 650]
            
            # Add the corrected table
            page['tables'].append(table)
            return True
        
        return False
    
    def _reconstruct_ability_requirements_table(
        self,
        header_left: str,
        header_right: str,
        data_left: str,
        data_right: str,
        row_labels: List[str]
    ) -> Dict | None:
        """Reconstruct the Racial Ability Requirements table.
        
        Args:
            header_left: Left column headers
            header_right: Right column headers
            data_left: Data for first 3 columns
            data_right: Data for last 5 columns
            row_labels: Row labels (ability names)
            
        Returns:
            Table dictionary
        """
        # Parse headers
        left_headers = header_left.split()  # ["Ability", "Dwarf", "Elf"]
        right_headers = header_right.split()  # ["H-Elf", "H-giant", "Halfling", "Mul", "Thri-kreen"]
        all_headers = left_headers + right_headers
        
        # Parse data values (ratio format: "10/20 5/20 ...")
        import re
        left_values = re.findall(r'\d+/\d+', data_left)
        right_values = re.findall(r'\d+/\d+', data_right)
        
        # The data should have 6 rows × number of numeric columns
        # Left has 2 numeric columns (Dwarf, Elf), Right has 5 numeric columns
        num_rows = 6
        left_cols = 2
        right_cols = 5
        
        # Build table rows
        rows = []
        
        # Header row
        header_cells = []
        for header in all_headers:
            header_cells.append({
                'text': header,
                'bbox': [0, 0, 0, 0],
                'rowspan': 1,
                'colspan': 1
            })
        rows.append({'cells': header_cells})
        
        # Data rows
        ability_names = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        
        for row_idx in range(num_rows):
            cells = []
            
            # First column: ability name
            cells.append({
                'text': ability_names[row_idx] if row_idx < len(ability_names) else '',
                'bbox': [0, 0, 0, 0],
                'rowspan': 1,
                'colspan': 1
            })
            
            # Left data columns (Dwarf, Elf)
            for col_idx in range(left_cols):
                data_idx = row_idx * left_cols + col_idx
                value = left_values[data_idx] if data_idx < len(left_values) else ''
                cells.append({
                    'text': value,
                    'bbox': [0, 0, 0, 0],
                    'rowspan': 1,
                    'colspan': 1
                })
            
            # Right data columns (H-Elf, H-giant, Halfling, Mul, Thri-kreen)
            for col_idx in range(right_cols):
                data_idx = row_idx * right_cols + col_idx
                value = right_values[data_idx] if data_idx < len(right_values) else ''
                cells.append({
                    'text': value,
                    'bbox': [0, 0, 0, 0],
                    'rowspan': 1,
                    'colspan': 1
                })
            
            rows.append({'cells': cells})
        
        # Create table structure
        # Position after "Racial Ability Requirements" header (Y=554) in left column
        # Y increases downward, so table should be at Y > 554 to appear below the header
        table = {
            'bbox': [40, 560, 290, 720],  # Left column, below the header
            'rows': rows
        }
        
        return table
    
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
    
    def _fix_table_3_header_rows(self, page: Dict) -> bool:
        """Remove malformed Table 3 created by borderless detector.
        
        The borderless table detector creates a malformed version of Table 3
        with incorrect structure (28+ cells in first row instead of 9 columns).
        We remove any detected tables on this page so that the chapter processing
        during transformation can create the correct version with proper header_rows.
        
        Args:
            page: Page data
            
        Returns:
            True if tables were removed
        """
        tables = page.get('tables', [])
        if not tables:
            return False
        
        # Remove all tables on page 6 (Table 3's page)
        # The correct table will be created by chapter_2_processing during transformation
        page['tables'] = []
        return True
    
    def _ensure_other_languages_table(self, page: Dict) -> bool:
        """Ensure the Other Languages table exists on page 7 without hardcoded values.
        
        The Other Languages section lists languages in a 2-column table format.
        We detect the section boundaries by finding the 'Other Languages' header
        and the next major header (typically 'Dwarves'), then collect narrow text
        blocks within that region to form a 2-column table.
        """
        logger = logging.getLogger(__name__)
        existing_tables = page.get('tables', [])
        if existing_tables:
            return False
        
        # Helper to normalize text
        def _norm(s: str) -> str:
            return " ".join(s.replace("\u00ad", " ").split()).strip().lower()
        
        # Find 'Other Languages' header block and the next header (e.g., 'Dwarves')
        y_min = None
        y_max = None
        next_header_y = None
        
        blocks = page.get('blocks', [])
        for block in blocks:
            if block.get('type') != 'text' or not block.get('lines'):
                continue
            text = self._get_block_text(block).strip()
            ntext = _norm(text)
            if "other languages" == ntext:
                y_min = float(block['bbox'][1]) + 2.0
                break
        
        if y_min is None:
            return False
        
        # Find the next colored header by looking for short bold-like headings or known next section
        candidates_y = []
        for block in blocks:
            if block.get('type') != 'text' or not block.get('lines'):
                continue
            text = self._get_block_text(block).strip()
            ntext = _norm(text)
            if ntext in {"dwarves"} or ntext.startswith("dwarves"):
                candidates_y.append(float(block['bbox'][1]))
        if candidates_y:
            next_header_y = min(candidates_y)
        
        y_max = next_header_y - 2.0 if next_header_y is not None else float(page.get("height", 0) or 0)
        
        # Collect narrow blocks between y_min and y_max as language entries
        items: List[tuple[int, str, List[float]]] = []
        for idx, block in enumerate(blocks):
            if block.get('type') != 'text' or not block.get('lines'):
                continue
            bbox = block.get('bbox', [0, 0, 0, 0])
            y0 = float(bbox[1])
            if y0 <= y_min or y0 >= y_max:
                continue
            width = float(bbox[2]) - float(bbox[0])
            if width > 160.0:
                continue
            text = self._get_block_text(block).strip()
            # Heuristic: skip empty or paragraph-like sentences
            if not text or len(text.split()) > 2:
                continue
            items.append((idx, text, bbox))
        
        if len(items) < 6:
            return False
        
        # Sort and form 2-column rows by reading order
        items.sort(key=lambda x: (x[2][1], x[2][0]))
        rows: List[Dict] = []
        for i in range(0, len(items), 2):
            left = items[i][1]
            right = items[i + 1][1] if i + 1 < len(items) else ""
            rows.append({"cells": [{"text": left}, {"text": right}]})
        
        # Compute bbox
        ys = [b[2] for b in items]
        min_x = min(b[0] for b in ys)
        min_y = min(b[1] for b in ys)
        max_x = max(b[2] for b in ys)
        max_y = max(b[3] for b in ys)
        
        table = {
            "bbox": [min_x, min_y, max_x, max_y],
            "rows": rows
        }
        
        page.setdefault("tables", []).append(table)
        # Clear lines from language blocks so they don't duplicate under the table
        for idx, _, _ in items:
            if 0 <= idx < len(page['blocks']):
                page['blocks'][idx]['lines'] = []
        logger.debug("Constructed Other Languages table with %d rows", len(rows))
        return True

