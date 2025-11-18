"""
Unit tests for Chapter 11 Monstrous Compendium 1&2 list extraction helpers.

Tests the refactored _extract_monstrous_compendium_list() and its helper functions.
"""

import pytest
from tools.pdf_pipeline.transformers.chapter_11_processing import (
    _find_monstrous_compendium_header,
    _is_section_header_block,
    _should_skip_mc12_block,
    _clean_ocr_spacing,
    _split_space_star_pattern,
    _split_camelcase_items,
    _merge_known_multiword_monsters,
    _split_camelcase_with_comma,
    _filter_non_mc12_items,
)


class TestFindMonstrousCompendiumHeader:
    """Test header finding logic."""
    
    def test_finds_header_on_page_80(self):
        """Should find MC1&2 header on page 80."""
        pages = [
            {"page_number": 80, "blocks": [
                {"type": "text", "bbox": [0, 100, 100, 110], "lines": [
                    {"spans": [{"text": "Monstrous Compendium 1 and 2"}]}
                ]}
            ]}
        ]
        page_idx, block_idx, y_pos = _find_monstrous_compendium_header(pages)
        assert page_idx == 0
        assert block_idx == 0
        assert y_pos == 100
    
    def test_returns_none_when_not_found(self):
        """Should return None when header not found."""
        pages = [{"page_number": 80, "blocks": []}]
        page_idx, block_idx, y_pos = _find_monstrous_compendium_header(pages)
        assert page_idx is None
        assert block_idx is None
        assert y_pos is None


class TestIsSectionHeaderBlock:
    """Test section header detection."""
    
    def test_detects_marked_h2_header(self):
        """Should detect blocks marked as H2 headers."""
        block = {"__render_as_h2": True}
        assert _is_section_header_block(block, "Any text")
    
    def test_detects_mc_realm_headers(self):
        """Should detect headers with MC markers and realm names."""
        block = {"lines": [{"spans": [{"color": "#000000", "size": 9}]}]}
        assert _is_section_header_block(block, "Forgotten Realms® (MC3)")
        assert _is_section_header_block(block, "Dragonlance® (MC4)")
    
    def test_detects_headers_by_color(self):
        """Should detect headers by special color."""
        block = {"lines": [{"spans": [{"color": "#ca5804", "size": 9}]}]}
        assert _is_section_header_block(block, "Some Header")
    
    def test_rejects_non_headers(self):
        """Should reject blocks that are not headers."""
        block = {"lines": [{"spans": [{"color": "#000000", "size": 9}]}]}
        assert not _is_section_header_block(block, "Regular text")


class TestShouldSkipMC12Block:
    """Test block skipping logic."""
    
    def test_preserves_section_headers(self):
        """Should not skip section headers."""
        block = {"__render_as_h2": True}
        assert not _should_skip_mc12_block(block, "Forgotten Realms® (MC3)")
    
    def test_skips_known_non_mc12_content(self):
        """Should skip known non-MC1&2 content."""
        block = {"lines": [{"spans": [{"color": "#000000", "size": 9}]}]}
        assert _should_skip_mc12_block(block, "indicates possible psionic")
        assert _should_skip_mc12_block(block, "SPELLJAMMER")
        assert _should_skip_mc12_block(block, "Thessalmonster")
    
    def test_allows_mc12_content(self):
        """Should allow MC1&2 monster names."""
        block = {"lines": [{"spans": [{"color": "#000000", "size": 9}]}]}
        assert not _should_skip_mc12_block(block, "Aarakocra")
        assert not _should_skip_mc12_block(block, "Beetle")


class TestCleanOCRSpacing:
    """Test OCR spacing cleanup."""
    
    def test_fixes_single_letter_spacing(self):
        """Should fix 'A n t' -> 'Ant'."""
        assert _clean_ocr_spacing("A n t") == "Ant"
        assert _clean_ocr_spacing("B e h i r") == "Behir"
        assert _clean_ocr_spacing("R o t") == "Rot"
    
    def test_preserves_proper_two_word_names(self):
        """Should preserve 'Aerial Servant' as-is."""
        assert _clean_ocr_spacing("Aerial Servant") == "Aerial Servant"
        assert _clean_ocr_spacing("Giant Ant") == "Giant Ant"
    
    def test_handles_single_words(self):
        """Should return single words unchanged."""
        assert _clean_ocr_spacing("Aarakocra") == "Aarakocra"


