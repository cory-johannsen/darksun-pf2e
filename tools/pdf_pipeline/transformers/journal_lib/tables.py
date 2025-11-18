"""
Table building and processing for journal transformation.

This module handles table construction from PDF cells and rows.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Sequence

from .utilities import compute_bbox_from_cells, cluster_positions, join_fragments

# Create alias for backward compatibility
_cluster_positions = cluster_positions
_join_fragments = join_fragments


def build_matrix_from_cells(
    cells: Sequence[dict],
    *,
    expected_columns: int | None = None,
    row_tolerance: float = 2.5,
    column_tolerance: float = 6.0,
) -> List[List[str]]:
    if not cells:
        return []

    row_centers = _cluster_positions([cell["bbox"][1] for cell in cells], row_tolerance)
    column_centers = _cluster_positions([cell["bbox"][0] for cell in cells], column_tolerance)

    if expected_columns is not None and column_centers and len(column_centers) != expected_columns:
        # Attempt to reconcile by merging closest columns until counts match.
        while len(column_centers) > expected_columns:
            deltas = [column_centers[i + 1] - column_centers[i] for i in range(len(column_centers) - 1)]
            merge_idx = deltas.index(min(deltas))
            merged_value = (column_centers[merge_idx] + column_centers[merge_idx + 1]) / 2
            column_centers = column_centers[:merge_idx] + [merged_value] + column_centers[merge_idx + 2 :]
        # If there are still fewer columns than expected, we accept the detected count to avoid empty columns.

    matrix: List[List[List[str]]] = [
        [[] for _ in range(len(column_centers))] for _ in range(len(row_centers))
    ]

    for cell in cells:
        bbox = cell["bbox"]
        row_idx = 0 if not row_centers else min(
            range(len(row_centers)), key=lambda i: abs(bbox[1] - row_centers[i])
        )
        col_idx = 0 if not column_centers else min(
            range(len(column_centers)), key=lambda i: abs(bbox[0] - column_centers[i])
        )
        matrix[row_idx][col_idx].append(cell["text"])

    rows: List[List[str]] = []
    for row_cells in matrix:
        row: List[str] = []
        for fragments in row_cells:
            if not fragments:
                row.append("")
            else:
                row.append(_join_fragments(fragments))
        rows.append(row)
    return rows




def table_from_rows(rows: Sequence[Sequence[str]], *, header_rows: int = 1, bbox: Sequence[float] | None = None) -> dict:
    table_rows = []
    for row in rows:
        table_rows.append({"cells": [{"text": cell} for cell in row]})
    table: dict = {"rows": table_rows}
    if bbox:
        table["bbox"] = list(bbox)
    if header_rows:
        table["header_rows"] = header_rows
    return table




