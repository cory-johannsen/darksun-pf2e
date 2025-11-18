# Chapter 5 Processing Specification — Proficiencies

## Overview

Uses `journal`. Tables are handled by generic extraction and rendering, with special postprocessing for the New Nonweapon Proficiencies table.

## Header Structure

### Header Levels

Chapter 5 uses a three-level header hierarchy:

**H1 Headers (1.2rem)** - Main section headers:
- "Dark Sun Weapon Proficiencies"
- "New Nonweapon Proficiencies"

**H2 Headers (1.1rem)** - Subsection headers:
- "Description of New Proficiencies"
- "Nonweapon Proficiency Group Crossovers"
- "Use of Existing Proficiencies in Dark Sun"
- "Use of Survival Proficiency in Dark Sun"

**H3 Headers (1.0rem)** - Individual item headers:
- Individual proficiency names: "Armor Optimization:", "Bargain:", "Bureaucracy:", "Heat Protection:", "Psionic Detection:", "Sign Language:", "Somatic Concealment:", "Water Find:", "Weapon Improvisation:"
- Sub-items under crossovers: "Character Class", "Proficiency Groups"
- Individual proficiency clarifications: "Agriculture:", "Armorer:", "Artistic Ability:", "Blacksmithing:", "Fishing:", "Navigation:", "Religion:", "Seamanship:", "Swimming:", "Weaponsmithing:"

### Special Header Handling

**Armor Optimization Extraction:**
The PDF extraction incorrectly merges "Armor Optimization:" into the "Description of New Proficiencies" paragraph. Postprocessing:
1. Extracts "Armor Optimization:" from the paragraph
2. Creates a separate H3 header for it
3. Applies proper styling with class="h3-header"

## Paragraph Breaks

### Introduction (Pre-Header Content)
The opening content should be split into 2 paragraphs:

1. First paragraph: "In Dark Sun, both weapon and nonweapon proficiencies generally follow the guidelines in the Player's Handbook. Any exceptions to typical AD&D® game mechanics appear in this chapter."

2. Second paragraph: "Dark Sun characters often have higher attribute scores than those in other AD & D campaign worlds. As a result, Dark Sun characters can more easily accomplish proficiency checks, which are based upon attributes. Even so, players should remember that rolling a natural 20 still results in failure, regardless of their characters' attribute scores."

**Break marker:** "Dark Sun characters often"

### Dark Sun Weapon Proficiencies
The "Dark Sun Weapon Proficiencies" section should be split into 3 paragraphs:

1. First paragraph: "Weapon proficiencies and specialization function as usual for all Dark Sun character classes extent the gladiator class. Gladiators begin the game with proficiency in every weapon. In addition, they can specialize in any number of weapons, provided they have enough slots available to do so. A gladiator must spend two slots to specialize in any melee or missile weapon except a bow, which requires three slots. Gladiators thus transcend the rule that limits specialization to fighters."

2. Second paragraph: "For example, Barlyuth, a dwarven gladiator, starts the game with four weapon proficiency slots. As a gladiator, he already holds proficiency in all weapons, so he needn't spend any of his four slots to become proficient. Instead, he may spend all four slots to specialize in two melee weapons, or spend three slots to specialize in a bow weapon and save the remaining slot for later specialization."

3. Third paragraph: "A 9th-level gladiator could thus specialize in two melee weapons and one bow weapon (seven total weapon proficiency slots) and an 18th-level gladiator could specialize in five melee weapons (10 total weapon proficiency slots). A gladiator gains all the benefits for every weapon in which he specializes, suffering no penalty for multiple specializations."

**Break markers:** "For example, Barlyuth" and "A 9th-level gladiator could thus"

## Tables

### New Nonweapon Proficiencies Table

This is a complex table under the "New Nonweapon Proficiencies" header with the following structure:

**Columns:** Proficiency, Slots, Ability, Modifier

**Sections:**
- **GENERAL** (5 rows): Bargain, Heat Protection, Psionic Detection, Sign Language, Water Find
- **PRIEST** (1 row): Bureaucracy
- **WARRIOR** (3 rows): Armor Optimization, Weapon Improvisation, Somatic Concealment
- **WIZARD** (1 row): Somatic Concealment

**Special Handling:**
- The raw extraction treats table columns and section headers as document headers
- Postprocessing reconstructs the table by:
  1. Extracting text from malformed paragraphs and headers
  2. Parsing proficiency data (handling multi-word proficiency names)
  3. Normalizing ability scores (removing extraneous whitespace like "W i s" → "Wis")
  4. Building proper HTML table with section headers as colspan rows
- Section headers use `background-color: var(--accent-light)` styling
- Column headers (Proficiency, Slots, Ability, Modifier) are repeated for each section

## Validation

- Verify table header styling and TOC anchors
- Verify intro paragraphs are correctly split into 2 paragraphs
- Verify Dark Sun Weapon Proficiencies section is correctly split into 3 paragraphs
- Verify New Nonweapon Proficiencies table has correct structure with 4 sections
- Verify GENERAL section has 5 rows, PRIEST has 1 row, WARRIOR has 3 rows, WIZARD has 1 row
- Verify all ability scores are properly normalized (no extra spaces)


