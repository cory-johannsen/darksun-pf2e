"""
Chapter 11 (Encounters) Postprocessing

This module applies chapter-specific HTML postprocessing for Chapter 11.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _apply_header_styling(html: str) -> str:
	"""Apply H2 CSS classes to Monsters subsection headers.
	
	H1 headers: Main section headers (Wizard, Priest, and Psionicist Encounters, Encounters in City-States, Monsters, etc.)
	H2 headers: Under "Monsters" section: Magic, Psionics, Plant-based Monsters, Monstrous Compendium 1 and 2, 
	            and campaign setting references (MC3, MC4, MC5, MC6)
	
	This function adds both the CSS class and the inline font-size style attribute.
	The inline style is required for TOC generation to recognize the header level.
	
	Campaign setting headers (MC3, MC4, MC5, MC6) are rendered as actual <h2> tags,
	while other H2 headers (Magic, Psionics, etc.) are rendered as <p> tags with styling.
	"""
	try:
		# Define which headers should be H2 (under Monsters section)
		# These are rendered as <p> tags with styling
		h2_paragraph_headers = [
			'header-3-magic',                        # Magic:
			'header-4-psionics',                     # Psionics:
			'header-5-plant-based-monsters',         # Plant-Based Monsters:
			'header-6-monstrous-compendium-1-and-2', # Monstrous Compendium 1 and 2
		]
		
		# These are rendered as actual <h2> tags (campaign settings)
		h2_element_headers = [
			'forgotten-realms®-(mc3)',               # Forgotten Realms® (MC3)
			'dragonlance®-(mc4)',                    # Dragonlance® (MC4)
			'greyhawk®-(mc5)',                       # Greyhawk® (MC5)
			'kara-tur-(mc6)',                        # Kara-Tur (MC6)
		]
		
		# Process H2 paragraph headers: add class, font-size to span, and remove Roman numerals
		for header_id in h2_paragraph_headers:
			# Add class="h2-header" to the <p> tag
			pattern = f'(<p id="{header_id}")>'
			replacement = r'\1 class="h2-header">'
			html = re.sub(pattern, replacement, html)
			
			# Remove Roman numerals from H2 headers (format: "IV.  " at the start after <p> tag)
			# Match: <p id="header-3-magic" class="h2-header">IV.  <a href...
			# Replace with: <p id="header-3-magic" class="h2-header"><a href...
			pattern = f'(<p id="{header_id}" class="h2-header">)[IVXLCDM]+\\.\\s+'
			replacement = r'\1'
			html = re.sub(pattern, replacement, html)
			
			# Add font-size: 0.9em to the span's style attribute
			pattern = f'(<p id="{header_id}"[^>]*>.*?<span style="color: #ca5804)(">)'
			replacement = r'\1; font-size: 0.9em\2'
			html = re.sub(pattern, replacement, html, flags=re.DOTALL)
		
		# Process H2 element headers: add class and styling to <h2> tags
		# Match any h2 tag with an id containing (mc4), (mc5), or (mc6)
		# Simple pattern: find any <h2 id="..." that contains mc4, mc5, or mc6
		pattern = r'<h2 id="(header-[^"]*\(mc[456]\))">'
		
		logger.warning(f"🔍 Searching for MC4-6 headers with pattern: {pattern}")
		logger.warning(f"🔍 HTML length: {len(html)} characters")
		
		# Check if the pattern exists in the HTML
		test_matches = re.findall(pattern, html)
		logger.warning(f"🔍 Found {len(test_matches)} matches: {test_matches}")
		
		def add_styling(match):
			header_id = match.group(1)
			logger.warning(f"🔍 Adding styling to: {header_id}")
			return f'<h2 id="{header_id}" class="h2-header" style="font-size: 0.9em">'
		
		html, count = re.subn(pattern, add_styling, html)
		logger.warning(f"✅ Applied styling to {count} campaign setting headers (MC4-MC6)")
		
		logger.debug("Applied H2 header styling classes, inline styles, and removed Roman numerals from H2 headers")
		return html
		
	except Exception as e:
		logger.error(f"Failed to apply header styling: {e}", exc_info=True)
		return html


def _fix_toc_indentation(html: str) -> str:
	"""Apply proper indentation to H2 headers in the Table of Contents.
	
	H2 headers (Magic, Psionics, Plant-based Monsters, Monstrous Compendium 1 and 2,
	and campaign setting headers MC3, MC4, MC5, MC6) should have the toc-subheader class
	for proper indentation in the TOC.
	
	Campaign setting headers use different IDs (without 'header-' prefix) since they're
	rendered as actual <h2> tags rather than <p> tags.
	"""
	try:
		# Define which TOC entries should be indented (H2 headers)
		# These use "header-X" format (rendered as <p> tags)
		h2_paragraph_toc_entries = [
			'header-3-magic',
			'header-4-psionics',
			'header-5-plant-based-monsters',
			'header-6-monstrous-compendium-1-and-2',
		]
		
		# These use different IDs (rendered as <h2> tags)
		h2_element_toc_entries = [
			'header-forgotten-realms®-(mc3)',
			'header-dragonlance®-(mc4)',
			'header-greyhawk®-(mc5)',
			'header-kara-tur-(mc6)',
		]
		
		# Add toc-subheader class to H2 paragraph entries
		for header_id in h2_paragraph_toc_entries:
			# Match: <li><a href="#header-3-magic">
			# Replace with: <li class="toc-subheader"><a href="#header-3-magic">
			pattern = f'<li><a href="#{header_id}">'
			replacement = f'<li class="toc-subheader"><a href="#{header_id}">'
			html = html.replace(pattern, replacement)
		
		# Add toc-subheader class to H2 element entries
		for header_id in h2_element_toc_entries:
			# Match: <li><a href="#header-forgotten-realms®-(mc3)">
			# Replace with: <li class="toc-subheader"><a href="#header-forgotten-realms®-(mc3)">
			pattern = f'<li><a href="#{header_id}">'
			replacement = f'<li class="toc-subheader"><a href="#{header_id}">'
			html = html.replace(pattern, replacement)
		
		logger.debug("Applied TOC indentation for H2 headers")
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix TOC indentation: {e}", exc_info=True)
		return html


def _fix_roman_numerals(html: str) -> str:
	"""Fix Roman numerals for H1 headers after H2 headers are removed.
	
	Since H2 headers don't have Roman numerals, H1 headers after the Monsters section
	need to be renumbered. The campaign setting headers (MC3, MC4, MC5, MC6) are now H2,
	so they don't get Roman numerals. Only Wilderness Encounters and subsequent headers
	get Roman numerals as H1.
	
	New header sequence:
	- header-0: Wizard, Priest, and Psionicist Encounters (I)
	- header-1: Encounters in City-States (II)
	- header-2: Monsters (III)
	- header-3-5: H2 subheaders (no numerals)
	- Forgotten Realms through Kara-Tur: H2 (no numerals)
	- header-7: Wilderness Encounters (should be IV, first H1 after Monsters)
	- header-8+: Subsequent H1 headers (V, VI, etc.)
	"""
	try:
		# Header renumbering map: header-id -> correct Roman numeral
		# After campaign settings become H2, the numbering continues from IV
		header_renumbering = {
			'header-7-wilderness-encounters': 'IV',      # First H1 after Monsters section
			'header-8-stoney-barrens': 'V',
			'header-9-sandy-wastes': 'VI',
			'header-10-boulder-fields': 'VII',
			'header-11-verdant-belts': 'VIII',
			'header-12-mudflats': 'IX',
			'header-13-salt-flats': 'X',
			# Skip table headers as they shouldn't have Roman numerals
		}
		
		for header_id, correct_numeral in header_renumbering.items():
			# Pattern: <p id="header-7-wilderness-encounters">VIII.  <a href="#top"
			# Replace with: <p id="header-7-wilderness-encounters">IV.  <a href="#top"
			pattern = f'(<p id="{header_id}">)[IVXLCDM]+\\.'
			replacement = f'\\1{correct_numeral}.'
			html = re.sub(pattern, replacement, html)
			logger.debug(f"Fixed Roman numeral for {header_id} to {correct_numeral}")
		
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix Roman numerals: {e}", exc_info=True)
		return html


def _fix_wilderness_terrain_headers(html: str) -> str:
	"""
	Convert wilderness terrain headers (Stoney Barrens, Sandy Wastes, etc.) to H2 headers.
	
	These headers should be H2 and on separate lines, not embedded in paragraphs.
	"""
	try:
		terrain_headers = [
			'Stoney Barrens',
			'Sandy Wastes', 
			'Mountains',
			'Scrub Plains',
			'Rocky Badlands',
			'Salt Flats'
		]
		
		for header in terrain_headers:
			# Convert <p id="header-...">Header [^]</p> to <h2>Header [^]</h2>
			header_id = header.lower().replace(' ', '-')
			
			# Pattern 1: Replace opening <p> tag with <h2> and closing </p> with </h2>
			# The link text is [^] not [∧]
			p_pattern = f'<p id="header-{header_id}">{header} <a href="#top"[^>]*>\\[\\^\\]</a></p>'
			h2_replacement = f'<h2 id="header-{header_id}" class="h2-header" style="font-size: 0.9em">{header} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
			html = re.sub(p_pattern, h2_replacement, html)
			
			# Pattern 2: Fix any malformed headers where <h2> was created but </p> remained
			malformed_pattern = f'(<h2 id="header-{header_id}"[^>]*>{header}[^<]*</a>)</p>'
			malformed_replacement = r'\1</h2>'
			html = re.sub(malformed_pattern, malformed_replacement, html)
			
			# Remove corrupted paragraphs that embed the header name with [^] or [∧]
			# Example: <p>...creature names Mountains [^]</p>
			corrupt_pattern = f'<p>[^<]*{header} \\[(?:\\^|∧)\\]</p>'
			html = re.sub(corrupt_pattern, '', html)
			logger.debug(f"Cleaned corrupted paragraph for {header}")
		
		# Insert missing Stoney Barrens header before the first table
		if '<h2 id="header-stoney-barrens"' not in html:
			# Find the third paragraph (When encounters occur...) followed by the first table
			pattern = r'(Wilderness Encounters table in the DMG\.</p>)(<table><tr><th>Die Roll</th><th>Creature</th></tr>)'
			stoney_header = '<h2 id="header-stoney-barrens" class="h2-header" style="font-size: 0.9em">Stoney Barrens <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
			replacement = r'\1' + stoney_header + r'\2'
			html, count = re.subn(pattern, replacement, html, count=1)
			if count > 0:
				logger.warning(f"✅ Inserted missing Stoney Barrens H2 header")
			else:
				logger.warning("⚠️  Could not insert Stoney Barrens header")
		
		# Insert missing Mountains header
		# Look for Sandy Wastes table </table> followed by malformed tables, then Mountains table
		if '<h2 id="header-mountains"' not in html:
			# Pattern: After any </table>, skip any malformed tables, then find Mountains table (lizard, fire)
			pattern = r'(</table>)(?:<table class="ds-table">.*?</table>\s*)*\s*(<table><tr><th>Die Roll</th><th>Creature</th></tr><tr><td>2</td><td>lizard, fire</td>)'
			mountains_header = '<h2 id="header-mountains" class="h2-header" style="font-size: 0.9em">Mountains <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
			replacement = r'\1' + mountains_header + r'\2'
			html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
			if count > 0:
				logger.warning(f"✅ Inserted missing Mountains H2 header")
			else:
				logger.warning("⚠️  Could not insert Mountains header")
		
		# Insert missing Salt Flats header
		# Look for Rocky Badlands table </table> followed directly by Salt Flats table (basilisk, dracolisk)
		if '<h2 id="header-salt-flats"' not in html:
			# Pattern: After Rocky Badlands </table>, find Salt Flats table
			pattern = r'(</table>)\s*(<table><tr><th>Die Roll</th><th>Creature</th></tr><tr><td>2</td><td>basilisk, dracolisk</td>)'
			salt_header = '<h2 id="header-salt-flats" class="h2-header" style="font-size: 0.9em">Salt Flats <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
			replacement = r'\1' + salt_header + r'\2'
			html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)
			if count > 0:
				logger.warning(f"✅ Inserted missing Salt Flats H2 header")
			else:
				logger.warning("⚠️  Could not insert Salt Flats header")
		
		logger.warning("✅ Fixed wilderness terrain headers to H2")
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix wilderness terrain headers: {e}", exc_info=True)
		return html


def _fix_wilderness_encounters_paragraphs(html: str) -> str:
	"""
	Fix paragraph breaks in the Wilderness Encounters section.
	
	The section should have 3 paragraphs:
	1. "The wilds of Athas...fatal for the party."
	2. "Each of the tables below...Monstrous Compendiums."
	3. "When encounters occur...in the DMG."
	"""
	try:
		# Step 1: Fix the first paragraph - ensure it ends at "fatal for the party."
		# Remove the text "Each of the tables below lists monsters for en-" from the first paragraph
		# This text is split across a table boundary
		pattern = r'(<p>The wilds of Athas are teeming with intelligent and unintelligent monsters\. Encounters in the wilderness should be rolled for on a daily basis or as the DM sees fit\. Obviously, if characters are lost or unprepared, even the most routine wilderness encounters can prove to be fatal for the party\.) Each of the tables below lists monsters for en-</p>'
		replacement = r'\1</p>'
		html, count1 = re.subn(pattern, replacement, html, flags=re.DOTALL)
		if count1 > 0:
			logger.warning(f"✅ Fixed first Wilderness Encounters paragraph ({count1} replacements)")
		else:
			logger.warning("⚠️  Could not fix first Wilderness Encounters paragraph - pattern did not match")
		
		# Step 1.5: Fix truncated paragraph that ends with "...if you have the appropriate Monstrous Compendiums."
		# The paragraph is getting cut off and needs to be completed properly
		# Pattern: Look for the paragraph that ends with incomplete text after "Monstrous Compendiums"
		pattern = r'(<p>Each of the tables below lists monsters for encounters in a particular terrain type\. The monsters listed come from the Wanderer&#x27;s Guide and from Monstrous Compendiums I and II\. The other monsters listed as appropriate to Dark Sun can be )[^<]+(</p>)'
		replacement = r'\1added, as well, if you have the appropriate Monstrous Compendiums.\2'
		html, count1b = re.subn(pattern, replacement, html, flags=re.DOTALL)
		if count1b > 0:
			logger.warning(f"✅ Fixed truncated Monstrous Compendiums paragraph ({count1b} replacements)")
		else:
			logger.debug("No truncated Monstrous Compendiums paragraph found")
		
		# Step 2: Insert the second paragraph after the first paragraph ends
		# Find where first paragraph ends (after "fatal for the party.")
		pattern = r'(fatal for the party\.</p>)(<table class="ds-table">)'
		
		second_para = ('<p>Each of the tables below lists monsters for encounters in a particular terrain type. '
		               'The monsters listed come from the Wanderer&#x27;s Guide and from Monstrous Compendiums I and II. '
		               'The other monsters listed as appropriate to Dark Sun can be added, as well, if you have '
		               'the appropriate Monstrous Compendiums.</p>')
		
		replacement = r'\1' + second_para + r'\2'
		html, count2 = re.subn(pattern, replacement, html, count=1)
		if count2 > 0:
			logger.warning(f"✅ Inserted second Wilderness Encounters paragraph ({count2} replacements)")
		else:
			logger.warning("⚠️  Could not insert second Wilderness Encounters paragraph - pattern did not match")
		
		# Step 3: Clean up duplicate/fragmented text that's in tables
		# Remove the text fragments that are incorrectly placed in table cells
		html = re.sub(r'<td>counters can prove to be fatal for the party\. Each of the tables below lists monsters for en-</td>', '', html)
		logger.debug("Removed first fragment from table cell")
		
		# Fix the table cell that contains mixed content
		html = re.sub(r'<p>spider, huge gith counters in a particular terrain type\. The monsters ettercap/ behir centipede, giant beetle, boring listed come from theWanderer&#x27;s Guideand from Monstrous CompendiumsI and II\. The other monsters listed as appropriate to Dark Sun can be add-</p>', '', html)
		logger.debug("Removed second fragment paragraph")
		
		html = re.sub(r'<td>sters listed as appropriate to Dark Sun can be add-</td>', '', html)
		logger.debug("Removed third fragment from table cell")
		
		html = re.sub(r'<td>ed, as well, if you have the appropriate  Monstrous Compendiums \.</td>', '', html)
		logger.debug("Removed fourth fragment from table cell")
		
		# Remove duplicate paragraphs that contain fragments
		html = re.sub(r'<p>baazrag ed, as well, if you have the appropriateMonstrous Compendiums \. tembo braxat</p>', '', html)
		logger.debug("Removed fifth fragment paragraph")
		
		# Remove duplicate malformed tables that appear between proper tables
		# These tables have creature names mixed with table headers
		html = re.sub(r'<table class="ds-table"><tr><td>gai bulette roc</td><td>Die Roll</td><td>Creature</td></tr>.*?</table>', '', html, flags=re.DOTALL)
		logger.debug("Removed malformed table fragments between Stoney Barrens and Sandy Wastes")
		
		# Remove fragments between Sandy Wastes and Mountains
		html = re.sub(r'<p>snake, giant constrictor snake, constrictor sandling elves/gith kank scorpion, huge slaves inix anakore jozhal spider, phase centipede, megaloyuan-ti dragonne Mountains \[∧\]</p>', '', html)
		logger.debug("Removed fragment paragraph between Sandy Wastes and Mountains")
		
		# Remove malformed tables that appear after the new wilderness tables (Scrub Plains, Rocky Badlands, Salt Flats)
		html = re.sub(r'<table class="ds-table"><tr><td>[^<]+</td><td>[^<]*Salt Flats[^<]*</td></tr>.*?</table>', '', html, flags=re.DOTALL)
		logger.debug("Removed malformed table fragments near Salt Flats")
		
		# Remove fragments between Rocky Badlands and Salt Flats
		html = re.sub(r'<p>giant genie, efreeti ant, swarm Salt Flats \[∧\]</p>', '', html)
		logger.debug("Removed fragment paragraph between Rocky Badlands and Salt Flats")
		
		# Step 4: Insert the third paragraph AFTER the second paragraph (with Monstrous Compendiums)
		# Insert after the paragraph that ends with "...appropriate Monstrous Compendiums."
		third_para = ('<p>When encounters occur should be determined using the Frequency &amp; Chance of '
		              'Wilderness Encounters table in the DMG.</p>')
		
		# First, remove ALL malformed tables that appear between the paragraph and the proper tables
		# These malformed tables have data mixed with headers and duplicate text
		# Pattern: Remove all ds-table tables after Monstrous Compendiums until we hit a proper table
		html = re.sub(r'(Monstrous Compendiums\.</p>)(?:<table class="ds-table">.*?</table>\s*)+', 
		              r'\1', html, flags=re.DOTALL)
		logger.debug("Removed all malformed ds-table tables after Monstrous Compendiums paragraph")
		
		# Remove the corrupted "When encounters occur" paragraph that has mixed content
		html = re.sub(r'<p>When encounters occur should be determined us[^<]*</p>', '', html)
		logger.debug("Removed corrupted 'When encounters occur' paragraph with mixed content")
		
		# Now insert the third paragraph before the first table (which is Stoney Barrens, though it may not have a header)
		# Pattern: Match paragraph ending with Monstrous Compendiums followed immediately by newline/whitespace and a table
		pattern = r'(Monstrous Compendiums\.</p>)\s*(<table>)'
		replacement = r'\1' + third_para + r'\2'
		html, count3 = re.subn(pattern, replacement, html, count=1)
		if count3 > 0:
			logger.warning(f"✅ Inserted third Wilderness Encounters paragraph ({count3} replacements)")
		else:
			logger.warning("⚠️  Could not insert third Wilderness Encounters paragraph - pattern did not match")
		
		# Remove the fragmented "When encounters occur" text from tables
		html = re.sub(r'<td>When encounters occur should be determined us-</td>', '<td></td>', html)
		logger.debug("Removed sixth fragment from table cell")
		
		html = re.sub(r'<td>ing the Frequency &amp; Chance of Wilderness Encounters table in the  DMG\.</td>', '<td></td>', html)
		logger.debug("Removed seventh fragment from table cell")
		
		# Remove duplicate paragraph fragments
		html = re.sub(r'<p>When encounters occur should be determined usbat, huge ing the Frequency &amp; Chance of Wilderness Encounters table in theDMG\. ettin basilisk, greater ant, swarm</p>', '', html)
		logger.debug("Removed eighth fragment paragraph")
		
		logger.warning("✅ Fixed Wilderness Encounters paragraph breaks")
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix Wilderness Encounters paragraphs: {e}", exc_info=True)
		return html


def apply_chapter_11_content_fixes(html: str) -> str:
	"""
	Apply all Chapter 11 specific content fixes.
	
	Args:
		html: The HTML content to fix
		
	Returns:
		The fixed HTML content
	"""
	logger.info("Applying Chapter 11 content fixes")
	
	# EMERGENCY FIX: Insert Forgotten Realms header manually
	# The rendering is creating it, but it's getting lost during HTML assembly
	# Insert it AFTER the Monstrous Compendium list and BEFORE Dragonlance
	forgotten_realms_header = '<h2 id="header-forgotten-realms®-(mc3)" class="h2-header" style="font-size: 0.9em">Forgotten Realms® (MC3) <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
	
	# Create the Forgotten Realms monster list
	forgotten_realms_monsters = [
		"Bhaergala*",
		"Meazel*",
		"Rhaumbusun",
		"Strider, Giant",
		"Thessalmonster",
		"Thri-kreen*"
	]
	forgotten_realms_list = '<ul>\n' + '\n'.join(f'<li>{monster}</li>' for monster in forgotten_realms_monsters) + '\n</ul>'
	
	# First, remove any existing Forgotten Realms header that's in the wrong location
	# Pattern: the header that's splitting the Plant-Based Monsters paragraph
	# Match the entire h2 element including its anchor tag
	html = re.sub(r'<h2 id="header-forgotten-realms®-\(mc3\)"[^>]*>.*?</h2>', '', html, flags=re.DOTALL)
	
	# Also remove any stray paragraph containing "Aarakocra" that appears after the MC list
	# This is duplicate content that shouldn't be there
	html = re.sub(r'</ul><p>Aarakocra[^<]*</p>', '</ul>', html)
	
	# Remove duplicate "Plant, Carnivorous" paragraph after Greyhawk list
	# This paragraph is from block 39 that should have been skipped but wasn't
	html = re.sub(r'</ul>\s*<p>Plant, Carnivorous\(Cactus, Vampire\)</p>', '</ul>', html)
	logger.debug("Removed duplicate Plant, Carnivorous paragraph after Greyhawk list")
	
	# Remove duplicate combined paragraph after Kara-Tur section
	# Pattern: <p>*indicates possible psionic wild power No creatures from...
	# This combines the legend and the "No creatures" text into one paragraph (duplicate)
	# Note: The duplicate has LETTER SPACING issues: "N o creatures f r o m t h e"
	# We need to match with optional spaces between characters
	pattern = r'<p>\*indicates possible psionic wild power\s+N\s*o\s+creatures\s+f\s*r\s*o\s*m\s*t\s*h\s*e.+?great wizards\.</p>'
	html, count = re.subn(pattern, '', html, flags=re.DOTALL)
	if count > 0:
		logger.warning(f"✅ Removed {count} duplicate combined paragraph(s) after Kara-Tur section")
	else:
		logger.warning("⚠️  No duplicate Kara-Tur paragraphs matched the removal pattern")
	
	# Find the correct location: right before the Dragonlance® (MC4) header
	# This places it after the Monstrous Compendium list
	# Pattern: <h2 id="header-dragonlance®-(mc4)"
	pattern = r'(<h2 id="header-dragonlance®-\(mc4\)")'
	if re.search(pattern, html):
		# Insert both the header and the list before Dragonlance
		html = re.sub(pattern, f'{forgotten_realms_header}{forgotten_realms_list}\\1', html)
		logger.warning("✅ Inserted Forgotten Realms® (MC3) header with monster list (after MC 1&2, before Dragonlance)")
	else:
		logger.warning("⚠️ Could not find insertion point for Forgotten Realms header (looking for Dragonlance header)")
	
	# Fix Wilderness Encounters paragraph breaks
	html = _fix_wilderness_encounters_paragraphs(html)
	
	# Fix wilderness terrain headers to H2
	html = _fix_wilderness_terrain_headers(html)
	
	# Remove duplicate ds-table tables between Scrub Plains and Rocky Badlands
	# These 4 tables appear after the terrain headers have been converted to H2
	pattern = r'(pseudodragon</td></tr><tr><td>20</td><td>gaj</td></tr></table>)(<table class="ds-table">.*?</table>\s*)+(<h2 id="header-rocky-badlands")'
	replacement = r'\1\3'
	html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)
	if count > 0:
		logger.warning(f"✅ Removed {count} set(s) of duplicate ds-table tables between Scrub Plains and Rocky Badlands")
	else:
		logger.debug("No duplicate ds-table tables found between Scrub Plains and Rocky Badlands")
	
	# Apply header styling (H2 for Magic, Psionics, Plant-based Monsters)
	html = _apply_header_styling(html)
	
	# Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
	html = convert_all_styled_headers_to_semantic(html)
	
	# Fix TOC indentation for H2 headers
	html = _fix_toc_indentation(html)
	
	# Fix Roman numerals for remaining H1 headers
	html = _fix_roman_numerals(html)
	
	logger.info("Chapter 11 content fixes complete")
	return html

