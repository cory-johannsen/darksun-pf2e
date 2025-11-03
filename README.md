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

## Foundry VTT Module

- Manifest: `module.json`
- Minimum Foundry version: 13 (PF2E system 5.0.0 or newer).
- Compendium packs shipped in `packs/` (currently: `Dark Sun Ancestries`, `Dark Sun Rules`).

To install manually, copy the repository into your Foundry `Data/modules/` folder (or host the repo and supply the manifest URL). Enable the module in a Pathfinder 2E world to access the compendium content.
