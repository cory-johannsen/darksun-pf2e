# Chapter 6 Processing Specification — Money and Equipment

## Overview

Chapter 6 uses `journal` processing with custom header size adjustments and paragraph break hints for multiple sections.

## Header Size Adjustments

The chapter contains several headers that require size adjustments to achieve proper hierarchy:

### H2 Headers (size 10.8)
- **Barter:**
- **Simple Barter:**
- **Protracted Barter:**
- **Service:**
- **Initial Character Funds**
- **Metal Armor in Dark Sun:**

#### Armor Section H2 Headers (HTML Post-Processed)
The following armor headers are formatted as H2 (font-size: 0.9em) with Roman numerals via HTML post-processing in `_fix_chapter_6_armor_headers_after_anchoring()`:

- **Alternate Materials:** (XVII) - existing header, H2 styling applied
- **Shields:** (XVII) - extracted from paragraph text
- **Leather Armor:** (XVIII) - existing header, H2 styling applied
- **Padded Armor:** (XIX) - existing header, H2 styling applied
- **Hide Armor:** (XX) - existing header, H2 styling applied
- **Studded Leather, Ring Mail, Brigandine, and Scale Mail Armor:** (XXI) - merged from 3 fragmented headers
- **Chain, Splint, Banded, Bronze Plate, or Plate Mail; Field Plate and Full Plate Armor:** (XXIV) - merged from 2 fragmented headers

**Note:** These armor headers use HTML post-processing rather than PDF-level manipulation because:
1. Some headers are embedded in paragraph text (Shields)
2. Some headers are fragmented across multiple blocks (Studded Leather, Chain/Splint)
3. Post-processing is more reliable for these complex cases

### H3 Headers (size 9.6)
- **Common Wages**
- **Tun of Water:** (in Equipment Descriptions > Household Provisions section)
- **Fire Kit:** (in Equipment Descriptions > Household Provisions section)
- **Barding:** (in Equipment Descriptions > Tack and Harness section)
- **Chariot:** (in Equipment Descriptions > Transportation section)
- **Howdah:** (in Equipment Descriptions > Transportation section)
- **Wagons, open:** (in Equipment Descriptions > Transportation section)
- **Wagons, enclosed:** (in Equipment Descriptions > Transportation section)
- **Wagon, armored caravan:** (in Equipment Descriptions > Transportation section)
- **Erdlu:** (in Equipment Descriptions > Animals section)
- **Inix:** (in Equipment Descriptions > Animals section)
- **Kank:** (in Equipment Descriptions > Animals section)
- **Mekillot:** (in Equipment Descriptions > Animals section)

### Equipment Descriptions Section H2 Headers
- **Transportation**

### Equipment Descriptions > Weapons Section H3 Headers
- **Chatkcha:**
- **Gythka:**
- **Impaler:**
- **Quabone:**
- **Wrist Razor:**

These adjustments are implemented in `tools/pdf_pipeline/transformers/chapter_6_processing.py` via the `apply_chapter_6_adjustments()` function. The function is called during transformation before HTML rendering.

**Note:** "Service:" is embedded in regular text in the source PDF and needs to be split into a separate header span.

## Paragraph Breaks

### What Things Are Worth Section

This section contains 7 paragraphs with breaks at the following points:

1. **Paragraph 1**: "The equipment lists in the Players Handbook..."
2. **Paragraph 2**: "On Athas, the relative rarity..."
3. **Paragraph 3**: "All nonmetal items cost one percent..."
4. **Paragraph 4**: "All metal items cost the price listed..."
5. **Paragraph 5**: "Thus, the small canoe (a nonmetal item)..."
6. **Paragraph 6**: "If an item is typically a mixture of metal..."
7. **Paragraph 7**: "All prices listed in the DARK SUN..."

### Protracted Barter Section

This section contains 3 paragraphs with breaks at the following points:

