# Chapter 1 Processing Specification — Ability Scores

## Overview

This chapter uses the generic `journal` transformer with chapter-specific postprocessing for header levels.

## Processing

- Extraction: Standard structured extraction
- Transformation: `journal` renders headers, paragraphs, and tables
- Postprocessing: `chapter_1_postprocessing.py` applies header level styling

## Header Structure

### H1 Headers (Main Sections)
- Rolling Ability Scores (header-0)
- Rolling Player Character Ability Scores (header-1)
- Rolling Non-player Character Ability Scores (header-2)
- The Ability Scores (header-9)

### H2 Headers (Subsections)
- Optional Methods (header-3)
- Optional Method I: (header-4)
- Optional Method II: (header-5)
- Optional Method III: (header-6)
- Optional Method IV: (header-7)
- Optional Method V: (header-8)
- Intelligence: (header-10)
- Wisdom: (header-11)

## Postprocessing Details

The `apply_chapter_1_content_fixes` function:
- Applies `h2-header` CSS class to Optional Methods headers
- Adds `font-size: 0.9em` inline style to H2 header spans
- Removes Roman numerals from H2 headers (they only appear on H1)

## Validation

- Verify table column headers use table header styling, not document headers
- Confirm TOC anchors and back-to-top links [^] exist
- Verify H2 headers have no Roman numerals
- Verify H2 headers display at correct size (smaller than H1)

## Notes

- Two-column layout is handled by the renderer; no custom markers required


