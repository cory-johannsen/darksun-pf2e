"""Unit tests for Chapter 5 (Proficiencies) HTML postprocessing."""

import pytest
from tools.pdf_pipeline.postprocessors.chapter_5_postprocessing import (
    apply_chapter_5_fixes,
    _split_intro_paragraphs,
    _split_weapon_proficiencies_section,
)


def test_split_intro_paragraphs_basic():
    """Test that intro content splits into 2 paragraphs at the correct marker."""
    html = '''<html>
<nav id="table-of-contents"><h2>TOC</h2></nav>
<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&amp;D® game mechanics appear in this chapter. Dark Sun characters often have higher attribute scores than those in other AD &amp; D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes. Even so, players should remember that rolling a natural 20 still results in failure, regardless of their characters' attribute scores.</p>
<p id="header-0-dark-sun-weapon-proficiencies">I. <span>Dark Sun Weapon Proficiencies</span></p>
</html>'''
    
    result = _split_intro_paragraphs(html)
    
    # Should have 2 separate paragraphs now
    assert result.count('<p>In Dark Sun, both weapon and nonweapon proficiencies') == 1
    assert result.count('<p>Dark Sun characters often have higher attribute scores') == 1
    
    # First paragraph should end at "this chapter."
    assert 'appear in this chapter.</p>' in result
    
    # Second paragraph should start with "Dark Sun characters often"
    assert '<p>Dark Sun characters often have higher attribute scores' in result


def test_split_intro_paragraphs_with_html_entities():
    """Test splitting works with HTML entities like &#x27; for apostrophes."""
    html = '''<nav id="table-of-contents"></nav>
<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player&#x27;s Handbook. Any exceptions to typical AD&amp;D® game mechanics appear in this chapter. Dark Sun characters often have higher attribute scores than those in other AD &amp; D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes. Even so, players should remember that rolling a natural 20 still results in failure, regardless of their characters&#x27; attribute scores.</p>'''
    
    result = _split_intro_paragraphs(html)
    
    # Should still split correctly despite HTML entities
    assert result.count('</p>') >= 2  # At least 2 paragraphs
    assert 'appear in this chapter.</p>' in result
    assert '<p>Dark Sun characters often' in result


def test_split_intro_paragraphs_no_nav():
    """Test splitting works even without a nav element."""
    html = '''<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&amp;D® game mechanics appear in this chapter. Dark Sun characters often have higher attribute scores than those in other AD &amp; D campaign worlds.</p>'''
    
    result = _split_intro_paragraphs(html)
    
    # Should split even without nav
    assert 'appear in this chapter.</p>' in result
    assert '<p>Dark Sun characters often' in result


def test_split_intro_paragraphs_already_split():
    """Test that already-split paragraphs are not modified."""
    html = '''<nav id="table-of-contents"></nav>
<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&amp;D® game mechanics appear in this chapter.</p>
<p>Dark Sun characters often have higher attribute scores than those in other AD &amp; D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes.</p>'''
    
    result = _split_intro_paragraphs(html)
    
    # Should remain essentially unchanged
    assert result.count('<p>In Dark Sun, both weapon and nonweapon') == 1
    assert result.count('<p>Dark Sun characters often') == 1


def test_apply_chapter_5_fixes_full():
    """Test the full chapter 5 fixes application."""
    html = '''<!DOCTYPE html>
<html>
<head><title>Chapter Five: Proficiencies</title></head>
<body>
<nav id="table-of-contents"><h2>Table of Contents</h2></nav>
<section class="content">
<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&amp;D® game mechanics appear in this chapter. Dark Sun characters often have higher attribute scores than those in other AD &amp; D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes. Even so, players should remember that rolling a natural 20 still results in failure, regardless of their characters' attribute scores.</p>
<p id="header-0-dark-sun-weapon-proficiencies">I. <span>Dark Sun Weapon Proficiencies</span></p>
<p>Weapon proficiencies and specialization function as usual for all Dark Sun character classes...</p>
</section>
</body>
</html>'''
    
    result = apply_chapter_5_fixes(html)
    
    # Verify the split occurred
    assert 'appear in this chapter.</p>' in result
    assert '<p>Dark Sun characters often have higher attribute scores' in result
    
    # Verify other content remains intact
    assert '<nav id="table-of-contents">' in result
    assert 'Dark Sun Weapon Proficiencies' in result
    assert 'Weapon proficiencies and specialization function as usual' in result


def test_split_intro_paragraphs_marker_not_found():
    """Test that missing marker doesn't break the function."""
    html = '''<nav id="table-of-contents"></nav>
<p>Some completely different content without the marker.</p>'''
    
    result = _split_intro_paragraphs(html)
    
    # Should return unchanged
    assert result == html


