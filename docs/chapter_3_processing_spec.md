# Chapter 3 Processing Spec — Player Character Classes

This document describes the chapter-specific processing applied to `chapter-three-player-character-classes` with a focus on the “Multi-Class and Dual-Class Characters” section.

## Goals
- Preserve all narrative paragraphs exactly as extracted (no data loss).
- Reconstruct the multi-class combination lists as structured tables per race.
- Maintain correct reading order across the 2-column layout.
- Format headers according to project rules (H1 with roman numerals, H2/H3/H4 with inline [^] links).

## Multi-Class and Dual-Class Characters

### Expected Structure
1. H1: “Multi-Class and Dual-Class Characters”
2. Paragraph: “Dark Sun characters can become multi-or dualclass just, as described in the Players Handbook.”
3. H2: “Multi-Class Combinations”
4. Intro paragraph (must be preserved):
   - Any demihuman character who meets the ability requirements may elect to become a multi-class character, subject to the restrictions presented in the Players Handbook.
   - The following chart lists the possible character class combinations available based upon the race of the character.
5. Race subheaders (H2): Dwarf; Elf or Half-elf; Half-giant; Halfling; Mul; Thri-kreen
6. One 2-column table per race with combinations (class pairs/triples).
7. Substitution rules paragraph: begins “Defiler or preserver can be substituted...”

### Special Handling
- Header Fix: The H1 may be split across two lines in the source; we merge these into a single header.
- Table Reconstruction: Free-text rows containing combinations (e.g., “Fighter/Cleric”) are cleared and rebuilt into structured tables.
- Paragraph Preservation: No aggressive clearing of blocks in this section. Only multi-class combination fragments are removed; narrative paragraphs (including the intro and substitution rules) are preserved.
- Substitution Rules Formatting: The block of text following the Thri-kreen table (“Defiler or preserver...” through “combination for demihumans.”) is split into separate paragraphs per sentence for readability.
- Ordering: All content appears in right-column order on page 39 and left-column order on page 40, matching reading order.

## Validation
- H1 must be a single header (no stray “Characters” header).
- The intro paragraph content between “Multi-Class Combinations” and “Dwarf” must contain:
  - “Any demihuman character…”
  - “The following chart lists the possible character class combinations available…”
  - “…based upon the race of the character.”
- Six race headers must be present with tables of the expected dimensions.
- Substitution rules sentences should render as distinct paragraphs (multiple <p> tags, not a single long paragraph).

## TOC and Headers
- H1 headers include roman numerals and inline [^] links.
- H2/H3/H4 are styled as subheaders with inline [^] links (not document headers).

## Templar Spell Progression

### Expected Structure
- H2: "Templar Spell Progression"
- Single table with:
  - 2 header rows (with rowspan and colspan for proper structure)
  - 20 data rows (levels 1-20)
  - 8 columns: Templar Level + 7 spell levels (1-7)

### Special Handling
- **Critical Fix (2025-11-12)**: The borderless table detection was creating hundreds (713) of malformed tables from fragmented spell progression data. The fix replaces ALL tables on page 35 with a single corrected table built from authoritative reference data.
- Table uses rowspan and colspan in headers for proper structure
- All spell slots are rendered correctly for levels 1-20
- Source data had typos (e.g., "17" instead of "19") which are corrected using reference data

### Validation
- Exactly ONE table appears under the "Templar Spell Progression" header
- Table has 22 rows total (2 header + 20 data)
- All levels 1-20 are present with correct spell slot progressions

## Rangers Followers Section

### Expected Structure
1. Paragraphs describing ranger abilities and followers (ending with "At 10th level, a ranger attracts 2d6 followers...")
2. H2: "RANGERS FOLLOWERS"
3. Rangers Followers d100 table (24 rows: 1 header + 23 data)
4. Paragraph: "A rangers motivations can vary greatly..."

### Special Handling
- **Header Rendering**: The "RANGERS FOLLOWERS" header block is marked with `__followers_header` and rendered as an H2 tag with an inline link back to the top of the document.
- **Full-Width Treatment**: Both the header and table marker blocks are treated as full-width to ensure correct rendering order in multi-column layout.
- **Ordering Fix**: The "A rangers motivations" paragraph appears at the bottom of the LEFT column (y: ~708) while the "RANGERS FOLLOWERS" header appears in the RIGHT column (y: ~648). Visually, the header is ABOVE the motivations paragraph, so the motivations block is moved to appear after the table marker.
- **Table Reconstruction**: The Rangers Followers table is reconstructed from fragmented data on page 7 (index 7) and inserted as a marker block on page 6 (index 6) immediately after the "RANGERS FOLLOWERS" header. All malformed tables on page 7 are cleared after reconstruction.
- **Coalescing Prevention**: The header block is excluded from coalescing with other blocks to preserve its marker.
- **Paragraph Breaks**: The "A rangers motivations" block is marked with `__force_paragraph_break` to ensure it starts a new paragraph.
- **Critical Fix (2025-11-18)**: The PDF extraction creates multiple malformed tables that mix paragraph text with table data (e.g., "largely unchanged. The wilderness is harsh and unforgiving..." mixed with "01-04 Aarakocra"). The `reconstruct_rangers_followers_table_inplace()` function now:
  1. Finds ALL malformed tables containing Rangers Followers data (not just one)
  2. Removes ALL malformed tables from the page
  3. Reconstructs a single correct table with proper d100 ranges and follower types
  4. This prevents multiple broken tables from appearing in the output

