These rules must be applied by the agent:
- [RULES] Watch this file RULES.md for changes and integrate them when thy occur
- [GOAL] The overall goal of the project is to extract the data from the source PDF, transform it into HTLM that is formatted suitably for inclusion into a Foundry VTT Compendium, then construct the Compedium and module that contains it. 
- [REQUIREMENTS] The primary requirement of the extraction and post-processing stages of the pipeline is to achieve as close to 100% extraction accurary as possible with regards to the source.  When extraction acuracy is limited due to source fragmentation rely on post-processing. Any filtering or obfuscation can be handled further in the pipeline.  Any loss of data or intentional erasure for any reason will fail validation.
- [README] Refer to README.md for details on the project
- [SPEC] Refer to SPEC.md for the specification of the domain for the project
- [PIPELINE] Refer to docs/pipeline_overview for details on the pipeline
- [SOURCE_MATERIAL] The source material for the project is available as a PDF document tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf in the project
- [SOURCE_MATERIAL_LICENSE] The source material is in the public domain
- [SOURCE_MATERIAL_FORMAT] The source material is in 2-column format and extraction should consider that when determining the order of content
- [SOURCE_MATERIAL_PAGE_NUMERS] The source material contains page numbers that should be omitted from the output except where needed as metadata.  They should not be visible.
- [SOURCE_MATERIAL_TABLES] There are tables embedded in the source PDF data.  Retain them and attempt to retain their placement.  Final placement will be adjusted during verificatino and iteration.
- [REFERENCE_AD&D_2E_DM_CORE] The AD&D 2E Dungeon Master's guide is available as the PDFs "Dungeon Master Guide.pdf", "Dungeon Master Guide Revised.pdf", and "Dungeon Master Guide Revised  (Premium Edition).pdf".  The materials are in the public domain.
- [REFERENCE_AD&D_2E_PLAYER_CORE] The AD&D 2E Player's guide is available as the PDFs "Player's Handbook.pdf", "Player's Handbook Revised.pdf", and "Player's Handbook Revised  (Premium Edition).pdf".  The materials are in the public domain.
- [PATHFINDER_2E_PLAYER_CORE] The Pathfinder 2E Player core rules are available as PDF document PZO12001E.pdf in the project
- [PATHFINDER_2E_GM_CORE] The Pathfinder 2E GM core rules are available as PDF document PZO12002E.pdf in the project
- [PATHFINDER_2E_MONSTER_CORE] The Pathfinder 2E Monster rules are available as PDF document PZO12003E.pdf in the project
- [PATHFINDER_2E_PLAYER_CORE_2] The Pathfinder 2E Player core 2 rules are available as PDF document PZO12004E.pdf in the project
- [FOUNDRY_API] The Foundry VTT API is available at https://foundryvtt.com/api/
- [FOUNDRY_VERSION] The Foundry version is 13
- [PF2E_SYSTEM_SOURCE] The source code for the Pathfinder 2E system for Foundry is available through the MCP server p2fe
- [SEGMENT_PROCESSING] TSegment-specific processing must be separated into dedicated python files following the pattern "chapter_#_processing.py"
- [SEGMENT_SUBPROCESSING] Segment-specific processing must itself be subdivided dedicated at the header level into python files following the pattern "chapter_#_{header_index}_{header}_subprocessing.py" where "{header_index}" is the numerical index of the header in the source and "{header}" is the header text
- [PIPELINE_OVERVIEW] Always keep docs/pipeline_overview.md up-to-date as the pipeline evolves
- [CHANGELOG] Keep a changelog for each chapter in docs/ using the naming pattern "chapter_#_changelog.md"
- [POSTPROCESSING] Postprocessing should only be used if direct PDF extraction and transformation is too complex.
- [POSTPROCESSING_SUBDIVISION] The Postprocessing stage must be separated into dedicated python files following the pattern "chapter_#_postprocessing.py" 
- [VIRTUALENV] This project is configure with a python virtual env, all executions should use the virtualenv at ./.venv
- [EXECUTION] Do not group commands. Execute commands separately with detailed logging to prevent halting or return code erasure.
- [VALIDATION] For each modification made to to the pipeline or any of the transformers, stages, processors, or postprocessors add a validation check to the validation stage the verifies the change to prevent regressions.
- [TOC] Every output HTML file should contain a table of contents at the top with links to the headers in the document.
- [DEPENDENCIES] Utilize any available python libraries necessary to simplify the task.  

[ORDER_OF_CONTENT] The source material sections should be processed in the following order:
1. chapter-one-ability-scores
1. chapter-two-player-character-races
1. chapter-three-player-character-classes
1. chapter-four-alignment
1. chapter-five-proficiencies
1. chapter-six-money-and-equipment
1. chapter-seven-magic
1. chapter-eight-experience
1. chapter-nine-combat
1. chapter-ten-treasure
1. chapter-eleven-encounters
1. chapter-twelve-npcs
1. chapter-thirteen-vision-and-light
1. chapter-fourteen-time-and-movement
1. chapter-fifteen-new-spells
1. chapter-one-the-world-of-athas
1. chapter-two-athasian-society
1. chapter-three-athasian-geography
1. chapter-four-atlas-of-the-tyr-region
1. chapter-five-monsters-of-athas
1. a-little-knowledge
1. a-flip-book-adventure
1. kluzd
1. wezer