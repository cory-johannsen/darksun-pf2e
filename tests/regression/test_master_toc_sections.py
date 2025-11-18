"""
Test that the master table of contents displays hierarchical section structure.

[TOC_DOCUMENT] The table of contents should show major sections (Rules Book, 
Wanderer's Journal, A Little Knowledge) with chapters nested underneath.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_master_toc_has_section_headers():
    """Test that the master TOC includes section headers."""
    toc_file = project_root / "data" / "html_output" / "table_of_contents.html"
    
    if not toc_file.exists():
        print(f"❌ FAILED: Master TOC file not found at {toc_file}")
        return False
    
    content = toc_file.read_text(encoding='utf-8')
    
    # Should have section headers
    has_rules_book = 'Rules Book' in content
    has_wanderers = "The Wanderer's Journal" in content or "Wanderer's Journal" in content
    has_little_knowledge = 'A Little Knowledge' in content
    
    if not has_rules_book:
        print("❌ FAILED: Missing 'Rules Book' section header")
        return False
    if not has_wanderers:
        print("❌ FAILED: Missing 'Wanderer's Journal' section header")
        return False
    if not has_little_knowledge:
        print("❌ FAILED: Missing 'A Little Knowledge' section header")
        return False
    
    print("✅ SUCCESS: All section headers present")
    return True


def test_master_toc_has_hierarchical_structure():
    """Test that chapters are grouped under section headers."""
    toc_file = project_root / "data" / "html_output" / "table_of_contents.html"
    
    if not toc_file.exists():
        print(f"❌ FAILED: Master TOC file not found")
        return False
    
    content = toc_file.read_text(encoding='utf-8')
    
    # Rules Book section should come before its chapters
    rules_book_pos = content.find('Rules Book')
    ability_scores_pos = content.find('Chapter One: Ability Scores')
    
    if rules_book_pos < 0:
        print("❌ FAILED: Rules Book section not found")
        return False
    if ability_scores_pos < 0:
        print("❌ FAILED: Chapter One: Ability Scores not found")
        return False
    if ability_scores_pos <= rules_book_pos:
        print("❌ FAILED: Chapter One: Ability Scores should come after Rules Book section")
        return False
    
    # Wanderer's Journal section should come before its chapters
    wanderers_pos = max(content.find("The Wanderer's Journal"), content.find("Wanderer's Journal"))
    world_of_athas_pos = content.find('The World Of Athas') 
    if world_of_athas_pos < 0:
        world_of_athas_pos = content.find('World Of Athas')
    
    if wanderers_pos < 0:
        print("❌ FAILED: Wanderer's Journal section not found")
        return False
    if world_of_athas_pos < 0:
        print("❌ FAILED: World of Athas chapter not found")
        return False
    if world_of_athas_pos <= wanderers_pos:
        print("❌ FAILED: World of Athas should come after Wanderer's Journal section")
        return False
    
    print("✅ SUCCESS: Hierarchical structure is correct")
    return True


def test_master_toc_section_order():
    """Test that sections appear in the correct order."""
    toc_file = project_root / "data" / "html_output" / "table_of_contents.html"
    
    if not toc_file.exists():
        print(f"❌ FAILED: Master TOC file not found")
        return False
    
    content = toc_file.read_text(encoding='utf-8')
    
    # Find positions of sections
    rules_book_pos = content.find('Rules Book')
    wanderers_pos = max(content.find("The Wanderer's Journal"), content.find("Wanderer's Journal"))
    little_knowledge_pos = content.find('A Little Knowledge')
    
    # All should exist
    if rules_book_pos < 0:
        print("❌ FAILED: Rules Book section not found")
        return False
    if wanderers_pos < 0:
        print("❌ FAILED: Wanderer's Journal section not found")
        return False
    if little_knowledge_pos < 0:
        print("❌ FAILED: A Little Knowledge section not found")
        return False
    
    # Should be in order
    if not (rules_book_pos < wanderers_pos):
        print("❌ FAILED: Rules Book should come before Wanderer's Journal")
        return False
    if not (wanderers_pos < little_knowledge_pos):
        print("❌ FAILED: Wanderer's Journal should come before A Little Knowledge")
        return False
    
    print("✅ SUCCESS: Sections are in correct order")
    return True


def test_master_toc_has_section_styling():
    """Test that sections have distinct styling from chapters."""
    toc_file = project_root / "data" / "html_output" / "table_of_contents.html"
    
    if not toc_file.exists():
        print(f"❌ FAILED: Master TOC file not found")
        return False
    
    content = toc_file.read_text(encoding='utf-8')
    
    # Should have CSS classes or elements that distinguish sections from chapters
    has_section_markers = (
        'class="section' in content.lower() or
        'class="toc-section' in content.lower() or
        '<h3>' in content or
        '<h2>' in content
    )
    
    if not has_section_markers:
        print("❌ FAILED: TOC should have distinct styling for section headers vs chapters")
        return False
    
    print("✅ SUCCESS: Section styling is present")
    return True


def test_master_toc_chapter_indentation():
    """Test that chapters are visually indented under their sections."""
    toc_file = project_root / "data" / "html_output" / "table_of_contents.html"
    
    if not toc_file.exists():
        print(f"❌ FAILED: Master TOC file not found")
        return False
    
    content = toc_file.read_text(encoding='utf-8')
    
    # Should have nested lists or CSS classes for indentation
    has_indentation = (
        '<ul>' in content and '</ul>' in content and content.count('<ul>') > 1
    ) or (
        'class="toc-chapter' in content.lower() or
        'style="margin-left' in content.lower() or
        'class="indented' in content.lower()
    )
    
    if not has_indentation:
        print("❌ FAILED: Chapters should be indented under their sections")
        return False
    
    print("✅ SUCCESS: Chapter indentation is present")
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("Testing Master TOC Section Structure")
    print("="*70 + "\n")
    
    tests = [
        ("Section Headers", test_master_toc_has_section_headers),
        ("Hierarchical Structure", test_master_toc_has_hierarchical_structure),
        ("Section Order", test_master_toc_section_order),
        ("Section Styling", test_master_toc_has_section_styling),
        ("Chapter Indentation", test_master_toc_chapter_indentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        print("-" * 70)
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

