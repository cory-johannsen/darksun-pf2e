"""
Validate the Character Advancement subsection splits into 4 paragraphs with expected breaks.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def test_character_advancement_four_paragraphs() -> bool:
    html_path = project_root / "data" / "html_output" / "chapter-three-player-character-classes.html"
    if not html_path.exists():
        print(f"❌ FAILED: HTML not found at {html_path}")
        return False
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Locate the Character Advancement subheader (H2 with font-size: 0.9em)
    header_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>Character Advancement</span>\s*</p>",
        re.IGNORECASE,
    )
    m_header = header_pat.search(content)
    if not m_header:
        print("❌ FAILED: Character Advancement subheader not found.")
        return False

    # Find next subheader (H2) after Character Advancement
    next_h2_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>[^<]+</span>\s*</p>",
        re.IGNORECASE,
    )
    m_next = next_h2_pat.search(content, pos=m_header.end())
    end_idx = m_next.start() if m_next else len(content)
    segment = content[m_header.end() : end_idx]

    # Collect non-empty paragraph texts
    paras = re.findall(r"<p[^>]*>(.*?)</p>", segment, flags=re.DOTALL | re.IGNORECASE)
    paras_text = [_strip_tags(p) for p in paras]
    paras_text = [p for p in paras_text if p]

    if len(paras_text) != 4:
        print(f"❌ FAILED: Expected 4 paragraphs under Character Advancement, found {len(paras_text)}")
        return False

    expected_starts = [
        # Paragraphs 2..4 starts
        "Every time the active character",
        "For purposes of character tree",
        "For inactive multi-class characters",
    ]
    for idx, expected in enumerate(expected_starts, start=1):
        got = paras_text[idx]
        if not got.startswith(expected):
            print(f"❌ FAILED: Paragraph {idx+1} should start with '{expected}', got '{got[:90]}'")
            return False

    print("✅ SUCCESS: Character Advancement renders 4 paragraphs with expected break points.")
    return True


def main() -> int:
    print("Testing Character Advancement paragraph segmentation...")
    print("=" * 60)
    results = [test_character_advancement_four_paragraphs()]
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())

