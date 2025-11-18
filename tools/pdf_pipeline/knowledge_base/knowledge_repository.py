"""Knowledge repository for storing and retrieving game rules.

This module provides a unified interface for storing, indexing, and querying
AD&D 2E and PF2E game rules.

Requirements:
- PY-3: Pydantic MUST be used for data modeling and validation
- SWENG-1: Single Responsibility Principle
- SWENG-2: Design by Contract with explicit preconditions and postconditions
- PY-6: Console logs tracing execution
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel

from .adnd_schema import (
    ADnDAbilityScore,
    ADnDArmorClass,
    ADnDClass,
    ADnDCombatMechanic,
    ADnDProficiency,
    ADnDRule,
    ADnDSavingThrow,
    ADnDSourcebook,
    ADnDSpell,
    ADnDTHAC0,
)
from .pf2e_schema import (
    PF2EAbilityScore,
    PF2EAction,
    PF2ECachedQuery,
    PF2EClass,
    PF2EFeat,
    PF2ERule,
    PF2ESave,
    PF2ESkill,
    PF2ESpell,
    PF2ETrait,
)

# Set up logging per PY-6
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class RuleCategory(str, Enum):
    """Enumeration of rule categories for organization."""

    ABILITY_SCORES = "ability_scores"
    SAVES = "saves"
    COMBAT = "combat"
    SPELLS = "spells"
    CLASSES = "classes"
    SKILLS = "skills"
    FEATS = "feats"
    PROFICIENCIES = "proficiencies"
    TRAITS = "traits"
    ACTIONS = "actions"
    GENERAL = "general"


class KnowledgeRepository:
    """Repository for storing and retrieving game rules.

    Provides a unified interface for managing AD&D 2E and PF2E rule knowledge bases.
    Supports indexing, querying, and version control for extracted rules.

    Preconditions:
    - base_dir must be a valid directory path
    - All stored models must be valid Pydantic BaseModel instances

    Postconditions:
    - All operations maintain data integrity
    - Index is kept in sync with stored data
    """

    # Schema registry mapping categories to their model types
    ADND_SCHEMA_REGISTRY: Dict[RuleCategory, Type[BaseModel]] = {
        RuleCategory.ABILITY_SCORES: ADnDAbilityScore,
        RuleCategory.SAVES: ADnDSavingThrow,
        RuleCategory.COMBAT: ADnDCombatMechanic,
        RuleCategory.SPELLS: ADnDSpell,
        RuleCategory.CLASSES: ADnDClass,
        RuleCategory.PROFICIENCIES: ADnDProficiency,
        RuleCategory.GENERAL: ADnDRule,
    }

    PF2E_SCHEMA_REGISTRY: Dict[RuleCategory, Type[BaseModel]] = {
        RuleCategory.ABILITY_SCORES: PF2EAbilityScore,
        RuleCategory.SAVES: PF2ESave,
        RuleCategory.SKILLS: PF2ESkill,
        RuleCategory.TRAITS: PF2ETrait,
        RuleCategory.ACTIONS: PF2EAction,
        RuleCategory.FEATS: PF2EFeat,
        RuleCategory.SPELLS: PF2ESpell,
        RuleCategory.CLASSES: PF2EClass,
        RuleCategory.GENERAL: PF2ERule,
    }

    def __init__(self, base_dir: Union[str, Path]):
        """Initialize the knowledge repository.

        Args:
            base_dir: Base directory for knowledge base storage
        """
        self.base_dir = Path(base_dir)
        self.adnd_dir = self.base_dir / "adnd_2e"
        self.pf2e_dir = self.base_dir / "pf2e_cache"
        self.index_file = self.base_dir / "index.json"

        # Create directory structure
        self.adnd_dir.mkdir(parents=True, exist_ok=True)
        self.pf2e_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize index
        self.index = self._load_index()

        logger.info(f"Initialized KnowledgeRepository at {self.base_dir}")

    def _load_index(self) -> Dict[str, Any]:
        """Load the knowledge base index.

        Returns:
            Dictionary containing index data
        """
        if self.index_file.exists():
            logger.debug(f"Loading index from {self.index_file}")
            return json.loads(self.index_file.read_text(encoding="utf-8"))

        logger.debug("Creating new index")
        return {
            "version": "1.0.0",
            "adnd_2e": {},
            "pf2e": {},
            "metadata": {
                "total_adnd_rules": 0,
                "total_pf2e_rules": 0,
                "sourcebooks_indexed": [],
            },
        }

    def _save_index(self) -> None:
        """Save the knowledge base index to disk."""
        logger.debug(f"Saving index to {self.index_file}")
        self.index_file.write_text(
            json.dumps(self.index, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def store_adnd_rule(
        self,
        rule: BaseModel,
        category: RuleCategory,
        sourcebook: ADnDSourcebook,
        rule_id: Optional[str] = None,
    ) -> str:
        """Store an AD&D 2E rule in the repository.

        Args:
            rule: Pydantic model instance containing the rule
            category: Rule category for organization
            sourcebook: Source sourcebook identifier
            rule_id: Optional unique identifier (generated if not provided)

        Returns:
            Rule identifier

        Raises:
            ValueError: If rule type doesn't match category
        """
        # Validate schema matches category
        expected_type = self.ADND_SCHEMA_REGISTRY.get(category)
        if expected_type and not isinstance(rule, expected_type):
            raise ValueError(
                f"Rule type {type(rule).__name__} doesn't match category {category}"
            )

        # Generate rule ID if not provided
        if rule_id is None:
            rule_id = self._generate_rule_id(rule, category, sourcebook.value)

        # Determine storage path
        sourcebook_dir = self.adnd_dir / sourcebook.value / category.value
        sourcebook_dir.mkdir(parents=True, exist_ok=True)
        rule_file = sourcebook_dir / f"{rule_id}.json"

        # Store rule
        logger.debug(f"Storing AD&D rule: {rule_id} in {rule_file}")
        rule_file.write_text(rule.model_dump_json(indent=2), encoding="utf-8")

        # Update index
        if sourcebook.value not in self.index["adnd_2e"]:
            self.index["adnd_2e"][sourcebook.value] = {}
        if category.value not in self.index["adnd_2e"][sourcebook.value]:
            self.index["adnd_2e"][sourcebook.value][category.value] = []

        if rule_id not in self.index["adnd_2e"][sourcebook.value][category.value]:
            self.index["adnd_2e"][sourcebook.value][category.value].append(rule_id)
            self.index["metadata"]["total_adnd_rules"] += 1

        if sourcebook.value not in self.index["metadata"]["sourcebooks_indexed"]:
            self.index["metadata"]["sourcebooks_indexed"].append(sourcebook.value)

        self._save_index()
        logger.info(f"Stored AD&D rule: {rule_id}")
        return rule_id

    def store_pf2e_rule(
        self, rule: BaseModel, category: RuleCategory, rule_id: Optional[str] = None
    ) -> str:
        """Store a PF2E rule in the repository.

        Args:
            rule: Pydantic model instance containing the rule
            category: Rule category for organization
            rule_id: Optional unique identifier (generated if not provided)

        Returns:
            Rule identifier

        Raises:
            ValueError: If rule type doesn't match category
        """
        # Validate schema matches category
        expected_type = self.PF2E_SCHEMA_REGISTRY.get(category)
        if expected_type and not isinstance(rule, expected_type):
            raise ValueError(
                f"Rule type {type(rule).__name__} doesn't match category {category}"
            )

        # Generate rule ID if not provided
        if rule_id is None:
            rule_id = self._generate_rule_id(rule, category, "pf2e")

        # Determine storage path
        category_dir = self.pf2e_dir / category.value
        category_dir.mkdir(parents=True, exist_ok=True)
        rule_file = category_dir / f"{rule_id}.json"

        # Store rule
        logger.debug(f"Storing PF2E rule: {rule_id} in {rule_file}")
        rule_file.write_text(rule.model_dump_json(indent=2), encoding="utf-8")

        # Update index
        if category.value not in self.index["pf2e"]:
            self.index["pf2e"][category.value] = []

        if rule_id not in self.index["pf2e"][category.value]:
            self.index["pf2e"][category.value].append(rule_id)
            self.index["metadata"]["total_pf2e_rules"] += 1

        self._save_index()
        logger.info(f"Stored PF2E rule: {rule_id}")
        return rule_id

    def get_adnd_rule(
        self, rule_id: str, category: RuleCategory, sourcebook: ADnDSourcebook
    ) -> Optional[BaseModel]:
        """Retrieve an AD&D 2E rule from the repository.

        Args:
            rule_id: Rule identifier
            category: Rule category
            sourcebook: Source sourcebook identifier

        Returns:
            Pydantic model instance or None if not found
        """
        rule_file = self.adnd_dir / sourcebook.value / category.value / f"{rule_id}.json"

        if not rule_file.exists():
            logger.warning(f"AD&D rule not found: {rule_id}")
            return None

        # Load and validate against schema
        schema_type = self.ADND_SCHEMA_REGISTRY.get(category)
        if not schema_type:
            logger.error(f"No schema registered for category: {category}")
            return None

        logger.debug(f"Loading AD&D rule: {rule_id} from {rule_file}")
        rule_data = json.loads(rule_file.read_text(encoding="utf-8"))
        return schema_type(**rule_data)

    def get_pf2e_rule(self, rule_id: str, category: RuleCategory) -> Optional[BaseModel]:
        """Retrieve a PF2E rule from the repository.

        Args:
            rule_id: Rule identifier
            category: Rule category

        Returns:
            Pydantic model instance or None if not found
        """
        rule_file = self.pf2e_dir / category.value / f"{rule_id}.json"

        if not rule_file.exists():
            logger.warning(f"PF2E rule not found: {rule_id}")
            return None

        # Load and validate against schema
        schema_type = self.PF2E_SCHEMA_REGISTRY.get(category)
        if not schema_type:
            logger.error(f"No schema registered for category: {category}")
            return None

        logger.debug(f"Loading PF2E rule: {rule_id} from {rule_file}")
        rule_data = json.loads(rule_file.read_text(encoding="utf-8"))
        return schema_type(**rule_data)

    def list_adnd_rules(
        self, category: Optional[RuleCategory] = None, sourcebook: Optional[ADnDSourcebook] = None
    ) -> List[str]:
        """List all AD&D 2E rule identifiers.

        Args:
            category: Optional category filter
            sourcebook: Optional sourcebook filter

        Returns:
            List of rule identifiers
        """
        rules = []

        for sb in self.index["adnd_2e"].keys():
            if sourcebook and sb != sourcebook.value:
                continue

            for cat in self.index["adnd_2e"][sb].keys():
                if category and cat != category.value:
                    continue

                rules.extend(self.index["adnd_2e"][sb][cat])

        logger.debug(f"Listed {len(rules)} AD&D rules")
        return rules

    def list_pf2e_rules(self, category: Optional[RuleCategory] = None) -> List[str]:
        """List all PF2E rule identifiers.

        Args:
            category: Optional category filter

        Returns:
            List of rule identifiers
        """
        rules = []

        for cat in self.index["pf2e"].keys():
            if category and cat != category.value:
                continue

            rules.extend(self.index["pf2e"][cat])

        logger.debug(f"Listed {len(rules)} PF2E rules")
        return rules

    def search_adnd_rules(
        self, query: str, category: Optional[RuleCategory] = None
    ) -> List[Dict[str, Any]]:
        """Search AD&D 2E rules by query string.

        Args:
            query: Search query
            category: Optional category filter

        Returns:
            List of matching rules with metadata
        """
        results = []
        query_lower = query.lower()

        for sourcebook_name in self.index["adnd_2e"].keys():
            sourcebook = ADnDSourcebook(sourcebook_name)

            for cat_name in self.index["adnd_2e"][sourcebook_name].keys():
                if category and cat_name != category.value:
                    continue

                cat = RuleCategory(cat_name)

                for rule_id in self.index["adnd_2e"][sourcebook_name][cat_name]:
                    rule = self.get_adnd_rule(rule_id, cat, sourcebook)
                    if rule and self._matches_query(rule, query_lower):
                        results.append(
                            {
                                "rule_id": rule_id,
                                "category": cat.value,
                                "sourcebook": sourcebook.value,
                                "rule": rule,
                            }
                        )

        logger.debug(f"Found {len(results)} AD&D rules matching '{query}'")
        return results

    def search_pf2e_rules(
        self, query: str, category: Optional[RuleCategory] = None
    ) -> List[Dict[str, Any]]:
        """Search PF2E rules by query string.

        Args:
            query: Search query
            category: Optional category filter

        Returns:
            List of matching rules with metadata
        """
        results = []
        query_lower = query.lower()

        for cat_name in self.index["pf2e"].keys():
            if category and cat_name != category.value:
                continue

            cat = RuleCategory(cat_name)

            for rule_id in self.index["pf2e"][cat_name]:
                rule = self.get_pf2e_rule(rule_id, cat)
                if rule and self._matches_query(rule, query_lower):
                    results.append(
                        {"rule_id": rule_id, "category": cat.value, "rule": rule}
                    )

        logger.debug(f"Found {len(results)} PF2E rules matching '{query}'")
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics.

        Returns:
            Dictionary containing repository statistics
        """
        return {
            "total_adnd_rules": self.index["metadata"]["total_adnd_rules"],
            "total_pf2e_rules": self.index["metadata"]["total_pf2e_rules"],
            "sourcebooks_indexed": self.index["metadata"]["sourcebooks_indexed"],
            "adnd_categories": list(
                set(cat for sb in self.index["adnd_2e"].values() for cat in sb.keys())
            ),
            "pf2e_categories": list(self.index["pf2e"].keys()),
        }

    def _generate_rule_id(self, rule: BaseModel, category: RuleCategory, prefix: str) -> str:
        """Generate a unique rule identifier.

        Args:
            rule: Rule model instance
            category: Rule category
            prefix: ID prefix (sourcebook or 'pf2e')

        Returns:
            Unique rule identifier
        """
        # Try to use name field if available
        name = getattr(rule, "name", None)
        if name:
            # Sanitize name for filename
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())
            return f"{prefix}_{category.value}_{safe_name}"

        # Fallback to generic ID
        import uuid

        return f"{prefix}_{category.value}_{uuid.uuid4().hex[:8]}"

    def _matches_query(self, rule: BaseModel, query_lower: str) -> bool:
        """Check if a rule matches a search query.

        Args:
            rule: Rule model instance
            query_lower: Lowercase search query

        Returns:
            True if rule matches query
        """
        # Search in name field
        name = getattr(rule, "name", "")
        if query_lower in name.lower():
            return True

        # Search in description field
        description = getattr(rule, "description", "")
        if query_lower in description.lower():
            return True

        # Search in tags if available
        tags = getattr(rule, "tags", [])
        if any(query_lower in tag.lower() for tag in tags):
            return True

        return False

