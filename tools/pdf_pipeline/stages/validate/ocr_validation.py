"""Validation processor: OCRValidationProcessor.

This module contains the OCRValidationProcessor for the Dark Sun PDF pipeline.
"""

from __future__ import annotations

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

import fitz  # PyMuPDF

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...base import BaseProcessor
from ...domain import ExecutionContext, ProcessorInput, ProcessorOutput


class OCRValidationProcessor(BaseProcessor):
    """Processor for OCR-based content ordering validation.
    
    Uses OCR to extract text from PDF in reading order and compares
    with the extracted structured data to verify ordering is correct.
    Generates correction suggestions for spec files.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Validate content ordering using OCR.
        
        Args:
            input_data: Input containing PDF path and structured data directory
            context: Execution context
            
        Returns:
            ProcessorOutput with validation results and correction suggestions
        """
        if not TESSERACT_AVAILABLE:
            context.warnings.append("OCR libraries not available - skipping OCR validation")
            return ProcessorOutput(
                data={
                    "skipped": True,
                    "reason": "OCR libraries not installed",
                    "errors": [],
                    "warnings": ["Install pytesseract, pdf2image, and Pillow for OCR validation"],
                },
                metadata={"skipped": True}
            )
        
        # Extract configuration
        pdf_path = Path(self.config.get("pdf_path", "tsr02400_-_ADD_Setting_-_Dark_Sun_Box_Set_Original.pdf"))
        structured_dir = Path(self.config.get("structured_dir", "data/raw_structured/sections"))
        manifest_path = Path(self.config.get("manifest_path", "data/raw/pdf_manifest.json"))
        output_corrections = self.config.get("output_corrections", True)
        corrections_path = Path(self.config.get("corrections_path", "data/ocr_ordering_corrections.json"))
        ocr_cache_dir = Path(self.config.get("ocr_cache_dir", "data/.ocr_cache"))
        use_cache = self.config.get("use_cache", True)
        sample_pages = self.config.get("sample_pages", None)  # None = all pages, or list of page numbers
        
        errors = []
        warnings = []
        corrections = []
        
        # Load manifest for expected ordering
        if not manifest_path.exists():
            errors.append(f"Manifest not found: {manifest_path}")
            return self._error_output(errors, warnings, context)
        
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expected_order = [item["slug"] for item in manifest.get("sections", [])]
        except Exception as e:
            errors.append(f"Failed to load manifest: {e}")
            return self._error_output(errors, warnings, context)
        
        # Extract OCR text from PDF
        try:
            ocr_text, ocr_sections = self._extract_ocr_text(
                pdf_path, 
                ocr_cache_dir if use_cache else None,
                sample_pages
            )
            context.items_processed += 1
        except Exception as e:
            errors.append(f"OCR extraction failed: {e}")
            return self._error_output(errors, warnings, context)
        
        # Load structured sections for comparison
        structured_sections = self._load_structured_sections(structured_dir)
        
        # Compare ordering
        ordering_issues = self._compare_ordering(
            ocr_text,
            ocr_sections,
            structured_sections,
            expected_order
        )
        
        # Generate corrections
        if ordering_issues and output_corrections:
            corrections = self._generate_corrections(
                ordering_issues,
                expected_order,
                structured_sections
            )
            
            # Save corrections
            if corrections:
                self._save_corrections(corrections, corrections_path)
                warnings.append(f"Generated {len(corrections)} ordering corrections: {corrections_path}")
        
        # Add results to context
        if ordering_issues:
            for issue in ordering_issues:
                warnings.append(f"Ordering issue: {issue['description']}")
        
        context.warnings.extend(warnings)
        context.errors.extend(errors)
        
        success = len(errors) == 0
        
        return ProcessorOutput(
            data={
                "ocr_sections_found": len(ocr_sections),
                "structured_sections_found": len(structured_sections),
                "ordering_issues": ordering_issues,
                "corrections": corrections,
                "errors": errors,
                "warnings": warnings,
                "success": success,
            },
            metadata={
                "ocr_sections": len(ocr_sections),
                "structured_sections": len(structured_sections),
                "issues_found": len(ordering_issues),
                "corrections_generated": len(corrections),
            }
        )
    
    def _extract_ocr_text(
        self, 
        pdf_path: Path, 
        cache_dir: Optional[Path] = None,
        sample_pages: Optional[List[int]] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract text from PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            cache_dir: Directory to cache OCR results
            sample_pages: Optional list of page numbers to process (1-indexed)
            
        Returns:
            Tuple of (full OCR text, list of detected sections with page info)
        """
        # Check cache first
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = cache_dir / f"{pdf_path.stem}_ocr.json"
            
            if cache_file.exists():
                try:
                    cached = json.loads(cache_file.read_text(encoding="utf-8"))
                    return cached["text"], cached["sections"]
                except Exception:
                    pass  # Cache invalid, regenerate
        
        # Open PDF with PyMuPDF for metadata
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        
        # Determine which pages to process
        if sample_pages:
            pages_to_process = [p - 1 for p in sample_pages if 0 < p <= page_count]
        else:
            pages_to_process = list(range(page_count))
        
        doc.close()
        
        # Convert PDF pages to images and OCR
        full_text = []
        sections = []
        
        # Process in batches to manage memory
        batch_size = 10
        for batch_start in range(0, len(pages_to_process), batch_size):
            batch_pages = pages_to_process[batch_start:batch_start + batch_size]
            
            # Convert pages to images
            images = convert_from_path(
                str(pdf_path),
                first_page=batch_pages[0] + 1,
                last_page=batch_pages[-1] + 1,
                dpi=200
            )
            
            # OCR each image
            for idx, image in enumerate(images):
                page_num = batch_pages[idx]
                text = pytesseract.image_to_string(image)
                full_text.append(text)
                
                # Detect section headers (chapters, major headings)
                section_headers = self._detect_section_headers(text, page_num + 1)
                sections.extend(section_headers)
        
        combined_text = "\n\n".join(full_text)
        
        # Cache results
        if cache_dir:
            cache_data = {
                "text": combined_text,
                "sections": sections,
                "page_count": len(pages_to_process),
            }
            cache_file.write_text(
                json.dumps(cache_data, indent=2),
                encoding="utf-8"
            )
        
        return combined_text, sections
    
    def _detect_section_headers(self, text: str, page_num: int) -> List[Dict[str, Any]]:
        """Detect section headers in OCR text.
        
        Args:
            text: OCR text from a page
            page_num: Page number (1-indexed)
            
        Returns:
            List of detected section headers with metadata
        """
        sections = []
        
        # Pattern for chapter headers
        chapter_pattern = r"(?:CHAPTER|Chapter)\s+([A-Z]+|[IVX]+|\d+)[:\s]+(.+?)(?:\n|$)"
        
        for match in re.finditer(chapter_pattern, text, re.IGNORECASE):
            chapter_num = match.group(1).strip()
            chapter_title = match.group(2).strip()
            
            # Clean up title
            chapter_title = re.sub(r'\s+', ' ', chapter_title)
            chapter_title = chapter_title.strip('.')
            
            sections.append({
                "type": "chapter",
                "number": chapter_num,
                "title": chapter_title,
                "page": page_num,
                "raw_text": match.group(0),
            })
        
        return sections
    
    def _load_structured_sections(self, structured_dir: Path) -> Dict[str, Dict[str, Any]]:
        """Load structured section data.
        
        Args:
            structured_dir: Directory containing structured JSON files
            
        Returns:
            Dictionary mapping slug to section metadata
        """
        sections = {}
        
        for json_file in structured_dir.glob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                slug = data.get("slug", json_file.stem)
                
                sections[slug] = {
                    "file": str(json_file),
                    "slug": slug,
                    "title": data.get("title", ""),
                    "pages": data.get("metadata", {}).get("pages", []),
                    "section_number": data.get("metadata", {}).get("section_number", ""),
                }
            except Exception:
                continue
        
        return sections
    
    def _compare_ordering(
        self,
        ocr_text: str,
        ocr_sections: List[Dict[str, Any]],
        structured_sections: Dict[str, Dict[str, Any]],
        expected_order: List[str]
    ) -> List[Dict[str, Any]]:
        """Compare OCR-detected ordering with structured data ordering.
        
        Args:
            ocr_text: Full OCR text
            ocr_sections: Sections detected from OCR
            structured_sections: Structured section metadata
            expected_order: Expected section order from manifest
            
        Returns:
            List of ordering issues found
        """
        issues = []
        
        # Sort OCR sections by page number
        ocr_sections_sorted = sorted(ocr_sections, key=lambda x: x["page"])
        
        # Try to match OCR sections to structured sections
        ocr_to_structured = []
        
        for ocr_section in ocr_sections_sorted:
            # Attempt to match by title
            best_match = None
            best_score = 0
            
            for slug, struct_data in structured_sections.items():
                score = self._title_similarity(ocr_section["title"], struct_data["title"])
                if score > best_score and score > 0.5:  # Threshold
                    best_score = score
                    best_match = slug
            
            if best_match:
                ocr_to_structured.append({
                    "ocr_section": ocr_section,
                    "structured_slug": best_match,
                    "match_score": best_score,
                })
        
        # Compare detected order with expected order
        detected_order = [item["structured_slug"] for item in ocr_to_structured]
        
        if len(detected_order) < len(expected_order) * 0.5:
            issues.append({
                "type": "insufficient_detection",
                "description": f"OCR detected only {len(detected_order)} of {len(expected_order)} expected sections",
                "severity": "warning",
            })
        
        # Check for order mismatches
        for i, detected_slug in enumerate(detected_order):
            try:
                expected_index = expected_order.index(detected_slug)
                
                # Check if order is preserved
                if i > 0 and detected_order[i-1] in expected_order:
                    prev_expected_index = expected_order.index(detected_order[i-1])
                    
                    if expected_index < prev_expected_index:
                        issues.append({
                            "type": "order_mismatch",
                            "description": f"Section '{detected_slug}' appears before '{detected_order[i-1]}' in OCR but after in expected order",
                            "severity": "error",
                            "detected_slug": detected_slug,
                            "previous_slug": detected_order[i-1],
                            "expected_index": expected_index,
                            "detected_index": i,
                        })
            except ValueError:
                # Slug not in expected order
                issues.append({
                    "type": "unexpected_section",
                    "description": f"Section '{detected_slug}' found in OCR but not in expected order",
                    "severity": "warning",
                    "detected_slug": detected_slug,
                })
        
        return issues
    
    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles.
        
        Args:
            title1: First title
            title2: Second title
            
        Returns:
            Similarity score between 0 and 1
        """
        # Normalize titles
        t1 = re.sub(r'[^a-z0-9\s]', '', title1.lower())
        t2 = re.sub(r'[^a-z0-9\s]', '', title2.lower())
        
        # Simple word overlap scoring
        words1 = set(t1.split())
        words2 = set(t2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _generate_corrections(
        self,
        ordering_issues: List[Dict[str, Any]],
        expected_order: List[str],
        structured_sections: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate correction suggestions based on ordering issues.
        
        Args:
            ordering_issues: List of detected ordering issues
            expected_order: Expected section order
            structured_sections: Structured section metadata
            
        Returns:
            List of correction suggestions
        """
        corrections = []
        
        for issue in ordering_issues:
            if issue["type"] == "order_mismatch":
                # Suggest reordering in manifest
                correction = {
                    "issue_type": "order_mismatch",
                    "affected_section": issue["detected_slug"],
                    "suggestion": "update_manifest_order",
                    "details": {
                        "section": issue["detected_slug"],
                        "current_position": issue["expected_index"],
                        "suggested_position": issue["detected_index"],
                        "reason": issue["description"],
                    },
                    "action": f"Move '{issue['detected_slug']}' to position {issue['detected_index']} in manifest"
                }
                corrections.append(correction)
            
            elif issue["type"] == "unexpected_section":
                # Suggest adding to manifest
                correction = {
                    "issue_type": "missing_from_manifest",
                    "affected_section": issue["detected_slug"],
                    "suggestion": "add_to_manifest",
                    "details": {
                        "section": issue["detected_slug"],
                        "reason": issue["description"],
                    },
                    "action": f"Add '{issue['detected_slug']}' to manifest"
                }
                corrections.append(correction)
        
        return corrections
    
    def _save_corrections(self, corrections: List[Dict[str, Any]], output_path: Path) -> None:
        """Save correction suggestions to file.
        
        Args:
            corrections: List of corrections
            output_path: Path to save corrections
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        output_data = {
            "generated_at": "2025-11-03",
            "correction_count": len(corrections),
            "corrections": corrections,
            "instructions": "Review these corrections and apply manually to manifest or spec files",
        }
        
        output_path.write_text(
            json.dumps(output_data, indent=2),
            encoding="utf-8"
        )
    
    def _error_output(
        self,
        errors: List[str],
        warnings: List[str],
        context: ExecutionContext
    ) -> ProcessorOutput:
        """Generate error output.
        
        Args:
            errors: List of errors
            warnings: List of warnings
            context: Execution context
            
        Returns:
            ProcessorOutput with error state
        """
        context.errors.extend(errors)
        context.warnings.extend(warnings)
        
        return ProcessorOutput(
            data={
                "errors": errors,
                "warnings": warnings,
                "success": False,
            },
            metadata={
                "error_count": len(errors),
                "warning_count": len(warnings),
            }
        )


