# Dark Sun Conversion Pipeline

This repository contains a formal pipeline framework that ingests the original Dark Sun boxed set PDF and emits Foundry VTT-ready Pathfinder 2E compendia.

## Architecture Overview

The pipeline implements a formal domain model (defined in SPEC.md) with a hierarchical class structure:

```
Pipeline → Transformer → TransformerStage → Processor/PostProcessor
```

### Core Components

- **Pipeline**: Top-level orchestrator that executes transformers in sequence
- **Transformer**: Groups related processing stages for a major transformation step
- **TransformerStage**: Bundles a processor, optional postprocessor, and their specifications
- **Processor**: Performs one isolated unit of work (extraction, transformation, validation, etc.)
- **PostProcessor**: Applies secondary processing to processor output

### Directory Layout

```
tools/pdf_pipeline/
  - domain.py           # Core domain models (Pipeline, Transformer, Stage, etc.)
  - base.py             # Abstract base classes for Processor/PostProcessor
  - loader.py           # Dynamic module loading for processors
  - pipeline.py         # PipelineEngine orchestrator
  - stages/             # Stage implementations
    - extract.py        # PDF extraction processors
    - transform.py      # Data transformation processors  
    - validate.py       # Validation processors
    - rules_conversion.py # AD&D 2E → PF2E conversion (stub)
    - foundry_build.py  # Foundry compendium builders
  - transformers/       # Legacy transformer functions (ancestries, journal)
  - validators.py       # Validation helpers (extended with framework checks)

data/
  - pipeline_config.json       # Main pipeline configuration
  - mappings/                  # Stage specifications and mapping data
    - extract_stage_spec.json
    - transform_stage_spec.json
    - validate_stage_spec.json
    - rules_conversion_stage_spec.json
    - foundry_build_stage_spec.json
    - section_profiles.json    # Section-specific transformation profiles
    - ancestries.json          # Ancestry mapping data
  - raw/                       # Raw extraction output
  - raw_structured/sections/   # Structured PDF sections
  - processed/                 # Transformed data
    - journals/                # HTML journal entries
    - ancestries.json          # Ancestry data
  - pf2e_converted/           # PF2E-converted data (future)

packs/                        # Generated Foundry compendia
  - dark-sun-ancestries.db
  - dark-sun-rules.db

scripts/
  - run_pipeline.py           # NEW: Unified CLI for pipeline execution
  - extract_pdf.py            # Legacy: Direct extraction
  - transform_data.py         # Legacy: Direct transformation
  - build_compendia.py        # Legacy: Direct compendium build
  - validate_data.py          # Legacy: Direct validation
```

## Pipeline Stages

The pipeline consists of 6 major stages, each implemented as a Transformer:

### 0. Source Fetch Stage
Downloads required source materials from archive.org and verifies local sources.

**Processors:**
- `SourceFetchProcessor`: Downloads AD&D 2E PDFs and EPUBs from archive.org
- `PF2ESourceFetchProcessor`: Verifies PF2E source PDFs are present locally

**Features:**
- Parallel downloads (auto-detects optimal thread count based on CPU cores)
- Downloads both PDF and EPUB formats for comparison
- Skips already-downloaded files
- Automatic ZIP extraction with marker files to prevent re-downloading
- Thread-safe parallel downloads with progress tracking

**Configuration:**
- `sources_dir`: Directory to store downloaded files (default: `sources`)
- `archive_url`: Archive.org collection URL
- `max_workers`: Number of parallel download threads (default: auto-detect)

**Output:** Source PDFs and EPUBs in `sources/`

### 1. Extract Stage
Extracts data from the source PDF.

**Processors:**
- `ManifestProcessor`: Generates table of contents manifest
- `SectionExtractionProcessor`: Extracts sections with layout awareness

**PostProcessors:**
- `TableDetectionPostProcessor`: Detects and structures tables

**Output:** Structured JSON sections in `data/raw_structured/sections/`

### 2. Transform Stage
Transforms raw data to processed HTML and structured data.