def test_split_weapon_proficiencies_basic():
    """Test that weapon proficiencies section splits into 3 paragraphs at the correct markers."""
    html = '''<html>
<p id="header-0-dark-sun-weapon-proficiencies">I. <span>Dark Sun Weapon Proficiencies</span></p>
<p>Weapon proficiencies and specialization function as usual for all Dark Sun character classes extent the gladiator class. Gladiators begin the game with proficiency in every weapon. In addition, they can specialize in any number of weapons, provided they have enough slots available to do so. A gladiator must spend two slots to specialize in any melee or missile weapon except a bow, which requires three slots. Gladiators thus transcend the rule that limits specialization to fighters. For example, Barlyuth, a dwarven gladiator, starts the game with four weapon proficiency slots. As a gladiator, he already holds proficiency in all weapons, so he needn't spend any of his four slots to become proficient. Instead, he may spend all four slots to specialize in two melee weapons, or spend three slots to specialize in a bow weapon and save the remaining slot for later specialization. A 9th-level gladiator could thus specialize in two melee weapons and one bow weapon (seven total weapon proficiency slots) and an 18th-level gladiator could specialize in five melee weapons (10 total weapon proficiency slots). A gladiator gains all the benefits for every weapon in which he specializes, suffering no penalty for multiple specializations.</p>
<p id="header-1-new-nonweapon-proficiencies">II. <span>New Nonweapon Proficiencies</span></p>
</html>'''
    
    result = _split_weapon_proficiencies_section(html)
    
    # Should have 3 separate paragraphs now
    assert result.count('<p>Weapon proficiencies and specialization function as usual') == 1
    assert result.count('<p>For example, Barlyuth') == 1
    assert result.count('<p>A 9th-level gladiator could thus') == 1
    
    # First paragraph should end at "fighters."
    assert 'limits specialization to fighters.</p>' in result
    
    # Second paragraph should start with "For example, Barlyuth"
    assert '<p>For example, Barlyuth' in result
    
    # Third paragraph should start with "A 9th-level gladiator"
    assert '<p>A 9th-level gladiator could thus' in result


def test_split_weapon_proficiencies_already_split():
    """Test that already-split weapon proficiencies paragraphs are not modified."""
    html = '''<p id="header-0-dark-sun-weapon-proficiencies">I. <span>Dark Sun Weapon Proficiencies</span></p>
<p>Weapon proficiencies and specialization function as usual for all Dark Sun character classes extent the gladiator class. Gladiators begin the game with proficiency in every weapon. In addition, they can specialize in any number of weapons, provided they have enough slots available to do so. A gladiator must spend two slots to specialize in any melee or missile weapon except a bow, which requires three slots. Gladiators thus transcend the rule that limits specialization to fighters.</p>
<p>For example, Barlyuth, a dwarven gladiator, starts the game with four weapon proficiency slots. As a gladiator, he already holds proficiency in all weapons, so he needn't spend any of his four slots to become proficient. Instead, he may spend all four slots to specialize in two melee weapons, or spend three slots to specialize in a bow weapon and save the remaining slot for later specialization.</p>
<p>A 9th-level gladiator could thus specialize in two melee weapons and one bow weapon (seven total weapon proficiency slots) and an 18th-level gladiator could specialize in five melee weapons (10 total weapon proficiency slots). A gladiator gains all the benefits for every weapon in which he specializes, suffering no penalty for multiple specializations.</p>
<p id="header-1-new-nonweapon-proficiencies">II. <span>New Nonweapon Proficiencies</span></p>'''
    
    result = _split_weapon_proficiencies_section(html)
    
    # Should remain essentially unchanged
    assert result.count('<p>Weapon proficiencies and specialization') == 1
    assert result.count('<p>For example, Barlyuth') == 1
    assert result.count('<p>A 9th-level gladiator') == 1


def test_apply_chapter_5_fixes_complete():
    """Test the full chapter 5 fixes application with both intro and weapon proficiencies."""
    html = '''<!DOCTYPE html>
<html>
<head><title>Chapter Five: Proficiencies</title></head>
<body>
<nav id="table-of-contents"><h2>Table of Contents</h2></nav>
<section class="content">
<p>In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&D® game mechanics appear in this chapter. Dark Sun characters often have higher attribute scores than those in other AD & D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes. Even so, players should remember that rolling a natural 20 still results in failure, regardless of their characters' attribute scores.</p>
<p id="header-0-dark-sun-weapon-proficiencies">I. <span>Dark Sun Weapon Proficiencies</span></p>
<p>Weapon proficiencies and specialization function as usual for all Dark Sun character classes extent the gladiator class. Gladiators begin the game with proficiency in every weapon. In addition, they can specialize in any number of weapons, provided they have enough slots available to do so. A gladiator must spend two slots to specialize in any melee or missile weapon except a bow, which requires three slots. Gladiators thus transcend the rule that limits specialization to fighters. For example, Barlyuth, a dwarven gladiator, starts the game with four weapon proficiency slots. As a gladiator, he already holds proficiency in all weapons, so he needn't spend any of his four slots to become proficient. Instead, he may spend all four slots to specialize in two melee weapons, or spend three slots to specialize in a bow weapon and save the remaining slot for later specialization. A 9th-level gladiator could thus specialize in two melee weapons and one bow weapon (seven total weapon proficiency slots) and an 18th-level gladiator could specialize in five melee weapons (10 total weapon proficiency slots). A gladiator gains all the benefits for every weapon in which he specializes, suffering no penalty for multiple specializations.</p>
<p id="header-1-new-nonweapon-proficiencies">II. <span>New Nonweapon Proficiencies</span></p>
</section>
</body>
</html>'''
    
    result = apply_chapter_5_fixes(html)
    
    # Verify intro split occurred
    assert 'appear in this chapter.</p>' in result
    assert '<p>Dark Sun characters often have higher attribute scores' in result
    
    # Verify weapon proficiencies split occurred
    assert 'limits specialization to fighters.</p>' in result
    assert '<p>For example, Barlyuth' in result
    assert '<p>A 9th-level gladiator could thus' in result
    
    # Verify other content remains intact
    assert '<nav id="table-of-contents">' in result
    assert 'Dark Sun Weapon Proficiencies' in result
    assert 'New Nonweapon Proficiencies' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

