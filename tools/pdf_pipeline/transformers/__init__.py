"""Transformation registry for converting raw PDF sections into PF2E entities."""

from __future__ import annotations

from typing import Callable, Dict

from .ancestries import transform as transform_ancestries
from .journal_v2 import transform as transform_journal_v2

Transformer = Callable[..., dict]


REGISTRY: Dict[str, Transformer] = {
    "ancestries": transform_ancestries,
    "journal_v2": transform_journal_v2,
}


__all__ = ["REGISTRY"]