**Processors:**
- `JournalTransformProcessor`: Converts sections to HTML with TOC
- `AncestryTransformProcessor`: Extracts ancestry data from race chapters

**Output:** 
- HTML journals in `data/processed/journals/`
- Ancestry data in `data/processed/ancestries.json`

### 3. Knowledge Base Build Stage
Builds knowledge bases for AD&D 2E and PF2E rules.

**Processors:**
- `ADnDRuleExtractor`: Extracts rules from AD&D 2E PDF sourcebooks (DMG, PHB)
- `PF2ECacheInitializer`: Initializes PF2E rule cache by querying MCP server

**Output:** 
- AD&D 2E knowledge base in `data/knowledge_base/adnd_2e/`
- PF2E rule cache in `data/knowledge_base/pf2e_cache/`
- Index file in `data/knowledge_base/index.json`

### 4. Validate Stage
Validates data structure and content quality.

**Processors:**
- `StructuralValidationProcessor`: Validates JSON schema and structure
- `ContentValidationProcessor`: Validates content quality and completeness
- `OCRValidationProcessor`: Uses OCR to verify content ordering and generates correction suggestions

**Output:** Validation reports with errors, warnings, and ordering corrections

### 5. Rules Conversion Stage
Converts AD&D 2E rules to Pathfinder 2E equivalents using semantic mapping.

**Processors:**
- `ADnDToPF2EProcessor`: Converts game mechanics using knowledge bases and context analysis

**PostProcessors:**
- `RulesValidationPostProcessor`: Validates PF2E compliance

**Key Features:**
- Semantic mapping with confidence scores
- Dark Sun context awareness
- Flavor text preservation
- Intelligent fallback strategies

**Output:** PF2E-compatible data in `data/pf2e_converted/`

### 6. Foundry Build Stage
Generates Foundry VTT module and compendia.

**Processors:**
- `CompendiumBuildProcessor`: Builds .db compendium files
- `ModuleMetadataProcessor`: Generates module.json

**Output:**
- Compendium databases in `packs/`
- Module metadata in `module.json`

## Knowledge Base System

The pipeline now includes a comprehensive knowledge base system for AD&D 2E to PF2E conversion:

### Architecture Components

**1. AD&D 2E Knowledge Base**
- Extracts rules from sourcebooks (DMG, PHB)
- Structures data using Pydantic models
- Stores in queryable repository
- Supports: ability scores, saves, THAC0, AC, spells, classes

**2. PF2E Rule Integration**
- Queries PF2E rules via MCP server
- Caches results locally for performance
- Supports ability scores, saves, skills, actions, spells

**3. Semantic Mapping Engine**
- Context-aware rule translation
- Confidence scoring (high/medium/low/unmappable)
- Dark Sun setting considerations
- Flavor text preservation

**4. Rule Translators**
- AbilityScoreTranslator: Converts ability scores and modifiers
- CombatMechanicTranslator: Converts THAC0, AC, combat rules
- SpellTranslator: Converts spells with defiling magic support

**5. Context Analyzer**
- Dark Sun theme detection
- Setting-specific modifiers
- Metal/water scarcity handling
- Psionic integration

### Configuration Files

- `data/mappings/sourcebook_registry.json`: AD&D sourcebook registry
- `data/mappings/knowledge_base_spec.json`: Extraction specifications
- `data/mappings/rule_mappings/abilities.json`: Ability score conversions
- `data/mappings/rule_mappings/combat.json`: Combat mechanic conversions
- `data/mappings/rule_mappings/spells.json`: Spell system conversions
- `data/mappings/rule_mappings/classes.json`: Class feature conversions

## Usage

### Running the Complete Pipeline

Use the new unified CLI to run all stages:

```bash
source .venv/bin/activate
python scripts/run_pipeline.py --config data/pipeline_config.json
```

### Parallel Execution

The pipeline supports parallel execution to speed up CPU-intensive tasks. Parallel execution is enabled by default in the configuration.

