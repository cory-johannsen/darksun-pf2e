# Chapter 3 Italics Regression Fix

## Issue Summary

Recent refactors to Chapter 3 processing caused two related regressions:

1. **Italics Lost**: Italic formatting (book titles, emphasized words) was not being rendered  
2. **Word Merging**: Words were being incorrectly joined without spaces (e.g., "Thedefileris")

## Root Causes

### 1. Italic Font Not Recognized

The Dark Sun PDF uses font `MSTT31c576` for italic text, but the `is_italic()` function in `utilities.py` only checked for font names containing "italic" or "oblique" keywords.

**Affected Text**:
- Book titles: "The Complete Psionics Handbook", "Players Handbook"  
- Emphasized terms: defiler, preserver, illusionist, psionicist, etc.

**Fix**: Updated `is_italic()` function to explicitly recognize `MSTT31c576` as an italic font.

```python
def is_italic(font_name: str | None, flags: int | None) -> bool:
    if not font_name:
        return False
    lowered = font_name.lower()
    
    # Check for common italic font name patterns
    if any(keyword in lowered for keyword in ("italic", "oblique")):
        return True
    
    # Dark Sun PDF-specific font: MSTT31c576 is used for italicized text
    if font_name == "MSTT31c576":
        return True
    
    return False
```

**File**: `tools/pdf_pipeline/transformers/journal_lib/utilities.py:136-151`

### 2. Space Stripping in Chapter 3 Processing

Multiple locations in chapter 3 processing strip whitespace from individual spans during text collection and block merging, causing word boundaries to be lost.

**Problematic Patterns**:
```python
# Example 1: Stripping individual spans (chapter_3/warrior.py:350)
parts.append(span.get("text", "").strip())

# Example 2: Stripping joined text (chapter_3/warrior.py:367)  
next_text = " ".join(...).strip()

# Example 3: join_fragments utility (utilities.py:77)
return text.strip()  # Strips trailing spaces from joined fragments
```

**Affected Text**:
- "The defiler" → "Thedefiler"
- "The preserver" → "Thepreserver"  
- "The illusionist" → "Theillusionist"
- Similar patterns throughout Chapter 3

**Status**: ⚠️ **PENDING FIX** - Requires systematic refactor of chapter 3 processing to preserve spaces.

## Fix Implementation

### Phase 1: Italic Recognition ✅ COMPLETE

**Files Modified**:
- `tools/pdf_pipeline/transformers/journal_lib/utilities.py`

**Changes**:
- Added `MSTT31c576` font to `is_italic()` function
- Documented the Dark Sun-specific font usage

**Testing**:
- Created `tests/regression/test_chapter3_italics.py` with comprehensive tests
- Verified book titles are properly italicized in HTML output

### Phase 2: Space Preservation ⏳ PENDING

**Scope**: Multiple files in `tools/pdf_pipeline/transformers/chapter_3/`

**Required Changes**:
1. Remove `.strip()` calls on individual span text during collection
2. Only strip at final paragraph/block level when appropriate
3. Preserve font information through all merging operations
4. Update all text collection helpers to maintain word boundaries

**Risk Assessment**: 
- **Medium-High**: Changes affect core processing logic
- **Impact**: All chapter 3 sections (warrior, wizard, priest, rogue, psionicist, multiclass)
- **Testing Required**: Full regression suite + manual verification

**Recommended Approach**:
1. Audit all `.strip()` calls in chapter_3 modules
2. Create unit tests for space preservation
3. Refactor in small, testable increments
4. Verify each section independently

## Test Coverage

### Regression Tests Added

**File**: `tests/regression/test_chapter3_italics.py`

**Test Cases**:
1. `test_chapter3_book_titles_are_italicized` - Verifies book titles wrapped in `<i>` or `<em>` tags
2. `test_chapter3_no_word_merging_from_lost_italics` - Detects merged words from missing italics
3. `test_chapter3_intro_paragraph_italic_formatting` - Checks intro paragraph formatting
4. `test_chapter3_fighters_section_handbook_references` - Validates handbook references
5. `test_chapter3_common_italic_book_patterns` - Tests common book title patterns

**Coverage**: ✅ Italics detection | ⚠️ Space preservation (needs additional tests)

## Validation

### Before Fix
```html
<p>Dark Sun characters can also be psionicists, as described inThe Complete Psionics Handbook.There are...</p>
<p>Thedefileris a wizard who activates tremendous magical energy...</p>
```

### After Fix (Phase 1)
```html
<p>Dark Sun characters can also be psionicists, as described in<em>The</em> <em>Complete Psionics Handbook.</em>There are...</p>
<p>Thedefileris a wizard who activates tremendous magical energy...</p>
```

### Expected After Phase 2
```html
<p>Dark Sun characters can also be psionicists, as described in <em>The Complete Psionics Handbook.</em> There are...</p>
<p>The <em>defiler</em> is a wizard who activates tremendous magical energy...</p>
```

## Lessons Learned

1. **Font Detection**: PDF extraction requires explicit font mappings for proprietary/embedded fonts
2. **Space Preservation**: Text processing must carefully preserve whitespace boundaries
3. **Test Coverage**: Regression tests must include both positive (formatting present) and negative (spacing correct) checks
4. **Incremental Fixes**: Complex issues should be fixed in phases with independent validation

## Related Files

- `tools/pdf_pipeline/transformers/journal_lib/utilities.py` - Text processing utilities
- `tools/pdf_pipeline/transformers/journal_lib/rendering.py` - HTML rendering
- `tools/pdf_pipeline/transformers/chapter_3/*.py` - Chapter-specific processing
- `tests/regression/test_chapter3_italics.py` - Regression tests
- `data/html_output/chapter-three-player-character-classes.html` - Output validation

## References

- **Issue**: Chapter 3 italics regression from recent refactors
- **Test Coverage**: Inadequate - tests passing despite regressions
- **Requirements**: 
  - `HTML-12`: Source italic text must be preserved in output
  - `REQUIREMENTS-2`: 100% extraction accuracy required
  - `VALIDATION-2`: All regression tests must pass after modifications

## Status

- **Phase 1 (Italic Recognition)**: ✅ COMPLETE (2025-11-18)
- **Phase 2 (Space Preservation)**: ⏳ PENDING - Requires systematic refactor
- **Overall**: 🟡 PARTIAL FIX - Italics working, spacing issues remain

