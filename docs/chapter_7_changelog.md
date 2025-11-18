# Chapter 7 Processing Changelog

## 2025-11-14: Fixed Cross-Sphere Spell Duplication

### Issue
Fire and Water sphere spells were being incorrectly extracted and added to the Cosmos sphere, causing duplicates. Spells like "Fire Storm (7th)" and "Transmute Water to Dust (6th)" appeared in both their correct sphere AND in Cosmos.

### Root Cause
The postprocessing logic was extracting ALL 5th-7th level spells found before the Cosmos header, assuming they were misplaced Cosmos spells. However, these spells legitimately belonged to the Fire and Water spheres which appear BEFORE Cosmos in the document.

### Solution
1. **Removed "before Cosmos" extraction**: Spells before the Cosmos header belong to earlier spheres (Fire, Water)
2. **Added cross-sphere duplicate detection**: `_update_spell_json_with_extracted_spells()` now checks if a spell exists in ANY sphere before adding to Cosmos
3. **Only extracts genuine Cosmos spells**: From within the Cosmos section and after Wizardly Magic header

### Result
- ✅ No duplicates between Fire and Cosmos
- ✅ No duplicates between Water and Cosmos
- ✅ Cosmos now has 126 spells (down from 134)
- ✅ Fire sphere retains all 19 spells including Fire Storm (7th)
- ✅ Water sphere retains all 11 spells including Transmute Water to Dust (6th)
- ✅ All regression tests still pass

## 2025-11-14: Fixed Sphere of the Cosmos Regression - Embedded Spell Extraction

### Issue
The Sphere of the Cosmos spell list was incomplete after "Animal Growth (5th)". The remaining 5th-7th level spells (41+ spells) were mixed into surrounding paragraph text instead of appearing as list items. This was a regression of a previously fixed issue, indicating insufficient test coverage.

Missing spells included:
- **5th level**: Animal Summoning II, Anti-Plant Shell, and others
- **6th level**: Animal Summoning III, Heroes' Feast (listed as "Feast"), and others
- **7th level**: Regenerate, Reincarnate, Restoration, Resurrection, Succor, Sunray, Symbol

### Root Cause
The 2-column PDF layout caused spells to be extracted as plain text embedded within prose paragraphs rather than as dedicated spell list items. These embedded spells appeared in two locations:
1. **Within the Cosmos section** (between Cosmos and Wizardly Magic headers)
2. **After the Wizardly Magic header** (up to 5000 chars after)

The original regex pattern `[A-Z][a-z]+(?:[\s\-\'&]+[A-Z][a-z]+)*` couldn't match:
- **Spell names with Roman numerals**: "Animal Summoning II", "Animal Summoning III"
- **Spells merged with prose**: "Sphere Anti-Plant Shell" (needed to strip "Sphere " prefix)

### Solution

#### 1. Updated Regex Pattern (Both Processing and Postprocessing)
Changed pattern to: `(?:^|(?<=[^A-Za-z]))([A-Z][a-z]+(?:[\s\-\'&]+(?:or|and|of|with|to|from|the)?[\s\-\'&]*[A-Z][a-z]+|[\s\-\'&]*[IVX]+)*)\s+\((\d+(?:st|nd|rd|th))\)`

**Key improvements**:
- Added `[\s\-\'&]*[IVX]+` to match Roman numerals (I, II, III, IV, V, etc.)
- Used negative lookbehind `(?<=[^A-Za-z])` to prevent matching partial spell names
- Handles spell names with connecting words (e.g., "Commune With Nature")

#### 2. Enhanced Postprocessing (`chapter_7_postprocessing.py`)
**Search Areas**:
- **Within Cosmos**: Scan section between Cosmos header and Wizardly Magic header
- **After Wizardly Magic**: Check 5000 chars after header to catch displaced Cosmos spells
- **Note**: Does NOT extract from before Cosmos (those belong to Fire/Water spheres)

**Added Sphere Prefix Stripping**:
- Detects spell names starting with "Sphere " (e.g., "Sphere Anti-Plant Shell")
- Strips the "Sphere " prefix to get correct spell name ("Anti-Plant Shell")

**JSON Update**:
- Added `_update_spell_json_with_extracted_spells()` function
- Postprocessing now updates `data/processed/chapter-seven-spells.json` with extracted spells
- Prevents spell data loss since postprocessing runs after JSON generation

#### 3. Enhanced Processing (`chapter_7_processing.py`)
- Updated `embedded_spell_pattern` to match the new regex
- Added "Sphere " prefix stripping logic
- Added detailed logging to trace embedded spell extraction