1. **Paragraph 1**: "Protracted Barter: This more complicated method..."
2. **Paragraph 2**: "In the first round..."
3. **Paragraph 3**: "If Kyuln from the previous example..."

### Starting Money Section

This section contains 2 paragraphs with breaks at the following points:

1. **Paragraph 1**: "All PCs begin the game with a specific amount of money..."
2. **Paragraph 2**: "The following table indicates..."

### Breaking Weapons Section

This section contains 2 paragraphs with breaks at the following points:

1. **Paragraph 1**: "Obsidian, bone, and wooden weapons are prone to breaking..."
2. **Paragraph 2**: "Bruth is sent to the arena armed with a bone battle axe..."

### Metal Armor in Dark Sun Section

"Metal Armor in Dark Sun:" is an H2 header.

This section contains 2 paragraphs with breaks at the following points:

1. **Paragraph 1**: "Two facts on Athas conspire to limit the use of metal armor..."
2. **Paragraph 2**: "Likewise, the intense heat across Athas' barren surface..."

All paragraph breaks are configured in `tools/pdf_pipeline/transformers/journal.py` in the `transform()` function for slug `chapter-six-money-and-equipment`.

## Initial Character Funds Table

The "Initial Character Funds" section contains a table with the following structure:

### Table Structure
- **2 columns**: Character Group, Die Range
- **6 rows**: 1 header row + 5 data rows
- **Die Range Format**: `#d# x #cp` where # is an integer

### Table Content

| Character Group | Die Range |
|----------------|-----------|
| Warrior | 5d4 x 30cp |
| Wizard | (1d4+1) x 30cp |
| Rogue | 2d6 x 30cp |
| Priest | 3d6 x 30cp |
| Psionicist | 3d4 x 30cp |

### Processing Notes
- The table data is fragmented across multiple text blocks in the source PDF
- "Character Group" and "Die Range" appear as separate small headers (size 7.92) in the PDF
- These are converted to table header cells in the processing stage
- "Initial Character Funds" is promoted to H2 (size 10.8)
- The table is constructed programmatically in `chapter_6_processing._extract_initial_character_funds_table()`

## Processing Logic

1. **Header Adjustments**: Applied via `chapter_6_processing.apply_chapter_6_adjustments()` which modifies font sizes and splits embedded headers
   - "Initial Character Funds" is promoted to H2 (size 10.8)
2. **Table Extraction**: The Initial Character Funds table is extracted and reconstructed
3. **Duplicate Data Suppression**: Duplicate weapon table column headers (Damage, S-M, Speed, Type) that appear in Equipment Descriptions section are suppressed
4. **Paragraph Breaks**: Applied during HTML rendering using the following break points:
   - "On Athas, the relative rarity"
   - "All nonmetal items cost one percent"
   - "All metal items cost the price listed"
   - "Thus, the small canoe (a nonmetal item)"
   - "If an item is typically a mixture of metal"
   - "All prices listed in the"
   - "In the first round"
   - "If Kyuln from the previous example"
   - "The following table indicates"

## Common Wages Table

The "Common Wages" section contains a table with the following structure:

### Table Structure
- **4 columns**: Title, Daily, Weekly, Monthly
- **2 sections**: 
  - Military (10 rows)
  - Professional (3 rows)
- **Legend**: Two entries beneath the table
  - `*available only in some city-states`
  - `**available only in cities with organized militaries`

### Table Content

#### Military Section (10 rows)
1. Archer/artillerist | 1 bit | 1 cp | 4 cp
2. Cavalry, heavy | 3 bits | 2 cp, 5 bits | 1 sp
3. Cavalry, light | 1 bit | 1 cp | 2 bits
4. Cavalry, medium | 2 bits | 1 cp, 5 bits | 5 cp
5. Foot soldier, heavy* | 2 bits | 1 cp, 5 bits | 5 cp
6. Foot soldier, light | 1 bit | 1 cp | 4 cp
7. Foot soldier, militia | 1 bit | 4 bits | 2 cp
8. Foot soldier, medium | 2 bits | 1 cp | 4 cp
9. Lieutenant** | 2 bits | 2 cp | 1 sp
10. Officer/commander | 5 bits | 3 cp, 5 bits | 2 sp

