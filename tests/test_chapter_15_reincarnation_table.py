"""Test extraction of Reincarnation table in Chapter 15.

Tests that the Reincarnation spell table is correctly extracted with:
- 2 columns: D100 Roll and Incarnation
- 15 rows (1 header + 14 data rows)
- Proper handling of D100 range format "#-#"
- Proper handling of Incarnation values with hyphens and commas
- Table ends before "Transmute Water to Dust" spell
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


def test_reincarnation_table_exists():
    """Test that the Reincarnation table is extracted and added to the section."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the page containing the Reincarnation table
    # The spell header "R e i n c a r n a t i o n" is on page 95
    page_95 = None
    for page in chapter_15_data["pages"]:
        if page["page_number"] == 95:
            page_95 = page
            break
    
    assert page_95 is not None, "Page 95 not found"
    assert "tables" in page_95, "No tables found on page 95"
    
    # Find the Reincarnation table
    reincarnation_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if rows and rows[0].get("cells", [])[0].get("text") == "D100 Roll":
            reincarnation_table = table
            break
    
    assert reincarnation_table is not None, "Reincarnation table not found"


def test_reincarnation_table_structure():
    """Test that the Reincarnation table has the correct structure."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    reincarnation_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if rows and rows[0].get("cells", [])[0].get("text") == "D100 Roll":
            reincarnation_table = table
            break
    
    assert reincarnation_table is not None
    
    # Check table structure
    rows = reincarnation_table["rows"]
    assert len(rows) == 15, f"Expected 15 rows (1 header + 14 data), got {len(rows)}"
    
    # Check header row
    header_row = rows[0]
    assert len(header_row["cells"]) == 2, "Header should have 2 columns"
    assert header_row["cells"][0]["text"] == "D100 Roll"
    assert header_row["cells"][1]["text"] == "Incarnation"
    
    # Check header_rows attribute
    assert reincarnation_table["header_rows"] == 1


def test_reincarnation_table_data():
    """Test that the Reincarnation table contains the correct data."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    reincarnation_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if rows and rows[0].get("cells", [])[0].get("text") == "D100 Roll":
            reincarnation_table = table
            break
    
    assert reincarnation_table is not None
    rows = reincarnation_table["rows"]
    
    # Expected data (row index, d100 range, incarnation)
    expected_data = [
        (1, "01-08", "Aarakocra"),
        (2, "09-16", "Belgoi"),
        (3, "17-24", "Dwarf"),
        (4, "25-32", "Elf"),
        (5, "33-34", "Giant"),
        (6, "35-37", "Giant-kin, Cyclops"),
        (7, "38-48", "Half-elf"),
        (8, "49-55", "Half-giant"),
        (9, "56-66", "Halfling"),
        (10, "67-78", "Human"),
        (11, "79-85", "Kenku"),
        (12, "86-89", "Mul"),
        (13, "90-96", "Thri-kreen"),
        (14, "97-00", "Yuan-ti"),
    ]
    
    for row_idx, expected_roll, expected_incarnation in expected_data:
        actual_roll = rows[row_idx]["cells"][0]["text"]
        actual_incarnation = rows[row_idx]["cells"][1]["text"]
        
        assert actual_roll == expected_roll, (
            f"Row {row_idx}: expected roll '{expected_roll}', got '{actual_roll}'"
        )
        assert actual_incarnation == expected_incarnation, (
            f"Row {row_idx}: expected incarnation '{expected_incarnation}', "
            f"got '{actual_incarnation}'"
        )


def test_reincarnation_fragments_skipped():
    """Test that table fragment blocks are marked to skip rendering."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find page 95
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    blocks = page_95.get("blocks", [])
    
    # Count blocks marked to skip that contain table fragments
    skip_count = 0
    fragment_keywords = [
        "D100", "Roll", "Incarnation", "Aarakocra", "Belgoi", "Dwarf", "Elf",
        "Giant", "Cyclops", "Half-elf", "Half-giant", "Halfling", "Human",
        "Kenku", "M u l", "Thri-kreen", "Yuan-ti"
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
    assert skip_count > 5, f"Expected at least 6 fragment blocks to be skipped, got {skip_count}"


def test_reincarnation_table_does_not_include_transmute_water():
    """Test that the Reincarnation table stops before the next spell."""
    chapter_15_data = load_chapter_15_data()
    # Apply the extraction
    apply_chapter_15_adjustments(chapter_15_data)
    
    # Find the table
    page_95 = [p for p in chapter_15_data["pages"] if p["page_number"] == 95][0]
    reincarnation_table = None
    for table in page_95["tables"]:
        rows = table.get("rows", [])
        if rows and rows[0].get("cells", [])[0].get("text") == "D100 Roll":
            reincarnation_table = table
            break
    
    assert reincarnation_table is not None
    rows = reincarnation_table["rows"]
    
    # Check that no row contains "Transmute"
    for row in rows:
        for cell in row["cells"]:
            assert "Transmute" not in cell["text"], (
                "Table should not include 'Transmute Water to Dust' spell"
            )


if __name__ == "__main__":
    # Run all tests
    print("Running Reincarnation table extraction tests...")
    
    try:
        print("\n1. Testing table exists...")
        test_reincarnation_table_exists()
        print("   ✅ PASSED: Table exists")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n2. Testing table structure...")
        test_reincarnation_table_structure()
        print("   ✅ PASSED: Table structure correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n3. Testing table data...")
        test_reincarnation_table_data()
        print("   ✅ PASSED: Table data correct")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n4. Testing fragments skipped...")
        test_reincarnation_fragments_skipped()
        print("   ✅ PASSED: Fragments skipped")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    try:
        print("\n5. Testing table doesn't include Transmute Water...")
        test_reincarnation_table_does_not_include_transmute_water()
        print("   ✅ PASSED: Table ends correctly")
    except AssertionError as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

