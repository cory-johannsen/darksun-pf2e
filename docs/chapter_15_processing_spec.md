# Chapter 15 Processing Specification — New Spells

## Overview

Chapter 15 introduces new spells for the Dark Sun campaign setting, with modifications to existing AD&D spells and entirely new spells. Processing focuses on proper header hierarchy and table extraction.

## Header Structure

### H2 Headers
- Spell level groups (e.g., "First Level Spells", "Second Level Spells", etc.)
- Format pattern: `(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth)-?Level Spells`

### H3 Headers
- Individual spell names under "First Level Spells":
  - Charm Person
  - Find Familiar
  - Mount

### H1 Headers (Existing)
- "Wizard Spells"
- "Priest Spells"

## Tables

### Find Familiar Table
Located in the "Find Familiar" section, following the sentence: "In DARK SUN campaigns, substitute this table for that found in the Player's Handbook."

**Structure:**
- 3 columns: Die Roll, Familiar, Sensory Powers
- Die Roll format: "#" or "#-#" (e.g., "1-3", "4-5", "6-8")

**Data:**
| Die Roll | Familiar | Sensory Powers |
|----------|----------|----------------|
| 1-3 | Bat | Night vision, sonar-enhanced |
| 4-5 | Beetle | Senses minute vibrations |
| 6-8 | Cat, black | Excellent night vision and superior hearing |
| 9 | Pseudodragon | Normal sensory powers, but very intelligent |
| 10-11 | Rat | Excellent sense of taste and smell |
| 12-15 | Scorpion | Senses fear |
| 16-20 | Snake | Sensitivity to subtle temperature changes |

### Mount Table
Located in the "Mount" section, following the sentence: "In DARK SUN campaigns, substitute this table for that found in the Player's Handbook."

**Structure:**
- 2 columns: Caster Level, Mount
- Caster Level format: "#-# level" (e.g., "1st-3rd level", "4th-7th level")

**Data:**
| Caster Level | Mount |
|--------------|-------|
| 1st-3rd level | Wild Kank |
| 4th-7th level | Trained Kank |
| 8th-12th level | Inix |
| 13th-14th level | Mekillot (and howdah at 18th level) |
| 15th level & up | Roc (and saddle at 18th level) |

## Special Handling

### Table Headers
The raw PDF contains table column headers as separate colored text blocks:
- "Die Roll Familiar" and "S e n s o r y  P o w e r s" (with spacing)
- "Caster Level" and "Mount" (as separate blocks)

These header blocks are:
1. Identified during table extraction
2. Removed from the output (marked as `type: "skip"`)
3. Replaced with proper HTML table headers

### Table Data
Table data appears as continuous text in the PDF. The processing module:
1. Identifies table data blocks by content
2. Uses hardcoded data based on the source PDF to ensure 100% accuracy
3. Generates proper HTML table markup with semantic structure

## Validation

- Confirm "First Level Spells" is H2
- Confirm "Charm Person", "Find Familiar", "Mount" are H3
- Confirm Find Familiar table has 3 columns and 7 rows
- Confirm Mount table has 2 columns and 5 rows
- Confirm TOC and back-to-top links [^]
- Confirm table headers are removed from regular text flow
- Confirm tables use `.data-table` CSS class


