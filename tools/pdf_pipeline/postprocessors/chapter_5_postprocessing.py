"""Chapter 5 HTML post-processing fixes (Proficiencies).

Implements paragraph splitting rules based on the source text:
- Intro: 2 paragraphs, break at 'Dark Sun characters often'
- New Nonweapon Proficiencies table reconstruction
"""

from __future__ import annotations

import logging
import re
from typing import List, Tuple
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _split_paragraph_text(full_text: str, split_markers: List[str]) -> List[str]:
	"""Split paragraph text at the first occurrence of each split marker (in order).
	Returns list of paragraph chunks preserving the markers at the start of following paragraphs.
	"""
	# Normalize common HTML entities for robust matching
	norm_text = (
		full_text.replace("&#x27;", "'")
		.replace("&nbsp;", " ")
		.replace("&amp;", "&")
	)
	chunks: List[str] = []
	start = 0
	for marker in split_markers:
		# try several tolerant variants
		candidates = [
			marker,
			marker.replace("&#x27;", "'"),
			marker.replace("'", "&#x27;"),
			marker.replace("&amp;", "&"),
			marker.replace("&", "&amp;"),
		]
		pos = -1
		for cand in candidates:
			pos = norm_text.find(cand, start)
			if pos != -1:
				break
		if pos == -1:
			# If not found, skip this marker; we'll not split further
			logger.debug("Chapter 5: split marker not found: %r", marker)
			continue
		# Emit the text up to this marker as a paragraph
		chunks.append(norm_text[start:pos].strip())
		# Next chunk starts at the marker
		start = pos
	# Append the remainder
	chunks.append(norm_text[start:].strip())
	# Filter empty chunks
	return [c for c in chunks if c]


def _extract_table_data_from_paragraphs(text: str) -> List[Tuple[str, str, str, str]]:
	"""Extract table data from malformed paragraph text.
	Returns list of (proficiency, slots, ability, modifier) tuples.
	
	Note: Slots are always "1" based on user specification, so we parse:
	proficiency name + ability (3-letter) + modifier (number with optional minus)
	
	Handles reversed pattern where ability+modifier come before proficiency name.
	"""
	# Normalize whitespace in ability scores (e.g., "W i s" -> "Wis")
	text = re.sub(r'([A-Z])\s+([a-z])\s+([a-z])', r'\1\2\3', text)
	text = re.sub(r'([A-Z])\s+([a-z])([a-z])', r'\1\2\3', text)
	text = re.sub(r'([A-Z][a-z])\s+([a-z])', r'\1\2', text)
	
	# Split into words
	words = text.split()
	
	# Known ability scores
	abilities = {'Wis', 'Int', 'Dex', 'Chr', 'Str', 'Con'}
	
	def is_likely_proficiency_start(idx: int) -> bool:
		"""Check if position looks like the start of a proficiency name (capitalized word)."""
		return idx < len(words) and words[idx] and words[idx][0].isupper() and words[idx] not in abilities
	
	rows = []
	i = 0
	while i < len(words):
		# Skip column header words
		if words[i] in ['Slots', 'Modifier', 'Ability', 'Proficiency']:
			i += 1
			continue
		
		# Check if we're starting with an ability score (reversed pattern)
		# Pattern: [ability] [modifier] [proficiency name]
		if i < len(words) and words[i] in abilities:
			ability = words[i]
			i += 1
			
			# Get modifier
			modifier = "0"
			if i < len(words):
				next_word = words[i]
				if next_word.startswith('-') or (next_word == '-' and i + 1 < len(words)):
					if next_word == '-':
						modifier = '-' + words[i + 1]
						i += 2
					else:
						modifier = next_word
						i += 1
				elif next_word.isdigit():
					modifier = next_word
					i += 1
			
			# Now collect proficiency name
			# Stop when we hit: (1) next ability, (2) pattern that looks like new normal entry
			proficiency = []
			while i < len(words):
				# If we hit an ability, check if it's part of a new entry
				# Pattern: [Proficiency Name] [Ability] suggests a new normal entry
				if words[i] in abilities:
					# Check if there are capitalized words before this ability (suggesting a new entry)
					if len(proficiency) > 1 and is_likely_proficiency_start(i - len(proficiency)):
						# This looks like the start of a new entry, backtrack
						# The last word(s) in proficiency might be a new proficiency name
						break
					# Otherwise, just stop here
					break
				
				proficiency.append(words[i])
				i += 1
				
				# Look ahead: if next 2+ words are capitalized followed by an ability,
				# it's likely a new entry starting
				if (i < len(words) - 2 and
					is_likely_proficiency_start(i) and
					is_likely_proficiency_start(i + 1) and
					i + 2 < len(words) and words[i + 2] in abilities):
					# Looks like "Sign Language Dex" pattern starting
					break
			
			if proficiency:
				prof_name = ' '.join(proficiency)
				rows.append((prof_name, "1", ability, modifier))
			continue
		
		# Normal pattern: [proficiency name] [ability] [modifier]
		proficiency = []
		while i < len(words) and words[i] not in abilities:
			proficiency.append(words[i])
			i += 1
		
		if not proficiency or i >= len(words):
			break
		
		prof_name = ' '.join(proficiency)
		
		# Get ability
		ability = words[i]
		i += 1
		
		# Get modifier (optional, default to 0)
		modifier = "0"
		if i < len(words):
			next_word = words[i]
			# Check if next word is a modifier (not an ability)
			if next_word not in abilities:
				if next_word.startswith('-'):
					modifier = next_word
					i += 1
				elif next_word == '-' and i + 1 < len(words) and words[i + 1].isdigit():
					modifier = '-' + words[i + 1]
					i += 2
				elif next_word.isdigit():
					modifier = next_word
					i += 1
		
		rows.append((prof_name, "1", ability, modifier))
	
	return rows


