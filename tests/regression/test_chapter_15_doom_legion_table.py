"""Regression test for Chapter 15 Doom Legion table.

This test verifies that the Doom Legion spell table is properly rendered
in the HTML output with:
- Proper HTML table structure
- 2 columns: Battle Type and Dice Roll
- 3 data rows (Skirmish, Small Battle, Major Battle)
- Proper dice spec format (3d12, 6d12, 10d20)
- No extraneous text fragments mixed into the table
"""

import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def test_doom_legion_table_in_html():
    """Test that the Doom Legion table is properly rendered in HTML output."""
    # Load the Chapter 15 HTML output
    html_path = Path("data/html_output/chapter-fifteen-new-spells.html")
    
    if not html_path.exists():
        raise FileNotFoundError(
            f"HTML output not found at {html_path}. Run the pipeline first."
        )
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Search for the table by looking for text containing "rolls dice" or "Skirmish"
    # The table should appear after text about "rolls dice to find how many undead are raised"
    target_paragraph = None
    for p in soup.find_all("p"):
        if "rolls dice" in p.get_text().lower() and "undead" in p.get_text().lower():
            target_paragraph = p
            break
    
    assert target_paragraph is not None, "Could not find intro paragraph for Doom Legion table"
    logger.info(f"✓ Found Doom Legion intro paragraph")
    
    # Find the next table after this paragraph
    doom_legion_table = None
    current = target_paragraph
    while current:
        current = current.find_next_sibling()
        if current and current.name == "table":
            # Check if this table contains "Skirmish"
            if "Skirmish" in current.get_text():
                doom_legion_table = current
                break
    
    assert doom_legion_table is not None, "Doom Legion table not found after intro paragraph"
    logger.info("✓ Found Doom Legion table")
    
    # Verify table structure
    rows = doom_legion_table.find_all("tr")
    assert len(rows) == 4, f"Expected 4 rows (1 header + 3 data), got {len(rows)}"
    logger.info(f"✓ Table has {len(rows)} rows (including header)")
    
    # Verify header row
    header_row = rows[0]
    header_cells = header_row.find_all(["th", "td"])
    assert len(header_cells) == 2, f"Expected 2 header cells, got {len(header_cells)}"
    
    header_texts = [cell.get_text().strip() for cell in header_cells]
    assert any(word in header_texts[0] for word in ["Battle", "Type"]), (
        f"First header should contain 'Battle' or 'Type', got '{header_texts[0]}'"
    )
    assert any(word in header_texts[1] for word in ["Dice", "Roll"]), (
        f"Second header should contain 'Dice' or 'Roll', got '{header_texts[1]}'"
    )
    logger.info("✓ Header row is correct")
    
    # Verify data rows
    expected_data = [
        ("Skirmish", "3d12"),
        ("Small Battle", "6d12"),
        ("Major Battle", "10d20"),
    ]
    
    for i, (expected_type, expected_dice) in enumerate(expected_data, start=1):
        row = rows[i]
        cells = row.find_all(["th", "td"])
        assert len(cells) == 2, f"Row {i} should have 2 cells, got {len(cells)}"
        
        actual_type = cells[0].get_text().strip()
        actual_dice = cells[1].get_text().strip()
        
        assert expected_type in actual_type, (
            f"Row {i}: expected type to contain '{expected_type}', got '{actual_type}'"
        )
        assert expected_dice == actual_dice, (
            f"Row {i}: expected dice '{expected_dice}', got '{actual_dice}'"
        )
    
    logger.info("✓ All 3 data rows are correct")
    
    # Verify that table content is NOT mixed with paragraph text
    # Check that the next sibling after the table is not a paragraph with table data
    next_elem = doom_legion_table.find_next_sibling()
    if next_elem and next_elem.name == "p":
        next_text = next_elem.get_text()
        # Make sure it doesn't contain table fragments like "Skirmish" or "3d12"
        has_fragments = any(keyword in next_text for keyword in ["Skirmish", "3d12", "6d12", "10d20"])
        assert not has_fragments, (
            f"Found table fragments in next paragraph: {next_text[:100]}"
        )
        logger.info("✓ No table fragments found in surrounding text")
    
    # Verify the paragraph after the table should contain "Animated bodies"
    para_after_table = doom_legion_table.find_next("p")
    if para_after_table:
        para_text = para_after_table.get_text()
        assert "Animated bodies" in para_text or "animated" in para_text.lower(), (
            "Expected paragraph after table to contain 'Animated bodies'"
        )
        logger.info("✓ Found 'Animated bodies' paragraph after table")
    
    logger.info("=" * 60)
    logger.info("✅ All Doom Legion table checks passed!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    try:
        test_doom_legion_table_in_html()
        print("\n✅ Regression test PASSED")
    except AssertionError as e:
        print(f"\n❌ Regression test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Regression test ERROR: {e}")
        exit(1)

