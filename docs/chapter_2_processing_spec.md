# Chapter 2 Processing Specification

## Overview

Chapter Two: Player Character Races requires extensive custom processing due to complex table layouts, multi-column text fragmentation, and PDF extraction artifacts. This document specifies all processing steps applied to ensure accurate extraction and rendering.

## Source Files

- **Main Implementation:** `tools/pdf_pipeline/transformers/chapter_2_processing.py`
- **Archived HTML Post-processing:** `archive/old_implementation/tools/pdf_pipeline/postprocess.py`
- **Section:** "Chapter Two: Player Character Races" (pages 5-20 of PDF)

## Processing Pipeline

### Stage 1: PDF-Level Processing (Pre-Transformation)

Applied in `chapter_2_processing.py` via `apply_chapter_2_adjustments(section_data)`.

#### Page 0 (PDF page 5) - Tables and Adjustments

**1. Table 2: Ability Adjustments**
- **Location:** Between heading and "Racial Ability Requirements"
- **Columns:** 2 (Race, Adjustments)
- **Rows:** 7 races (Dwarf, Elf, Half-Elf, Half-Giant, Halfling, Mul, Thri-kreen)
- **Processing:**
  - Detect table boundaries (y-coordinates between headings)
  - Extract cells from blocks within boundaries
  - Build 2-column matrix with 4.0pt row tolerance
  - Merge fragmented adjustment text (e.g., multi-line ability lists)
  - Remove trailing commas from adjustments
  - Clear processed blocks after table extraction

**2. Racial Ability Requirements Table**
- **Location:** After "Racial Ability Requirements" heading
- **Columns:** 8 (Ability, 7 race columns)
- **Rows:** 7 abilities (Strength through Charisma)
- **Processing:**
  - Detect header block containing all race names
  - Extract cells up to next table heading or end of page
  - Build 8-column matrix
  - Filter rows to allowed abilities only
  - **Reposition table:** Move to appear BEFORE Ability Adjustments table
  - Sort tables by Y-coordinate for correct rendering order
  - Clean up isolated ability/race labels from text blocks

#### Page 1 (PDF page 6) - Class Limits

**3. Table 3: Racial Class And Level Limits**
- **Location:** After heading, before footer
- **Columns:** 9 (Class, 7 race columns, Notes)
- **Rows:** 13 classes (Bard through Thief)
- **Footer markers:** Lines starting with "U:", "Any #", "-:", "The Player"
- **Processing:**
  - Detect table boundaries (heading to footer)
  - Build 9-column matrix with 4.0pt row tolerance
  - Filter rows to allowed class names
  - Position heading directly above table (2pt spacing)
  - Clear table content blocks

#### Page 2 (PDF page 7) - Dwarves Section

**4. Dwarves Text Ordering Fix**
- **Problem:** Sentence fragments appear out of order:
  - "The task to which a dwarf is presently committed" appears at end
  - Should precede "is referred to as his focus"
  - "for compromise in the mind of a dwarf" should follow "There is very little room"
- **Processing:**
  - Find block containing "is referred to as his focus"
  - Find block containing "There is very little room"
  - Find duplicate block with both problem sentences
  - Prepend "The task..." to focus block's first span
  - Append "for compromise..." line to "little room" block
  - Remove duplicate block
  - Update block bounding boxes

**5. Other Languages Table**
- **Location:** After "Other Languages" heading, before "Dwarves"
- **Columns:** 2 (left and right lists)
- **Processing:**
  - Detect narrow blocks (width < 140pt) in heading boundaries
  - Build 2-column matrix
  - Filter to allowed language names
  - No header row (data starts immediately)

#### Other Characteristics (Height, Weight, Age)

**6. Height and Weight Table**
- **Location:** Between "Other Characteristics" intro and "Age" header
- **Columns:** 5 displayed (Race | Height Base | Height Modifier | Weight Base | Weight Modifier)
- **Rows:** 10 total (2 header rows + 8 race rows)
- **Header structure:**  
  - Row 1: Race (rowspan=2) | Height in Inches (colspan=2) | Weight in Pounds (colspan=2)  
  - Row 2: Base | Modifier | Base | Modifier
- **Processing (NO hard-coded values):**
  - Detect left group header ("Height in Inches", with "Race", "Base", "Modifier") and right group header ("Weight in Pounds", with "Base", "Modifier")
  - Derive column x-positions from header label bboxes (no fixed coordinates)
  - Build row anchors from the left-most column (race names) within the section bounds (from "Height and Weight" header to the next major header)
  - For each row anchor, locate nearest cells at the four target column x-centers (height base/modifier, weight base/modifier) using y-tolerance
  - Construct a table with `header_rows=2`, preserving multi-row/col spans
  - Clear header label blocks and row fragments used for the table while preserving footnotes (e.g., thri-kreen length note)

Note: The Starting Age and Aging Effects tables are still being migrated to programmatic extraction and may temporarily use reconstruction rules. These will be replaced in subsequent iterations.

