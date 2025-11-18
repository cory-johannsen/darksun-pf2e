"""Table header metadata validator."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class TableHeaderValidator:
    """Validates table header metadata in structured JSON files."""
    
    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.tables_checked = 0
        self.tables_with_issues = 0
    
    def validate(self, sections_dir: Path) -> Tuple[List[str], int, int]:
        """Validate table headers in all section files.
        
        Args:
            sections_dir: Path to sections directory
            
        Returns:
            Tuple of (errors, tables_checked, tables_with_issues)
        """
        logger.debug(f"Validating table headers in {sections_dir}")
        
        self.errors = []
        self.tables_checked = 0
        self.tables_with_issues = 0
        
        for section_file in sections_dir.glob("*.json"):
            self._validate_section_file(section_file)
        
        logger.info(
            f"Checked {self.tables_checked} tables, "
            f"found {self.tables_with_issues} with issues"
        )
        
        return self.errors, self.tables_checked, self.tables_with_issues
    
    def _validate_section_file(self, section_file: Path) -> None:
        """Validate tables in a single section file.
        
        Args:
            section_file: Path to section JSON file
        """
        with open(section_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        section_name = section_file.stem
        
        for page_idx, page in enumerate(section_data.get('pages', [])):
            page_num = page.get('page_number', page_idx)
            
            for table_idx, table in enumerate(page.get('tables', [])):
                self._validate_single_table(
                    table, section_name, page_num, table_idx
                )
    
    def _validate_single_table(
        self,
        table: Dict,
        section_name: str,
        page_num: int,
        table_idx: int
    ) -> None:
        """Validate a single table for header metadata.
        
        Args:
            table: Table data dictionary
            section_name: Name of the section
            page_num: Page number
            table_idx: Table index on page
        """
        self.tables_checked += 1
        rows = table.get('rows', [])
        
        if len(rows) < 2:
            return  # Too few rows to validate
        
        first_row = rows[0]
        if not isinstance(first_row, dict) or 'cells' not in first_row:
            return
        
        cells = first_row.get('cells', [])
        if len(cells) < 2:
            return
        
        if self._looks_like_header_row(cells) and 'header_rows' not in table:
            self._report_missing_header(
                section_name, page_num, table_idx, cells
            )
    
    def _looks_like_header_row(self, cells: List[Dict]) -> bool:
        """Check if cells look like table headers.
        
        Args:
            cells: List of cell dictionaries
            
        Returns:
            True if cells appear to be headers
        """
        cell_texts = [cell.get('text', '').strip() for cell in cells]
        avg_length = (
            sum(len(text) for text in cell_texts) / len(cell_texts)
            if cell_texts else 0
        )
        
        # Heuristic: headers are short, no special characters
        return (
            avg_length < 20 and
            all(len(text) < 50 for text in cell_texts if text) and
            not any('/' in text or text.isdigit() 
                   for text in cell_texts[:3] if text)
        )
    
    def _report_missing_header(
        self,
        section_name: str,
        page_num: int,
        table_idx: int,
        cells: List[Dict]
    ) -> None:
        """Report a table missing header metadata.
        
        Args:
            section_name: Section name
            page_num: Page number
            table_idx: Table index
            cells: Table cells
        """
        self.tables_with_issues += 1
        cell_texts = [cell.get('text', '').strip() for cell in cells]
        
        error_msg = (
            f"Table in {section_name}, page {page_num}, table {table_idx} "
            f"appears to have a header row (first cells: {cell_texts[:3]}) "
            f"but is missing 'header_rows' metadata. This will cause headers "
            f"to render as data cells."
        )
        self.errors.append(error_msg)