#### Enabling/Disabling Parallel Execution

```bash
# Enable parallel execution (overrides config)
python scripts/run_pipeline.py --parallel

# Disable parallel execution (overrides config)
python scripts/run_pipeline.py --no-parallel

# Set maximum workers for all stages
python scripts/run_pipeline.py --max-workers 8
```

#### Configuration

Parallel execution can be configured at two levels:

1. **Global level** in `data/pipeline_config.json`:
```json
{
  "parallel": true,
  ...
}
```

2. **Per-stage level** in processor config:
```json
{
  "processor_spec": {
    "config": {
      "parallel": true,
      "max_workers": 4,
      "chunksize": 1
    }
  }
}
```

Stage-level configuration takes precedence over global configuration.

#### What Gets Parallelized

The following stages support parallel execution:

- **Extract Stage**: PDF section extraction runs in parallel (per section)
- **Borderless Table Detection**: Table detection runs in parallel (per file)
- **Transform Stage**: Journal transformation runs in parallel (per section)
- **HTML Export**: HTML generation runs in parallel (per file)
- **Validation Stages**: File validation runs in parallel (per file)
- **OCR Validation**: OCR processing runs in parallel (per page)

#### Performance Considerations

- Default: `max_workers = min(4, cpu_count)`
- Parallel execution uses process-based parallelism (not threads)
- MacOS-safe spawn context is used for compatibility
- Memory usage increases with worker count
- For OCR, consider `ocr_batch_size` to limit memory usage

#### Determinism

Parallel execution produces identical outputs to sequential execution:
- File names and contents are unchanged
- Output arrays are sorted for consistency
- Error and warning aggregation is deterministic

### Running Specific Stages

Execute a single stage:

```bash
# Fetch sources only
python scripts/run_pipeline.py --stage source_fetch

# Extract only
python scripts/run_pipeline.py --stage extract

# Transform only
python scripts/run_pipeline.py --stage transform

# Validate only
python scripts/run_pipeline.py --stage validate
```

### Resuming from a Stage

Resume pipeline execution from a specific stage:

```bash
python scripts/run_pipeline.py --from-stage transform
```

### Dry Run Validation

Validate configuration without executing:

```bash
python scripts/run_pipeline.py --dry-run
```

### Verbose Logging

Enable debug-level logging:

```bash
python scripts/run_pipeline.py --verbose
```

### Saving Checkpoints

Save execution checkpoints:

```bash
python scripts/run_pipeline.py --checkpoint my-checkpoint-id
```

## HTML Output for Review

The transform stage automatically generates standalone HTML files for manual review and feedback:

**Location:** `data/html_output/`

### Features
- ✅ Styled HTML with Dark Sun theme
- ✅ Table of Contents with anchor links  
- ✅ Responsive design (mobile-friendly)
- ✅ Print-ready formatting
- ✅ Self-contained (no external dependencies)

### Usage
```bash
# Generate HTML files
python scripts/run_pipeline.py --stage transform

# Open in browser
open data/html_output/chapter-one-ability-scores.html
```

**See:** `HTML_EXPORT_COMPLETE.md` for full documentation

## Legacy Workflow (Still Supported)

The original scripts remain functional for backward compatibility:

1. **Extract the PDF**
   ```bash
   python scripts/extract_pdf.py --format structured
   ```

2. **Transform to PF2E-friendly JSON**
   ```bash
   python scripts/transform_data.py
   ```

3. **Build Foundry Compendia**
   ```bash
   python scripts/build_compendia.py
   ```

4. **Run QA Checks**
   ```bash
   python scripts/validate_data.py
   ```

## Usage Examples

### Running the Complete Pipeline

```bash
# Run all stages with verbose output
python scripts/run_pipeline.py --verbose

# Dry run to see what would execute
python scripts/run_pipeline.py --dry-run
```

### Running Individual Stages