**7. Starting Age Table**
- **Location:** Between the "Starting Age" subheader and the "Aging Effects" subheader
- **Columns:** 4, with 2 header rows  
  - Row 1: Race (rowspan=2) | Starting Age (colspan=2) | Maximum Age Range (Base + Variable) (rowspan=2)  
  - Row 2: Base Age | Variable
- **Processing (NO hardcoded values):**
  - Derive x-centers from the subheaders: "Base Age", the left "Variable" (Starting Age, not the right-side one), and "(Base + Variable)"
  - Build row anchors from Base Age integer values; for each anchor y:
    - Race: nearest left-side text at the same y
    - Base Age: integer near "Base Age" x-center
    - Variable: dice expression near the left "Variable" x-center (e.g. 4d6)
    - Maximum Age Range (Base + Variable): expression like "200 + 3d20" near the "(Base + Variable)" x-center
  - Remove any pre-existing tables within the section bounds to avoid borderless detector artifacts and insert the clean table with `header_rows=2`
  - Clear table header label lines within section bounds so they do not render as document headers: remove "Race", "Base Age", "Variable", "(Base + Variable)", and "Maximum Age Range"

**8. Aging Effects Table**
- **Location:** From the "Aging Effects" subheader to the next major header or page end
- **Columns:** 4 (Race | Middle Age* | Old Age** | Venerable***)
- **Processing (NO hardcoded values):**
  - Derive x-centers from the subheaders "R a c e", "Middle Age*", "Old Age**", and "Venerable***"
  - Build candidate row anchors from numeric cells under any of the three numeric columns; for each anchor y:
    - Race: nearest left-side text at the same y (excluding headers and legend text)
    - Middle, Old, Venerable: nearest numbers (or '-') under their respective x-centers
  - Remove pre-existing tables in the section bounds; insert the clean table with `header_rows=1`
  - Preserve star legend text as paragraph content (not part of the table)
  - Clear table header label lines within section bounds so they do not render as document headers: remove "Race"/"R a c e", "Middle Age*", "Old Age**", and "Venerable***"

#### Page 3 (PDF page 8) - Elves Paragraph Breaks

**6. Elves Section - 11 Paragraphs**
- **Problem:** Two-column layout merges 11 paragraphs into 1
- **Solution:** Force paragraph breaks at specific sentence starts:
  1. "The dunes and steppes of Athas"
  2. "Elves are all brethren"
  3. "Individually, tribal elves"
  4. "Elves use no beasts"
  5. "While most elven tribes"
  6. "Elven culture"
  7. "A player character elf"
  8. "Elves are masterful warriors"
  9. "Elves gain a bonus to surprise"
  10. "Elves have no special knowledge"
  11. "With nimble fingers"
- **Processing:**
  - Mark blocks starting with these sentences: `__force_paragraph_break = True`

#### Page 4 (PDF page 9) - Elves Roleplaying

**7. Elves Roleplaying - 3 Paragraphs**
- **Problem:** 3 paragraphs merge into 1
- **Solution:** Force breaks at:
  1. "Elves have no great love..." (implicit start)
  2. "When encountering outsiders"
  3. "Elves never ride on beasts"
- **Special handling:** Split mid-line at "transportation." if followed by content
- **Processing:**
  - Mark lines: `__force_line_break = True`
  - Mark split points: `__split_at_transportation = True`

#### Pages 4-5 (PDF pages 9-10) - Half-Elves

**8. Half-Elves Section - 11 Paragraphs**
- **Problem:** Heavy fragmentation across two-column, two-page layout
- **Solution:** Force breaks at:
  1. "Elves and humans travel"
  2. "A half-elf is generally tall"
  3. "A half-elf'salife is typically" (note: PDF typo, no space)
  4. Mid-line: ". Rarely do half-" (spans pages)
  5. "Intolerance, however, has given"
  6. "The skills involved in survival"
  7. "Coincidentally, faced with"
  8. Mid-line: ". Also, some half-elves turn"
  9. "Half-elves add one to their"
  10. "A half-elf character can choose"
  11. "A half-elf gains some benefits"
- **Processing:**
  - Mark lines: `__force_line_break = True`
  - Mid-sentence splits: `__split_at_rarely = True`, `__split_at_also = True`

#### Pages 5-6 (PDF pages 10-11) - Half-Elves Roleplaying

**9. Half-Elves Roleplaying - 3 Paragraphs**
- **Problem:** "For example..." block appears BEFORE "Roleplaying:" header in block order
- **Solution:**
  1. "Roleplaying: Half-elves pride..." (implicit start)
  2. "For example, when a half-elf" (reordered block)
  3. "Despite their self-reliance"
- **Processing:**
  - Mark all blocks: `__roleplaying_section = True`
  - Mark paragraph starts: `__force_paragraph_break = True`
  - Special handling for "For example" block reordering

#### Pages 6-7 (PDF pages 11-12) - Half-Giants

