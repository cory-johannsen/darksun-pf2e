"""Chapter 10 (Treasure) specific processing logic."""

from .common import (
    normalize_plain_text,
    is_header_block,
)
from .tables import (
    extract_lair_treasures_table,
)

__all__ = [
    'normalize_plain_text',
    'is_header_block',
    'extract_lair_treasures_table',
]

