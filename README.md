# darksun-p2fe

A pipeline to building a Pathfinder 2E Foundry VTT compendia that implement the Dark Sun universe.

## Getting Started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Pipeline

1. **Extract source PDF**
   ```bash
   python scripts/extract_pdf.py --format structured
   ```

2. **Transform into PF2E datasets**
   ```bash
   python scripts/transform_data.py
   ```

3. **Preview extraction results (optional)**
   ```bash
   python scripts/verify_extraction.py --slug chapter-one-the-world-of-athas
   ```

4. **Build Foundry compendia**
   ```bash
   python scripts/build_compendia.py
   ```

5. **Run validation**
   ```bash
   python scripts/validate_data.py
   ```

See `docs/pipeline_overview.md` for full details, mapping guidelines, and QA steps.

## Documentation

### Core Specs
- `SPEC.md` - Pipeline domain model and architecture
- `RULES.md` - Project rules and processing guidelines  
- `docs/pipeline_overview.md` - Complete pipeline guide

### Chapter-Specific Processing
- `docs/chapter_processing_index.md` - Index of all chapter processing
- `docs/chapter_2_processing_spec.md` - Chapter 2 (Races) detailed spec

### Status & Summaries
- `PIPELINE_IMPLEMENTATION_COMPLETE.md` - Implementation summary
- `HTML_EXPORT_COMPLETE.md` - HTML export documentation
- `HTML_POST_PROCESSING_COMPLETE.md` - HTML post-processing migration

## Foundry VTT Module

- Manifest: `module.json`
- Minimum Foundry version: 13 (PF2E system 5.0.0 or newer).
- Compendium packs shipped in `packs/` (currently: `Dark Sun Ancestries`, `Dark Sun Rules`).

To install manually, copy the repository into your Foundry `Data/modules/` folder (or host the repo and supply the manifest URL). Enable the module in a Pathfinder 2E world to access the compendium content.