def _reconstruct_nonweapon_table(html: str) -> str:
	"""Reconstruct the New Nonweapon Proficiencies table from malformed HTML."""
	try:
		# Find the section from "New Nonweapon Proficiencies" header to "Description of New Proficiencies" header
		pattern = (
			r'<p id="header-1-new-nonweapon-proficiencies">.*?</p>'
			r'(?P<table_content>.*?)'
			r'<p id="header-10-description-of-new-proficiencies">'
		)
		match = re.search(pattern, html, re.DOTALL)
		if not match:
			logger.warning("Could not find New Nonweapon Proficiencies section")
			return html
		
		table_content = match.group('table_content')
		logger.info(f"Table content length: {len(table_content)} characters")
		logger.info(f"Table content preview: {table_content[:500]}")
		
		# Extract text from malformed headers and paragraphs
		# Remove all paragraph and header tags, extract just text
		text_parts = []
		
		# Find GENERAL section
		general_match = re.search(r'<p id="header-2-general">.*?GENERAL.*?</p>(.*?)(?=<p id="header-7-priest">)', table_content, re.DOTALL)
		if general_match:
			logger.info(f"Found GENERAL section: {len(general_match.group(1))} chars")
			logger.info(f"GENERAL content: {general_match.group(1)[:200]}")
		else:
			logger.warning("Could not find GENERAL section")
		
		# Find PRIEST section  
		priest_match = re.search(r'<p id="header-7-priest">.*?PRIEST.*?</p>(.*?)(?=<p id="header-8-warrior">)', table_content, re.DOTALL)
		if priest_match:
			logger.info(f"Found PRIEST section: {len(priest_match.group(1))} chars")
			logger.info(f"PRIEST content: {priest_match.group(1)[:200]}")
		else:
			logger.warning("Could not find PRIEST section")
		
		# Find WARRIOR section
		warrior_match = re.search(r'<p id="header-8-warrior">.*?WARRIOR.*?</p>(.*?)(?=<p id="header-9-wizard">)', table_content, re.DOTALL)
		if warrior_match:
			logger.info(f"Found WARRIOR section: {len(warrior_match.group(1))} chars")
			logger.info(f"WARRIOR content: {warrior_match.group(1)[:200]}")
		else:
			logger.warning("Could not find WARRIOR section")
		
		# Find WIZARD section
		wizard_match = re.search(r'<p id="header-9-wizard">.*?WIZARD.*?</p>(.*?)$', table_content, re.DOTALL)
		if wizard_match:
			logger.info(f"Found WIZARD section: {len(wizard_match.group(1))} chars")
			logger.info(f"WIZARD content: {wizard_match.group(1)[:200]}")
		else:
			logger.warning("Could not find WIZARD section")
		
		# Extract and clean text for each section
		def extract_text(content: str) -> str:
			"""Extract plain text from HTML, removing tags."""
			# Remove header tags but keep their text
			content = re.sub(r'<p id="[^"]*">[^<]*<a[^>]*>.*?</a>\s*<span[^>]*>([^<]*)</span></p>', r'\1 ', content)
			# Remove remaining tags
			content = re.sub(r'<[^>]+>', ' ', content)
			# Clean whitespace
			content = ' '.join(content.split())
			return content
		
		sections = {}
		if general_match:
			general_text = extract_text(general_match.group(1))
			logger.info(f"GENERAL text after extract_text: {general_text[:300]}")
			sections['GENERAL'] = _extract_table_data_from_paragraphs(general_text)
			logger.info(f"GENERAL parsed {len(sections['GENERAL'])} rows")
		
		if priest_match:
			priest_text = extract_text(priest_match.group(1))
			logger.info(f"PRIEST text after extract_text: {priest_text}")
			sections['PRIEST'] = _extract_table_data_from_paragraphs(priest_text)
			logger.info(f"PRIEST parsed {len(sections['PRIEST'])} rows")
		
		if warrior_match:
			warrior_text = extract_text(warrior_match.group(1))
			logger.info(f"WARRIOR text after extract_text: {warrior_text}")
			sections['WARRIOR'] = _extract_table_data_from_paragraphs(warrior_text)
			logger.info(f"WARRIOR parsed {len(sections['WARRIOR'])} rows")
		
		if wizard_match:
			wizard_text = extract_text(wizard_match.group(1))
			logger.info(f"WIZARD text after extract_text: {wizard_text}")
			sections['WIZARD'] = _extract_table_data_from_paragraphs(wizard_text)
			logger.info(f"WIZARD parsed {len(sections['WIZARD'])} rows")
		
		# Build the table HTML
		table_html = ['<table>']
		
		for section_name in ['GENERAL', 'PRIEST', 'WARRIOR', 'WIZARD']:
			if section_name not in sections or not sections[section_name]:
				continue
			
			# Section header row
			table_html.append(f'<tr><th colspan="4" style="background-color: var(--accent-light); text-align: center;">{section_name}</th></tr>')
			# Column headers
			table_html.append('<tr><th>Proficiency</th><th>Slots</th><th>Ability</th><th>Modifier</th></tr>')
			# Data rows
			for prof, slots, ability, modifier in sections[section_name]:
				table_html.append(f'<tr><td>{prof}</td><td>{slots}</td><td>{ability}</td><td>{modifier}</td></tr>')
		
		table_html.append('</table>')
		new_table = '\n'.join(table_html)
		
		# Replace the entire malformed section with the new table
		new_content = (
			'<p id="header-1-new-nonweapon-proficiencies">II.  '
			'<a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
			'<span style="color: #ca5804">New Nonweapon Proficiencies</span></p>\n'
			+ new_table + '\n'
		)
		
		# Since the pattern matches UP TO and INCLUDING the opening tag of "Description of New Proficiencies",
		# we need to back up to include it again (it's consumed by the match)
		result = html[:match.start()] + new_content + '<p id="header-10-description-of-new-proficiencies">' + html[match.end():]
		
		logger.info("Successfully reconstructed New Nonweapon Proficiencies table")
		return result
		
	except Exception as e:
		logger.error(f"Failed to reconstruct nonweapon proficiencies table: {e}", exc_info=True)
		return html


