"""Regression test for Chapter 15 Time at Rest table.

This test verifies that the Time at Rest table (part of Doom Legion spell)
is properly rendered in the HTML output with:
- Proper HTML table structure
- 2 columns: Time at Rest and Chance to Ignore
- 10 data rows
- Proper time format (1 day, 1 week, 1 month, etc.)
- Proper percentage format (90%, 80%, etc.)
- No extraneous text fragments mixed into the table
"""

import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def test_time_at_rest_table_in_html():
    """Test that the Time at Rest table is properly rendered in HTML output."""
    # Load the Chapter 15 HTML output
    html_path = Path("data/html_output/chapter-fifteen-new-spells.html")
    
    if not html_path.exists():
        raise FileNotFoundError(
            f"HTML output not found at {html_path}. Run the pipeline first."
        )
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # The Time at Rest table doesn't have a separate header - it appears after
    # the paragraph mentioning "laid at rest"
    # Search for a table with headers "Time at Rest" and "Chance to Ignore"
    time_at_rest_table = None
    for table in soup.find_all("table"):
        # Check the first row for headers
        first_row = table.find("tr")
        if first_row:
            headers = first_row.find_all(["th", "td"])
            if len(headers) >= 2:
                header_texts = [h.get_text().strip() for h in headers]
                if ("Time at Rest" in header_texts[0] and "Chance to Ignore" in header_texts[1]):
                    time_at_rest_table = table
                    break
    
    assert time_at_rest_table is not None, "Time at Rest table not found"
    logger.info("✓ Found Time at Rest table")
    
    # Verify table structure
    rows = time_at_rest_table.find_all("tr")
    assert len(rows) == 11, f"Expected 11 rows (1 header + 10 data), got {len(rows)}"
    logger.info(f"✓ Table has {len(rows)} rows (including header)")
    
    # Verify header row
    header_row = rows[0]
    header_cells = header_row.find_all(["th", "td"])
    assert len(header_cells) == 2, f"Expected 2 header cells, got {len(header_cells)}"
    
    header_texts = [cell.get_text().strip() for cell in header_cells]
    assert any(word in header_texts[0] for word in ["Time", "Rest"]), (
        f"First header should contain 'Time' or 'Rest', got '{header_texts[0]}'"
    )
    assert any(word in header_texts[1] for word in ["Chance", "Ignore"]), (
        f"Second header should contain 'Chance' or 'Ignore', got '{header_texts[1]}'"
    )
    logger.info("✓ Header row is correct")
    
    # Verify data rows
    expected_data = [
        ("1 day", "90%"),
        ("1 week", "80%"),
        ("1 month", "70%"),
        ("3 months", "60%"),
        ("1 year", "50%"),
        ("5 years", "40%"),
        ("10 years", "30%"),
        ("50 years", "20%"),
        ("100 years", "10%"),
        ("Over 100 years", "0%"),
    ]
    
    for i, (expected_time, expected_chance) in enumerate(expected_data, start=1):
        row = rows[i]
        cells = row.find_all(["th", "td"])
        assert len(cells) == 2, f"Row {i} should have 2 cells, got {len(cells)}"
        
        actual_time = cells[0].get_text().strip()
        actual_chance = cells[1].get_text().strip()
        
        assert expected_time == actual_time, (
            f"Row {i}: expected time '{expected_time}', got '{actual_time}'"
        )
        assert expected_chance == actual_chance, (
            f"Row {i}: expected chance '{expected_chance}', got '{actual_chance}'"
        )
    
    logger.info("✓ All 10 data rows are correct")
    
    # Verify that table content is NOT mixed with paragraph text
    # Check that the next sibling after the table is not a paragraph with table data
    next_elem = time_at_rest_table.find_next_sibling()
    if next_elem and next_elem.name == "p":
        next_text = next_elem.get_text()
        # Make sure it doesn't contain table fragments
        has_fragments = any(keyword in next_text for keyword in ["1 day", "90%", "1 week", "80%"])
        assert not has_fragments, (
            f"Found table fragments in next paragraph: {next_text[:100]}"
        )
        logger.info("✓ No table fragments found in surrounding text")
    
    # Verify the paragraph after the table should contain "An army"
    para_after_table = time_at_rest_table.find_next("p")
    if para_after_table:
        para_text = para_after_table.get_text()
        assert "army" in para_text.lower(), (
            "Expected paragraph after table to contain 'army'"
        )
        logger.info("✓ Found 'An army' paragraph after table")
    
    logger.info("=" * 60)
    logger.info("✅ All Time at Rest table checks passed!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    try:
        test_time_at_rest_table_in_html()
        print("\n✅ Regression test PASSED")
    except AssertionError as e:
        print(f"\n❌ Regression test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Regression test ERROR: {e}")
        exit(1)

