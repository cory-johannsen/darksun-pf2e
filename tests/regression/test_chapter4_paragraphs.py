#!/usr/bin/env python3
"""Regression test for Chapter 4 paragraph structure.

Requirements:
- Intro has exactly 2 paragraphs, with a split at "As stated in the".
- "Half-giants and Alignment" has exactly 3 paragraphs, with splits at:
  "A half-giant must choose" and "A half-giant's shifting alignment".
- "Severe Desperation" has exactly 3 paragraphs, with splits at:
  "The madness created" and "Once a character has a".
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
html_path = project_root / "data" / "html_output" / "chapter-four-alignment.html"


def _read_html() -> str:
	if not html_path.exists():
		print(f"❌ FAILED: {html_path} not found (run transform stage first)")
		sys.exit(1)
	return html_path.read_text(encoding="utf-8")


def _extract_between(html: str, start_pat: str, end_pat: str) -> str:
	m = re.search(start_pat + r"(.*?)" + end_pat, html, re.DOTALL)
	return m.group(1) if m else ""


def test_intro_paragraphs() -> bool:
	html = _read_html()
	# Extract section content (avoid counting TOC area)
	section = _extract_between(html, r'<section class="content">', r'</section>')
	if not section:
		print("❌ FAILED: Could not locate <section class=\"content\"> in Chapter 4 HTML")
		return False
	# Grab content from start of section up to first header (Half-giants and Alignment)
	intro = _extract_between(section, r'\A', r'<p id="header-0-half-giants-and-alignment"')
	# Count non-header paragraph tags in intro
	intro_paras = re.findall(r'<p>(.*?)</p>', intro, re.DOTALL)
	if len(intro_paras) != 2:
		print(f"❌ FAILED: Intro paragraph count expected 2, got {len(intro_paras)}")
		return False
	# Verify split phrase appears at start of the second paragraph
	second = intro_paras[1]
	if not second.strip().startswith("As stated in the"):
		print("❌ FAILED: Second intro paragraph does not start with 'As stated in the'")
		return False
	print("✅ SUCCESS: Intro has 2 paragraphs with correct split")
	return True


def test_half_giants_paragraphs() -> bool:
	html = _read_html()
	section = _extract_between(html, r'<section class="content">', r'</section>')
	content = _extract_between(
		section,
		r'<p id="header-0-half-giants-and-alignment".*?</p>',
		r'<p id="header-1-alignment-in-desperate-situations".*?</p>',
	)
	# Count non-header paragraphs
	paras = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
	if len(paras) != 3:
		print(f"❌ FAILED: 'Half-giants and Alignment' paragraph count expected 3, got {len(paras)}")
		return False
	# Verify markers
	if "A half-giant must choose" not in " ".join(paras):
		print("❌ FAILED: Missing 'A half-giant must choose' in paragraph content")
		return False
	if ("A half-giant's shifting alignment" not in " ".join(paras)
		and "A half-giant&#x27;s shifting alignment" not in " ".join(paras)):
		print("❌ FAILED: Missing 'A half-giant's shifting alignment' in paragraph content")
		return False
	print("✅ SUCCESS: 'Half-giants and Alignment' has 3 paragraphs with correct splits")
	return True


def test_severe_desperation_paragraphs() -> bool:
	html = _read_html()
	section = _extract_between(html, r'<section class="content">', r'</section>')
	# Severe Desperation is the last section, so extract from its header to the end
	match = re.search(r'<p id="header-12-severe-desperation".*?</p>(.*)', section, re.DOTALL)
	if not match:
		print("❌ FAILED: Could not locate 'Severe Desperation' header in Chapter 4 HTML")
		return False
	content = match.group(1)
	# Count non-header paragraphs
	paras = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
	if len(paras) != 3:
		print(f"❌ FAILED: 'Severe Desperation' paragraph count expected 3, got {len(paras)}")
		return False
	# Verify markers
	if "The madness created" not in " ".join(paras):
		print("❌ FAILED: Missing 'The madness created' in paragraph content")
		return False
	if "Once a character has a" not in " ".join(paras):
		print("❌ FAILED: Missing 'Once a character has a' in paragraph content")
		return False
	print("✅ SUCCESS: 'Severe Desperation' has 3 paragraphs with correct splits")
	return True


def main() -> int:
	ok1 = test_intro_paragraphs()
	ok2 = test_half_giants_paragraphs()
	ok3 = test_severe_desperation_paragraphs()
	return 0 if (ok1 and ok2 and ok3) else 1


if __name__ == "__main__":
	sys.exit(main())


