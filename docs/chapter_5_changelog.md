# Chapter 5 Changelog: Proficiencies

## [2025-11-10] - Nonweapon Proficiency Group Crossovers Table Reconstruction

### Fixed
- Converted "Nonweapon Proficiency Group Crossovers" section from separate headers to a proper table
- Table has 2 columns (Character Class, Proficiency Groups) and 7 rows (1 header + 6 data)
- Removed "Character Class" and "Proficiency Groups" as separate H3 headers
- Removed their entries from the Table of Contents
- Special handling for "Psionicist" which appears both as a proficiency group and as a character class
- **Cleaned up TOC**: Removed table headers from "New Nonweapon Proficiencies" table (GENERAL, Slots, Ability, Proficiency, PRIEST, WARRIOR, WIZARD) that were incorrectly appearing as TOC entries

### Table Structure
| Character Class | Proficiency Groups |
|---|---|
| Defiler | Wizard, General |
| Gladiator | Warrior, General |
| Preserver | Wizard, General |
| Psionicist | Psionicist, General |
| Templar | Priest, Rogue, General |
| Trader | Rogue, Warrior, General |

### Technical Details
- Parser extracts data from malformed text following the section header
- Character classes list is necessary structural metadata to disambiguate "Psionicist"
- Psionicist appears twice in source text (once as proficiency group, once as character class)
- Parser finds second occurrence of "Psionicist" to correctly identify it as the character class
- Table reconstruction happens in HTML post-processing stage after template generation

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (added `_reconstruct_crossover_table()`)
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (updated `_fix_toc_indentation()` to remove deleted headers)
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (updated `_apply_header_styling()` to skip deleted headers)
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (updated `apply_chapter_5_html_fixes()` to call table reconstruction)
- `docs/chapter_5_changelog.md` (updated)

## [2025-11-10] - H3 Header Styling and TOC Indentation

### Fixed
- Changed proficiency headers (Bargain through Weapon Improvisation) to H3 format
- Added `font-size: 0.8em` to span elements for H3 headers (required for TOC generation)
- Removed Roman numerals from H3 headers (only H1 headers should have Roman numerals per [HEADER_NUMERALS])
- Added `toc-subsubheader` class to H3 header entries in the Table of Contents
- H3 headers are now properly indented in the TOC beneath their parent H2 header

### Technical Details
- H3 headers are visually smaller than H2 headers and indented further in the TOC
- The `font-size: 0.8em` attribute in the span element is detected by TOC generation logic
- TOC indentation uses `toc-subsubheader` class with `padding-left: 4rem`
- Header styling must happen before TOC generation, but TOC indentation fix happens after
- Split processing into two stages:
  1. Content fixes (before template): Add font-size to spans, remove Roman numerals
  2. HTML fixes (after template): Fix TOC indentation classes

### Affected Headers
H3 proficiency headers under "Description of New Proficiencies":
- Armor Optimization
- Bargain
- Bureaucracy
- Heat Protection
- Psionic Detection
- Sign Language
- Somatic Concealment
- Water Find
- Weapon Improvisation

Additional H3 headers under other sections:
- Character Class
- Proficiency Groups
- Agriculture through Weaponsmithing (under "Use of Existing Proficiencies")

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (added `_fix_toc_indentation()`, updated `_apply_header_styling()`)
- `docs/chapter_5_changelog.md` (updated)

### Verification
- Created and ran verification script to confirm all requirements met
- All regression tests passing (relative paths, dehyphenation, HTML index)

## [2025-11-10] - Proficiency Description Paragraph Breaks

### Fixed
- Added paragraph breaks in individual proficiency descriptions at natural break points
- Split 9 locations where PDF extraction merged multiple paragraphs:
  1. "Simple and protracted barter" (Bargain description)
  2. "In addition to these example uses, the" (Bureaucracy description)
  3. "Dehydration receives full explanation" (Heat Protection description)
  4. "When employing this proficiency, a" (Psionic Detection description)
  5. "Psionic detection proficiency can only inform" (Psionic Detection description)
  6. "A player whose character has psionic detection" (Psionic Detection description)
  7. "To use sign language for an entire round," (Sign Language description)
  8. "On Athas, many groups employ sign language" (Sign Language description)
  9. "A character using the somatic concealment" (Somatic Concealment description)

