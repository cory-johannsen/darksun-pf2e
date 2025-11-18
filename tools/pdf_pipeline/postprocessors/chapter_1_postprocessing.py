"""
Chapter 1 (Ability Scores) Postprocessing

This module applies chapter-specific HTML postprocessing for Chapter 1.
"""

import re
import logging
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def _apply_header_styling(html: str) -> str:
	"""Apply H2 CSS classes to Optional Methods headers.
	
	H1 headers: Main section headers (Rolling Ability Scores, The Ability Scores, etc.)
	H2 headers: Optional Methods and all Optional Method I through V
	
	This function adds both the CSS class and the inline font-size style attribute.
	The inline style is required for TOC generation to recognize the header level.
	"""
	try:
		# Define which headers should be H2
		h2_headers = [
			'header-3-optional-methods',       # Optional Methods
			'header-4-optional-method-i',      # Optional Method I:
			'header-5-optional-method-ii',     # Optional Method II:
			'header-6-optional-method-iii',    # Optional Method III:
			'header-7-optional-method-iv',     # Optional Method IV:
			'header-8-optional-method-v',      # Optional Method V:
			'header-10-intelligence',          # Intelligence:
			'header-11-wisdom',                # Wisdom:
		]
		
		# Process H2 headers: add class, font-size to span, and remove Roman numerals
		for header_id in h2_headers:
			# Add class="h2-header" to the <p> tag
			pattern = f'(<p id="{header_id}")>'
			replacement = r'\1 class="h2-header">'
			html = re.sub(pattern, replacement, html)
			
			# Remove Roman numerals from H2 headers (format: "IV.  " at the start after <p> tag)
			# Match: <p id="header-3-optional-methods" class="h2-header">IV.  <a href...
			# Replace with: <p id="header-3-optional-methods" class="h2-header"><a href...
			pattern = f'(<p id="{header_id}" class="h2-header">)[IVXLCDM]+\\.\\s+'
			replacement = r'\1'
			html = re.sub(pattern, replacement, html)
			
			# Add font-size: 0.9em to the span's style attribute
			pattern = f'(<p id="{header_id}"[^>]*>.*?<span style="color: #ca5804)(">)'
			replacement = r'\1; font-size: 0.9em\2'
			html = re.sub(pattern, replacement, html, flags=re.DOTALL)
		
		logger.debug("Applied H2 header styling classes, inline styles, and removed Roman numerals from H2 headers")
		return html
		
	except Exception as e:
		logger.error(f"Failed to apply header styling: {e}", exc_info=True)
		return html


def _fix_toc_indentation(html: str) -> str:
	"""Apply proper indentation to H2 headers in the Table of Contents.
	
	H2 headers (Optional Methods) should have the toc-subheader class
	for proper indentation in the TOC.
	"""
	try:
		# Define which TOC entries should be indented (H2 headers)
		h2_toc_entries = [
			'header-3-optional-methods',
			'header-4-optional-method-i',
			'header-5-optional-method-ii',
			'header-6-optional-method-iii',
			'header-7-optional-method-iv',
			'header-8-optional-method-v',
			'header-10-intelligence',
			'header-11-wisdom',
		]
		
		# Add toc-subheader class to H2 entries
		for header_id in h2_toc_entries:
			# Match: <li><a href="#header-3-optional-methods">
			# Replace with: <li class="toc-subheader"><a href="#header-3-optional-methods">
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
	
	Since H2 headers no longer have Roman numerals, H1 headers need to be renumbered.
	Header-9 "The Ability Scores" should be IV (not X) since headers 3-8 are now H2.
	"""
	try:
		# Replace "X." with "IV." for header-9-the-ability-scores
		# Pattern: <p id="header-9-the-ability-scores">X.  <a href="#top"
		# Replace with: <p id="header-9-the-ability-scores">IV.  <a href="#top"
		pattern = r'(<p id="header-9-the-ability-scores">)X\.'
		replacement = r'\1IV.'
		html = re.sub(pattern, replacement, html)
		
		logger.debug("Fixed Roman numeral for The Ability Scores (X → IV)")
		return html
		
	except Exception as e:
		logger.error(f"Failed to fix Roman numerals: {e}", exc_info=True)
		return html


def apply_chapter_1_content_fixes(html: str) -> str:
	"""
	Apply all Chapter 1 specific content fixes.
	
	Args:
		html: The HTML content to fix
		
	Returns:
		The fixed HTML content
	"""
	logger.info("Applying Chapter 1 content fixes")
	
	# Apply header styling (H2 for Optional Methods) - old method kept for creating classes
	html = _apply_header_styling(html)
	
	# Convert styled <p> headers to semantic HTML (<h2>, <h3>, <h4>)
	html = convert_all_styled_headers_to_semantic(html)
	
	# Fix TOC indentation for H2 headers
	html = _fix_toc_indentation(html)
	
	# Fix Roman numerals for remaining H1 headers
	html = _fix_roman_numerals(html)
	
	logger.info("Chapter 1 content fixes complete")
	return html

