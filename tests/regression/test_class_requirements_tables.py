"""
Regression test for class requirements tables in Chapter 3 HTML output.

This test validates that ALL player class requirements tables are present in the
final HTML output and formatted correctly as 2-column, 3-row tables.

REQ-TESTING-1: Every player class MUST have a requirements table in the HTML output.
REQ-TESTING-2: Each requirements table MUST have exactly 3 rows (Ability Requirements, Prime Requisite, Races Allowed).
REQ-TESTING-3: Each requirements table MUST have exactly 2 columns (label, value).
REQ-TESTING-4: Ability Requirements MUST contain at least one ability-number pair.
REQ-TESTING-5: Prime Requisite MUST be one of the six ability names.
REQ-TESTING-6: Races Allowed MUST be a non-empty list.
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup, Tag

# Expected player classes with their requirements
EXPECTED_PLAYER_CLASSES = {
    # Warriors
    "Fighter": {
        "abilities": ["Strength 9"],
        "prime": "Strength",
        "races": ["All"]
    },
    "Gladiator": {
        "abilities": ["Strength 13", "Dexterity 12", "Constitution 15"],
        "prime": "Strength",
        "races": ["All"]
    },
    "Ranger": {
        "abilities": ["Strength 13", "Dexterity 13", "Constitution 14", "Wisdom 14"],
        "prime": ["Strength", "Dexterity", "Wisdom"],
        "races": ["Human", "Elf", "Half-elf", "Halfling", "Thri-kreen"]
    },
    # Wizards
    "Defiler": {
        "abilities": ["Intelligence 9"],
        "prime": "Intelligence",
        "races": ["Human", "Elf", "Half-elf"]
    },
    "Preserver": {
        "abilities": ["Intelligence 9"],
        "prime": "Intelligence",
        "races": ["Human", "Elf", "Half-elf"]
    },
    "Illusionist": {
        "abilities": ["Dexterity 16"],
        "prime": "Intelligence",
        "races": ["Human", "Elf", "Half-elf", "Halfling"]
    },
    # Priests
    "Cleric": {
        "abilities": ["Wisdom 9"],
        "prime": "Wisdom",
        "races": ["All"]
    },
    "Druid": {
        "abilities": ["Wisdom 12", "Charisma 15"],
        "prime": ["Wisdom", "Charisma"],
        "races": ["Human", "Half-elf", "Halfling", "mul", "Thri-kreen"]
    },
    "Templar": {
        "abilities": ["Wisdom 3", "Intelligence 10"],
        "prime": "Wisdom",
        "races": ["Human", "Dwarf", "Elf", "Half-elf"]
    },
    # Rogues
    "Bard": {
        "abilities": ["Dexterity 12", "Intelligence 13", "Charisma 15"],
        "prime": ["Dexterity", "Charisma"],
        "races": ["Human", "Half-elf"]
    },
    "Thief": {
        "abilities": ["Dexterity 9"],
        "prime": "Dexterity",
        "races": ["All"]
    },
    # Psionicist
    "Psionicist": {
        "abilities": ["Constitution 11", "Intelligence 12", "Wisdom 15"],
        "prime": ["Constitution", "Wisdom"],
        "races": ["Any"]
    }
}

VALID_ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]


def find_class_requirements_table(soup: BeautifulSoup, class_name: str) -> Tag:
    """Find the requirements table for a specific class.
    
    The table should appear immediately after the class name header.
    
    Args:
        soup: BeautifulSoup object of the HTML
        class_name: Name of the class (e.g., "Fighter", "Gladiator")
        
    Returns:
        The table Tag, or None if not found
    """
    # Find the class header (H3 with class name)
    headers = soup.find_all(['h2', 'h3', 'h4'])
    class_header = None
    
    for header in headers:
        header_text = header.get_text(strip=True)
        # Remove roman numerals, colors, and other formatting
        clean_text = re.sub(r'^[IVXLCDM]+\.\s*', '', header_text)
        clean_text = re.sub(r'\[\^\]$', '', clean_text)
        
        if clean_text.strip() == class_name:
            class_header = header
            break
    
    if not class_header:
        return None
    
    # The requirements table should be the next sibling or very close after the header
    next_element = class_header.find_next_sibling()
    
    # Skip up to 2 elements (sometimes there might be a paragraph or marker in between)
    for _ in range(3):
        if next_element is None:
            break
        
        if next_element.name == "table":
            # Verify this looks like a requirements table
            rows = next_element.find_all("tr")
            if len(rows) >= 3:  # Should have at least 3 rows
                first_cell = rows[0].find(['td', 'th'])
                if first_cell and "Ability Requirements" in first_cell.get_text():
                    return next_element
        
        next_element = next_element.find_next_sibling()
    
    return None


def validate_requirements_table_structure(table: Tag) -> dict:
    """Validate the structure of a requirements table.
    
    Returns:
        Dictionary with validation results and extracted data
    """
    result = {
        "valid": True,
        "errors": [],
        "data": {
            "ability_requirements": None,
            "prime_requisite": None,
            "races_allowed": None
        }
    }
    
    rows = table.find_all("tr")
    
    # Must have exactly 3 rows
    if len(rows) != 3:
        result["valid"] = False
        result["errors"].append(f"Expected 3 rows, found {len(rows)}")
        return result
    
    # Validate each row
    for idx, (expected_label, data_key) in enumerate([
        ("Ability Requirements:", "ability_requirements"),
        ("Prime Requisite:", "prime_requisite"),
        ("Races Allowed:", "races_allowed")
    ]):
        row = rows[idx]
        cells = row.find_all(['td', 'th'])
        
        # Must have exactly 2 cells
        if len(cells) != 2:
            result["valid"] = False
            result["errors"].append(f"Row {idx+1} expected 2 cells, found {len(cells)}")
            continue
        
        # First cell should be the label
        label = cells[0].get_text(strip=True)
        if label != expected_label:
            result["valid"] = False
            result["errors"].append(f"Row {idx+1} expected label '{expected_label}', found '{label}'")
        
        # Second cell contains the value
        # Handle <br> tags by replacing them with spaces before extracting text
        cell_html = str(cells[1])
        # Replace <br> and <br/> with space
        cell_html = cell_html.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
        # Now extract text from the modified HTML
        from bs4 import BeautifulSoup
        temp_soup = BeautifulSoup(cell_html, 'html.parser')
        value = temp_soup.get_text(strip=True)
        if not value:
            result["valid"] = False
            result["errors"].append(f"Row {idx+1} value is empty")
        
        result["data"][data_key] = value
    
    return result


def validate_ability_requirements(ability_text: str) -> dict:
    """Validate that ability requirements follow the expected format.
    
    Each requirement should be "AbilityName Number" (e.g., "Strength 9").
    
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "abilities": []
    }
    
    # Parse ability requirements
    # Format: "Strength 9" or "Strength 9 Dexterity 12" or "Strength 9, Dexterity 12"
    # Remove commas and split on spaces
    parts = ability_text.replace(",", " ").split()
    
    i = 0
    while i < len(parts):
        # Expect: AbilityName Number
        if i + 1 >= len(parts):
            result["valid"] = False
            result["errors"].append(f"Incomplete ability requirement: {parts[i]}")
            break
        
        ability_name = parts[i]
        ability_value = parts[i + 1]
        
        # Validate ability name
        if ability_name not in VALID_ABILITIES:
            result["valid"] = False
            result["errors"].append(f"Invalid ability name: {ability_name}")
        
        # Validate ability value is a number
        if not ability_value.isdigit():
            result["valid"] = False
            result["errors"].append(f"Invalid ability value: {ability_value} for {ability_name}")
        
        result["abilities"].append(f"{ability_name} {ability_value}")
        i += 2
    
    if not result["abilities"]:
        result["valid"] = False
        result["errors"].append("No ability requirements found")
    
    return result


