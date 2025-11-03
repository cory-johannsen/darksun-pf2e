"""Layout-aware journal transformer for structured Dark Sun sections."""

from __future__ import annotations

import html
import re
from copy import deepcopy
from statistics import median
from typing import Iterable, List, Sequence

_WHITESPACE_RE = re.compile(r"\s+")
_TAG_RE = re.compile(r"<.*?>", re.DOTALL)
_PARAGRAPH_RE = re.compile(r"(<p>.*?</p>)", re.DOTALL)
_SPACED_LETTERS_RE = re.compile(r"((?:\b[A-Za-z]\b\s*){2,})")
_SPACED_DIGITS_RE = re.compile(r"((?:\b\d\b\s*){2,})")


def _normalize_plain_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\u00ad", " ")  # soft hyphen becomes space to avoid word splice
    text = text.replace("\u0097", " -- ")
    text = text.replace("\u2014", " -- ")
    text = text.replace("\u0091", "'")
    text = text.replace("\u0092", "'")
    text = text.replace("\u2018", "'")
    text = text.replace("\u2019", "'")
    text = text.replace("\u0093", '"')
    text = text.replace("\u0094", '"')
    text = text.replace("\u201c", '"')
    text = text.replace("\u201d", '"')
    text = text.replace("\u0082", ", ")
    text = text.replace("\u201a", ", ")
    text = text.replace("\xa0", " ")
    text = _WHITESPACE_RE.sub(" ", text)
    text = _SPACED_LETTERS_RE.sub(lambda match: match.group(0).replace(" ", ""), text)
    text = _SPACED_DIGITS_RE.sub(lambda match: match.group(0).replace(" ", ""), text)
    text = re.sub(r"-\s+(\d)", r"-\1", text)
    return text.strip()


def _merge_fragments(fragments: List[str]) -> List[str]:
    merged: List[str] = []
    for fragment in fragments:
        if not fragment:
            continue
        if merged:
            prev = merged[-1]
            if prev.endswith("-") and not prev.endswith("--") and fragment:
                if fragment[0].islower():
                    merged[-1] = prev[:-1] + fragment
                    continue
                merged[-1] = prev[:-1] + " " + fragment
                continue
        merged.append(fragment)
    return merged


def _join_fragments(merged: List[str]) -> str:
    if not merged:
        return ""
    text = merged[0]
    for fragment in merged[1:]:
        needs_space = True
        if text.endswith((" ", "--", "(", "[", "{", "\u2014")):
            needs_space = False
        if fragment.startswith((" ", ",", ".", ";", ":", "?", "!", "'", ")")):
            needs_space = False
        if needs_space:
            text += " "
        text += fragment
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def _merge_adjacent_paragraph_html(html_fragment: str) -> str:
    if "<p" not in html_fragment:
        return html_fragment

    segments = []
    pos = 0
    for match in _PARAGRAPH_RE.finditer(html_fragment):
        start, end = match.span()
        if start > pos:
            segments.append(("text", html_fragment[pos:start]))
        segments.append(("p", match.group(1)))
        pos = end
    if pos < len(html_fragment):
        segments.append(("text", html_fragment[pos:]))

    result: List[tuple[str, str]] = []
    plains: List[str] = []

    for kind, content in segments:
        if kind != "p":
            result.append((kind, content))
            continue

        inner = content[3:-4]
        plain = html.unescape(_TAG_RE.sub("", inner)).strip()

        prev_plain_text = plains[-1] if plains else ""
        prev_heading = prev_plain_text.strip().endswith(":")

        if (
            result
            and result[-1][0] == "p"
            and plain
            and prev_plain_text
            and plain[0].islower()
            and not prev_plain_text.endswith((".", "!", "?", ";"))
            and not prev_heading
            and "<span" not in content
            and "<span" not in result[-1][1]
        ):
            merged_fragments = _merge_fragments([plains[-1], plain])
            combined_text = _join_fragments(merged_fragments)
            new_html = f"<p>{html.escape(combined_text)}</p>"
            result[-1] = ("p", new_html)
            plains[-1] = combined_text
            continue

        result.append((kind, content))
        plains.append(plain)

    return "".join(fragment for _, fragment in result)


def _sanitize_plain_text(value: str) -> str:
    return (
        value.replace("\u0091", "'")
        .replace("\u0092", "'")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u0093", '"')
        .replace("\u0094", '"')
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u0082", ",")
        .replace("\u201a", ",")
    )


def _cluster_positions(values: Sequence[float], tolerance: float) -> List[float]:
    if not values:
        return []
    sorted_values = sorted(values)
    clusters: List[List[float]] = [[sorted_values[0]]]
    for value in sorted_values[1:]:
        if abs(value - clusters[-1][-1]) <= tolerance:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    return [sum(cluster) / len(cluster) for cluster in clusters]


