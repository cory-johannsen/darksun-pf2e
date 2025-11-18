"""
Unit tests for Chapter 11 postprocessing.

Tests the chapter_11_postprocessing module which applies H2 styling
to Magic, Psionics, and Plant-Based Monsters headers.
"""

from tools.pdf_pipeline.postprocessors.chapter_11_postprocessing import (
    apply_chapter_11_content_fixes,
    _apply_header_styling,
    _fix_toc_indentation,
    _fix_roman_numerals,
)


def test_apply_header_styling():
    """Test that H2 styling is applied to Magic, Psionics, and Plant-Based Monsters."""
    html = '''
    <p id="header-3-magic">IV.  <a href="#top">[^]</a> <span style="color: #ca5804">Magic:</span></p>
    <p id="header-4-psionics">V.  <a href="#top">[^]</a> <span style="color: #ca5804">Psionics:</span></p>
    <p id="header-5-plant-based-monsters">VI.  <a href="#top">[^]</a> <span style="color: #ca5804">Plant-Based Monsters:</span></p>
    '''
    
    result = _apply_header_styling(html)
    
    # Check that h2-header class is added
    assert 'class="h2-header"' in result
    assert '<p id="header-3-magic" class="h2-header">' in result
    assert '<p id="header-4-psionics" class="h2-header">' in result
    assert '<p id="header-5-plant-based-monsters" class="h2-header">' in result
    
    # Check that Roman numerals are removed from H2 headers
    assert 'IV.  <a href="#top">[^]</a> <span' not in result
    assert 'V.  <a href="#top">[^]</a> <span' not in result
    assert 'VI.  <a href="#top">[^]</a> <span' not in result
    
    # Check that font-size is added to spans
    assert 'font-size: 0.9em' in result


def test_fix_toc_indentation():
    """Test that TOC entries for H2 headers get proper indentation."""
    html = '''
    <nav id="table-of-contents">
    <ul>
    <li><a href="#header-2-monsters">Monsters</a></li>
    <li><a href="#header-3-magic">Magic:</a></li>
    <li><a href="#header-4-psionics">Psionics:</a></li>
    <li><a href="#header-5-plant-based-monsters">Plant-Based Monsters:</a></li>
    <li><a href="#header-6-monstrous-compendium-1-and-2">Monstrous Compendium 1 and 2</a></li>
    </ul>
    </nav>
    '''
    
    result = _fix_toc_indentation(html)
    
    # Check that H2 entries have toc-subheader class
    assert '<li class="toc-subheader"><a href="#header-3-magic">' in result
    assert '<li class="toc-subheader"><a href="#header-4-psionics">' in result
    assert '<li class="toc-subheader"><a href="#header-5-plant-based-monsters">' in result
    
    # Check that H1 entries do NOT have toc-subheader class
    assert '<li><a href="#header-2-monsters">' in result
    assert '<li><a href="#header-6-monstrous-compendium-1-and-2">' in result


def test_fix_roman_numerals():
    """Test that Roman numerals are renumbered after H2 headers."""
    html = '''
    <p id="header-6-monstrous-compendium-1-and-2">VII.  <a href="#top">[^]</a></p>
    <p id="header-7-greyhawk®-mc5">VIII.  <a href="#top">[^]</a></p>
    <p id="header-8-kara-tur-mc6">IX.  <a href="#top">[^]</a></p>
    <p id="header-9-wilderness-encounters">X.  <a href="#top">[^]</a></p>
    <p id="header-10-stoney-barrens">XI.  <a href="#top">[^]</a></p>
    <p id="header-11-sandy-wastes">XII.  <a href="#top">[^]</a></p>
    '''
    
    result = _fix_roman_numerals(html)
    
    # Check that Roman numerals are updated
    assert '<p id="header-6-monstrous-compendium-1-and-2">IV.' in result
    assert '<p id="header-7-greyhawk®-mc5">V.' in result
    assert '<p id="header-8-kara-tur-mc6">VI.' in result
    assert '<p id="header-9-wilderness-encounters">VII.' in result
    assert '<p id="header-10-stoney-barrens">VIII.' in result
    assert '<p id="header-11-sandy-wastes">IX.' in result


def test_apply_chapter_11_content_fixes_integration():
    """Test the full chapter 11 content fixes pipeline."""
    html = '''
    <nav id="table-of-contents">
    <ul>
    <li><a href="#header-2-monsters">Monsters</a></li>
    <li><a href="#header-3-magic">Magic:</a></li>
    <li><a href="#header-4-psionics">Psionics:</a></li>
    <li><a href="#header-5-plant-based-monsters">Plant-Based Monsters:</a></li>
    <li><a href="#header-6-monstrous-compendium-1-and-2">Monstrous Compendium 1 and 2</a></li>
    </ul>
    </nav>
    <p id="header-2-monsters">III.  <a href="#top">[^]</a> <span style="color: #ca5804">Monsters</span></p>
    <p id="header-3-magic">IV.  <a href="#top">[^]</a> <span style="color: #ca5804">Magic:</span></p>
    <p id="header-4-psionics">V.  <a href="#top">[^]</a> <span style="color: #ca5804">Psionics:</span></p>
    <p id="header-5-plant-based-monsters">VI.  <a href="#top">[^]</a> <span style="color: #ca5804">Plant-Based Monsters:</span></p>
    <p id="header-6-monstrous-compendium-1-and-2">VII.  <a href="#top">[^]</a> <span style="color: #ca5804">Monstrous Compendium 1 and 2</span></p>
    '''
    
    result = apply_chapter_11_content_fixes(html)
    
    # Verify H2 styling is applied
    assert '<p id="header-3-magic" class="h2-header">' in result
    assert '<p id="header-4-psionics" class="h2-header">' in result
    assert '<p id="header-5-plant-based-monsters" class="h2-header">' in result
    
    # Verify H2 headers have no Roman numerals (check specifically on H2 headers)
    assert '<p id="header-3-magic" class="h2-header">IV.' not in result
    assert '<p id="header-4-psionics" class="h2-header">V.' not in result
    assert '<p id="header-5-plant-based-monsters" class="h2-header">VI.' not in result
    
    # Verify H1 headers keep their Roman numerals but are renumbered
    assert '<p id="header-2-monsters">III.' in result  # Unchanged
    assert '<p id="header-6-monstrous-compendium-1-and-2">IV.' in result  # Was VII
    
    # Verify TOC indentation
    assert '<li class="toc-subheader"><a href="#header-3-magic">' in result
    assert '<li class="toc-subheader"><a href="#header-4-psionics">' in result
    assert '<li class="toc-subheader"><a href="#header-5-plant-based-monsters">' in result
    
    # Verify H1 TOC entries remain unchanged
    assert '<li><a href="#header-2-monsters">' in result
    assert '<li><a href="#header-6-monstrous-compendium-1-and-2">' in result


def test_empty_html():
    """Test that empty HTML doesn't cause errors."""
    html = ""
    result = apply_chapter_11_content_fixes(html)
    assert result == ""


def test_html_without_target_headers():
    """Test that HTML without target headers passes through unchanged."""
    html = '<p>Some random content</p>'
    result = apply_chapter_11_content_fixes(html)
    assert result == html


if __name__ == "__main__":
    """Run all tests."""
    tests = [
        test_apply_header_styling,
        test_fix_toc_indentation,
        test_fix_roman_numerals,
        test_apply_chapter_11_content_fixes_integration,
        test_empty_html,
        test_html_without_target_headers,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Tests: {passed} passed, {failed} failed")
    print("=" * 80)
    
    import sys
    sys.exit(0 if failed == 0 else 1)


