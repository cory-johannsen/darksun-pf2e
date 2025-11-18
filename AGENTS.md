## 1. Requirements Format

- REQ-1: Requirement identifiers MUST follow the pattern "{prefix}-{ordinal}".
- REQ-2: Requirement prefixes MUST concisely indicate the concern domain.
- REQ-3: Requirement text MUST use RFC 2119 modal verbs.
- REQ-4: Requirements MUST be short, concise, and unambiguous.
- REQ-5: Bulleted lists without requirement identifiers MUST NOT be used.
- REQ-6: These meta‑requirements themselves MUST follow all requirements defined in this section.

## 2. LLM Agentic Behavior & Anti‑Patterns

- AGENT-1: Agents MUST NOT emit TODOs, placeholders, or incomplete code.
- AGENT-2: All generated code MUST be production quality and free of missing logic.
- AGENT-3: Agents MUST NOT make assumptions; all gaps MUST be surfaced explicitly.
- AGENT-4: Conflicts or ambiguities in requirements MUST be escalated and resolved prior to execution.
- AGENT-5: Agents MUST adhere to deterministic, spec‑driven behavior.
- AGENT-6: Agents MUST NOT use hard-coded data values in extraction or processing logic. All data must be extracted from the source PDF or derived programmatically. 
- AGENT-7: Agents MUST keeping working files (markdown, temporary scripts) in the subdiretory 'scratch/'.  The root directory of the proejct MUST be kept clean.

## 3. Software Engineering Best Practices

- SWENG-1: Systems MUST follow the Single Responsibility Principle.
- SWENG-2: Systems MUST apply Design by Contract, with explicit preconditions and postconditions.
- SWENG-3: Systems SHOULD use a Functional Core with an Imperative Shell.
- SWENG-4: State mutation MUST be isolated at the system boundaries.
- SWENG-5: Functions that exceed 200 lines and files that exceed 1000 lines MUST be decomposed up into smaller pieces.  
- SWENG-6: Test driven development MUST be used for all new code

## 4. Python Development Standards

- PY-1: Python development MUST use the Astral toolchain (uv, ruff, ty).
- PY-2: pip MUST NOT be used under any circumstances.
- PY-3: Pydantic MUST be used for data modeling and validation.
- PY-4: Abstract Base Classes (ABCs) MUST be used for interface and contract definition.
- PY-5: Test suites MUST use state‑of‑the‑art testing tools appropriate for Python and MUST enforce high coverage.
- PY-6: All python code must produce console logs tracing execution at the debug, info, warn, and error level; with debug the default.

# 5. Requirements
- REQUIREMENT-1: The overall goal of the project is to extract the data from the source PDF, transform it into HTLM that is formatted suitably for inclusion into a Foundry VTT Compendium, then construct the Compedium and module that contains it. 
- REQUIREMENTS-2: The primary requirement of the extraction and post-processing stages of the pipeline is to achieve as close to 100% extraction accurary as possible with regards to the source.  When extraction acuracy is limited due to source fragmentation rely on post-processing. Any filtering or obfuscation can be handled further in the pipeline.  Any loss of data or intentional erasure for any reason will fail validation.
- REQUIREMENTS-3: Refer to README.md for details on the project
- REQUIREMENTS-4: Refer to SPEC.md for the specification of the domain for the project
- REQUIREMENTS-5: Refer to docs/pipeline_overview.md for details on the pipeline