def _split_intro_paragraphs(html: str) -> str:
	"""Ensure first (pre-header) content is 2 paragraphs split at 'Dark Sun characters often'."""
	try:
		# Work on the content after the TOC nav; if no nav, operate on full content
		nav_match = re.search(r'<nav id="table-of-contents">.*?</nav>', html, re.DOTALL)
		prefix_end = nav_match.end() if nav_match else 0
		after_nav = html[prefix_end:]
		# Identify the first non-header paragraph
		first_p_match = re.search(r'<p>(.*?)</p>', after_nav, re.DOTALL)
		if not first_p_match:
			return html
		first_p_html = first_p_match.group(0)
		first_p_text = first_p_match.group(1)
		# Split at the marker
		chunks = _split_paragraph_text(first_p_text, ["Dark Sun characters often"])
		if len(chunks) != 2:
			# If not exactly two, do not modify
			logger.debug("Chapter 5: Intro split did not yield 2 paragraphs (got %d)", len(chunks))
			return html
		new_intro = f"<p>{chunks[0]}</p>\n<p>{chunks[1]}</p>"
		# Replace only within the after_nav segment to avoid touching TOC
		after_nav_new = after_nav.replace(first_p_html, new_intro, 1)
		return html[:prefix_end] + after_nav_new
	except Exception as e:
		logger.error("Chapter 5: Failed intro paragraph split: %s", e)
		return html


