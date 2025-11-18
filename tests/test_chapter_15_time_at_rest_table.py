"""Test extraction of Time at Rest table in Chapter 15.

Tests that the Time at Rest table (part of Doom Legion spell) is correctly extracted with:
- 2 columns: Time at Rest and Chance to Ignore
- 11 rows (1 header + 10 data rows)
- Proper handling of time format ("# day", "# years", etc.)
- Proper handling of percentage format ("# %")
- Table ends before "An army" paragraph
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


def test_time_at_rest_table_exists():
    """Test that the Time at Rest table is extracted and added to the section."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the page containing the Time at Rest table (page 96)
    page_96 = None
    for page in chapter_15_data["pages"]:
        if page["page_number"] == 96:
            page_96 = page
            break
    
    assert page_96 is not None, "Page 96 not found"
    assert "tables" in page_96, "No tables found on page 96"
    
    # Find the Time at Rest table (should have "1 day" in first data row)
    time_at_rest_table = None
    for table in page_96["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1:
            # Check if second row (first data row) contains "1 day"
            if "day" in rows[1].get("cells", [])[0].get("text", "").lower():
                time_at_rest_table = table
                break
    
    assert time_at_rest_table is not None, "Time at Rest table not found"
    logger.info("✓ Found Time at Rest table")


def test_time_at_rest_table_structure():
    """Test that the Time at Rest table has the correct structure."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_96 = [p for p in chapter_15_data["pages"] if p["page_number"] == 96][0]
    time_at_rest_table = None
    for table in page_96["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "day" in rows[1].get("cells", [])[0].get("text", "").lower():
            time_at_rest_table = table
            break
    
    assert time_at_rest_table is not None
    
    # Check table structure
    rows = time_at_rest_table["rows"]
    assert len(rows) == 11, f"Expected 11 rows (1 header + 10 data), got {len(rows)}"
    
    # Check header row
    header_row = rows[0]
    assert len(header_row["cells"]) == 2, "Header should have 2 columns"
    assert "Time" in header_row["cells"][0]["text"] or "Rest" in header_row["cells"][0]["text"]
    assert "Chance" in header_row["cells"][1]["text"] or "Ignore" in header_row["cells"][1]["text"]
    
    # Check header_rows attribute
    assert time_at_rest_table["header_rows"] == 1
    logger.info("✓ Table structure is correct")


def test_time_at_rest_table_data():
    """Test that the Time at Rest table contains the correct data."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_96 = [p for p in chapter_15_data["pages"] if p["page_number"] == 96][0]
    time_at_rest_table = None
    for table in page_96["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "day" in rows[1].get("cells", [])[0].get("text", "").lower():
            time_at_rest_table = table
            break
    
    assert time_at_rest_table is not None
    rows = time_at_rest_table["rows"]
    
    # Expected data (row index, time at rest, chance to ignore)
    expected_data = [
        (1, "1 day", "90%"),
        (2, "1 week", "80%"),
        (3, "1 month", "70%"),
        (4, "3 months", "60%"),
        (5, "1 year", "50%"),
        (6, "5 years", "40%"),
        (7, "10 years", "30%"),
        (8, "50 years", "20%"),
        (9, "100 years", "10%"),
        (10, "Over 100 years", "0%"),
    ]
    
    for row_idx, expected_time, expected_chance in expected_data:
        actual_time = rows[row_idx]["cells"][0]["text"]
        actual_chance = rows[row_idx]["cells"][1]["text"]
        
        assert actual_time == expected_time, (
            f"Row {row_idx}: expected time '{expected_time}', got '{actual_time}'"
        )
        assert actual_chance == expected_chance, (
            f"Row {row_idx}: expected chance '{expected_chance}', got '{actual_chance}'"
        )
    
    logger.info("✓ Table data is correct")


def test_time_at_rest_fragments_skipped():
    """Test that table fragment blocks are marked to skip rendering."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find page 96
    page_96 = [p for p in chapter_15_data["pages"] if p["page_number"] == 96][0]
    blocks = page_96.get("blocks", [])
    
    # Count blocks marked to skip that contain table fragments
    skip_count = 0
    fragment_keywords = [
        "Time at Rest", "Chance to Ignore",
        "1 day", "9 0 %", "1 week", "8 0 %",
        "1 month", "7 0 %", "3 months", "6 0 %",
        "1 year", "5 0 %", "5 years", "4 0 %",
        "10 years", "3 0 %", "50 years", "2 0 %",
        "100 years", "1 0 %", "Over 100 years", "0 %"
    ]
    
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
    
    # We should have skipped multiple fragment blocks
    assert skip_count >= 8, f"Expected at least 8 fragment blocks to be skipped, got {skip_count}"
    logger.info(f"✓ Skipped {skip_count} fragment blocks")


def test_time_at_rest_table_does_not_include_next_paragraph():
    """Test that the Time at Rest table stops before the next paragraph."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_96 = [p for p in chapter_15_data["pages"] if p["page_number"] == 96][0]
    time_at_rest_table = None
    for table in page_96["tables"]:
        rows = table.get("rows", [])
        if len(rows) > 1 and "day" in rows[1].get("cells", [])[0].get("text", "").lower():
            time_at_rest_table = table
            break
    
    assert time_at_rest_table is not None
    rows = time_at_rest_table["rows"]
    
    # Check that no row contains "An army"
    for row in rows:
        for cell in row["cells"]:
            assert "An army" not in cell["text"], (
                "Table should not include 'An army' paragraph text"
            )
    
    logger.info("✓ Table ends correctly")


if __name__ == "__main__":
    # Run all tests
    print("Running Time at Rest table extraction tests...")
    
    try:
        print("\n1. Testing table exists...")
        test_time_at_rest_table_exists()
        print("   ✅ PASSED: Table exists")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n2. Testing table structure...")
        test_time_at_rest_table_structure()
        print("   ✅ PASSED: Table structure correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n3. Testing table data...")
        test_time_at_rest_table_data()
        print("   ✅ PASSED: Table data correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n4. Testing fragments skipped...")
        test_time_at_rest_fragments_skipped()
        print("   ✅ PASSED: Fragments skipped")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n5. Testing table doesn't include next paragraph...")
        test_time_at_rest_table_does_not_include_next_paragraph()
        print("   ✅ PASSED: Table ends correctly")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