**10. Half-Giants Section - 10 Paragraphs**
- **Problem:** Heavy fragmentation across pages
- **Solution:** Force breaks at:
  1. "Giants dominate many"
  2. "A half-giant is an enormous"
  3. "A half-giant character can be"
  4. "Simply put, a half-giant gains"
  5. Mid-line: "die. Though no one knows for certain" OR "die. seem to be a fairly young race"
  6. "All personal items such as"
  7. "Half-giants sometimes collect"
  8. "Half-giants can switch their"
  9. "This is not to say"
  10. "Half-giant characters add four"
- **Processing:**
  - Mark section blocks: `__half_giants_section = True`
  - Mark line breaks: `__force_line_break = True`
  - Mid-sentence splits: `__split_at_mid_sentence = pattern`

### Stage 2: HTML Post-Processing (Archived)

Located in `archive/old_implementation/tools/pdf_pipeline/postprocess.py`.

**Note:** These HTML-level fixes are currently disabled in the new pipeline (see `journal.py` lines 1109-1112). They may need to be re-enabled or migrated to the new postprocessor framework.

#### HTML Fixes Applied (from archived code)

1. **_fix_table_3_position** - Repositions Table 3 in HTML output
2. **_fix_chapter_two_races** - General race section fixes
3. **_fix_thri_kreen_section** - Thri-kreen specific paragraph handling
4. **_fix_height_weight_table** - Table formatting for height/weight data
5. **_fix_age_table** - Age table formatting
6. **_fix_aging_effects_table** - Aging effects table formatting

## Table Specifications

### Table 2: Ability Adjustments

```
Race         | Adjustments
-------------|--------------------------------------------------
Dwarf        | Constitution +2, Charisma -1
Elf          | Dexterity +2, Constitution -1
Half-Elf     | None
Half-Giant   | Strength +4, Constitution +2, Intelligence -2, Wisdom -2, Charisma -1
Halfling     | Dexterity +2, Strength -1
Mul          | Strength +2, Constitution +1
Thri-kreen   | Strength +2, Dexterity +4, Constitution +2, Intelligence -1, Wisdom -1, Charisma -2
```

### Racial Ability Requirements

8 columns: Ability | Dwarf | Elf | H-Elf | H-giant | Halfling | Mul | Thri-kreen

### Table 3: Racial Class And Level Limits

9 columns: Class | Dwarf | Elf | H-Elf | H-giant | Halfling | Mul | Thri-kreen | Notes

### Other Languages (Dwarves section)

2-column list format, no headers

## Special Markers Used

### Block-Level Markers
- `__force_paragraph_break` - Force new paragraph at block start
- `__roleplaying_section` - Mark Roleplaying section blocks
- `__half_giants_section` - Mark Half-Giants section blocks

### Line-Level Markers
- `__force_line_break` - Force new paragraph at line start
- `__split_at_transportation` - Split line at "transportation."
- `__split_at_rarely` - Split line at ". Rarely"
- `__split_at_also` - Split line at ". Also"
- `__split_at_mid_sentence` - Split at specified pattern

## Known Issues & Limitations

1. **PDF Typos Preserved:**
   - "A half-elf'salife" (no space) in source PDF
   - Processed as-is for accuracy

2. **HTML Post-Processing Disabled:**
   - Original HTML fixes in archived `postprocess.py` are commented out
   - May cause rendering issues in some tables/sections
   - TODO: Migrate to new HTMLExportPostProcessor if needed

3. **Page Detection Improvements:**
   - For the Other Characteristics tables, pages are located dynamically by header text instead of fixed indices.
   - Some earlier sections may still rely on assumed indices and are being migrated.

4. **Fragile Text Matching:**
   - Relies on exact text matches for paragraph boundaries
   - Minor PDF changes could break detection

## Testing Recommendations

1. **Visual Inspection:**
   - Open `data/html_output/chapter-two-player-character-races.html`
   - Verify all 3 tables render correctly
   - Check paragraph breaks in each race section

2. **Comparison:**
   - Compare with `data/verification/chapter-two-player-character-races.html` (archived)
   - Note differences due to disabled post-processing

3. **Structural Validation:**
   - Check `data/processed/journals/chapter-two-player-character-races.json`
   - Verify table structure and content

4. **Ancestry Data:**
   - Verify `data/processed/ancestries.json` contains all 7 races
   - Check ability adjustments match Table 2

## Future Enhancements

1. **Re-enable HTML Post-Processing:**
   - Port archived fixes to new HTMLExportPostProcessor
   - Or integrate into journal transformer

2. **Reduce Fragility:**
   - Use more robust text matching (regex, fuzzy matching)
   - Add fallback logic for PDF variations

3. **Automated Testing:**
   - Unit tests for each table extraction
   - Paragraph break detection tests
   - End-to-end visual regression tests

4. **Documentation Generation:**
   - Auto-generate table of races with stats
   - Create quick reference cards from extracted data

---

**Last Updated:** November 8, 2025  
**Implementation:** `tools/pdf_pipeline/transformers/chapter_2_processing.py`  
**Status:** ✅ Active (PDF-level processing)  
**HTML Post-processing:** ⚠️ Disabled (needs migration)



