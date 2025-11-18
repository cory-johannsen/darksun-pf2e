# Chapter 1 (Ability Scores) Changelog

## 2025-11-12 - Header Level Fix (Updated)

### Issue
All headers in Chapter 1 were being rendered as H1 headers with Roman numerals. The user requested that:
1. Optional Methods and all its sub-methods (I-V) should be H2 headers
2. Intelligence: and Wisdom: should be H2 headers

### Changes Made

1. **Created Chapter 1 Postprocessing Module**
   - Created `/tools/pdf_pipeline/postprocessors/chapter_1_postprocessing.py`
   - Implements `apply_chapter_1_content_fixes()` function
   - Applies H2 styling to Optional Methods headers

2. **Updated HTML Export Pipeline**
   - Modified `/tools/pdf_pipeline/postprocessors/html_export.py`
   - Added import for `apply_chapter_1_content_fixes`
   - Added chapter-specific postprocessing for "chapter-one-ability-scores" slug

3. **Updated Processing Specification**
   - Updated `/docs/chapter_1_processing_spec.md`
   - Documented H1 vs H2 header structure
   - Added postprocessing details section

4. **Created Unit Tests**
   - Created `/tests/test_chapter_1_postprocessing.py`
   - Tests H2 header styling application
   - Tests Roman numeral removal from H2 headers
   - Tests H1 headers remain unchanged

5. **Created Regression Test**
   - Created `/tests/regression/test_chapter1_header_levels.py`
   - Validates H2 headers have correct styling and no Roman numerals
   - Validates H1 headers have Roman numerals and no H2 styling

### Header Structure

**H1 Headers (Main Sections):**
- Rolling Ability Scores (I.)
- Rolling Player Character Ability Scores (II.)
- Rolling Non-player Character Ability Scores (III.)
- The Ability Scores (X.)

**H2 Headers (Subsections):**
- Optional Methods (no Roman numeral)
- Optional Method I: (no Roman numeral)
- Optional Method II: (no Roman numeral)
- Optional Method III: (no Roman numeral)
- Optional Method IV: (no Roman numeral)
- Optional Method V: (no Roman numeral)
- Intelligence: (no Roman numeral)
- Wisdom: (no Roman numeral)

### Technical Details

The postprocessing function:
1. Identifies headers 3-8, 10, 11 by their IDs
2. Adds `class="h2-header"` to the `<p>` tag
3. Adds `font-size: 0.9em` to the span's inline style
4. Removes Roman numerals from H2 headers using regex pattern matching
5. Renumbers "The Ability Scores" from X to IV (since headers 3-8 are now H2)

### Validation

All tests pass:
- ✅ Unit tests for chapter_1_postprocessing.py (5 tests)
- ✅ Regression test for header levels (48 checks including Intelligence and Wisdom)
- ✅ All existing regression tests (HTML index, relative paths, dehyphenation)

### Result

Chapter 1 now correctly displays:
- H1 headers with Roman numerals (I, II, III, X) at normal size
- H2 headers without Roman numerals at 90% size (Optional Methods I-V, Intelligence, Wisdom)
- Proper TOC indentation reflecting the header hierarchy
