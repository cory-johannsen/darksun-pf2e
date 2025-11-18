# Chapter 12 Processing Specification — NPCs

## Overview

Processed with `journal`. 

## Paragraph Breaks

### Spellcasters as NPCs
The "Spellcasters as NPCs" section has 5 paragraphs with breaks at:
1. Opening paragraph - discussion of priest NPC services
2. "Druid NPCs" - discussion of druid NPC services
3. "Wizard NPCs" - discussion of wizard NPC services
4. "Rare instances" - rare cases where wizards might be bought
5. "One notable" - exception for affluent defilers

### Templars as NPCs
The "Templars as NPCs" section has 8 paragraphs with breaks at:
1. Opening paragraph - "Templars are the most feared people"
2. "Templars perform three vital functions" - three primary functions
3. "One final," - advancement through ranks
4. "Templar soldiers are" - enforcement arm description
5. "In the administration of the" - administrative functions (NOTE: This paragraph is split by a table in the source, but should be merged with "NPCs occupy all positions")
6. "These are only a sampling" - levels of bureaucracy
7. "Technically, the sorcerer-king" - worship and temples
8. "The DM must keep two things" - using templars in gameplay

### Druids as NPCs
The "Druids as NPCs" section has 2 paragraphs with a break at:
1. Opening paragraph - "An NPC druid will defend his guarded lands"
2. "Irresponsible use of his guarded" - consequences of misuse

## Tables

### Typical Administrative Templar Positions
- **Location in source**: Between "In the administration of the city states, templar" and "NPCs occupy all positions from waste removal"
- **Visual position in output**: After all Templars as NPCs text paragraphs, before Druids as NPCs section
- **Structure**: 3 columns x 8 rows (plus header row)
- **Columns**: 
  - Low Level (1-4)
  - Mid Level (5-8)
  - High Level (9 +)
- **Note**: The table header "Typical Administrative Templar Positions" should be an H4 (table title), not an H1 (document header)
- **Note**: The level headers (Low/Mid/High) should be table column headers (<th>), not document headers

## Processing Details

### Journal Transformer
- Paragraph breaks are added in `tools/pdf_pipeline/transformers/journal.py`
- Breaks for both "Spellcasters as NPCs" and "Templars as NPCs" sections

### HTML Post-Processing
- Handled by `tools/pdf_pipeline/postprocessors/chapter_12_postprocessing.py`
- Restructures the Templar positions table from fragmented source data
- Moves table to correct visual position (after all text, before Druids)
- Converts table headers to proper <th> elements instead of document headers
- Merges paragraph that was split by table in source material

## Validation

- Ensure single-page output and valid links
- Verify 5 paragraphs in "Spellcasters as NPCs" section
- Verify 8 paragraphs in "Templars as NPCs" section
- Verify 2 paragraphs in "Druids as NPCs" section
- Verify table appears after all Templars text
- Verify table has 3 columns and 8 data rows
- Run regression test: `tests/regression/test_chapter12_templars.py`