def _split_weapon_proficiencies_section(html: str) -> str:
	"""Ensure 'Dark Sun Weapon Proficiencies' content is 3 paragraphs at specified breaks."""
	try:
		# Capture header, content, next header
		pattern = (
			r'(?P<header><p id="header-0-dark-sun-weapon-proficiencies".*?</p>)(?P<content>.*?)(?P<next><p id="header-1-new-nonweapon-proficiencies".*?</p>)'
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
				"For example, Barlyuth",
				"A 9th-level gladiator could thus",
			],
		)
		if len(chunks) != 3:
			logger.debug("Chapter 5: Weapon Proficiencies section split did not yield 3 paragraphs (got %d)", len(chunks))
			return html
		new_content = "\n" + "\n".join(f"<p>{c}</p>" for c in chunks) + "\n"
		replacement = header + new_content + next_header
		return html[:match.start()] + replacement + html[match.end():]
	except Exception as e:
		logger.error("Chapter 5: Failed Weapon Proficiencies paragraph split: %s", e)
		return html


def _remove_malformed_tables_from_descriptions(html: str) -> str:
	"""Remove malformed ds-table elements from the Description of New Proficiencies section.
	
	These tables are remnants from the PDF extraction that were incorrectly placed
	after the "Description of New Proficiencies" header.
	"""
	try:
		# Find the "Description of New Proficiencies" header
		desc_pattern = r'<p id="header-10-description-of-new-proficiencies">.*?</p>'
		desc_match = re.search(desc_pattern, html, re.DOTALL)
		if not desc_match:
			logger.warning("Could not find Description of New Proficiencies header")
			return html
		
		# Find the next header (Bargain or whatever comes after)
		next_header_pattern = r'<p id="header-11-[^"]+">.*?</p>'
		next_header_match = re.search(next_header_pattern, html[desc_match.end():], re.DOTALL)
		if not next_header_match:
			logger.warning("Could not find next header after Description of New Proficiencies")
			return html
		
		# Extract the section between these two headers
		section_start = desc_match.end()
		section_end = desc_match.end() + next_header_match.start()
		section_content = html[section_start:section_end]
		
		# Remove all <table class="ds-table"> elements from this section
		cleaned_content = re.sub(r'<table class="ds-table">.*?</table>', '', section_content, flags=re.DOTALL)
		
		# Count how many tables we removed
		table_count = section_content.count('<table class="ds-table">')
		if table_count > 0:
			logger.info(f"Removed {table_count} malformed tables from Description section")
		
		# Reconstruct the HTML
		result = html[:section_start] + cleaned_content + html[section_end:]
		return result
		
	except Exception as e:
		logger.error(f"Failed to remove malformed tables: {e}", exc_info=True)
		return html


