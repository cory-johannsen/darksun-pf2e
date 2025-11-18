# Chapter 13 Processing Specification — Vision and Light

## Overview

Chapter 13 contains visibility rules and lighting conditions specific to Dark Sun.

## Extraction Challenges

1. **Intro Paragraph Split**: The introductory paragraph is split across two columns
2. **Table Structure**: The "Dark Sun Visibility Ranges" table is embedded in the text flow
3. **Header Confusion**: Table column headers could be mistaken for document headers

## Processing Strategy

### Stage 1: Extraction (chapter_13_processing.py)

1. **Merge Intro Paragraphs**
   - Combine left column: "All of the conditions presented on the Visibility Ranges table in the Player's Handbook exist on"
   - With right column: "Athas. However, there are a number of conditions unique to Athas that should be added."
   - Result: Single continuous paragraph

2. **Mark H2 Header**
   - Mark "Dark Sun Visibility Ranges" as H2 (not H1)
   - Increase font size to 12.0

3. **Extract Table Data**
   - Mark table headers (Condition, Movement, Spotted, Type, ID, Detail) with `is_table_header` flag
   - Mark condition values (Sand, blowing; Sandstorm, mild; etc.) with `is_table_data` flag
   - Mark numeric values in table area (y: 244-322) with `is_table_data` flag
   - Set `skip_render` on all table elements to prevent normal rendering

### Stage 2: Post-Processing (chapter_13_postprocessing.py)

1. **Fix Intro Paragraph**
   - Ensure paragraph is properly merged in HTML

2. **Insert Visibility Table**
   - Create properly formatted HTML table
   - Insert after "Dark Sun Visibility Ranges" H2 header
   - Remove incorrectly rendered table fragments

3. **Update Table of Contents**
   - Remove table header entries (Condition, Movement, Type, Spotted, Detail)
   - Keep only main section headers

## Table Structure

### Dark Sun Visibility Ranges Table

| Column | Type | Description |
|--------|------|-------------|
| Condition | Text | Environmental condition (contains comma) |
| Movement | Number | Movement detection distance |
| Spotted | Number | Spotting distance |
| Type | Number | Type identification distance |
| ID | Number | Identification distance |
| Detail | Number | Detail recognition distance |

### Table Data

| Condition | Movement | Spotted | Type | ID | Detail |
|-----------|----------|---------|------|----|----|
| Sand, blowing | 100 | 50 | 25 | 15 | 10 |
| Sandstorm, mild | 50 | 25 | 15 | 10 | 5 |
| Sandstorm, driving | 10 | 10 | 5 | 5 | 3 |
| Night, both moons | 200 | 100 | 50 | 25 | 15 |
| Silt Sea, calm | 500 | 200 | 100 | 50 | 25 |
| Silt Sea, rolling | 100 | 50 | 25 | 10 | 5 |

## Validation

### Unit Tests (test_chapter_13_processing.py)

- Test intro paragraph merging
- Test H2 marking
- Test table extraction
- Test idempotency

### Regression Tests (test_chapter_13_vision_and_light.py)

1. Verify intro paragraph is merged
2. Verify "Dark Sun Visibility Ranges" is H2
3. Verify table exists and is properly formatted
4. Verify all 6 columns present
5. Verify all 6 data rows present
6. Verify table headers not rendered as document headers
7. Verify condition values only appear in table

## Special Handling

### Header Level

- "Dark Sun Visibility Ranges" must be H2, not H1
- Remove roman numeral from this header

### Table Headers vs Document Headers

- Table headers (Condition, Movement, etc.) must NOT be rendered as document headers
- They should only appear in the `<thead>` of the table
- They should NOT appear in the table of contents

### Paragraph Breaks

The intro paragraph must NOT be split into:
1. "All of the conditions presented..."
2. "However, there are a number..."

These must be a single paragraph.
