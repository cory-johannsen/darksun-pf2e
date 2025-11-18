# Chapter 5: Monsters of Athas Processing Specification

## Overview

Chapter Five: Monsters of Athas contains both descriptive creature entries and formal Monster Manual pages. The chapter uses structured tables for detailed monster statistics following AD&D 2E conventions.

## Structure

### Introduction (3 Paragraphs)
1. "Life is a mysterious... sun-baked clay."
2. "To survive... pages that follow."
3. "Over the course... is often deadly on Athas."

### Animals, Domestic
- **Format**: Multi-column table (5 columns: label + 4 creatures)
- **Creatures**: Erdlu, Kank, Mekillot, Inix
- **Rows**: 22 data rows + 1 header row
- **Status**: ✅ Complete (implemented in `_reconstruct_animals_domestic_table()`)

### Monster Manual Pages

The following 10 monsters each have a dedicated monster manual page:
1. Belgoi
2. Braxat
3. Dragon of Tyr
4. Dune Freak (Anakore)
5. Gaj
6. Giant, Athasian
7. Gith
8. Jozhal
9. Silk Wyrm
10. Tembo

## Monster Manual Page Format

Each monster manual page follows this structure:

### Page Layout

```
{Title}

{Monster Statistics Table}

[Optional] {Psionics Summary}

Combat: {Combat description text}

Habitat/Society: {Habitat/Society description text}

Ecology: {Ecology description text}
```

### Monster Statistics Table

**Format**: 2 columns × 21 rows

**Column Structure**:
- Column 1: Stat label (e.g., "CLIMATE/TERRAIN:", "FREQUENCY:", etc.)
- Column 2: Stat value

**IMPORTANT**: Every monster manual page contains ALL 21 rows. The source PDF may merge multiple rows together without line breaks. Processing must use the known valid value patterns (documented below) to intelligently split merged text and reconstruct proper line breaks.

**LINE BREAK RECONSTRUCTION RULE**: For rows with documented valid value ranges, any text that does NOT match those valid values/patterns is NOT part of that row and requires a line break. This allows intelligent splitting of merged text by detecting value boundaries.

**Row Groups** (separated by horizontal lines in source):

#### Group 1 (Rows 1-3):
- Row 1: **CLIMATE/TERRAIN** - Text string, may contain commas, may span two lines
  - **Valid values**: "Any", "Tablelands", "Tablelands, Mountains, and Hinterlands", "Any sandy region", "Sands, stony barrens, rocky badlands, and islands", "Sea of Silt Islands, Tablelands", "Tablelands, Mountains", "Tablelands and Hinterlands", "Badlands", "Tablelands and mountains"
- Row 2: **FREQUENCY** - One of: Uncommon, Rare, Very Rare, Unique
- Row 3: **ORGANIZATION** - One of: Tribe, Solitary, Small Tribes, Clans, Tribal, Family, Pack

#### Group 2 (Rows 4-6):
- Row 4: **ACTIVITY CYCLE** - One of: Night, Any, Day, Day/Night, Nocturnal
- Row 5: **DIET** - One of: Omnivore, Carnivore
- Row 6: **INTELLIGENCE** - Format: "Word" or "Word (#)" or "Word (#-#)" where # is a number
  - Examples: "Low (5-7)", "High (13-14)", "Supra-genius (20)"

#### Group 3 (Rows 7-8):
- Row 7: **TREASURE** - Format: "X, (X)", "X, X", "(X)", "X", "X (Individual), X (Lair)" where X is a capital letter
  - **Note**: May appear with extra whitespace in source (e.g., "TRE AS U R E")
  - Examples: "M,(I)", "R, V", "Y (I)", "Z"
- Row 8: **ALIGNMENT** - One of: Neutral evil, Lawful evil, Varies by individual, Chaotic, Chaotic neutral, Neutral

#### Group 4 (Rows 9-11):
- Row 9: **NO. APPEARING** - Format: "#", "#-#", "# or #", "#-# (#d#)", "#-# (#d#+#)" where # is a number
  - Examples: "1-10", "1 or 2", "2-12 (2d6)"
- Row 10: **ARMOR CLASS** - Number (may be negative)
  - Examples: "5", "-10", "9"
- Row 11: **MOVEMENT** - Number or complex movement notation
  - Examples: "12", "15, Fl 45 (A), Jp 5, Br 6"

#### Group 5 (Rows 12-14):
- Row 12: **HIT DICE** - Number or dice notation
  - Examples: "7", "32 (250 hit points)"
- Row 13: **THAC0** - Number (may be negative)
  - **Note**: May be recorded as "THACo" in source (lowercase 'o')
  - Examples: "13", "-3"
- Row 14: **NO. OF ATTACKS** - Format: "#", "# or #", "# + breath weapon or spell & psionic" where # is a number
  - Examples: "1", "1 or 2", "4 + breath weapon or spell & psionic"

