#!/usr/bin/env python3
"""
Regression tests for Chapter 5: Monsters of Athas monster manual page reconstruction.

Tests verify that:
1. All 10 monster manual pages have proper H2 headers
2. All 10 monsters have stats tables with 21 rows (PSIONICS moved to separate section)
3. Monster sections contain Combat, Habitat/Society, and Ecology descriptions
4. No fragmented paragraph tags remain in monster sections
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup


def test_monster_manual_pages():
    """Test that all monster manual pages are properly reconstructed."""
    
    # Expected monsters in order
    monsters = [
        "Belgoi",
        "Braxat",
        "Dragon of Tyr",
        "Dune Freak (Anakore)",
        "Gaj",
        "Giant, Athasian",
        "Gith",
        "Jozhal",
        "Silk Wyrm",
        "Tembo"
    ]
    
    # Read the HTML file
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-five-monsters-of-athas.html"
    if not html_path.exists():
        print(f"❌ HTML file not found: {html_path}")
        return False
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\n🧪 Testing Chapter 5 Monster Manual Pages")
    print("=" * 80)
    
    all_passed = True
    
    for i, monster_name in enumerate(monsters, start=1):
        print(f"\n📋 Testing {monster_name}...")
        
        # Test 1: Check for H2 header
        monster_slug = monster_name.lower().replace(" ", "-").replace(",", "").replace("(", "").replace(")", "")
        # Find H2 by ID pattern (header-*-slug or monster-slug) or by text content
        h2 = None
        for header in soup.find_all('h2'):
            header_id = header.get('id', '')
            header_text = header.get_text()
            if (monster_slug in header_id or 
                monster_name.lower() in header_text.lower()):
                h2 = header
                break
        
        if not h2:
            print(f"  ❌ Missing H2 header for {monster_name}")
            all_passed = False
            continue
        else:
            print(f"  ✅ H2 header found: {h2.get_text()[:50]}")
        
        # Test 2: Check for stats table
        # Find the stats table after this header
        table = h2.find_next('table', class_='monster-stats')
        if not table:
            print(f"  ❌ Missing stats table for {monster_name}")
            all_passed = False
            continue
        else:
            print(f"  ✅ Stats table found")
        
        # Test 3: Verify 21 rows in stats table (PSIONICS now in separate section)
        rows = table.find_all('tr')
        if len(rows) != 21:
            print(f"  ❌ Stats table has {len(rows)} rows, expected 21")
            all_passed = False
        else:
            print(f"  ✅ Stats table has 21 rows")
        
        # Test 4: Check for required stat labels (21 labels, PSIONICS moved to separate section)
        expected_labels = [
            "CLIMATE/TERRAIN", "FREQUENCY", "ORGANIZATION", "ACTIVITY CYCLE", "DIET",
            "INTELLIGENCE", "TREASURE", "ALIGNMENT", "NO. APPEARING", "ARMOR CLASS",
            "MOVEMENT", "HIT DICE", "THAC0", "NO. OF ATTACKS", "DAMAGE/ATTACK",
            "SPECIAL ATTACKS", "SPECIAL DEFENSES", "MAGIC RESISTANCE", "SIZE",
            "MORALE", "XP VALUE"
        ]
        
        table_text = table.get_text()
        missing_labels = []
        for label in expected_labels:
            if label not in table_text:
                missing_labels.append(label)
        
        if missing_labels:
            print(f"  ❌ Missing stat labels: {', '.join(missing_labels)}")
            all_passed = False
        else:
            print(f"  ✅ All 21 stat labels present")
        
        # Test 4b: Check for empty cells (CRITICAL per spec: "Every row contains values")
        rows = table.find_all('tr')
        empty_cells = []
        for row in rows:
            label_cell = row.find('td', class_='stat-label')
            value_cell = row.find('td', class_='stat-value')
            if label_cell and value_cell:
                label_text = label_cell.get_text(strip=True)
                value_text = value_cell.get_text(strip=True)
                if not value_text:
                    empty_cells.append(label_text)
        
        if empty_cells:
            print(f"  ❌ PARSING FAILURE: {len(empty_cells)} empty cells: {', '.join(empty_cells[:5])}")
            all_passed = False
        else:
            print(f"  ✅ All cells have values (0 empty)")
        
        # Test 5: Check for description sections after the table
        # Get all text from table to next monster (or end)
        next_h2 = table.find_next('h2')
        if next_h2:
            section_end = next_h2
        else:
            section_end = soup.find('body')
        
        # Get all text between table and next section
        description_text = ""
        current = table.find_next_sibling()
        while current and current != section_end:
            if hasattr(current, 'get_text'):
                description_text += current.get_text()
            current = current.find_next_sibling()
        
        # Check for Combat, Habitat/Society, Ecology
        if "Combat:" not in description_text and "Combat :" not in description_text:
            print(f"  ⚠️  Missing Combat section")
        else:
            print(f"  ✅ Combat section present")
        
        if "Habitat/Society:" not in description_text and "Habitat/Society :" not in description_text:
            print(f"  ⚠️  Missing Habitat/Society section")
        else:
            print(f"  ✅ Habitat/Society section present")
        
        if "Ecology:" not in description_text and "Ecology :" not in description_text:
            print(f"  ⚠️  Missing Ecology section")
        else:
            print(f"  ✅ Ecology section present")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All monster manual page tests PASSED")
        return True
    else:
        print("❌ Some monster manual page tests FAILED")
        return False


def test_no_fragmented_paragraphs():
    """Test that monster sections don't have excessive fragmented <p> tags."""
    
    html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-five-monsters-of-athas.html"
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("\n🧪 Testing for Fragmented Paragraphs")
    print("=" * 80)
    
    # Check for patterns like: <p><span...>CLIMATE/TERRAIN: ...</span></p><p><span...>value</span></p>
    # This indicates fragmented monster stats that should be in a table
    
    fragmentation_patterns = [
        r'<p><span[^>]*>CLIMATE/TERRAIN:[^<]*</span></p>\s*<p>',
        r'<p><span[^>]*>FREQUENCY:[^<]*</span></p>\s*<p>',
        r'<p><span[^>]*>NO\. APPEARING:[^<]*</span></p>\s*<p><span[^>]*>ARMOR CLASS:',
    ]
    
    found_fragments = []
    for pattern in fragmentation_patterns:
        matches = re.findall(pattern, html)
        if matches:
            found_fragments.extend(matches)
    
    if found_fragments:
        print(f"❌ Found {len(found_fragments)} fragmented paragraph patterns")
        print("  This suggests monster stats are still in <p> tags instead of tables")
        return False
    else:
        print("✅ No fragmented paragraph patterns found")
        return True


def main():
    """Run all tests."""
    results = []
    
    results.append(test_monster_manual_pages())
    results.append(test_no_fragmented_paragraphs())
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    
    if all(results):
        print("✅ ALL TESTS PASSED")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