def _collect_cells_from_blocks(page: dict, block_indices: Sequence[int]) -> List[dict]:
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


def _build_matrix_from_cells(
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


def _table_from_rows(rows: Sequence[Sequence[str]], *, header_rows: int = 1, bbox: Sequence[float] | None = None) -> dict:
    table_rows = []
    for row in rows:
        table_rows.append({"cells": [{"text": cell} for cell in row]})
    table: dict = {"rows": table_rows}
    if bbox:
        table["bbox"] = list(bbox)
    if header_rows:
        table["header_rows"] = header_rows
    return table


def _compute_bbox_from_cells(cells: Sequence[dict]) -> List[float]:
    min_x = min(cell["bbox"][0] for cell in cells)
    min_y = min(cell["bbox"][1] for cell in cells)
    max_x = max(cell["bbox"][2] for cell in cells)
    max_y = max(cell["bbox"][3] for cell in cells)
    return [min_x, min_y, max_x, max_y]


# Chapter-specific adjustments have been moved to separate processing modules


def _is_bold(font_name: str | None, flags: int | None) -> bool:
    if not font_name:
        return False
    lowered = font_name.lower()
    return any(keyword in lowered for keyword in ("bold", "black", "heavy"))


def _is_italic(font_name: str | None, flags: int | None) -> bool:
    if not font_name:
        return False
    lowered = font_name.lower()
    return any(keyword in lowered for keyword in ("italic", "oblique"))


def _wrap_span(text: str, *, bold: bool, italic: bool, color: str | None) -> str:
    escaped = html.escape(text)
    if not escaped:
        return ""

    styles: List[str] = []
    if color and color != "#000000":
        styles.append(f"color: {color}")

    content = escaped
    if bold:
        content = f"<strong>{content}</strong>"
    if italic:
        content = f"<em>{content}</em>"

    if styles:
        style_attr = "; ".join(styles)
        content = f"<span style=\"{style_attr}\">{content}</span>"
    return content


def _render_line(line: dict) -> str:
    parts: List[str] = []
    for span in line.get("spans", []):
        text = span.get("text", "")
        if not text:
            continue
        parts.append(
            _wrap_span(
                text,
                bold=_is_bold(span.get("font"), span.get("flags")),
                italic=_is_italic(span.get("font"), span.get("flags")),
                color=span.get("color"),
            )
        )
    return "".join(parts)


def _line_plain_text(line: dict) -> str:
    return "".join(span.get("text", "") for span in line.get("spans", []))


def _merge_lines(lines: List[dict]) -> List[dict]:
    if not lines:
        return []
    sorted_lines = sorted(lines, key=lambda ln: (ln.get("bbox", [0, 0, 0, 0])[1], ln.get("bbox", [0, 0, 0, 0])[0]))
    merged: List[dict] = []
    for line in sorted_lines:
        spans_copy = [span.copy() for span in line.get("spans", [])]
        bbox = [float(coord) for coord in line.get("bbox", [0, 0, 0, 0])]

        line_segments = []
        if spans_copy:
            first_color = (spans_copy[0].get("color") or "").lower()
            rest = spans_copy[1:]
            if (
                first_color
                and first_color != "#000000"
                and rest
                and all((span.get("color") or "#000000").lower() == "#000000" for span in rest)
            ):
                heading_span = spans_copy[0].copy()
                body_spans = [span.copy() for span in rest]
                line_segments.append({"bbox": bbox[:], "spans": [heading_span], "__split_heading": True})
                line_segments.append({"bbox": bbox[:], "spans": body_spans})
            elif line.get("__split_at_rarely"):
                # Special case: Split line at ". Rarely"
                full_text = _normalize_plain_text("".join(span.get("text", "") for span in spans_copy))
                split_idx = full_text.index(". Rarely")
                
                # Find which spans to put in each segment
                char_count = 0
                first_spans = []
                second_spans = []
                for span in spans_copy:
                    span_text = _normalize_plain_text(span.get("text", ""))
                    if char_count + len(span_text) <= split_idx + 2:  # +2 for ". "
                        first_spans.append(span.copy())
                        char_count += len(span_text)
                    elif char_count >= split_idx + 2:
                        second_spans.append(span.copy())
                        char_count += len(span_text)
                    else:
                        # Span straddles the split point - need to split the span
                        split_in_span = split_idx + 2 - char_count
                        span1 = span.copy()
                        span2 = span.copy()
                        span1["text"] = span.get("text", "")[:split_in_span]
                        span2["text"] = span.get("text", "")[split_in_span:]
                        first_spans.append(span1)
                        second_spans.append(span2)
                        char_count += len(span_text)
                
                line_segments.append({"bbox": bbox[:], "spans": first_spans})
                line_segments.append({"bbox": bbox[:], "spans": second_spans, "__force_line_break": True})
            elif line.get("__split_at_also"):
                # Special case: Split line at ". Also"
                full_text = _normalize_plain_text("".join(span.get("text", "") for span in spans_copy))
                split_idx = full_text.index(". Also")
                
                # Find which spans to put in each segment
                char_count = 0
                first_spans = []
                second_spans = []
                for span in spans_copy:
                    span_text = _normalize_plain_text(span.get("text", ""))
                    if char_count + len(span_text) <= split_idx + 2:  # +2 for ". "
                        first_spans.append(span.copy())
                        char_count += len(span_text)
                    elif char_count >= split_idx + 2:
                        second_spans.append(span.copy())
                        char_count += len(span_text)
                    else:
                        # Span straddles the split point - need to split the span
                        split_in_span = split_idx + 2 - char_count
                        span1 = span.copy()
                        span2 = span.copy()
                        span1["text"] = span.get("text", "")[:split_in_span]
                        span2["text"] = span.get("text", "")[split_in_span:]
                        first_spans.append(span1)
                        second_spans.append(span2)
                        char_count += len(span_text)
                
                line_segments.append({"bbox": bbox[:], "spans": first_spans})
                line_segments.append({"bbox": bbox[:], "spans": second_spans, "__force_line_break": True})
            elif line.get("__split_at_transportation"):
                # Special case: Split line at "transportation."
                full_text = _normalize_plain_text("".join(span.get("text", "") for span in spans_copy))
                split_pattern = "will be taking animal or magical transportation."
                
                if split_pattern in full_text:
                    split_idx = full_text.index(split_pattern) + len(split_pattern)
                    
                    # Find which spans to put in each segment
                    char_count = 0
                    first_spans = []
                    second_spans = []
                    for span in spans_copy:
                        span_text = _normalize_plain_text(span.get("text", ""))
                        if char_count + len(span_text) <= split_idx:
                            first_spans.append(span.copy())
                            char_count += len(span_text)
                        elif char_count >= split_idx:
                            second_spans.append(span.copy())
                            char_count += len(span_text)
                        else:
                            # Span straddles the split point - need to split the span
                            split_in_span = split_idx - char_count
                            span1 = span.copy()
                            span2 = span.copy()
                            span1["text"] = span.get("text", "")[:split_in_span]
                            span2["text"] = span.get("text", "")[split_in_span:]
                            first_spans.append(span1)
                            second_spans.append(span2)
                            char_count += len(span_text)
                    
                    line_segments.append({"bbox": bbox[:], "spans": first_spans})
                    line_segments.append({"bbox": bbox[:], "spans": second_spans, "__force_line_break": True})
                else:
                    # Pattern not found, treat as normal line
                    segment = {"bbox": bbox, "spans": spans_copy}
                    if line.get("__force_line_break"):
                        segment["__force_line_break"] = True
                    line_segments.append(segment)
            elif line.get("__split_at_mid_sentence"):
                # Generic mid-sentence split based on pattern
                split_pattern = line.get("__split_at_mid_sentence")
                full_text = _normalize_plain_text("".join(span.get("text", "") for span in spans_copy))
                
                if split_pattern in full_text:
                    split_idx = full_text.index(split_pattern)
                    # Find the period before the sentence
                    period_idx = full_text.rfind(". ", 0, split_idx + len(split_pattern))
                    if period_idx >= 0:
                        split_idx = period_idx + 2  # Split after ". "
                    
                        # Find which spans to put in each segment
                        char_count = 0
                        first_spans = []
                        second_spans = []
                        for span in spans_copy:
                            span_text = _normalize_plain_text(span.get("text", ""))
                            if char_count + len(span_text) <= split_idx:
                                first_spans.append(span.copy())
                                char_count += len(span_text)
                            elif char_count >= split_idx:
                                second_spans.append(span.copy())
                                char_count += len(span_text)
                            else:
                                # Span straddles the split point - need to split the span
                                split_in_span = split_idx - char_count
                                span1 = span.copy()
                                span2 = span.copy()
                                span1["text"] = span.get("text", "")[:split_in_span]
                                span2["text"] = span.get("text", "")[split_in_span:]
                                first_spans.append(span1)
                                second_spans.append(span2)
                                char_count += len(span_text)
                        
                        line_segments.append({"bbox": bbox[:], "spans": first_spans})
                        line_segments.append({"bbox": bbox[:], "spans": second_spans, "__force_line_break": True})
                    else:
                        # Couldn't find period, treat as normal line
                        segment = {"bbox": bbox, "spans": spans_copy}
                        if line.get("__force_line_break"):
                            segment["__force_line_break"] = True
                        line_segments.append(segment)
                else:
                    # Pattern not found, treat as normal line
                    segment = {"bbox": bbox, "spans": spans_copy}
                    if line.get("__force_line_break"):
                        segment["__force_line_break"] = True
                    line_segments.append(segment)
            else:
                segment = {"bbox": bbox, "spans": spans_copy}
                # Preserve force line break marker
                if line.get("__force_line_break"):
                    segment["__force_line_break"] = True
                line_segments.append(segment)
        else:
            segment = {"bbox": bbox, "spans": spans_copy}
            # Preserve force line break marker
            if line.get("__force_line_break"):
                segment["__force_line_break"] = True
            line_segments.append(segment)

        for current in line_segments:
            if not merged:
                merged.append(current)
                continue
            prev = merged[-1]
            prev_center = (prev["bbox"][0] + prev["bbox"][2]) / 2
            curr_center = (current["bbox"][0] + current["bbox"][2]) / 2
            prev_spans = prev.get("spans", [])
            has_colored_heading = (
                len(prev_spans) == 1
                and (prev_spans[0].get("color") or "").lower() not in {"", "#000000"}
            )
            # Don't merge if current line has a force break marker
            has_force_break = current.get("__force_line_break", False)
            if (
                not has_colored_heading
                and not has_force_break
                and abs(current["bbox"][1] - prev["bbox"][1]) < 1.0
                and abs(curr_center - prev_center) < 20.0
            ):
                prev["spans"].extend(current["spans"])
                prev_bbox = prev["bbox"]
                prev_bbox[0] = min(prev_bbox[0], current["bbox"][0])
                prev_bbox[1] = min(prev_bbox[1], current["bbox"][1])
                prev_bbox[2] = max(prev_bbox[2], current["bbox"][2])
                prev_bbox[3] = max(prev_bbox[3], current["bbox"][3])
            else:
                merged.append(current)
    return merged


def _split_lines_by_column(lines: List[dict]) -> List[List[dict]]:
    if not lines:
        return []

    overall_min_x = min(line.get("bbox", [0, 0, 0, 0])[0] for line in lines)
    overall_max_x = max(line.get("bbox", [0, 0, 0, 0])[2] for line in lines)
    overall_width = overall_max_x - overall_min_x

    centers: List[tuple[float, float]] = []  # (count, avg)
    threshold = 80.0
    for line in lines:
        bbox = line.get("bbox", [0, 0, 0, 0])
        center = (bbox[0] + bbox[2]) / 2 if bbox else 0.0
        for idx, (count, avg) in enumerate(centers):
            if abs(center - avg) <= threshold:
                new_count = count + 1
                centers[idx] = (new_count, (avg * count + center) / new_count)
                break
        else:
            centers.append((1, center))

    column_centers = sorted(avg for _, avg in centers)
    if len(column_centers) <= 1 or overall_width < 360.0:
        return [sorted(lines, key=lambda ln: (ln.get("bbox", [0, 0, 0, 0])[1], ln.get("bbox", [0, 0, 0, 0])[0]))]

    buckets: dict[int, List[dict]] = {idx: [] for idx in range(len(column_centers))}
    for line in lines:
        bbox = line.get("bbox", [0, 0, 0, 0])
        center = (bbox[0] + bbox[2]) / 2 if bbox else 0.0
        column_idx = min(range(len(column_centers)), key=lambda i: abs(center - column_centers[i]))
        buckets[column_idx].append(line)

    return [
        sorted(buckets[idx], key=lambda ln: ln.get("bbox", [0, 0, 0, 0])[1])
        for idx in sorted(buckets)
    ]


def _render_text_block(block: dict, *, paragraph_breaks: List[str]) -> str:
    column_groups = _split_lines_by_column(_merge_lines(block.get("lines", [])))
    if not column_groups:
        return ""

    # Check if this block should force a paragraph break
    force_paragraph_break = block.get("__force_paragraph_break", False)
    
    # Check if this block is part of a special section that should not auto-split
    in_special_section = (block.get("__roleplaying_section", False) or 
                         block.get("__half_giants_section", False) or
                         block.get("__ranger_description", False))

    paragraphs: List[List[dict]] = []
    paragraph_centers: List[float | None] = []

    for column_index, column_lines in enumerate(column_groups):
        gaps = []
        for idx in range(1, len(column_lines)):
            delta = column_lines[idx]["bbox"][1] - column_lines[idx - 1]["bbox"][1]
            if delta > 0.5:
                gaps.append(delta)
        base_gap = median(gaps) if gaps else None

        current: List[dict] = []
        column_paragraphs: List[List[dict]] = []
        for idx, line in enumerate(column_lines):
            plain = _line_plain_text(line).strip()
            if not plain:
                if current:
                    column_paragraphs.append(current)
                    current = []
                continue
            if plain.isdigit() and len(plain) <= 3:
                continue
            html_line = _render_line(line)
            if not html_line:
                continue

            start_new = False
            if current and base_gap is not None and idx > 0 and not in_special_section:
                delta = line["bbox"][1] - column_lines[idx - 1]["bbox"][1]
                if delta > base_gap + 1.0:
                    start_new = True

            # Check if this line has a force break marker
            force_line_break = line.get("__force_line_break", False)

            force_break = any(plain.startswith(pattern) for pattern in paragraph_breaks)
            if (start_new or force_break or force_line_break) and current:
                column_paragraphs.append(current)
                current = []

            spans_with_text = [span for span in line.get("spans", []) if span.get("text")]
            first_span = spans_with_text[0] if spans_with_text else None
            if spans_with_text and all((span.get("color") or "").lower() != "#000000" for span in spans_with_text):
                color = spans_with_text[0].get("color")
                is_heading = True
            else:
                color = first_span.get("color") if first_span else None
                is_heading = color is not None and color.lower() != "#000000" and len(spans_with_text) == 1
            if is_heading and not line.get("__split_heading") and plain.rstrip().endswith(":"):
                is_heading = False

            if is_heading:
                if current:
                    column_paragraphs.append(current)
                    current = []
                column_paragraphs.append(
                    [
                        {
                            "html": html_line,
                            "plain": plain,
                            "is_heading": True,
                            "center": (line["bbox"][0] + line["bbox"][2]) / 2,
                        }
                    ]
                )
                continue

            current.append(
                {
                    "html": html_line,
                    "plain": plain,
                    "is_heading": is_heading,
                    "center": (line["bbox"][0] + line["bbox"][2]) / 2,
                }
            )

        if current:
            column_paragraphs.append(current)

        if not column_paragraphs:
            continue

        column_paragraph_centers: List[float | None] = []
        for para in column_paragraphs:
            centers = [entry.get("center") for entry in para if entry.get("center") is not None]
            column_paragraph_centers.append(sum(centers) / len(centers) if centers else None)

        if paragraphs:
            first_para = column_paragraphs[0]
            first_entry = first_para[0] if first_para else None
            first_plain = first_entry.get("plain") if first_entry else ""
            first_is_heading = first_entry.get("is_heading") if first_entry else False
            should_merge = (
                first_entry is not None
                and not first_is_heading
                and not force_paragraph_break  # Don't merge if block has force break marker
                and first_plain
                and first_plain[0].islower()
                and not any(first_plain.startswith(pattern) for pattern in paragraph_breaks)
            )
            if should_merge:
                target_idx = len(paragraphs) - 1
                current_center = column_paragraph_centers[0]
                if paragraph_centers and current_center is not None:
                    deltas = [
                        (abs(center - current_center) if center is not None else float("inf"), idx)
                        for idx, center in enumerate(paragraph_centers)
                    ]
                    candidates = [item for item in deltas if item[0] <= 120.0]
                    if candidates:
                        target_idx = min(candidates, key=lambda item: item[0])[1]
                    elif deltas:
                        target_idx = min(deltas, key=lambda item: item[0])[1]
                paragraphs[target_idx].extend(first_para)
                if current_center is not None:
                    existing = paragraph_centers[target_idx]
                    if existing is not None:
                        paragraph_centers[target_idx] = (existing + current_center) / 2
                    else:
                        paragraph_centers[target_idx] = current_center
                column_paragraphs = column_paragraphs[1:]
                column_paragraph_centers = column_paragraph_centers[1:]

        paragraphs.extend(column_paragraphs)
        paragraph_centers.extend(column_paragraph_centers)

    if not paragraphs:
        return ""

    rendered_paragraphs: List[str] = []
    paragraph_texts: List[str] = []
    for para in paragraphs:
        if not para:
            continue

        if len(para) == 1 and para[0]["is_heading"]:
            heading_html = para[0]["html"]
            rendered_paragraphs.append(f"<p>{heading_html}</p>")
            paragraph_texts.append(_normalize_plain_text(para[0]["plain"]))
            continue

        fragments = [_normalize_plain_text(entry["plain"]) for entry in para]
        fragments = [fragment for fragment in fragments if fragment]
        merged = _merge_fragments(fragments)
        combined = _join_fragments(merged)
        if not combined:
            continue
        rendered_paragraphs.append(f"<p>{html.escape(combined)}</p>")
        paragraph_texts.append(combined)

    if not rendered_paragraphs:
        return ""

    final_html: List[str] = []
    final_plain: List[str] = []
    for html_paragraph, plain_paragraph in zip(rendered_paragraphs, paragraph_texts):
        if final_html:
            prev_plain = final_plain[-1]
            if (
                plain_paragraph
                and prev_plain
                and plain_paragraph[0].islower()
                and not prev_plain.endswith((".", "!", "?", ":", ";"))
                and "<span" not in final_html[-1]
                and "<span" not in html_paragraph
            ):
                merged = _merge_fragments([prev_plain, plain_paragraph])
                combined_text = _join_fragments(merged)
                final_plain[-1] = combined_text
                final_html[-1] = f"<p>{html.escape(combined_text)}</p>"
                continue
        final_html.append(html_paragraph)
        final_plain.append(plain_paragraph)

    return "".join(final_html)


def _render_table(table: dict, *, table_class: str | None = None) -> str:
    rows_html: List[str] = []
    header_rows = int(table.get("header_rows", 0) or 0)
    for row_index, row in enumerate(table.get("rows", [])):
        cell_tag = "th" if row_index < header_rows else "td"
        cells_html: List[str] = []
        for cell in row.get("cells", []):
            attrs: List[str] = []
            rowspan = cell.get("rowspan", 1)
            colspan = cell.get("colspan", 1)
            if rowspan and rowspan > 1:
                attrs.append(f"rowspan=\"{int(rowspan)}\"")
            if colspan and colspan > 1:
                attrs.append(f"colspan=\"{int(colspan)}\"")
            text = cell.get("text")
            contents = html.escape(text) if text else "&nbsp;"
            attr_str = " " + " ".join(attrs) if attrs else ""
            cells_html.append(f"<{cell_tag}{attr_str}>{contents}</{cell_tag}>")
        if cells_html:
            rows_html.append(f"<tr>{''.join(cells_html)}</tr>")
    if not rows_html:
        return ""
    class_attr = f" class=\"{table_class}\"" if table_class else ""
    return f"<table{class_attr}>{''.join(rows_html)}</table>"


def _render_page(
    page: dict,
    *,
    include_tables: bool,
    table_class: str | None,
    wrap_pages: bool,
    paragraph_breaks: List[str],
) -> str:
    def _render_item(meta) -> str:
        kind = meta["kind"]
        payload = meta["payload"]
        if kind == "block":
            if payload.get("type") != "text":
                return ""
            return _render_text_block(payload, paragraph_breaks=paragraph_breaks)
        if kind == "table":
            return _render_table(payload, table_class=table_class)
        return ""

    page_width = float(page.get("width", 0) or 0)
    column_threshold = max(page_width * 0.08, 60.0) if page_width else 60.0
    column_min_width = page_width * 0.25 if page_width else 150.0
    full_width_cutoff = page_width * 0.7 if page_width else float("inf")

    items_meta = []
    order_counter = 0
    for block in page.get("blocks", []):
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        items_meta.append(
            {
                "kind": "block",
                "payload": block,
                "bbox": bbox,
                "y": bbox[1],
                "x": bbox[0],
                "width": bbox[2] - bbox[0],
                "center": (bbox[0] + bbox[2]) / 2 if bbox else 0.0,
                "order": order_counter,
            }
        )
        order_counter += 1
    if include_tables:
        for table in page.get("tables", []):
            bbox = [float(coord) for coord in table.get("bbox", [0, 0, 0, 0])]
            items_meta.append(
                {
                    "kind": "table",
                    "payload": table,
                    "bbox": bbox,
                    "y": bbox[1],
                    "x": bbox[0],
                    "width": bbox[2] - bbox[0],
                    "center": (bbox[0] + bbox[2]) / 2 if bbox else 0.0,
                    "order": order_counter,
                }
            )
            order_counter += 1

    if not items_meta:
        return ""

    def build_columns(candidates: Iterable[dict]) -> List[float]:
        reps: List[tuple[float, float]] = []
        for meta in candidates:
            center = meta["center"]
            for idx, (count, avg) in enumerate(reps):
                if abs(center - avg) <= column_threshold:
                    new_count = count + 1
                    reps[idx] = (new_count, (avg * count + center) / new_count)
                    break
            else:
                reps.append((1, center))
        return sorted(avg for _, avg in reps)

    primary_candidates = [
        meta
        for meta in items_meta
        if meta["kind"] == "block"
        and meta["payload"].get("type") == "text"
        and (meta["width"] >= column_min_width or page_width == 0)
        and meta["width"] <= full_width_cutoff
    ]

    columns = build_columns(primary_candidates)
    if not columns:
        fallback_candidates = [
            meta
            for meta in items_meta
            if meta["kind"] == "block" and meta["payload"].get("type") == "text" and meta["width"] <= full_width_cutoff
        ]
        columns = build_columns(fallback_candidates)

    if len(columns) <= 1:
        ordered_html: List[str] = []
        for meta in sorted(items_meta, key=lambda m: (m["y"], m["x"], m["order"])):
            html_piece = _render_item(meta)
            if html_piece:
                ordered_html.append(html_piece)
        if not ordered_html:
            return ""
        page_html = "".join(ordered_html)
        if wrap_pages:
            return f"<section data-page=\"{page.get('page_number')}\">{page_html}</section>"
        return page_html

    full_width_items: List[dict] = []
    column_buckets: dict[int, List[dict]] = {idx: [] for idx in range(len(columns))}

    for meta in items_meta:
        width = meta["width"]
        kind = meta["kind"]
        if width >= full_width_cutoff or (kind == "block" and meta["payload"].get("type") != "text"):
            full_width_items.append(meta)
            continue
        if kind == "table":
            target_idx = min(range(len(columns)), key=lambda i: abs(meta["center"] - columns[i]))
            column_buckets[target_idx].append(meta)
            continue
        column_idx = min(range(len(columns)), key=lambda i: abs(meta["center"] - columns[i]))
        column_buckets[column_idx].append(meta)

    full_width_items.sort(key=lambda m: (m["y"], m["x"], m["order"]))

    def _coalesce_column_items(items: List[dict]) -> List[dict]:
        combined: List[dict] = []
        buffer: dict | None = None
        for meta in items:
            if meta["kind"] != "block" or meta["payload"].get("type") != "text":
                if buffer is not None:
                    combined.append(buffer)
                    buffer = None
                combined.append(meta)
                continue

            # Don't coalesce if this block has a force paragraph break marker
            if meta["payload"].get("__force_paragraph_break"):
                if buffer is not None:
                    combined.append(buffer)
                    buffer = None
                combined.append(meta)
                continue

            if buffer is None:
                buffer = {
                    "kind": "block",
                    "payload": {"type": "text", "lines": []},
                    "bbox": meta["bbox"][:],
                    "y": meta["y"],
                    "x": meta["x"],
                    "width": meta["width"],
                    "center": meta["center"],
                    "order": meta["order"],
                }
                # Preserve special section markers
                if meta["payload"].get("__roleplaying_section"):
                    buffer["payload"]["__roleplaying_section"] = True
                if meta["payload"].get("__half_giants_section"):
                    buffer["payload"]["__half_giants_section"] = True
            buffer["payload"]["lines"].extend(meta["payload"].get("lines", []))
            buffer_bbox = buffer["bbox"]
            meta_bbox = meta["bbox"]
            buffer_bbox[0] = min(buffer_bbox[0], meta_bbox[0])
            buffer_bbox[1] = min(buffer_bbox[1], meta_bbox[1])
            buffer_bbox[2] = max(buffer_bbox[2], meta_bbox[2])
            buffer_bbox[3] = max(buffer_bbox[3], meta_bbox[3])
            buffer["y"] = min(buffer["y"], meta["y"])
            buffer["x"] = min(buffer["x"], meta["x"])
            buffer["width"] = max(buffer["width"], meta["bbox"][2] - meta["bbox"][0])
            buffer["center"] = (buffer_bbox[0] + buffer_bbox[2]) / 2

        if buffer is not None:
            combined.append(buffer)
        return combined

    column_order = sorted(column_buckets.keys())
    for idx in column_order:
        column_buckets[idx].sort(key=lambda m: (m["y"], m["x"], m["order"]))
        column_buckets[idx] = _coalesce_column_items(column_buckets[idx])

    ordered_html: List[str] = []
    full_index = 0

    def consume_full(upto_y: float) -> None:
        nonlocal full_index
        while full_index < len(full_width_items) and full_width_items[full_index]["y"] <= upto_y:
            html_piece = _render_item(full_width_items[full_index])
            if html_piece:
                ordered_html.append(html_piece)
            full_index += 1

    for idx in column_order:
        for meta in column_buckets[idx]:
            consume_full(meta["y"])
            html_piece = _render_item(meta)
            if html_piece:
                ordered_html.append(html_piece)

    consume_full(float("inf"))

    if not ordered_html:
        return ""

    page_html = "".join(ordered_html)
    page_html = _merge_adjacent_paragraph_html(page_html)
    if wrap_pages:
        return f"<section data-page=\"{page.get('page_number')}\">{page_html}</section>"
    return page_html


def _render_pages(
    pages: Iterable[dict],
    *,
    include_tables: bool,
    table_class: str | None,
    wrap_pages: bool,
    paragraph_breaks: List[str],
) -> str:
    snippets = [
        snippet
        for snippet in (
            _render_page(
                page,
                include_tables=include_tables,
                table_class=table_class,
                wrap_pages=wrap_pages,
                paragraph_breaks=paragraph_breaks,
            )
            for page in pages
        )
        if snippet
    ]
    if not snippets:
        return "<p></p>"
    return "\n".join(snippets)


def _generate_table_of_contents(html_content: str) -> str:
    """Generate a table of contents from headers in the HTML content.
    
    Extracts all headers (colored span elements) and creates anchor links.
    Returns the TOC HTML to be prepended to the content.
    
    Args:
        html_content: The rendered HTML content with anchor IDs already added
        
    Returns:
        TOC HTML string with links to all headers
    """
    import re
    
    # Find all headers (colored span elements that look like section headers)
    # After _add_header_anchors, the pattern is: <p id="header-X-slug"><span style="color: #ca5804">Header Text</span></p>
    header_pattern = r'<p id="([^"]+)"><span[^>]*style="color: #ca5804"[^>]*>([^<]+)</span></p>'
    matches = re.findall(header_pattern, html_content)
    
    if not matches:
        return ""
    
    # Build TOC HTML
    toc_items = []
    for header_id, header_text in matches:
        toc_items.append(f'<li><a href="#{header_id}">{header_text}</a></li>')
    
    toc_html = f'''<nav id="table-of-contents">
<h2>Table of Contents</h2>
<ul>
{''.join(toc_items)}
</ul>
</nav>
'''
    
    return toc_html


def _add_header_anchors(html_content: str) -> str:
    """Add anchor IDs to headers in the HTML content.
    
    Modifies colored span headers to include IDs for TOC linking.
    
    Args:
        html_content: The rendered HTML content
        
    Returns:
        HTML content with header anchor IDs added
    """
    import re
    
    # Find all headers and add IDs
    header_pattern = r'<p><span([^>]*style="color: #ca5804"[^>]*)>([^<]+)</span></p>'
    
    def replace_header(match):
        span_attrs = match.group(1)
        header_text = match.group(2)
        
        # Create a slug-friendly ID
        counter = replace_header.counter
        replace_header.counter += 1
        header_id = f"header-{counter}-{header_text.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '').replace(',', '')}"
        
        return f'<p id="{header_id}"><span{span_attrs}>{header_text}</span></p>'
    
    replace_header.counter = 0
    return re.sub(header_pattern, replace_header, html_content)


def transform(section_data: dict, config: dict | None = None) -> dict:
    config = config or {}
    pages = section_data.get("pages", [])
    include_tables = config.get("include_tables", True)
    table_class = config.get("table_class")
    wrap_pages = config.get("wrap_pages", True)
    slug = section_data.get("slug")
    paragraph_breaks = list(config.get("paragraph_breaks", []))
    per_slug = config.get("paragraph_break_hints", {})
    if slug and isinstance(per_slug, dict):
        paragraph_breaks.extend(per_slug.get(slug, []))

    # Apply chapter-specific processing
    if slug == "chapter-two-player-character-races":
        from . import chapter_2_processing
        chapter_2_processing.apply_chapter_2_adjustments(section_data)
        paragraph_breaks.extend(
            [
                "The player character races are no exception to this",
            ]
        )
    elif slug == "chapter-three-player-character-classes":
        from . import chapter_3_processing
        chapter_3_processing.apply_chapter_3_adjustments(section_data)

    html_content = _render_pages(
        pages,
        include_tables=include_tables,
        table_class=table_class,
        wrap_pages=wrap_pages,
        paragraph_breaks=paragraph_breaks,
    )

    # Apply post-processing to the rendered HTML
    if slug:
        from ..postprocess import postprocess_chapter_2_html
        html_content = postprocess_chapter_2_html(html_content, slug)
    
    # Add header anchors and generate TOC (Rule #32)
    html_content = _add_header_anchors(html_content)
    toc_html = _generate_table_of_contents(html_content)
    if toc_html:
        html_content = toc_html + html_content

    return {
        "entity_type": "journal",
        "slug": section_data.get("slug"),
        "title": section_data.get("title"),
        "content": html_content,
        "source_pages": [section_data.get("start_page"), section_data.get("end_page")],
        "metadata": {
            "parent_slugs": section_data.get("parent_slugs", []),
            "level": section_data.get("level"),
            "layout": "structured",
        },
    }


