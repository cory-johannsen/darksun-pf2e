"""PF2E MCP client wrapper for rule lookups.

This module provides a client interface for querying PF2E rules via the MCP server
and caching results locally to improve performance.

Requirements:
- SWENG-1: Single Responsibility Principle
- SWENG-6: Test-driven development pattern
- SWENG-7: All functions MUST have automated unit tests
- PY-6: Console logs tracing execution
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from .knowledge_repository import KnowledgeRepository, RuleCategory
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


class PF2EMCPClient:
    """Client for querying PF2E rules via MCP server with local caching.

    This client wraps MCP server calls and provides caching to reduce
    redundant queries. Results are stored in the knowledge repository.
    """

    def __init__(self, cache_dir: Path, mcp_server: str = "p2fe"):
        """Initialize the PF2E MCP client.

        Args:
            cache_dir: Directory for caching query results
            mcp_server: MCP server identifier
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mcp_server = mcp_server

        # Initialize knowledge repository for PF2E rules
        self.repo = KnowledgeRepository(self.cache_dir.parent)

        logger.info(f"Initialized PF2E MCP client with cache at {self.cache_dir}")

    def query_ability_scores(self) -> List[PF2EAbilityScore]:
        """Query PF2E ability score information.

        Returns:
            List of PF2E ability scores
        """
        logger.debug("Querying PF2E ability scores")

        # Check cache first
        cached = self._get_cached_query("ability_scores", RuleCategory.ABILITY_SCORES)
        if cached:
            return cached

        # Query via MCP (placeholder - real implementation would use MCP tools)
        # For now, return structured placeholder data
        ability_scores = self._create_default_ability_scores()

        # Cache results
        self._cache_query_results(
            "ability_scores", RuleCategory.ABILITY_SCORES, ability_scores
        )

        return ability_scores

    def query_saves(self) -> List[PF2ESave]:
        """Query PF2E saving throw information.

        Returns:
            List of PF2E saves
        """
        logger.debug("Querying PF2E saves")

        # Check cache first
        cached = self._get_cached_query("saves", RuleCategory.SAVES)
        if cached:
            return cached

        # Query via MCP (placeholder)
        saves = self._create_default_saves()

        # Cache results
        self._cache_query_results("saves", RuleCategory.SAVES, saves)

        return saves

    def query_skills(self) -> List[PF2ESkill]:
        """Query PF2E skill information.

        Returns:
            List of PF2E skills
        """
        logger.debug("Querying PF2E skills")

        # Check cache first
        cached = self._get_cached_query("skills", RuleCategory.SKILLS)
        if cached:
            return cached

        # Query via MCP (placeholder)
        skills = self._create_default_skills()

        # Cache results
        self._cache_query_results("skills", RuleCategory.SKILLS, skills)

        return skills

    def query_actions(self, query: str) -> List[PF2EAction]:
        """Query PF2E actions by search string.

        Args:
            query: Search query

        Returns:
            List of matching actions
        """
        logger.debug(f"Querying PF2E actions: {query}")

        # Check cache first
        cache_key = f"actions_{query}"
        cached = self._get_cached_query(cache_key, RuleCategory.ACTIONS)
        if cached:
            return cached

        # Query via MCP (placeholder)
        actions = []

        # Cache results
        self._cache_query_results(cache_key, RuleCategory.ACTIONS, actions)

        return actions

    def query_spells(self, query: str, rank: Optional[int] = None) -> List[PF2ESpell]:
        """Query PF2E spells by search string and optional rank.

        Args:
            query: Search query
            rank: Optional spell rank filter

        Returns:
            List of matching spells
        """
        logger.debug(f"Querying PF2E spells: {query} (rank={rank})")

        # Check cache first
        cache_key = f"spells_{query}_{rank}" if rank else f"spells_{query}"
        cached = self._get_cached_query(cache_key, RuleCategory.SPELLS)
        if cached:
            return cached

        # Query via MCP (placeholder)
        spells = []

        # Cache results
        self._cache_query_results(cache_key, RuleCategory.SPELLS, spells)

        return spells

    def query_feats(self, query: str, level: Optional[int] = None) -> List[PF2EFeat]:
        """Query PF2E feats by search string and optional level.

        Args:
            query: Search query
            level: Optional feat level filter

        Returns:
            List of matching feats
        """
        logger.debug(f"Querying PF2E feats: {query} (level={level})")

        # Check cache first
        cache_key = f"feats_{query}_{level}" if level else f"feats_{query}"
        cached = self._get_cached_query(cache_key, RuleCategory.FEATS)
        if cached:
            return cached

        # Query via MCP (placeholder)
        feats = []

        # Cache results
        self._cache_query_results(cache_key, RuleCategory.FEATS, feats)

        return feats

    def query_traits(self, query: str) -> List[PF2ETrait]:
        """Query PF2E traits by search string.

        Args:
            query: Search query

        Returns:
            List of matching traits
        """
        logger.debug(f"Querying PF2E traits: {query}")

        # Check cache first
        cache_key = f"traits_{query}"
        cached = self._get_cached_query(cache_key, RuleCategory.TRAITS)
        if cached:
            return cached

        # Query via MCP (placeholder)
        traits = []

        # Cache results
        self._cache_query_results(cache_key, RuleCategory.TRAITS, traits)

        return traits

    def _get_cached_query(
        self, cache_key: str, category: RuleCategory
    ) -> Optional[List[Any]]:
        """Retrieve cached query results.

        Args:
            cache_key: Cache key
            category: Rule category

        Returns:
            Cached results or None
        """
        cache_file = self.cache_dir / category.value / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            cache_data = json.loads(cache_file.read_text(encoding="utf-8"))
            cached_query = PF2ECachedQuery(**cache_data)

            logger.debug(f"Cache hit for {cache_key}")

            # Reconstruct objects from cached results
            schema_type = self._get_schema_type(category)
            if schema_type:
                return [schema_type(**result) for result in cached_query.results]

            return cached_query.results

        except Exception as e:
            logger.warning(f"Error loading cache for {cache_key}: {e}")
            return None

    def _cache_query_results(
        self, cache_key: str, category: RuleCategory, results: List[Any]
    ) -> None:
        """Cache query results to disk.

        Args:
            cache_key: Cache key
            category: Rule category
            results: Query results to cache
        """
        cache_file = self.cache_dir / category.value / f"{cache_key}.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert results to dicts
        result_dicts = [
            r.model_dump() if hasattr(r, "model_dump") else r for r in results
        ]

        cached_query = PF2ECachedQuery(
            query=cache_key,
            category=category.value,
            results=result_dicts,
            timestamp=datetime.utcnow().isoformat(),
            source=self.mcp_server,
        )

        cache_file.write_text(
            cached_query.model_dump_json(indent=2), encoding="utf-8"
        )

        logger.debug(f"Cached {len(results)} results for {cache_key}")

    def _get_schema_type(self, category: RuleCategory) -> Optional[type]:
        """Get the Pydantic schema type for a category.

        Args:
            category: Rule category

        Returns:
            Schema type or None
        """
        schema_map = {
            RuleCategory.ABILITY_SCORES: PF2EAbilityScore,
            RuleCategory.SAVES: PF2ESave,
            RuleCategory.SKILLS: PF2ESkill,
            RuleCategory.ACTIONS: PF2EAction,
            RuleCategory.SPELLS: PF2ESpell,
            RuleCategory.FEATS: PF2EFeat,
            RuleCategory.TRAITS: PF2ETrait,
            RuleCategory.CLASSES: PF2EClass,
        }
        return schema_map.get(category)

    def _create_default_ability_scores(self) -> List[PF2EAbilityScore]:
        """Create default PF2E ability score data.

        Returns:
            List of default ability scores
        """
        abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        return [
            PF2EAbilityScore(
                ability=ability,
                modifier=0,
                description=f"{ability} represents {self._get_ability_description(ability)}",
                source="PF2E Core Rulebook",
            )
            for ability in abilities
        ]

    def _create_default_saves(self) -> List[PF2ESave]:
        """Create default PF2E save data.

        Returns:
            List of default saves
        """
        return [
            PF2ESave(
                save_type="Fortitude",
                ability="CON",
                description="Fortitude saves represent your ability to withstand physical punishment",
                source="PF2E Core Rulebook",
            ),
            PF2ESave(
                save_type="Reflex",
                ability="DEX",
                description="Reflex saves represent your ability to dodge and evade",
                source="PF2E Core Rulebook",
            ),
            PF2ESave(
                save_type="Will",
                ability="WIS",
                description="Will saves represent your mental fortitude",
                source="PF2E Core Rulebook",
            ),
        ]

    def _create_default_skills(self) -> List[PF2ESkill]:
        """Create default PF2E skill data.

        Returns:
            List of default skills
        """
        skills = [
            ("Acrobatics", "DEX"),
            ("Arcana", "INT"),
            ("Athletics", "STR"),
            ("Crafting", "INT"),
            ("Deception", "CHA"),
            ("Diplomacy", "CHA"),
            ("Intimidation", "CHA"),
            ("Medicine", "WIS"),
            ("Nature", "WIS"),
            ("Occultism", "INT"),
            ("Performance", "CHA"),
            ("Religion", "WIS"),
            ("Society", "INT"),
            ("Stealth", "DEX"),
            ("Survival", "WIS"),
            ("Thievery", "DEX"),
        ]

        return [
            PF2ESkill(
                name=name,
                ability=ability,
                description=f"{name} skill based on {ability}",
                source="PF2E Core Rulebook",
            )
            for name, ability in skills
        ]

    def _get_ability_description(self, ability: str) -> str:
        """Get description for an ability.

        Args:
            ability: Ability name

        Returns:
            Description string
        """
        descriptions = {
            "STR": "physical power",
            "DEX": "agility and reflexes",
            "CON": "hardiness and health",
            "INT": "reasoning and memory",
            "WIS": "awareness and intuition",
            "CHA": "force of personality",
        }
        return descriptions.get(ability, "unknown")


