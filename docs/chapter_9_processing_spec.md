# Chapter 9 Processing Specification — Combat

## Overview

Chapter 9 is processed via `journal` transformer with custom processing in `chapter_9_processing.py` to handle header levels and paragraph breaks in the Arena Combats section.

## Header Structure

### Arena Combats Section

**H1 (Main Header):**
- Arena Combats

**H3 (Game Types):**
These are subsections under Arena Combats describing different types of arena games:
- Games:
- Matinee:
- Grudge Match:
- Trial by Combat:
- Matched Pairs:
- Bestial Combat:
- Test of Champions:
- Advanced Games:

**H2 (Major Sections):**
These are standalone major sections:
- Stables:
- Wagering:
- Trading of Gladiators:

**Other H1 Sections:**
- Battling Undead in Dark Sun
- Turning and Controlling Undead
- Character Death
- Waging Wars
- Piecemeal Armor

**H2 (Combat Sections):**
- Followers

**H2 (Special Section):**
- Hovering on Deaths Door (Optional Rule) - This appears as a merged H2 header combining two separate lines from the source

**H2 (Piecemeal Armor Sections):**
- Important Considerations

**H3 (Piecemeal Armor Sections):**
- Bonus to AC Per Type of Piece

## Paragraph Breaks

### Arena Combats Section
The Arena Combats introductory text is broken into 3 paragraphs at:
1. "Player characters may well find themselves"
2. "The customs of every arena"

### Stables Section
The Stables section is broken into 4 paragraphs at:
1. (intro) "Most noble and merchant houses have stables of slaves..."
2. "Typical stables of slaves have between 10 and 100..."
3. "Every slave in a stable receives minimal training..."
4. "Every stable has its champion or champions..."

### Battling Undead in Dark Sun Section
The Battling Undead introductory text is broken into 4 paragraphs at:
1. (intro) "On Athas, undead are still just that..."
2. "Mindless undead are corpses or skeletal remains..."
3. "Free-willed undead are usually very powerful creatures..."
4. "Quite often, free-willed undead have minions..."

### Turning and Controlling Undead Section
**H1 (Main Header):**
- Turning and Controlling Undead

**H2 (Sub-sections):**
- Turning Undead:
- Commanding Undead:

### Turning Undead Section
The "Turning Undead" section is broken into 2 paragraphs at:
1. (intro) "A cleric on Athas wishing to turn undead..."
2. "Turned undead flee as described in the Player's Handbook..."

### Hovering on Death's Door (Optional Rule) Section
The "Hovering on Death's Door (Optional Rule)" section is broken into 6 paragraphs at:
1. (intro) "DMs may find that their DARK SUN campaign has become too deadly..."
2. "Thereafter, he automatically loses 1 hit point each round..."
3. "If the only action is to bind his wounds, the injured character no longer loses..."
4. "If a cure spell of some type is cast upon him..."
5. "If a heal spell is cast on the character, his hit points are restored..."
6. (final paragraph continues after the heal spell description)

### Waging Wars Section
The "Waging Wars" section is broken into 3 paragraphs at:
1. (intro) "The sands of Athas have been stained red with the blood of a thousand campaigns..."
2. "Player characters will eventually be called upon to fight wars..."
3. "Once player characters must deal with large numbers of troops..."

### Followers Section
The "Followers" section is an H2 and is broken into 2 paragraphs at:
1. (intro) "Though fighters and gladiators automatically gain followers when they reach higher levels..."
2. "A warrior's followers almost never arrive with all of their equipment..."

### Piecemeal Armor Section
The "Piecemeal Armor" section is broken into 2 paragraphs at:
1. (intro) "Dark Sun characters seldom (if ever) wear complete suits of metal armor..."
2. "Determining the correct Armor Class for someone in piecemeal armor..."

**Note:** The "Bonus to AC Per Type of Piece" H3 header and table are moved to appear AFTER the "Important Considerations" section for better readability.

### Important Considerations Section
The "Important Considerations" section is an H2 and is broken into 2 paragraphs at:
1. (intro) "Although piecemeal armor is lighter than full suits of armor..."
2. "Characters wearing piecemeal metal armor are also subject to the exhausting effects..."

### Content Reordering
The "Bonus to AC Per Type of Piece" H3 header and table are moved to appear after the "Important Considerations" section. This prevents the table from interrupting the flow of the piecemeal armor description paragraphs.

## Special Handling

### Bonus to AC Table Reconstruction (chapter_9_processing.py)
The `_extract_and_reconstruct_bonus_ac_table()` function extracts and reconstructs the "Bonus to AC Per Type of Piece" table.

