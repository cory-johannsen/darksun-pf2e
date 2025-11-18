"""Test extraction of Doom Legion table in Chapter 15.

Tests that the Doom Legion spell table is correctly extracted with:
- 2 columns: Battle Type and Dice Roll
- 4 rows (1 header + 3 data rows)
- Proper handling of dice spec format "#d#"
- Table ends before "Animated bodies that are less than" text
"""

import json
import logging
from pathlib import Path

# Import the extraction function
from tools.pdf_pipeline.transformers.chapter_15_processing import (
    apply_chapter_15_adjustments,
)

logger = logging.getLogger(__name__)


def load_chapter_15_data():
    """Load the raw Chapter 15 JSON data."""
    data_path = Path("data/raw_structured/sections/02-092-chapter-fifteen-new-spells.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_doom_legion_table_exists():
    """Test that the Doom Legion table is extracted and added to the section."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the page containing the Doom Legion table (page 95)
    page_95 = None
    for page in chapter_15_data["pages"]:
        if page["page_number"] == 95:
            page_95 = page
            break
    
    assert page_95 is not None, "Page 95 not found"
    assert "tables" in page_95, "No tables found on page 95"
    
    # Find the Doom Legion table (should have "Skirmish" in first data row)
    doom_legion_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1:
            # Check if second row (first data row) contains "Skirmish"
            if "Skirmish" in rows[1].get("cells", [])[0].get("text", ""):
                doom_legion_table = table
                break
    
    assert doom_legion_table is not None, "Doom Legion table not found"
    logger.info("✓ Found Doom Legion table")


def test_doom_legion_table_structure():
    """Test that the Doom Legion table has the correct structure."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    doom_legion_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "Skirmish" in rows[1].get("cells", [])[0].get("text", ""):
            doom_legion_table = table
            break
    
    assert doom_legion_table is not None
    
    # Check table structure
    rows = doom_legion_table["rows"]
    assert len(rows) == 4, f"Expected 4 rows (1 header + 3 data), got {len(rows)}"
    
    # Check header row
    header_row = rows[0]
    assert len(header_row["cells"]) == 2, "Header should have 2 columns"
    assert "Battle" in header_row["cells"][0]["text"] or "Type" in header_row["cells"][0]["text"]
    assert "Dice" in header_row["cells"][1]["text"] or "Roll" in header_row["cells"][1]["text"]
    
    # Check header_rows attribute
    assert doom_legion_table["header_rows"] == 1
    logger.info("✓ Table structure is correct")


def test_doom_legion_table_data():
    """Test that the Doom Legion table contains the correct data."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    doom_legion_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "Skirmish" in rows[1].get("cells", [])[0].get("text", ""):
            doom_legion_table = table
            break
    
    assert doom_legion_table is not None
    rows = doom_legion_table["rows"]
    
    # Expected data (row index, battle type, dice roll)
    expected_data = [
        (1, "Skirmish", "3d12"),
        (2, "Small Battle", "6d12"),
        (3, "Major Battle", "10d20"),
    ]
    
    for row_idx, expected_type, expected_dice in expected_data:
        actual_type = rows[row_idx]["cells"][0]["text"]
        actual_dice = rows[row_idx]["cells"][1]["text"]
        
        assert actual_type == expected_type, (
            f"Row {row_idx}: expected type '{expected_type}', got '{actual_type}'"
        )
        assert actual_dice == expected_dice, (
            f"Row {row_idx}: expected dice '{expected_dice}', got '{actual_dice}'"
        )
    
    logger.info("✓ Table data is correct")


def test_doom_legion_fragments_skipped():
    """Test that table fragment blocks are marked to skip rendering."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find page 95
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    blocks = page_95.get("blocks", [])
    
    # Count blocks marked to skip that contain table fragments
    skip_count = 0
    fragment_keywords = ["S k i r m i s h", "3 d 12", "Small Battle", "6d12", "Major Battle", "10d20"]
    
    for block in blocks:
        if block.get("type") != "text":
            continue
        
        text = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text += span.get("text", "")
        
        # Check if this block contains table fragments and is marked to skip
        if any(keyword in text for keyword in fragment_keywords):
            if block.get("__skip_render"):
                skip_count += 1
    
    # We should have skipped 3 fragment blocks (one for each row)
    assert skip_count >= 3, f"Expected at least 3 fragment blocks to be skipped, got {skip_count}"
    logger.info(f"✓ Skipped {skip_count} fragment blocks")


def test_doom_legion_table_does_not_include_next_paragraph():
    """Test that the Doom Legion table stops before the next paragraph."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    doom_legion_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "Skirmish" in rows[1].get("cells", [])[0].get("text", ""):
            doom_legion_table = table
            break
    
    assert doom_legion_table is not None
    rows = doom_legion_table["rows"]
    
    # Check that no row contains "Animated"
    for row in rows:
        for cell in row["cells"]:
            assert "Animated" not in cell["text"], (
                "Table should not include 'Animated bodies' paragraph text"
            )
    
    logger.info("✓ Table ends correctly")


if __name__ == "__main__":
    # Run all tests
    print("Running Doom Legion table extraction tests...")
    
    try:
        print("\n1. Testing table exists...")
        test_doom_legion_table_exists()
        print("   ✅ PASSED: Table exists")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n2. Testing table structure...")
        test_doom_legion_table_structure()
        print("   ✅ PASSED: Table structure correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n3. Testing table data...")
        test_doom_legion_table_data()
        print("   ✅ PASSED: Table data correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n4. Testing fragments skipped...")
        test_doom_legion_fragments_skipped()
        print("   ✅ PASSED: Fragments skipped")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n5. Testing table doesn't include next paragraph...")
        test_doom_legion_table_does_not_include_next_paragraph()
        print("   ✅ PASSED: Table ends correctly")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

