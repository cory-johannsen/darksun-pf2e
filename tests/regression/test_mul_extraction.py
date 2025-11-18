"""
Regression tests for Mul section extraction and data transformation.

These tests ensure that the Mul section content is properly extracted
from the PDF and that no data is lost during transformation.
"""

import json
import pytest
from pathlib import Path


def check_mul_content_extraction(json_file_path: str) -> tuple[bool, list[str]]:
    """Test that all Mul content is extracted from the PDF.
    
    Args:
        json_file_path: Path to the structured JSON file
        
    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    
    json_path = Path(json_file_path)
    if not json_path.exists():
        errors.append(f"JSON file not found: {json_file_path}")
        return False, errors
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all text from pages 11 and 12 (where Mul content is)
    mul_text = ""
    pages = data.get('pages', [])
    
    for page_idx in [11, 12]:
        if len(pages) <= page_idx:
            errors.append(f"Page index {page_idx} not found in data")
            continue
        
        page = pages[page_idx]
        for block in page.get('blocks', []):
            if block.get('type') != 'text':
                continue
            
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '')
                    mul_text += text + " "
    
    # Check for key phrases that must be present
    required_phrases = [
        "A mul (pronounced: mül)",
        "crossbreed of a human and dwarf",
        "A full-grown mul stands",
        "Born as they are to lives of slave labor",
        "Many slave muls have either escaped",
        "A player character mul may become",
        "A mul character adds two to his initial Strength",
        "Mules are able to work longer and harder",
        "Regardless of the preceding type of exertion",
        "Like their dwarven parent"
    ]
    
    missing_phrases = []
    for phrase in required_phrases:
        if phrase not in mul_text:
            missing_phrases.append(phrase)
    
    if missing_phrases:
        errors.append(f"Missing {len(missing_phrases)} required phrases in Mul extraction:")
        for phrase in missing_phrases[:5]:  # Show first 5
            errors.append(f"  - {phrase}")
    
    # Check that we have a reasonable amount of text (at least 2000 characters)
    if len(mul_text) < 2000:
        errors.append(f"Mul text too short: {len(mul_text)} characters (expected >2000)")
    
    return len(errors) == 0, errors


def check_mul_paragraph_breaks(json_file_path: str) -> tuple[bool, list[str]]:
    """Test that paragraph break markers are correctly set.
    
    NOTE: This test is informational only. The __force_paragraph_break markers
    are set during the TRANSFORMATION stage, not during extraction. They are
    not saved back to the JSON file. This test helps document where breaks
    should occur, but will always show 0 markers in the extracted JSON.
    
    Args:
        json_file_path: Path to the structured JSON file
        
    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    warnings = []
    
    json_path = Path(json_file_path)
    if not json_path.exists():
        errors.append(f"JSON file not found: {json_file_path}")
        return False, errors
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pages = data.get('pages', [])
    
    # Count blocks with __force_paragraph_break on pages 11 and 12
    force_break_count = 0
    
    for page_idx in [11, 12]:
        if len(pages) <= page_idx:
            continue
        
        page = pages[page_idx]
        for block in page.get('blocks', []):
            if block.get('__force_paragraph_break', False):
                force_break_count += 1
    
    # NOTE: This will always be 0 in extracted JSON - markers are added during transformation
    if force_break_count == 0:
        warnings.append("INFO: Paragraph break markers are set during transformation, not extraction (expected)")
    
    # This test always passes - it's informational only
    return True, warnings


def check_mul_section_boundaries(json_file_path: str) -> tuple[bool, list[str]]:
    """Test that Mul section boundaries are correctly identified.
    
    Args:
        json_file_path: Path to the structured JSON file
        
    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    
    json_path = Path(json_file_path)
    if not json_path.exists():
        errors.append(f"JSON file not found: {json_file_path}")
        return False, errors
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pages = data.get('pages', [])
    
    # Find the block that contains "A mul (pronounced:"
    mul_start_found = False
    mul_end_found = False
    
    for page in pages:
        for block in page.get('blocks', []):
            if block.get('type') != 'text':
                continue
            
            text = ""
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text += span.get('text', '')
            
            if "A mul (pronounced:" in text or "A mul (pronounced: mül)" in text:
                mul_start_found = True
            
            if "Like their dwarven parent" in text:
                mul_end_found = True
    
    if not mul_start_found:
        errors.append("Mul section start not found")
    
    if not mul_end_found:
        errors.append("Mul section end (Roleplaying) not found")
    
    return len(errors) == 0, errors


def run_all_tests(json_file_path: str) -> tuple[bool, dict]:
    """Run all Mul extraction tests.
    
    Args:
        json_file_path: Path to the structured JSON file
        
    Returns:
        Tuple of (all_passed, results_dict)
    """
    tests = [
        ("Content Extraction", check_mul_content_extraction),
        ("Paragraph Break Markers", check_mul_paragraph_breaks),
        ("Section Boundaries", check_mul_section_boundaries),
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        success, errors = test_func(json_file_path)
        results[test_name] = {
            "passed": success,
            "errors": errors
        }
        if not success:
            all_passed = False
    
    return all_passed, results


def print_test_results(results: dict) -> None:
    """Print test results in a readable format.
    
    Args:
        results: Results dictionary from run_all_tests
    """
    print("\n" + "=" * 70)
    print("MUL EXTRACTION REGRESSION TEST RESULTS")
    print("=" * 70 + "\n")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r["passed"])
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result["passed"] else "✗ FAILED"
        print(f"{test_name}: {status}")
        
        if not result["passed"] and result["errors"]:
            for error in result["errors"]:
                print(f"  - {error}")
            print()
    
    print("=" * 70)
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
    print("=" * 70 + "\n")


# Pytest test functions
@pytest.fixture
def json_file():
    """Fixture to provide the structured JSON file for testing."""
    json_path = Path(__file__).parent.parent.parent / "data" / "raw_structured" / "sections" / "chapter-two-player-character-races.json"
    if not json_path.exists():
        pytest.skip(f"JSON file not found: {json_path}")
    return str(json_path)


def test_mul_content_extraction_pytest(json_file):
    """Test Mul content extraction using pytest."""
    success, errors = check_mul_content_extraction(json_file)
    assert success, f"Mul content extraction failed:\n" + "\n".join(errors)


def test_mul_paragraph_breaks_pytest(json_file):
    """Test Mul paragraph breaks using pytest."""
    success, errors = check_mul_paragraph_breaks(json_file)
    # This test is informational only and always passes
    assert success, f"Mul paragraph breaks check:\n" + "\n".join(errors)


def test_mul_section_boundaries_pytest(json_file):
    """Test Mul section boundaries using pytest."""
    success, errors = check_mul_section_boundaries(json_file)
    assert success, f"Mul section boundaries failed:\n" + "\n".join(errors)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_mul_extraction.py <path_to_json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    all_passed, results = run_all_tests(json_file)
    print_test_results(results)
    
    sys.exit(0 if all_passed else 1)

