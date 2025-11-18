"""
Validate the Alignment subsection in Character Trees has 4 paragraphs with expected breaks.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent


def _strip_tags(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def test_alignment_subsection_has_four_paragraphs() -> bool:
    html_path = project_root / "data" / "html_output" / "chapter-three-player-character-classes.html"
    if not html_path.exists():
        print(f"❌ FAILED: HTML not found at {html_path}")
        return False
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Locate the Alignment subheader (styled as subheader)
    header_pat = re.compile(
        r"<p[^>]*>\s*(?:[IVXLCDM]+\.\s+)?<a[^>]*>\[\^\]</a>\s*<span[^>]*font-size:\s*0\.9em[^>]*>Alignment</span>\s*</p>",
        re.IGNORECASE,
    )
    m_header = header_pat.search(content)
    if not m_header:
        print("❌ FAILED: Alignment subheader not found.")
        return False

    # Next subheader after Alignment
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
        print(f"❌ FAILED: Expected 4 paragraphs under Alignment, found {len(paras_text)}")
        return False

    expected_starts = [
        # Paragraph 2..4 starts
        "For example, one character tree might",
        "If a character is forced to change alignment",
        "Discarded characters should be given",
    ]
    for idx, expected in enumerate(expected_starts, start=1):
        got = paras_text[idx]
        if not got.startswith(expected):
            print(f"❌ FAILED: Paragraph {idx+1} should start with '{expected}', got '{got[:90]}'")
            return False

    print("✅ SUCCESS: Alignment subsection renders exactly 4 paragraphs with expected break points.")
    return True


def main() -> int:
    print("Testing Alignment subsection paragraph segmentation...")
    print("=" * 60)
    results = [test_alignment_subsection_has_four_paragraphs()]
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())