#### Group 6 (Rows 15-17):
- Row 15: **DAMAGE/ATTACK** - Complex damage notation
  - Formats: "#d#", "#d#+#", "by weapon +#", "by weapon #d# / #d#", "#d#+# / #d#+# / #d# / #d#", "#d# / #d#", "#d# or by weapon -# or #d# / #d#", "#d# (x#) / #d# (x#) / #d#"
  - **Known error**: "Giant, Athasian" has "2-16 + 14" which should be "2d6 + 14"
  - Examples: "1d4+2", "2d10+15/2d10+15/4d12/5d10", "by weapon +10"
- Row 16: **SPECIAL ATTACKS** - Text description
  - Examples: "Constitution drain", "Breath Weapon", "Nil", "See below"
- Row 17: **SPECIAL DEFENSES** - Text description
  - Examples: "Nil", "Hit only by magical or steel weapons", "See below"

#### Group 7 (Rows 18-21):
- Row 18: **MAGIC RESISTANCE** - Format: "Nil" or "#%" where # is a number
  - Examples: "Nil", "10%", "80%"
- Row 19: **SIZE** - Format: "X", "X (#-#')", "X (#' xxx)", "X (# xxx)" where X is a capital letter [S, M, L, H, G]
  - **Known error**: "Silk Wyrm" has "L (501 long)" which should be "L (50' long)"
  - Examples: "M (6' tall)", "L (50' long)", "H (20-30')", "G (40' tall)"
- Row 20: **MORALE** - Format: "Xxx (#)" or "Xxx (#-#)" where Xxx is a capitalized word
  - Examples: "Average (8-10)", "Fearless (20)", "Steady (11-12)"
- Row 21: **XP VALUE** - Number that may contain comma
  - Examples: "65", "1,400", "5,000", "42,000"

### Line Break Reconstruction Examples

When the source merges multiple rows without line breaks, use valid value ranges to detect boundaries:

**Example 1: Categorical Fields**
```
Source: "TablelandsUncommonTribe"
Parse as:
  CLIMATE/TERRAIN: Tablelands  ← valid CLIMATE/TERRAIN value
  FREQUENCY: Uncommon          ← NOT valid CLIMATE/TERRAIN, so line break here
  ORGANIZATION: Tribe          ← NOT valid FREQUENCY, so line break here
```

**Example 2: Format-Based Fields**
```
Source: "Omnivore5-7"
Parse as:
  DIET: Omnivore              ← valid DIET value
  INTELLIGENCE: 5-7           ← matches pattern "# or #-#", NOT valid DIET
```

**Example 3: Numeric Fields**
```
Source: "1215"
Parse as:
  MOVEMENT: 12                ← number for MOVEMENT
  HIT DICE: 15                ← number for HIT DICE (MOVEMENT values are typically 1-2 digits)
```

**Key Principle**: If a value doesn't match the documented valid values or format for the current row, it belongs to the next row. Insert a line break at that boundary.

### Known Source Errors to Correct

The following errors exist in the source PDF and should be corrected during processing:

1. **Giant, Athasian - DAMAGE/ATTACK**: Source has "2-16 + 14", should be "2d6 + 14"
2. **Silk Wyrm - SIZE**: Source has "L (501 long)", should be "L (50' long)"
3. **THAC0 spelling**: Some monsters may have "THACo" (lowercase 'o') instead of "THAC0"
4. **MORALE spacing**: May appear as "MOR A L E" instead of "MORALE"
5. **TREASURE spacing**: May appear as "TRE AS U R E" instead of "TREASURE"
6. **Extraneous whitespace**: 
   - "N i l" should be "Nil"
   - "M u l e" should be "Mule"
7. **Nines vs Sevens**: The source sometimes incorrectly uses "7" where "9" is intended

### Optional: Psionics Summary

**Format**: Multi-section block containing:

1. **Details text** (optional) - Descriptive paragraph about psionic capabilities
2. **Psionics Table** - 5 columns × 2 rows:
   - Headers: `Level | Dis/Sci/Dev | Attack/Defense | Score | PSPs`
   - Data row: Contains specific values for the monster

3. **Psionic Details List** (optional) - Each item is a line beginning with psionic name in bold:
   ```
   Discipline -- Sciences: list; Devotions: list.
   Discipline -- Sciences: list; Devotions: list.
   ```

### Description Sections

After the table (and optional Psionics Summary), there are 3 mandatory description sections:

1. **Combat:** - Paragraph(s) describing combat tactics and abilities
2. **Habitat/Society:** - Paragraph(s) describing social structure and environment
3. **Ecology:** - Paragraph(s) describing ecological role and resource use

## Processing Requirements

### Extraction Challenges

The PDF extraction creates scattered paragraph fragments for monster pages because:
1. The two-column table layout confuses the extraction order
2. Row labels and values are extracted as separate text blocks
3. Table structure is lost entirely

