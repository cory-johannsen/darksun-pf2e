# Chapter 3 Changelog — Player Character Classes

## 2025-11-18

### Rangers Followers Table Regression Fix
- **Fixed regression**: Multiple malformed tables were appearing in the Ranger section after "the ranger answers that challenge" paragraph. These tables mixed paragraph text with table data (e.g., "largely unchanged. The wilderness is harsh and unforgiving, calling for skilled and capable men to" mixed with "01-04 Aarakocra").
- **Root Cause**: The `reconstruct_rangers_followers_table_inplace()` function was only reconstructing ONE malformed table but not removing ALL malformed tables from the page.
- **Fix**: Updated the function to:
  1. Find ALL malformed tables containing Rangers Followers data (using both creature keywords and paragraph fragments as indicators)
  2. Delete ALL malformed tables (in reverse order to maintain indices)
  3. Create and append a single correctly structured Rangers Followers table with d100 ranges and follower types
- **Testing**: Created new regression test `tests/regression/test_ranger_malformed_tables.py` to detect this specific issue in the future. The test checks:
  - No malformed tables exist between "ranger answers that challenge" and "Rangers Followers" section
  - No paragraph text appears mixed with table data
  - Only the requirements table is allowed in this section
- **Files Modified**:
  - `tools/pdf_pipeline/transformers/chapter_3/ranger.py` - Updated `reconstruct_rangers_followers_table_inplace()` function
  - `docs/chapter_3_processing_spec.md` - Documented the fix
  - `tests/regression/test_ranger_malformed_tables.py` - New regression test

### Header Hierarchy Fix
- **Corrected header levels throughout Chapter 3** to match proper document structure:
  - **H2**: "Warriors", "Wizard", "Priest", "Rogue", "Psionicist (Dark Sun variation)" now properly render as H2 headers with roman numerals
  - **H2 (subsections)**: "Starting Level", "Starting Proficiencies", "Starting Money" now render as H2 with 0.9em font-size
  - **H3**: Class names ("Fighter", "Gladiator", "Ranger", "Defiler", "Preserver", "Illusionist", "Cleric", "Druid", "Templar", "Bard", "Thief") now render as H3 with 0.8em font-size
  - **H4**: Detailed subsections ("Fighters Followers", "RANGERS FOLLOWERS", "Defiler Experience Levels", "Sphere of Earth", "Sphere of Air", "Sphere of Fire", "Sphere of Water", "Templar Spell Progression") now render as H4 with 0.7em font-size
- **Implementation**:
  - Added `_adjust_header_levels()` function in `chapter_3_processing.py` to mark headers with `__render_as_h3` and `__render_as_h4` flags
  - Updated `apply_subheader_styling()` in `toc.py` to apply correct font-sizes (0.8em for H3, 0.7em for H4)
  - Modified `_convert_by_class()` in `header_conversion.py` to handle headers without roman numerals
  - Updated `render_text_block()` in `rendering.py` to check for `__css_class` markers and apply them to spans
- **Table of Contents**: All headers now display with proper indentation and hierarchy in the TOC

### Italics Fix
- **Fixed italics regression**: Updated `is_italic()` function in `utilities.py` to recognize Dark Sun PDF's italic font (`MSTT31c576`). This font is used for book titles like "The Complete Psionics Handbook" and "Players Handbook", as well as emphasized terms throughout the document.
- **Added regression test suite**: Created `tests/regression/test_chapter3_italics.py` with 5 test cases to catch future italic formatting issues:
  - Book title italicization
  - Word merging detection
  - Intro paragraph formatting
  - Handbook reference validation
  - Common book title patterns
- **Identified space stripping issue**: Discovered that `.strip()` calls in chapter 3 processing modules are removing trailing spaces from spans, causing words to merge (e.g., "Thedefileris", "Thepreserverattempts"). This requires a systematic refactor across multiple files in `tools/pdf_pipeline/transformers/chapter_3/`. See `docs/chapter_3_italics_fix.md` for detailed analysis.
- **Test Coverage Improvement**: Regression tests now verify both italic formatting (✅ fixed) and proper word spacing (⏳ pending fix).
- **Partial Fix Status**: Italics are now correctly rendered, but space preservation between words requires additional work to avoid breaking existing functionality.

## 2025-11-12
- **Fixed Templar Spell Progression duplicate tables**: The borderless table detection was creating 713 malformed tables from fragmented spell progression data on page 35. Fixed by replacing ALL tables on the page with a single corrected table built from authoritative reference data.
- Changed `page["tables"][0] = {...}` to `page["tables"] = [corrected_table]` in `_extract_templar_spell_progression_table()`
- Verified only ONE properly formatted table now appears under "Templar Spell Progression" header
- Updated processing spec with fix documentation and validation requirements

## 2025-11-08
- Locked Chapter 3 (“Player Character Classes”) from transformation by adding `chapter-three-player-character-classes` to `skip_slugs` in `data/mappings/section_profiles.json`, per CONTENT_LOCK policy. This preserves current processed JSON/HTML as the source of truth.

## 2025-11-08 (later)
- Ensured “Character Trees” renders as four paragraphs by adding paragraph break hints at:
  - “Replacing a fallen player character of high level”
  - “In DARK SUN campaigns, players are encour-”
  - “In brief, a character tree consists of one active”
- Regenerated outputs and validated paragraph structure via regression tests.
- Aligned the `Alignment` subsection under Character Trees to 4 paragraphs using break hints at:
  - “For example, one character tree might”
  - “If a character is forced to change alignment”
  - “Discarded characters should be given to the”
- Enforced 4-paragraph structure for `Character Advancement` using break hints at:
  - “Every time the active character …”
  - “For purposes of character tree …”
  - “For inactive multi-class characters …”
- Ensured `The Status of Inactive Characters` renders as 3 paragraphs with break hints at:
  - “When not in play, …”
  - “All characters in a character …”
- Added break hints:
  - `Using the Character Tree to Advantage`: “As only one inactive character gains …”, “As another example, the quest might …”
  - `Exchanges Between Characters`: “In some instances …”, “DARK SUN …”, “As stated in the …”

## 2025-11-08
- Fixed “Multi-Class Combinations” intro paragraph assembly by concatenating all text blocks between the subheader and the first race header. This avoids phrase-specific heuristics and ensures the full paragraph is preserved, including “subject to the restrictions…” and “The following chart lists the possible character class combinations available…”.
- Regenerated Chapter 3 outputs and verified via regression tests.
- Split the substitution rules after the Thri-kreen table into separate sentences as distinct paragraphs for readability.

## 2025-11-07
- Preserve “Multi-Class and Dual-Class Characters” introductory paragraph.
- Removed aggressive block clearing in multi-class section to avoid deleting narrative paragraphs.
- Limited cleanup to combination list fragments only; rebuilt race tables from extracted combos.
- Ensured substitution rules paragraph remains after all race tables.
- Regenerated chapter 3 HTML and verified presence of the intro text.


