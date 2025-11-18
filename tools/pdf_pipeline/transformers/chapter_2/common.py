"""
Common utility functions for Chapter 2 processing.

This module contains shared utility functions used across all race-specific processors.
"""

from ..journal import _normalize_plain_text


def update_block_bbox(block: dict) -> None:
    """Update block bbox based on its lines."""
    lines = block.get("lines", [])
    if not lines:
        return
    x0 = min(float(line.get("bbox", [0, 0, 0, 0])[0]) for line in lines)
    y0 = min(float(line.get("bbox", [0, 0, 0, 0])[1]) for line in lines)
    x1 = max(float(line.get("bbox", [0, 0, 0, 0])[2]) for line in lines)
    y1 = max(float(line.get("bbox", [0, 0, 0, 0])[3]) for line in lines)
    block["bbox"] = [x0, y0, x1, y1]


def find_block(page: dict, predicate) -> tuple[int, dict] | None:
    """Find a block in a page that matches the predicate."""
    for idx, block in enumerate(page.get("blocks", [])):
        texts = [
            _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", [])))
            for line in block.get("lines", [])
        ]
        if predicate(texts):
            return idx, block
    return None

