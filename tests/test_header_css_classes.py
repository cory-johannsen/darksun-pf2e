"""Unit tests for CSS class-based header level detection.

Tests the new semantic approach to header levels using CSS classes
instead of inline font-size attributes.
"""

import pytest
import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from pdf_pipeline.transformers.journal import _add_header_anchors, _build_toc


class TestHeaderCSSClasses:
    """Test header level detection using CSS classes."""
    
    def test_h1_header_gets_roman_numeral(self):
        """H1 headers (no class or class='header-h1') should get roman numerals."""
        html = '<p><span style="color: #ca5804">Test Header</span></p>'
        result = _add_header_anchors(html)
        
        # Should have roman numeral "I. "
        assert 'I.  <a href="#top"' in result
        assert 'Test Header' in result
        
    def test_h1_with_class_gets_roman_numeral(self):
        """H1 headers with explicit class='header-h1' should get roman numerals."""
        html = '<p><span class="header-h1">Test Header</span></p>'
        result = _add_header_anchors(html)
        
        # Should have roman numeral "I. "
        assert 'I.  <a href="#top"' in result
        assert 'Test Header' in result
    
    def test_h2_header_no_roman_numeral(self):
        """H2 headers should NOT get roman numerals."""
        html = '<p><span class="header-h2">Subheader</span></p>'
        result = _add_header_anchors(html)
        
        # Should NOT have roman numeral
        assert 'I.' not in result
        assert 'II.' not in result
        # Should still have back-to-top link
        assert '<a href="#top"' in result
        assert 'Subheader' in result
    
    def test_h3_header_no_roman_numeral(self):
        """H3 headers should NOT get roman numerals."""
        html = '<p><span class="header-h3">Sub-subheader</span></p>'
        result = _add_header_anchors(html)
        
        # Should NOT have roman numeral
        assert 'I.' not in result
        assert '<a href="#top"' in result
        assert 'Sub-subheader' in result
    
    def test_h4_header_no_roman_numeral(self):
        """H4 headers should NOT get roman numerals."""
        html = '<p><span class="header-h4">Smallest Header</span></p>'
        result = _add_header_anchors(html)
        
        # Should NOT have roman numeral
        assert 'I.' not in result
        assert '<a href="#top"' in result
        assert 'Smallest Header' in result
    
    def test_mixed_headers_correct_numbering(self):
        """Mixed H1 and H2 headers should only number H1s."""
        html = '''
        <p><span class="header-h1">First Main</span></p>
        <p><span class="header-h2">Sub One</span></p>
        <p><span class="header-h2">Sub Two</span></p>
        <p><span class="header-h1">Second Main</span></p>
        <p><span class="header-h3">Sub Sub</span></p>
        <p><span class="header-h1">Third Main</span></p>
        '''
        result = _add_header_anchors(html)
        
        # Should have exactly 3 roman numerals for the 3 H1 headers
        assert 'I.  <a href="#top"' in result
        assert 'II.  <a href="#top"' in result
        assert 'III.  <a href="#top"' in result
        # Should NOT have IV
        assert 'IV.' not in result
        
        # All headers should have back-to-top links
        assert result.count('<a href="#top"') == 6
    
    def test_backward_compatibility_no_class(self):
        """Headers without class should default to H1 (backward compatibility)."""
        html = '<p><span style="color: #ca5804">Legacy Header</span></p>'
        result = _add_header_anchors(html)
        
        # Should get roman numeral (treated as H1)
        assert 'I.  <a href="#top"' in result
        assert 'Legacy Header' in result
    
    def test_toc_generation_with_classes(self):
        """TOC should correctly categorize headers by CSS class."""
        html = '''
        <p id="header-1"><span class="header-h1">Main One</span></p>
        <p id="header-2"><span class="header-h2">Sub One</span></p>
        <p id="header-3"><span class="header-h3">SubSub One</span></p>
        <p id="header-4"><span class="header-h1">Main Two</span></p>
        '''
        
        toc = _build_toc(html)
        
        # H1 should not have toc-subheader class
        assert '<li><a href="#header-1">Main One</a></li>' in toc
        assert '<li><a href="#header-4">Main Two</a></li>' in toc
        
        # H2 should have toc-subheader class
        assert '<li class="toc-subheader"><a href="#header-2">Sub One</a></li>' in toc
        
        # H3 should have toc-subsubheader class
        assert '<li class="toc-subsubheader"><a href="#header-3">SubSub One</a></li>' in toc
    
    def test_css_class_preserved_after_anchor_addition(self):
        """CSS classes should be preserved when anchors are added."""
        html = '<p><span class="header-h2">Test</span></p>'
        result = _add_header_anchors(html)
        
        # Class should still be present
        assert 'class="header-h2"' in result
        assert 'Test' in result
    
    def test_inline_styles_preserved_with_classes(self):
        """Inline styles can coexist with CSS classes."""
        html = '<p><span class="header-h2" style="color: #ca5804; font-weight: bold;">Test</span></p>'
        result = _add_header_anchors(html)
        
        # Both class and style should be preserved
        assert 'class="header-h2"' in result
        assert 'style="color: #ca5804; font-weight: bold;"' in result
        assert 'Test' in result
        # Should NOT have roman numeral (it's H2)
        assert 'I.' not in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

