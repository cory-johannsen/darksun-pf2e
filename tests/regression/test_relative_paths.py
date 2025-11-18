#!/usr/bin/env python3
"""Regression test to verify all HTML files use relative paths only.

Per RULES.md [HTML_PATHS]: All paths in HTML files must be relative,
not absolute filesystem paths or file:// URLs.
"""

import re
import sys
import pytest
from pathlib import Path


def check_no_absolute_paths(html_file_path: str) -> tuple[bool, list[str]]:
    """Verify that HTML file contains no absolute filesystem paths.
    
    Args:
        html_file_path: Path to the HTML file to check
        
    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    
    html_path = Path(html_file_path)
    if not html_path.exists():
        errors.append(f"HTML file not found: {html_file_path}")
        return False, errors
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Patterns that indicate absolute paths (not relative)
    absolute_path_patterns = [
        (r'file://', 'file:// URL scheme'),
        (r'href="/(?![#])', 'absolute path starting with /'),
        (r'src="/(?![#])', 'absolute src path starting with /'),
        (r'/Users/', 'macOS absolute path'),
        (r'/home/', 'Linux absolute path'),
        (r'C:\\', 'Windows absolute path'),
        (r'[A-Z]:\\', 'Windows drive letter path'),
    ]
    
    for pattern, description in absolute_path_patterns:
        matches = re.findall(pattern, html_content)
        if matches:
            # Get context for first match
            match_pos = html_content.find(matches[0])
            context_start = max(0, match_pos - 50)
            context_end = min(len(html_content), match_pos + 100)
            context = html_content[context_start:context_end]
            
            errors.append(
                f"Found {description}: {matches[0]}\n"
                f"  Context: ...{context}..."
            )
    
    return len(errors) == 0, errors


def check_all_links_are_relative(html_file_path: str) -> tuple[bool, list[str]]:
    """Verify that all href and src attributes use relative paths.
    
    Args:
        html_file_path: Path to the HTML file to check
        
    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    
    html_path = Path(html_file_path)
    if not html_path.exists():
        errors.append(f"HTML file not found: {html_file_path}")
        return False, errors
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Find all href and src attributes
    href_pattern = r'href="([^"]+)"'
    src_pattern = r'src="([^"]+)"'
    
    hrefs = re.findall(href_pattern, html_content)
    srcs = re.findall(src_pattern, html_content)
    
    # Check each href
    for href in hrefs:
        # Skip anchor-only links (starting with #)
        if href.startswith('#'):
            continue
        
        # Skip external URLs (http://, https://, mailto:, etc.)
        if '://' in href or href.startswith('mailto:'):
            continue
        
        # Check if it's an absolute path
        if href.startswith('/'):
            errors.append(f"Absolute href path found: {href}")
        
        # Check for absolute filesystem indicators
        if any(indicator in href for indicator in ['/Users/', '/home/', 'C:\\', 'file://']):
            errors.append(f"Hardcoded filesystem path in href: {href}")
    
    # Check each src
    for src in srcs:
        # Skip external URLs
        if '://' in src and not src.startswith('file://'):
            continue
        
        # Check if it's an absolute path
        if src.startswith('/'):
            errors.append(f"Absolute src path found: {src}")
        
        # Check for absolute filesystem indicators
        if any(indicator in src for indicator in ['/Users/', '/home/', 'C:\\', 'file://']):
            errors.append(f"Hardcoded filesystem path in src: {src}")
    
    return len(errors) == 0, errors


def run_tests(html_file_path: str) -> int:
    """Run all path verification tests.
    
    Args:
        html_file_path: Path to the HTML file to test
        
    Returns:
        0 if all tests pass, 1 otherwise
    """
    print("\n" + "="*70)
    print("HTML RELATIVE PATH VERIFICATION TEST")
    print("="*70)
    print(f"\nTesting: {html_file_path}\n")
    
    all_passed = True
    
    # Test 1: No absolute paths
    success, errors = check_no_absolute_paths(html_file_path)
    if success:
        print("No Absolute Paths: ✓ PASSED")
    else:
        print("No Absolute Paths: ✗ FAILED")
        for error in errors:
            print(f"  - {error}")
        all_passed = False
    
    # Test 2: All links are relative
    success, errors = check_all_links_are_relative(html_file_path)
    if success:
        print("All Links Relative: ✓ PASSED")
    else:
        print("All Links Relative: ✗ FAILED")
        for error in errors:
            print(f"  - {error}")
        all_passed = False
    
    print("="*70)
    if all_passed:
        print("SUMMARY: All tests passed")
    else:
        print("SUMMARY: Some tests failed")
    print("="*70)
    print()
    
    return 0 if all_passed else 1


# Pytest test functions
@pytest.fixture(params=None)
def html_files():
    """Fixture to provide all HTML files for testing."""
    html_dir = Path(__file__).parent.parent.parent / "data" / "html_output"
    if not html_dir.exists():
        pytest.skip(f"HTML output directory not found: {html_dir}")
    
    html_files = list(html_dir.glob("*.html"))
    if not html_files:
        pytest.skip(f"No HTML files found in {html_dir}")
    
    return html_files


def test_no_absolute_paths_pytest(html_files):
    """Test that no HTML files contain absolute paths."""
    errors = []
    for html_file in html_files:
        success, file_errors = check_no_absolute_paths(str(html_file))
        if not success:
            errors.append(f"{html_file.name}: {file_errors}")
    
    assert len(errors) == 0, f"Found absolute paths in {len(errors)} files:\n" + "\n".join(str(e) for e in errors[:5])


def test_all_links_are_relative_pytest(html_files):
    """Test that all links in HTML files are relative."""
    errors = []
    for html_file in html_files:
        success, file_errors = check_all_links_are_relative(str(html_file))
        if not success:
            errors.append(f"{html_file.name}: {file_errors}")
    
    assert len(errors) == 0, f"Found absolute links in {len(errors)} files:\n" + "\n".join(str(e) for e in errors[:5])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_relative_paths.py <html_file_path>")
        print("   or: python test_relative_paths.py --all")
        sys.exit(1)
    
    if sys.argv[1] == "--all":
        # Test all HTML files in data/html_output/
        html_dir = Path("data/html_output")
        if not html_dir.exists():
            print(f"Error: HTML output directory not found: {html_dir}")
            sys.exit(1)
        
        html_files = list(html_dir.glob("*.html"))
        if not html_files:
            print(f"Error: No HTML files found in {html_dir}")
            sys.exit(1)
        
        print(f"\nTesting {len(html_files)} HTML files...\n")
        
        failed_files = []
        for html_file in sorted(html_files):
            result = run_tests(str(html_file))
            if result != 0:
                failed_files.append(html_file.name)
        
        if failed_files:
            print(f"\n✗ {len(failed_files)} file(s) failed:")
            for filename in failed_files:
                print(f"  - {filename}")
            sys.exit(1)
        else:
            print(f"\n✓ All {len(html_files)} files passed!")
            sys.exit(0)
    else:
        sys.exit(run_tests(sys.argv[1]))

