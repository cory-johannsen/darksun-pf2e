# Chapter 7 Processing Specification — Magic

## Overview

Processed with `journal` and `chapter_7_processing`.

## Header Structure

The chapter contains the following header hierarchy:

- **H1 (size 14.88)**: Main section headers
  - Priestly Magic
  - Wizardly Magic
  
- **H3 (size 9.6)**: Sphere subsections under Priestly Magic
  - Sphere of Earth
  - Sphere of Air
  - Sphere of Fire
  - Sphere of Water
  - Sphere of the Cosmos

## Spell List Formatting

Each sphere header is followed by a list of spells. Each spell is formatted as:
- **Format**: `Spell Name (level)`
- **Example**: `Magical Stone (1st)` or `Transport Via Plants (6th)`

### HTML Rendering

Spell lists are rendered as HTML unordered lists:
```html
<ul class="spell-list">
  <li class="spell-list-item">Magical Stone (1st)</li>
  <li class="spell-list-item">Dust Devil (2nd)</li>
  ...
</ul>
```

### Structured Data Export

Spell data is extracted and saved to `data/processed/chapter-seven-spells.json`:
```json
{
  "chapter": "Chapter 7 - Magic",
  "spheres": {
    "Sphere of Earth": [
      {"name": "Magical Stone", "level": "1st", "sphere": "Sphere of Earth", "page": 0, "block": 5},
      ...
    ],
    ...
  },
  "metadata": {
    "total_spheres": 5,
    "total_spells": 150
  }
}
```

## Processing Logic

The `chapter_7_processing.py` module:
1. **Merges Wizardly Magic intro paragraph**: Combines the 5 text blocks between "Wizardly Magic" and "Defiling" headers into a single paragraph
2. Adjusts sphere header sizes from 10.8 (H2) to 9.6 (H3) to reflect proper hierarchy
3. Parses spell lists using regex pattern `^(.+?)\s*\((\d+(?:st|nd|rd|th))\)\s*$`
4. Extracts spell name and level from each spell block
5. **Extracts embedded spells from mixed-content blocks**: Uses pattern `(?:^|(?<=[^A-Za-z]))([A-Z][a-z]+(?:[\s\-\'&]+(?:or|and|of|with|to|from|the)?[\s\-\'&]*[A-Z][a-z]+|[\s\-\'&]*[IVX]+)*)\s+\((\d+(?:st|nd|rd|th))\)` to find spells embedded in prose (e.g., "Animal Summoning II (5th)" within paragraph text)
6. Handles 2-column layout by tracking sphere state per column (left/right)
7. Marks spell blocks with `_render_as: "spell_list_item"` for special rendering
8. Saves structured spell data to JSON file

### Wizardly Magic Paragraph Merge

The text between "Wizardly Magic" and "Defiling" headers is extracted as 5 separate blocks due to line breaks in the PDF:
- Block 36: "Wizards draw their magical energies from the living things and life-giving elements around them."
- Block 37: "Preservers cast spells in harmony with nature, using"
- Block 38: "their magic so as to return to the land what they take"
- Block 39: "from it. Defilers care nothing for such harmony and"
- Block 40: "damage the land with every spell they cast."

These are merged into a single paragraph during processing.

### Column-Aware Parsing

Chapter 7 uses a 2-column layout on some pages (e.g., page 61). The spell parsing logic:
- Detects column based on X coordinate (< 200 is left, >= 200 is right)
- Tracks current sphere independently for each column
- Persists sphere state across pages until reset by a new header
- This prevents "Wizardly Magic" header in the right column from resetting spell parsing in the left column

### Embedded Spell Extraction

Due to the 2-column PDF layout, some spells in the Sphere of the Cosmos appear embedded within prose paragraphs rather than as dedicated spell list items. The processing logic includes:

1. **Regex Pattern for Embedded Spells**: `(?:^|(?<=[^A-Za-z]))([A-Z][a-z]+(?:[\s\-\'&]+(?:or|and|of|with|to|from|the)?[\s\-\'&]*[A-Z][a-z]+|[\s\-\'&]*[IVX]+)*)\s+\((\d+(?:st|nd|rd|th))\)`
   - Handles spell names with multiple capitalized words: "Animal Growth", "Commune With Nature"
   - Handles Roman numerals: "Animal Summoning II", "Animal Summoning III"
   - Uses negative lookbehind to avoid matching partial spell names (e.g., "Light Wounds" in "Cure Light Wounds")

2. **Filtering False Positives**:
   - Skips matches preceded by lowercase letters (mid-sentence fragments)
   - Skips matches followed by "level" (e.g., "magic (5th level)")
   - Removes "Sphere " prefix if attached to spell name (e.g., "Sphere Anti-Plant Shell" → "Anti-Plant Shell")
   - Skips common prose prefixes: "Those spells", "These", "All spells", "Such spells", "The"

3. **Extraction Locations**:
   - **Within Cosmos Section**: Scans the section between Cosmos header and Wizardly Magic header
   - **After Wizardly Magic**: Checks 5000 chars after Wizardly Magic header for spells that belong to Cosmos but were displaced by column layout
   - **Note**: Does NOT extract from before Cosmos header, as those spells belong to earlier spheres (Fire, Water)

### Postprocessing

The `chapter_7_postprocessing.py` module:
1. Removes duplicate table elements
2. **Fixes cosmos spell ordering** due to 2-column layout rendering issues:
   - Extracts embedded 5th/6th/7th level spells from paragraph text within and after the Cosmos section
   - Converts extracted spells to `<li class="spell-list-item">` elements
   - Places them in a properly formatted `<ul class="spell-list">` within the Cosmos section
   - Removes spell text from prose paragraphs to avoid duplication
   - Updates `data/processed/chapter-seven-spells.json` with newly extracted spells
   - Includes cross-sphere duplicate detection to prevent spells from Fire/Water/etc being added to Cosmos
3. Separates prose paragraphs from spell lists in Sphere of the Cosmos:
   - Extracts fragmented paragraphs about clerics and deities
   - Reassembles them as complete paragraphs
   - Places them after the spell list but before Wizardly Magic section
4. Adds line breaks before sphere headers:
   - Inserts `<br>` tags before Sphere of Air, Fire, Water, and Cosmos headers
   - Provides visual separation between spell lists and sphere headers
   - Sphere of Earth is excluded as it immediately follows Priestly Magic

## Validation

- Ensure dehyphenation and merged lines are correct
- Verify sphere headers appear as H3 (subheaders) in the output
- Verify "Priestly Magic" and "Wizardly Magic" appear as H1 (main headers)
- Verify spell lists are rendered as HTML `<ul>` with one spell per `<li>` element
- Verify structured spell JSON is created with complete spell data
- **Verify Sphere of the Cosmos completeness**: Run `test_chapter7_cosmos_sphere_completeness.py` to ensure all 41+ spells (including 5th-7th level) are extracted correctly
  - Test validates that embedded spells like "Animal Summoning II", "Anti-Plant Shell", "Symbol" are present
  - Test ensures spells appear as list items in HTML, not mixed into prose paragraphs
  - Test verifies JSON contains complete spell data with correct sphere assignments


