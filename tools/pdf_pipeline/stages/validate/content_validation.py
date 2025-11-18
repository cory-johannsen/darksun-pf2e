"""Validation processor: ContentValidationProcessor.

This module contains the ContentValidationProcessor for the Dark Sun PDF pipeline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...base import BaseProcessor
from ...domain import ExecutionContext, ProcessorInput, ProcessorOutput


class ContentValidationProcessor(BaseProcessor):
    """Processor for validating content quality and completeness.
    
    Validates content length, HTML validity, and data integrity.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Validate content quality.
        
        Args:
            input_data: Input containing processed data directory
            context: Execution context
            
        Returns:
            ProcessorOutput with validation results
        """
        # Extract configuration
        processed_dir = Path(self.config.get("processed_dir", "data/processed"))
        min_description_length = self.config.get("min_description_length", 10)
        check_html_validity = self.config.get("check_html_validity", True)
        check_missing_data = self.config.get("check_missing_data", True)
        
        errors = []
        warnings = []
        validated_items = []
        
        # Validate journal files
        journals_dir = processed_dir / "journals"
        if journals_dir.exists():
            for json_file in journals_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    item_data = data.get("data", {})
                    
                    # Check description length
                    description = item_data.get("description", "")
                    if isinstance(description, str) and len(description) < min_description_length:
                        warnings.append(
                            f"{json_file.name}: Description too short ({len(description)} < {min_description_length})"
                        )
                    
                    # Check HTML validity (basic check)
                    if check_html_validity and isinstance(description, str):
                        if "<" in description and ">" in description:
                            # Basic tag matching
                            open_tags = description.count("<")
                            close_tags = description.count(">")
                            if open_tags != close_tags:
                                warnings.append(f"{json_file.name}: Mismatched HTML tags")
                    
                    validated_items.append(str(json_file))
                    context.items_processed += 1
                    
                except Exception as e:
                    errors.append(f"{json_file.name}: Content validation error - {e}")
        
        # Validate ancestry file
        ancestry_file = processed_dir / "ancestries.json"
        if ancestry_file.exists():
            try:
                data = json.loads(ancestry_file.read_text(encoding="utf-8"))
                ancestries = data.get("data", [])
                
                if isinstance(ancestries, list):
                    for ancestry in ancestries:
                        if check_missing_data:
                            # Check required fields
                            required_fields = ["name", "description"]
                            for field in required_fields:
                                if field not in ancestry or not ancestry[field]:
                                    warnings.append(
                                        f"ancestries.json: Missing or empty '{field}' in ancestry"
                                    )
                
                validated_items.append(str(ancestry_file))
                context.items_processed += 1
                
            except Exception as e:
                errors.append(f"ancestries.json: Content validation error - {e}")
        
        # Add to context
        context.errors.extend(errors)
        context.warnings.extend(warnings)
        
        return ProcessorOutput(
            data={
                "validated_items": validated_items,
                "errors": errors,
                "warnings": warnings,
                "success": len(errors) == 0,
            },
            metadata={
                "item_count": len(validated_items),
                "error_count": len(errors),
                "warning_count": len(warnings),
            }
        )


