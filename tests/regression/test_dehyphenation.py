"""Test that hyphenated words across line breaks are properly merged.

[MERGED_LINES] Ensure sentences that are merged to remove line breaks are properly 
joined. For example, "in- ner" should be "inner", "specializa- tion" should be 
"specialization".
"""

import os
import re
import sys
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_no_hyphenated_words(html_file: Path) -> bool:
    """Test that HTML file doesn't contain improperly hyphenated words.
    
    Pattern: hyphen followed by space and lowercase letter, which indicates
    a word that was split across lines and not properly merged.
    """
    if not html_file.exists():
        print(f"⚠️  SKIPPED: {html_file.name} not found")
        return True  # Don't fail if file doesn't exist yet
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find hyphenated words: "word- word" where second word starts with lowercase
    # Exclude HTML attributes (href, style, class, id, etc.)
    pattern = r'(?<!href=")(?<!style=")(?<!class=")(?<!id=")(?<!src=")(\w+)- ([a-z])'
    matches = re.findall(pattern, content)
    
    if matches:
        # Show first few examples
        examples = [f"{m[0]}- {m[1]}" for m in matches[:5]]
        print(f"❌ FAILED: {html_file.name} contains {len(matches)} hyphenated words")
        print(f"   Examples: {', '.join(examples)}")
        if len(matches) > 5:
            print(f"   ... and {len(matches) - 5} more")
        return False
    
    print(f"✅ SUCCESS: {html_file.name} has no improperly hyphenated words")
    return True


def main():
    """Run dehyphenation tests on all HTML files."""
    print("Testing line merge hyphenation...")
    print("=" * 60)
    
    html_dir = project_root / "data" / "html_output"
    
    if not html_dir.exists():
        print(f"❌ FAILED: HTML output directory not found: {html_dir}")
        return 1
    
    # Test all chapter HTML files
    html_files = list(html_dir.glob("chapter-*.html"))
    
    if not html_files:
        print(f"⚠️  WARNING: No chapter HTML files found in {html_dir}")
        return 0
    
    results = []
    for html_file in sorted(html_files):
        results.append(check_no_hyphenated_words(html_file))
    
    print("=" * 60)
    if all(results):
        print(f"✅ ALL TESTS PASSED ({len(results)} files checked)")
        return 0
    else:
        failed_count = sum(1 for r in results if not r)
        print(f"❌ {failed_count} of {len(results)} FILES FAILED")
        return 1


# Pytest test functions
@pytest.fixture
def html_files():
    """Fixture to provide all chapter HTML files for testing."""
    html_dir = project_root / "data" / "html_output"
    
    if not html_dir.exists():
        pytest.skip(f"HTML output directory not found: {html_dir}")
    
    html_files = list(html_dir.glob("chapter-*.html"))
    
    if not html_files:
        pytest.skip(f"No chapter HTML files found in {html_dir}")
    
    return sorted(html_files)


def test_no_hyphenated_words(html_files):
    """Test that all HTML files don't contain improperly hyphenated words."""
    failed_files = []
    
    for html_file in html_files:
        if not check_no_hyphenated_words(html_file):
            failed_files.append(html_file.name)
    
    assert len(failed_files) == 0, f"{len(failed_files)} files contain hyphenated words: {', '.join(failed_files)}"


if __name__ == "__main__":
    sys.exit(main())

