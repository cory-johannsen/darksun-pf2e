# Chapter 14 Processing Specification — Time and Movement

## Overview

Chapter 14 contains time, calendar, and movement rules for Dark Sun. The chapter includes a critical table displaying the Athasian Calendar cycles that requires special processing.

## Header Hierarchy

Per user feedback, the following header levels are established:

### H1 Headers (Main Sections)
- "The Athasian Calendar"
- "Dehydration"
- "Overland Movement"
- Other major sections

### H2 Headers (Subsections)
- "Year of the Messenger"
- "Starting the Campaign"
- "Water Consumption"
- "Substituting Other Liquids"
- "Effects of Dehydration"
- "Rehydration"
- "Animals and Dehydration"

### H3 Headers (Sub-subsections)
- "Unusual Races"
- "Dehydration Effects Table"
- "Example of Dehydration"
- "Transporting Water"

### H4 Headers (Minor subsections)
- "Thri-kreen:"
- "Half-giants:"

## Extraction Challenges

1. **Athasian Calendar Table**: A two-column table embedded in the text showing the Endlean Cycle and Seofean Cycle
2. **Table Headers as Document Headers**: "The Endlean Cycle" and "The Seofean Cycle" are being incorrectly identified as H1 document headers
3. **Table Position**: The table should appear between the paragraph ending "a year of Guthay's Agitation." and the paragraph beginning "Superstition and folklore"
4. **Multiple Other Tables**: The chapter contains other tables that need similar handling
5. **Header Levels**: Many headers need to be adjusted to establish proper hierarchy

## Processing Strategy

### Stage 1: Extraction (chapter_14_processing.py)

1. **Mark Athasian Calendar Table Headers**
   - Identify "The Endlean Cycle" and "The Seofean Cycle" (orange text, size ~7.92)
   - Mark as `is_table_header` (NOT H1 headers)
   - Set `skip_render` to prevent them appearing as document headers

2. **Mark Calendar Table Data**
   - Identify table data in y-coordinate range approximately 516-630
   - Left column (x < 120): Ral, Friend, Desert, Priest, Wind, Dragon, Mountain, King, Silt, Enemy, Guthay
   - Right column (x > 160): Fury, Contemplation, Vengeance, Slumber, Defiance, Reverence, Agitation
   - Mark all with `is_table_data` flag
   - Set `skip_render` to prevent normal paragraph rendering

3. **Paragraph Breaks**
   - Ensure proper paragraph break after "a year of Guthay's Agitation."
   - Ensure proper paragraph break before "Superstition and folklore"

4. **Adjust Header Levels**
   - Set H2 headers: "Year of the Messenger", "Starting the Campaign", "Water Consumption", "Substituting Other Liquids", "Effects of Dehydration", "Rehydration", "Animals and Dehydration"
   - Set H3 headers: "Unusual Races", "Dehydration Effects Table", "Example of Dehydration", "Transporting Water"
   - Set H4 headers: "Thri-kreen:", "Half-giants:"

### Stage 2: Post-Processing (chapter_14_postprocessing.py)

1. **Insert Athasian Calendar Table**
   - Create properly formatted HTML table with two columns
   - Insert after the paragraph ending "a year of Guthay's Agitation."
   - Format with `ds-table` class for consistent styling

2. **Remove Incorrectly Rendered Headers**
   - Remove "The Endlean Cycle" and "The Seofean Cycle" from TOC and document
   - Remove "Amount of Water" and "Constitution Loss" (table column headers)

3. **Insert Dehydration Effects Table**
   - Create properly formatted HTML table with two columns
   - Insert after "Dehydration Effects Table" header
   - Format with `ds-table` class

4. **Fix Whitespace Issues**
   - Fix "M u l" → "Mul"
   - Fix "E l f" → "Elf"
   - Fix "R a c e" → "Race"
   - Fix "Fo r" → "For"
   - Fix "Wi n d" → "Wind"

## Validation

- Verify Athasian Calendar table appears in correct location
- Verify "The Endlean Cycle" and "The Seofean Cycle" do not appear as headers
- Verify Dehydration Effects table appears in correct location
- Verify whitespace issues are fixed
- Verify header hierarchy is correct:
  - H2: "Year of the Messenger", "Starting the Campaign", "Water Consumption", "Substituting Other Liquids", "Effects of Dehydration", "Rehydration", "Animals and Dehydration"
  - H3: "Unusual Races", "Dehydration Effects Table", "Example of Dehydration", "Transporting Water"
  - H4: "Thri-kreen:", "Half-giants:"
- Remove "The Endlean Cycle" and "The Seofean Cycle" from document headers
   - Remove from table of contents

3. **Clean Up Table Fragments**
   - Remove any incorrectly rendered table data fragments
   - Clean up extraneous table elements at end of sections

## Table Structure

### Athasian Calendar Cycles Table

| The Endlean Cycle | The Seofean Cycle |
|-------------------|-------------------|
| Ral | Fury |
| Friend | Contemplation |
| Desert | Vengeance |
| Priest | Slumber |
| Wind | Defiance |
| Dragon | Reverence |
| Mountain | Agitation |
| King | |
| Silt | |
| Enemy | |
| Guthay | |

**Note**: The Endlean Cycle has 11 entries, the Seofean Cycle has 7 entries. This reflects the 11-year and 7-year cycles mentioned in the text.

## Validation Requirements

1. **Table Placement**: Verify table appears between correct paragraphs
2. **Header Count**: Verify "The Endlean Cycle" and "The Seofean Cycle" are not counted as document headers
3. **Table of Contents**: Verify table headers don't appear in TOC
4. **Table Completeness**: Verify all 11 Endlean entries and 7 Seofean entries are present
5. **No Extraneous Fragments**: Verify no table data fragments appear in wrong locations
