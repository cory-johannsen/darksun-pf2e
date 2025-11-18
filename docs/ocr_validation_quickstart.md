# OCR Validation Quick Start Guide

## Prerequisites

### 1. Install System Dependencies

**macOS:**
```bash
brew install tesseract poppler
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

### 2. Install Python Packages

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Running OCR Validation

### Full Pipeline with Validation

```bash
source .venv/bin/activate
python scripts/run_pipeline.py --stage validate --verbose
```

The OCR validation will run as part of the validate stage automatically.

### View Results

```bash
# Check if corrections were generated
cat data/ocr_ordering_corrections.json | jq .

# View cache status
ls -lh data/.ocr_cache/
```

## Understanding the Output

### Validation Report

The OCR validation produces:

1. **Console Output:**
   ```
   INFO - Processing stage: ocr_ordering_validation
   INFO - OCR validation: Found 24 sections via OCR
   WARNING - Ordering issue: Section 'chapter-X' appears out of order
   INFO - Generated 3 ordering corrections: data/ocr_ordering_corrections.json
   ```

2. **Corrections File:** `data/ocr_ordering_corrections.json`
   ```json
   {
     "correction_count": 2,
     "corrections": [
       {
         "issue_type": "order_mismatch",
         "affected_section": "chapter-three-player-character-classes",
         "action": "Move 'chapter-three-player-character-classes' to position 3"
       }
     ]
   }
   ```

## Applying Corrections

### Review Process

1. **Examine corrections:**
   ```bash
   cat data/ocr_ordering_corrections.json | jq '.corrections[]'
   ```

2. **Verify in PDF:**
   - Open the source PDF
   - Check the actual page order
   - Confirm the correction makes sense

3. **Update manifest:**
   ```bash
   nano data/raw/pdf_manifest.json
   # Reorder sections array as suggested
   ```

4. **Re-run extraction:**
   ```bash
   python scripts/run_pipeline.py --stage extract --verbose
   ```

5. **Verify fix:**
   ```bash
   python scripts/run_pipeline.py --stage validate --verbose
   # Should show fewer/no ordering issues
   ```

## Configuration Tips

### Quick Validation (Sample Pages)

Edit `data/pipeline_config.json`:

```json
{
  "name": "ocr_ordering_validation",
  "processor_spec": {
    "config": {
      "sample_pages": [1, 10, 20, 30, 40, 50]
    }
  }
}
```

Then run:
```bash
python scripts/run_pipeline.py --stage validate --verbose
```

### Disable Caching

For testing pattern changes:

```json
{
  "config": {
    "use_cache": false
  }
}
```

### Skip OCR Validation

Remove or comment out the `ocr_ordering_validation` stage in `data/pipeline_config.json`.

## Troubleshooting

### "OCR libraries not available"

**Problem:** Tesseract or dependencies not installed.

**Solution:**
```bash
# macOS
brew install tesseract poppler

# Verify installation
tesseract --version
pdftoppm -v
```

### "OCR taking too long"

**Problem:** First run processes all pages without cache.

**Solutions:**
- Wait for cache to build (one-time cost)
- Use `sample_pages` for quick checks
- Monitor progress with `--verbose`

### "Few sections detected"

**Problem:** OCR not detecting chapter headers.

**Check:**
1. View cached OCR output:
   ```bash
   cat data/.ocr_cache/tsr02400_*_ocr.json | jq '.sections'
   ```

2. If empty or few results:
   - Check PDF quality (scanned vs. digital)
   - Verify chapter header format in PDF
   - May need to adjust detection patterns in code

### "Too many false positives"

**Problem:** OCR matching wrong sections.

**Solutions:**
- Increase similarity threshold in code (default: 0.5)
- Review match scores in validation output
- Refine title normalization logic

## Performance

### Expected Times

| Operation | Time | Notes |
|-----------|------|-------|
| First OCR run (full PDF) | 5-10 min | Depends on page count and DPI |
| Cached validation | < 1 sec | Reads from cache |
| Sample pages (10 pages) | 30-60 sec | Quick validation |

### Optimization

1. **Always use caching** for repeated runs
2. **Sample pages** for development/testing
3. **Full scan** only when verifying final ordering

## Integration with Workflow

### Normal Development Flow

```bash
# 1. Run pipeline normally
python scripts/run_pipeline.py --verbose

# 2. Check for ordering issues
cat data/ocr_ordering_corrections.json

# 3. If corrections exist:
#    - Review corrections
#    - Update manifest if needed
#    - Re-run extract stage
#    - Re-run validate stage
```

### One-Time Setup

```bash
# Generate initial OCR cache
python scripts/run_pipeline.py --stage validate --verbose

# This will take ~5-10 minutes but only needed once
# Future validations will be instant
```

## FAQ

**Q: Do I need to run OCR validation every time?**  
A: No. Run it:
- After modifying extraction logic
- When changing section ordering
- As part of periodic QA
- Before major releases

**Q: Can OCR validation fix issues automatically?**  
A: No. It generates suggestions that must be reviewed and applied manually. This ensures human oversight of critical ordering decisions.

**Q: What if I don't have Tesseract installed?**  
A: The stage will skip gracefully with a warning. Other validation stages will still run.

**Q: Can I customize section detection patterns?**  
A: Yes, edit `_detect_section_headers()` in `tools/pdf_pipeline/stages/validate.py`.

**Q: How accurate is the OCR?**  
A: Depends on PDF quality. Digital PDFs: ~95%+. Scanned PDFs: ~80-90%. The fuzzy matching helps handle OCR errors.

## Next Steps

1. **Read full documentation:** `OCR_VALIDATION_IMPLEMENTATION.md`
2. **Run first validation:** Generate cache and corrections
3. **Review results:** Examine corrections file
4. **Apply fixes:** Update manifest/specs as needed
5. **Iterate:** Re-run until no ordering issues

## Support

For issues or questions:
1. Check `OCR_VALIDATION_IMPLEMENTATION.md` for detailed documentation
2. Review console output with `--verbose` flag
3. Examine cache files for OCR quality
4. Test with sample pages first

---

**Last Updated:** November 3, 2025

