"""Chapter 4 HTML post-processing fixes (Alignment).

Implements paragraph splitting rules based on the source text:
- Intro: 2 paragraphs, break at 'As stated in the'
- 'Half-giants and Alignment': 3 paragraphs, breaks at
  'A half-giant must choose' and 'A half-giant's shifting alignment'
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _find_between(html: str, start_pat: str, end_pat: str) -> Optional[Tuple[int, int, str]]:
	"""Return (start_idx, end_idx, inner_html) for the first match between patterns."""
	start = re.search(start_pat, html, re.DOTALL)
	if not start:
		return None
	end = re.search(end_pat, html, re.DOTALL)
	if not end:
		return None
	# Ensure end occurs after start
	if end.start() <= start.end():
		# Find next end occurrence after start
		end = re.search(end_pat, html[start.end():], re.DOTALL)
		if not end:
			return None
		abs_end_start = start.end() + end.start()
		abs_end_end = start.end() + end.end()
		return (start.end(), abs_end_start, html[start.end():abs_end_start])
	return (start.end(), end.start(), html[start.end():end.start()])


def _split_paragraph_text(full_text: str, split_markers: List[str]) -> List[str]:
	"""Split paragraph text at the first occurrence of each split marker (in order).
	Returns list of paragraph chunks preserving the markers at the start of following paragraphs.
	"""
	# Normalize common HTML entities for robust matching
	norm_text = (
		full_text.replace("&#x27;", "'")
		.replace("&nbsp;", " ")
	)
	chunks: List[str] = []
	start = 0
	for marker in split_markers:
		# try several tolerant variants
		candidates = [
			marker,
			marker.replace("&#x27;", "'"),
			marker.replace("'", "&#x27;"),
			re.sub(r"half-?giant", "half-giant", marker, flags=re.IGNORECASE),
			re.sub(r"half-?giant", "halfgiant", marker, flags=re.IGNORECASE),
		]
		pos = -1
		for cand in candidates:
			pos = norm_text.find(cand, start)
			if pos != -1:
				break
		if pos == -1:
			# If not found, skip this marker; we'll not split further
			logger.debug("Chapter 4: split marker not found: %r", marker)
			continue
		# Emit the text up to this marker as a paragraph
		chunks.append(norm_text[start:pos].strip())
		# Next chunk starts at the marker
		start = pos
	# Append the remainder
	chunks.append(norm_text[start:].strip())
	# Filter empty chunks
	return [c for c in chunks if c]


def _split_intro_paragraphs(html: str) -> str:
	"""Ensure first (pre-header) content is 2 paragraphs split at 'As stated in the'."""
	try:
		# Work on the content after the TOC nav; if no nav, operate on full content
		nav_match = re.search(r'<nav id="table-of-contents">.*?</nav>', html, re.DOTALL)
		prefix_end = nav_match.end() if nav_match else 0
		after_nav = html[prefix_end:]
		# Identify the first non-header paragraph and the first header for Half-giants
		first_p_match = re.search(r'<p>(.*?)</p>', after_nav, re.DOTALL)
		header0_match = re.search(r'(<p id="header-0-half-giants-and-alignment".*?</p>)', after_nav, re.DOTALL)
		if not first_p_match or not header0_match:
			return html
		first_p_html = first_p_match.group(0)
		first_p_text = first_p_match.group(1)
		# Split at the marker
		chunks = _split_paragraph_text(first_p_text, ["As stated in the"])
		if len(chunks) != 2:
			# If not exactly two, do not modify
			logger.debug("Chapter 4: Intro split did not yield 2 paragraphs (got %d)", len(chunks))
			return html
		new_intro = f"<p>{chunks[0]}</p>\n<p>{chunks[1]}</p>"
		# Replace only within the after_nav segment to avoid touching TOC
		after_nav_new = after_nav.replace(first_p_html, new_intro, 1)
		return html[:prefix_end] + after_nav_new
	except Exception as e:
		logger.error("Chapter 4: Failed intro paragraph split: %s", e)
		return html


def _split_half_giants_section(html: str) -> str:
	"""Ensure 'Half-giants and Alignment' content is 3 paragraphs at specified breaks."""
	try:
		# Capture header, content, next header
		pattern = (
			r'(?P<header><p id="header-0-half-giants-and-alignment".*?</p>)(?P<content>.*?)(?P<next><p id="header-1-alignment-in-desperate-situations".*?</p>)'
		)
		match = re.search(pattern, html, re.DOTALL)
		if not match:
			return html
		header = match.group("header")
		content = match.group("content")
		next_header = match.group("next")
		# Extract all paragraph bodies within content
		paras: List[str] = []
		for m in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
			txt = m.group(1).strip()
			if txt:
				paras.append(txt)
		if not paras:
			return html
		full_text = " ".join(paras)
		# Split at markers
		chunks = _split_paragraph_text(
			full_text,
			[
				"A half-giant must choose",
				"A half-giant's shifting alignment",
			],
		)
		if len(chunks) != 3:
			# Attempt with HTML entity apostrophe
			chunks = _split_paragraph_text(
				full_text,
				[
					"A half-giant must choose",
					"A half-giant&#x27;s shifting alignment",
				],
			)
		if len(chunks) != 3:
			logger.debug("Chapter 4: Half-giants section split did not yield 3 paragraphs (got %d)", len(chunks))
			return html
		new_content = "\n" + "\n".join(f"<p>{c}</p>" for c in chunks) + "\n"
		replacement = header + new_content + next_header
		return html[:match.start()] + replacement + html[match.end():]
	except Exception as e:
		logger.error("Chapter 4: Failed Half-giants paragraph split: %s", e)
		return html


def _merge_alignment_desperate_header(html: str) -> str:
	"""Merge 'Alignment in Desperate Situations' and '(Optional Rule)' into a single header.
	
	These two text elements appear on the same line in the PDF but are extracted separately
	due to different font sizes. They should be combined into one header with renumbering
	of subsequent headers.
	"""
	try:
		# Pattern to match both headers
		pattern = (
			r'(<p id="header-1-alignment-in-desperate-situations">II\.\s+<a href="#top"[^>]*>\[.*?\]</a>\s*<span[^>]*>)Alignment in Desperate Situations(</span></p>)'
			r'(<p id="header-2-optional-rule">III\.\s+<a href="#top"[^>]*>\[.*?\]</a>\s*<span[^>]*>)\(Optional Rule\)(</span></p>)'
		)
		
		match = re.search(pattern, html, re.DOTALL)
		if not match:
			logger.debug("Chapter 4: Could not find separate 'Alignment in Desperate Situations' and '(Optional Rule)' headers to merge")
			return html
		
		# Create merged header with both texts
		merged_header = match.group(1) + 'Alignment in Desperate Situations (Optional Rule)' + match.group(2)
		
		# Replace both headers with the merged one
		html = html[:match.start()] + merged_header + html[match.end():]
		
		# Now renumber all subsequent headers (decrement by 1)
		# We need to find ALL headers after the merged one and renumber them
		# First, collect all header IDs and their current numbers
		header_pattern = r'<p id="(header-(\d+)-[^"]+)">([IVX]+)\.'
		headers_to_update = []
		
		for m in re.finditer(header_pattern, html):
			full_id = m.group(1)
			num = int(m.group(2))
			roman = m.group(3)
			# Only update headers numbered 2 and above (which come after the merged header-1)
			# After merging, header-2 needs to become roman numeral III, header-3 becomes IV, etc.
			if num >= 2:
				headers_to_update.append((full_id, num, roman))
		
		# Sort by number to process in order (though they should already be in order)
		headers_to_update.sort(key=lambda x: x[1], reverse=True)
		
		# Update each header ID and recalculate the roman numeral
		# When we merge two headers and decrement IDs, roman numerals need to be recalculated
		# to match the new sequential position: header-2 should be III, header-3 should be IV, etc.
		# Formula: roman_numeral = header_number + 1 (since header-0 = I, header-1 = II, etc.)
		for full_id, old_num, old_roman in headers_to_update:
			new_num = old_num - 1
			new_id = full_id.replace(f'header-{old_num}-', f'header-{new_num}-')
			# Calculate the new roman numeral based on position
			# header-0=I (1), header-1=II (2), header-2=III (3), etc.
			new_roman = _int_to_roman(new_num + 1)
			
			# Replace the header ID
			html = html.replace(f'<p id="{full_id}">', f'<p id="{new_id}">')
			
			# Replace the roman numeral for this specific header
			# Use a more specific pattern to avoid replacing unrelated roman numerals
			pattern = rf'<p id="{re.escape(new_id)}">{re.escape(old_roman)}\.'
			replacement = f'<p id="{new_id}">{new_roman}.'
			html = re.sub(pattern, replacement, html, count=1)
		
		# Update TOC links to match new header IDs
		# Remove the Optional Rule entry
		html = re.sub(
			r'<li><a href="#header-2-optional-rule">\(Optional Rule\)</a></li>',
			'',
			html
		)
		
		# Update remaining TOC links
		for full_id, old_num, _ in headers_to_update:
			new_num = old_num - 1
			old_href = full_id
			new_href = full_id.replace(f'header-{old_num}-', f'header-{new_num}-')
			html = html.replace(f'href="#{old_href}"', f'href="#{new_href}"')
		
		logger.info("Chapter 4: Merged 'Alignment in Desperate Situations' and '(Optional Rule)' headers and renumbered %d subsequent headers", len(headers_to_update))
		return html
	except Exception as e:
		logger.error("Chapter 4: Failed to merge alignment desperate headers: %s", e)
		return html


def _int_to_roman(num: int) -> str:
	"""Convert integer to roman numeral."""
	val_map = [
		(10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
	]
	result = []
	for value, numeral in val_map:
		count = num // value
		if count:
			result.append(numeral * count)
			num -= value * count
	return ''.join(result)


def _split_severe_desperation_section(html: str) -> str:
	"""Ensure 'Severe Desperation' content is 5 paragraphs at specified breaks."""
	try:
		# Capture header, content, and section end
		# The section ends at closing </section> since it's the last section in the chapter
		# Note: header number is now 11 after merging the alignment headers
		pattern = (
			r'(?P<header><p id="header-11-severe-desperation".*?</p>)(?P<content>.*?)(?P<end></section>)'
		)
		match = re.search(pattern, html, re.DOTALL)
		if not match:
			return html
		header = match.group("header")
		content = match.group("content")
		end_tag = match.group("end")
		# Extract all paragraph bodies within content
		paras: List[str] = []
		for m in re.finditer(r'<p>(.*?)</p>', content, re.DOTALL):
			txt = m.group(1).strip()
			if txt:
				paras.append(txt)
		if not paras:
			return html
		full_text = " ".join(paras)
		# Split at markers - these mark the START of new paragraphs
		chunks = _split_paragraph_text(
			full_text,
			[
				"The madness created",
				"Once a character has a",
			],
		)
		if len(chunks) != 3:
			logger.debug("Chapter 4: Severe Desperation section split did not yield 3 paragraphs (got %d)", len(chunks))
			return html
		new_content = "\n" + "\n".join(f"<p>{c}</p>" for c in chunks) + "\n"
		replacement = header + new_content + end_tag
		return html[:match.start()] + replacement + html[match.end():]
	except Exception as e:
		logger.error("Chapter 4: Failed Severe Desperation paragraph split: %s", e)
		return html


def apply_chapter_4_fixes(html: str) -> str:
	"""Apply all Chapter 4 HTML post-processing fixes."""
	logger.debug("Applying Chapter 4 postprocessing fixes")
	html = _split_intro_paragraphs(html)
	html = _split_half_giants_section(html)
	html = _merge_alignment_desperate_header(html)  # Must run before severe desperation (affects numbering)
	html = _split_severe_desperation_section(html)
	
	# Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
	html = convert_all_styled_headers_to_semantic(html)
	
	return html