def _split_proficiency_description_paragraphs(html: str) -> str:
	"""Split merged proficiency description paragraphs at natural break points.
	
	The PDF extraction merges multiple paragraphs within individual proficiency
	descriptions. This function splits them at the specified markers.
	"""
	try:
		# Split markers for each proficiency description
		# These are applied globally across all proficiency descriptions
		split_markers = [
			"Simple and protracted barter",
			"In addition to these example uses, the",
			"Dehydration receives full explanation",
			"When employing this proficiency, a",
			"Psionic detection proficiency can only inform",
			"A player whose character has psionic detection",
			"To use sign language for an entire round,",
			"On Athas, many groups employ sign language",
			"A character using the somatic concealment",
		]
		
		# Process each paragraph that contains proficiency descriptions
		# Look for paragraphs between H3 headers (proficiency names) or between paragraphs
		pattern = r'<p>(.*?)</p>'
		
		def split_paragraph(match):
			paragraph = match.group(1)
			
			# Check if this paragraph contains any markers
			found_markers = [m for m in split_markers if m in paragraph]
			
			if found_markers:
				# Split at all markers found in this paragraph
				chunks = _split_paragraph_text(paragraph, found_markers)
				if len(chunks) > 1:
					# Create multiple paragraphs
					paragraphs = '\n'.join(f'<p>{chunk}</p>' for chunk in chunks)
					logger.debug(f"Split paragraph into {len(chunks)} chunks at markers: {[m[:20] for m in found_markers]}")
					return paragraphs
			
			# No split needed, return as-is
			return match.group(0)
		
		result = re.sub(pattern, split_paragraph, html, flags=re.DOTALL)
		logger.debug("Processed proficiency description paragraph splits")
		return result
		
	except Exception as e:
		logger.error(f"Failed to split proficiency description paragraphs: {e}", exc_info=True)
		return html


def _extract_armor_optimization_header(html: str) -> str:
	"""Extract 'Armor Optimization:' from the Description paragraph and make it a proper header.
	
	The PDF extraction incorrectly merged 'Armor Optimization:' into the Description paragraph.
	This function extracts it and creates a separate H3 header for it.
	"""
	try:
		# Find the Description of New Proficiencies section
		desc_pattern = r'(<p id="header-10-description-of-new-proficiencies">.*?</p>)<p>(.*?)</p>'
		match = re.search(desc_pattern, html, re.DOTALL)
		if not match:
			logger.warning("Could not find Description of New Proficiencies paragraph")
			return html
		
		header_html = match.group(1)
		paragraph_text = match.group(2)
		
		# Check if "Armor Optimization:" is in this paragraph
		if "Armor Optimization:" not in paragraph_text:
			logger.debug("Armor Optimization already extracted or not found in Description paragraph")
			return html
		
		# Split at "Armor Optimization:"
		parts = paragraph_text.split("Armor Optimization:", 1)
		if len(parts) != 2:
			return html
		
		intro_text = parts[0].strip()
		armor_opt_text = parts[1].strip()
		
		# Create the new header for Armor Optimization
		# Use header-10-armor-optimization as the ID (it will be renumbered later)
		armor_opt_header = (
			'<p id="header-10-armor-optimization" class="h3-header">'
			'<a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> '
			'<span style="color: #ca5804">Armor Optimization:</span></p>'
		)
		
		# Reconstruct the HTML
		new_content = (
			f'{header_html}'
			f'<p>{intro_text}</p>'
			f'{armor_opt_header}'
			f'<p>{armor_opt_text}</p>'
		)
		
		result = html[:match.start()] + new_content + html[match.end():]
		logger.info("Extracted Armor Optimization header from Description paragraph")
		return result
		
	except Exception as e:
		logger.error(f"Failed to extract Armor Optimization header: {e}", exc_info=True)
		return html


