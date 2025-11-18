# Chapter 6 Changelog — Money and Equipment

## 2025-11-11: New Equipment Section Tables Specification

### Changes Made

1. **Household Provisions**
   - Specified as H2 header
   - Identifies a table with 2 rows and 2 columns

2. **Tack and Harness**
   - Specified as H2 header

3. **Barding**
   - Specified as H3 header (sub-section under Tack and Harness)
   - Identifies a table with 6 rows and 3 columns
   - Column 2 format: `# sp` or `# cp` (where # is a number)
   - Column 3 format: `# lb` (where # is a number)

4. **Transport**
   - Specified as H2 header
   - Identifies a table with 2 columns
   - Column 2 format: `# cp` or `# sp` (where # is a number)
   - Table has 4 sections with varying row counts:
     - Chariot: 3 rows
     - Howdah: 4 rows
     - Wagon, open: 4 rows
     - Wagon, enclosed: 5 rows

### Technical Details

**Modified Files:**
- `docs/chapter_6_processing_spec.md`: Added New Equipment section documentation with detailed table specifications and validation requirements

### Validation

- Verify "Household Provisions" is H2 with table (2 rows, 2 columns)
- Verify "Tack and Harness" is H2
- Verify "Barding" is H3 under "Tack and Harness" with table (6 rows, 3 columns)
- Verify Barding table column 2 format: `# sp` or `# cp`
- Verify Barding table column 3 format: `# lb`
- Verify "Transport" is H2 with table (2 columns)
- Verify Transport table column 2 format: `# cp` or `# sp`
- Verify Transport table has 4 sections: Chariot (3 rows), Howdah (4 rows), Wagon, open (4 rows), Wagon, enclosed (5 rows)

### User Feedback

User specified: "in chapter 6 The 'New Equipment' section contains a sequence of tables. 'Household Provisions' should be an H2 thqt identifies a table with 2 rows and 2 columns. 'Tack and Harness' should be an H2. 'Barding' should be an H3. 'Barding' identifies a table with 3 columns and 6 rows; the second column is of the format '# sp' of '# cp' where # is a number; the third column is og the format '# lb' where # is a number.'. 'Transport' should be an H2. 'Transport' identifies a table with 4 sections ['Chariot', 'Howdah', 'Wagon, open', 'Wagon, enclosed']. The 'Transport' table has 2 columns, the sceond column is of the format '# cp' or '# sp' where # is a number. The 'Chariot' section has 3 rows. The 'Howdah' section has 4 rows. The 'Wagon, open' section has 4 rows. The 'Wagon, enclosed' section has 5 rows."

Resolution: Documented detailed specifications for all New Equipment section tables, including header levels, table structures, column formats, and section row counts.

## 2025-11-11: Armor Section Headers Promoted to H2

### Changes Made

1. **Header Promotions**
   - Promoted all armor section headers to H2 (subheaders with `font-size: 0.9em`)
   - All headers now display with proper Roman numerals
   - Total of 7 armor headers properly formatted

2. **Headers Formatted**
   - **Alternate Materials:** (XVII) - existing header, added H2 styling
   - **Shields:** (XVII) - extracted from paragraph text
   - **Leather Armor:** (XVIII) - existing header, added H2 styling
   - **Padded Armor:** (XIX) - existing header, added H2 styling
   - **Hide Armor:** (XX) - existing header, added H2 styling
   - **Studded Leather, Ring Mail, Brigandine, and Scale Mail Armor:** (XXI) - merged from 3 fragmented headers
   - **Chain, Splint, Banded, Bronze Plate, or Plate Mail; Field Plate and Full Plate Armor:** (XXIV) - merged from 2 fragmented headers

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/journal.py`: 
  - Updated `_fix_chapter_6_armor_headers_after_anchoring()` function
  - Adds `font-size: 0.9em` styling to armor headers with Roman numerals
  - Merges fragmented headers using HTML post-processing
  - Extracts "Shields:" from paragraph text into separate header
  
**Implementation Approach:**
- Used HTML post-processing rather than PDF-level manipulation
- More reliable for handling fragmented and embedded headers
- Operates after Roman numerals are assigned by `_add_header_anchors()`
- Preserves proper sequence of Roman numerals (XVII-XX, XXI, XXIV)

### Validation

- ✅ All 7 armor headers properly formatted as H2 (font-size: 0.9em)
- ✅ All headers have Roman numerals
- ✅ "Shields:" successfully extracted from paragraph text
- ✅ "Studded Leather..." merged from 3 fragmented headers
- ✅ "Chain, Splint..." merged from 2 fragmented headers
- ✅ Headers appear correctly in Table of Contents

### User Feedback

User specified: "'Alternate Materials:' should be an H2. 'Shields:' should be an H2. 'Leather Armor:' should be an H2. 'Padded Armor:' should be an H2. 'Hide Armor:' should be an H2. 'Studded Leather, Ring Mail, Brigandine, and Scale Mail Armor:' should be an H2. 'Chain, Splint, Banded, Bronze Plate, or Plate Mail; Field Plate and Full Plate Armor:' should be an H2."

Resolution: Implemented comprehensive HTML post-processing to promote all armor headers to H2, merge fragmented headers, and extract embedded headers from paragraphs. All 7 armor headers now display correctly with H2 styling and Roman numerals.

## 2025-11-11: Metal Armor in Dark Sun Header and Paragraph Break

### Changes Made

1. **Header Adjustment**
   - "Metal Armor in Dark Sun:" promoted to H2 (font size 10.8)
   - Header now displays with proper Roman numeral formatting

2. **Paragraph Break**
   - Added paragraph break at "Likewise, the intense heat across"
   - Section contains 3 paragraphs total (one natural break from PDF structure, plus the requested break)

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`: Added "Metal Armor in Dark Sun:" to H2 header adjustments
- `tools/pdf_pipeline/transformers/journal.py`: Added "Likewise, the intense heat across" to paragraph breaks list
- `docs/chapter_6_processing_spec.md`: Added Metal Armor in Dark Sun section documentation

**Paragraph Structure:**
1. First paragraph: "Two facts on Athas conspire to limit the use of metal armor..."
2. Second paragraph: "Simply put, a sorcerer-king can either purchase..." (natural break from PDF structure)
3. Third paragraph: "Likewise, the intense heat across Athas' barren surface..."

### Validation

- ✅ Verify "Metal Armor in Dark Sun:" is H2 header
- ✅ Verify paragraph break at "Likewise, the intense heat across"
- ✅ Verify header displays with Roman numeral

### User Feedback

User specified: "In the section 'Armor', 'Metal Armor in Dark Sun:' should be an H2. Following that there is a paragraph break at 'Likewise, the intense heat across'"

Resolution: Promoted header to H2 and added paragraph break at the specified location.

## 2025-11-11: Breaking Weapons Paragraph Break

### Changes Made

1. **Paragraph Break**
   - Added paragraph break to "Breaking Weapons" section
   - Section now contains 2 properly separated paragraphs
   - Break point at "Bruth is sent to the arena"

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/journal.py`: Added "Bruth is sent to the arena" to paragraph breaks list
- `docs/chapter_6_processing_spec.md`: Added Breaking Weapons section documentation with paragraph break specification

**Paragraph Structure:**
1. First paragraph: "Obsidian, bone, and wooden weapons are prone to breaking..."
2. Second paragraph: "Bruth is sent to the arena armed with a bone battle axe..."

### Validation

- ✅ Verify Breaking Weapons section has 2 paragraphs
- ✅ Verify paragraph break occurs at "Bruth is sent to the arena"
- ✅ Verify proper sentence structure in both paragraphs

### User Feedback

User specified: "in chapter 6 the section Breaking Weapons has 2 paragraphs with a break at 'Bruth is sent to the arena'"

Resolution: Added paragraph break configuration to split the Breaking Weapons section into 2 paragraphs at the specified location.

## 2025-11-11: Weapon Materials Table and Legend Implementation

### Changes Made

1. **Weapon Materials Table Header**
   - Fixed spacing in "W e a p o n  M a t e r i a l s  T a b l e" to "Weapon Materials Table"
   - Adjusted "Weapon Materials Table" to H3 (font size 9.6)

2. **Weapon Materials Table Structure**
   - Implemented proper HTML table with 5 columns and 5 rows
   - Top row is header: Material, Cost, Wt., Dmg*, Hit Prob.**
   - Data rows: metal, bone, stone/obsidian, wood
   - Table data was split across 3 separate PDF blocks

3. **Table Content Formatting**
   - Cost column format: `#%` (e.g., 100 %, 30 %, 50 %, 10 %)
   - Wt. column format: `#%` (e.g., 100 %, 50 %, 75 %, 50 %)
   - Dmg* column format: `-` or `-#` (e.g., -, -1, -1, -2)
   - Hit Prob.** column format: `-` or `-#` (e.g., -, -1, -2, -3)
   - Fixed whitespace issues (e.g., "10 0 %" → "100 %")

4. **Table Legend**
   - Added 2-line legend immediately after table
   - Line 1: "*The damage modifier subtracts from the damage normally done by that weapon, with a minimum of one point."
   - Line 2: "** this does not apply to missile weapons."
   - Formatted with line break (`<br/>`) and smaller font (0.9em)
   - Added via post-processing (similar to Common Wages table legend)

5. **Paragraph Breaks After Table**
   - Added paragraph breaks to create 3 separate paragraphs
   - Paragraph 1: "In the game and in text..."
   - Paragraph 2: "Nonmetal weapons detract from..."
   - Paragraph 3: "Nonmetal weapons can be enchanted..."

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`:
  - Added `_extract_weapon_materials_table()` function to extract and format table
  - Function collects data from 3 separate PDF blocks (header + 2 data rows, row 3, row 4)
  - Adjusts header to H3 (size 9.6)
  - Builds table structure with proper cell format for `_render_table`
  - Whitespace cleanup regex to handle multi-space digit sequences
  - Marks all data blocks with `__skip_render` to prevent duplicate rendering
- `tools/pdf_pipeline/transformers/journal.py`:
  - Added `__weapon_materials_table` marker handling in `_render_item`
  - Added weapon materials table to `has_special_table` check for full-width rendering
  - Modified `_coalesce_column_items` to prevent coalescing blocks with `__skip_render` markers
  - Added paragraph breaks for the 3 paragraphs after the table
  - Added post-processing to insert legend HTML after table with proper styling
  - Removes partial legend text that may have been rendered from blocks
  - Error handling for table rendering

### Validation

- ✅ Verify "Weapon Materials Table" header has correct spacing (no extra spaces)
- ✅ Verify "Weapon Materials Table" is H3
- ✅ Verify table has 5 columns
- ✅ Verify table has 5 rows (1 header + 4 data)
- ✅ Verify header row: Material, Cost, Wt., Dmg*, Hit Prob.**
- ✅ Verify all 4 material rows: metal, bone, stone/obsidian, wood
- ✅ Verify Cost column values: 100 %, 30 %, 50 %, 10 %
- ✅ Verify Wt. column values: 100 %, 50 %, 75 %, 50 %
- ✅ Verify Dmg* column values: -, -1, -1, -2
- ✅ Verify Hit Prob.** column values: -, -1, -2, -3
- ✅ Verify no duplicate rendering of table data
- ✅ Verify no incorrect headers ("Cost", "Material", etc.) appearing before the table
- ✅ Verify legend appears immediately after table with 2 lines
- ✅ Verify legend line 1: "*The damage modifier subtracts from the damage normally done by that weapon, with a minimum of one point."
- ✅ Verify legend line 2: "** this does not apply to missile weapons."
- ✅ Verify legend has line break between lines (`<br/>` tag)
- ✅ Verify legend has smaller font (0.9em styling)
- ✅ Verify 3 separate paragraphs after legend
- ✅ Verify paragraph 1 starts with "In the game and in text"
- ✅ Verify paragraph 2 starts with "Nonmetal weapons detract from"
- ✅ Verify paragraph 3 starts with "Nonmetal weapons can be enchanted"

### User Feedback

User specified: ""W e a p o n  M a t e r i a l s  T a b l e" has incorrect spacing, it should say "Weapon Materials Table". "Weapon Materials Table" should be an H3. "Weapon Materials Table" identifies a table with 5 columns and 5 rows. The top row is a header row with value [Material, Cost, Wt., Dmg*, Hit Prob.**]. The Cost column has the format "#%" where # is a number. The "Wt." column has the format "#%" where # is a number. The "Dmg*" column has the format "-" or "-#" where # is a number. The "Hit Prob.**" column has the format "-" or "-#" where # is a number."

User specified: "Underneath the "Weapon Materials Table" is a 2 line legend. The first line is "*The damage modifier subtracts from the damage normally done by that weapon, with a minimum of one point." and the second is "** this does not apply to missile weapons.". Then come 3 paragraphs of text "In the game and in text", "Nonmetal weapons detract from", "Nonmetal weapons can be enchanted"."

Resolution: Implemented proper table extraction from multiple PDF blocks, fixed header spacing, adjusted to H3, ensured all formatting specifications were met. Added 2-line legend with proper styling (line break and smaller font) via post-processing. Added paragraph breaks to create 3 separate paragraphs after the legend.

## 2025-11-11: Weapons Section Formatting

### Changes Made

1. **Weapons Header Adjustment**
   - Adjusted "Weapons" header (after "Athasian Market: List of Provisions") to H2
   - Header size changed from 11.76 to 10.8 (H2 size)
   - Ensured only the first "Weapons" header (not others in the document) is adjusted

2. **Weapons Section Paragraph Breaks**
   - Added paragraph breaks to create 4 paragraphs in the Weapons section
   - Break points:
     - "The following weapons,"
     - "The remaining weapons"
     - "The arquebus is unavailable"

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`:
  - Updated `_adjust_header_sizes()` to detect and adjust the "Weapons" header after "Athasian Market"
  - Uses flag to ensure only the first "Weapons" header (size ~11.76) is adjusted
- `tools/pdf_pipeline/transformers/journal.py`:
  - Added paragraph breaks for Weapons section

### Validation

- ✓ Verify "Weapons" after "Athasian Market: List of Provisions" is H2
- ✓ Verify Weapons section has 4 paragraphs
- ✓ Verify paragraph breaks at specified points
- ✓ Verify other "Weapons" headers in the document are not affected

### User Feedback

User specified: "Beneath 'Athasian Market: List of Provisions', 'Weapons' should be an H2. The 'weapons' section has 4 paragraphs with breaks at 'The following weapons,', 'The remaining weapons', 'The arquebus is unavailable'."

Resolution: Adjusted the Weapons header to H2 and implemented paragraph breaks at all specified points.

## 2025-11-11: Athasian Market Header Merge

### Changes Made

1. **Header Merge**
   - Merged "Athasian Market: List of" and "Provisions" into single header
   - Single header now reads: "Athasian Market: List of Provisions"
   - These were split across two lines in the source PDF but should be treated as one header

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`:
  - Added `_merge_athasian_market_header()` function to merge consecutive header lines
  - Function searches for "Athasian Market: List of" followed by "Provisions" within same block
  - Merges the text and removes the duplicate line
  - Updated `apply_chapter_6_adjustments()` to call header merge function

### Validation

- ✓ Verify "Athasian Market: List of Provisions" is a single header (header-10)
- ✓ Verify "Weapons" is the next header (header-11) after the merged header
- ✓ Verify table of contents shows merged header correctly

### User Feedback

User specified: "In chapter 6, 'Athasian Market: List of Provisions' should be on a single line."

Resolution: Implemented header merging logic to combine the two lines into a single header at the PDF extraction stage.

## 2025-11-11: Initial Character Funds Table Implementation

### Changes Made

1. **Initial Character Funds Table Structure**
   - Implemented proper HTML table for "Initial Character Funds" section
   - Table contains 2 columns: Character Group, Die Range
   - 6 rows total: 1 header row + 5 data rows
   - Die Range format: `#d# x #cp`

2. **Table Content**
   - Warrior: 5d4 x 30cp
   - Wizard: (1d4+1) x 30cp
   - Rogue: 2d6 x 30cp
   - Priest: 3d6 x 30cp
   - Psionicist: 3d4 x 30cp

3. **Header Adjustments**
   - "Initial Character Funds" promoted to H2 (font size 10.8)
   - "Character Group" and "Die Range" converted from separate headers to table header cells

4. **Paragraph Flow**
   - "Starting Money" section now has 2 properly separated paragraphs
   - Break point at "The following table indicates"

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`:
  - Added "Initial Character Funds" to H2 header adjustments in `_adjust_header_sizes()`
  - Added `_extract_initial_character_funds_table()` function to build table structure
  - Updated `apply_chapter_6_adjustments()` to call Initial Character Funds table extraction
  - Removed fragmented table pieces and malformed headers between Initial Character Funds and Athasian Market
- `tools/pdf_pipeline/transformers/journal.py`:
  - Added `__initial_character_funds_table` marker handling in renderer
  - Added "The following table indicates" to paragraph breaks list
- `docs/chapter_6_processing_spec.md`:
  - Added comprehensive Initial Character Funds table documentation
  - Updated validation requirements

### Validation

- ✓ Verify "Initial Character Funds" is H2 header
- ✓ Verify table has 2 columns
- ✓ Verify table has 6 rows (1 header + 5 data)
- ✓ Verify "Character Group" and "Die Range" are table header cells, NOT separate headers
- ✓ Verify all 5 character classes are present with correct die ranges
- ✓ Verify die range format is `#d# x #cp`
- ✓ Verify 2 paragraphs in "Starting Money" section
- ✓ Verify paragraph break at "The following table indicates"

### User Feedback

User specified: "In chapter 6 in the section Starting Money there are two paragraphs with the break at 'The following table indicates'. 'Initial Character Funds' is an H2. 'Initial Character Funds' identifies a table with 2 columns and 6 rows. The top row is a header row [Character Group, Die Range]. The 'Die Range' column values are formatted '#d# x #cp' where # is an integer. 'Athasian Market: List of Provisions' is the next section."

Resolution: Implemented proper table structure with correct header hierarchy, converted separate headers to table cells, and added paragraph break in Starting Money section.

## 2025-11-10: Common Wages Table Implementation

### Changes Made

1. **Common Wages Table Structure**
   - Implemented proper HTML table for "Common Wages" section
   - Table contains 4 columns: Title, Daily, Weekly, Monthly
   - Two sections: Military (10 rows) and Professional (3 rows)
   - Added legend entries beneath table

2. **Table Content**
   - Military section includes: Archer/artillerist, Cavalry (heavy/light/medium), Foot soldiers (heavy/light/militia/medium), Lieutenant, Officer/commander
   - Professional section includes: Unskilled labor, Skilled labor, Professional
   - Legend: `*available only in some city-states`, `**available only in cities with organized militaries`

3. **Paragraph Flow**
   - Text between "Protracted Barter" and "Common Wages" belongs to "Protracted Barter"
   - "With both barter and service exchanges" starts new paragraph after table and legend

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`:
  - Added `_clean_whitespace()` function to clean extraneous spaces
  - Added `_extract_common_wages_table()` function to build table structure
  - Updated `apply_chapter_6_adjustments()` to call table extraction
  - Added block removal logic to prevent duplicate rendering
- `tools/pdf_pipeline/transformers/journal.py`:
  - Added `__common_wages_table` marker handling in renderer
  - Added `__skip_render` marker to skip duplicate blocks
- `docs/chapter_6_processing_spec.md`:
  - Added comprehensive Common Wages table documentation

### Validation

- ✓ Verify table has 4 columns
- ✓ Verify Military section has 10 rows
- ✓ Verify Professional section has 3 rows
- ✓ Verify legend appears below table
- ✓ Verify "With both barter" starts new paragraph
- ✓ Verify no duplicate rendering of table data

### User Feedback

User specified: "Text between 'Protracted Barter' and 'Common Wages' is part of 'Protracted Barter'. 'Common Wages' identifies a table with 4 columns and 2 sections [Military, Professional]. The column headers are [Title, Daily, Weekly, Monthly]. The Military section has 10 rows. The Professional section had 3 rows. Beneath the table is a legend containing 2 entries. 'With both barter and service exchanges' is a new paragraph."

Resolution: Implemented proper table structure with all specified columns, sections, rows, and legend. Ensured proper paragraph separation.

## 2025-11-10: Header Size Adjustments and Additional Paragraph Breaks

### Changes Made

1. **Header Size Adjustments**
   - Created `chapter_6_processing.py` module to adjust header sizes in "Monetary Systems" section
   - Adjusted "Barter:", "Simple Barter:", "Protracted Barter:", and "Service:" to H2 (font size 10.8)
   - Adjusted "Common Wages" to H3 (font size 9.6)
   - Split "Service:" from embedded text into separate header span

2. **Additional Paragraph Breaks**
   - Implemented paragraph breaks for "Protracted Barter" section
   - Total of 3 paragraphs properly separated
   - Break points configured in `journal.py` transformer

### Technical Details

**Modified/Created Files:**
- `tools/pdf_pipeline/transformers/chapter_6_processing.py`: NEW - Header size adjustment logic
- `tools/pdf_pipeline/transformers/journal.py`: Updated to call `apply_chapter_6_adjustments()` and added Protracted Barter paragraph breaks
- `docs/chapter_6_processing_spec.md`: Documented header adjustments and all paragraph break specifications

**Header Adjustments:**
- Barter: → H2 (size 10.8)
- Simple Barter: → H2 (size 10.8)
- Protracted Barter: → H2 (size 10.8)
- Service: → H2 (size 10.8, split from text)
- Common Wages → H3 (size 9.6)

**Protracted Barter Paragraph Break Points:**
1. First paragraph: "Protracted Barter: This more complicated method..."
2. Second paragraph: "In the first round..."
3. Third paragraph: "If Kyuln from the previous example..."

### Validation

- Added automated tests to verify header sizes and paragraph structure
- Ensured proper sentence joining without hyphenation artifacts
- Confirmed relative links and master TOC link functionality

### User Feedback

User reported: "In the 'Monetary Systems' section the following are all H2: 'Barter:', 'Simple Barter:', 'Protracted Barter:' 'Protracted Barter' contains 3 paragraphs with breaks at 'In the first round', 'If Kyuln from the previous example'. 'Service:' is an H2. 'Common Wages' is an H3."

Resolution: Implemented header size adjustments via chapter-specific processing and added paragraph breaks for the Protracted Barter section.

## 2025-11-10: Paragraph Break Implementation

### Changes Made

1. **Paragraph Breaks Added**
   - Implemented paragraph breaks for "What Things Are Worth" section
   - Total of 7 paragraphs properly separated
   - Break points configured in `journal.py` transformer

### Technical Details

**Modified Files:**
- `tools/pdf_pipeline/transformers/journal.py`: Added Chapter 6 paragraph break logic in `transform()` function
- `docs/chapter_6_processing_spec.md`: Documented paragraph break specifications and validation requirements

**Paragraph Break Points:**
1. First paragraph: "The equipment lists in the Players Handbook..."
2. Second paragraph: "On Athas, the relative rarity..."
3. Third paragraph: "All nonmetal items cost one percent..."
4. Fourth paragraph: "All metal items cost the price listed..."
5. Fifth paragraph: "Thus, the small canoe (a nonmetal item)..."
6. Sixth paragraph: "If an item is typically a mixture of metal..."
7. Seventh paragraph: "All prices listed in the DARK SUN..."

### Validation

- Added automated tests to verify paragraph structure
- Ensured proper sentence joining without hyphenation artifacts
- Confirmed relative links and master TOC link functionality

### User Feedback

User reported: "In chapter 6 Money and Equipment section 'What Things Are Worth' there are 7 paragraphs with break at 'On Athas, the relative rarity', 'All nonmetal items cost one percent', 'All metal items cost the price listed', 'Thus, the small canoe (a nonmetal item)', 'If an item is typically a mixture of metal', 'All prices listed in the'"

Resolution: Implemented paragraph breaks at all specified points to maintain the correct paragraph structure from the source material.

## Future Enhancements

- Monitor for any additional sections in Chapter 6 that may require paragraph break adjustments
- Consider adding validation checks for table formatting if issues arise

