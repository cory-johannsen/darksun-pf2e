# Chapter 10 Processing Specification — Treasure

## Overview

Chapter 10 requires custom processing to handle:
1. Split paragraphs across page boundaries
2. Header level corrections
3. Complex table extraction:
   - Lair Treasures table (treasure types A-J)
   - Individual and Small Lair Treasures table (treasure types J-Z)

## Processing Steps

### 1. Paragraph Merging

**Issue**: The introductory paragraph is split across page boundaries with hyphenation.

**Solution**: 
- Find paragraph starting with "Since Athas is a metal-poor"
- Find continuation with "priate for coins found"
- Merge into complete paragraph: "Since Athas is a metal-poor world, the treasure tables in the Dungeon Master's Guide are inappropriate for coins found in a lair."

**Implementation**: `chapter_10/common.py::merge_paragraph_fragments()`

### 1a. Coins Section Paragraph Breaks

**Issue**: The Coins section should have 4 separate paragraphs, but the rendering logic merges them into a single paragraph.

**Required paragraph breaks at**:
1. "Because metal coins are more valuable on Athas..." (first paragraph)
2. "No platinum or electrum pieces are regularly minted..."
3. "Bits are one-tenth pie pieces of a ceramic piece..."
4. "Ceramic, silver, and gold pieces weigh in at 50 to the pound..."

**Solution**: 
- Mark lines that should start new paragraphs with `__force_line_break` flag
- This forces the rendering logic to create paragraph breaks at these specific locations

**Implementation**: `chapter_10_processing.py::_mark_coins_paragraph_breaks()`

### 2. Header Level Corrections

**Header Levels**:
- H2 headers (font-size: 0.9em, no Roman numerals):
  - "Lair Treasures"
  - "Individual and Small Lair Treasures"
  - "Coins"
  - "Gems"
  - "Objects of Art"
- H3 headers (font-size: 0.8em, no Roman numerals):
  - "Gem Table"

**Implementation**: 
- `chapter_10/tables.py::extract_lair_treasures_table()` - marks "Lair Treasures" header before table extraction
- `journal_lib/toc.py::apply_subheader_styling()` - applies font-size styling for all H2/H3 headers based on chapter slug

### 3. Lair Treasures Table Extraction

**Table Structure**:
- **Columns**: 7
  1. Treasure Type (A-J)
  2. Bits
  3. Ceramic
  4. Silver
  5. Gold
  6. Gems
  7. Magical Item

- **Rows**: 10 (A through J)

**Cell Format**:
Each cell (except Treasure Type) contains 1-2 lines:
- Line 1: Value (e.g., "200-2,000", "-", "Any 2")
- Line 2 (optional): Percentage (e.g., "30%")

**Cell Value Formats**:
- "-" (empty/none)
- "#-#\n#%" (range with percentage)
- "Any #\n#%" (any items with percentage)
- "Any #+# potion\n#%" (items plus potions)
- "Any #+# scroll\n#%" (items plus scrolls)
- "Any # except weapons\n#%" (items excluding weapons)
- "Armor Weapon\n#%" (armor or weapon)

**Extraction Process**:
1. Find "Lair Treasures" header block
2. Collect all text cells between header and "Individual and Small Lair Treasures"
3. Identify treasure type markers (A-J) by single-letter cells
4. Group cells by Y-coordinate (row grouping)
5. Map cells to columns by X-coordinate ranges:
   - Bits: x ∈ [110, 170)
   - Ceramic: x ∈ [180, 250)
   - Silver: x ∈ [260, 330)
   - Gold: x ∈ [340, 410)
   - Gems: x ∈ [415, 480)
   - Magical Item: x ∈ [480, 600)
6. Combine multi-line cells with newline separator
7. Clean whitespace (e.g., "3 0 %" → "30%")

**Implementation**: `chapter_10/tables.py::_extract_table_cells_from_blocks()`, `_organize_cells_into_table()`

**Rendering**: 
- Attach table to header block using `__lair_treasures_table` marker
- Mark intervening blocks with `__skip_render` to remove fragmented content
- Render header + table in `journal_lib/rendering.py`

### 4. Individual and Small Lair Treasures Table Extraction

**Table Structure**:
- **Columns**: 7
  1. Treasure Type (J-Z)
  2. Bits
  3. Ceramic
  4. Silver
  5. Gold
  6. Gems
  7. Magical Item

- **Rows**: 17 (J through Z)