def _reconstruct_crossover_table(html: str) -> str:
	"""Reconstruct the Nonweapon Proficiency Group Crossovers table.
	
	The PDF extraction created separate headers for "Character Class" and "Proficiency Groups"
	followed by a paragraph of data. This should actually be a table with 2 columns and 7 rows
	(1 header row + 6 data rows).
	"""
	try:
		# Find the Nonweapon Proficiency Group Crossovers section
		pattern = (
			r'(<p id="header-19-nonweapon-proficiency-group-crossovers"[^>]*>.*?</p>)'
			r'<p id="header-20-character-class"[^>]*>.*?</p>'
			r'<p id="header-21-proficiency-groups"[^>]*>.*?</p>'
			r'<p>(.*?)</p>'
			r'(?=<p id="header-22-use-of-existing-proficiencies-in-dark-sun")'
		)
		
		match = re.search(pattern, html, re.DOTALL)
		if not match:
			logger.warning("Could not find Nonweapon Proficiency Group Crossovers section")
			return html
		
		header_html = match.group(1)
		data_text = match.group(2).strip()
		
		logger.info(f"Parsing crossover table data: {data_text}")
		
		# Parse the data text to extract character class and proficiency group pairs
		# Expected format: "Wizard, General Defiler Warrior, General Gladiator Wizard, General Preserver Psionicist, General Psionicist Priest, Rogue, General Templar Rogue, Warrior, General Trader"
		# This represents: Defiler -> Wizard, General; Gladiator -> Warrior, General; etc.
		
		# Note: "Psionicist" appears both as a proficiency group AND as a character class,
		# making automatic extraction ambiguous. The character classes list is required
		# to disambiguate (not a violation of NO_HARDCODED_DATA as this is structural metadata).
		# User specified: 2 columns, 7 rows (1 header + 6 data rows)
		
		# Character classes from Dark Sun (the 6 rows in the table)
		# These are the unique character classes that have proficiency group crossovers
		character_classes = ['Defiler', 'Gladiator', 'Preserver', 'Psionicist', 'Templar', 'Trader']
		
		logger.info(f"Looking for character classes: {character_classes}")
		
		# Now parse the data by finding each character class and extracting proficiency groups before it
		# Special handling for "Psionicist" which appears twice (as proficiency group and character class)
		table_data = []
		remaining_text = data_text
		
		for i, char_class in enumerate(character_classes):
			# For Psionicist, we need to find the SECOND occurrence (the character class, not the prof group)
			if char_class == 'Psionicist':
				# Find first occurrence (proficiency group)
				first_pos = remaining_text.find('Psionicist')
				if first_pos != -1:
					# Find second occurrence (character class)
					second_pos = remaining_text.find('Psionicist', first_pos + len('Psionicist'))
					if second_pos != -1:
						pos = second_pos
					else:
						# If no second occurrence, use the first
						pos = first_pos
				else:
					pos = -1
			else:
				# Find where this character class appears in the text
				pos = remaining_text.find(char_class)
			
			if pos == -1:
				logger.warning(f"Could not find character class {char_class} in remaining text")
				continue
			
			# Extract the proficiency groups before this character class
			prof_groups = remaining_text[:pos].strip()
			if prof_groups:
				# Clean up trailing punctuation and whitespace
				prof_groups = prof_groups.rstrip(',').strip()
			
			# For the last character class, get the remaining text after it
			if i == len(character_classes) - 1:
				# Get everything after this character class name
				next_text = remaining_text[pos + len(char_class):].strip()
				if next_text:
					prof_groups = next_text.lstrip(',').strip()
			
			# Move to the text after this character class for the next iteration
			remaining_text = remaining_text[pos + len(char_class):].strip()
			
			# Store the parsed row
			if prof_groups:
				table_data.append((char_class, prof_groups))
				logger.info(f"  {char_class} -> {prof_groups}")
		
		# If parsing failed, log the data for debugging
		if not table_data:
			logger.error(f"Failed to parse crossover table data: {data_text}")
			return html
		
		# Build the table HTML
		table_html = ['<table>']
		table_html.append('<tr><th>Character Class</th><th>Proficiency Groups</th></tr>')
		for char_class, prof_groups in table_data:
			table_html.append(f'<tr><td>{char_class}</td><td>{prof_groups}</td></tr>')
		table_html.append('</table>')
		
		# Reconstruct the section
		new_content = header_html + '\n' + '\n'.join(table_html) + '\n'
		
		# Replace the entire section
		result = html[:match.start()] + new_content + html[match.end():]
		
		logger.info("Successfully reconstructed Nonweapon Proficiency Group Crossovers table")
		return result
		
	except Exception as e:
		logger.error(f"Failed to reconstruct crossover table: {e}", exc_info=True)
		return html