### Validation
- The "RANGERS FOLLOWERS" header should be followed immediately by the table
- The "A rangers motivations" paragraph should appear after the table
- The table should have 24 rows (1 header + 23 data rows with d100 ranges)
- NO malformed tables should exist between "the ranger answers that challenge" and "A rangers motivations can vary greatly"
- Only ONE Rangers Followers table should exist in the entire chapter

## Notes
- Dehyphenation and line merging are handled prior to chapter-specific processing.
- No content is hard-coded; all data is derived from the source extraction.


## Character Trees

### Expected Structure
1. H1: “Character Trees”
2. Four paragraphs (in order):
   - Starts “DARK SUN campaigns are set in a violent world...” and ends with “...for player characters in DARK SUN campaigns.”
   - Starts “Replacing a fallen player character of high level...”
   - Starts “In DARK SUN campaigns, players are encour-” (continues “aged to use character trees...”)
   - Starts “In brief, a character tree consists of one active...”

### Special Handling
- Paragraph Break Hints: Added start-of-line break hints to ensure the four paragraphs split at:
  - “Replacing a fallen player character of high level”
  - “In DARK SUN campaigns, players are encour-”
  - “In brief, a character tree consists of one active”
- These hints are scoped to `chapter-three-player-character-classes` only.

### Validation
- The “Character Trees” section renders those four distinct `<p>` blocks in order, prior to the subsequent subheaders (e.g., “Setting Up a Character Tree”).

## Alignment (Character Trees)

### Expected Structure
Four paragraphs immediately under the `Alignment` subheader:
1. Starts “The four characters that make up a players character tree…” and ends “…difference, however.”
2. Starts “For example, one character tree might…”
3. Starts “If a character is forced to change alignment…”
4. Starts “Discarded characters should be given…”

### Special Handling
- Paragraph Break Hints added for:
  - “For example, one character tree might”
  - “If a character is forced to change alignment”
  - “Discarded characters should be given to the”

### Validation
- Exactly 4 `<p>` elements appear between the `Alignment` subheader and the next subheader, and paragraphs 2–4 start with the phrases above (allowing for dehyphenation).

## Character Advancement

### Expected Structure
Four paragraphs (in order) under the `Character Advancement` subheader:
1. Starts “The active character in a campaign receives experience points and advances in levels…”
2. Starts “Every time the active character …”
3. Starts “For purposes of character tree …”
4. Starts “For inactive multi-class characters …”

### Special Handling
- Paragraph Break Hints added for:
  - “Every time the active character goes up a level of”
  - “For purposes of character tree advancement,”
  - “For inactive multi-class characters, care must be”

### Validation
- Exactly 4 `<p>` elements appear between the `Character Advancement` subheader and the next subheader, and paragraphs 2–4 start with the phrases above (allowing for dehyphenation).

## The Status of Inactive Characters

### Expected Structure
Three paragraphs (in order) under the `The Status of Inactive Characters` subheader:
1. Opening paragraph about inactive characters’ general status.
2. Starts “When not in play,”
3. Starts “All characters in a character …”

### Special Handling
- Paragraph Break Hints added for:
  - “When not in play, inactive characters are assumed”
  - “All characters in a character tree are assumed to”

### Validation
- Exactly 3 `<p>` elements appear between this subheader and the next subheader, and paragraphs 2–3 start with the phrases above (allowing for dehyphenation).

## Using the Character Tree to Advantage

### Expected Structure
Three paragraphs with breaks at:
1. Starts “As only one inactive character gains …”
2. Starts “As another example, the quest might …”

### Special Handling
- Paragraph Break Hints added for:
  - “As only one inactive character gains a level of”
  - “As another example, the quest might”

## Exchanges Between Characters

### Expected Structure
Four paragraphs with breaks at:
1. Starts “In some instances …”
2. Starts “DARK SUN …”
3. Starts “As stated in the …”

### Special Handling
- Paragraph Break Hints added for:
  - "In some instances, if there is a compelling reason"
  - "DARK SUN"
  - "As stated in the"

## Player Class Requirements Tables

### Expected Structure
Every player class in Chapter 3 must have a requirements table immediately following the class name header. This table has a standard format:

**Structure:**
- 2 columns: Label | Value
- 3 rows:
  1. Ability Requirements: list of "Ability #" pairs (e.g., "Strength 9", "Dexterity 12")
  2. Prime Requisite: one or more ability names (e.g., "Strength" or "Strength, Dexterity")
  3. Races Allowed: list of races (e.g., "All", "Human, Elf, Half-elf")