**Cell Format**:
Each cell (except Treasure Type) contains 1-2 lines following these formats:
- "-" (empty/none)
- "#-#" (range)
- "#-#\n#%" (range with percentage)
- "#-# potions" (potions)
- "#-# scrolls" (scrolls)
- "Any #\n#%" (any items with percentage)
- "Any # potions\n#%" (any potions with percentage)
- "Any #+# potion\n#%" (items plus potions with percentage)
- "Any #+# scroll\n#%" (items plus scrolls with percentage)
- "Any # except weapons\n#%" (items excluding weapons)
- "Armor Weapon\n#%" (armor or weapon with percentage)

**Extraction Process**:
1. Find "Individual and Small Lair Treasures" header block
2. Collect all text cells between header and "Coins" header
3. Identify treasure type markers (J-Z) by single-letter cells
4. Group cells by Y-coordinate (row grouping)
5. Map cells to columns by X-coordinate ranges (same as Lair Treasures table):
   - Bits: x ∈ [108, 170)
   - Ceramic: x ∈ [180, 250)
   - Silver: x ∈ [260, 330)
   - Gold: x ∈ [340, 410)
   - Gems: x ∈ [415, 480)
   - Magical Item: x ∈ [480, 600)
6. Combine multi-line cells with newline separator
7. Clean whitespace (e.g., "3 0 %" → "30%", "5 0 %" → "50%")

**Implementation**: `chapter_10/tables.py::extract_individual_treasures_table()`, `_extract_individual_table_cells_from_blocks()`, `_organize_individual_cells_into_table()`

**Rendering**: 
- Attach table to header block using `__individual_treasures_table` marker
- Mark intervening blocks with `__skip_render` to remove fragmented content
- Render header + table in `journal_lib/rendering.py`

## Whitespace Cleaning

Apply standard whitespace cleaning rules (from [WHITESPACE] requirement):
- Remove spaces between digits and % signs
- Remove spaces within numbers
- Remove spaces between single letters in words

**Implementation**: `chapter_10/common.py::clean_whitespace()`

## Files

- **Main Module**: `tools/pdf_pipeline/transformers/chapter_10_processing.py`
- **Common Utilities**: `tools/pdf_pipeline/transformers/chapter_10/common.py`
- **Table Extraction**: `tools/pdf_pipeline/transformers/chapter_10/tables.py`

## Validation

- Relative paths only; TOC before content section
- Paragraph beginning "Since Athas is a metal-poor" should be complete
- "Lair Treasures" must be H2 header
- Lair Treasures table must have 7 columns × 10 rows (treasure types A-J)
- "Individual and Small Lair Treasures" must be H2 header
- Individual and Small Lair Treasures table must have 7 columns × 17 rows (treasure types J-Z)
- All treasure types A-Z must be present
- "Gem Table" must be H3 header
- Gem Table must have 3 columns × 6 data rows
- Gem Table must follow the format: [D100 Roll, Base Value, Class]
- Cell values must match specified formats
- No fragmented table content should appear in output


### 6. Magical Items Section Paragraph Breaks

**Issue**: The Magical Items section should have 5 separate paragraphs and a formatted list of 9 items, but the rendering logic merges them into fewer paragraphs.

**Required paragraph breaks at**:
1. "The nature of magical items..." (first paragraph) - ends with "...traditional pantheon of giants."
2. "If a Dark Sun DM rolls up..." (second paragraph) - ends with "...from years of play."
3. "Other magical items in the DMG..." (third paragraph) - ends with "...obviously do not apply."
4. "A final group of items..." (fourth paragraph) - ends with "...or lycanthropes."
5. "The following items are changed to fit DARK SUN campaigns:" (fifth paragraph)

**Required formatted list**:
Following the fifth paragraph is a list of 9 items, each in "name: description" format:
1. Potion of Giant Control
2. Potion of Giant Strength
3. Potion of Undead Control
4. Rod of Resurrection
5. Boots of Varied Tracks
6. Candle of Invocation
7. Deck of Illusions
8. Figurines of Wondrous Power
9. Necklace of Prayer Beads

**Solution**: 
- Mark lines that should start new paragraphs with `__force_line_break` flag
- Mark each block containing a list item with `__magical_item_entry` flag and `__force_paragraph_break`
- This forces the rendering logic to create paragraph breaks at these specific locations and render each list item in its own paragraph

**Implementation**: 
- `chapter_10_processing.py::_mark_magical_items_paragraph_breaks()` - marks paragraph breaks and identifies each block containing a list item
- `journal_lib/rendering.py::render_magical_item_entry()` - renders each individual item in its own paragraph with proper formatting (bold orange-colored name followed by description)

### 7. Potions Section Formatting

