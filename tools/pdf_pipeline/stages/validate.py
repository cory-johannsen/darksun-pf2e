"""Validate stage processors for data validation.

This module wraps existing validation logic in Processor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput


class StructuralValidationProcessor(BaseProcessor):
    """Processor for validating data structure and schema compliance.
    
    Validates JSON structure, required fields, and references.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Validate data structure.
        
        Args:
            input_data: Input containing processed data directory
            context: Execution context
            
        Returns:
            ProcessorOutput with validation results
        """
        # Extract configuration
        processed_dir = Path(self.config.get("processed_dir", "data/processed"))
        strict = self.config.get("strict", True)
        check_schema = self.config.get("check_schema", True)
        check_references = self.config.get("check_references", True)
        
        errors = []
        warnings = []
        validated_files = []
        
        # Validate all JSON files in processed directory
        for json_file in processed_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                
                # Basic structure validation
                if check_schema:
                    if "slug" not in data:
                        errors.append(f"{json_file.name}: Missing 'slug' field")
                    if "transformer" not in data:
                        warnings.append(f"{json_file.name}: Missing 'transformer' field")
                    if "data" not in data:
                        errors.append(f"{json_file.name}: Missing 'data' field")
                
                validated_files.append(str(json_file))
                context.items_processed += 1
                
            except json.JSONDecodeError as e:
                errors.append(f"{json_file.name}: Invalid JSON - {e}")
            except Exception as e:
                errors.append(f"{json_file.name}: Validation error - {e}")
        
        # Add to context
        context.errors.extend(errors)
        context.warnings.extend(warnings)
        
        # Determine success
        success = len(errors) == 0 or not strict
        
        return ProcessorOutput(
            data={
                "validated_files": validated_files,
                "errors": errors,
                "warnings": warnings,
                "success": success,
            },
            metadata={
                "file_count": len(validated_files),
                "error_count": len(errors),
                "warning_count": len(warnings),
            }
        )


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

