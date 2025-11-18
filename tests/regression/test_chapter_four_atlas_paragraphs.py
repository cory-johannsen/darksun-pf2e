"""
Regression Test: Chapter Four Atlas Paragraph Breaks

This test verifies that Chapter Four: Atlas of the Tyr Region has proper
paragraph breaks at the user-specified locations.

Test Sections:
1. Main intro: 5 paragraphs with breaks at specific phrases
2. Cities section: 2 paragraphs
3. Balic section: 7 paragraphs
4. Draj section: 9 paragraphs
5. Gulg section: 8 paragraphs
6. Nibenay section: 7 paragraphs
7. Raam section: 6 paragraphs
8. Tyr section: 8 paragraphs
9. Urik section: 9 paragraphs (first 3 in blockquote)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup


def test_chapter_four_atlas_paragraph_breaks():
    """Test that Chapter Four: Atlas has proper paragraph breaks."""
    
    html_file = project_root / "data" / "html_output" / "chapter-four-atlas-of-the-tyr-region.html"
    
    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Track all test results
    all_tests_passed = True
    
    # Test 1: Main intro section (before "Cities" header) - 5 paragraphs
    print("\n📋 Test 1: Main Intro Section (5 paragraphs)")
    cities_header = soup.find('p', id='header-0-cities')
    if not cities_header:
        print("❌ Could not find Cities header")
        all_tests_passed = False
    else:
        # Get all <p> tags before the Cities header
        intro_paragraphs = []
        for elem in soup.find_all('p'):
            if elem == cities_header:
                break
            # Skip TOC link paragraphs
            if 'back-to-master-toc' not in elem.get('class', []):
                intro_paragraphs.append(elem)
        
        expected_intro_paragraphs = 5
        actual_intro_paragraphs = len(intro_paragraphs)
        
        if actual_intro_paragraphs == expected_intro_paragraphs:
            print(f"✅ Main intro has {actual_intro_paragraphs} paragraphs (expected {expected_intro_paragraphs})")
            
            # Verify each break point exists at the START of a paragraph
            expected_breaks = [
                "That won't",
                "Despite these",
                "In honor of",
                "The Tyr region"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in intro_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Main intro has {actual_intro_paragraphs} paragraphs (expected {expected_intro_paragraphs})")
            all_tests_passed = False
    
    # Test 2: Cities section - 2 paragraphs
    print("\n📋 Test 2: Cities Section (2 paragraphs)")
    balic_header = soup.find('p', id='header-1-balic')
    if cities_header and balic_header:
        cities_paragraphs = []
        found_cities = False
        for elem in soup.find_all('p'):
            if elem == cities_header:
                found_cities = True
                continue
            if found_cities and elem == balic_header:
                break
            if found_cities and elem.get('id') != cities_header.get('id'):
                cities_paragraphs.append(elem)
        
        expected_cities_paragraphs = 2
        actual_cities_paragraphs = len(cities_paragraphs)
        
        if actual_cities_paragraphs == expected_cities_paragraphs:
            print(f"✅ Cities section has {actual_cities_paragraphs} paragraphs (expected {expected_cities_paragraphs})")
            
            # Verify the break point
            found_break = False
            for para in cities_paragraphs:
                if para.get_text().strip().startswith("Of course,"):
                    found_break = True
                    print(f"  ✅ Found paragraph starting with: 'Of course,'")
                    break
            if not found_break:
                print(f"  ❌ No paragraph starts with: 'Of course,'")
                all_tests_passed = False
        else:
            print(f"❌ Cities section has {actual_cities_paragraphs} paragraphs (expected {expected_cities_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Cities or Balic headers")
        all_tests_passed = False
    
    # Test 3: Balic section - 7 paragraphs
    print("\n📋 Test 3: Balic Section (7 paragraphs)")
    draj_header = soup.find('p', id='header-2-draj')
    if balic_header and draj_header:
        balic_paragraphs = []
        found_balic = False
        for elem in soup.find_all('p'):
            if elem == balic_header:
                found_balic = True
                continue
            if found_balic and elem == draj_header:
                break
            if found_balic and elem.get('id') != balic_header.get('id'):
                balic_paragraphs.append(elem)
        
        expected_balic_paragraphs = 7
        actual_balic_paragraphs = len(balic_paragraphs)
        
        if actual_balic_paragraphs == expected_balic_paragraphs:
            print(f"✅ Balic section has {actual_balic_paragraphs} paragraphs (expected {expected_balic_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "On the rare",
                "Andropinis lives",
                "Balic's templars",
                "The nobles of",
                "Balic's Merchant",
                "Balic's secluded"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in balic_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Balic section has {actual_balic_paragraphs} paragraphs (expected {expected_balic_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Balic or Draj headers")
        all_tests_passed = False
    
    # Test 4: Draj section - 9 paragraphs (8 breaks + 1 initial = 9 total)
    print("\n📋 Test 4: Draj Section (9 paragraphs)")
    gulg_header = soup.find('p', id='header-3-gulg')
    if draj_header and gulg_header:
        draj_paragraphs = []
        found_draj = False
        for elem in soup.find_all('p'):
            if elem == draj_header:
                found_draj = True
                continue
            if found_draj and elem == gulg_header:
                break
            if found_draj and elem.get('id') != draj_header.get('id'):
                draj_paragraphs.append(elem)
        
        expected_draj_paragraphs = 9
        actual_draj_paragraphs = len(draj_paragraphs)
        
        if actual_draj_paragraphs == expected_draj_paragraphs:
            print(f"✅ Draj section has {actual_draj_paragraphs} paragraphs (expected {expected_draj_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "Be that as",
                "No one seems",
                "This last claim",
                "Because Draj",
                "Nevertheless,",
                "Captives are",
                "On a day",
                "Despite its warlike"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in draj_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Draj section has {actual_draj_paragraphs} paragraphs (expected {expected_draj_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Draj or Gulg headers")
        all_tests_passed = False
    
    # Test 5: Gulg section - 8 paragraphs
    print("\n📋 Test 5: Gulg Section (8 paragraphs)")
    nibenay_header = soup.find('p', id='header-4-nibenay')
    if gulg_header and nibenay_header:
        gulg_paragraphs = []
        found_gulg = False
        for elem in soup.find_all('p'):
            if elem == gulg_header:
                found_gulg = True
                continue
            if found_gulg and elem == nibenay_header:
                break
            if found_gulg and elem.get('id') != gulg_header.get('id'):
                gulg_paragraphs.append(elem)
        
        expected_gulg_paragraphs = 8
        actual_gulg_paragraphs = len(gulg_paragraphs)
        
        if actual_gulg_paragraphs == expected_gulg_paragraphs:
            print(f"✅ Gulg section has {actual_gulg_paragraphs} paragraphs (expected {expected_gulg_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "Lalali-Puy is perhaps",
                "Gulg is not",
                "While most of",
                "Her templars,",
                "In Gulg,",
                "Like all property",  # Note: user had ":ike" which is probably a typo
                "The warriors of"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in gulg_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Gulg section has {actual_gulg_paragraphs} paragraphs (expected {expected_gulg_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Gulg or Nibenay headers")
        all_tests_passed = False
    
    # Test 6: Nibenay section - 7 paragraphs
    print("\n📋 Test 6: Nibenay Section (7 paragraphs)")
    raam_header = soup.find('p', id='header-5-raam')
    if nibenay_header and raam_header:
        nibenay_paragraphs = []
        found_nibenay = False
        for elem in soup.find_all('p'):
            if elem == nibenay_header:
                found_nibenay = True
                continue
            if found_nibenay and elem == raam_header:
                break
            if found_nibenay and elem.get('id') != nibenay_header.get('id'):
                nibenay_paragraphs.append(elem)
        
        expected_nibenay_paragraphs = 7
        actual_nibenay_paragraphs = len(nibenay_paragraphs)
        
        if actual_nibenay_paragraphs == expected_nibenay_paragraphs:
            print(f"✅ Nibenay section has {actual_nibenay_paragraphs} paragraphs (expected {expected_nibenay_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "The Shadow King lives",
                "Nibenay's templars are",
                "This is completely",
                "Nibenay sits",
                "Nibenay's merchant trade",
                "The core of"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in nibenay_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Nibenay section has {actual_nibenay_paragraphs} paragraphs (expected {expected_nibenay_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Nibenay or Raam headers")
        all_tests_passed = False
    
    # Test 7: Raam section - 6 paragraphs
    print("\n📋 Test 7: Raam Section (6 paragraphs)")
    tyr_header = soup.find('p', id='header-6-t-y-r')
    if raam_header and tyr_header:
        raam_paragraphs = []
        found_raam = False
        for elem in soup.find_all('p'):
            if elem == raam_header:
                found_raam = True
                continue
            if found_raam and elem == tyr_header:
                break
            if found_raam and elem.get('id') != raam_header.get('id'):
                raam_paragraphs.append(elem)
        
        expected_raam_paragraphs = 6
        actual_raam_paragraphs = len(raam_paragraphs)
        
        if actual_raam_paragraphs == expected_raam_paragraphs:
            print(f"✅ Raam section has {actual_raam_paragraphs} paragraphs (expected {expected_raam_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "Abalach-Re professes",
                "This is one of",
                "As a consequence",
                "Of course,",
                "The only thing"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in raam_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Raam section has {actual_raam_paragraphs} paragraphs (expected {expected_raam_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Raam or Tyr headers")
        all_tests_passed = False
    
    # Test 8: Tyr section - 8 paragraphs
    print("\n📋 Test 8: Tyr Section (8 paragraphs)")
    urik_header = soup.find('p', id='header-7-urik')
    if tyr_header and urik_header:
        tyr_paragraphs = []
        found_tyr = False
        for elem in soup.find_all('p'):
            if elem == tyr_header:
                found_tyr = True
                continue
            if found_tyr and elem == urik_header:
                break
            if found_tyr and elem.get('id') != tyr_header.get('id'):
                tyr_paragraphs.append(elem)
        
        expected_tyr_paragraphs = 8
        actual_tyr_paragraphs = len(tyr_paragraphs)
        
        if actual_tyr_paragraphs == expected_tyr_paragraphs:
            print(f"✅ Tyr section has {actual_tyr_paragraphs} paragraphs (expected {expected_tyr_paragraphs})")
            
            # Verify break points
            expected_breaks = [
                "If Kalak's",
                "The Tyrant of Tyr",
                "Of late,",
                "Kalak has also",
                "To make matters",
                "Can it be",
                "When the final battle"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in tyr_paragraphs:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Tyr section has {actual_tyr_paragraphs} paragraphs (expected {expected_tyr_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Tyr or Urik headers")
        all_tests_passed = False
    
    # Test 9: Urik section - 9 paragraphs (first 3 in blockquote)
    print("\n📋 Test 9: Urik Section (9 paragraphs with blockquote)")
    villages_header = soup.find('p', id='header-8-villages')
    if urik_header and villages_header:
        # For Urik, we need to count both blockquote paragraphs and regular paragraphs
        urik_content = []
        found_urik = False
        for elem in soup.find_all(['p', 'blockquote']):
            if elem.name == 'p' and elem == urik_header:
                found_urik = True
                continue
            if found_urik and elem.name == 'p' and elem == villages_header:
                break
            if found_urik and elem.get('id') != urik_header.get('id'):
                if elem.name == 'blockquote':
                    # Count paragraphs inside the blockquote
                    blockquote_paras = elem.find_all('p')
                    urik_content.extend(blockquote_paras)
                elif elem.name == 'p':
                    # Skip paragraphs that are inside a blockquote (already counted)
                    if not elem.find_parent('blockquote'):
                        urik_content.append(elem)
        
        expected_urik_paragraphs = 9
        actual_urik_paragraphs = len(urik_content)
        
        if actual_urik_paragraphs == expected_urik_paragraphs:
            print(f"✅ Urik section has {actual_urik_paragraphs} paragraphs (expected {expected_urik_paragraphs})")
            
            # Verify blockquote exists and contains first 3 paragraphs
            blockquote = soup.find('blockquote')
            if blockquote:
                blockquote_paras = blockquote.find_all('p')
                if len(blockquote_paras) == 3:
                    print(f"  ✅ Found blockquote with 3 paragraphs")
                    # Check if they're italicized
                    has_italic = all(para.find('em') is not None for para in blockquote_paras)
                    if has_italic:
                        print(f"  ✅ Blockquote paragraphs are italicized")
                    else:
                        print(f"  ❌ Blockquote paragraphs are not italicized")
                        all_tests_passed = False
                else:
                    print(f"  ❌ Blockquote has {len(blockquote_paras)} paragraphs (expected 3)")
                    all_tests_passed = False
            else:
                print(f"  ❌ No blockquote found")
                all_tests_passed = False
            
            # Verify break points
            expected_breaks = [
                "I am Hamanu, King",
                "The Great Spirits",
                "I am Hamanu of",
                "As you",
                "Hamanu's palace",
                "One of the most",
                "Urik's economy",
                "As a final note"
            ]
            
            for break_phrase in expected_breaks:
                found = False
                for para in urik_content:
                    text = para.get_text()
                    if text.strip().startswith(break_phrase):
                        found = True
                        print(f"  ✅ Found paragraph starting with: '{break_phrase}'")
                        break
                if not found:
                    print(f"  ❌ No paragraph starts with: '{break_phrase}'")
                    all_tests_passed = False
        else:
            print(f"❌ Urik section has {actual_urik_paragraphs} paragraphs (expected {expected_urik_paragraphs})")
            all_tests_passed = False
    else:
        print("❌ Could not locate Urik or Villages headers")
        all_tests_passed = False
    
    # Final result
    print("\n" + "="*60)
    if all_tests_passed:
        print("🏆 ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False


if __name__ == '__main__':
    success = test_chapter_four_atlas_paragraph_breaks()
    sys.exit(0 if success else 1)