**Table Structure:**
- 7 columns: [Armor Type, Full Suit, Breast Plate, Two Arms, One Arm, Two Legs, One Leg]
- 14 armor type rows in alphabetical order from "Banded Mail" to "Studded Leather"
- Each row's values are generally descending, e.g., "Banded Mail" = [6, 3, 2, 1, 1, 0]

**Extraction Process:**
1. Finds the "Bonus to AC Per Type of Piece" header block
2. Locates detected borderless tables on the same page
3. Extracts armor names and "Full Suit" values from ALL tables (data is fragmented across multiple tables)
4. Collects ONLY numeric values from table cells (skipping cells with armor names)
5. Reconstructs 14 armor rows using alphabetical ordering from armor_types_ordered list
6. Creates properly formatted table with 7 columns and header row
7. Replaces page's table list with single reconstructed table
8. Marks fragmented text blocks to skip rendering

**Status:** ✅ COMPLETE - Table header is H3 and positioned correctly. All 14 armor types successfully extracted from fragmented source data and reconstructed into a clean 7-column, 15-row table. Original fragmented blocks are hidden from output.

### Header Merging (chapter_9_processing.py)
The `_merge_hovering_on_deaths_door_header()` function merges two separate lines:
- "Hovering on Deaths Door" and "(Optional Rule)" are combined into a single H2 header
- The merged header is marked with size 14.88 and header_level 2

### Header Levels (chapter_9_processing.py)
The `_adjust_header_levels()` function adjusts font sizes in the raw PDF data:
- Game type headers (Games through Advanced Games) are set to size 12.0 (H3)
- Major section headers (Stables, Wagering, Trading of Gladiators) are ensured to be size 14.88 (H2)
- Turning Undead section headers (Turning Undead, Commanding Undead) are set to size 14.88 (H2)
- Combat section headers (Followers) are set to size 14.88 (H2)
- Piecemeal Armor section headers (Important Considerations) are set to size 14.88 (H2)

### Paragraph Breaks (chapter_9_processing.py)
The `_prevent_stables_paragraph_break()` function prevents undesired paragraph breaks.
The `_force_battling_undead_paragraph_breaks()` function forces paragraph breaks in the Battling Undead section.
The `_force_turning_undead_paragraph_breaks()` function forces paragraph breaks in the Turning Undead section.
The `_force_hovering_on_deaths_door_paragraph_breaks()` function forces paragraph breaks in the Hovering on Death's Door section.
The `_force_waging_wars_paragraph_breaks()` function forces paragraph breaks in the Waging Wars section.
The `_force_followers_paragraph_breaks()` function forces paragraph breaks in the Followers section.
The `_force_piecemeal_armor_paragraph_breaks()` function forces paragraph breaks in the Piecemeal Armor section.
The `_force_important_considerations_paragraph_breaks()` function forces paragraph breaks in the Important Considerations section.

### Content Reordering (chapter_9_processing.py)
The `_reorder_bonus_ac_table_after_important_considerations()` function moves the "Bonus to AC Per Type of Piece" H3 header and table to appear after the "Important Considerations" section. This improves readability by preventing the table from interrupting the piecemeal armor description text.

### HTML Styling (journal.py)
The HTML generation applies regex patterns to set font-size CSS:
- H3 headers (game types): `font-size: 0.8em`
- H2 headers (major sections): `font-size: 0.9em`
- H2 headers (special): `font-size: 0.9em` for "Hovering on Deaths Door (Optional Rule)"
- H1 headers (default): No size reduction, receive Roman numerals

## Validation

- Ensure headers follow H1/H2/H3 styling rules
- Verify Arena Combats has 3 paragraphs
- Verify Stables has 4 paragraphs
- Verify Battling Undead in Dark Sun has 4 paragraphs
- Verify Turning Undead has 2 paragraphs
- Verify Hovering on Death's Door (Optional Rule) has 6 paragraphs
- Verify Waging Wars has 3 paragraphs
- Verify Followers has 2 paragraphs
- Verify Piecemeal Armor has 2 paragraphs
- Verify "Bonus to AC Per Type of Piece" H3 and table appear AFTER "Important Considerations" section
- Verify Important Considerations has 2 paragraphs
- Verify Game types (Games through Advanced Games) are H3 with smaller font
- Verify Stables, Wagering, Trading of Gladiators are H2
- Verify Turning Undead, Commanding Undead are H2
- Verify Followers is H2
- Verify Important Considerations is H2
- Verify "Bonus to AC Per Type of Piece" is H3
- Verify "Hovering on Deaths Door (Optional Rule)" is a single H2 header
- Verify Bonus to AC table has 7 columns and 15 rows (1 header + 14 armor types)
- Verify armor types are in alphabetical order from "Banded Mail" to "Studded Leather"
- Ensure all headers have anchor links [^] to return to top