class TestSplitSpaceStarPattern:
    """Test splitting on space-asterisk pattern."""
    
    def test_splits_on_space_asterisk(self):
        """Should split 'Aarakocra *Behir' into two items."""
        result = _split_space_star_pattern("Aarakocra *Behir")
        assert len(result) == 2
        assert "Aarakocra*" in result  # Asterisk attached to previous item, space removed
        assert "Behir" in result
    
    def test_preserves_asterisks(self):
        """Should keep asterisks with their items."""
        result = _split_space_star_pattern("Monster *Another")
        assert any("*" in item for item in result)
    
    def test_returns_single_item_when_no_split(self):
        """Should return single item when no space-asterisk pattern."""
        result = _split_space_star_pattern("Aarakocra")
        assert result == ["Aarakocra"]


class TestSplitCamelCaseItems:
    """Test CamelCase splitting."""
    
    def test_splits_camelcase(self):
        """Should split 'BeetleBehir' into ['Beetle', 'Behir']."""
        result = _split_camelcase_items(["BeetleBehir"])
        assert "Beetle" in result
        assert "Behir" in result
    
    def test_preserves_spaced_names(self):
        """Should preserve names with spaces."""
        result = _split_camelcase_items(["Aerial Servant"])
        assert result == ["Aerial Servant"]
    
    def test_handles_long_concatenated_items(self):
        """Should split very long concatenated items."""
        result = _split_camelcase_items(["BuletteCatsCentipede"])
        assert len(result) >= 3


class TestMergeKnownMultiwordMonsters:
    """Test merging known two-word monster names."""
    
    def test_merges_aerial_servant(self):
        """Should merge 'Aerial' + 'Servant' -> 'Aerial Servant'."""
        result = _merge_known_multiword_monsters(["Aerial", "Servant", "Beetle"])
        assert "Aerial Servant" in result
        assert "Beetle" in result
        assert len(result) == 2
    
    def test_leaves_other_items_unchanged(self):
        """Should not merge other adjacent items."""
        result = _merge_known_multiword_monsters(["Ant", "Beetle", "Cat"])
        assert result == ["Ant", "Beetle", "Cat"]


class TestSplitCamelCaseWithComma:
    """Test splitting CamelCase items that have commas."""
    
    def test_splits_camelcase_with_comma(self):
        """Should split 'BuletteCats, Great' into ['Bulette', 'Cats, Great']."""
        result = _split_camelcase_with_comma(["BuletteCats, Great"])
        assert len(result) == 2
        assert "Bulette" in result
        assert "Cats, Great" in result
    
    def test_preserves_items_without_comma(self):
        """Should leave items without commas unchanged."""
        result = _split_camelcase_with_comma(["Beetle", "Cat"])
        assert result == ["Beetle", "Cat"]


class TestFilterNonMC12Items:
    """Test filtering out non-MC1&2 items."""
    
    def test_filters_other_compendium_sections(self):
        """Should filter out MC3, MC4, etc."""
        items = ["Beetle", "Forgotten Realms", "Cat", "MC3", "Ant"]
        result = _filter_non_mc12_items(items)
        assert "Beetle" in result
        assert "Cat" in result
        assert "Ant" in result
        assert "Forgotten Realms" not in result
        assert "MC3" not in result
    
    def test_filters_specific_monsters(self):
        """Should filter out Meazel, Dragonlance monsters, etc."""
        items = ["Beetle", "Meazel", "Ant"]
        result = _filter_non_mc12_items(items)
        assert "Beetle" in result
        assert "Ant" in result
        assert "Meazel" not in result
    
    def test_filters_short_items(self):
        """Should filter out very short items."""
        items = ["Beetle", "a", "Cat", "B"]
        result = _filter_non_mc12_items(items)
        assert "Beetle" in result
        assert "Cat" in result
        assert "a" not in result
        assert "B" not in result

