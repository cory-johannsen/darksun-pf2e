"""Unit tests for Chapter 3 HTML postprocessing functions."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pytest
except ImportError:
    pytest = None

from tools.pdf_pipeline.postprocessors.chapter_3_postprocessing import (
    _reposition_rangers_followers_table,
    _remove_rangers_followers_duplicate_data
)


def test_reposition_rangers_followers_table_moves_table():
    """Test that the Rangers Followers table is moved to the correct position."""
    # Create sample HTML with table in wrong position
    html = """
    <p>The ranger answers that challenge.</p>
    <table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>
    <tr><td>01-04</td><td>Aarakocra</td></tr></table>
    <p>Other content here.</p>
    <p>To determine the type, consult the following table (rolling once for each follower).</p>
    <p>More content after.</p>
    """
    
    result = _reposition_rangers_followers_table(html)
    
    # Verify the table appears AFTER "consult the following table"
    consult_pos = result.find("consult the following table")
    table_pos = result.find('<table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>')
    
    assert consult_pos != -1, "Target sentence should be present"
    assert table_pos != -1, "Table should be present"
    assert table_pos > consult_pos, "Table should appear after the target sentence"


def test_reposition_rangers_followers_table_already_correct():
    """Test that function doesn't modify HTML if table is already in correct position."""
    # Create sample HTML with table already in correct position
    html = """
    <p>The ranger answers that challenge.</p>
    <p>Other content here.</p>
    <p>To determine the type, consult the following table (rolling once for each follower).</p>
    <table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>
    <tr><td>01-04</td><td>Aarakocra</td></tr></table>
    <p>More content after.</p>
    """
    
    result = _reposition_rangers_followers_table(html)
    
    # Verify the table still appears AFTER "consult the following table"
    consult_pos = result.find("consult the following table")
    table_pos = result.find('<table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>')
    
    assert table_pos > consult_pos, "Table should remain after the target sentence"


def test_reposition_rangers_followers_table_missing_table():
    """Test that function handles missing Rangers Followers table gracefully."""
    html = """
    <p>The ranger answers that challenge.</p>
    <p>To determine the type, consult the following table (rolling once for each follower).</p>
    """
    
    result = _reposition_rangers_followers_table(html)
    
    # Should return original HTML unchanged
    assert result == html


def test_reposition_rangers_followers_table_missing_target():
    """Test that function handles missing target sentence gracefully."""
    html = """
    <p>The ranger answers that challenge.</p>
    <table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>
    <tr><td>01-04</td><td>Aarakocra</td></tr></table>
    """
    
    result = _reposition_rangers_followers_table(html)
    
    # Should return original HTML unchanged
    assert result == html


def test_remove_rangers_followers_duplicate_data():
    """Test that duplicate data after Rangers Followers table is removed."""
    # Create HTML with duplicate/malformed data after the table
    html = """
    <p>To determine the type, consult the following table (rolling once for each follower).</p>
    <table class="ds-table"><tr><th>d100 Roll</th><th>Follower Type</th></tr>
    <tr><td>01-04</td><td>Aarakocra</td></tr>
    <tr><td>00</td><td>Other wilderness creature (chosen by the DM)</td></tr></table>
    <p>01-04</p>
    <p>Druid 32-35 Fighter (elf) 46-52 In all other ways, govern the creation and play of rangers as presented in thePlayers Handbook.</p>
    <p>Next section content.</p>
    """
    
    result = _remove_rangers_followers_duplicate_data(html)
    
    # Verify duplicate data is removed
    assert "<p>01-04</p>" not in result, "Leftover table fragment should be removed"
    assert "Druid 32-35 Fighter" not in result, "Mixed table data should be removed"
    
    # Verify valid content is preserved
    assert "In all other ways, govern the creation and play of rangers" in result, "Valid content should be preserved"
    assert "Next section content" in result, "Subsequent content should be preserved"


def test_remove_rangers_followers_duplicate_data_no_duplicates():
    """Test that function handles HTML without duplicate data gracefully."""
    # Create HTML without duplicate data
    html = """
    <table class="ds-table">
    <tr><td>00</td><td>Other wilderness creature (chosen by the DM)</td></tr></table>
    In all other ways, govern the creation and play of rangers as presented in thePlayers Handbook.
    """
    
    result = _remove_rangers_followers_duplicate_data(html)
    
    # Should return HTML unchanged (or with whitespace normalized)
    assert "In all other ways, govern the creation and play of rangers" in result


def test_remove_rangers_followers_duplicate_data_missing_markers():
    """Test that function handles missing markers gracefully."""
    html = """
    <p>Some other content without the Rangers Followers table.</p>
    """
    
    result = _remove_rangers_followers_duplicate_data(html)
    
    # Should return original HTML unchanged
    assert result == html


if __name__ == "__main__":
    # Run tests if executed directly
    import sys
    
    tests = [
        ("test_reposition_rangers_followers_table_moves_table", test_reposition_rangers_followers_table_moves_table),
        ("test_reposition_rangers_followers_table_already_correct", test_reposition_rangers_followers_table_already_correct),
        ("test_reposition_rangers_followers_table_missing_table", test_reposition_rangers_followers_table_missing_table),
        ("test_reposition_rangers_followers_table_missing_target", test_reposition_rangers_followers_table_missing_target),
        ("test_remove_rangers_followers_duplicate_data", test_remove_rangers_followers_duplicate_data),
        ("test_remove_rangers_followers_duplicate_data_no_duplicates", test_remove_rangers_followers_duplicate_data_no_duplicates),
        ("test_remove_rangers_followers_duplicate_data_missing_markers", test_remove_rangers_followers_duplicate_data_missing_markers),
    ]
    
    failed = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            test_func()
            print("✓ PASS")
        except AssertionError as e:
            print(f"✗ FAIL: {e}")
            failed.append(test_name)
        print()
    
    if failed:
        print(f"✗ {len(failed)} test(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("✓ All tests passed!")