```bash
# Run only the extract stage
python scripts/run_pipeline.py --stage extract --verbose

# Run only the transform stage
python scripts/run_pipeline.py --stage transform --verbose

# Run only the validate stage
python scripts/run_pipeline.py --stage validate --verbose

# Run only the Foundry build stage
python scripts/run_pipeline.py --stage foundry_build --verbose
```

### Testing Individual Stages

```bash
# Test extract stage
python scripts/test_extract.py

# Test transform stage
python scripts/test_transform.py

# Test validate stage
python scripts/test_validate.py

# Test Foundry build stage
python scripts/test_foundry_build.py

# Test complete pipeline
python scripts/test_pipeline_full.py
```

### Checkpointing and Resumption

```bash
# Enable checkpointing (future feature)
python scripts/run_pipeline.py --checkpoint

# Resume from a specific stage (future feature)
python scripts/run_pipeline.py --resume-from transform
```

## Extending the Pipeline

### Adding New Processors

1. Create a new processor class inheriting from `BaseProcessor`:

```python
from tools.pdf_pipeline.base import BaseProcessor
from tools.pdf_pipeline.domain import ProcessorInput, ProcessorOutput, ExecutionContext

class MyCustomProcessor(BaseProcessor):
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        # Your processing logic
        result = do_something(input_data.data)
        
        context.items_processed += 1
        
        return ProcessorOutput(
            data=result,
            metadata={"custom_info": "value"}
        )
```

2. Add the processor to a stage in `data/pipeline_config.json`:

```json
{
  "name": "my_stage",
  "processor_spec": {
    "name": "MyCustomProcessor",
    "module_path": "path.to.module",
    "class_name": "MyCustomProcessor",
    "config": {
      "custom_param": "value"
    }
  }
}
```

### Adding Chapter-Specific Processing

Per RULES.md, segment-specific processing should be in dedicated files:

1. Create `tools/pdf_pipeline/transformers/chapter_N_processing.py`
2. Implement processor classes for that chapter
3. Configure dynamic loading in the stage specification

### Configuration

Pipeline behavior is controlled by:

- `data/pipeline_config.json`: Main pipeline configuration
- `data/mappings/*_stage_spec.json`: Stage-specific specifications
- `data/mappings/section_profiles.json`: Section transformation profiles
- `data/mappings/ancestries.json`: Domain-specific mapping data

## Validation

Per RULES.md line 30, the pipeline includes comprehensive validation:

### Framework Validation

- `validate_pipeline_config()`: Validates pipeline configuration schema
- `validate_processor_loading()`: Validates all processors can be loaded
- `validate_stage_compatibility()`: Validates stage I/O compatibility
- `validate_framework_integrity()`: Validates framework module structure

### Data Validation

- `validate_ancestries()`: Validates ancestry data structure and content
- `validate_journals()`: Validates journal content and formatting
- Chapter-specific validators (e.g., `_validate_chapter_3()`)

### OCR-Based Ordering Validation

The OCR validation stage uses optical character recognition to verify that content ordering is correct:

- **Process:** Extracts text from PDF via OCR and detects section headers in reading order
- **Comparison:** Matches OCR-detected sections with extracted structured data
- **Detection:** Identifies ordering mismatches, missing sections, and unexpected sections
- **Correction:** Generates automated correction suggestions for manifest and spec files
- **Output:** `data/ocr_ordering_corrections.json` with actionable fixes

**Features:**
- ✅ Caching of OCR results for performance
- ✅ Configurable page sampling for quick validation
- ✅ Fuzzy matching for section title recognition
- ✅ Severity classification (error vs. warning)
- ✅ Automated correction generation

**Requirements:**
- Tesseract OCR installed on system (`brew install tesseract` on macOS)
- Python packages: `pytesseract`, `pdf2image`, `Pillow`

If OCR libraries are not available, the stage gracefully skips with a warning.

Run validation:

```bash
python scripts/validate_data.py
```

Or use the validate stage:

```bash
python scripts/run_pipeline.py --stage validate
```

## Manual Review Guidelines

