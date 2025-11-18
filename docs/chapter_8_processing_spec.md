# Chapter 8 Processing Specification — Experience

## Overview

Chapter 8 contains 15 Individual Class Awards tables and 7 Individual Race Awards tables that require special processing.
Each table has 2 columns (Action, Awards) and is identified by a class or race header.

**Current Status:**
- **Class Awards: 15/15 tables correct (100%)** ✅ COMPLETE
- **Race Awards: 7/7 tables correct (100%)** ✅ COMPLETE

## Tables

### Individual Class Awards Tables

The following 15 tables are extracted and formatted:

1. **All Warriors:** - General warrior awards
2. **Fighter:** - Fighter-specific awards
3. **Gladiator:** - Gladiator-specific awards
4. **Ranger:** - Ranger-specific awards
5. **All Wizards:** - General wizard awards
6. **Preserver:** - Preserver-specific awards
7. **Defiler:** - Defiler-specific awards
8. **All Priests:** - General priest awards
9. **Cleric:** - Cleric-specific awards
10. **Druid:** - Druid-specific awards
11. **Templar:** - Templar-specific awards
12. **All Rogues:** - General rogue awards
13. **Thief:** - Thief-specific awards
14. **Bard:** - Bard-specific awards
15. **Psionicist:** - Psionicist-specific awards

### Table Structure

Each table:
- Has a header rendered as **H2** (without the colon)
- Contains 2 columns:
  - **Action**: Description of the action
  - **Awards**: XP value in various formats

### Awards Column Formats

The Awards column uses these formats:
- `# XP/level` - XP per character level
- `# XP/day` - XP per day
- `# XP/spell level` - XP per spell level
- `# XP` - Flat XP amount
- `XP value` - Variable XP value
- `# XP/cp value` - XP per copper piece value
- `# XP/PSP` - XP per psionic strength point
- `# XP x level` - XP multiplied by level
- `Hit Dice` - Based on hit dice

## Processing

The chapter_8_processing.py module:

1. Identifies "Individual Class Awards" section markers or class award headers
2. Sorts blocks by Y-coordinate for proper reading order (top-to-bottom)
3. Detects class award headers (All Warriors:, Fighter:, Psionicist:, etc.)
4. Filters table items by column (LEFT vs RIGHT) to avoid cross-column contamination
5. Groups subsequent text blocks into table rows based on spatial layout
6. Pairs Action and Awards columns based on X-coordinate boundaries
7. Cleans up whitespace in XP values (e.g., "1 0  X P / P S P" → "10 XP/PSP")
8. Creates table markers with `__class_award_table` flag
9. Suppresses original text blocks to avoid duplication
10. Renders tables with proper HTML structure

### Special Handling

- **Y-coordinate sorting**: Blocks are sorted by Y-coordinate to ensure proper reading order, especially important when class headers appear at the start of a page
- **Column filtering**: Items are filtered by X-coordinate to prevent mixing data from LEFT column tables with RIGHT column race awards (boundary at x=300)
- **Whitespace cleanup**: The `_clean_xp_text()` function removes excessive spaces in awards like "1 0  X P / P S P" → "10 XP/PSP"
- **Psionicist table**: Located on page 66 (page index 1) in the LEFT column, extracted with 4 rows as specified
- **Legend entries**: Two legend entries follow the Psionicist table:
  - `*For gladiators, this award only applies to creatures slain without outside aid. The gladiator gets no experience gain for treasure obtained.`
  - `**The thief adds this XP allotment to the rogue gain for treasure obtained.`
  These are captured and rendered as paragraphs after the table.

## Individual Race Awards Tables

The following 7 race award tables are extracted and formatted:

1. **Dwarf:** - Dwarf-specific awards based on focus
2. **Elf:** - Elf-specific awards based on trust tests and running
3. **Half-elf:** - Half-elf-specific awards for customs and contests
4. **Half-Giant:** - Half-Giant-specific awards for imitation and alignment shifts
5. **Halfling:** - Halfling-specific awards for customs and aiding other halflings
6. **Mul:** - Mul-specific awards for heavy exertion
7. **Thri-kreen:** - Thri-kreen-specific awards for hunting and combat abilities

### Table Structure

Each race award table:
- Has a header rendered as **H2** (without the colon)
- Contains 2 columns:
  - **Action**: Description of the action
  - **Awards**: XP value in various formats

### Awards Column Formats

Similar to class awards, race awards use these formats:
- `# XP/day` - XP per day
- `# XP` - Flat XP amount
- `# XP/mile` - XP per mile
- `# XP/12 hours` - XP per 12 hours

### Processing

The race award extraction follows the same pattern as class awards:
1. Identifies "Individual Race Awards" section marker or race award headers
2. Detects race award headers (Dwarf:, Elf:, Half-elf:, etc.)
3. Filters table items by column (RIGHT column, x >= 300)
4. Groups subsequent text blocks into table rows based on spatial layout
5. Pairs Action and Awards columns based on X-coordinate boundaries
6. Creates table markers with `__class_award_table` flag
7. Suppresses original text blocks to avoid duplication
8. Renders tables with proper HTML structure

### Special Handling

- **Column filtering**: Race awards are in the RIGHT column (x >= 300), while class awards are primarily in the LEFT column
- **Boundary detection**: The extraction stops when it detects "roleplaying revolves" text which indicates the start of detailed race descriptions
- **Coordinate boundary**: Uses x=380 as the boundary between Action (left) and Awards (right) columns within the right column of the page