# 6. Source material
- SOURCE_MATERIAL-1: All source materials are stored in the subdirectory sources/
- SOURCE_MATERIAL-2: The source material for the project is available as a PDF document tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf in the project
- SOURCE_MATERIAL-3: The source material is in the public domain
- SOURCE_MATERIAL-4: The source material is in 2-column format and extraction should consider that when determining the order of content
- SOURCE_MATERIAL-5: The source material contains page numbers that should be omitted from the output except where needed as metadata.  They should not be visible.
- SOURCE_MATERIAL-6: There are tables embedded in the source PDF data.  Retain them and attempt to retain their placement.  Final placement will be adjusted during verificatino and iteration.
- SOURCE_MATERIAL-7: The AD&D 2E Dungeon Master's guide is available as the PDF "Dungeon Master Guide Revised  (Premium Edition).pdf".  The materials are in the public domain.
- SOURCE_MATERIAL-8: The AD&D 2E Player's guide is available as the PDFs "Player's Handbook Revised  (Premium Edition).pdf".  The materials are in the public domain.
- SOURCE_MATERIAL-9: The Pathfinder 2E Player core rules are available as PDF document PZO12001E.pdf in the project
- SOURCE_MATERIAL-10: The Pathfinder 2E GM core rules are available as PDF document PZO12002E.pdf in the project
- SOURCE_MATERIAL-11: The Pathfinder 2E Monster rules are available as PDF document PZO12003E.pdf in the project
- SOURCE_MATERIAL-12: The Pathfinder 2E Player core 2 rules are available as PDF document PZO12004E.pdf in the project
- SOURCE_MATERIAL-13: The Foundry VTT API is available at https://foundryvtt.com/api/
- SOURCE_MATERIAL-14: The Foundry version is 13
- SOURCE_MATERIAL-15: The source code for the Pathfinder 2E system for Foundry is available through the MCP server p2fe
- SOURCE_MATERIAL-16: The source material sections must be processed in the following order, and must retain this order in the output:
    1. chapter-one-ability-scores
    2. chapter-two-player-character-races
    3. chapter-three-player-character-classes
    4. chapter-four-alignment
    5. chapter-five-proficiencies
    6. chapter-six-money-and-equipment
    7. chapter-seven-magic
    8. chapter-eight-experience
    9. chapter-nine-combat
    10. chapter-ten-treasure
    11. chapter-eleven-encounters
    12. chapter-twelve-npcs
    13. chapter-thirteen-vision-and-light
    14. chapter-fourteen-time-and-movement
    15. chapter-fifteen-new-spells
    16. chapter-one-the-world-of-athas
    17. chapter-two-athasian-society
    18. chapter-three-athasian-geography
    19. chapter-four-atlas-of-the-tyr-region
    20. chapter-five-monsters-of-athas
    21. a-little-knowledge
    22. a-flip-book-adventure
    23. kluzd
    24. wezer

# 7. Processing
- PROCESSING-1: Segment-specific processing must be separated into dedicated python files following the pattern "chapter_#_processing.py"
- PROCESSING-2: Segment-specific processing must itself be subdivided dedicated at the header level into python files following the pattern "chapter_#_{header_index}_{header}_subprocessing.py" where "{header_index}" is the numerical index of the header in the source and "{header}" is the header text
- PROCESSING-3: All chapter-specific processing must be documented in "docs/chapter_#_processing_spec.md" including tables, paragraph breaks, and special handling
- PROCESSING-4: Always keep docs/pipeline_overview.md up-to-date as the pipeline evolves
- PROCESSING-5: Postprocessing should only be used if direct PDF extraction and transformation is too complex.
- PROCESSING-6: The Postprocessing stage must be separated into dedicated python files following the pattern "chapter_#_postprocessing.py" 

# 8. Execution
- EXECUTION-1: This project is configure with a python virtual env, all executions should use the virtualenv at ./.venv
- EXECUTION-2: Do not group commands. Execute commands separately with detailed logging to prevent halting or return code erasure.
- EXECUTION-3: The 'cd' command MUST NOT be used.  The 'cd' command MUST NOT be combined with other commands.

