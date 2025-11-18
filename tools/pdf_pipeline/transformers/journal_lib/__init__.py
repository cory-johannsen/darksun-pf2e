"""
Journal transformation sub-package.

This package contains journal HTML transformation and rendering functions.
"""

# Re-export utility functions
from .utilities import (
    normalize_plain_text,
    merge_fragments,
    join_fragments,
    sanitize_plain_text,
    cluster_positions,
    compute_bbox_from_cells,
    is_bold,
    is_italic,
    wrap_span,
    dehyphenate_text,
)

# Re-export block processing
from .blocks import collect_cells_from_blocks

# Re-export table functions
from .tables import (
    build_matrix_from_cells,
    table_from_rows,
)

# Re-export rendering functions
from .rendering import (
    merge_adjacent_paragraph_html,
    render_line,
    render_text_block,
    render_table,
    render_page,
    render_pages,
)

# Re-export TOC functions
from .toc import (
    generate_table_of_contents,
    fix_chapter_6_armor_headers_after_anchoring,
    apply_subheader_styling,
    add_header_anchors,
)

__all__ = [
    # Utilities
    "normalize_plain_text",
    "merge_fragments",
    "join_fragments",
    "sanitize_plain_text",
    "cluster_positions",
    "compute_bbox_from_cells",
    "is_bold",
    "is_italic",
    "wrap_span",
    "dehyphenate_text",
    # Blocks
    "collect_cells_from_blocks",
    # Tables
    "build_matrix_from_cells",
    "table_from_rows",
    # Rendering
    "merge_adjacent_paragraph_html",
    "render_line",
    "render_text_block",
    "render_table",
    "render_page",
    "render_pages",
    # TOC
    "generate_table_of_contents",
    "fix_chapter_6_armor_headers_after_anchoring",
    "apply_subheader_styling",
    "add_header_anchors",
]

