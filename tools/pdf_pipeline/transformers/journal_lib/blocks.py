"""
Block processing for journal transformation.

This module handles PDF block collection and processing.
"""

from __future__ import annotations

from typing import List, Dict, Any, Sequence

from .utilities import normalize_plain_text

# Create alias for backward compatibility
_normalize_plain_text = normalize_plain_text


def collect_cells_from_blocks(page: dict, block_indices: Sequence[int]) -> List[dict]:
    cells: List[dict] = []
    blocks = page.get("blocks", [])
    for idx in block_indices:
        if idx < 0 or idx >= len(blocks):
            continue
        block = blocks[idx]
        for line in block.get("lines", []):
            raw_text = "".join(span.get("text", "") for span in line.get("spans", []))
            text = _normalize_plain_text(raw_text)
            if not text:
                continue
            bbox = [float(coord) for coord in line.get("bbox", [0, 0, 0, 0])]
            cells.append({"text": text, "bbox": bbox, "block_index": idx})
    return cells




