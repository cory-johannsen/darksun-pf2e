"""
Regression test: Chapter 2 Starting Age section should not contain stray header labels
or aggregated race lines outside the table after transformation.
"""

import re
from pathlib import Path


def _load_html() -> str:
    html_path = Path(__file__).resolve().parents[2] / "data" / "html_output" / "chapter-two-player-character-races.html"
    return html_path.read_text(encoding="utf-8")


def _slice_between(content: str, start_pat: str, end_pat: str) -> str:
    start = re.search(start_pat, content, re.DOTALL | re.IGNORECASE)
    end = re.search(end_pat, content, re.DOTALL | re.IGNORECASE)
    if not start or not end:
        return ""
    return content[start.end(): end.start()]


def main() -> int:
    html = _load_html()
    # Must not contain colored span header paragraphs for table labels anywhere
    label_words = [
        "Base Age", "Race", "Variable", "(Base + Variable)", "Maximum Age Range",
    ]
    bad_label_pattern = re.compile(
        r'<p id="header-\d+[^"]*">.*?<span[^>]*color:\s*#ca5804[^>]*>('
        + "|".join(re.escape(w) for w in label_words)
        + r")</span>",
        re.IGNORECASE | re.DOTALL,
    )
    if bad_label_pattern.search(html):
        print("✗ FAILED: Found colored header paragraphs for table labels")
        return 1
    
    # Must contain the Starting Age table header structure
    if '<th>Base Age</th>' not in html or '<th>Variable</th>' not in html or 'Max Age Range (Base + Variable)' not in html:
        print("✗ FAILED: Starting Age table header not found")
        return 1
    
    # Must not contain aggregated race list lines (3+ race names in a single paragraph) in Age section
    age_region = _slice_between(html, r'<p id="header-\d+-age">.*?</p>', r'$')
    race_names = ["Dwarf", "Elf", "Half-elf", "Half-giant", "Halfling", "Human", "Mul", "Thri-kreen"]
    para_matches = re.findall(r'<p[^>]*>(.*?)</p>', age_region, flags=re.DOTALL | re.IGNORECASE)
    for para in para_matches:
        text = re.sub(r"<[^>]+>", "", para)  # strip tags
        count = sum(1 for rn in race_names if rn.lower() in text.lower())
        if count >= 3:
            print("✗ FAILED: Found aggregated race list paragraph")
            return 1

    print("✓ PASSED: Starting Age cleanup checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


