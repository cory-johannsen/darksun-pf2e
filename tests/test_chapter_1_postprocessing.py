"""
Unit tests for Chapter 1 (Ability Scores) postprocessing.
"""

import unittest
from tools.pdf_pipeline.postprocessors.chapter_1_postprocessing import apply_chapter_1_content_fixes


class TestChapter1Postprocessing(unittest.TestCase):
	"""Test Chapter 1 postprocessing functions."""

	def test_apply_h2_header_styling(self):
		"""Test that H2 headers get proper styling and no Roman numerals."""
		# Mock HTML with Optional Methods header (H1 format with Roman numeral)
		input_html = '''
		<p id="header-3-optional-methods">IV.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Optional Methods</span></p>
		<p id="header-4-optional-method-i">V.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Optional Method I:</span></p>
		'''
		
		result = apply_chapter_1_content_fixes(input_html)
		
		# Verify H2 class is added
		self.assertIn('class="h2-header"', result)
		self.assertIn('id="header-3-optional-methods" class="h2-header"', result)
		self.assertIn('id="header-4-optional-method-i" class="h2-header"', result)
		
		# Verify font-size is added to span
		self.assertIn('style="color: #ca5804; font-size: 0.9em"', result)
		
		# Verify Roman numerals are removed from H2 headers
		# Should not have "IV.  " or "V.  " after the <p> tag opening for these headers
		self.assertNotIn('header-3-optional-methods" class="h2-header">IV.', result)
		self.assertNotIn('header-4-optional-method-i" class="h2-header">V.', result)

	def test_all_optional_methods_become_h2(self):
		"""Test that all Optional Method headers I-V, Intelligence, and Wisdom become H2."""
		input_html = '''
		<p id="header-3-optional-methods">IV.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Methods</span></p>
		<p id="header-4-optional-method-i">V.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method I:</span></p>
		<p id="header-5-optional-method-ii">VI.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method II:</span></p>
		<p id="header-6-optional-method-iii">VII.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method III:</span></p>
		<p id="header-7-optional-method-iv">VIII.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method IV:</span></p>
		<p id="header-8-optional-method-v">IX.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method V:</span></p>
		<p id="header-10-intelligence">XI.  <a href="#top">[^]</a> <span style="color: #ca5804">Intelligence:</span></p>
		<p id="header-11-wisdom">XII.  <a href="#top">[^]</a> <span style="color: #ca5804">Wisdom:</span></p>
		'''
		
		result = apply_chapter_1_content_fixes(input_html)
		
		# All should have h2-header class
		for i in range(3, 9):  # headers 3-8
			self.assertIn(f'id="header-{i}-', result)
		# Also check 10 and 11
		self.assertIn('id="header-10-intelligence"', result)
		self.assertIn('id="header-11-wisdom"', result)
		
		# Count h2-header occurrences - should be 8 (6 Optional Methods + Intelligence + Wisdom)
		h2_count = result.count('class="h2-header"')
		self.assertEqual(h2_count, 8, f"Expected 8 H2 headers, found {h2_count}")
		
		# Verify all have font-size styling
		# Should have 8 instances of the styled color span
		styled_span_count = result.count('style="color: #ca5804; font-size: 0.9em"')
		self.assertEqual(styled_span_count, 8, f"Expected 8 styled spans, found {styled_span_count}")

	def test_h1_headers_unchanged(self):
		"""Test that H1 headers remain unchanged."""
		input_html = '''
		<p id="header-0-rolling-ability-scores">I.  <a href="#top">[^]</a> <span style="color: #ca5804">Rolling Ability Scores</span></p>
		<p id="header-3-optional-methods">IV.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Methods</span></p>
		'''
		
		result = apply_chapter_1_content_fixes(input_html)
		
		# H1 header should keep Roman numeral
		self.assertIn('header-0-rolling-ability-scores">I.', result)
		
		# H1 header should NOT have h2-header class
		self.assertNotIn('id="header-0-rolling-ability-scores" class="h2-header"', result)
		
		# H2 header should not have Roman numeral
		self.assertNotIn('header-3-optional-methods" class="h2-header">IV.', result)

	def test_roman_numeral_renumbering(self):
		"""Test that The Ability Scores gets renumbered from X to IV."""
		input_html = '''
		<p id="header-9-the-ability-scores">X.  <a href="#top">[^]</a> <span style="color: #ca5804">The Ability Scores</span></p>
		'''
		
		result = apply_chapter_1_content_fixes(input_html)
		
		# Should have IV not X
		self.assertIn('header-9-the-ability-scores">IV.', result)
		self.assertNotIn('header-9-the-ability-scores">X.', result)

	def test_toc_indentation(self):
		"""Test that H2 headers get proper TOC indentation."""
		input_html = '''
		<nav id="table-of-contents">
		<ul>
		<li><a href="#header-0-rolling-ability-scores">Rolling Ability Scores</a></li>
		<li><a href="#header-3-optional-methods">Optional Methods</a></li>
		<li><a href="#header-4-optional-method-i">Optional Method I:</a></li>
		<li><a href="#header-10-intelligence">Intelligence:</a></li>
		</ul>
		</nav>
		<p id="header-3-optional-methods">IV.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Methods</span></p>
		<p id="header-4-optional-method-i">V.  <a href="#top">[^]</a> <span style="color: #ca5804">Optional Method I:</span></p>
		<p id="header-10-intelligence">XI.  <a href="#top">[^]</a> <span style="color: #ca5804">Intelligence:</span></p>
		'''
		
		result = apply_chapter_1_content_fixes(input_html)
		
		# H1 TOC entry should NOT have toc-subheader class
		self.assertNotIn('class="toc-subheader"><a href="#header-0-rolling-ability-scores"', result)
		
		# H2 TOC entries SHOULD have toc-subheader class
		self.assertIn('class="toc-subheader"><a href="#header-3-optional-methods"', result)
		self.assertIn('class="toc-subheader"><a href="#header-4-optional-method-i"', result)
		self.assertIn('class="toc-subheader"><a href="#header-10-intelligence"', result)


if __name__ == "__main__":
	unittest.main()

