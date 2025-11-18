"""Chapter 3 HTML post-processing fixes (Player Character Classes).

Fixes minor punctuation omission in Character Trees narrative:
- Insert a dash in the sentence fragment:
  '... between them - the player may decide that the individuals ...'
"""

from __future__ import annotations

import logging
import re
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _fix_character_tree_connections_dash(html: str) -> str:
	"""Ensure the dash is present between 'between them' and 'the player may decide'."""
	try:
		# Target the 'The Status of Inactive Characters' section where this sentence appears
		section_pat = (
			r'(?P<header><p id="header-\d+-the-status-of-inactive-characters".*?</p>)(?P<body>.*?)(?P<next><p id="header-\d+-using-the-character-tree-to-advantage".*?</p>)'
		)
		m = re.search(section_pat, html, re.DOTALL | re.IGNORECASE)
		if not m:
			# Fallback: global single replacement if section ids changed
			html_fixed, n = re.subn(
				r"(between them)\s+(the player may decide)",
				r"\1 - \2",
				html,
				count=1,
				flags=re.IGNORECASE,
			)
			return html_fixed if n > 0 else html
		header = m.group("header")
		body = m.group("body")
		next_h = m.group("next")
		# Replace missing dash, tolerate extra spaces
		body_fixed, n = re.subn(
			r"(between them)\s+(the player may decide)",
			r"\1 - \2",
			body,
			count=1,
			flags=re.IGNORECASE,
		)
		if n == 0:
			return html
		replacement = header + body_fixed + next_h
		return html[:m.start()] + replacement + html[m.end():]
	except Exception as e:
		logger.error("Chapter 3: Failed Character Trees dash fix: %s", e)
		return html


def _remove_duplicate_tables(html: str) -> str:
	"""Remove consecutive duplicate table elements.
	
	The raw PDF extraction sometimes creates many duplicate table structures
	that appear consecutively in the HTML. This function identifies and removes
	consecutive duplicates, keeping only the first occurrence.
	"""
	try:
		# Find all <table>...</table> elements
		table_pattern = r'<table[^>]*>.*?</table>'
		tables = list(re.finditer(table_pattern, html, re.DOTALL))
		
		if len(tables) < 2:
			return html
		
		logger.debug(f"Found {len(tables)} tables total in Chapter 3")
		
		# Track which tables to remove (by their match object)
		tables_to_remove = []
		prev_table_content = None
		duplicate_count = 0
		
		for i, table_match in enumerate(tables):
			table_content = table_match.group(0)
			
			# Check if this table is identical to the previous one
			if prev_table_content and table_content == prev_table_content:
				tables_to_remove.append(table_match)
				duplicate_count += 1
			else:
				prev_table_content = table_content
		
		if not tables_to_remove:
			logger.debug("No duplicate tables found in Chapter 3")
			return html
		
		logger.info(f"Removing {duplicate_count} duplicate tables from Chapter 3")
		
		# Remove duplicates in reverse order to preserve positions
		for table_match in reversed(tables_to_remove):
			html = html[:table_match.start()] + html[table_match.end():]
		
		return html
		
	except Exception as e:
		logger.error(f"Chapter 3: Failed to remove duplicate tables: {e}")
		return html


def _reposition_rangers_followers_table(html: str) -> str:
	"""Move the Rangers Followers table to appear after 'consult the following table'.
	
	The table currently appears after 'the ranger answers that challenge' but should
	appear after the sentence ending with 'consult the following table (rolling once for each follower).'
	"""
	try:
		# Pattern to find the Rangers Followers table
		# The table starts with <table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>
		table_pattern = r'(<table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>.*?</table>)'
		
		# Find the table
		table_match = re.search(table_pattern, html, re.DOTALL)
		if not table_match:
			logger.warning("Rangers Followers table not found in HTML")
			return html
		
		table_html = table_match.group(1)
		
		# Find the target position: after "consult the following table (rolling once for each follower)."
		target_pattern = r'(consult the following table \(rolling once for each follower\)\.)'
		target_match = re.search(target_pattern, html)
		
		if not target_match:
			logger.warning("Target position 'consult the following table' not found in HTML")
			return html
		
		# Check if the table is already in the correct position
		table_pos = table_match.start()
		target_pos = target_match.end()
		
		if table_pos > target_pos:
			logger.debug("Rangers Followers table is already after 'consult the following table'")
			return html
		
		logger.info(f"Repositioning Rangers Followers table from position {table_pos} to after position {target_pos}")
		
		# Remove the table from its current location
		html_without_table = html[:table_match.start()] + html[table_match.end():]
		
		# Find the target position again in the modified HTML (since positions have shifted)
		target_match = re.search(target_pattern, html_without_table)
		if not target_match:
			logger.warning("Target position lost after removing table")
			return html
		
		# Insert the table after the target sentence
		# We want to insert it right after the closing </p> tag of the paragraph containing the target
		# Find the closing </p> after the target text
		insert_pos = target_match.end()
		closing_p_match = re.search(r'</p>', html_without_table[insert_pos:insert_pos+100])
		if closing_p_match:
			insert_pos += closing_p_match.end()
		
		html_with_table = html_without_table[:insert_pos] + table_html + html_without_table[insert_pos:]
		
		logger.info("Rangers Followers table repositioned successfully")
		return html_with_table
		
	except Exception as e:
		logger.error(f"Chapter 3: Failed to reposition Rangers Followers table: {e}")
		return html


def _remove_rangers_followers_duplicate_data(html: str) -> str:
	"""Remove duplicate/malformed table data that appears after the Rangers Followers table.
	
	After the Rangers Followers table, there are leftover fragments of table data that should
	be removed. The valid content resumes with "In all other ways, govern the creation..."
	"""
	try:
		# Find the end of the Rangers Followers table
		table_end_pattern = r'Other wilderness creature \(chosen by the DM\)</td></tr></table>'
		table_end_match = re.search(table_end_pattern, html)
		
		if not table_end_match:
			logger.debug("Rangers Followers table end not found, skipping duplicate data cleanup")
			return html
		
		# Find the start of valid content after the table
		valid_content_pattern = r'In all other ways, govern the creation and play of rangers'
		valid_content_match = re.search(valid_content_pattern, html[table_end_match.end():])
		
		if not valid_content_match:
			logger.debug("Valid content marker not found after Rangers Followers table")
			return html
		
		# Calculate positions
		start_removal = table_end_match.end()
		end_removal = table_end_match.end() + valid_content_match.start()
		
		# Check if there's actually content to remove
		content_to_check = html[start_removal:end_removal].strip()
		if not content_to_check or content_to_check == '':
			logger.debug("No duplicate content found after Rangers Followers table")
			return html
		
		logger.info(f"Removing {len(content_to_check)} characters of duplicate data after Rangers Followers table")
		
		# Remove the duplicate content
		html = html[:start_removal] + html[end_removal:]
		
		return html
		
	except Exception as e:
		logger.error(f"Chapter 3: Failed to remove Rangers Followers duplicate data: {e}")
		return html


def apply_chapter_3_fixes(html: str) -> str:
	"""Apply all Chapter 3 HTML post-processing fixes."""
	logger.debug("Applying Chapter 3 postprocessing fixes")
	html = _fix_character_tree_connections_dash(html)
	html = _remove_duplicate_tables(html)
	html = _reposition_rangers_followers_table(html)
	html = _remove_rangers_followers_duplicate_data(html)
	
	# Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
	html = convert_all_styled_headers_to_semantic(html)
	
	return html