def validate_prime_requisite(prime_text: str) -> dict:
    """Validate that prime requisite contains only valid ability names.
    
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "abilities": []
    }
    
    # Parse prime requisites
    # Format: "Strength" or "Strength, Dexterity, Wisdom"
    abilities = [a.strip() for a in prime_text.replace(" and ", ", ").split(",")]
    
    for ability in abilities:
        if ability not in VALID_ABILITIES:
            result["valid"] = False
            result["errors"].append(f"Invalid prime requisite: {ability}")
        else:
            result["abilities"].append(ability)
    
    if not result["abilities"]:
        result["valid"] = False
        result["errors"].append("No prime requisite found")
    
    return result


def validate_races_allowed(races_text: str) -> dict:
    """Validate that races allowed is a non-empty list.
    
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "errors": [],
        "races": []
    }
    
    # Parse races
    # Format: "All" or "Human, Elf, Half-elf"
    if races_text in ["All", "Any"]:
        result["races"] = [races_text]
    else:
        races = [r.strip() for r in races_text.replace(" and ", ", ").split(",")]
        result["races"] = races
    
    if not result["races"]:
        result["valid"] = False
        result["errors"].append("No races found")
    
    return result


def main(html_path: Path = None) -> int:
    """Main test function.
    
    Args:
        html_path: Path to the HTML file to test (optional)
        
    Returns:
        0 if all tests pass, 1 if any test fails
    """
    if html_path is None:
        html_path = Path(__file__).parent.parent.parent / "data" / "html_output" / "chapter-three-player-character-classes.html"
    
    if not html_path.exists():
        print(f"❌ ERROR: HTML file not found: {html_path}")
        return 1
    
    print(f"📄 Testing class requirements tables in: {html_path}")
    print()
    
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    all_passed = True
    missing_classes = []
    invalid_classes = []
    
    for class_name, expected in EXPECTED_PLAYER_CLASSES.items():
        print(f"🔍 Testing {class_name}...")
        
        # Find the requirements table
        table = find_class_requirements_table(soup, class_name)
        
        if table is None:
            print(f"  ❌ FAIL: Requirements table not found for {class_name}")
            missing_classes.append(class_name)
            all_passed = False
            continue
        
        # Validate table structure
        structure_result = validate_requirements_table_structure(table)
        
        if not structure_result["valid"]:
            print(f"  ❌ FAIL: Invalid table structure for {class_name}")
            for error in structure_result["errors"]:
                print(f"    - {error}")
            invalid_classes.append(class_name)
            all_passed = False
            continue
        
        # Validate ability requirements
        ability_result = validate_ability_requirements(structure_result["data"]["ability_requirements"])
        if not ability_result["valid"]:
            print(f"  ❌ FAIL: Invalid ability requirements for {class_name}")
            for error in ability_result["errors"]:
                print(f"    - {error}")
            invalid_classes.append(class_name)
            all_passed = False
            continue
        
        # Validate prime requisite
        prime_result = validate_prime_requisite(structure_result["data"]["prime_requisite"])
        if not prime_result["valid"]:
            print(f"  ❌ FAIL: Invalid prime requisite for {class_name}")
            for error in prime_result["errors"]:
                print(f"    - {error}")
            invalid_classes.append(class_name)
            all_passed = False
            continue
        
        # Validate races allowed
        races_result = validate_races_allowed(structure_result["data"]["races_allowed"])
        if not races_result["valid"]:
            print(f"  ❌ FAIL: Invalid races allowed for {class_name}")
            for error in races_result["errors"]:
                print(f"    - {error}")
            invalid_classes.append(class_name)
            all_passed = False
            continue
        
        print(f"  ✅ PASS: Requirements table valid for {class_name}")
        print(f"    - Abilities: {', '.join(ability_result['abilities'])}")
        print(f"    - Prime: {', '.join(prime_result['abilities'])}")
        print(f"    - Races: {', '.join(races_result['races'])}")
    
    print()
    print("=" * 70)
    print(f"📊 Test Summary: {len(EXPECTED_PLAYER_CLASSES)} classes tested")
    print(f"  ✅ Passed: {len(EXPECTED_PLAYER_CLASSES) - len(missing_classes) - len(invalid_classes)}")
    if missing_classes:
        print(f"  ❌ Missing tables: {len(missing_classes)} - {', '.join(missing_classes)}")
    if invalid_classes:
        print(f"  ❌ Invalid tables: {len(invalid_classes)} - {', '.join(invalid_classes)}")
    print("=" * 70)
    
    if all_passed:
        print("🏆 ALL TESTS PASSED!")
        return 0
    else:
        print("💥 TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

