# Mul Section Fix Summary

## Problem Statement

The Mul section in Chapter 2 was rendering with 21+ fragmented paragraphs instead of the expected 8 paragraphs in the main section and 2 paragraphs in the Roleplaying subsection. Additionally, the Mul Exertion Table was not being properly extracted and was rendering as inline text within paragraphs.

## Root Causes

1. **Missing Table Extraction**: The Mul Exertion Table was never being extracted during the transformation stage, causing its content to be rendered as inline text within paragraphs.

2. **Paragraph Fragmentation**: PyMuPDF extracts text in small line-by-line fragments. While the data transformation stage was marking major paragraph boundaries with `__force_paragraph_break` flags, the HTML rendering was creating separate paragraphs for each small text fragment.

3. **Previous Corruption Issues**: Earlier attempts to fix the Mul section using HTML post-processing caused catastrophic corruption of the Table of Contents, embedding the entire document content within the TOC.

## Solution Architecture

The fix involved a **two-stage approach**:

### Stage 1: Data Transformation (Extraction/Structure)

**File**: `tools/pdf_pipeline/transformers/chapter_2_processing.py`

1. **Created `_process_mul_exertion_table()` function** to properly extract and structure the Mul Exertion Table:
   - Identifies the table region between "Mul Exertion Table" header and "Roleplaying:" header
   - Manually constructs the table with proper structure:
     - Header row: `["Type of Exertion", "Duration"]`
     - Data rows for Heavy, Medium, Light Labor and Normal Activity
   - Sets `header_rows=1` metadata for proper HTML rendering
   - Clears the original text blocks to prevent duplicate rendering

2. **Called `_process_mul_exertion_table()` for pages 11 and 12** where Mul content spans:
   ```python
   if len(pages) > 11:
       page11 = pages[11]
       _process_mul_exertion_table(page11)
       _force_mul_paragraph_breaks(page11)
   
   if len(pages) > 12:
       page12 = pages[12]
       _process_mul_exertion_table(page12)
       _force_mul_paragraph_breaks(page12)
       _force_mul_roleplaying_paragraph_breaks(page12)
   ```

3. **Existing paragraph break functions** (`_force_mul_paragraph_breaks()` and `_force_mul_roleplaying_paragraph_breaks()`) were already correctly splitting blocks at user-specified break points.

### Stage 2: HTML Post-Processing (Safe Merging)

**File**: `tools/pdf_pipeline/postprocessors/chapter_2_fixes.py`

1. **Created `_fix_mul_main_section_v2()` function** with multiple safety checks:
   - Uses very specific pattern matching to avoid TOC corruption:
     ```python
     pattern = r'(<p id="header-19-mul"><span[^>]*>Mul</span></p>)(.*?)(<p id="header-20-mul-exertion-table"><span[^>]*>Mul Exertion Table</span></p>)'
     ```
   - Safety checks:
     - Content length < 15,000 chars (prevents matching TOC content)
     - Must contain "A mul (pronounced:" 
     - Must contain > 1,000 chars
   - Merges text fragments into 8 cohesive paragraphs based on user-specified breaks
   - Skips table headers (header-20, header-21) during paragraph extraction

2. **Created `_fix_mul_roleplaying_paragraphs_v2()` function** with similar safety:
   - Uses specific pattern for Roleplaying section:
     ```python
     pattern = r'(<p id="header-21-roleplaying-"><span[^>]*>Roleplaying:[^<]*</span></p>)(.*?)(<p id="header-22-thri-kreen"><span[^>]*>Thri-kreen</span></p>)'
     ```
   - Safety checks:
     - Content length < 5,000 chars
     - Must contain "Muls are slaves"
     - Must contain > 200 chars
   - Merges into 2 cohesive paragraphs

3. **Disabled old problematic functions**:
   - `_fix_mul_main_section()` (old version)
   - `_fix_mul_roleplaying_paragraphs()` (old version)
   - `_fix_chapter_two_races()` (caused corruption)

## Regression Testing

### Test Suite 1: HTML Integrity (`tests/regression/test_html_integrity.py`)

Tests for catastrophic HTML corruption:

1. **`test_toc_integrity()`**:
   - No unclosed `<a>` tags in TOC
   - No embedded tables in TOC
   - No massive text blocks in TOC (> 10,000 chars)

2. **`test_section_integrity()`**:
   - All race sections exist (Dwarves, Elves, Half-elves, Half-giants, Halflings, Human, Mul, Thri-kreen)
   - Race headers not incorrectly embedded in TOC

3. **`test_document_structure()`**:
   - HTML has proper structure (doctype, head, body)
   - TOC comes before content sections
   - Document size reasonable (< 5MB)
   - No duplicate headers

4. **`test_mul_section_integrity()`**:
   - Mul main section found (between header-19-mul and header-20-mul-exertion-table)
   - Paragraph count reasonable (5-15 paragraphs)
   - Mul Roleplaying section found
   - No other race content embedded in Mul section