- Spot-check extracted `data/raw_structured/sections/*.json` for clean text
- Review `data/processed/*.json` for anomalies
- Import `packs/*.db` into Foundry for end-to-end verification
- Check validation reports for warnings
- Verify tables are correctly structured
- Ensure HTML formatting is correct in journals

## Migration Notes

This framework implements the evolved architecture defined in SPEC.md and RULES.md:

- **Domain Model**: Full class hierarchy as specified
- **Specifications**: Pydantic models loaded from JSON
- **Dynamic Loading**: Processors loaded via importlib
- **5 Stages**: Extract → Transform → Validate → Rules Conversion → Foundry Build
- **Backward Compatible**: Legacy scripts still functional

The framework is designed for iteration and extensibility, allowing the pipeline to evolve as requirements change.

## Troubleshooting

### Common Issues

**Import Errors:**
- Ensure virtual environment is activated: `source .venv/bin/activate`
- Verify all dependencies installed: `pip install -r requirements.txt`

**Missing Files:**
- Extract stage must run before transform
- Transform stage must run before validate
- Validate stage must run before Foundry build

**Pipeline Fails Silently:**
- Run with `--verbose` flag to see detailed logging
- Check error messages in console output

**Configuration Errors:**
- Validate pipeline config: `python scripts/run_pipeline.py --dry-run`
- Check JSON syntax in spec files
- Verify module paths in processor specs

### Performance Tips

- Extract stage is slowest (~15 seconds) due to PDF processing
- Use `--stage` flag to run only needed stages during development
- Checkpoint frequently for long pipelines (once implemented)

### Getting Help

- Review `PIPELINE_IMPLEMENTATION_COMPLETE.md` for implementation details
- Check `SPEC.md` for domain model specifications
- Check `RULES.md` for project requirements
- Examine test scripts in `scripts/` for usage examples

---

**Last Updated:** 2025-11-08  
**Pipeline Version:** 1.0.0  
**Implementation Status:** ✅ Production Ready

## Recent Changes

- 2025-11-18: **Source Fetch Stage** added as Stage 0 of the pipeline. Automatically downloads AD&D 2E source materials from archive.org with parallel downloads (auto-detects optimal thread count based on CPU cores). Downloads both PDF and EPUB formats for comparison. Includes ZIP extraction with marker files to prevent re-downloading. Verifies PF2E source materials are present. Configure with `--stage source_fetch` or run as part of the full pipeline.

- 2025-11-08: Chapter 3 "Player Character Classes" locked from transformation by adding its slug to `skip_slugs` in `data/mappings/section_profiles.json` per CONTENT_LOCK policy. Existing output remains unchanged.

- 2025-11-08: Chapter 2 "Player Character Races" locked from transformation by adding its slug to `skip_slugs` in `data/mappings/section_profiles.json` per CONTENT_LOCK policy. Existing output remains unchanged.

- 2025-11-08: Chapter 1 "Ability Scores" locked from transformation by adding its slug to `skip_slugs` in `data/mappings/section_profiles.json` per CONTENT_LOCK policy. Existing output remains unchanged.

- 2025-11-08: Chapter 3 “Multi-Class Combinations” intro paragraph merge updated to concatenate all text blocks between the section subheader and the first race header, ensuring the full paragraph is preserved without hard-coded phrases. See `docs/chapter_3_processing_spec.md` and `docs/chapter_3_changelog.md`.
- 2025-11-08: Chapter 2 tables updated to prevent table column labels from rendering as document headers. The transform stage now clears header label lines within the “Starting Age” and “Aging Effects” sections after table reconstruction. See `docs/chapter_2_processing_spec.md` and `docs/chapter_2_changelog.md`.
- 2025-11-07: Chapter 3 multi-class section updated to preserve the introductory paragraph and context. Aggressive clearing removed; only combination text fragments are cleared. Race tables are reconstructed programmatically from extracted combinations. See `docs/chapter_3_processing_spec.md` and `docs/chapter_3_changelog.md`.
