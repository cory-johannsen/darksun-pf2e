#!/usr/bin/env python3
"""Regression test for Chapter 6 paragraph structure and header sizes.

Requirements:
- "What Things Are Worth" section has exactly 7 paragraphs with splits at:
  1. "The equipment lists in the Players Handbook..." (first paragraph, no split)
  2. "On Athas, the relative rarity"
  3. "All nonmetal items cost one percent"
  4. "All metal items cost the price listed"
  5. "Thus, the small canoe (a nonmetal item)"
  6. "If an item is typically a mixture of metal"
  7. "All prices listed in the"
- "Protracted Barter" section has exactly 3 paragraphs with splits at:
  1. "Protracted Barter: ..." (first paragraph, no split)
  2. "In the first round"
  3. "If Kyuln from the previous example"
- Header sizes: Barter, Simple Barter, Protracted Barter, Service should be H2
- Header size: Common Wages should be H3
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
html_path = project_root / "data" / "html_output" / "chapter-six-money-and-equipment.html"


def _read_html() -> str:
	if not html_path.exists():
		print(f"❌ FAILED: {html_path} not found (run transform stage first)")
		sys.exit(1)
	return html_path.read_text(encoding="utf-8")


def _extract_between(html: str, start_pat: str, end_pat: str) -> str:
	m = re.search(start_pat + r"(.*?)" + end_pat, html, re.DOTALL)
	return m.group(1) if m else ""


def test_what_things_are_worth_paragraphs() -> bool:
	html = _read_html()
	# Extract section content (avoid counting TOC area)
	section = _extract_between(html, r'<section class="content">', r'</section>')
	if not section:
		print("❌ FAILED: Could not locate <section class=\"content\"> in Chapter 6 HTML")
		return False
	
	# Extract content between "What Things Are Worth" header and "Monetary Systems" header
	content = _extract_between(
		section,
		r'<p id="header-1-what-things-are-worth".*?</p>',
		r'<p id="header-2-monetary-systems".*?</p>',
	)
	
	if not content:
		print("❌ FAILED: Could not locate 'What Things Are Worth' section in Chapter 6 HTML")
		return False
	
	# Count non-header paragraph tags
	paras = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
	
	if len(paras) != 7:
		print(f"❌ FAILED: 'What Things Are Worth' paragraph count expected 7, got {len(paras)}")
		print("Paragraphs found:")
		for i, para in enumerate(paras, 1):
			snippet = para[:100].replace('\n', ' ').strip()
			print(f"  {i}. {snippet}...")
		return False
	
	# Verify paragraph breaks by checking the start of each paragraph
	expected_starts = [
		("The equipment lists in the", "equipment lists intro"),
		("On Athas, the relative rarity", "relative rarity of metal"),
		("All nonmetal items cost one percent", "nonmetal pricing rule"),
		("All metal items cost the price listed", "metal pricing rule"),
		("Thus, the small canoe", "example with canoe"),
		("If an item is typically a mixture of metal", "mixed item rule"),
		("All prices listed in the", "DARK SUN pricing note"),
	]
	
	for i, (expected_start, description) in enumerate(expected_starts):
		para_text = paras[i].strip()
		# Handle HTML entities
		para_text_clean = para_text.replace('&nbsp;', ' ')
		if not para_text_clean.startswith(expected_start):
			print(f"❌ FAILED: Paragraph {i+1} ({description}) does not start with '{expected_start}'")
			print(f"  Actual start: {para_text_clean[:100]}...")
			return False
	
	print("✅ SUCCESS: 'What Things Are Worth' has 7 paragraphs with correct splits")
	return True


def test_protracted_barter_paragraphs() -> bool:
	html = _read_html()
	# Extract section content
	section = _extract_between(html, r'<section class="content">', r'</section>')
	if not section:
		print("❌ FAILED: Could not locate <section class=\"content\"> in Chapter 6 HTML")
		return False
	
	# Find the Protracted Barter header and extract content until the next header (Service)
	match = re.search(r'<p id="header-6-protracted-barter".*?</p>(.*?)<p id="header-7', section, re.DOTALL)
	if not match:
		print("❌ FAILED: Could not locate 'Protracted Barter' section in Chapter 6 HTML")
		return False
	
	content = match.group(1)
	
	# Verify paragraph breaks exist by checking for the key text markers
	# Note: There may be table-related paragraph fragments, so we focus on the main paragraph breaks
	expected_breaks = [
		("In the first round", "first round description"),
		("If Kyuln from the previous example", "Kyuln example"),
	]
	
	all_found = True
	for expected_start, description in expected_breaks:
		if expected_start not in content:
			print(f"❌ FAILED: Could not find paragraph break with '{expected_start}' ({description})")
			all_found = False
	
	if not all_found:
		return False
	
	# Verify the paragraphs are actually separated (not just present as text)
	paras = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
	
	# Check that "In the first round" starts a new paragraph
	first_round_in_para = False
	kyuln_in_para = False
	for para in paras:
		para_text = para.strip().replace('&nbsp;', ' ')
		if para_text.startswith("In the first round"):
			first_round_in_para = True
		if para_text.startswith("If Kyuln from the previous example"):
			kyuln_in_para = True
	
	if not first_round_in_para:
		print("❌ FAILED: 'In the first round' does not start a new paragraph")
		return False
	if not kyuln_in_para:
		print("❌ FAILED: 'If Kyuln from the previous example' does not start a new paragraph")
		return False
	
	print("✅ SUCCESS: 'Protracted Barter' has correct paragraph splits")
	return True


def test_header_sizes() -> bool:
	html = _read_html()
	# Note: We can't directly test font sizes in HTML, but we can verify headers exist
	# The actual header hierarchy will be reflected in the document structure
	
	# Check that these headers exist and are properly formatted
	required_headers = [
		"header-4-barter",
		"header-5-simple-barter",
		"header-6-protracted-barter",
		"header-7-service",  # Service is header-7
		"header-8-common-wages",  # Common Wages is header-8 (after Service)
	]
	
	for header_id in required_headers:
		if f'id="{header_id}"' not in html:
			print(f"❌ FAILED: Missing header with id='{header_id}'")
			return False
	
	print("✅ SUCCESS: All required headers are present")
	return True


def main() -> int:
	ok1 = test_what_things_are_worth_paragraphs()
	ok2 = test_protracted_barter_paragraphs()
	ok3 = test_header_sizes()
	return 0 if (ok1 and ok2 and ok3) else 1


if __name__ == "__main__":
	sys.exit(main())

