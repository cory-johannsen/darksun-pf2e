"""
Utility functions for journal transformation.

This module contains text processing and formatting utilities.
"""

from __future__ import annotations

import html
import re
from typing import List, Tuple, Optional


def normalize_plain_text(text: str) -> str:
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
    # Fix spaced letters/digits BEFORE collapsing whitespace so that double spaces
    # between words prevent cross-word collapsing.
    text = _SPACED_LETTERS_RE.sub(lambda match: match.group(0).replace(" ", ""), text)
    text = _SPACED_DIGITS_RE.sub(lambda match: match.group(0).replace(" ", ""), text)
    # Normalize hyphen + space + digit (e.g., "- 1" -> "-1")
    text = re.sub(r"-\s+(\d)", r"-\1", text)
    # Finally, collapse excess whitespace
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()




def merge_fragments(fragments: List[str]) -> List[str]:
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




def join_fragments(merged: List[str]) -> str:
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




def sanitize_plain_text(value: str) -> str:
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




def cluster_positions(values: Sequence[float], tolerance: float) -> List[float]:
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




def compute_bbox_from_cells(cells: Sequence[dict]) -> List[float]:
    min_x = min(cell["bbox"][0] for cell in cells)
    min_y = min(cell["bbox"][1] for cell in cells)
    max_x = max(cell["bbox"][2] for cell in cells)
    max_y = max(cell["bbox"][3] for cell in cells)
    return [min_x, min_y, max_x, max_y]


# Chapter-specific adjustments have been moved to separate processing modules




def is_bold(font_name: str | None, flags: int | None) -> bool:
    if not font_name:
        return False
    lowered = font_name.lower()
    return any(keyword in lowered for keyword in ("bold", "black", "heavy"))




def is_italic(font_name: str | None, flags: int | None) -> bool:
    if not font_name:
        return False
    lowered = font_name.lower()
    
    # Check for common italic font name patterns
    if any(keyword in lowered for keyword in ("italic", "oblique")):
        return True
    
    # Dark Sun PDF-specific font: MSTT31c576 is used for italicized text
    # This font is used for book titles like "The Complete Psionics Handbook",
    # "Players Handbook", etc.
    if font_name == "MSTT31c576":
        return True
    
    return False






# Regular expressions for text normalization
_WHITESPACE_RE = re.compile(r'\s+')
_SPACED_LETTERS_RE = re.compile(r'\b(?:[A-Za-z]\s){4,}[A-Za-z]\b')
_SPACED_DIGITS_RE = re.compile(r'\b(?:\d\s){1,}\d\b')



def wrap_span(text: str, *, bold: bool, italic: bool, color: str | None) -> str:
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




def dehyphenate_text(text: str) -> str:
    """Remove end-of-line hyphens from merged text.
    
    [MERGED_LINES] Ensures proper merging of hyphenated words.
    For example, "in- ner" becomes "inner", "specializa- tion" becomes "specialization".
    """
    # Pattern: hyphen followed by space and a lowercase letter
    # Replace with just the lowercase letter (no hyphen, no space)
    import re
    result = re.sub(r'- ([a-z])', r'\1', text)
    return result



