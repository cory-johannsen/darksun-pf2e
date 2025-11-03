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


def _structured_blocks(page_dict: dict) -> List[Block]:
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
    return structured_blocks


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
        blocks = _structured_blocks(raw_dict)
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

