# Chapter 4 Changelog — Alignment

## 2025-11-08

### Second Update: Severe Desperation Section
- Added paragraph splitting for "Severe Desperation" section into 3 paragraphs at:
  - "The madness created"
  - "Once a character has a"
- Fixed HTML export postprocessing to apply chapter-specific fixes to HTML content (not JSON content)
- Updated regression test `tests/regression/test_chapter4_paragraphs.py` to verify Severe Desperation paragraph structure
- Regenerated HTML output and verified all regression tests pass

### Initial Update: Intro and Half-giants Sections
- Added chapter-specific HTML postprocessing:
  - Split intro into 2 paragraphs at "As stated in the".
  - Split "Half-giants and Alignment" into 3 paragraphs at:
    - "A half-giant must choose"
    - "A half-giant's shifting alignment"
- Updated `docs/chapter_4_processing_spec.md` to document rules.
- Regenerated HTML output and executed regression tests.