#### 4. Comprehensive Regression Tests
Created `test_chapter7_cosmos_sphere_completeness.py` with 7 test methods:
- `test_cosmos_sphere_ends_with_symbol`: Verifies last 7th level spell is "Symbol"
- `test_cosmos_sphere_has_all_expected_spells`: Checks all 41+ critical spells are present
- `test_cosmos_sphere_minimum_spell_count`: Ensures at least 120 spells total
- `test_cosmos_sphere_spell_level_distribution`: Validates 5th/6th/7th level spell counts
- `test_html_cosmos_spells_in_list_format`: Verifies spells appear as `<li>` elements in HTML
- `test_html_no_spells_mixed_in_cosmos_paragraphs`: Ensures no spells mixed into prose
- `test_cosmos_spell_json_completeness`: Validates JSON contains complete spell data

### Validation Results
- ✅ All 7 regression tests pass
- ✅ Sphere of the Cosmos now contains 134 spells (was 85-127 during debugging)
- ✅ All 5th-7th level spells correctly extracted and formatted as list items
- ✅ "Feast" (also known as "Heroes' Feast") present in spell list
- ✅ Spells with Roman numerals ("Animal Summoning II", "Animal Summoning III") extracted correctly
- ✅ No spell text remains mixed into prose paragraphs
- ✅ All Chapter 7 regression tests pass:
  - `test_chapter7_cosmos_sphere_completeness.py`: 7/7 tests pass
  - `test_chapter7_sphere_of_air.py`: All tests pass
  - `test_chapter7_wizardly_magic_paragraph.py`: All tests pass

### Result
- Sphere of the Cosmos spell list is now complete with all 5th-7th level spells
- All embedded spells correctly extracted from prose paragraphs
- Spells properly formatted as `<li class="spell-list-item">` elements in HTML
- JSON data contains complete spell information with correct sphere assignments
- Comprehensive test suite prevents future regressions

## 2025-11-14: Added Line Breaks Above Sphere Headers

### Issue
The sphere headers (Sphere of Air, Fire, Water, and Cosmos) appeared directly attached to the preceding spell lists without any visual separation, making it difficult to distinguish where one sphere ends and another begins.

### Root Cause
The HTML generation created sphere headers immediately after the spell list `</ul>` tags with no spacing or line breaks. This caused a cramped appearance where the sphere headers visually ran into the spell lists.

### Solution
**Updated `chapter_7_postprocessing.py`**:
- Added `_add_sphere_header_line_breaks()` function
- Inserts `<br>` tags before the following sphere headers:
  - Sphere of Air (header-2)
  - Sphere of Fire (header-3)
  - Sphere of Water (header-4)
  - Sphere of the Cosmos (header-5)
- Sphere of Earth is excluded as it immediately follows the "Priestly Magic" header
- Function checks for existing line breaks to avoid duplicates

### Validation
- Visual inspection of HTML output confirms line breaks are present
- All four target sphere headers now have `<br>` tags immediately before them
- Sphere of Earth correctly has no line break (follows main header)

### Result
- Sphere headers now have clear visual separation from preceding spell lists
- Document structure is easier to scan and navigate
- Reading experience is improved with better visual hierarchy

## 2025-11-14: Merged Wizardly Magic Intro into Single Paragraph

### Issue
The text between "Wizardly Magic" and "Defiling" headers was being rendered as 5 separate paragraphs instead of one continuous paragraph. This fragmentation made the introduction difficult to read and broke the natural flow of the text.

The fragmented paragraphs were:
1. "Wizards draw their magical energies from the living things and life-giving elements around them."
2. "Preservers cast spells in harmony with nature, using"
3. "their magic so as to return to the land what they take"
4. "from it. Defilers care nothing for such harmony and"
5. "damage the land with every spell they cast."

### Root Cause
The PDF extraction split this text into 5 separate blocks (blocks 36-40 on page 3) due to line breaks in the 2-column layout. Without explicit merging logic, these blocks were being rendered as individual paragraphs in the HTML output.

### Solution
**Updated `chapter_7_processing.py`**:
- Added `_merge_wizardly_magic_intro()` function
- Finds the "Wizardly Magic" and "Defiling" header blocks
- Identifies all blocks between these headers (should be 5 blocks)
- Merges all lines from these blocks into a single block
- Deletes the now-redundant individual blocks
- This is done during the processing stage, before HTML rendering

