# Chapter-Specific Processing Index

## Overview

Several chapters in the Dark Sun Box Set require custom processing due to complex layouts, tables, and PDF extraction artifacts. This document indexes all chapter-specific processing documentation.

## Chapters with Custom Processing

### Chapter 2: Player Character Races

**Documentation:** `docs/chapter_2_processing_spec.md`  
**Implementation:** `tools/pdf_pipeline/transformers/chapter_2_processing.py`  
**Archived HTML Processing:** `archive/old_implementation/tools/pdf_pipeline/postprocess.py`

**Processing Scope:**
- 3 complex multi-column tables (Ability Adjustments, Requirements, Class Limits)
- Text reordering fixes (Dwarves section)
- Paragraph break detection for 7 race sections
- Mid-sentence paragraph splits across pages
- Two-column layout fragmentation handling
- Special block/line markers for rendering control

**Complexity:** 🔴🔴🔴 **High** (849 lines of custom code)

**Status:**
- ✅ PDF-level processing active
- ⚠️  HTML post-processing disabled (needs migration)

**Tables Extracted:**
1. Table 2: Ability Adjustments (2 columns, 7 rows)
2. Racial Ability Requirements (8 columns, 7 rows)
3. Table 3: Racial Class And Level Limits (9 columns, 13 rows)
4. Other Languages (2 columns, 8+8 rows)

**Paragraph Break Fixes:**
- Elves: 11 paragraphs
- Elves Roleplaying: 3 paragraphs
- Half-Elves: 11 paragraphs
- Half-Elves Roleplaying: 3 paragraphs
- Half-Giants: 10 paragraphs

### Chapter 3: Player Character Classes

**Documentation:** `docs/chapter_3_processing_spec.md` (TODO)  
**Implementation:** `tools/pdf_pipeline/transformers/chapter_3_processing.py`  
**Archived HTML Processing:** `archive/old_implementation/tools/pdf_pipeline/chapter_3_postprocessing.py`

**Processing Scope:**
- Complex class tables
- Multi-column text layouts
- Class-specific special abilities

**Complexity:** 🔴🔴 **Medium-High** (427 lines of custom code)

**Status:**
- ✅ PDF-level processing active
- ⚠️  HTML post-processing archived (needs review)

### Other Chapters

**Status:** Use generic `journal` transformer without custom processing.

**Examples:**
- Chapter 1: Ability Scores (simple, no custom processing needed)
- Chapter 4: Alignment (simple)
- Chapter 5: Proficiencies (tables handled generically)
- Chapter 6-15: Various topics (no special handling)

## Processing Techniques Used

### 1. Table Extraction

**When:** Complex multi-column tables in PDF  
**How:** 
- Detect table boundaries (headings, footers)
- Extract cells from blocks
- Build matrix with row tolerance
- Filter to known content
- Generate HTML table structure

**Chapters:** 2, 3

### 2. Paragraph Break Detection

**When:** Two-column layout merges paragraphs  
**How:**
- Mark blocks/lines with paragraph start patterns
- Use `__force_paragraph_break` markers
- Split mid-sentence with special markers

**Chapters:** 2 (extensive), 3 (moderate)

### 3. Text Reordering

**When:** PDF extraction produces out-of-order text  
**How:**
- Detect misplaced blocks by content
- Reposition in correct order
- Update bounding boxes

**Chapters:** 2 (Dwarves section)

### 4. Block/Line Markers

**Purpose:** Control rendering without modifying source text  
**Types:**
- `__force_paragraph_break` - Block-level
- `__force_line_break` - Line-level
- `__split_at_*` - Mid-sentence splits
- `__*_section` - Section grouping

**Chapters:** 2 (10+ marker types)

### 5. HTML Post-Processing

**When:** PDF-level fixes insufficient  
**How:**
- Regex-based HTML modifications
- Paragraph merging/splitting
- Element reordering
- Text cleanup

**Status:** Mostly disabled (archived)  
**Chapters:** 2, 3

