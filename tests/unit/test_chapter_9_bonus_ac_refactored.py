"""Unit tests for refactored bonus AC table extraction functions.

Tests the helper functions extracted from _extract_and_reconstruct_bonus_ac_table().
"""

import pytest
from typing import Dict, List

# Import the functions we're testing
from tools.pdf_pipeline.transformers.chapter_9_processing import (
    _find_bonus_ac_header,
    _get_ordered_armor_types,
    _extract_armor_full_suit_values,
    _extract_remaining_numeric_values,
    _reconstruct_armor_rows,
    _create_formatted_table,
    _mark_fragmented_blocks_to_skip,
)


class TestFindBonusAcHeader:
    """Test _find_bonus_ac_header function."""
    
    def test_finds_header_in_first_page(self):
        """Test finding header on first page."""
        pages = [
            {
                "blocks": [
                    {
                        "type": "text",
                        "lines": [
                            {
                                "spans": [
                                    {"text": "Bonus to AC Per Type of Piece"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
        
        result = _find_bonus_ac_header(pages)
        assert result is not None
        assert result[0] == 0  # page_idx
        assert result[1] == 0  # block_idx
        assert result[2] == pages[0]["blocks"][0]  # block
    
    def test_finds_header_in_later_page(self):
        """Test finding header on a later page."""
        pages = [
            {"blocks": [{"type": "text", "lines": [{"spans": [{"text": "Other text"}]}]}]},
            {"blocks": [{"type": "text", "lines": [{"spans": [{"text": "Bonus to AC Per Type of Piece"}]}]}]},
        ]
        
        result = _find_bonus_ac_header(pages)
        assert result is not None
        assert result[0] == 1  # page_idx
    
    def test_returns_none_when_not_found(self):
        """Test returns None when header not found."""
        pages = [
            {"blocks": [{"type": "text", "lines": [{"spans": [{"text": "Other text"}]}]}]}
        ]
        
        result = _find_bonus_ac_header(pages)
        assert result is None
    
    def test_skips_non_text_blocks(self):
        """Test that non-text blocks are skipped."""
        pages = [
            {
                "blocks": [
                    {"type": "image"},
                    {
                        "type": "text",
                        "lines": [{"spans": [{"text": "Bonus to AC Per Type of Piece"}]}]
                    }
                ]
            }
        ]
        
        result = _find_bonus_ac_header(pages)
        assert result is not None
        assert result[1] == 1  # Found in second block


class TestGetOrderedArmorTypes:
    """Test _get_ordered_armor_types function."""
    
    def test_returns_correct_count(self):
        """Test returns 14 armor types."""
        result = _get_ordered_armor_types()
        assert len(result) == 14
    
    def test_includes_expected_types(self):
        """Test includes expected armor types."""
        result = _get_ordered_armor_types()
        assert "Banded Mail" in result
        assert "Bronze Plate" in result
        assert "Leather Armor" in result
        assert "Full Plate" in result
    
    def test_alphabetical_order(self):
        """Test armor types are in alphabetical order."""
        result = _get_ordered_armor_types()
        assert result == sorted(result)


class TestExtractArmorFullSuitValues:
    """Test _extract_armor_full_suit_values function."""
    
    def test_extracts_simple_values(self):
        """Test extracting armor names with values."""
        tables = [
            {
                "rows": [
                    {
                        "cells": [
                            {"text": "Banded Mail 6 Brigandine 4 "}
                        ]
                    }
                ]
            }
        ]
        
        result = _extract_armor_full_suit_values(tables)
        assert "Banded Mail" in result
        assert result["Banded Mail"] == "6"
        assert "Brigandine" in result
        assert result["Brigandine"] == "4"
    
    def test_normalizes_whitespace(self):
        """Test normalizes extra whitespace in armor names."""
        tables = [
            {
                "rows": [
                    {
                        "cells": [
                            {"text": "Bronze  Plate 6 "}
                        ]
                    }
                ]
            }
        ]
        
        result = _extract_armor_full_suit_values(tables)
        assert "Bronze Plate" in result  # Normalized from "Bronze  Plate"
        assert result["Bronze Plate"] == "6"
    
    def test_handles_multiple_tables(self):
        """Test extracting from multiple tables."""
        tables = [
            {"rows": [{"cells": [{"text": "Chain Mail 5 "}]}]},
            {"rows": [{"cells": [{"text": "Scale Mail 4 "}]}]},
        ]
        
        result = _extract_armor_full_suit_values(tables)
        assert len(result) >= 2
        assert "Chain Mail" in result
        assert "Scale Mail" in result


class TestExtractRemainingNumericValues:
    """Test _extract_remaining_numeric_values function."""
    
    def test_extracts_single_digits(self):
        """Test extracts single-digit numeric values."""
        tables = [
            {
                "rows": [
                    {
                        "cells": [
                            {"text": "3 4 5"}
                        ]
                    }
                ]
            }
        ]
        
        result = _extract_remaining_numeric_values(tables)
        assert result == ["3", "4", "5"]
    
    def test_skips_cells_with_letters(self):
        """Test skips cells that contain letters."""
        tables = [
            {
                "rows": [
                    {
                        "cells": [
                            {"text": "Armor 5"},  # Has letters, skip
                            {"text": "3 4"}       # Only numbers, include
                        ]
                    }
                ]
            }
        ]
        
        result = _extract_remaining_numeric_values(tables)
        assert result == ["3", "4"]
    
    def test_handles_empty_cells(self):
        """Test handles empty cells gracefully."""
        tables = [
            {
                "rows": [
                    {
                        "cells": [
                            {"text": ""},
                            {"text": "5 6"}
                        ]
                    }
                ]
            }
        ]
        
        result = _extract_remaining_numeric_values(tables)
        assert result == ["5", "6"]


class TestReconstructArmorRows:
    """Test _reconstruct_armor_rows function."""
    
    def test_reconstructs_complete_rows(self):
        """Test reconstructing rows with complete data."""
        armor_types = ["Banded Mail", "Brigandine"]
        full_suit_map = {"Banded Mail": "6", "Brigandine": "4"}
        numeric_values = ["3", "2", "1", "1", "0", "2", "1", "1", "0", "0"]
        
        result = _reconstruct_armor_rows(armor_types, full_suit_map, numeric_values)
        
        assert len(result) == 2
        assert result[0][0] == "Banded Mail"
        assert result[0][1] == "6"
        assert len(result[0]) == 7  # Name + 6 values
        
        assert result[1][0] == "Brigandine"
        assert result[1][1] == "4"
    
    def test_pads_insufficient_values(self):
        """Test pads with zeros when not enough values."""
        armor_types = ["Banded Mail"]
        full_suit_map = {"Banded Mail": "6"}
        numeric_values = ["3", "2"]  # Only 2 values, need 5 more
        
        result = _reconstruct_armor_rows(armor_types, full_suit_map, numeric_values)
        
        assert len(result) == 1
        assert len(result[0]) == 7  # Name + 6 values
        assert result[0][-3:] == ["0", "0", "0"]  # Padded with zeros
    
    def test_handles_missing_armor_in_map(self):
        """Test handles armor type not in full suit map."""
        armor_types = ["Banded Mail"]
        full_suit_map = {}  # Empty map
        numeric_values = ["3", "2", "1", "1", "0"]
        
        result = _reconstruct_armor_rows(armor_types, full_suit_map, numeric_values)
        
        assert len(result) == 1
        assert result[0][1] == "0"  # Default value when not in map


class TestCreateFormattedTable:
    """Test _create_formatted_table function."""
    
    def test_creates_table_with_header(self):
        """Test creates table with proper header row."""
        table_rows = [
            ["Banded Mail", "6", "3", "2", "1", "1", "0"]
        ]
        header_block = {"bbox": [10, 20, 30, 40]}
        
        result = _create_formatted_table(table_rows, header_block)
        
        assert "header_rows" in result
        assert result["header_rows"] == 1
        assert "rows" in result
        assert len(result["rows"]) == 2  # Header + 1 data row
    
    def test_header_row_structure(self):
        """Test header row has correct columns."""
        table_rows = [["Armor", "1", "2", "3", "4", "5", "6"]]
        header_block = {"bbox": [0, 0, 0, 0]}
        
        result = _create_formatted_table(table_rows, header_block)
        
        header_row = result["rows"][0]
        assert header_row["cells"][0]["text"] == "Armor Type"
        assert header_row["cells"][1]["text"] == "Full Suit"
        assert header_row["cells"][2]["text"] == "Breast Plate"
        assert header_row["cells"][6]["text"] == "One Leg"
    
    def test_data_row_structure(self):
        """Test data rows have correct structure."""
        table_rows = [["Banded Mail", "6", "3", "2", "1", "1", "0"]]
        header_block = {"bbox": [0, 0, 0, 0]}
        
        result = _create_formatted_table(table_rows, header_block)
        
        data_row = result["rows"][1]
        assert len(data_row["cells"]) == 7
        assert data_row["cells"][0]["text"] == "Banded Mail"
        assert data_row["cells"][1]["text"] == "6"


class TestMarkFragmentedBlocksToSkip:
    """Test _mark_fragmented_blocks_to_skip function."""
    
    def test_marks_blocks_after_header(self):
        """Test marks blocks after header index."""
        page = {
            "blocks": [
                {"type": "text", "lines": [{"spans": [{"text": "Header"}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "Fragmented"}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "plate from a suit"}]}]},
            ]
        }
        
        result = _mark_fragmented_blocks_to_skip(page, 0)
        
        assert result == 1  # One block marked
        assert "__skip_render" in page["blocks"][1]
        assert page["blocks"][1]["__skip_render"] is True
    
    def test_stops_at_continuation_text(self):
        """Test stops marking when reaching continuation text."""
        page = {
            "blocks": [
                {"type": "text", "lines": [{"spans": [{"text": "Header"}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "Block 1"}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "Block 2"}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "...plate from a suit of armor..."}]}]},
                {"type": "text", "lines": [{"spans": [{"text": "Block 3"}]}]},
            ]
        }
        
        result = _mark_fragmented_blocks_to_skip(page, 0)
        
        assert result == 2  # Only blocks 1 and 2 marked
        assert "__skip_render" in page["blocks"][1]
        assert "__skip_render" in page["blocks"][2]
        assert "__skip_render" not in page["blocks"][3]  # Continuation text
        assert "__skip_render" not in page["blocks"][4]  # After continuation
    
    def test_skips_non_text_blocks(self):
        """Test doesn't mark non-text blocks."""
        page = {
            "blocks": [
                {"type": "text", "lines": [{"spans": [{"text": "Header"}]}]},
                {"type": "image"},
                {"type": "text", "lines": [{"spans": [{"text": "plate from a suit"}]}]},
            ]
        }
        
        result = _mark_fragmented_blocks_to_skip(page, 0)
        
        assert result == 0  # Image block skipped, no text blocks marked
        assert "__skip_render" not in page["blocks"][1]


# Integration test
class TestBonusAcTableIntegration:
    """Integration tests for the complete bonus AC table extraction."""
    
    def test_end_to_end_extraction(self):
        """Test complete extraction process with minimal data."""
        # This would be a more complex integration test
        # For now, just verify all functions work together
        
        pages = [{"blocks": [{"type": "text", "lines": [{"spans": [{"text": "Bonus to AC Per Type of Piece"}]}]}]}]
        header_info = _find_bonus_ac_header(pages)
        assert header_info is not None
        
        armor_types = _get_ordered_armor_types()
        assert len(armor_types) == 14
        
        # Create minimal table structure
        tables = [{"rows": [{"cells": [{"text": "Banded Mail 6 "}]}]}]
        full_suit_map = _extract_armor_full_suit_values(tables)
        assert "Banded Mail" in full_suit_map
        
        # Create formatted table
        table_rows = [["Banded Mail", "6", "3", "2", "1", "1", "0"]]
        formatted = _create_formatted_table(table_rows, {"bbox": [0, 0, 0, 0]})
        assert "header_rows" in formatted
        assert len(formatted["rows"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

