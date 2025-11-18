# Chapter 11 Processing Specification — Encounters

## Overview

Chapter-specific processing with header merging, paragraph breaks, and header level styling.

## Special Processing

### Header Merging

The first section header in the source appears as two lines:
- Line 1: "Wizard, Priest, and Psionicist"
- Line 2: "Encounters"

These should be merged into a single header: "Wizard, Priest, and Psionicist Encounters"

This is handled in `chapter_11_processing.py` by:
1. Finding the block containing both lines
2. Merging the text into the first line
3. Removing the second line
4. Updating bounding boxes appropriately

### Paragraph Breaks

#### Wizard, Priest, and Psionicist Encounters (2 paragraphs)
- First paragraph: "Spellcasters and psionicists pose..."
- Second paragraph: "At times, an encounter with a large group..."

#### Encounters in City-States (3 paragraphs)
- First paragraph: "Athasian city states are usually very crowded..."
- Second paragraph: "When dealing with encounters in a city..."
- Third paragraph: "Specific encounters should be set up by the DM..."

#### Plant-Based Monsters (1 paragraph)
- Single paragraph: "Defiling magic destroys all plant-life within its area of effect without exception. A plant-based monster can thus be destroyed (or injured if it isn't wholly contained within the area of effect), with no save allowed."
- The text appears across multiple lines in the source PDF but should be merged into a single paragraph

### Header Structure

#### H1 Headers (Main Sections)
- Wizard, Priest, and Psionicist Encounters (header-0)
- Encounters in City-States (header-1)
- Monsters (header-2)
- Wilderness Encounters (header-11)

#### H2 Headers (Under Monsters)
- Magic: (header-3)
- Psionics: (header-4)
- Plant-Based Monsters: (header-5)
- Monstrous Compendium 1 and 2 (header-6)
- Forgotten Realms® (MC3) (header-7)
- Dragonlance® (MC4) (header-8)
- Greyhawk® (MC5) (header-9)
- Kara-Tur (MC6) (header-10)

These H2 headers appear under the "Monsters" section and provide more specific guidance about monster types.

#### Special: Monstrous Compendium List

"Monstrous Compendium 1 and 2" introduces an alphabetical list of monster types that spans two columns:
- List items are single words or short phrases (may contain whitespace, commas, asterisks, parentheses)
- Left column starts at x~50
- Right column starts at x~313
- The right column items (starting with "Hornet") appear earlier in Y-coordinates than the header itself
- This requires special handling to extract the list in proper order and group it under the correct header

### Postprocessing

The `chapter_11_postprocessing.py` module applies H2 styling:
- Adds `h2-header` CSS class to H2 headers
- Removes Roman numerals from H2 headers
- Adds `font-size: 0.9em` to H2 header spans
- Adds `toc-subheader` class to H2 entries in the TOC for indentation
- Renumbers Roman numerals on subsequent H1 headers (VI becomes IV, etc.)

## Validation

- Check that "Wizard, Priest, and Psionicist Encounters" appears as a single header (H1)
- Check that Magic, Psionics, and Plant-Based Monsters are H2 headers
- Check anchors and TOC placement
- Verify section wrapper
- Verify paragraph breaks are correct in both sections
- Verify Plant-Based Monsters text is a single paragraph (not split)
- Verify H2 headers have no Roman numerals
- Verify H2 headers display at correct size (smaller than H1)
- Verify TOC shows proper indentation for H2 headers


