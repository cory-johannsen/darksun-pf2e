#!/usr/bin/env python3
"""
Unit tests for the build_multiclass_table function.

Tests that the function correctly builds 2-column tables in column-first order.
"""

import sys
sys.path.insert(0, '/Users/cjohannsen/git/darksun-pf2e/tools')

from pdf_pipeline.transformers.chapter_3_processing import build_multiclass_table


def test_basic_8_combinations():
    """Test with 8 combinations (4 rows x 2 columns)."""
    combinations = ["A", "B", "C", "D", "E", "F", "G", "H"]
    
    result = build_multiclass_table(combinations, num_cols=2)
    
    rows = result["rows"]
    assert len(rows) == 4, f"Expected 4 rows, got {len(rows)}"
    
    # Check layout (column-first order):
    # | A | E |
    # | B | F |
    # | C | G |
    # | D | H |
    assert rows[0]["cells"][0]["text"] == "A"
    assert rows[0]["cells"][1]["text"] == "E"
    assert rows[1]["cells"][0]["text"] == "B"
    assert rows[1]["cells"][1]["text"] == "F"
    assert rows[2]["cells"][0]["text"] == "C"
    assert rows[2]["cells"][1]["text"] == "G"
    assert rows[3]["cells"][0]["text"] == "D"
    assert rows[3]["cells"][1]["text"] == "H"
    
    print("✓ Test 8 combinations passed")


def test_7_combinations_dwarf():
    """Test with 7 combinations (Dwarf case: 4 rows, last row has empty cell)."""
    combinations = [
        "Cleric/Psionicist",
        "Fighter/Cleric",
        "Fighter/Psionicist",
        "Fighter/Thief",
        "Thief/Psionicist",
        "Fighter/Cleric/Psionicist",
        "Fighter/Thief/Psionicist"
    ]
    
    result = build_multiclass_table(combinations, num_cols=2)
    
    rows = result["rows"]
    assert len(rows) == 4, f"Expected 4 rows, got {len(rows)}"
    
    # Column-first: First 4 go in left column, next 3 in right column
    # | Cleric/Psionicist           | Thief/Psionicist          |
    # | Fighter/Cleric              | Fighter/Cleric/Psionicist |
    # | Fighter/Psionicist          | Fighter/Thief/Psionicist  |
    # | Fighter/Thief               |                           |
    
    assert rows[0]["cells"][0]["text"] == "Cleric/Psionicist"
    assert rows[0]["cells"][1]["text"] == "Thief/Psionicist"
    assert rows[1]["cells"][0]["text"] == "Fighter/Cleric"
    assert rows[1]["cells"][1]["text"] == "Fighter/Cleric/Psionicist"
    assert rows[2]["cells"][0]["text"] == "Fighter/Psionicist"
    assert rows[2]["cells"][1]["text"] == "Fighter/Thief/Psionicist"
    assert rows[3]["cells"][0]["text"] == "Fighter/Thief"
    assert rows[3]["cells"][1]["text"] == ""  # Empty cell
    
    print("✓ Test 7 combinations (Dwarf) passed")


def test_3_combinations_half_giant():
    """Test with 3 combinations (Half-giant case: 2 rows)."""
    combinations = [
        "Fighter/Cleric",
        "Fighter/Psionicist",
        "Cleric/Psionicist"
    ]
    
    result = build_multiclass_table(combinations, num_cols=2)
    
    rows = result["rows"]
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
    
    # Column-first: First 2 in left column, last 1 in right
    # | Fighter/Cleric     | Cleric/Psionicist |
    # | Fighter/Psionicist |                   |
    
    assert rows[0]["cells"][0]["text"] == "Fighter/Cleric"
    assert rows[0]["cells"][1]["text"] == "Cleric/Psionicist"
    assert rows[1]["cells"][0]["text"] == "Fighter/Psionicist"
    assert rows[1]["cells"][1]["text"] == ""
    
    print("✓ Test 3 combinations (Half-giant) passed")


def test_empty_list():
    """Test with empty list."""
    result = build_multiclass_table([], num_cols=2)
    
    assert result["rows"] == []
    
    print("✓ Test empty list passed")


def test_cell_structure():
    """Test that cells have the correct structure for journal.py."""
    combinations = ["Fighter/Cleric", "Fighter/Thief"]
    
    result = build_multiclass_table(combinations, num_cols=2)
    
    cell = result["rows"][0]["cells"][0]
    
    # Check required fields
    assert "text" in cell
    assert "spans" in cell
    assert isinstance(cell["spans"], list)
    assert len(cell["spans"]) > 0
    assert cell["spans"][0]["text"] == "Fighter/Cleric"
    
    print("✓ Test cell structure passed")


if __name__ == "__main__":
    try:
        test_basic_8_combinations()
        test_7_combinations_dwarf()
        test_3_combinations_half_giant()
        test_empty_list()
        test_cell_structure()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)

