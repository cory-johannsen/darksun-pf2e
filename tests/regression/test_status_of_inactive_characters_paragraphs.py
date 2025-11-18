"""
Validate The Status of Inactive Characters renders 3 paragraphs with expected breaks.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def test_status_of_inactive_characters_three_paragraphs() -> bool:
    html_path = project_root / "data" / "html_output" / "chapter-three-player-character-classes.html"
    if not html_path.exists():
        print(f"❌ FAILED: HTML not found at {html_path}")
        return False
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Locate the subheader (H2) for The Status of Inactive Characters
    header_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>The Status of Inactive Characters</span>\s*</p>",
        re.IGNORECASE,
    )
    m_header = header_pat.search(content)
    if not m_header:
        print("❌ FAILED: The Status of Inactive Characters subheader not found.")
        return False

    # Next H2 after this subheader
    next_h2_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>[^<]+</span>\s*</p>",
        re.IGNORECASE,
    )
    m_next = next_h2_pat.search(content, pos=m_header.end())
    end_idx = m_next.start() if m_next else len(content)
    segment = content[m_header.end() : end_idx]

    # Collect non-empty paragraph texts between
    paras = re.findall(r"<p[^>]*>(.*?)</p>", segment, flags=re.DOTALL | re.IGNORECASE)
    paras_text = [_strip_tags(p) for p in paras]
    paras_text = [p for p in paras_text if p]

    if len(paras_text) != 3:
        print(f"❌ FAILED: Expected 3 paragraphs, found {len(paras_text)}")
        return False

    # Paragraphs 2..3 should start with the expected phrases
    expected_starts = [
        "When not in play,",
        "All characters in a character",
    ]
    for idx, expected in enumerate(expected_starts, start=1):
        got = paras_text[idx]
        if not got.startswith(expected):
            print(f"❌ FAILED: Paragraph {idx+1} should start with '{expected}', got '{got[:90]}'")
            return False

    print("✅ SUCCESS: The Status of Inactive Characters renders 3 paragraphs with expected break points.")
    return True


def main() -> int:
    print("Testing The Status of Inactive Characters paragraph segmentation...")
    print("=" * 60)
    results = [test_status_of_inactive_characters_three_paragraphs()]
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())

