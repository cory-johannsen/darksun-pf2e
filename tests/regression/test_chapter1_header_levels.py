#!/usr/bin/env python3
"""
Regression test for Chapter 1 header levels.

Verifies that Optional Methods headers are H2 (no Roman numerals, smaller font size)
while main section headers remain H1 (with Roman numerals).
"""

import re
import sys
from pathlib import Path


def test_chapter1_header_levels():
	"""Test that Chapter 1 headers have correct levels."""
	html_file = Path("data/html_output/chapter-one-ability-scores.html")
	
	if not html_file.exists():
		print(f"❌ FAILED: {html_file} does not exist")
		return False
	
	content = html_file.read_text(encoding="utf-8")
	
	# Test H2 headers (Optional Methods, Intelligence, Wisdom)
	h2_headers = [
		"header-3-optional-methods",
		"header-4-optional-method-i",
		"header-5-optional-method-ii",
		"header-6-optional-method-iii",
		"header-7-optional-method-iv",
		"header-8-optional-method-v",
		"header-10-intelligence",
		"header-11-wisdom",
	]
	
	print("\nTesting H2 headers (Optional Methods)...")
	for header_id in h2_headers:
		# Check for semantic <h2> tag (not styled <p> tag)
		if f'<h2 id="{header_id}">' not in content:
			print(f"❌ FAILED: {header_id} not using semantic <h2> tag")
			return False
		print(f"  ✓ {header_id} is using semantic <h2> tag")
		
		# Check that back-to-top link is present
		pattern = f'<h2 id="{header_id}">[^<]*<a href="#top"[^>]*>\\[\\^\\]</a></h2>'
		if not re.search(pattern, content, re.DOTALL):
			print(f"❌ FAILED: {header_id} missing back-to-top link")
			return False
		print(f"  ✓ {header_id} has back-to-top link")
		
		# Check that Roman numerals are NOT present (h2 headers shouldn't have them)
		pattern = f'<h2 id="{header_id}">[IVXLCDM]+\\.'
		if re.search(pattern, content):
			print(f"❌ FAILED: {header_id} has Roman numeral (should not)")
			return False
		print(f"  ✓ {header_id} has no Roman numeral")
	
	# Test H1 headers (main sections)
	h1_headers = [
		("header-0-rolling-ability-scores", "I."),
		("header-1-rolling-player-character-ability-scores", "II."),
		("header-2-rolling-non-player-character-ability-scores", "III."),
		("header-9-the-ability-scores", "IV."),
	]
	
	print("\nTesting H1 headers (main sections)...")
	for header_id, expected_numeral in h1_headers:
		# Check that it's NOT an <h2> tag (should be styled <p> for H1)
		if f'<h2 id="{header_id}">' in content:
			print(f"❌ FAILED: {header_id} is using <h2> tag (should be styled <p> for H1)")
			return False
		print(f"  ✓ {header_id} is not using semantic <h2> tag")
		
		# Check that Roman numeral IS present
		pattern = f'id="{header_id}">{re.escape(expected_numeral)}'
		if not re.search(pattern, content):
			print(f"❌ FAILED: {header_id} missing Roman numeral {expected_numeral}")
			return False
		print(f"  ✓ {header_id} has Roman numeral {expected_numeral}")
	
	# Test TOC indentation
	print("\nTesting TOC indentation...")
	for header_id in h2_headers:
		# H2 headers should have toc-subheader class in TOC
		pattern = f'<li class="toc-subheader"><a href="#{header_id}">'
		if pattern not in content:
			print(f"❌ FAILED: {header_id} missing toc-subheader class in TOC")
			return False
		print(f"  ✓ {header_id} has toc-subheader class in TOC")
	
	for header_id, _ in h1_headers:
		# H1 headers should NOT have toc-subheader class
		pattern = f'<li class="toc-subheader"><a href="#{header_id}">'
		if pattern in content:
			print(f"❌ FAILED: {header_id} has toc-subheader class in TOC (should not)")
			return False
		print(f"  ✓ {header_id} does not have toc-subheader class in TOC")
	
	return True


if __name__ == "__main__":
	print("=" * 60)
	print("Chapter 1 Header Level Regression Test")
	print("=" * 60)
	
	success = test_chapter1_header_levels()
	
	print("\n" + "=" * 60)
	if success:
		print("✅ ALL TESTS PASSED")
		print("=" * 60)
		sys.exit(0)
	else:
		print("❌ TESTS FAILED")
		print("=" * 60)
		sys.exit(1)

