#!/usr/bin/env python3
"""
[HTML_SINGLE_PAGE_VERIFICATION] Test that HTML files do not contain page break sections.

Each chapter HTML file should be rendered as a single continuous page without
<section data-page="..."> tags wrapping content.
"""

import re
from pathlib import Path

# Define the directory where HTML files are generated
HTML_OUTPUT_DIR = Path("data/html_output")


def test_no_page_sections():
    """Verify that HTML files do not contain <section data-page="..."> tags."""
    html_files = list(HTML_OUTPUT_DIR.glob("*.html"))
    
    if not html_files:
        print("Warning: No HTML files found for testing")
        return
    
    errors = []
    
    for html_file in html_files:
        # Skip the master table of contents
        if html_file.name == "table_of_contents.html":
            continue
        
        content = html_file.read_text(encoding='utf-8')
        
        # Look for <section data-page="..."> tags
        section_pattern = r'<section\s+data-page="[^"]*">'
        matches = re.findall(section_pattern, content)
        
        if matches:
            errors.append(
                f"{html_file.name}: Found {len(matches)} page section tags. "
                f"[HTML_SINGLE_PAGE] Each chapter should be a single continuous page."
            )
    
    if errors:
        print("\n❌ FAILED: Page section tags found in HTML files:")
        for error in errors:
            print(f"  - {error}")
        raise AssertionError(
            f"Found page section tags in {len(errors)} file(s). "
            "HTML chapters should be single continuous pages without section wrapping."
        )
    else:
        print(f"\n✓ PASSED: All {len(html_files) - 1} HTML files are single continuous pages")


if __name__ == "__main__":
    test_no_page_sections()
    print("\n[HTML_SINGLE_PAGE_VERIFICATION] Complete")