## Individual Class Awards Descriptions

The second "Individual Class Awards" section (Roman numeral III) contains descriptive text about experience awards for each class. Some class descriptions require specific paragraph breaks:

### Paragraph Breaks

- **Cleric:** 2 paragraphs with break at "However,"
- **Templar:** 5 paragraphs with breaks at "DMs should", "Similarly,", "Note that", "Pleasing the"

These paragraph breaks are implemented by splitting text blocks at the line level where the break points occur, using the `__force_paragraph_break` marker.

### Individual Race Awards Description Intro

The opening text for the Individual Race Awards descriptions section (Roman numeral IV) has a paragraph break:

- **Paragraph 1:** "Good roleplaying of the player character races in DARK SUN brings with it substantial experience point awards. Conversely, poor roleplaying brings drastic penalties, regardless of individual class awards."
- **Paragraph 2:** "Judgement of good roleplaying ultimately lies with the DM, so he must be familiar with all the nuances of the Athasian player character races. Players should be careful never to forget the peculiarities of their character's race, and should apply these to all the roleplaying situations they can. The lines of communication between the DM and the players should be clear to allow good roleplaying and to emphasize the unique nature of Dark Sun."

The break occurs at "Judgement of good" and is implemented using the same `__force_paragraph_break` marker mechanism.

## Individual Race Awards Descriptions

The second "Individual Race Awards" section (Roman numeral IV) contains descriptive text about roleplaying each race. Each race has a header followed by explanatory paragraphs:

1. **Dwarf:** - Description of dwarf focus and roleplaying guidelines
2. **Elf:** - Description of elf trust tests and self-reliance (2 paragraphs with break at "With regards to se f-reliance,")
3. **Half-elf:** - Description of half-elf customs and competitions (3 paragraphs with breaks at "In extreme" and "Winning such")
4. **Half-Giant:** - Description of half-giant alignment shifts and imitation (3 paragraphs with breaks at "Sometimes a" and "When a half-giant character shifts")
5. **Halfling:** - Description of halfling curiosity and customs (2 paragraphs with break at "Halflings are honor")
6. **Mul:** - Description of mul exertion abilities
7. **Thri-kreen:** - Description of thri-kreen natural combat abilities (2 paragraphs with break at "Each creature slain and")

### Header Structure

Each race name header in the descriptive section:
- Renders as **H2** (with the colon preserved in display)
- Uses `class="header-h2"` styling with color and font-size
- Appears in the TOC as an indented subheader under "Individual Race Awards"
- Has an inline link back to the top of the document

### Processing

The `_mark_race_description_headers()` function:
1. Tracks occurrences of "Individual Race Awards" headers
2. Identifies the second occurrence (the descriptive section)
3. Searches for blocks starting with race names followed by colons
4. Marks those blocks with `__render_as_race_description_h2` flag
5. Stores the race name in `__race_name` for rendering

The journal transformer then renders these marked blocks with H2 styling using the template:
```html
<p><span class="header-h2" style="color: #ca5804; font-size: 0.9em">{race_name}:</span></p>
```

## Elf Trust Test Lists

Within the Elf race description, there are two H3 headers that introduce lists of trust tests:

### Subtle Tests of Trust

**Header:** "Subtle tests of trust include the following:"

**List Items (4):**
1. entrusting an outsider with a confidential piece of information,
2. leaving a valuable item out in the open, in clear view, to see if the outsider takes it,
3. arranging a secret rendezvous, then making sure the outsider shows up in the right place and on time,
4. asking the outsider to deliver a message or item.

### Life-Threatening Tests of Trust

**Header:** "Life-threatening tests of trust include the following:"

**List Items (4):**
1. letting oneself get captured by gith to see if the outsider attempts a rescue (this is a favorite among elves of the stony barrens),
2. faking unconsciousness after a battle to see what care the outsider provides,
3. making certain part of the water supply is lost on a cross-desert journey, then seeing if he gets a fair share of what's left,
4. challenging a particularly deadly enemy to see if the outsider stands with him or flees.

### Processing

The `_mark_trust_test_sections()` function:
1. Searches for the two trust test header texts
2. When found, marks the block with `__render_as_h3_with_list` flag
3. Collects the following 4 list items based on expected starting words
4. Stores the header text in `__h3_text` and list items in `__list_items`
5. Marks collected list item blocks with `__skip_render` to prevent duplication

The `_collect_list_items_after_header()` function:
1. Scans blocks following the header
2. Identifies list items by their starting words (e.g., "entrusting", "leaving", etc.)
3. Extracts and combines all text from each list item block
4. Returns a list of complete list item texts
5. Marks the original blocks for skipping

The journal transformer renders these as:
```html
<h3>{header_text}</h3>
<ul>
  <li>{list_item_1}</li>
  <li>{list_item_2}</li>
  <li>{list_item_3}</li>
  <li>{list_item_4}</li>
</ul>
```

## Validation

- Confirm all 15 class award tables are present
- Confirm all 7 race award tables are present
- Verify Action and Awards columns are properly aligned for all tables
- Ensure class and race headers render as H2
- Confirm TOC includes all class and race award sections
- Verify relative paths only


