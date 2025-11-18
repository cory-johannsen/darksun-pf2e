"""Section extraction utilities for the Dark Sun parsing pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple

import fitz
import pdfplumber

from .models import (
    Block,
    ImageData,
    Line,
    Manifest,
    Page,
    Section,
    Span,
    StructuredSection,
    Table,
    TableCell,
    TableRow,
)

DEFAULT_TABLE_SETTINGS: Dict[str, object] = {
    "vertical_strategy": "lines",
    "horizontal_strategy": "lines",
    "intersection_tolerance": 5,
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 1,
    "min_words_horizontal": 1,
}


def _iter_sections(
    sections: Sequence[Section],
    parent_chain: Tuple[str, ...] = (),
) -> Iterator[Tuple[Section, Tuple[str, ...]]]:
    for section in sections:
        chain = parent_chain + (section.slug,)
        yield section, parent_chain
        if section.children:
            yield from _iter_sections(section.children, chain)


def _serialize_blocks(blocks: Iterable[tuple]) -> List[dict]:
    serialized = []
    for block in blocks:
        if len(block) < 5:
            continue
        x0, y0, x1, y1, text = block[:5]
        attrs = {}
        if len(block) >= 6:
            attrs["number"] = block[5]
        if len(block) >= 7:
            attrs["type"] = block[6]
        serialized.append(
            {
                "bbox": [x0, y0, x1, y1],
                "text": text.strip(),
                **attrs,
            }
        )
    return serialized

def _color_to_hex(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)) and len(value) >= 3:
        channels = [max(0, min(255, int(round(c * 255 if isinstance(c, float) else c)))) for c in value[:3]]
    elif isinstance(value, (int, float)):
        if isinstance(value, float):
            channel = max(0, min(255, int(round(value * 255))))
            channels = [channel, channel, channel]
        else:
            channels = [(value >> shift) & 0xFF for shift in (16, 8, 0)]
    else:
        return None
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def _span_text(span: dict) -> str:
    text = span.get("text") or ""
    if text:
        return text
    chars = span.get("chars")
    if chars:
        return "".join(char.get("c", "") for char in chars)
    return ""


def _detect_columns(blocks: List[Block], page_width: float) -> int:
    """Detect if page has multiple columns based on block distribution.
    
    Args:
        blocks: List of blocks to analyze
        page_width: Width of the page
        
    Returns:
        Number of columns detected (1 or 2)
    """
    # Get X-coordinates of text blocks
    text_blocks = [b for b in blocks if b.type == "text" and b.lines]
    if len(text_blocks) < 4:
        return 1
    
    # Calculate horizontal center of each block
    block_centers = [(b.bbox[0] + b.bbox[2]) / 2 for b in text_blocks]
    
    # Find the median center position
    sorted_centers = sorted(block_centers)
    median_center = sorted_centers[len(sorted_centers) // 2]
    
    # Count blocks significantly left vs right of page center
    page_center = page_width / 2
    left_blocks = sum(1 for c in block_centers if c < page_center - 30)
    right_blocks = sum(1 for c in block_centers if c > page_center + 30)
    
    # If we have significant blocks on both sides, it's two columns
    if left_blocks >= 2 and right_blocks >= 2:
        return 2
    
    return 1


def _sort_blocks_by_columns(blocks: List[Block], page_width: float) -> List[Block]:
    """Sort blocks for proper reading order, handling multi-column layouts.
    
    Args:
        blocks: List of blocks to sort
        page_width: Width of the page
        
    Returns:
        Sorted list of blocks
    """
    if not blocks:
        return blocks
    
    # Detect number of columns
    num_columns = _detect_columns(blocks, page_width)
    
    if num_columns == 1:
        # Single column: sort by Y-position (top to bottom)
        return sorted(blocks, key=lambda b: b.bbox[1])
    
    # Two columns: sort by column first, then Y-position
    page_center = page_width / 2
    
    # Separate blocks into left and right columns
    left_column = []
    right_column = []
    
    for block in blocks:
        # Use the horizontal center of the block to determine column
        block_center_x = (block.bbox[0] + block.bbox[2]) / 2
        
        if block_center_x < page_center:
            left_column.append(block)
        else:
            right_column.append(block)
    
    # Sort each column by Y-position (top to bottom)
    left_column.sort(key=lambda b: b.bbox[1])
    right_column.sort(key=lambda b: b.bbox[1])
    
    # Concatenate: left column first, then right column
    return left_column + right_column


def _split_multicolumn_blocks(blocks: List[Block], page_width: float) -> List[Block]:
    """Split blocks that span multiple columns into separate blocks.
    
    PyMuPDF sometimes groups lines from different columns into the same block.
    This function splits such blocks so each resulting block contains only lines
    from a single column.
    
    Args:
        blocks: List of blocks to process
        page_width: Width of the page
        
    Returns:
        List of blocks with multi-column blocks split
    """
    result: List[Block] = []
    page_center = page_width / 2
    
    for block in blocks:
        if block.type != "text" or not block.lines:
            result.append(block)
            continue
        
        # Check if block has lines in both columns
        left_lines = []
        right_lines = []
        
        for line in block.lines:
            line_center_x = (line.bbox[0] + line.bbox[2]) / 2
            if line_center_x < page_center:
                left_lines.append(line)
            else:
                right_lines.append(line)
        
        # If block only has lines in one column, keep it as is
        if not left_lines or not right_lines:
            result.append(block)
            continue
        
        # Split into two blocks - one for each column
        if left_lines:
            # Calculate bbox for left block
            left_x0 = min(line.bbox[0] for line in left_lines)
            left_y0 = min(line.bbox[1] for line in left_lines)
            left_x1 = max(line.bbox[2] for line in left_lines)
            left_y1 = max(line.bbox[3] for line in left_lines)
            result.append(Block(
                bbox=[left_x0, left_y0, left_x1, left_y1],
                type="text",
                lines=left_lines
            ))
        
        if right_lines:
            # Calculate bbox for right block
            right_x0 = min(line.bbox[0] for line in right_lines)
            right_y0 = min(line.bbox[1] for line in right_lines)
            right_x1 = max(line.bbox[2] for line in right_lines)
            right_y1 = max(line.bbox[3] for line in right_lines)
            result.append(Block(
                bbox=[right_x0, right_y0, right_x1, right_y1],
                type="text",
                lines=right_lines
            ))
    
    return result


def _structured_blocks(page_dict: dict, page_width: float = 612.0) -> List[Block]:
    """Extract and sort blocks from page dictionary.
    
    Args:
        page_dict: Raw page dictionary from PyMuPDF
        page_width: Width of the page for column detection
        
    Returns:
        Sorted list of blocks in reading order
    """
    structured_blocks: List[Block] = []
    for block in page_dict.get("blocks", []):
        block_type = block.get("type", 0)
        bbox = [float(coord) for coord in block.get("bbox", [])]
        if block_type == 0:
            lines: List[Line] = []
            for line in block.get("lines", []):
                spans: List[Span] = []
                for span in line.get("spans", []):
                    text_content = _span_text(span)
                    spans.append(
                        Span(
                            text=text_content,
                            font=span.get("font"),
                            size=span.get("size"),
                            flags=span.get("flags"),
                            color=_color_to_hex(span.get("color")),
                            ascender=span.get("ascender"),
                            descender=span.get("descender"),
                        )
                    )
                lines.append(Line(bbox=[float(coord) for coord in line.get("bbox", [])], spans=spans))
            structured_blocks.append(Block(bbox=bbox, type="text", lines=lines))
        elif block_type == 1:
            image = ImageData(
                xref=block.get("xref"),
                name=block.get("name"),
                width=block.get("width"),
                height=block.get("height"),
                colorspace=block.get("cs-name"),
                ext=block.get("ext"),
            )
            structured_blocks.append(Block(bbox=bbox, type="image", image=image))
        else:
            structured_blocks.append(Block(bbox=bbox, type="vector"))
    
    # Split blocks that span multiple columns
    structured_blocks = _split_multicolumn_blocks(structured_blocks, page_width)
    
    # Sort blocks by columns for proper reading order
    return _sort_blocks_by_columns(structured_blocks, page_width)


def _structured_tables(plumber_page, *, table_settings: Dict[str, object]) -> List[Table]:
    tables: List[Table] = []
    for table in plumber_page.find_tables(table_settings=table_settings):
        if not table.cells:
            continue
        cell_map = {(cell.row, cell.col): cell for cell in table.cells}
        row_indices = sorted({cell.row for cell in table.cells})
        col_indices = sorted({cell.col for cell in table.cells})
        rows: List[TableRow] = []
        for row_idx in row_indices:
            cells: List[TableCell] = []
            for col_idx in col_indices:
                cell = cell_map.get((row_idx, col_idx))
                if cell is None:
                    continue
                cells.append(
                    TableCell(
                        text=cell.text,
                        bbox=[float(coord) for coord in cell.bbox],
                        rowspan=getattr(cell, "rowspan", 1) or 1,
                        colspan=getattr(cell, "colspan", 1) or 1,
                    )
                )
            if cells:
                rows.append(TableRow(cells=cells))
        if rows:
            tables.append(Table(bbox=[float(coord) for coord in table.bbox], rows=rows))
    return tables


def _extract_structured_section(
    doc: fitz.Document,
    plumber_doc: pdfplumber.PDF,
    section: Section,
    parents: Tuple[str, ...],
    *,
    table_settings: Dict[str, object],
) -> StructuredSection:
    pages: List[Page] = []
    for page_number in section.page_span:
        page = doc[page_number - 1]
        plumber_page = plumber_doc.pages[page_number - 1]
        raw_dict = page.get_text("rawdict")
        # Pass page width for column detection and sorting
        blocks = _structured_blocks(raw_dict, page_width=page.rect.width)
        tables = _structured_tables(plumber_page, table_settings=table_settings)
        pages.append(
            Page(
                page_number=page_number,
                width=page.rect.width,
                height=page.rect.height,
                rotation=page.rotation,
                blocks=blocks,
                tables=tables,
            )
        )

    return StructuredSection(
        title=section.title,
        slug=section.slug,
        level=section.level,
        start_page=section.start_page,
        end_page=section.end_page,
        parent_slugs=list(parents),
        pages=pages,
    )


def extract_sections(
    manifest: Manifest,
    *,
    output_dir: Path,
    min_level: int = 2,
    include_blocks: bool = True,
    mode: str = "legacy",
    table_settings: Dict[str, object] | None = None,
) -> List[Path]:
    """Extract section content according to a manifest.

    Parameters
    ----------
    manifest:
        Parsed manifest describing available sections.
    output_dir:
        Directory where extracted JSON files will be written.
    min_level:
        Minimum section depth to export from the manifest (default: 2).
    include_blocks:
        Legacy-mode flag to include basic block metadata in output.
    mode:
        Extraction mode. ``"legacy"`` mimics the previous pipeline, ``"structured"``
        captures span-level layout data suitable for faithful HTML reconstruction.
    table_settings:
        Optional overrides passed to the table detection helper when ``mode`` is
        ``"structured"``. Falls back to sensible defaults when unset.
    """

    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = Path(manifest.pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    written_files: List[Path] = []

    if mode not in {"legacy", "structured"}:
        raise ValueError(f"Unsupported extraction mode '{mode}'")

    if mode == "legacy":
        with fitz.open(pdf_path) as doc:
            for section, parents in _iter_sections(manifest.sections):
                if section.level < min_level:
                    continue

                pages = []
                for page_number in section.page_span:
                    page = doc[page_number - 1]
                    page_entry = {
                        "page_number": page_number,
                        "text": page.get_text("text"),
                    }
                    if include_blocks:
                        page_entry["blocks"] = _serialize_blocks(page.get_text("blocks"))
                    pages.append(page_entry)

                data = {
                    "title": section.title,
                    "slug": section.slug,
                    "level": section.level,
                    "start_page": section.start_page,
                    "end_page": section.end_page,
                    "parent_slugs": list(parents),
                    "pages": pages,
                }

                filename = f"{section.level:02d}-{section.start_page:03d}-{section.slug}.json"
                output_path = output_dir / filename
                output_path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                written_files.append(output_path)
    else:
        settings = DEFAULT_TABLE_SETTINGS.copy()
        if table_settings:
            settings.update(table_settings)

        with fitz.open(pdf_path) as doc, pdfplumber.open(str(pdf_path)) as plumber_doc:
            for section, parents in _iter_sections(manifest.sections):
                if section.level < min_level:
                    continue

                structured_section = _extract_structured_section(
                    doc,
                    plumber_doc,
                    section,
                    parents,
                    table_settings=settings,
                )

                filename = f"{section.level:02d}-{section.start_page:03d}-{section.slug}.json"
                output_path = output_dir / filename
                output_path.write_text(
                    json.dumps(structured_section.model_dump(), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                written_files.append(output_path)

    return written_files

