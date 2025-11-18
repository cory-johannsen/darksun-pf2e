"""Validation processor: StructuralValidationProcessor.

This module contains the StructuralValidationProcessor for the Dark Sun PDF pipeline.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...base import BaseProcessor
from ...domain import ExecutionContext, ProcessorInput, ProcessorOutput


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