**Issue**: The Potions section requires proper header levels and paragraph breaks. Additionally, the source PDF has a 2-column layout issue where "Magical Enchantment" and "Botanical Enchantment" headers appear in the RIGHT column at a Y-coordinate that would place them BEFORE the "Potions" header in the LEFT column during 2-column rendering.

**Additional Issue**: The "Magical Enchantment:" and "Botanical Enchantment:" headers share the same line as the beginning of their respective paragraphs. For example, "Magical Enchantment: Any wizard, cleric, or" appears as two separate spans in the same line. The header span must be skipped during rendering while preserving the paragraph text.

**H3 Headers**:
- "Magical Enchantment:" should be marked as H3
- "Botanical Enchantment:" should be marked as H3

**Botanical Enchantment Paragraph Breaks**:
The text following "Botanical Enchantment:" header should be broken into 4 separate paragraphs:
1. "Any wizard, ranger, cleric, or druid can use botanical enchantment. Botanical enchantment is the process of using one enchanted fruit to grow more." (first paragraph after header)
2. "The original potion fruit must be planted unused..." (second paragraph) - ends with "...no additional potion fruits from that tree."
3. "If a permanency spell is cast..." (third paragraph) - ends with "...unless it is destroyed."
4. "Botanical enchantment is somewhat risky..." (fourth paragraph) - continues to end of section

**2-Column Reading Order Fix**:
The page containing the Potions section is marked with `__force_single_column` to prevent Y-coordinate-based sorting from placing the enchantment headers before the Potions content. The blocks are reordered during transformation to move blocks 48-54 (Magical/Botanical Enchantment) to after block 47 (last Potions introductory content), and single-column rendering preserves this order by sorting by block array index rather than Y-coordinate.

**Solution**: 
- Mark "Magical Enchantment:" and "Botanical Enchantment:" blocks with `__header_level` = 3 (H3) and `__section_header` = True
- Mark only the header span (not the entire line) with `__skip_render` = True to preserve the paragraph text that follows
- Mark lines starting with "If a permanency" and "Botanical enchantment is somewhat" with `__force_line_break` flag
- Reorder blocks 48-54 to appear after block 47 in the blocks array
- Mark the page with `__force_single_column` to preserve block ordering during rendering

**Implementation**: 
- `chapter_10_processing.py::_mark_potions_paragraph_breaks()` - block reordering and header marking with span-level `__skip_render`
- `journal_lib/rendering.py::render_line()` - skips spans marked with `__skip_render`
- `journal_lib/rendering.py::render_page()` - single-column rendering with order-based sorting

### 8. New Magical Items Section

**Issue**: The New Magical Items section contains specific item headers that should be H2 (without Roman numerals), not H1:
- Amulet of Psionic Interference
- Oil of Feather Falling
- Ring of Life
- Rod of Divining

Each item is followed by "XP Value: #" and a paragraph description.

**Solution**:
- Identify these specific headers by text matching
- Adjust font size to H2 size (14.0) and set `header_level = 2`
- This prevents them from being rendered as H1 with Roman numerals

**Implementation**: `chapter_10_processing.py::_mark_new_magical_items_headers()`

### 5. Gem Table Extraction

**Table Structure**:
- **Columns**: 3
  1. D100 Roll
  2. Base Value
  3. Class

- **Rows**: 6 data rows
  - 01-2, 15 cp, Ornamental
  - 26-50, 75 cp, semi-precious
  - 51-70, 15 sp, Fancy
  - 71-90, 75 sp, Precious
  - 91-99, 15 gp, Gems
  - 00, 75 gp, Jewels

**Cell Format**:
- **D100 Roll**: "#-#" or "#" (e.g., "01-2", "26-50", "00")
- **Base Value**: "# cp" or "# sp" or "# gp" (e.g., "15 cp", "75 sp")
- **Class**: Gem class names (may contain hyphens, e.g., "semi-precious")

**Following Content**:
- Paragraph beginning: "The gem variations and descriptions of the individual stones from the DMG still apply to gems found in Dark Sun."

**Extraction Process**:
1. Find "Gem Table" header block (H3)
2. The table data is stored in a single text block immediately after the header
3. The block contains mixed headers and data at Y~492-636
4. Following the table data at Y~599 is the paragraph starting with "The gem variations"

**Implementation**: `chapter_10/tables.py::extract_gem_table()`

**Rendering**: 
- Attach table to header block using `__gem_table` marker
- Mark the table data block with `__skip_render` to remove fragmented content
- Render header + table in `journal_lib/rendering.py`
- The following paragraph ("The gem variations...") should remain as normal paragraph text