**Player Classes with Requirements Tables:**
- **Warriors**: Fighter, Gladiator, Ranger
- **Wizards**: Defiler, Preserver, Illusionist
- **Priests**: Cleric, Druid, Templar
- **Rogues**: Bard, Thief
- **Psionicist**: Psionicist

### Special Handling
- **Critical Fix (2025-11-18)**: The source PDF has class requirements as plain text paragraphs. The fix:
  1. Detects the requirements text blocks for each class (either in a single block or across multiple blocks)
  2. Parses the text to extract the three required fields
  3. Creates a structured 2-column, 3-row table with `__class_requirements_table` marker
  4. Clears the original text blocks that contained the requirements
- **Two extraction strategies**:
  - Strategy 1: Class name and requirements in a single text block (e.g., "Fighter Ability Requirements: ...")
  - Strategy 2: Class name as a separate header block, followed by requirements blocks (e.g., Gladiator)
- **Ranger Custom Handler**: Special extraction logic due to severely fragmented data across 8+ blocks with interleaved labels/values
- **HTML Rendering Enhancements**:
  - Multiple ability requirements are automatically split onto separate lines using `<br>` tags for improved readability
  - Example: "Strength 13<br>Dexterity 12<br>Constitution 15" renders as three lines instead of one long line
  - Applies only to the Ability Requirements row when 2+ abilities are present
- **Validation**: Each class must have exactly 3 rows with the correct labels
- **Ability Names**: Must be one of [Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma]
- **Ability Values**: Must be numeric
- **Races**: Can include standard races, "All", "Any", or special races like "mul", "Thri-kreen"

### Validation
- Regression test: `tests/regression/test_class_requirements_tables.py` validates:
  - All 12 player classes have requirements tables
  - Each table has exactly 3 rows and 2 columns
  - Ability requirements follow the "Ability #" format
  - Prime requisites contain only valid ability names
  - Races allowed is non-empty
- Unit tests: `tests/unit/test_class_requirements_extraction.py` validates:
  - Parsing logic for various requirement formats
  - Extraction logic for both single-block and multi-block formats
  - All player classes are in the extraction list

### Data Location
- Extraction code: `tools/pdf_pipeline/transformers/chapter_3/class_requirements.py`
- Common utilities: `tools/pdf_pipeline/transformers/chapter_3/common.py`
- Entry point: `tools/pdf_pipeline/transformers/chapter_3/adjustments.py` → `extract_all_class_requirements_tables()`

## Inherent Potential Table

### Expected Structure
1. H1: "Inherent Potential :" (header with trailing colon and space)
2. Paragraph: "In DARK SUN campaigns, a character may have a Wisdom or Constitution score as high as 22. This table is an expanded version of that given in The Complete Psionics Handbook, covering the higher scores."
3. H2: "Inherent Potential Table"
4. Table with 3 columns and 9 rows:
   - **Headers**: Ability Score | Base Score | Ability Modifier
   - **Data rows (8)**: Scores 15-22 with corresponding base PSP scores (20-34) and modifiers (0 to +7)

### Special Handling
- **Critical Fix (2025-11-15)**: The source PDF has this table heavily fragmented:
  - Header text split across multiple blocks with spacing (e.g., "S c o r e")
  - All numeric data concatenated in blocks with whitespace issues (e.g., "1 7" instead of "17", "+ 1" instead of "+1")
  - Multi-class combinations from the right column bleeding into the left column table region
- **Extraction Logic**: The `extract_inherent_potential_table()` function:
  1. Finds the "Inherent Potential Table" header
  2. Extracts all numeric values from blocks in the left column (x < 150) between the header and "Power Checks:" section
  3. Cleans up whitespace issues (removes internal spaces in numbers, normalizes modifiers)
  4. Parses values into rows of 3 (ability, base, modifier) with validation
  5. Falls back to authoritative reference data if extraction fails
  6. Clears the fragmented table blocks that were replaced
- **Reference Data**: Table values are based on The Complete Psionics Handbook, expanded for Dark Sun's higher ability scores (up to 22)
- **Multi-Class Protection**: Only clears blocks in the left column (x < 290) to avoid removing multi-class combinations that appear in the right column at the same Y coordinates

### Validation
- Table must have exactly 9 rows (1 header + 8 data)
- Table must have exactly 3 columns
- Headers must be: "Ability Score", "Base Score", "Ability Modifier"
- Data rows must cover scores 15-22 with correct base scores and modifiers
- No whitespace issues (e.g., "+ 1" should be "+1")
- No multi-class combinations should appear in the table

### Data Values
| Ability Score | Base Score | Ability Modifier |
|---------------|------------|------------------|
| 15            | 20         | 0                |
| 16            | 22         | +1               |
| 17            | 24         | +2               |
| 18            | 26         | +3               |
| 19            | 28         | +4               |
| 20            | 30         | +5               |
| 21            | 32         | +6               |
| 22            | 34         | +7               |

