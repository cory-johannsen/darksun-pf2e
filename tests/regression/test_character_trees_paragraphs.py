"""
Validate Character Trees paragraph segmentation in Chapter 3 HTML.

Requirement: Section XXXII Character Trees has 4 paragraphs with breaks at:
- "Replacing a fallen player ..."
- "In DARK SUN campaigns ..."
- "In brief, a character tree consists ..."
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def test_character_trees_has_four_paragraphs_with_expected_breaks() -> bool:
    html_path = project_root / "data" / "html_output" / "chapter-three-player-character-classes.html"
    if not html_path.exists():
        print(f"❌ FAILED: HTML not found at {html_path}")
        return False
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Anchor to the Character Trees header
    header_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*>Character Trees</span>\s*</p>",
        re.IGNORECASE,
    )
    m_header = header_pat.search(content)
    if not m_header:
        print("❌ FAILED: Character Trees header not found.")
        return False

    # Find next subheader (H2) after Character Trees
    next_header_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>[^<]+</span>\s*</p>",
        re.IGNORECASE,
    )
    m_next = next_header_pat.search(content, pos=m_header.end())
    end_idx = m_next.start() if m_next else len(content)

    segment = content[m_header.end() : end_idx]

    # Collect non-empty paragraph texts
    paras = re.findall(r"<p[^>]*>(.*?)</p>", segment, flags=re.DOTALL | re.IGNORECASE)
    paras_text = [_strip_tags(p) for p in paras]
    paras_text = [p for p in paras_text if p]

    if len(paras_text) != 4:
        print(f"❌ FAILED: Expected 4 paragraphs in Character Trees intro, found {len(paras_text)}")
        return False

    expected_starts = [
        "Replacing a fallen player character of high level",
        "In DARK SUN campaigns, players are encour",
        "In brief, a character tree consists of one active",
    ]
    # Verify paragraphs 2-4 start as expected
    for idx, expected in enumerate(expected_starts, start=1):
        got = paras_text[idx]
        if not got.startswith(expected):
            print(f"❌ FAILED: Paragraph {idx+1} should start with '{expected}', got '{got[:80]}'")
            return False

    print("✅ SUCCESS: Character Trees renders 4 paragraphs with the expected break points.")
    return True


def main() -> int:
    print("Testing Character Trees paragraph segmentation...")
    print("=" * 60)
    results = [test_character_trees_has_four_paragraphs_with_expected_breaks()]
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())


