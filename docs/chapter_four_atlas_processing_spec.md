# Chapter Four: Atlas of the Tyr Region Processing Specification

## Overview

Chapter Four: Atlas of the Tyr Region contains descriptions of various locations in the Tyr Region, including cities, villages, oases, islands, ruins, and landmarks. The PDF extraction merges paragraphs due to the 2-column layout, requiring HTML postprocessing to split them at the correct locations.

## Table of Contents Generation

**Implementation:** `tools/pdf_pipeline/postprocessors/html_export.py` (lines 191-206)

After all postprocessing is complete, a table of contents is generated using the `generate_table_of_contents()` function. This TOC includes:
- **H1 headers** (Cities, Villages, Oases, etc.) as main TOC entries
- **H2 headers** (city and village names) as indented subheaders with the `toc-subheader` class

The TOC generation process:
1. Extracts body content from the fully postprocessed HTML
2. Removes any outdated TOC from the journal JSON content
3. Generates a fresh TOC that includes all H2 headers
4. Inserts the new TOC at the beginning of the body

This ensures the TOC reflects all header conversions (from `<p>` to `<h2>`) performed during postprocessing.

## Paragraph Break Requirements

### Main Introduction Section
- **Expected Paragraphs:** 5
- **Break Points:**
  - "That won't"
  - "Despite these"
  - "In honor of"
  - "The Tyr region"

### Cities Section
- **Expected Paragraphs:** 2
- **Break Points:**
  - "Of course,"

### Balic Section
- **Expected Paragraphs:** 7
- **Break Points:**
  - "On the rare"
  - "Andropinis lives"
  - "Balic's templars"
  - "The nobles of"
  - "Balic's Merchant"
  - "Balic's secluded"

### Draj Section
- **Expected Paragraphs:** 9 (8 breaks + 1 initial paragraph = 9 total)
- **Break Points:**
  - "Be that as"
  - "No one seems"
  - "This last claim"
  - "Because Draj"
  - "Nevertheless,"
  - "Captives are"
  - "On a day"
  - "Despite its warlike"

### Gulg Section
- **Expected Paragraphs:** 8
- **Break Points:**
  - "Lalali-Puy is perhaps"
  - "Gulg is not"
  - "While most of"
  - "Her templars,"
  - "In Gulg,"
  - "Like all property"
  - "The warriors of"

### Nibenay Section
- **Expected Paragraphs:** 7
- **Break Points:**
  - "The Shadow King lives"
  - "Nibenay's templars are"
  - "This is completely"
  - "Nibenay sits"
  - "Nibenay's merchant trade"
  - "The core of"

### Raam Section
- **Expected Paragraphs:** 6
- **Break Points:**
  - "Abalach-Re professes"
  - "This is one of"
  - "As a consequence"
  - "Of course,"
  - "The only thing"

### Tyr Section
- **Expected Paragraphs:** 8
- **Break Points:**
  - "If Kalak's"
  - "The Tyrant of Tyr"
  - "Of late,"
  - "Kalak has also"
  - "To make matters"
  - "Can it be"
  - "When the final battle"

### Urik Section
- **Expected Paragraphs:** 9
- **Special Formatting:** First 3 paragraphs are a block quote (indented and italicized)
- **Break Points:**
  - "I am Hamanu, King" (blockquote start)
  - "The Great Spirits" (blockquote)
  - "I am Hamanu of" (blockquote)
  - "As you"
  - "Hamanu's palace"
  - "One of the most"
  - "Urik's economy"
  - "As a final note"

## H2 Header Conversions - Villages

The following village names are converted from styled `<p>` tags to `<h2>` headers:
- Altaruk (3 paragraphs, breaks at "This contingent", "Despite its")
- Makla (1 paragraph)
- North and South Ledopolus (2 paragraphs, break at "Occassionally,")
- Salt View (1 paragraph)
- Ogo (2 paragraphs, break at "Ogo is unique")
- Walis (2 paragraphs, break at "The reason for all")

## H2 Header Conversions - Oases

The following oases names are converted from styled `<p>` tags to `<h2>` headers:
- Bitter Well (2 paragraphs, break at "I would advise")
- Black Waters (1 paragraph)
- Lake Pit (2 paragraphs, break at "In either case")
- Lake of Golden Dreams (1 paragraph)
- Silver Spring (1 paragraph)
- Grak's Pool (1 paragraph)
- Lost Oasis (1 paragraph)
- The Mud Palace (2 paragraphs, break at "At the center")

### Oases Section (Main Intro)
- **Expected Paragraphs:** 2
- **Break Points:**
  - "The largest and most reliable"

## H2 Header Conversions - Islands

The following island names are converted from styled `<p>` tags to `<h2>` headers:
- Ledo (1 paragraph)
- Dragon's Palate (3 paragraphs, breaks at "The giants", "I should warn")
- Siren's Song (2 paragraphs, break at "Some claim")
- Waverly (2 paragraphs, break at "According to")
- Lake Island (2 paragraphs, break at "In the crater")

### Islands Section (Main Intro)
- **Expected Paragraphs:** 2
- **Break Points:**
  - "I have learned"

## H2 Header Conversions - Landmarks

The following landmark names are converted from styled `<p>` tags to `<h2>` headers:
- Dragon's Bowl (2 paragraphs, break at "Perhaps this")
- Mekillot Mountains (2 paragraphs, break at "It is well")
- Estuary of the Forked Tongue (1 paragraph)
- Dragon's Crown Mountain (2 paragraphs, break at "If you make")

## H2 Header Conversions - Ruins

The following ruins names are converted from styled `<p>` tags to `<h2>` headers:
- Bleak Tower (1 paragraph)
- Arkhold (2 paragraphs, break at "As for the castle")
- Kalidnay (1 paragraph)
- Bodach (3 paragraphs, breaks at "Unfortunately", "I have talked")
- Giustenal (3 paragraphs, breaks at "Giustenal appears", "I have never")
- Yaramuke (1 paragraph)

## Implementation

### Location
- **Postprocessor:** `tools/pdf_pipeline/postprocessors/chapter_four_atlas_postprocessing.py`
- **Wired into:** `tools/pdf_pipeline/postprocessors/html_export.py`
- **Test:** `tests/regression/test_chapter_four_atlas_paragraphs.py`

### Processing Strategy

1. **Locate Section Boundaries:** Use header IDs to identify section boundaries (e.g., `header-0-cities`, `header-1-balic`)
2. **Extract Content:** Extract the paragraph content between section boundaries
3. **Split at Markers:** Split the content at specified text markers
4. **Wrap Paragraphs:** Wrap each split segment in `<p>` tags
5. **Replace Content:** Replace the original merged content with the properly split paragraphs

### Special Considerations

- HTML entity normalization (e.g., `&#x27;` to `'`) is required for proper matching
- The postprocessing runs AFTER cleanup to ensure all content is in its final form
- Each section has a different number of expected paragraphs based on the source material

## Validation

The regression test (`test_chapter_four_atlas_paragraphs.py`) verifies:
1. Correct number of paragraphs in each section
2. Each break point appears at the START of a paragraph
3. No content is lost during splitting
4. Proper paragraph wrapping with `<p>` tags

## Notes

- This chapter contains extensive geographic descriptions that span multiple pages in the source PDF
- The 2-column layout causes natural paragraph breaks to be lost during extraction
- Postprocessing is the most effective approach for restoring proper paragraph structure
- Additional cities and sections (Nibenay, Raam, Tyr, Urik, etc.) may require similar treatment in future updates