## Implementation Patterns

### Standard Chapter Processing

```python
def apply_chapter_N_adjustments(section_data: dict) -> None:
    """Apply all Chapter N specific adjustments."""
    pages = section_data.get("pages", [])
    if not pages:
        return
    
    # Page-specific processing
    if len(pages) > 0:
        _process_page_0_tables(pages[0])
    
    if len(pages) > 1:
        _fix_page_1_paragraphs(pages[1])
    
    # Cross-page processing
    _fix_section_paragraph_breaks(pages)
```

### Table Detection Pattern

```python
def _process_table(page: dict) -> None:
    """Extract and format a table from page."""
    # 1. Find heading
    heading = _find_block(page, lambda texts: "Table N:" in texts)
    
    # 2. Determine boundaries
    y_min = heading_bbox[1] - 2.0
    y_max = next_heading_bbox[1] if next_heading else page_height
    
    # 3. Collect cells
    cells = _collect_cells_from_blocks(page, table_blocks)
    
    # 4. Build matrix
    rows = _build_matrix_from_cells(cells, expected_columns=N)
    
    # 5. Filter and format
    filtered_rows = [row for row in rows if row[0] in allowed_values]
    
    # 6. Create table structure
    table = _table_from_rows(filtered_rows, header_rows=1, bbox=bbox)
    page.setdefault("tables", []).append(table)
```

### Paragraph Break Pattern

```python
def _fix_section_paragraph_breaks(pages: list) -> None:
    """Force paragraph breaks at specific sentences."""
    paragraph_starts = [
        "First sentence of para 1",
        "First sentence of para 2",
        # ...
    ]
    
    for page in pages:
        for block in page.get("blocks", []):
            first_text = get_first_line_text(block)
            for para_start in paragraph_starts:
                if first_text.startswith(para_start):
                    block["__force_paragraph_break"] = True
                    break
```

## Testing Checklist

### Per-Chapter Tests

- [ ] All tables extract correctly
- [ ] Paragraph counts match specification
- [ ] No orphaned text fragments
- [ ] HTML renders correctly
- [ ] JSON structure validates
- [ ] Comparison with archived output

### Visual Inspection

1. **Open HTML file:** `data/html_output/chapter-*.html`
2. **Check tables:** Correct columns, rows, alignment
3. **Check paragraphs:** Proper breaks, no merging
4. **Check ordering:** Logical flow, no jumps
5. **Check formatting:** Headers, emphasis, spacing

### Automated Validation

```bash
# Validate JSON structure
python scripts/run_pipeline.py --stage validate

# Compare with archived output
diff data/html_output/chapter-two-player-character-races.html \
     archive/data_verification/verification/chapter-two-player-character-races.html
```

## Migration Status

### Completed
- ✅ Chapter 2 PDF-level processing migrated
- ✅ Chapter 3 PDF-level processing migrated
- ✅ Generic journal transformer
- ✅ Chapter 1 and Chapters 4–15 documentation stubs added

### Pending
- ⚠️  Chapter 2 HTML post-processing (disabled)
- ⚠️  Chapter 3 HTML post-processing (archived)
- 📝 Chapter 3 processing documentation
- 📝 Wanderer's Journal (Ch. 1–5) documentation stubs

### Future
- 🔮 Automated paragraph break detection
- 🔮 ML-based table extraction
- 🔮 PDF layout analysis improvements

## Contributing

When adding chapter-specific processing:

1. **Create documentation:** `docs/chapter_N_processing_spec.md`
2. **Create implementation:** `tools/pdf_pipeline/transformers/chapter_N_processing.py`
3. **Update this index:** Add entry above
4. **Add tests:** Visual and automated validation
5. **Document in RULES.md:** Reference processing guidelines

---

**Last Updated:** November 8, 2025  
**Chapters Documented:** 15/20 (Rules Book 1–15 complete; Wanderer's Journal pending)  
**Status:** 📝 In Progress



