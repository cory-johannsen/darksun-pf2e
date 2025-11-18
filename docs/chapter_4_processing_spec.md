# Chapter 4 Processing Specification — Alignment

## Overview

Chapter-specific HTML postprocessing is applied to correct paragraph boundaries derived from the 2‑column PDF extraction:

- Intro section: exactly 2 paragraphs, break at the phrase "As stated in the".
- Half-giants and Alignment: exactly 3 paragraphs, breaks at:
  - "A half-giant must choose"
  - "A half-giant's shifting alignment"
- Severe Desperation: exactly 3 paragraphs, breaks at:
  - "The madness created"
  - "Once a character has a"

Additionally, the headers "Alignment in Desperate Situations" and "(Optional Rule)" are merged into a single header "Alignment in Desperate Situations (Optional Rule)", with subsequent headers renumbered accordingly.

These adjustments are implemented in `tools/pdf_pipeline/postprocessors/chapter_4_postprocessing.py` and wired via the HTML export stage for slug `chapter-four-alignment`.

## Header Merging

The PDF extraction treats "Alignment in Desperate Situations" and "(Optional Rule)" as two separate headers due to different font sizes (14.88pt vs 8.88pt). These appear on the same line in the source PDF and should be combined into a single header.

The postprocessing:
1. Merges the two headers into one
2. Renumbers all subsequent headers (decrements their index by 1)
3. Updates roman numerals to match the new header indices
4. Updates TOC links to reflect the new header IDs

## Validation

- Ensure headers have roman numerals and [^] back-to-top links.
- Confirm no `<section data-page>` wrappers are present.
- Verify Chapter 4 intro has 2 paragraphs, "Half-giants and Alignment" has 3 paragraphs, and "Severe Desperation" has 3 paragraphs (see regression test `tests/regression/test_chapter4_paragraphs.py`).
- Verify "Alignment in Desperate Situations (Optional Rule)" is a single merged header.
- Verify no "(Optional Rule)" header exists separately in the TOC.

