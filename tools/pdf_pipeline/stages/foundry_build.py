"""Foundry build stage processors for generating Foundry VTT modules.

This module wraps existing compendium build logic in Processor classes
following the domain model architecture.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from ..compendium import build_ancestry_pack, build_journal_pack


class CompendiumBuildProcessor(BaseProcessor):
    """Processor for generating Foundry compendium databases.
    
    Wraps the existing compendium build functionality.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Build Foundry compendium databases.
        
        Args:
            input_data: Input containing converted data directory
            context: Execution context
            
        Returns:
            ProcessorOutput with built compendium information
        """
        # Extract configuration
        # For now, use processed dir since conversion is stubbed
        converted_dir = Path(self.config.get("converted_dir", "data/processed"))
        output_dir = Path(self.config.get("output_dir", "packs"))
        foundry_version = self.config.get("foundry_version", 13)
        system = self.config.get("system", "pf2e")
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        built_compendia = []
        
        # Build ancestry compendium
        ancestry_file = converted_dir / "ancestries.json"
        if ancestry_file.exists():
            ancestry_db = output_dir / "dark-sun-ancestries.db"
            try:
                build_ancestry_pack(ancestry_file, ancestry_db)
                built_compendia.append({
                    "name": "dark-sun-ancestries",
                    "path": str(ancestry_db),
                    "type": "ancestry"
                })
                context.items_processed += 1
            except Exception as e:
                context.errors.append(f"Error building ancestry compendium: {e}")
        
        # Build rules compendium (journals)
        journals_dir = converted_dir / "journals"
        if journals_dir.exists():
            rules_db = output_dir / "dark-sun-rules.db"
            try:
                build_journal_pack(journals_dir, rules_db)
                built_compendia.append({
                    "name": "dark-sun-rules",
                    "path": str(rules_db),
                    "type": "journal"
                })
                context.items_processed += 1
            except Exception as e:
                context.errors.append(f"Error building rules compendium: {e}")
        
        return ProcessorOutput(
            data={
                "output_dir": str(output_dir),
                "compendia": built_compendia,
            },
            metadata={
                "compendium_count": len(built_compendia),
                "foundry_version": foundry_version,
                "system": system,
            }
        )


class ModuleMetadataProcessor(BaseProcessor):
    """Processor for generating or updating module.json.
    
    Creates module.json with correct metadata for Foundry VTT.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Generate or update module.json.
        
        Args:
            input_data: Input containing module configuration
            context: Execution context
            
        Returns:
            ProcessorOutput with module metadata
        """
        # Extract configuration
        output_dir = Path(self.config.get("output_dir", "."))
        module_id = self.config.get("module_id", "darksun-pf2e")
        title = self.config.get("title", "Dark Sun for PF2E")
        version = self.config.get("version", "1.0.0")
        compatibility = self.config.get("compatibility", {"minimum": "13", "verified": "13"})
        
        # Build module.json structure
        module_data = {
            "id": module_id,
            "title": title,
            "version": version,
            "compatibility": {
                "minimum": compatibility.get("minimum", "13"),
                "verified": compatibility.get("verified", "13"),
            },
            "description": "Dark Sun campaign setting converted to Pathfinder 2E for Foundry VTT",
            "authors": [
                {
                    "name": "Pipeline Generator",
                    "flags": {}
                }
            ],
            "packs": [
                {
                    "name": "dark-sun-ancestries",
                    "label": "Dark Sun Ancestries",
                    "path": "packs/dark-sun-ancestries.db",
                    "type": "Item",
                    "system": "pf2e",
                    "ownership": {
                        "PLAYER": "OBSERVER",
                        "ASSISTANT": "OWNER"
                    }
                },
                {
                    "name": "dark-sun-rules",
                    "label": "Dark Sun Rules",
                    "path": "packs/dark-sun-rules.db",
                    "type": "JournalEntry",
                    "system": "pf2e",
                    "ownership": {
                        "PLAYER": "OBSERVER",
                        "ASSISTANT": "OWNER"
                    }
                }
            ],
            "relationships": {
                "systems": [
                    {
                        "id": "pf2e",
                        "type": "system",
                        "compatibility": {
                            "minimum": "6.0.0"
                        }
                    }
                ]
            },
            "manifest": f"https://example.com/modules/{module_id}/module.json",
            "download": f"https://example.com/modules/{module_id}/module.zip"
        }
        
        # Write module.json
        module_json_path = output_dir / "module.json"
        module_json_path.write_text(
            json.dumps(module_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        context.items_processed = 1
        
        return ProcessorOutput(
            data={
                "module_json": str(module_json_path),
                "module_data": module_data,
            },
            metadata={
                "module_id": module_id,
                "version": version,
            }
        )

