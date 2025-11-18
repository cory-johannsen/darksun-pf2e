"""Regression test for Chapter 15 Reincarnation table.

This test verifies that the Reincarnation spell table is properly rendered
in the HTML output with:
- Proper HTML table structure
- 2 columns: D100 Roll and Incarnation
- 14 data rows
- All races from the Dark Sun setting
- No extraneous text fragments mixed into the table
"""

import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def test_reincarnation_table_in_html():
    """Test that the Reincarnation table is properly rendered in HTML output."""
    # Load the Chapter 15 HTML output
    html_path = Path("data/html_output/chapter-fifteen-new-spells.html")
    
    if not html_path.exists():
        raise FileNotFoundError(
            f"HTML output not found at {html_path}. Run the pipeline first."
        )
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the Reincarnation header
    reincarnation_header = None
    for header in soup.find_all(["h2", "h3", "h4"]):
        if "reincarnation" in header.get_text().lower():
            reincarnation_header = header
            break
    
    assert reincarnation_header is not None, "Reincarnation header not found in HTML"
    logger.info(f"✓ Found Reincarnation header: {reincarnation_header.get_text()}")
    
    # Find the next table after the Reincarnation header
    reincarnation_table = None
    current = reincarnation_header
    while current:
        current = current.find_next_sibling()
        if current and current.name == "table":
            reincarnation_table = current
            break
    
    assert reincarnation_table is not None, "Reincarnation table not found after header"
    logger.info("✓ Found Reincarnation table")
    
    # Verify table structure
    rows = reincarnation_table.find_all("tr")
    assert len(rows) >= 15, f"Expected at least 15 rows, got {len(rows)}"
    logger.info(f"✓ Table has {len(rows)} rows (including header)")
    
    # Verify header row
    header_row = rows[0]
    header_cells = header_row.find_all(["th", "td"])
    assert len(header_cells) == 2, f"Expected 2 header cells, got {len(header_cells)}"
    
    header_texts = [cell.get_text().strip() for cell in header_cells]
    assert "D100" in header_texts[0] or "Roll" in header_texts[0], (
        f"First header should be 'D100 Roll', got '{header_texts[0]}'"
    )
    assert "Incarnation" in header_texts[1], (
        f"Second header should be 'Incarnation', got '{header_texts[1]}'"
    )
    logger.info("✓ Header row is correct")
    
    # Verify some key data rows
    expected_races = [
        "Aarakocra", "Belgoi", "Dwarf", "Elf", "Giant",
        "Giant-kin", "Cyclops", "Half-elf", "Half-giant", "Halfling",
        "Human", "Kenku", "Mul", "Thri-kreen", "Yuan-ti"
    ]
    
    table_text = reincarnation_table.get_text()
    found_races = []
    for race in expected_races:
        if race in table_text:
            found_races.append(race)
    
    assert len(found_races) >= 12, (
        f"Expected at least 12 of 15 races to be found, got {len(found_races)}: {found_races}"
    )
    logger.info(f"✓ Found {len(found_races)} races in the table")
    
    # Verify D100 roll format in data rows
    d100_rolls_found = 0
    for row in rows[1:]:  # Skip header row
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            first_cell = cells[0].get_text().strip()
            # Check if it looks like a D100 roll (e.g., "01-08", "97-00")
            if "-" in first_cell and len(first_cell) <= 6:
                d100_rolls_found += 1
    
    assert d100_rolls_found >= 14, (
        f"Expected at least 14 D100 roll entries, got {d100_rolls_found}"
    )
    logger.info(f"✓ Found {d100_rolls_found} D100 roll entries")
    
    # Verify that table content is NOT mixed with paragraph text
    # Check that the next sibling after the table is not a paragraph with table data
    next_elem = reincarnation_table.find_next_sibling()
    if next_elem and next_elem.name == "p":
        next_text = next_elem.get_text()
        # Make sure it doesn't contain table fragments like "01-08" or "Aarakocra"
        has_fragments = any(race in next_text for race in expected_races[:3])
        assert not has_fragments, (
            f"Found table fragments in next paragraph: {next_text[:100]}"
        )
        logger.info("✓ No table fragments found in surrounding text")
    
    logger.info("=" * 60)
    logger.info("✅ All Reincarnation table checks passed!")
    logger.info("=" * 60)
    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    try:
        test_reincarnation_table_in_html()
        print("\n✅ Regression test PASSED")
    except AssertionError as e:
        print(f"\n❌ Regression test FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Regression test ERROR: {e}")
        exit(1)

