import json
from pathlib import Path

from tools.pdf_pipeline.transformers.chapter_2_processing import _process_height_weight_table


def _load_ch2_section() -> dict:
    section_path = Path("data/raw_structured/sections/02-005-chapter-two-player-character-races.json")
    with section_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _find_page_with_header(section_data: dict, header_text: str) -> dict | None:
    for page in section_data.get("pages", []):
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                text = "".join(s.get("text", "") for s in spans)
                if header_text in text:
                    return page
    return None


def test_height_weight_table_structure():
    section = _load_ch2_section()
    page = _find_page_with_header(section, "Height and Weight")
    assert page is not None, "Could not locate 'Height and Weight' page in section JSON"

    # Ensure a clean state
    page["tables"] = []

    # Run processor
    _process_height_weight_table(page)

    # Verify a table with 2 header rows is added
    tables = page.get("tables", [])
    assert tables, "No tables produced by height/weight processor"

    # Find the table that has the expected header composition
    target = None
    for t in tables:
        rows = t.get("rows", [])
        header_rows = int(t.get("header_rows", 0) or 0)
        if header_rows >= 2 and rows:
            first = rows[0].get("cells", [])
            texts = [c.get("text", "") for c in first]
            if any("Height in Inches" in tx for tx in texts) and any("Weight in Pounds" in tx for tx in texts):
                target = t
                break

    assert target is not None, "Height/Weight table with two-row header not found"

    # Check header structure
    header_rows = int(target.get("header_rows", 0) or 0)
    assert header_rows == 2, "Expected 2 header rows for Height/Weight table"

    rows = target.get("rows", [])
    assert len(rows) == 10, f"Expected 10 total rows (2 header + 8 data), got {len(rows)}"

    # Validate first header row cell spans
    hdr1 = rows[0]["cells"]
    # Expect at least 3 cells: Race (rowspan=2) and two group headers with colspan=2
    assert any(c.get("rowspan", 1) == 2 and c.get("text") == "Race" for c in hdr1), "Race cell should rowspan=2"
    assert any(c.get("colspan", 1) == 2 and "Height in Inches" in c.get("text", "") for c in hdr1), "Missing Height in Inches colspan"
    assert any(c.get("colspan", 1) == 2 and "Weight in Pounds" in c.get("text", "") for c in hdr1), "Missing Weight in Pounds colspan"