# 9. Validation
- VALIDATION-1: For each modification made to to the pipeline or any of the transformers, stages, processors, or postprocessors add a validation check to the validation stage the verifies the change to prevent regressions.
- VALIDATION-2: The regression test suite in tests/regression/ MUST be executed in full after ANY modification to the pipeline, transformers, stages, processors, or postprocessors. ALL regression tests must pass before the modification is considered complete. If any test fails, the modification must be rolled back or fixed immediately.
- VALIDATION-3: Execute regression tests using: `.venv/bin/python tests/regression/test_html_integrity.py data/html_output/chapter-two-player-character-races.html` after every pipeline run that modifies HTML output.
- VALIDATION-4: The pipeline includes OCR-based ordering validation that extracts text from the PDF, detects section ordering, and generates automated correction suggestions. This validates that extracted content follows the source PDF's reading order.
- VALIDATION-5: OCR validation outputs corrections to data/ocr_ordering_corrections.json. Review and apply these corrections to manifest and spec files to improve extraction accuracy.
- VALIDATION-6: OCR validation requires Tesseract OCR installed on the system and Python packages: pytesseract, pdf2image, Pillow. If unavailable, the stage gracefully skips with a warning.

# 10. HTML
- HTML-1: Every output HTML file MUST contain a table of contents at the top with links to the headers in the document.
- HTML-2: When creating the table of contents, subheaders (H2) MUST be indented and displayed in a smaller font. This also applies to H3 and H3 subheaders, which MUST be indented beneath the subheaders.
- HTML-3: The output must contain a top level table of contents that contains all the converted chapters, in order. This MUST be stored in a file named "table_of_contents.{format}" where format is the output format (html, json, etc).  Every chapter must have a link back to the top level table of contents.
- HTML-4: The output html MUST contain an index.html page that redirects to the table of contents.
- HTML-5: All paths in HTML files (href, src, etc.) MUST be relative paths, never absolute filesystem paths or file:// URLs. This ensures portability across different systems and deployment environments. The relative path verification test in tests/regression/test_relative_paths.py must pass for all HTML output files.
- HTML-6: Each chapter HTML file MUST be rendered as a single continuous page without page break sections. Do not wrap content in <section> tags with data-page attributes. 
- HTML-7: Sentences that are merged to remove line breaks MUST be properly joined.  For example, "in- ner" must be "inner", "specializa- tion" must be "specialization".
- HTML-8: The user will specify header sizes using HTML notation when providing feedback: H1; H2; H3; H4; with H1 the largest and H4 the smallest. H4 is larger than normal text.  H1 > H2 > H3 > H4 > Normal text. 
- HTML-9: Every header MUST contain an appended inline link that returns to the top of the document.  The link MUST look like [^]
- HTML-10: Every header MUST include a prepended roman numeral that identifies the header section.  For instance, the header "Warrior Classes" MUST become "I. Warrior Classes".  Only assign numerals to headers (H1), not subheaders or tables (H2, H3, H4).  The user will reference these numerals when providing feedback.
- HTML-11: Table header values MUST use a distinct style that is not one of the header styles mentioned in HEADER_FORMAT. Table header values are NOT document headers.
- HTML-12: The source material contains text in italics.  This MUST be preserved such that the resulting HTML text is in italics. Text in italics MUST preserve whitespace required to form grammatically correct words and sentences.
- HTML-13: The source material contain text in bold face.  This MUST be preserved such that the resulting HTML is in bold face. Text in bold face MUST preserve whitespace required to form grammatically correct words and sentences.

# 11. Communication
- COMMUNICATION-1: Use emojis strategically to highlight information types:
  - 🏆 for achievements and records
  - ✅ for completed items
  - ⏳ for in-progress work
  - ❌ for problems
  - 📊 for metrics and data
  - 🎯 for goals and targets
  - 💡 for insights and tips
  - ⚠️ for warnings
  - 🚀 for next actions
- COMMUNICATION-2: Create visual celebrations for milestones (ASCII art, banners)
- COMMUNICATION-3: Provide quantitative metrics with before/after comparisons
- COMMUNICATION-4: Use tables, boxes, and clear hierarchies for readability
- COMMUNICATION-5: Be genuinely enthusiastic about good work
- COMMUNICATION-6: Balance celebration with actionable next steps
- COMMUNICATION-7: Track progress visually (progress bars, checklists)
- COMMUNICATION-8: Make reports feel rewarding to read
- COMMUNICATION-9: Don't be afraid to use exclamation marks for impact!