### Postprocessing Strategy

For each of the 10 monster manual pages:

1. **Identify page boundaries** - Find the monster header (e.g., "Belgoi") through the description sections
2. **Extract table data** - Parse the scattered paragraphs between header and "Combat:" section
3. **Reconstruct table** - Build proper 2-column, 22-row HTML table
4. **Parse psionics** - If present, extract and format the Psionics Summary table and details
5. **Preserve descriptions** - Keep Combat, Habitat/Society, and Ecology sections intact
6. **Remove fragments** - Delete all scattered paragraph remnants used to build the table

### Table Reconstruction Algorithm

```python
def reconstruct_monster_table(paragraphs: List[str]) -> Dict[str, str]:
    """
    Parse scattered paragraph fragments to extract 21 table rows.
    
    Returns dict mapping stat names to values:
    {
        'CLIMATE/TERRAIN': 'Tablelands',
        'FREQUENCY': 'Uncommon',
        ...
    }
    """
```

### HTML Output Format

```html
<h2 id="header-N-monster-name">Monster Name <a href="#top">[^]</a></h2>

<table class="monster-stats">
  <tr>
    <td class="stat-label">CLIMATE/TERRAIN:</td>
    <td class="stat-value">Tablelands</td>
  </tr>
  <!-- 20 more rows -->
</table>

<!-- Optional Psionics Summary -->
<div class="psionics-summary">
  <h3>PSIONICS SUMMARY:</h3>
  <table class="psionics-table">
    <tr>
      <th>Level</th>
      <th>Dis/Sci/Dev</th>
      <th>Attack/Defense</th>
      <th>Score</th>
      <th>PSPs</th>
    </tr>
    <tr>
      <td>--</td>
      <td>2/1/5</td>
      <td>EW, PB / M--</td>
      <td>12</td>
      <td></td>
    </tr>
  </table>
  <p><strong>Telepathy --</strong> Sciences: domination; Devotions: attraction, ego whip, psionic blast, mind blank, contact.</p>
</div>

<p><strong>Combat:</strong> {combat description}</p>
<p><strong>Habitat/Society:</strong> {habitat description}</p>
<p><strong>Ecology:</strong> {ecology description}</p>
```

## Validation

### Monster Table Validation
- [x] Each of the 10 monsters has properly structured table
- [x] All 21 rows present for each monster (PSIONICS moved to separate section)
- [x] Row values match source PDF format specifications
- [x] No extraneous whitespace in stat values (e.g., "N i l" → "Nil")

### Psionics Summary Validation
- [ ] Belgoi: Has psionics table (Telepathy)
- [ ] Braxat: Has psionics table (Telepathy)
- [ ] Dragon of Tyr: Has psionics table (6 disciplines + spells)
- [ ] Dune Freak: No psionics
- [ ] Gaj: Has psionics table (Telepathy)
- [ ] Giant, Athasian: Has psionics note (special handling)
- [ ] Gith: Has psionics table (Telepathy + Psychokinesis)
- [ ] Jozhal: Has psionics table (Psychoportation + Telepathy + Spells)
- [ ] Silk Wyrm: Has psionics table (Psychometabolism)
- [ ] Tembo: Has psionics table (Psychometabolism)

### Description Section Validation
- [ ] All monsters have Combat section
- [ ] All monsters have Habitat/Society section
- [ ] All monsters have Ecology section
- [ ] Sections are properly paragraphed (not fragmented)

## Special Cases

### Dragon of Tyr
- Most complex entry with extensive psionics (6 disciplines)
- Includes both psionic powers AND defiler spells
- XP VALUE is very high: 42,000

### Giant, Athasian
- Psionics Summary contains explanatory text about humanoid vs. beast-headed variants
- Does not follow standard psionics table format exactly

### Gaj, Gith, Jozhal
- These have NO headers in the source (unlike Belgoi, Dragon of Tyr, etc. which have headers)
- Need to detect these by pattern matching on the leading text

## Implementation Files

- **Processing**: `tools/pdf_pipeline/postprocessors/chapter_five_monsters_postprocessing.py`
- **Tests**: `tests/regression/test_chapter_five_monsters.py`
- **Spec**: This file (`docs/chapter_five_monsters_processing_spec.md`)

## Status

- [x] Introduction paragraph breaks ✅
- [x] Animals, Domestic table reconstruction ✅  
- [x] Belgoi monster manual page ✅
- [x] Braxat monster manual page ✅
- [x] Dragon of Tyr monster manual page ✅
- [x] Dune Freak (Anakore) monster manual page ✅
- [x] Gaj monster manual page ✅
- [x] Giant, Athasian monster manual page ✅
- [x] Gith monster manual page ✅
- [x] Jozhal monster manual page ✅
- [x] Silk Wyrm monster manual page ✅
- [x] Tembo monster manual page ✅

