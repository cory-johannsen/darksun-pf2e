"""Unit tests for process_height_weight_table() and its helper functions.

Tests the refactored Height and Weight table extraction logic from Chapter 2.
"""

import pytest
from tools.pdf_pipeline.transformers.chapter_2.physical_tables import (
    process_height_weight_table,
    _line_text,
    _find_hw_table_bounds,
    _reposition_existing_hw_table,
    _extract_hw_header_positions,
    _collect_hw_row_anchors,
    _build_hw_data_rows,
)


class TestLineText:
    """Tests for _line_text() helper function."""
    
    def test_extracts_simple_text(self):
        """Should extract text from a line with single span."""
        line = {"spans": [{"text": "Test"}]}
        assert _line_text(line) == "Test"
    
    def test_extracts_multispan_text(self):
        """Should concatenate text from multiple spans."""
        line = {"spans": [{"text": "Hello"}, {"text": " "}, {"text": "World"}]}
        assert _line_text(line) == "Hello World"
    
    def test_strips_whitespace(self):
        """Should strip leading and trailing whitespace."""
        line = {"spans": [{"text": "  Trimmed  "}]}
        assert _line_text(line) == "Trimmed"
    
    def test_handles_empty_line(self):
        """Should handle line with no spans."""
        line = {"spans": []}
        assert _line_text(line) == ""


class TestFindHWTableBounds:
    """Tests for _find_hw_table_bounds() helper function."""
    
    def test_finds_bounds_successfully(self):
        """Should find section bounds when header exists."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "bbox": [100, 200, 300, 220],
                    "lines": [{"spans": [{"text": "Height and Weight"}]}]
                },
                {
                    "type": "text",
                    "bbox": [100, 400, 300, 420],
                    "lines": [{"spans": [{"text": "Age"}]}]
                }
            ],
            "height": 800
        }
        result = _find_hw_table_bounds(page)
        assert result is not None
        hw_bbox, y_min, y_max = result
        assert hw_bbox == [100, 200, 300, 220]
        assert y_min == 222.0  # 220 + 2.0
        assert y_max == 398.0  # 400 - 2.0
    
    def test_returns_none_when_header_missing(self):
        """Should return None when Height and Weight header is not found."""
        page = {"blocks": []}
        assert _find_hw_table_bounds(page) is None


class TestRepositionExistingHWTable:
    """Tests for _reposition_existing_hw_table() helper function."""
    
    def test_repositions_existing_table(self):
        """Should reposition table and return True when found."""
        page = {
            "blocks": [],
            "width": 612.0,
            "tables": [
                {
                    "rows": [
                        {
                            "cells": [
                                {"text": "Race"},
                                {"text": "Height in Inches"},
                                {"text": "Weight in Pounds"}
                            ]
                        }
                    ],
                    "header_rows": 2,
                    "bbox": [0, 500, 600, 600]
                }
            ]
        }
        hw_bbox = [0, 100, 600, 120]
        y_max = 700
        
        result = _reposition_existing_hw_table(page, hw_bbox, y_max)
        assert result is True
        assert page["tables"][0]["bbox"][1] == 121.0  # desired_top = 120 + 1
    
    def test_returns_false_when_no_table(self):
        """Should return False when no matching table exists."""
        page = {"blocks": [], "tables": []}
        hw_bbox = [0, 100, 600, 120]
        y_max = 700
        
        result = _reposition_existing_hw_table(page, hw_bbox, y_max)
        assert result is False


class TestExtractHWHeaderPositions:
    """Tests for _extract_hw_header_positions() helper function."""
    
    def test_extracts_header_positions(self):
        """Should extract column positions from header blocks."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "bbox": [50, 100, 150, 120],
                    "lines": [
                        {"spans": [{"text": "Height in Inches"}], "bbox": [50, 100, 150, 110]},
                        {"spans": [{"text": "Race"}], "bbox": [50, 110, 100, 120]},
                        {"spans": [{"text": "Base"}], "bbox": [150, 110, 200, 120]},
                        {"spans": [{"text": "Modifier"}], "bbox": [200, 110, 250, 120]}
                    ]
                },
                {
                    "type": "text",
                    "bbox": [300, 100, 400, 120],
                    "lines": [
                        {"spans": [{"text": "Weight in Pounds"}], "bbox": [300, 100, 400, 110]},
                        {"spans": [{"text": "Base"}], "bbox": [300, 110, 350, 120]},
                        {"spans": [{"text": "Modifier"}], "bbox": [350, 110, 400, 120]}
                    ]
                }
            ]
        }
        result = _extract_hw_header_positions(page)
        assert result is not None
        race_x1, h_base_x, h_mod_x, w_base_x, w_mod_x = result
        assert race_x1 == 100
        assert h_base_x == 175.0  # (150 + 200) / 2
        assert h_mod_x == 225.0  # (200 + 250) / 2
        assert w_base_x == 325.0  # (300 + 350) / 2
        assert w_mod_x == 375.0  # (350 + 400) / 2
    
    def test_returns_none_when_headers_missing(self):
        """Should return None when required headers are not found."""
        page = {"blocks": []}
        assert _extract_hw_header_positions(page) is None


