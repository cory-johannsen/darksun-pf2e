"""AD&D 2E rule extractor for building knowledge base.

This module extracts game rules from AD&D 2E sourcebooks (primarily DMG)
and stores them in structured format using the knowledge repository.

Requirements:
- SWENG-1: Single Responsibility Principle
- SWENG-6: Test-driven development pattern
- SWENG-7: All functions MUST have automated unit tests
- PY-6: Console logs tracing execution
- AGENT-6: No hard-coded data values in extraction logic
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from .adnd_schema import (
    ADnDAbilityScore,
    ADnDArmorClass,
    ADnDCombatMechanic,
    ADnDProficiency,
    ADnDRule,
    ADnDSavingThrow,
    ADnDSourcebook,
    ADnDSpell,
    ADnDTHAC0,
)
from .knowledge_repository import KnowledgeRepository, RuleCategory

# Set up logging per PY-6
logger = logging.getLogger(__name__)


class ADnDRuleExtractor(BaseProcessor):
    """Processor for extracting AD&D 2E rules from PDF sourcebooks.

    This processor reads AD&D 2E PDFs, extracts structured rules,
    and stores them in the knowledge repository.
    """

    def process(
        self, input_data: ProcessorInput, context: ExecutionContext
    ) -> ProcessorOutput:
        """Extract AD&D 2E rules from sourcebooks.

        Args:
            input_data: Input containing extraction configuration
            context: Execution context

        Returns:
            ProcessorOutput with extraction results
        """
        # Load configuration
        registry_path = Path(self.config.get("sourcebook_registry"))
        kb_dir = Path(self.config.get("knowledge_base_dir", "data/knowledge_base"))

        if not registry_path.exists():
            context.errors.append(f"Sourcebook registry not found: {registry_path}")
            return ProcessorOutput(data={"status": "error"}, metadata={})

        registry = json.loads(registry_path.read_text(encoding="utf-8"))

        # Initialize repository
        repo = KnowledgeRepository(kb_dir)

        # Extract rules from each sourcebook
        extracted_rules = []

        for sourcebook_config in registry["sourcebooks"]:
            if not sourcebook_config.get("extract_rules"):
                logger.info(f"Skipping {sourcebook_config['id']} (no extraction rules)")
                continue

            try:
                rules = self._extract_from_sourcebook(
                    sourcebook_config, repo, context
                )
                extracted_rules.extend(rules)
            except Exception as e:
                error_msg = f"Error extracting from {sourcebook_config['id']}: {e}"
                context.errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        logger.info(f"Extracted {len(extracted_rules)} rules total")

        return ProcessorOutput(
            data={
                "extracted_rules": len(extracted_rules),
                "repository_stats": repo.get_statistics(),
            },
            metadata={"sourcebooks_processed": registry["extraction_order"]},
        )

    def _extract_from_sourcebook(
        self,
        sourcebook_config: Dict[str, Any],
        repo: KnowledgeRepository,
        context: ExecutionContext,
    ) -> List[str]:
        """Extract rules from a single sourcebook.

        Args:
            sourcebook_config: Sourcebook configuration
            repo: Knowledge repository
            context: Execution context

        Returns:
            List of extracted rule IDs
        """
        sourcebook_id = sourcebook_config["id"]
        filename = sourcebook_config["filename"]
        extract_rules = sourcebook_config["extract_rules"]

        logger.info(f"Extracting rules from {sourcebook_id}: {filename}")

        # Map sourcebook ID to enum
        try:
            sourcebook = ADnDSourcebook(sourcebook_id)
        except ValueError:
            context.warnings.append(
                f"Unknown sourcebook ID: {sourcebook_id}, using dmg_revised"
            )
            sourcebook = ADnDSourcebook.DMG_REVISED

        pdf_path = Path(filename)
        if not pdf_path.exists():
            context.warnings.append(f"PDF not found: {pdf_path}")
            return []

        extracted = []

        # Extract each rule type
        for rule_type in extract_rules:
            try:
                if rule_type == "ability_scores":
                    rules = self._extract_ability_scores(pdf_path, sourcebook)
                elif rule_type == "saves":
                    rules = self._extract_saving_throws(pdf_path, sourcebook)
                elif rule_type == "thac0":
                    rules = self._extract_thac0(pdf_path, sourcebook)
                elif rule_type == "armor_class":
                    rules = self._extract_armor_class(pdf_path, sourcebook)
                elif rule_type == "combat":
                    rules = self._extract_combat_mechanics(pdf_path, sourcebook)
                elif rule_type == "proficiencies":
                    rules = self._extract_proficiencies(pdf_path, sourcebook)
                else:
                    logger.warning(f"Unknown rule type: {rule_type}")
                    continue

                # Store extracted rules
                for rule in rules:
                    category = self._get_category_for_rule(rule)
                    rule_id = repo.store_adnd_rule(rule, category, sourcebook)
                    extracted.append(rule_id)
                    context.items_processed += 1

                logger.info(f"Extracted {len(rules)} {rule_type} rules")

            except Exception as e:
                error_msg = f"Error extracting {rule_type}: {e}"
                context.errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        return extracted

    def _extract_ability_scores(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDAbilityScore]:
        """Extract ability score tables from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of ability score rules
        """
        logger.debug(f"Extracting ability scores from {pdf_path}")

        # This is a placeholder for actual extraction logic
        # Real implementation would parse PDF tables on pages 13-16
        # Per AGENT-6, we must extract from source, not hard-code

        rules = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract from pages 13-16 (0-indexed: 12-15)
                for page_num in range(12, 16):
                    if page_num >= len(pdf.pages):
                        break

                    page = pdf.pages[page_num]
                    text = page.extract_text()

                    # Look for ability score patterns
                    # This is a simplified example - real implementation needs table parsing
                    ability_pattern = r"(STR|DEX|CON|INT|WIS|CHA)\s+(\d+)"
                    matches = re.findall(ability_pattern, text)

                    for ability, score in matches:
                        # Extract modifiers from surrounding context
                        # Real implementation would parse complete tables
                        rule = ADnDAbilityScore(
                            ability=ability,
                            score=int(score),
                            modifiers={},
                            source=sourcebook,
                            page_reference=str(page_num + 1),
                        )
                        rules.append(rule)

        except Exception as e:
            logger.error(f"Error extracting ability scores: {e}", exc_info=True)

        logger.info(f"Extracted {len(rules)} ability score entries")
        return rules

    def _extract_saving_throws(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDSavingThrow]:
        """Extract saving throw tables from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of saving throw rules
        """
        logger.debug(f"Extracting saving throws from {pdf_path}")

        # Placeholder for actual extraction logic
        # Real implementation would parse saving throw tables from pages 101-102

        rules = []
        logger.info(f"Extracted {len(rules)} saving throw entries")
        return rules

    def _extract_thac0(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDTHAC0]:
        """Extract THAC0 progression tables from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of THAC0 rules
        """
        logger.debug(f"Extracting THAC0 from {pdf_path}")

        # Placeholder for actual extraction logic
        # Real implementation would parse THAC0 tables from pages 91-92

        rules = []
        logger.info(f"Extracted {len(rules)} THAC0 entries")
        return rules

    def _extract_armor_class(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDArmorClass]:
        """Extract armor class tables from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of armor class rules
        """
        logger.debug(f"Extracting armor class from {pdf_path}")

        # Placeholder for actual extraction logic
        # Real implementation would parse AC tables from pages 75-76

        rules = []
        logger.info(f"Extracted {len(rules)} armor class entries")
        return rules

    def _extract_combat_mechanics(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDCombatMechanic]:
        """Extract combat mechanics from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of combat mechanic rules
        """
        logger.debug(f"Extracting combat mechanics from {pdf_path}")

        # Placeholder for actual extraction logic
        # Real implementation would parse combat rules from pages 89-120

        rules = []
        logger.info(f"Extracted {len(rules)} combat mechanic entries")
        return rules

    def _extract_proficiencies(
        self, pdf_path: Path, sourcebook: ADnDSourcebook
    ) -> List[ADnDProficiency]:
        """Extract proficiency rules from DMG.

        Args:
            pdf_path: Path to PDF file
            sourcebook: Sourcebook identifier

        Returns:
            List of proficiency rules
        """
        logger.debug(f"Extracting proficiencies from {pdf_path}")

        # Placeholder for actual extraction logic
        # Real implementation would parse proficiency tables

        rules = []
        logger.info(f"Extracted {len(rules)} proficiency entries")
        return rules

    def _get_category_for_rule(self, rule: Any) -> RuleCategory:
        """Determine the category for a rule based on its type.

        Args:
            rule: Rule instance

        Returns:
            Rule category
        """
        type_mapping = {
            ADnDAbilityScore: RuleCategory.ABILITY_SCORES,
            ADnDSavingThrow: RuleCategory.SAVES,
            ADnDTHAC0: RuleCategory.COMBAT,
            ADnDArmorClass: RuleCategory.COMBAT,
            ADnDCombatMechanic: RuleCategory.COMBAT,
            ADnDSpell: RuleCategory.SPELLS,
            ADnDProficiency: RuleCategory.PROFICIENCIES,
            ADnDRule: RuleCategory.GENERAL,
        }

        return type_mapping.get(type(rule), RuleCategory.GENERAL)

