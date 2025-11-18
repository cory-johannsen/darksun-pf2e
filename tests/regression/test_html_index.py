"""Test that index.html exists and correctly redirects to table_of_contents.html.

[HTML_INDEX] The output html should contain an index.html page that redirects 
to the table of contents.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_index_exists():
    """Verify index.html exists."""
    html_dir = project_root / "data" / "html_output"
    index_file = html_dir / "index.html"
    
    if not index_file.exists():
        print(f"❌ FAILED: index.html not found at {index_file}")
        return False
    
    print(f"✅ SUCCESS: index.html exists at {index_file}")
    return True


def test_index_redirects():
    """Verify index.html contains a redirect to table_of_contents.html."""
    html_dir = project_root / "data" / "html_output"
    index_file = html_dir / "index.html"
    
    if not index_file.exists():
        print(f"❌ FAILED: index.html not found")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for meta refresh tag
    if 'url=table_of_contents.html' not in content:
        print(f"❌ FAILED: index.html does not contain redirect to table_of_contents.html")
        return False
    
    # Check for manual link
    if 'href="table_of_contents.html"' not in content:
        print(f"❌ FAILED: index.html does not contain manual link to table_of_contents.html")
        return False
    
    print(f"✅ SUCCESS: index.html correctly redirects to table_of_contents.html")
    return True


def main():
    """Run all index.html tests."""
    print("Testing HTML index requirements...")
    print("=" * 60)
    
    results = [
        test_index_exists(),
        test_index_redirects(),
    ]
    
    print("=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

