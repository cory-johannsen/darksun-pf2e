import copy

from tools.pdf_pipeline.transformers.chapter_3_processing import apply_chapter_3_adjustments


def _text_block(text: str, x1: float, y1: float, x2: float, y2: float) -> dict:
    return {
        "type": "text",
        "bbox": [x1, y1, x2, y2],
        "lines": [
            {
                "bbox": [x1, y1, x2, y2],
                "spans": [
                    {
                        "text": text,
                        "color": "#000000",
                        "size": 9.0,
                    }
                ],
            }
        ],
    }


def _header_block(text: str, x1: float, y1: float, x2: float, y2: float) -> dict:
    return {
        "type": "text",
        "bbox": [x1, y1, x2, y2],
        "lines": [
            {
                "bbox": [x1, y1, x2, y2],
                "spans": [
                    {
                        "text": text,
                        "color": "#ca5804",
                        "size": 10.8,
                    }
                ],
            }
        ],
    }


def test_apply_chapter_3_adjustments_preserves_intro_paragraph():
    # Minimal section_data stub with pages 19-20 (multi-class section)
    # Place header and intro paragraph within the multi-class Y ranges.
    section_data = {
        "slug": "chapter-three-player-character-classes",
        "pages": [
            {"page": 18, "blocks": [], "tables": []},
            {"page": 19, "blocks": [], "tables": []},
            {"page": 20, "blocks": [], "tables": []},
        ],
    }
    page19 = section_data["pages"][1]
    # H1 header on page 19, right column
    page19["blocks"].append(
        _header_block(
            "Multi-Class and Dual-Class Characters",
            303.84,
            149.25,
            489.23,
            179.25,
        )
    )
    # Intro paragraph block (right column, y ~ 260-300 range)
    intro_text = (
        "Any demihuman character who meets the ability requirements may elect to become a "
        "multi-class character, subject to the restrictions presented in the Player's Handbook. "
        "The following chart lists the possible character class combinations available based upon "
        "the race of the character."
    )
    page19["blocks"].append(_text_block(intro_text, 298.32, 260.12, 536.82, 300.58))
    # Add some combination fragments that should be cleared
    page19["blocks"].append(_text_block("Fighter/Cleric Fighter/Thief", 298.32, 320.0, 536.82, 330.0))

    # Deep copy for comparison
    original = copy.deepcopy(section_data)

    apply_chapter_3_adjustments(section_data)

    # Find intro block after adjustments and ensure it was not cleared
    preserved_texts = []
    for blk in section_data["pages"][1]["blocks"]:
        if blk.get("type") != "text":
            continue
        for line in blk.get("lines", []):
            for span in line.get("spans", []):
                preserved_texts.append(span.get("text", ""))
    joined = " ".join(preserved_texts)
    assert "Any demihuman character who meets the ability requirements may elect to become a" in joined
    assert "based upon the race of the character." in joined

    # Ensure combination fragments were cleared from free text
    assert "Fighter/Cleric Fighter/Thief" not in joined

