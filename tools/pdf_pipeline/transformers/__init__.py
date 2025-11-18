"""Transformation registry for converting raw PDF sections into PF2E entities."""

from __future__ import annotations

from typing import Callable, Dict

from .ancestries import transform as transform_ancestries
from .journal import transform as transform_journal

Transformer = Callable[..., dict]


REGISTRY: Dict[str, Transformer] = {
    "ancestries": transform_ancestries,
    "journal": transform_journal,
}


__all__ = ["REGISTRY"]