#### Professional Section (3 rows)
1. Unskilled labor | 2 bits | - | 1 cp
2. Skilled labor* | 1 bit | 5 bits | 2 cp
3. Professional | - | - | 3 cp

### Paragraph Flow
- Text between "Protracted Barter" and "Common Wages" belongs to "Protracted Barter"
- "With both barter and service exchanges" starts a new paragraph after the table and legend

### Known Issues
- **Legend text in Protracted Barter**: The PDF source contains the legend text ("*available only in some city-states **available only in cities with organized militaries") embedded within the "Protracted Barter" paragraph text. This text should read "...and then to a third" but has the legend inserted between "a" and "third". This is a source PDF layout issue where the table legend overlapped the paragraph text.

## New Equipment Section

The "New Equipment" section contains a sequence of tables with specific header levels and structures:

### Household Provisions

**Header Level**: H2

**Table Structure**:
- **2 columns**
- **2 rows**

**Note**: In the "Equipment Descriptions" section later in the chapter, there is another "Household Provisions" H2 header with item descriptions. Under this second occurrence, "Tun of Water:" and "Fire Kit:" are H3 headers.

### Tack and Harness

**Header Level**: H2

#### Barding

**Header Level**: H3 (sub-section of Tack and Harness)

**Special Processing Notes**:
- There are TWO "Barding" entries in the source PDF:
  1. First: plain text "Barding" (no colon, black color) after H2 "Tack and Harness" in the "New Equipment" section
  2. Second: "Barding: " (with colon, header color) in the "Equipment Descriptions" section later
- The first occurrence is converted to an H3 header by `_adjust_header_sizes()`
- The table is attached to the first occurrence (H3 in New Equipment section) by `_extract_barding_table()`

