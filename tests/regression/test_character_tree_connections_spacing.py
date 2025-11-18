"""
Validate that spaced-letter artifacts are normalized and words are properly separated
in the Character Trees narrative (connections/relationship sentences).
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent


def test_connections_sentence_spacing() -> bool:
    html_path = project_root / "data" / "html_output" / "chapter-three-player-character-classes.html"
    if not html_path.exists():
        print(f"❌ FAILED: HTML not found at {html_path}")
        return False
    content = html_path.read_text(encoding="utf-8", errors="ignore")

    # Basic sanity: the connections sentence should be present without spaced letters
    assert "invent connections" in content, "Connections sentence missing from HTML output."

    # Ensure no spaced-letter artifacts and no run-together phrase reported by user
    bad_patterns = [
        r"t\s+w\s+e\s+e\s+n",      # 't w e e n'
        r"b e t\s+w e e n",        # 'bet ween'
        r"theplayermaydecide",     # run-together words
        r"t h e  p l a y e r",     # spaced letters in 'the player'
    ]
    for pat in bad_patterns:
        if re.search(pat, content, flags=re.IGNORECASE):
            print(f"❌ FAILED: Found spacing artifact matching pattern: {pat}")
            return False

    # Positive check: the critical segment reads naturally
    expected_fragment = "between them - the player may decide that the individuals"
    if expected_fragment.lower() not in content.lower():
        print(f"❌ FAILED: Expected fragment not found:\n{expected_fragment}")
        return False

    print("✅ SUCCESS: Connections sentence spacing is normalized and readable.")
    return True


def main() -> int:
    print("Testing Character Tree connections sentence spacing...")
    print("=" * 60)
    ok = test_connections_sentence_spacing()
    print("=" * 60)
    if ok:
        print("✅ ALL TESTS PASSED")
        return 0
    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())