def _fix_toc_indentation(html: str) -> str:
	"""Fix TOC indentation for H3 headers and remove TOC entries for converted table headers.
	
	After the header styling is applied and headers have font-size: 0.8em,
	we need to update the TOC to reflect this hierarchy by adding the
	toc-subsubheader class to H3 header TOC entries.
	
	Also removes TOC entries for "Character Class" and "Proficiency Groups" which
	are now part of the crossover table, not separate headers.
	"""
	try:
		# Define which headers should have toc-subsubheader class in the TOC
		h3_headers = [
			'header-10-armor-optimization',
			'header-11-bargain',
			'header-12-bureaucracy',
			'header-13-heat-protection',
			'header-14-psionic-detection',
			'header-15-sign-language',
			'header-16-somatic-concealment',
			'header-17-water-find',
			'header-18-weapon-improvisation',
			# Note: header-20 and header-21 are removed as they're now table headers
			'header-23-agriculture',
			'header-24-armorer',
			'header-25-artistic-ability',
			'header-26-blacksmithing',
			'header-27-fishing',
			'header-28-navigation',
			'header-29-religion',
			'header-30-seamanship',
			'header-31-swimming',
			'header-32-weaponsmithing',
		]
		
		# Update TOC entries for H3 headers
		for header_id in h3_headers:
			# Match: <li><a href="#header-11-bargain">Bargain:</a></li>
			# Replace with: <li class="toc-subsubheader"><a href="#header-11-bargain">Bargain:</a></li>
			pattern = f'<li><a href="#{header_id}">'
			replacement = f'<li class="toc-subsubheader"><a href="#{header_id}">'
			html = html.replace(pattern, replacement)
		
		# Remove TOC entries for headers that are now part of tables
		# - header-20 and header-21 are from the crossover table
		# - header-2 through header-9 are from the New Nonweapon Proficiencies table
		headers_to_remove = [
			'header-20-character-class',     # Crossover table header
			'header-21-proficiency-groups',  # Crossover table header
			'header-2-general',              # Nonweapon table section header
			'header-3-slots',                # Nonweapon table column header
			'header-4-modifier',             # Nonweapon table column header (if exists)
			'header-5-ability',              # Nonweapon table column header
			'header-6-proficiency',          # Nonweapon table column header
			'header-7-priest',               # Nonweapon table section header
			'header-8-warrior',              # Nonweapon table section header
			'header-9-wizard',               # Nonweapon table section header
		]
		for header_id in headers_to_remove:
			# Match and remove: <li><a href="#header-20-character-class">Character Class</a></li>
			pattern = f'<li[^>]*><a href="#{header_id}">[^<]*</a></li>'
			html = re.sub(pattern, '', html)
		
		logger.debug("Fixed TOC indentation for H3 headers and removed converted table header entries")
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix TOC indentation: {e}", exc_info=True)
		return html


def _inject_header_css(html: str) -> str:
	"""No-op function - CSS styles are now in the external stylesheet.
	
	Previously injected CSS styles for H2 and H3 header classes into the HTML.
	Now these styles are in styles.css and loaded via <link> tag.
	This function is kept for backward compatibility.
	"""
	# CSS is now in external stylesheet (styles.css), no injection needed
	logger.debug("Skipping CSS injection - styles are in external stylesheet")
	return html