### Technical Details
- Function `_split_proficiency_description_paragraphs()` processes all `<p>` tags globally
- Handles multiple split markers within a single paragraph
- Uses existing `_split_paragraph_text()` utility to perform the splits
- Applied after header styling so H3 headers are already marked

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (added `_split_proficiency_description_paragraphs()`)
- `docs/chapter_5_changelog.md` (updated)

## [2025-11-10] - Header Styling and Structure Fixes

### Fixed
- Applied proper H2 and H3 styling to headers for correct visual hierarchy
- "Description of New Proficiencies" is now H2 (subheader, 1.1rem)
- Individual proficiency names (Armor Optimization, Bargain, Bureaucracy, etc.) are now H3 (sub-subheader, 1.0rem)
- Extracted "Armor Optimization:" from the Description paragraph and made it a proper H3 header
- Injected CSS styles for .h2-header and .h3-header classes
- Split Chapter 5 postprocessing into content fixes (before template) and HTML fixes (after template)

### Technical Details
- H1 headers (default): 1.2rem - section headers like "New Nonweapon Proficiencies"
- H2 headers: 1.1rem - subsection headers like "Description of New Proficiencies"
- H3 headers: 1.0rem - individual items like proficiency names
- CSS injection happens after HTML template generation
- Header class application happens before template generation

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (added header extraction, CSS injection, and styling functions)
- `tools/pdf_pipeline/postprocessors/html_export.py` (added call to HTML fixes after template generation)
- `docs/chapter_5_changelog.md` (updated)

## [2025-11-10] - New Nonweapon Proficiencies Table Reconstruction

### Fixed
- Reconstructed the "New Nonweapon Proficiencies" complex table from malformed headers
- Table properly displays 4 sections (GENERAL, PRIEST, WARRIOR, WIZARD) with 4 columns (Proficiency, Slots, Ability, Modifier)
- Removed incorrectly created headers for table columns (GENERAL, Slots, Ability, etc.) and section names
- Moved chapter 5 postprocessing to run before HTML template generation to access source headers
- Successfully extracted all 5 rows from GENERAL section: Bargain, Heat Protection, Psionic Detection, Sign Language, Water Find
- Removed all malformed table duplicates from "Description of New Proficiencies" section
- Implemented enhanced parser with lookahead to detect entry boundaries for multi-word proficiency names
- Parser now handles both normal [proficiency][ability][modifier] and reversed [ability][modifier][proficiency] patterns

### Known Limitations
- Some section boundaries may not perfectly align with source PDF due to extraction grouping multiple table rows together
- Currently extracting: GENERAL (5/5 rows ✓), PRIEST (2 rows), WARRIOR (2 rows), WIZARD (1 row)
- Section distribution differences may stem from PDF extraction limitations
- Full alignment would require improving the PDF extraction stage to properly separate table rows based on bbox coordinates

### Technical Details
- The source PDF table has individual cells as separate text spans with bbox coordinates
- Current extraction groups multiple table rows into single text blocks
- Postprocessing parses the malformed text to extract proficiency data
- Assumes Slots are always "1" based on source material
- Normalizes ability score formatting (e.g., "W i s" → "Wis")

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (added `_extract_table_data_from_paragraphs()`, `_reconstruct_nonweapon_table()`, `_remove_malformed_tables_from_descriptions()`)
- `tools/pdf_pipeline/postprocessors/html_export.py` (updated to run chapter 5 postprocessing before template generation)
- `docs/chapter_5_processing_spec.md` (updated with table documentation)
- `docs/chapter_5_changelog.md` (updated)

## [2025-01-10] - Paragraph Break Fixes

### Fixed
- Split opening content into 2 paragraphs at "Dark Sun characters often"
- Split "Dark Sun Weapon Proficiencies" section into 3 paragraphs at "For example, Barlyuth" and "A 9th-level gladiator could thus"
- Created chapter_5_postprocessing.py to handle paragraph splitting
- Integrated postprocessor into HTML export pipeline

### Technical Details
- The source PDF has these as separate text blocks (different bounding boxes)
- The transformer was incorrectly merging them into single paragraphs
- Postprocessor now splits at the correct boundaries during HTML export

### Files Modified
- `tools/pdf_pipeline/postprocessors/chapter_5_postprocessing.py` (created)
- `tools/pdf_pipeline/postprocessors/html_export.py` (updated)
- `docs/chapter_5_processing_spec.md` (updated)
- `docs/chapter_5_changelog.md` (created)

