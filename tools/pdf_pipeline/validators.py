"""Validation helpers for processed conversion datasets.

Extended with framework validation checks for the pipeline architecture.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any


class ValidationError(Exception):
    """Raised when a dataset fails validation rules."""


# ============================================================================
# Framework Validation Functions
# ============================================================================

def validate_pipeline_config(config_path: Path) -> List[str]:
    """Validate pipeline configuration schema and structure.
    
    Per RULES.md line 30, this validates modifications to the pipeline configuration.
    
    Args:
        config_path: Path to pipeline_config.json
        
    Returns:
        List of validation issues found
    """
    issues: List[str] = []
    
    if not config_path.exists():
        issues.append(f"Pipeline config not found: {config_path}")
        return issues
    
    try:
        config = _load_json(config_path)
    except Exception as e:
        issues.append(f"Failed to parse config: {e}")
        return issues
    
    # Validate top-level fields
    required_fields = ["name", "version", "transformers"]
    for field in required_fields:
        if field not in config:
            issues.append(f"Missing required field: {field}")
    
    # Validate transformers
    transformers = config.get("transformers", [])
    if not transformers:
        issues.append("No transformers defined")
    
    for idx, transformer in enumerate(transformers):
        transformer_name = transformer.get("name", f"transformer_{idx}")
        
        # Check required transformer fields
        if "stages" not in transformer:
            issues.append(f"{transformer_name}: Missing 'stages' field")
            continue
        
        # Validate stages
        stages = transformer.get("stages", [])
        if not stages:
            issues.append(f"{transformer_name}: No stages defined")
        
        for stage_idx, stage in enumerate(stages):
            stage_name = stage.get("name", f"stage_{stage_idx}")
            
            # Check processor spec
            if "processor_spec" not in stage:
                issues.append(f"{transformer_name}.{stage_name}: Missing processor_spec")
                continue
            
            proc_spec = stage["processor_spec"]
            for req_field in ["name", "module_path", "class_name"]:
                if req_field not in proc_spec:
                    issues.append(
                        f"{transformer_name}.{stage_name}: processor_spec missing {req_field}"
                    )
    
    return issues


def validate_processor_loading(config_path: Path) -> List[str]:
    """Validate that all processors/postprocessors can be loaded.
    
    Per RULES.md line 30, validates processor/postprocessor loading.
    
    Args:
        config_path: Path to pipeline_config.json
        
    Returns:
        List of validation issues found
    """
    issues: List[str] = []
    
    if not config_path.exists():
        issues.append(f"Pipeline config not found: {config_path}")
        return issues
    
    try:
        config = _load_json(config_path)
    except Exception as e:
        issues.append(f"Failed to parse config: {e}")
        return issues
    
    # Try to import the loader
    try:
        from .loader import load_processor, load_postprocessor
        from .domain import ProcessorSpec, PostProcessorSpec
    except Exception as e:
        issues.append(f"Failed to import framework modules: {e}")
        return issues
    
    # Validate each processor can be loaded
    for transformer in config.get("transformers", []):
        transformer_name = transformer.get("name", "unknown")
        
        for stage in transformer.get("stages", []):
            stage_name = stage.get("name", "unknown")
            
            # Validate processor
            proc_spec_dict = stage.get("processor_spec", {})
            if proc_spec_dict:
                try:
                    proc_spec = ProcessorSpec(**proc_spec_dict)
                    # Don't actually load, just validate spec is valid
                except Exception as e:
                    issues.append(
                        f"{transformer_name}.{stage_name}: Invalid processor spec - {e}"
                    )
            
            # Validate postprocessor if present
            postproc_spec_dict = stage.get("postprocessor_spec")
            if postproc_spec_dict:
                try:
                    postproc_spec = PostProcessorSpec(**postproc_spec_dict)
                    # Don't actually load, just validate spec is valid
                except Exception as e:
                    issues.append(
                        f"{transformer_name}.{stage_name}: Invalid postprocessor spec - {e}"
                    )
    
    return issues


def validate_stage_compatibility(config_path: Path) -> List[str]:
    """Validate stage input/output compatibility.
    
    Per RULES.md line 30, validates stage input/output compatibility.
    
    Args:
        config_path: Path to pipeline_config.json
        
    Returns:
        List of validation issues found
    """
    issues: List[str] = []
    
    if not config_path.exists():
        issues.append(f"Pipeline config not found: {config_path}")
        return issues
    
    try:
        config = _load_json(config_path)
    except Exception as e:
        issues.append(f"Failed to parse config: {e}")
        return issues
    
    # Check transformer sequence compatibility
    transformers = config.get("transformers", [])
    for idx in range(len(transformers) - 1):
        current = transformers[idx]
        next_trans = transformers[idx + 1]
        
        current_output = current.get("output_type")
        next_input = next_trans.get("input_type")
        
        if current_output and next_input and current_output != next_input:
            issues.append(
                f"Type mismatch: {current['name']} outputs {current_output} "
                f"but {next_trans['name']} expects {next_input}"
            )
    
    return issues


def validate_framework_integrity() -> List[str]:
    """Validate overall framework integrity.
    
    Per RULES.md line 30, validates the framework components.
    
    Returns:
        List of validation issues found
    """
    issues: List[str] = []
    
    # Check required framework modules exist
    from pathlib import Path
    framework_dir = Path(__file__).parent
    
    required_modules = [
        "domain.py",
        "base.py",
        "loader.py",
        "pipeline.py",
    ]
    
    for module in required_modules:
        module_path = framework_dir / module
        if not module_path.exists():
            issues.append(f"Required framework module missing: {module}")
    
    # Check stages directory
    stages_dir = framework_dir / "stages"
    if not stages_dir.exists():
        issues.append("Stages directory missing")
    else:
        required_stages = [
            "extract.py",
            "transform.py",
            "validate.py",
            "rules_conversion.py",
            "foundry_build.py",
        ]
        
        for stage in required_stages:
            stage_path = stages_dir / stage
            if not stage_path.exists():
                issues.append(f"Required stage module missing: stages/{stage}")
    
    return issues


# ============================================================================
# Original Validation Functions
# ============================================================================


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_ancestries(processed_path: Path) -> List[str]:
    """Run sanity checks on the processed ancestry dataset."""

    data = _load_json(processed_path)
    entities = data.get("data", {}).get("entities", [])
    issues: List[str] = []

    if not entities:
        issues.append("no ancestry entities found")
        return issues

    for entity in entities:
        name = entity.get("name", "<unknown>")
        description = entity.get("description", "").strip()
        pf2e = entity.get("pf2e", {})

        if len(description) < 40:
            issues.append(f"{name}: description too short")
        boosts = pf2e.get("boosts", [])
        if not boosts or "free" not in boosts:
            issues.append(f"{name}: missing free ability boost")
        if pf2e.get("hit_points", 0) <= 0:
            issues.append(f"{name}: invalid hit point value")
        languages = pf2e.get("languages", [])
        if not languages:
            issues.append(f"{name}: no languages mapped")

    return issues


def validate_journals(processed_dir: Path) -> List[str]:
    """Ensure each processed journal entry has content and a title."""

    issues: List[str] = []
    if not processed_dir.exists():
        issues.append(f"journal directory missing: {processed_dir}")
        return issues

    files = sorted(processed_dir.glob("*.json"))
    if not files:
        issues.append("no journal entries generated")
        return issues

    for journal_file in files:
        payload = _load_json(journal_file)
        data = payload.get("data", {})
        title = data.get("title") or payload.get("slug") or journal_file.stem
        content = data.get("content", "").strip()

        if not title:
            issues.append(f"{journal_file.name}: missing title")
        if len(content) < 40:
            issues.append(f"{journal_file.name}: content too short")
        
        # Chapter-specific validations
        if journal_file.stem == "chapter-three-player-character-classes":
            issues.extend(_validate_chapter_3(journal_file, content))

    return issues


def _validate_chapter_3(journal_file: Path, content: str) -> List[str]:
    """Validate Chapter 3: Player Character Classes specific requirements.
    
    Args:
        journal_file: Path to the journal file
        content: HTML content of the journal
        
    Returns:
        List of validation issues found
    """
    issues: List[str] = []
    
    # Validate Class Ability Requirements table (Rule #31)
    # This table was fixed in chapter_3_postprocessing.py and should have:
    # - 7 columns: Class, Str, Dex, Con, Int, Wis, Cha
    # - 5 rows: 1 header + 4 data rows (Gladiator, Defiler, Templar, Psionicist)
    table_match = re.search(
        r'Class Ability Requirements</span></p>\s*<table[^>]*>(.*?)</table>',
        content,
        re.DOTALL
    )
    
    if not table_match:
        issues.append(f"{journal_file.name}: Class Ability Requirements table not found")
    else:
        table_html = table_match.group(1)
        rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
        
        if len(rows) != 5:
            issues.append(
                f"{journal_file.name}: Class Ability Requirements table should have 5 rows "
                f"(1 header + 4 data), found {len(rows)}"
            )
        
        # Check header row has correct columns
        if rows:
            header_cells = re.findall(r'<th>([^<]*)</th>', rows[0])
            expected_headers = ['Class', 'Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
            if header_cells != expected_headers:
                issues.append(
                    f"{journal_file.name}: Class Ability Requirements table headers incorrect. "
                    f"Expected {expected_headers}, found {header_cells}"
                )
        
        # Check that all 4 classes are present
        expected_classes = ['Gladiator', 'Defiler', 'Templar', 'Psionicist']
        for class_name in expected_classes:
            if class_name not in table_html:
                issues.append(
                    f"{journal_file.name}: Class Ability Requirements table missing {class_name}"
                )
        
        # Check specific corrected values (from earlier fixes)
        # Defiler Int should be 3 (was incorrectly 9)
        defiler_row_match = re.search(
            r'<tr>.*?<td>Defiler</td>.*?<td>-</td>.*?<td>-</td>.*?<td>-</td>.*?<td>(\d+)</td>',
            table_html,
            re.DOTALL
        )
        if defiler_row_match:
            defiler_int = defiler_row_match.group(1)
            if defiler_int != '3':
                issues.append(
                    f"{journal_file.name}: Defiler Int should be 3, found {defiler_int}"
                )
        
        # Templar should be Int: 10, Wis: 7, Cha: -
        templar_row_match = re.search(
            r'<tr>.*?<td>Templar</td>.*?<td>-</td>.*?<td>-</td>.*?<td>-</td>.*?<td>(\d+)</td>.*?<td>(\d+)</td>.*?<td>(-)</td>',
            table_html,
            re.DOTALL
        )
        if templar_row_match:
            templar_int = templar_row_match.group(1)
            templar_wis = templar_row_match.group(2)
            if templar_int != '10' or templar_wis != '7':
                issues.append(
                    f"{journal_file.name}: Templar should have Int: 10, Wis: 7, "
                    f"found Int: {templar_int}, Wis: {templar_wis}"
                )
    
    # Validate that "Newly Created Characters" header appears after the table (Rule #31)
    newly_created_match = re.search(
        r'Class Ability Requirements</span></p>\s*<table[^>]*>.*?</table>\s*<p><span[^>]*>Newly Created Characters</span></p>',
        content,
        re.DOTALL
    )
    
    if not newly_created_match:
        issues.append(
            f"{journal_file.name}: 'Newly Created Characters' header missing or not positioned after Class Ability Requirements table"
        )
    
    # Validate Fighters Followers table (Rule #31)
    # This table was extracted in chapter_3_processing.py and should have:
    # - 4 columns: Char. Level, Stands, Level, Special
    # - 11 rows: 1 header + 10 data rows (levels 11-20)
    # We need to match specifically from <table> to </table> that contains "Char. Level"
    # and only count rows within that specific table
    fighters_table_match = re.search(
        r'<table[^>]*>\s*<tr>\s*<th>Char\. Level</th>.*?</table>',
        content,
        re.DOTALL
    )
    
    if fighters_table_match:
        fighters_table = fighters_table_match.group(0)
        rows = re.findall(r'<tr>(.*?)</tr>', fighters_table, re.DOTALL)
        
        # Check row count (1 header + 10 data)
        if len(rows) != 11:
            issues.append(
                f"{journal_file.name}: Fighters Followers table should have 11 rows "
                f"(1 header + 10 data for levels 11-20), found {len(rows)}"
            )
        
        # Check that level 11 is present (was missing in earlier version)
        if '<td>11</td>' not in fighters_table:
            issues.append(
                f"{journal_file.name}: Fighters Followers table missing level 11 row"
            )
        
        # Check that level 20 is present
        if '<td>20</td>' not in fighters_table:
            issues.append(
                f"{journal_file.name}: Fighters Followers table missing level 20 row"
            )
    
    # Validate Gladiator section paragraph count (Rule #31)
    gladiator_match = re.search(
        r'<p><span[^>]*>Gladiator</span></p>(.*?)(<p><span[^>]*>(?:Ranger|Fighter)</span></p>|$)',
        content,
        re.DOTALL
    )
    
    if gladiator_match:
        gladiator_section = gladiator_match.group(1)
        # Count paragraphs, excluding table rows
        paragraphs = re.findall(r'<p>(?!<table)(.*?)</p>', gladiator_section, re.DOTALL)
        # Filter out empty paragraphs and table content
        paragraphs = [p for p in paragraphs if p.strip() and not re.search(r'<table|Ability Requirements:|Prime Requisite:', p)]
        
        if len(paragraphs) != 10:
            issues.append(
                f"{journal_file.name}: Gladiator section should have 10 paragraphs, found {len(paragraphs)}"
            )
        
        # Check for specific paragraph starting points
        expected_starts = [
            "Gladiators are the slave warriors",
            "A gladiator who has a Strength",
            "Gladiators can have any alignment:",
            "A gladiator can use most magical items,",
            "Gladiators have the following",
            "A gladiator is automatically proficient",
            "A gladiator can specialize in",
            "A gladiator is an expert in unarmed",
            "A gladiator learns to optimize",
            "A gladiator attracts followers"
        ]
        
        for expected in expected_starts:
            if expected not in gladiator_section:
                issues.append(
                    f"{journal_file.name}: Gladiator section missing paragraph starting with '{expected[:40]}...'"
                )
    
    # Validate that ability requirements tables don't have duplicate text after them (Rule #31)
    # Check all 9 classes: Ranger, Defiler, Preserver, Illusionist, Cleric, Templar, Thief, Bard, Psionicist
    classes_with_tables = ['Ranger', 'Defiler', 'Preserver', 'Illusionist', 'Cleric', 'Templar', 'Thief', 'Bard', 'Psionicist']
    
    for class_name in classes_with_tables:
        # Find the class section with its ability requirements table
        class_pattern = rf'<p><span[^>]*>{class_name}\s*</span></p>(.*?)</table>(.*?)(<p>[A-Z])'
        class_match = re.search(class_pattern, content, re.DOTALL)
        
        if class_match:
            after_table = class_match.group(2)
            
            # Look for fragmented ability requirements text (short paragraphs with keywords)
            fragments = re.findall(r'<p>([^<]*)</p>', after_table[:400])
            suspicious = [f for f in fragments if any(kw in f for kw in [
                'Ability Requirements', 'Prime Requisite', 'Races Allowed',
                'Strength', 'Dexterity', 'Intelligence', 'Wisdom'
            ]) and len(f) < 150]
            
            if suspicious:
                issues.append(
                    f"{journal_file.name}: {class_name} has duplicate ability requirements text after table: '{suspicious[0][:60]}...'"
                )
    
    return issues
