"""Unit tests for header conversion utilities."""

import unittest
from tools.pdf_pipeline.utils.header_conversion import (
    convert_styled_p_to_semantic_header,
    convert_all_styled_headers_to_semantic,
)


class TestConvertStyledPToSemanticHeader(unittest.TestCase):
    """Test conversion of styled <p> tags to semantic headers."""
    
    def test_convert_h2_header_basic(self):
        """Test basic conversion of h2-header class to <h2> tag."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em">Test Header</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert '<h2 id="header-1-test">Test Header <a href="#top"' in result
        assert 'class="h2-header"' not in result
        assert '</h2>' in result
    
    def test_convert_h3_header(self):
        """Test conversion to <h3> tag."""
        html = '<p id="header-2-subtest" class="h3-header"><a href="#top">[^]</a> <span style="color: #cd490a;">Sub Header</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-subtest', 'h3')
        
        assert '<h3 id="header-2-subtest">Sub Header <a href="#top"' in result
        assert '</h3>' in result
    
    def test_convert_h4_header(self):
        """Test conversion to <h4> tag."""
        html = '<p id="header-3-tiny" class="h4-header"><a href="#top">[^]</a> <span>Tiny Header</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-tiny', 'h4')
        
        assert '<h4 id="header-3-tiny">Tiny Header <a href="#top"' in result
        assert '</h4>' in result
    
    def test_preserves_header_text_spacing(self):
        """Test that header text spacing is preserved correctly."""
        html = '<p id="header-1-multi-word" class="h2-header"><a href="#top">[^]</a> <span style="color: #cd490a;">Multi Word Header</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-multi-word', 'h2')
        
        assert 'Multi Word Header' in result
        assert 'MultiWordHeader' not in result  # No space removal
    
    def test_multiple_headers_same_pattern(self):
        """Test conversion of multiple headers with same pattern."""
        html = '''
        <p id="header-1-first" class="h2-header"><a href="#top">[^]</a> <span>First</span></p>
        <p id="header-2-second" class="h2-header"><a href="#top">[^]</a> <span>Second</span></p>
        '''
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-\w+', 'h2')
        
        assert '<h2 id="header-1-first">First' in result
        assert '<h2 id="header-2-second">Second' in result
        assert 'class="h2-header"' not in result
    
    def test_no_match_returns_unchanged(self):
        """Test that HTML without matching headers is unchanged."""
        html = '<p>Regular paragraph</p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert result == html
    
    def test_preserves_header_id(self):
        """Test that header IDs are preserved in conversion."""
        html = '<p id="header-5-ability-scores" class="h2-header"><a href="#top">[^]</a> <span>Ability Scores</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-ability-scores', 'h2')
        
        assert 'id="header-5-ability-scores"' in result
    
    def test_back_to_top_link_preserved(self):
        """Test that back-to-top [^] link is preserved."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span>Test</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert '[^]</a>' in result
        assert 'href="#top"' in result


class TestConvertAllStyledHeadersToSemantic(unittest.TestCase):
    """Test conversion of all header types at once."""
    
    def test_convert_mixed_header_levels(self):
        """Test conversion of h2, h3, and h4 headers in same HTML."""
        html = '''
        <p id="header-1-main" class="h2-header"><a href="#top">[^]</a> <span>Main</span></p>
        <p id="header-2-sub" class="h3-header"><a href="#top">[^]</a> <span>Sub</span></p>
        <p id="header-3-tiny" class="h4-header"><a href="#top">[^]</a> <span>Tiny</span></p>
        '''
        result = convert_all_styled_headers_to_semantic(html)
        
        assert '<h2 id="header-1-main">Main' in result
        assert '<h3 id="header-2-sub">Sub' in result
        assert '<h4 id="header-3-tiny">Tiny' in result
        assert 'class="h2-header"' not in result
        assert 'class="h3-header"' not in result
        assert 'class="h4-header"' not in result
    
    def test_convert_multiple_same_level(self):
        """Test conversion of multiple headers at the same level."""
        html = '''
        <p id="header-1-first" class="h2-header"><a href="#top">[^]</a> <span>First</span></p>
        <p>Some content</p>
        <p id="header-2-second" class="h2-header"><a href="#top">[^]</a> <span>Second</span></p>
        '''
        result = convert_all_styled_headers_to_semantic(html)
        
        assert '<h2 id="header-1-first">First' in result
        assert '<h2 id="header-2-second">Second' in result
        assert '<p>Some content</p>' in result  # Regular content preserved
    
    def test_empty_html(self):
        """Test that empty HTML is handled safely."""
        result = convert_all_styled_headers_to_semantic("")
        assert result == ""
    
    def test_no_headers_returns_unchanged(self):
        """Test that HTML without headers is unchanged."""
        html = '<p>Just a paragraph</p><div>And a div</div>'
        result = convert_all_styled_headers_to_semantic(html)
        assert result == html


class TestHeaderTextExtraction(unittest.TestCase):
    """Test that header text is correctly extracted from various formats."""
    
    def test_header_with_complex_styling(self):
        """Test extraction from headers with complex inline styles."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #cd490a; font-size: 0.9em; font-weight: bold;">Complex Header</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert '<h2 id="header-1-test">Complex Header' in result
    
    def test_header_with_special_characters(self):
        """Test headers containing special characters."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span>Header: With-Special_Characters!</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert 'Header: With-Special_Characters!' in result
    
    def test_header_with_numbers(self):
        """Test headers containing numbers."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span>Level 20 Abilities</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert 'Level 20 Abilities' in result


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_malformed_header_ignored(self):
        """Test that malformed headers are ignored safely."""
        html = '<p id="header-1-test" class="h2-header"><span>Missing link</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        # Should remain unchanged since it doesn't match the expected pattern
        assert 'class="h2-header"' in result
    
    def test_nested_tags_in_header(self):
        """Test headers with nested tags (should not occur but handle gracefully)."""
        html = '<p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span>Header <em>with</em> nesting</span></p>'
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        # Pattern should still extract the text including nested tags
        assert '<h2 id="header-1-test">' in result
    
    def test_preserves_surrounding_html(self):
        """Test that non-header HTML surrounding headers is preserved."""
        html = '''
        <div class="content">
            <p>Introduction paragraph</p>
            <p id="header-1-test" class="h2-header"><a href="#top">[^]</a> <span>Header</span></p>
            <p>Following paragraph</p>
        </div>
        '''
        result = convert_styled_p_to_semantic_header(html, r'header-\d+-test', 'h2')
        
        assert '<div class="content">' in result
        assert '<p>Introduction paragraph</p>' in result
        assert '<p>Following paragraph</p>' in result
        assert '<h2 id="header-1-test">Header' in result


if __name__ == '__main__':
    unittest.main()