### Validation
- Created regression test `test_chapter7_wizardly_magic_paragraph.py`
- Verifies exactly 1 paragraph exists between the two headers
- Verifies all expected text is present in the merged paragraph
- Verifies no hyphenation artifacts remain
- Verifies no fake paragraph breaks (no `</p><p>` in the middle)

### Result
- The Wizardly Magic introduction is now rendered as a single, coherent paragraph
- All text flows naturally from "Wizards draw their magical energies..." to "...damage the land with every spell they cast."
- Reading experience is significantly improved
- Proper dehyphenation of "liv-ing" to "living"

## 2025-11-14: Fixed Prose Paragraphs Mixed with Spell Lists

### Issue
Two descriptive paragraphs in the "Sphere of the Cosmos" section were intermixed with spell list items:
1. "Clerics have major access to the sphere of the element they worship, plus minor access to the Sphere of the Cosmos. Templars have major access to all spheres, but gain spells more slowly."
2. "There are no deities in Dark Sun. Those spells that indicate some contact with a deity instead reflect contact with a powerful being of the elemental planes."

These paragraphs were fragmented across multiple `<p>` tags and intermixed with `<li class="spell-list-item">` elements, making them difficult to read.

### Root Cause
The 2-column PDF layout placed these paragraphs in the right column of the page while spell list items were in the left column. During HTML rendering, the columns were being interleaved incorrectly, causing paragraph fragments to appear between spell items.

### Solution
**Updated `chapter_7_postprocessing.py`**:
- Added `_fix_cosmos_sphere_paragraphs()` function
- Searches for fragmented paragraph patterns using regex
- Extracts all fragments of both paragraphs
- Removes them from their intermixed positions
- Reassembles them as complete paragraphs
- Inserts them cleanly before the "Wizardly Magic" header

### Validation
- Created unit test `test_chapter_7_postprocessing.py`
- Verifies paragraphs exist as complete, non-fragmented text
- Verifies both paragraphs appear together without spell items between them
- Verifies paragraphs appear in the correct location (after spell list, before Wizardly Magic)
- Verifies fragmented versions no longer exist
- All regression tests pass (HTML paths, index, dehyphenation)

### Result
- Both paragraphs now appear as complete, properly formatted text
- Paragraphs are positioned correctly after the spell list
- No spell list items intermixed with the prose text
- Reading flow is natural and clear

## 2025-11-13: Fixed Sphere of the Cosmos Spell Ordering

### Issue
Spells from "Sphere of the Cosmos" (5th, 6th, and 7th level) were incorrectly appearing mixed into the "Wizardly Magic" section in the HTML output. The spell data showed only 39 spells for "Sphere of the Cosmos" instead of the full 80, with no 7th level spells.

### Root Cause
Two related issues:
1. **Parsing Issue**: The spell parsing logic tracked `current_sphere` per page+column tuple, but didn't persist sphere state across pages. When "Sphere of the Cosmos" started on page 60 and continued on page 61, the sphere state wasn't carried over, causing spells on page 61 to not be assigned to any sphere.
2. **Rendering Issue**: Even after fixing parsing, the 2-column layout on page 61 caused blocks to be rendered sequentially (0, 1, 2, ...) rather than in reading order (right column, then left column). This caused left column cosmos spells (blocks 6-28, Y=257-686) to appear AFTER right column headers like "Wizardly Magic" (block 35, Y=267).

### Solution
1. **Updated `chapter_7_processing.py`**:
   - Changed `current_sphere_by_column` from `{(page_idx, column): sphere}` to `{column: sphere}`
   - This allows sphere state to persist across pages for each column independently
   - The left column sphere state set on page 60 now continues on page 61

2. **Updated `chapter_7_postprocessing.py`**:
   - Added `_fix_cosmos_spell_ordering()` function
   - Identifies 5th/6th/7th level spell list items that appear after "Wizardly Magic"
   - Extracts and moves them before "Wizardly Magic" header
   - Wraps them in proper `<ul class="spell-list">` tags

### Validation
- Created unit test `test_chapter_7_column_aware_parsing.py`
- Verifies "Sphere of the Cosmos" ends with "Symbol (7th)"
- Verifies no wizard spells in cosmos sphere
- Verifies HTML output has all cosmos spells before "Wizardly Magic"

### Result
- "Sphere of the Cosmos" now contains all 80 spells (was 39)
- Includes all 13 seventh-level spells: Changestaff, Confusion, Creeping Doom, Exaction, Gate, Holy Word, Regenerate, Reincarnate, Restoration, Resurrection, Succor, Sunray, and Symbol
- HTML output shows all cosmos spells properly grouped before "Wizardly Magic" section