class TestCollectHWRowAnchors:
    """Tests for _collect_hw_row_anchors() helper function."""
    
    def test_collects_row_anchors(self):
        """Should collect race names as row anchors."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "lines": [
                        {"spans": [{"text": "Human"}], "bbox": [50, 200, 100, 210]},
                        {"spans": [{"text": "Elf"}], "bbox": [50, 220, 90, 230]},
                        {"spans": [{"text": "Dwarf"}], "bbox": [50, 240, 100, 250]}
                    ]
                }
            ]
        }
        y_min = 190
        y_max = 260
        race_split_x = 120
        
        result = _collect_hw_row_anchors(page, y_min, y_max, race_split_x)
        assert len(result) == 3
        assert result[0][1] == "Human"
        assert result[1][1] == "Elf"
        assert result[2][1] == "Dwarf"
    
    def test_merges_fragmented_text(self):
        """Should merge text fragments that are close together."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "lines": [
                        {"spans": [{"text": "Hu"}], "bbox": [50, 200, 70, 210]},
                        {"spans": [{"text": "man"}], "bbox": [75, 201, 100, 211]}
                    ]
                }
            ]
        }
        y_min = 190
        y_max = 260
        race_split_x = 120
        
        result = _collect_hw_row_anchors(page, y_min, y_max, race_split_x)
        assert len(result) == 1
        # _join_fragments adds a space between fragments
        assert result[0][1] == "Hu man"  # Merged with space
    
    def test_filters_by_y_bounds(self):
        """Should filter out lines outside y bounds."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "lines": [
                        {"spans": [{"text": "Above"}], "bbox": [50, 100, 100, 110]},
                        {"spans": [{"text": "Human"}], "bbox": [50, 200, 100, 210]},
                        {"spans": [{"text": "Below"}], "bbox": [50, 300, 100, 310]}
                    ]
                }
            ]
        }
        y_min = 190
        y_max = 260
        race_split_x = 120
        
        result = _collect_hw_row_anchors(page, y_min, y_max, race_split_x)
        assert len(result) == 1
        assert result[0][1] == "Human"
    
    def test_returns_empty_when_no_anchors(self):
        """Should return empty list when no valid anchors found."""
        page = {"blocks": []}
        result = _collect_hw_row_anchors(page, 100, 200, 150)
        assert result == []


class TestBuildHWDataRows:
    """Tests for _build_hw_data_rows() helper function."""
    
    def test_builds_data_rows(self):
        """Should build data rows from row anchors."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "lines": [
                        {"spans": [{"text": "Human"}], "bbox": [50, 200, 100, 210]},
                        {"spans": [{"text": "60"}], "bbox": [150, 200, 170, 210]},
                        {"spans": [{"text": "+2d10"}], "bbox": [200, 200, 240, 210]},
                        {"spans": [{"text": "140"}], "bbox": [300, 200, 330, 210]},
                        {"spans": [{"text": "+6d10"}], "bbox": [350, 200, 390, 210]}
                    ]
                }
            ]
        }
        row_anchors = [(205, "Human")]
        h_base_x = 160
        h_mod_x = 220
        w_base_x = 315
        w_mod_x = 370
        
        result = _build_hw_data_rows(page, row_anchors, h_base_x, h_mod_x, w_base_x, w_mod_x)
        assert len(result) == 1
        assert result[0]["cells"][0]["text"] == "Human"
        assert result[0]["cells"][1]["text"] == "60"
        assert result[0]["cells"][2]["text"] == "+2d10"
        assert result[0]["cells"][3]["text"] == "140"
        assert result[0]["cells"][4]["text"] == "+6d10"
    
    def test_accepts_rows_with_minimum_cells(self):
        """Should accept rows with exactly 3 populated cells."""
        page = {
            "blocks": [
                {
                    "type": "text",
                    "lines": [
                        {"spans": [{"text": "Human"}], "bbox": [50, 200, 100, 210]},
                        {"spans": [{"text": "60"}], "bbox": [150, 200, 170, 210]},
                        {"spans": [{"text": "+2d10"}], "bbox": [200, 200, 240, 210]}
                        # Missing weight columns - _find_near will find other nearby text
                    ]
                }
            ]
        }
        row_anchors = [(205, "Human")]
        h_base_x = 160
        h_mod_x = 220
        w_base_x = 500  # Far away, won't find data
        w_mod_x = 550  # Far away, won't find data
        
        result = _build_hw_data_rows(page, row_anchors, h_base_x, h_mod_x, w_base_x, w_mod_x)
        # Should pass with race + 2 height values (3 cells) even without weight values
        assert len(result) >= 1  # Row accepted due to >= 3 populated cells


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