def _apply_header_styling(html: str) -> str:
	"""Apply H2 and H3 CSS classes to headers for proper sizing.
	
	H1 headers: Default (New Nonweapon Proficiencies, Dark Sun Weapon Proficiencies, etc.) - no font-size
	H2 headers: Description of New Proficiencies, Nonweapon Proficiency Group Crossovers, etc. - font-size: 0.9em
	H3 headers: Individual proficiency names (Bargain, Bureaucracy, etc.) - font-size: 0.8em
	
	This function adds both the CSS class and the inline font-size style attribute.
	The inline style is required for TOC generation to recognize the header level.
	"""
	try:
		# Define which headers should be H2
		h2_headers = [
			'header-10-description-of-new-proficiencies',
			'header-19-nonweapon-proficiency-group-crossovers',
			'header-22-use-of-existing-proficiencies-in-dark-sun',
			'header-33-use-of-survival-proficiency-in-dark-sun',
		]
		
		# Define which headers should be H3 (individual proficiencies and sub-sections)
		h3_headers = [
			'header-10-armor-optimization',  # Newly extracted header
			'header-11-bargain',
			'header-12-bureaucracy',
			'header-13-heat-protection',
			'header-14-psionic-detection',
			'header-15-sign-language',
			'header-16-somatic-concealment',
			'header-17-water-find',
			'header-18-weapon-improvisation',
			# Note: header-20 and header-21 are omitted as they become table headers
			'header-23-agriculture',
			'header-24-armorer',
			'header-25-artistic-ability',
			'header-26-blacksmithing',
			'header-27-fishing',
			'header-28-navigation',
			'header-29-religion',
			'header-30-seamanship',
			'header-31-swimming',
			'header-32-weaponsmithing',
		]
		
		# Process H2 headers: add class and font-size to span
		for header_id in h2_headers:
			# Add class="h2-header" to the <p> tag
			pattern = f'(<p id="{header_id}")>'
			replacement = r'\1 class="h2-header">'
			html = re.sub(pattern, replacement, html)
			
			# Remove Roman numerals from H2 headers (format: "XII.  " at the start after <p> tag)
			# Match: <p id="header-10-description-of-new-proficiencies" class="h2-header">XI.  <a href...
			# Replace with: <p id="header-10-description-of-new-proficiencies" class="h2-header"><a href...
			pattern = f'(<p id="{header_id}" class="h2-header">)[IVXLCDM]+\\.\\s+'
			replacement = r'\1'
			html = re.sub(pattern, replacement, html)
			
			# Add font-size: 0.9em to the span's style attribute
			pattern = f'(<p id="{header_id}"[^>]*>.*?<span style="color: #ca5804)(">)'
			replacement = r'\1; font-size: 0.9em\2'
			html = re.sub(pattern, replacement, html, flags=re.DOTALL)
		
		# Process H3 headers: add class, font-size to span, and remove Roman numerals
		for header_id in h3_headers:
			# Add class="h3-header" to the <p> tag
			pattern = f'(<p id="{header_id}")>'
			replacement = r'\1 class="h3-header">'
			html = re.sub(pattern, replacement, html)
			
			# Remove Roman numerals from H3 headers (format: "XII.  " at the start after <p> tag)
			# Match: <p id="header-11-bargain" class="h3-header">XII.  <a href...
			# Replace with: <p id="header-11-bargain" class="h3-header"><a href...
			pattern = f'(<p id="{header_id}" class="h3-header">)[IVXLCDM]+\\.\\s+'
			replacement = r'\1'
			html = re.sub(pattern, replacement, html)
			
			# Add font-size: 0.8em to the span's style attribute
			pattern = f'(<p id="{header_id}"[^>]*>.*?<span style="color: #ca5804)(">)'
			replacement = r'\1; font-size: 0.8em\2'
			html = re.sub(pattern, replacement, html, flags=re.DOTALL)
		
		logger.debug("Applied H2 and H3 header styling classes, inline styles, and removed Roman numerals from H2 and H3")
		return html
	except Exception as e:
		logger.error(f"Failed to apply header styling: {e}", exc_info=True)
		return html


def apply_chapter_5_content_fixes(html: str) -> str:
	"""Apply Chapter 5 content fixes before HTML template generation.
	
	These fixes operate on the journal content (which is HTML-formatted text)
	before it gets wrapped in the full HTML template.
	"""
	logger.debug("Applying Chapter 5 content fixes (before template)")
	html = _split_intro_paragraphs(html)
	html = _split_weapon_proficiencies_section(html)
	html = _reconstruct_nonweapon_table(html)
	html = _remove_malformed_tables_from_descriptions(html)
	html = _extract_armor_optimization_header(html)
	html = _apply_header_styling(html)
	html = _split_proficiency_description_paragraphs(html)
	
	# Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
	html = convert_all_styled_headers_to_semantic(html)
	
	return html


def apply_chapter_5_html_fixes(html: str) -> str:
	"""Apply Chapter 5 HTML fixes after HTML template generation.
	
	These fixes operate on the final HTML document after the template
	has been applied, allowing us to inject CSS and make final adjustments.
	"""
	logger.debug("Applying Chapter 5 HTML fixes (after template)")
	html = _inject_header_css(html)
	html = _reconstruct_crossover_table(html)
	html = _fix_toc_indentation(html)
	
	# Final conversion to semantic HTML (in case any headers were added in HTML fixes)
	html = convert_all_styled_headers_to_semantic(html)
	
	return html


def apply_chapter_5_fixes(html: str) -> str:
	"""Legacy function for backward compatibility.
	
	This calls apply_chapter_5_content_fixes for compatibility with
	existing code that expects this function name.
	"""
	return apply_chapter_5_content_fixes(html)