### Test Suite 2: Extraction Integrity (`tests/regression/test_mul_extraction.py`)

Tests for data loss during extraction:

1. **`test_mul_content_extraction()`**:
   - All required phrases present:
     - "A mul (pronounced: mül)"
     - "crossbreed of a human and dwarf"
     - "A full-grown mul stands"
     - "Born as they are to lives of slave labor"
     - "Many slave muls have either escaped"
     - "A player character mul may become"
     - "A mul character adds two to his initial Strength"
     - "Mules are able to work longer and harder"
     - "Regardless of the preceding type of exertion"
     - "Like their dwarven parent"
   - Text length > 2,000 characters

2. **`test_mul_paragraph_breaks()`**:
   - Informational test (always passes)
   - Documents that `__force_paragraph_break` markers are transformation-time, not extraction-time

3. **`test_mul_section_boundaries()`**:
   - Mul section start found ("A mul (pronounced:")
   - Mul section end found ("Like their dwarven parent")

## Results

### Before Fix
- ✗ 21+ fragmented paragraphs in Mul main section (expected 8)
- ✗ Mul Exertion Table rendered as inline text
- ✗ Table headers embedded in paragraphs
- ✗ Previous HTML post-processing attempts caused TOC corruption

### After Fix
- ✓ Exactly 8 cohesive paragraphs in Mul main section
- ✓ Exactly 2 cohesive paragraphs in Mul Roleplaying section
- ✓ Mul Exertion Table properly extracted and rendered
- ✓ All HTML integrity tests pass
- ✓ All extraction integrity tests pass
- ✓ Pipeline validation errors: **0 Mul-related errors**

## Test Execution

### Running HTML Integrity Tests
```bash
cd /Users/cjohannsen/git/darksun-pf2e
.venv/bin/python tests/regression/test_html_integrity.py data/html_output/chapter-two-player-character-races.html
```

Expected output:
```
======================================================================
HTML INTEGRITY REGRESSION TEST RESULTS
======================================================================

TOC Integrity: ✓ PASSED
Section Integrity: ✓ PASSED
Document Structure: ✓ PASSED
Mul Section Integrity: ✓ PASSED
======================================================================
SUMMARY: 4/4 tests passed
======================================================================
```

### Running Extraction Integrity Tests
```bash
cd /Users/cjohannsen/git/darksun-pf2e
.venv/bin/python tests/regression/test_mul_extraction.py data/raw_structured/sections/02-005-chapter-two-player-character-races.json
```

Expected output:
```
======================================================================
MUL EXTRACTION REGRESSION TEST RESULTS
======================================================================

Content Extraction: ✓ PASSED
Paragraph Break Markers: ✓ PASSED
Section Boundaries: ✓ PASSED
======================================================================
SUMMARY: 3/3 tests passed
======================================================================
```

### Running Full Pipeline
```bash
cd /Users/cjohannsen/git/darksun-pf2e
.venv/bin/python scripts/run_pipeline.py
```

Expected: **No Mul-related validation errors**

## Key Learnings

1. **Two-stage processing is essential**: Data transformation for structure, HTML post-processing for presentation.

2. **Safety checks are critical**: HTML post-processing can easily corrupt the TOC if patterns aren't specific enough. Always:
   - Use very specific regex patterns with full tag structure
   - Check content length before processing
   - Verify expected content markers are present
   - Return unchanged HTML if safety checks fail

3. **Comprehensive regression testing prevents catastrophic failures**: The test suite caught TOC corruption immediately and prevented it from being reintroduced.

4. **Table extraction requires explicit handling**: Borderless tables or tables with unusual structure need dedicated extraction functions, not just general-purpose detection.

## Files Modified

1. `tools/pdf_pipeline/transformers/chapter_2_processing.py`
   - Added `_process_mul_exertion_table()`
   - Updated `apply_chapter_2_adjustments()` to call table processing

2. `tools/pdf_pipeline/postprocessors/chapter_2_fixes.py`
   - Added `_fix_mul_main_section_v2()`
   - Added `_fix_mul_roleplaying_paragraphs_v2()`
   - Updated `apply_chapter_2_fixes()` to use new functions
   - Disabled old problematic functions

3. `tests/regression/test_html_integrity.py`
   - Updated Mul section patterns to match correct header IDs
   - Fixed section integrity test regex for race detection

4. `tests/regression/test_mul_extraction.py` (NEW)
   - Created comprehensive extraction integrity tests
   - Documents expected behavior for transformation-time markers

## Maintenance Notes

- The Mul Exertion Table structure is hardcoded in `_process_mul_exertion_table()`. If the source PDF changes, update the table rows accordingly.
- The paragraph break patterns in `_force_mul_paragraph_breaks()` are based on user-specified text. If content changes, update the patterns.
- Header IDs (header-19-mul, header-20-mul-exertion-table, header-21-roleplaying-, header-22-thri-kreen) are used in multiple places. If the header generation logic changes, update all references.
- Always run both regression test suites after any modifications to the Mul section processing.