**Table Structure**:
- **3 columns**: Type, Price, Weight
- **7 rows** (1 header + 6 data rows)
- **Column 2 Format**: `# sp` or `# cp` (where # is a number)
- **Column 3 Format**: `# lb` (where # is a number)

**Table Data**:
- Inix, leather | 35 sp | 240 lb
- Inix, chitin | 50 sp | 400 lb
- Kank, leather | 15 sp | 70 lb
- Kank, chitin | 35 sp | 120 lb
- Mekillot, leather | 500 sp | 1000 lb
- Mekillot, chitin | 750 sp | 1600 lb

### Transport

**Header Level**: H2

**Table Structure**:
- **2 columns**
- **Column 2 Format**: `# cp` or `# sp` (where # is a number)
- **4 sections** with varying row counts
- **Section headers** are rendered in **bold** within the table using the `bold` cell property

#### Chariot Section
- **3 rows**

#### Howdah Section
- **4 rows**

#### Wagon, open Section
- **4 rows**

#### Wagon, enclosed Section
- **5 rows**

**Implementation Notes**:
- Section headers (Chariot, Howdah, Wagon open, Wagon enclosed) are marked with `bold: True` property
- This ensures they render as `<strong>` tags in HTML, not escaped HTML text
- Regular data rows do not have the `bold` property
- **OCR Error Handling**: The extraction logic fixes common OCR errors like 'l sp' → '1 sp'
- **Unmatched Price Tracking**: Prices that can't be immediately matched with descriptions are saved and applied to subsequent descriptions in the same section
- **Section Boundary Matching**: At section boundaries, any unmatched descriptions are matched with unmatched prices before clearing the buffers

### Animals

**Header Level**: H2

**Table Structure**:
- **2 columns**: Animal, Price
- **7 rows** (1 header + 6 data rows)
- **Special handling**: "Kank" row is a section divider with sub-items "Trained" and "Untrained"

**Table Data**:
- Erdlu | 10 cp
- Inix | 10 sp
- Kank (section divider - bold, no price)
  - Trained | 12 sp (indented)
  - Untrained | 5 sp (indented)
- Mekillot | 20 sp

**Implementation Notes**:
- The "Kank" row uses the `bold: True` property to indicate it's a section divider
- The "Trained" and "Untrained" rows are indented with leading spaces in the text
- The table is constructed programmatically in `chapter_6_processing._extract_animals_table()`

### New Weapons

**Header Level**: H2

**Table Structure**:
- **8 columns**: Weapons, Cost, Wt, Size, Type, Speed, S-M, L
- **7 rows** (2 header rows + 5 data rows)
- **First header row**: ["Weapons", "", "", "", "", "", "Damage"] where "Damage" spans 2 columns
- **Second header row**: ["", "Cost", "Wt", "Size", "Type", "Speed", "S-M", "L"]

**Column Formats**:
- **Cost**: `# cp` or `# sp` (e.g., "1 cp", "6 cp", "1 sp")
- **Wt**: numeric, may contain fractions (e.g., "½", "4") - can be empty
- **Size**: single letter (S, M, L)
- **Type**: single letter or combination (S, P, P/S, P/B)
- **Speed**: numeric (e.g., "1", "2")
- **S-M**: dice notation `#d#` or `#d#+#` (e.g., "1d4+1", "2d4", "1d8")
- **L**: dice notation `#d#` or `#d#+#` (e.g., "1d3", "1d10", "1d8")

**Table Data** (5 weapons):
- Chatkcha | 1 cp | ½ | S | S | 1 | 1d4+1 | 1d3
- Impaler | 4 cp | - | M | P/B | 1 | 1d8 | 1d8
- Polearm, Gythka | 6 cp | 4 | M | P/S | 2 | 2d4 | 1d10
- Quabone | 1 cp | - | S | P | 1 | 1d4 | 1d3
- Wrist Razor | 1 sp | - | S | S | 1 | 1d6+1 | 1d4+1

**Implementation Notes**:
- This is the second "Weapons" header in the chapter (first is in "Athasian Market" section)
- The table data is heavily fragmented in the source PDF across multiple blocks
- The table is constructed programmatically in `chapter_6_processing._extract_new_weapons_table()`
- Header rows are marked with `header_rows: 2` to properly style both header rows
- Empty cells in Wt column for some weapons are represented as empty strings

## Validation

- Check relative links and master TOC link
- Verify header sizes in Monetary Systems section (Barter, Simple Barter, Protracted Barter, Service should be H2; Common Wages should be H3)
- Verify "Initial Character Funds" is H2
- Verify 7 paragraphs in "What Things Are Worth" section
- Verify 3 paragraphs in "Protracted Barter" section
- Verify 2 paragraphs in "Starting Money" section
- Verify 2 paragraphs in "Breaking Weapons" section
- Verify "Metal Armor in Dark Sun:" is H2
- Verify 2 paragraphs in "Metal Armor in Dark Sun" section
- Ensure paragraph breaks occur at the specified points
- Confirm proper sentence joining (no hyphenation artifacts)
- Verify Initial Character Funds table structure (2 columns, 6 rows including header)
- Verify Initial Character Funds table data matches specification
- Verify "Character Group" and "Die Range" are NOT separate headers, but table header cells
- Verify Common Wages table structure (4 columns, 2 sections with correct row counts)
- Verify New Weapons table appears AFTER Animals table in New Equipment section
- Verify New Weapons table structure (8 columns, 7 rows: 2 header + 5 data)
- Verify New Weapons table contains: Chatkcha, Impaler, Polearm Gythka, Quabone, Wrist Razor (in that order)
- Verify no fragmented column headers (Cost, Wt, Size, Type, Speed, Damage, S-M, L) appear as separate H1 headers after Weapons table
- Verify legend entries appear below table
- Verify "With both barter and service exchanges" starts new paragraph after legend
- Verify "Household Provisions" is H2 with table (2 rows, 2 columns)
- Verify "Tun of Water:" is H3 in Equipment Descriptions > Household Provisions section
- Verify "Fire Kit:" is H3 in Equipment Descriptions > Household Provisions section
- Verify duplicate weapon column headers (Damage, S-M, Speed, Type) do NOT appear in Equipment Descriptions section
- Verify "Barding:" is H3 in Equipment Descriptions > Tack and Harness section
- Verify "Transportation" is H2 in Equipment Descriptions section
- Verify "Chariot:" is H3 in Equipment Descriptions > Transportation section
- Verify "Howdah:" is H3 in Equipment Descriptions > Transportation section
- Verify "Wagons, open:" is H3 in Equipment Descriptions > Transportation section
- Verify "Wagons, enclosed:" is H3 in Equipment Descriptions > Transportation section
- Verify "Wagon, armored caravan:" is H3 in Equipment Descriptions > Transportation section
- Verify "Erdlu:" is H3 in Equipment Descriptions > Animals section
- Verify "Inix:" is H3 in Equipment Descriptions > Animals section
- Verify "Kank:" is H3 in Equipment Descriptions > Animals section
- Verify "Mekillot:" is H3 in Equipment Descriptions > Animals section
- Verify "Chatkcha:" is H3 in Equipment Descriptions > Weapons section
- Verify "Gythka:" is H3 in Equipment Descriptions > Weapons section
- Verify "Impaler:" is H3 in Equipment Descriptions > Weapons section
- Verify "Quabone:" is H3 in Equipment Descriptions > Weapons section
- Verify "Wrist Razor:" is H3 in Equipment Descriptions > Weapons section
- Verify "Tack and Harness" is H2
- Verify "Barding" is H3 under "Tack and Harness" in the New Equipment section (first occurrence)
- Verify Barding table appears immediately after the H3 "Barding" header in New Equipment section
- Verify Barding table has 7 rows (1 header + 6 data rows) and 3 columns (Type, Price, Weight)
- Verify Barding table column 2 format: `# sp` or `# cp`
- Verify Barding table column 3 format: `# lb`
- Verify Barding table contains all 6 data rows: Inix (leather/chitin), Kank (leather/chitin), Mekillot (leather/chitin)
- Verify second "Barding:" (with colon) in Equipment Descriptions section is NOT converted to H3 (remains as descriptive text header)
- Verify "Transport" is H2 with table (2 columns)
- Verify Transport table column 2 format: `# cp` or `# sp`
- Verify Transport table has 4 sections: Chariot (3 rows), Howdah (4 rows), Wagon, open (4 rows), Wagon, enclosed (5 rows)
- Verify "Animals" is H2 with table (2 columns, 7 rows including header)
- Verify Animals table has "Kank" as a section divider (bold, no price)
- Verify Animals table has "Trained" and "Untrained" as indented sub-items under "Kank"
- Verify Animals table data matches specification
- Verify "Weapons" (second occurrence after Animals) is H2 with table (8 columns, 6 rows including 2 header rows)
- Verify New Weapons table has proper two-row header structure
- Verify New Weapons table first header row: ["Weapons", "", "", "", "", "", "Damage"] with "Damage" spanning 2 columns
- Verify New Weapons table second header row: ["", "Cost", "Wt", "Size", "Type", "Speed", "S-M", "L"]
- Verify New Weapons table has 4 weapon data rows: Chatkcha, Gythka, Impaler, Quabone, Wrist Razor
- Verify New Weapons table Cost column format: `# cp` or `# sp`
- Verify New Weapons table S-M and L columns use dice notation: `#d#` or `#d#+#`