class PF2ECacheInitializer(BaseProcessor):
    """Processor for initializing PF2E rule cache from MCP.

    This processor pre-populates the cache with commonly needed PF2E rules
    to improve performance of the conversion stage.
    """

    def process(
        self, input_data: ProcessorInput, context: ExecutionContext
    ) -> ProcessorOutput:
        """Initialize PF2E cache with base rules.

        Args:
            input_data: Input containing cache configuration
            context: Execution context

        Returns:
            ProcessorOutput with cache initialization results
        """
        cache_dir = Path(self.config.get("cache_dir", "data/knowledge_base/pf2e_cache"))
        mcp_server = self.config.get("mcp_server", "p2fe")
        initial_queries = self.config.get(
            "initial_queries", ["ability_scores", "saving_throws", "skills"]
        )

        logger.info(f"Initializing PF2E cache at {cache_dir}")

        # Initialize client
        client = PF2EMCPClient(cache_dir, mcp_server)

        cached_items = 0

        # Run initial queries
        for query in initial_queries:
            try:
                if query == "ability_scores":
                    results = client.query_ability_scores()
                    cached_items += len(results)
                elif query == "saving_throws":
                    results = client.query_saves()
                    cached_items += len(results)
                elif query == "skills":
                    results = client.query_skills()
                    cached_items += len(results)
                elif query == "combat_actions":
                    results = client.query_actions("combat")
                    cached_items += len(results)
                else:
                    logger.warning(f"Unknown query type: {query}")

                context.items_processed += 1
                logger.info(f"Cached {len(results)} items for {query}")

            except Exception as e:
                error_msg = f"Error caching {query}: {e}"
                context.errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        return ProcessorOutput(
            data={"cached_items": cached_items, "cache_dir": str(cache_dir)},
            metadata={"initial_queries": initial_queries},
        )

