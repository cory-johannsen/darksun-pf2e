"""
Core rendering functions for journal transformation.

This module contains the main HTML rendering logic for journal entries.
"""

from __future__ import annotations

import html
import logging
import re
from statistics import median
from typing import List, Dict, Any, Optional, Tuple

from .utilities import (
    normalize_plain_text,
    merge_fragments,
    join_fragments,
    sanitize_plain_text,
    is_bold,
    is_italic,
    wrap_span,
    dehyphenate_text,
)
from .tables import build_matrix_from_cells, table_from_rows

logger = logging.getLogger(__name__)

# Create aliases for backward compatibility with underscore-prefixed function calls
_normalize_plain_text = normalize_plain_text
_merge_fragments = merge_fragments
_join_fragments = join_fragments
_sanitize_plain_text = sanitize_plain_text
_is_bold = is_bold
_is_italic = is_italic
_wrap_span = wrap_span

# Regular expressions
_PARAGRAPH_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
_TAG_RE = re.compile(r'<[^>]+>')


# Helper functions for rendering

def line_plain_text(line: dict) -> str:
    return "".join(span.get("text", "") for span in line.get("spans", []))



def merge_lines(lines: List[dict]) -> List[dict]:
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
            # Check if this line should not be split (e.g., for "Inherent Potential: In DARK SUN...")
            dont_split = line.get("__dont_split_heading", False)
            if (
                not dont_split
                and first_color
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
                
                # Check if pattern exists before trying to split
                if ". Rarely" not in full_text:
                    # Pattern not found, treat as normal line
                    line_segments.append({"bbox": bbox[:], "spans": spans_copy})
                else:
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
                
                # Check if pattern exists before trying to split
                if ". Also" not in full_text:
                    # Pattern not found, treat as normal line
                    line_segments.append({"bbox": bbox[:], "spans": spans_copy})
                else:
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
                    if line.get("__split_heading"):
                        segment["__split_heading"] = True
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
                        if line.get("__split_heading"):
                            segment["__split_heading"] = True
                        line_segments.append(segment)
                else:
                    # Pattern not found, treat as normal line
                    segment = {"bbox": bbox, "spans": spans_copy}
                    if line.get("__force_line_break"):
                        segment["__force_line_break"] = True
                    if line.get("__split_heading"):
                        segment["__split_heading"] = True
                    line_segments.append(segment)
            else:
                segment = {"bbox": bbox, "spans": spans_copy}
                # Preserve markers
                if line.get("__force_line_break"):
                    segment["__force_line_break"] = True
                if line.get("__split_heading"):
                    segment["__split_heading"] = True
                line_segments.append(segment)
        else:
            segment = {"bbox": bbox, "spans": spans_copy}
            # Preserve markers
            if line.get("__force_line_break"):
                segment["__force_line_break"] = True
            if line.get("__split_heading"):
                segment["__split_heading"] = True
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



def split_lines_by_column(lines: List[dict]) -> List[List[dict]]:
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



def wrap_spell_list_items(html_content: str) -> str:
    """Wrap consecutive spell list items in <ul> tags.
    
    Args:
        html_content: HTML content with individual <li> elements
        
    Returns:
        HTML with <li> elements wrapped in <ul class="spell-list"> tags
    """
    import re
    
    # Find all <li class="spell-list-item"> elements
    # Replace consecutive list items with a wrapped <ul> containing them
    result = []
    current_list_items = []
    
    # Split by <li> tags to find list items
    parts = re.split(r'(<li class="spell-list-item">.*?</li>)', html_content)
    
    for part in parts:
        if part.startswith('<li class="spell-list-item">'):
            # This is a spell list item, accumulate it
            current_list_items.append(part)
        else:
            # Not a spell list item
            # If we have accumulated list items, wrap them in <ul>
            if current_list_items:
                result.append('<ul class="spell-list">')
                result.extend(current_list_items)
                result.append('</ul>')
                current_list_items = []
            
            # Add the non-list-item content
            if part:
                result.append(part)
    
    # Handle any remaining list items
    if current_list_items:
        result.append('<ul class="spell-list">')
        result.extend(current_list_items)
        result.append('</ul>')
    
    return ''.join(result)



def merge_adjacent_paragraph_html(html_fragment: str) -> str:
    if "<p" not in html_fragment:
        return html_fragment

    segments = []
    pos = 0
    for match in _PARAGRAPH_RE.finditer(html_fragment):
        start, end = match.span()
        if start > pos:
            segments.append(("text", html_fragment[pos:start]))
        # Store the FULL paragraph tag, not just the inner content
        segments.append(("p", match.group(0)))  # group(0) is the full match including <p>...</p>
        pos = end
    if pos < len(html_fragment):
        segments.append(("text", html_fragment[pos:]))

    result: List[tuple[str, str]] = []
    plains: List[str] = []

    for kind, content in segments:
        if kind != "p":
            result.append((kind, content))
            continue

        # content now contains the full <p>...</p> tag
        # Extract inner content by finding the opening and closing tag positions
        # Handle both <p> and <p data-force-break="true"> etc.
        if '>' not in content or '</p>' not in content:
            # Malformed content, keep as-is
            result.append((kind, content))
            continue
        
        opening_tag_end = content.index('>') + 1
        closing_tag_start = content.rindex('</p>')
        inner = content[opening_tag_end:closing_tag_start]
        plain = html.unescape(_TAG_RE.sub("", inner)).strip()
        
        # Check if this paragraph has data-force-break attribute
        has_force_break = 'data-force-break="true"' in content

        prev_plain_text = plains[-1] if plains else ""
        prev_heading = prev_plain_text.strip().endswith(":")

        # [HTML_SINGLE_PAGE] Find the last paragraph in result, skipping whitespace-only text segments
        last_paragraph_idx = -1
        for i in range(len(result) - 1, -1, -1):
            if result[i][0] == "p":
                last_paragraph_idx = i
                break
            elif result[i][0] == "text" and result[i][1].strip():
                # Non-whitespace text segment, stop looking
                break

        # Determine if the current paragraph looks like a continuation
        # It's a continuation if it starts with lowercase, or if previous paragraph
        # has an incomplete sentence (doesn't end with proper punctuation)
        looks_like_continuation = (
            plain and
            (plain[0].islower() or 
             (prev_plain_text and 
              not prev_plain_text.endswith((".", "!", "?", ";", ":")) and
              len(plain.split()) < 20))  # Short fragment likely continues previous
        )
        
        # Don't merge if this paragraph has a force break marker
        if (
            last_paragraph_idx >= 0
            and plain
            and prev_plain_text
            and looks_like_continuation
            and not prev_heading
            and not has_force_break
            and "<span" not in content
            and "<span" not in result[last_paragraph_idx][1]
        ):
            merged_fragments = _merge_fragments([plains[-1], plain])
            combined_text = _join_fragments(merged_fragments)
            new_html = f"<p>{html.escape(combined_text)}</p>"
            result[last_paragraph_idx] = ("p", new_html)
            plains[-1] = combined_text
            continue

        result.append((kind, content))
        plains.append(plain)

    return "".join(fragment for _, fragment in result)




def render_line(line: dict) -> str:
    """Render a line to HTML, handling text formatting."""
    parts: List[str] = []
    spans = line.get("spans", [])
    
    for idx, span in enumerate(spans):
        # Skip spans marked with __skip_render (e.g., headers that are rendered separately)
        if span.get("__skip_render"):
            continue
            
        text = _normalize_plain_text(span.get("text", ""))
        if not text:
            continue
        
        # Special handling for legend entries - make the label bold
        if span.get("__legend_entry"):
            # Split at the first colon to separate label from description
            if ":" in text:
                colon_idx = text.index(":")
                label = text[:colon_idx + 1]  # Include the colon
                description = text[colon_idx + 1:]  # Everything after the colon
                
                # Render label as bold
                parts.append(wrap_span(label, bold=True, italic=False, color=span.get("color")))
                # Render description as normal text
                if description:
                    parts.append(wrap_span(description, bold=False, italic=False, color=span.get("color")))
            else:
                # No colon found, render as-is
                parts.append(
                    wrap_span(
                        text,
                        bold=_is_bold(span.get("font"), span.get("flags")),
                        italic=_is_italic(span.get("font"), span.get("flags")),
                        color=span.get("color"),
                    )
                )
        else:
            # Normal span rendering
            rendered_span = wrap_span(
                text,
                bold=_is_bold(span.get("font"), span.get("flags")),
                italic=_is_italic(span.get("font"), span.get("flags")),
                color=span.get("color"),
            )
            
            # Check if this span has a CSS class marker (for Chapter 3 header levels)
            if "__css_class" in span:
                css_class = span["__css_class"]
                # Inject the class attribute into the span tag
                # If it's a colored span like <span style="color: #ca5804">Text</span>
                # we want to add the class: <span class="header-h3" style="color: #ca5804">Text</span>
                if rendered_span.startswith('<span style="'):
                    rendered_span = rendered_span.replace('<span style="', f'<span class="{css_class}" style="')
                elif rendered_span.startswith('<span>'):
                    rendered_span = rendered_span.replace('<span>', f'<span class="{css_class}">')
                # If there's no span tag (just text with bold/italic), wrap it
                elif not rendered_span.startswith('<span'):
                    # Extract any strong/em tags and rewrap
                    rendered_span = f'<span class="{css_class}">{rendered_span}</span>'
            
            parts.append(rendered_span)
    return "".join(parts)




def render_text_block(block: dict, *, paragraph_breaks: List[str]) -> str:
    # Check if this block should be rendered as an H2 header (Chapter 11 campaign settings)
    # This check should happen early to prevent the block from being processed as normal text
    if block.get("__render_as_h2"):
        header_text = block.get("__header_text", "Unknown")
        header_id = f"header-{header_text.lower().replace(' ', '-')}"
        
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"🎯 render_text_block: Rendering H2 header: '{header_text}'")
        
        return f'<h2 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
    
    # Check if this block should be rendered as an H3 header (Chapter 15 spell names)
    if block.get("__render_as_h3"):
        header_text = block.get("__header_text", "Unknown")
        header_id = f"header-{header_text.lower().replace(' ', '-')}"
        
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"🎯 render_text_block: Rendering H3 header: '{header_text}'")
        
        return f'<h3 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h3>'
    
    # Check if this block should be rendered as an H4 header (Chapter 3 Geography subsections)
    if block.get("__render_as_h4"):
        header_text = block.get("__header_text", "Unknown")
        header_id = f"header-{header_text.lower().replace(' ', '-')}"
        
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"🎯 render_text_block: Rendering H4 header: '{header_text}'")
        
        return f'<h4 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h4>'
    
    # Check if this block has a class requirements table attached
    if "__class_requirements_table" in block:
        table_data = block["__class_requirements_table"]
        return render_table(table_data, table_class="ds-table")
    
    # Check if this block has a wilderness encounter table attached
    if "__wilderness_encounter_table" in block:
        import logging
        logger = logging.getLogger(__name__)
        
        # Extract the header text for this wilderness table
        header_text = ""
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                header_text += span.get("text", "")
        header_text = header_text.strip()
        
        logger.warning(f"🎯 render_text_block: Rendering wilderness encounter table for '{header_text}'")
        
        # Render the header
        header_id = f"header-{header_text.lower().replace(' ', '-')}"
        result = f'<p id="{header_id}">{html.escape(header_text)} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></p>\n'
        
        # Render the table
        table_data = block["__wilderness_encounter_table"]
        result += render_table(table_data)
        
        return result
    
    # Check if this block should be rendered as an HTML list (e.g., Monstrous Compendium list)
    if block.get("__format_as_html_list"):
        lines = block.get("lines", [])
        if not lines:
            return ""
        
        # Extract the text from all spans
        full_text = ""
        for line in lines:
            for span in line.get("spans", []):
                full_text += span.get("text", "")
        
        # Split by newlines to get individual list items
        items = [item.strip() for item in full_text.split('\n') if item.strip()]
        
        if not items:
            return ""
        
        # Create HTML unordered list
        list_html = '<ul>\n'
        for item in items:
            # Remove bullet character if present (we'll use HTML bullets)
            item_text = item.lstrip('• ').strip()
            if item_text:
                list_html += f'<li>{html.escape(item_text)}</li>\n'
        list_html += '</ul>'
        
        return list_html
    
    # Check if this block should be rendered as a spell list item
    if block.get("_render_as") == "spell_list_item":
        # Extract ALL spell lines from the block (some blocks have multiple spells)
        import re
        spell_pattern = re.compile(r'^(.+?)\s*\((\d+(?:st|nd|rd|th))\)\s*$')
        
        spell_items = []
        accumulated_text = ""
        
        for line in block.get("lines", []):
            # Concatenate all spans in the line (some spells are split across spans)
            line_text = ""
            for span in line.get("spans", []):
                span_text = span.get("text", "").strip()
                if span_text:
                    line_text += " " + span_text if line_text else span_text
            
            line_text = line_text.strip()
            if not line_text:
                continue
            
            # Try to match the spell pattern
            if spell_pattern.match(line_text):
                # This line is a complete spell
                spell_items.append(f'<li class="spell-list-item">{html.escape(line_text)}</li>')
            elif accumulated_text:
                # We have accumulated text from a previous line - try combining
                combined = (accumulated_text + " " + line_text).strip()
                if spell_pattern.match(combined):
                    # The combination is a complete spell
                    spell_items.append(f'<li class="spell-list-item">{html.escape(combined)}</li>')
                    accumulated_text = ""
                else:
                    # Still not a complete spell - flush accumulated and start new
                    spell_items.append(f'<li class="spell-list-item">{html.escape(accumulated_text)}</li>')
                    accumulated_text = line_text
            else:
                # This line might be incomplete - accumulate it
                accumulated_text = line_text
        
        # Flush any remaining accumulated text
        if accumulated_text:
            spell_items.append(f'<li class="spell-list-item">{html.escape(accumulated_text)}</li>')
        
        if spell_items:
            # Return all spell items from this block
            return '\n'.join(spell_items)
        return ""
    
    # Check if this block should be rendered as an H2 header
    if block.get("__followers_header", False):
        # Render the Rangers Followers header as an H2 tag
        column_groups = split_lines_by_column(merge_lines(block.get("lines", [])))
        if not column_groups:
            return ""
        
        # Extract the header text
        header_text = ""
        for column_lines in column_groups:
            for line in column_lines:
                plain = line_plain_text(line).strip()
                if plain:
                    header_text = plain
                    break
            if header_text:
                break
        
        if header_text:
            # Generate a slug for the header ID
            import re
            header_slug = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
            # Create H2 tag with inline link back to top
            return f'<h2 id="header-{header_slug}"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> {header_text}</h2>'
        
        return ""
    
    # Don't re-split blocks that have already been assigned to a column
    # (marked with __column_assigned during multi-column rendering)
    if block.get("__column_assigned"):
        merged_lines = merge_lines(block.get("lines", []))
        column_groups = [merged_lines]  # Treat as single column
    else:
        column_groups = split_lines_by_column(merge_lines(block.get("lines", [])))
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
            plain = line_plain_text(line).strip()
            if not plain:
                if current:
                    column_paragraphs.append(current)
                    current = []
                continue
            # Skip page numbers and page artifacts like "3 8", "4 I"
            if plain.isdigit() and len(plain) <= 3:
                continue
            import re as _re_pg
            if (
                len(plain) <= 4
                and (
                    _re_pg.fullmatch(r"[0-9 ]+", plain)  # spaced digits like "3 8"
                    or _re_pg.fullmatch(r"[IVXLCDM ]+", plain)  # roman numerals or spaced roman
                    or _re_pg.fullmatch(r"\d+\s+[IVXLCDM]+", plain)  # "4 I"
                )
            ):
                continue
            html_line = render_line(line)
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
    
    # Check if we should force a break on the first paragraph
    should_force_first_break = block.get("__force_paragraph_break", False)
    
    for para_idx, para in enumerate(paragraphs):
        if not para:
            continue

        # Only apply force-break attribute to the first paragraph of the block
        force_break_attr = ' data-force-break="true"' if (should_force_first_break and para_idx == 0) else ''

        if len(para) == 1 and para[0]["is_heading"]:
            heading_html = para[0]["html"]
            rendered_paragraphs.append(f"<p{force_break_attr}>{heading_html}</p>")
            paragraph_texts.append(_normalize_plain_text(para[0]["plain"]))
            continue

        # Use "html" field directly for entries that have custom formatting (like legend entries)
        # Otherwise use "plain" text
        html_fragments = []
        plain_fragments = []
        for entry in para:
            html_fragments.append(entry["html"])
            plain_fragments.append(_normalize_plain_text(entry["plain"]))
        
        # Join the HTML fragments with spaces
        combined_html = " ".join(html_fragments)
        combined_plain = " ".join([f for f in plain_fragments if f])
        
        # [MERGED_LINES] Apply dehyphenation to the combined HTML to fix cross-line hyphens
        combined_html = dehyphenate_text(combined_html)
        combined_plain = dehyphenate_text(combined_plain)
        
        if not combined_plain:
            continue
            
        rendered_paragraphs.append(f"<p{force_break_attr}>{combined_html}</p>")
        paragraph_texts.append(combined_plain)

    # Check if this block has an attached Initial Character Funds table
    attached_table_html = ""
    if "__initial_character_funds_table" in block:
        # Always render the "Initial Character Funds" H2 header before the table
        # This header identifies the table as per user requirements
        header_id = "header-initial-character-funds"
        header_html = f'<p id="{header_id}">XI.  <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804">Initial Character Funds</span></p>'
        attached_table_html = header_html
        
        # Render the table
        table_data = block["__initial_character_funds_table"]
        attached_table_html += render_table(table_data, table_class="ds-table")
    
    # Check if this block has an attached Bonus to AC table (Chapter 9)
    if "__bonus_ac_table" in block:
        # Render the table
        table_data = block["__bonus_ac_table"]
        attached_table_html += render_table(table_data, table_class="ds-table")
    
    if not rendered_paragraphs:
        # If there are no paragraphs but there's an attached table, return just the table
        return attached_table_html

    final_html: List[str] = []
    final_plain: List[str] = []
    for html_paragraph, plain_paragraph in zip(rendered_paragraphs, paragraph_texts):
        if final_html:
            prev_plain = final_plain[-1]
            # Don't merge if this paragraph has a force-break attribute
            has_force_break = 'data-force-break="true"' in html_paragraph
            if (
                not has_force_break  # New check: don't merge if forced break
                and plain_paragraph
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

    # Append attached table HTML if present
    if attached_table_html:
        final_html.append(attached_table_html)

    return "".join(final_html)




def render_table(table: dict, *, table_class: str | None = None) -> str:
    rows_html: List[str] = []
    header_rows = int(table.get("header_rows", 0) or 0)
    
    # Check if this is a class requirements table by looking at first row
    is_class_requirements_table = False
    if table.get("rows") and len(table["rows"]) > 0:
        first_row = table["rows"][0]
        if first_row.get("cells") and len(first_row["cells"]) > 0:
            first_cell_text = first_row["cells"][0].get("text", "")
            if first_cell_text == "Ability Requirements:":
                is_class_requirements_table = True
    
    for row_index, row in enumerate(table.get("rows", [])):
        cell_tag = "th" if row_index < header_rows else "td"
        cells_html: List[str] = []
        for cell_index, cell in enumerate(row.get("cells", [])):
            attrs: List[str] = []
            rowspan = cell.get("rowspan", 1)
            colspan = cell.get("colspan", 1)
            if rowspan and rowspan > 1:
                attrs.append(f"rowspan=\"{int(rowspan)}\"")
            if colspan and colspan > 1:
                attrs.append(f"colspan=\"{int(colspan)}\"")
            text = cell.get("text")
            # [MERGED_LINES] Apply dehyphenation to table cell text
            if text:
                text = dehyphenate_text(text)
                
                # Special formatting for ability requirements: split multiple abilities onto separate lines
                # This applies to the second column (cell_index 1) of the first row (row_index 0) in class requirements tables
                if is_class_requirements_table and row_index == 0 and cell_index == 1:
                    # Check if text contains multiple ability scores (e.g., "Strength 13 Dexterity 12")
                    # Pattern: AbilityName Number [AbilityName Number]*
                    import re
                    ability_pattern = r'((?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+\d+)'
                    abilities = re.findall(ability_pattern, text)
                    if len(abilities) > 1:
                        # Multiple abilities found - join with line breaks
                        contents = '<br>'.join(html.escape(ability) for ability in abilities)
                    else:
                        # Single ability or doesn't match pattern - use as-is
                        contents = html.escape(text)
                else:
                    contents = html.escape(text)
                
                # Apply bold formatting if cell has bold property
                if cell.get("bold"):
                    contents = f"<strong>{contents}</strong>"
            else:
                contents = "&nbsp;"
            attr_str = " " + " ".join(attrs) if attrs else ""
            cells_html.append(f"<{cell_tag}{attr_str}>{contents}</{cell_tag}>")
        if cells_html:
            rows_html.append(f"<tr>{''.join(cells_html)}</tr>")
    if not rows_html:
        return ""
    # Prefer custom class from table dict, fall back to parameter
    final_class = table.get("class") or table_class
    class_attr = f" class=\"{final_class}\"" if final_class else ""
    return f"<table{class_attr}>{''.join(rows_html)}</table>"


def render_magical_items_list(block: dict, *, paragraph_breaks: List[str]) -> str:
    """Render the Magical Items list from Chapter 10.
    
    This function formats the list of 9 items that appear after "The following items
    are changed to fit DARK SUN campaigns:". Each item follows the format:
    "name: description"
    
    Args:
        block: The block dictionary containing the list
        paragraph_breaks: List of paragraph break patterns
        
    Returns:
        HTML string with the formatted list
    """
    logger.info("Rendering Magical Items list")
    
    # Collect all text from the block
    items = []
    current_item = None
    
    for line in block.get("lines", []):
        line_text = ""
        for span in line.get("spans", []):
            line_text += span.get("text", "")
        line_text = line_text.strip()
        
        # Skip the "campaigns:" line
        if line_text == "campaigns:":
            continue
        
        # Check if this line starts a new item (has a colon and an item name)
        if line.get("__list_item"):
            # Save previous item if exists
            if current_item:
                items.append(current_item)
            
            # Start new item
            # Split on first colon to separate name from description
            if ":" in line_text:
                parts = line_text.split(":", 1)
                item_name = parts[0].strip()
                item_desc = parts[1].strip() if len(parts) > 1 else ""
                current_item = {"name": item_name, "description": item_desc}
                logger.debug(f"Started new item: {item_name}")
        elif current_item and line_text:
            # Continue description from previous line
            if current_item["description"]:
                current_item["description"] += " " + line_text
            else:
                current_item["description"] = line_text
            logger.debug(f"Continuing item {current_item['name']}: {line_text[:40]}")
    
    # Add the last item
    if current_item:
        items.append(current_item)
    
    logger.info(f"Found {len(items)} items in Magical Items list")
    
    # Generate HTML
    if not items:
        logger.warning("No items found in Magical Items list, rendering as normal text block")
        return render_text_block(block, paragraph_breaks=paragraph_breaks)
    
    # Build the list HTML
    list_items = []
    for item in items:
        name_html = f"<span style=\"color: #ca5804\"><strong>{html.escape(item['name'])}:</strong></span>"
        desc_html = html.escape(item["description"])
        list_items.append(f"<p>{name_html} {desc_html}</p>")
    
    return "\n".join(list_items)


def render_magical_item_entry(block: dict, *, paragraph_breaks: List[str]) -> str:
    """Render a single magical item entry from Chapter 10.
    
    Each entry block contains one item in the format " ItemName: description".
    The text has already been properly extracted and cleaned.
    
    Args:
        block: The block dictionary containing the item
        paragraph_breaks: List of paragraph break patterns
        
    Returns:
        HTML string with the formatted item as a single paragraph
    """
    item_name = block.get("__magical_item_entry", "")
    logger.info(f"Rendering magical item entry: {item_name}")
    
    # Get the text from the block
    full_text = ""
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            full_text += span.get("text", "")
    
    full_text = full_text.strip()
    
    # The text should be in format " ItemName: description"
    # Split on the first colon after the item name
    if ":" in full_text and item_name in full_text:
        # Find the colon after the item name
        name_idx = full_text.find(item_name)
        after_name = full_text[name_idx + len(item_name):]
        if ":" in after_name:
            colon_idx = after_name.find(":")
            # Extract name (including the colon)
            name_with_colon = full_text[name_idx:name_idx + len(item_name) + colon_idx + 1].strip()
            # Extract description (everything after the colon)
            description = after_name[colon_idx + 1:].strip()
            
            # Format as colored/bolded name followed by description
            name_html = f"<span style=\"color: #ca5804\"><strong>{html.escape(name_with_colon)}</strong></span>"
            desc_html = html.escape(description)
            
            return f"<p>{name_html} {desc_html}</p>"
    
    # Fallback: just render as normal paragraph with colored text
    logger.warning(f"Could not parse item entry for {item_name}, using fallback rendering")
    return f"<p><span style=\"color: #ca5804\">{html.escape(full_text)}</span></p>"


def render_page(
    page: dict,
    *,
    include_tables: bool,
    table_class: str | None,
    wrap_pages: bool,
    paragraph_breaks: List[str],
) -> str:
    import logging
    logger = logging.getLogger(__name__)
    page_num = page.get("page", -1)
    num_blocks = len(page.get("blocks", []))
    num_tables = len(page.get("tables", []))
    
    # Debug for page 1 (where Gem Table should be)
    if num_blocks == 15:  # This is likely page 1 of chapter 10
        logger.warning(f"=" * 80)
        logger.warning(f"render_page called with {num_blocks} blocks (page {page_num})")
        logger.warning(f"Blocks 0-9:")
        for idx, block in enumerate(page.get("blocks", [])[:10]):
            text = ""
            has_gem_table = '__gem_table' in block
            skip = block.get('__skip_render', False)
            for line in block.get('lines', [])[:1]:
                for span in line.get('spans', [])[:1]:
                    text = span.get('text', '')[:40]
            logger.warning(f"  Block {idx}: __gem_table={has_gem_table}, __skip={skip}, text='{text}'")
        logger.warning(f"=" * 80)
    
    if num_tables > 0:
        logger.info(f"_render_page called for page {page_num} with {num_tables} tables, include_tables={include_tables}")
    
    # Debug: Check blocks at start of _render_page
    if page.get("page_number") == 66:
        import time
        render_id = int(time.time() * 1000) % 100000
        with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
            f.write(f"\n=== _render_page START for page 66 (ID:{render_id}) ===\n")
            for idx, block in enumerate(page.get("blocks", [])[:5]):
                bbox_val = block.get("bbox", "NOT_SET")
                skip_val = block.get("__skip_render", "NOT_SET")
                text = ""
                if block.get("lines") and len(block["lines"]) > 0:
                    if block["lines"][0].get("spans") and len(block["lines"][0]["spans"]) > 0:
                        text = block["lines"][0]["spans"][0].get("text", "")[:50]
                f.write(f"Block {idx}: bbox={bbox_val}, __skip_render={skip_val}, text='{text}'\n")
            f.write(f"render_id={render_id}\n")
    
    def _render_item(meta) -> str:
        kind = meta["kind"]
        payload = meta["payload"]
        
        # Debug: Check for Rangers Followers marker
        if kind == "block" and "__rangers_followers_table" in payload:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"_render_item: Found Rangers Followers marker block!")
        
        # Debug: Check all blocks for the table marker
        if kind == "block" and "__initial_character_funds_table" in payload:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"\n=== _render_item called with table marker! ===\n")
                f.write(f"payload type: {payload.get('type')}\n")
                f.write(f"payload keys: {list(payload.keys())}\n")
        
        if kind == "block":
            # Debug chapter 8 blocks
            if payload.get("lines"):
                for line in payload.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if text.startswith('*For gladiators') or text.startswith('**The thief'):
                            with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                bbox = payload.get('bbox', [])
                                f.write(f"FOUND legend block in rendering:\n")
                                f.write(f"  type={payload.get('type')}\n")
                                f.write(f"  bbox={bbox}\n")
                                f.write(f"  __skip_render={payload.get('__skip_render')}\n")
                                f.write(f"  id(payload)={id(payload)}\n")
                                f.write(f"  text='{text[:80]}'\n")
                                f.write(f"  Will render: {payload.get('__skip_render') != True}\n")
            
            if payload.get("type") != "text":
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    if "__initial_character_funds_table" in payload:
                        f.write(f"SKIPPING block because type != 'text' (type={payload.get('type')})\n")
                return ""
            # Debug: Log blocks that might be the problem headers
            if payload.get("lines") and len(payload["lines"]) > 0:
                first_line_text = payload["lines"][0].get("spans", [{}])[0].get("text", "").strip()
                if first_line_text in ["Cost", "Material", "Wt .", "Dmg*", "Hit Prob.**"]:
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"\n=== Rendering potential problem header: '{first_line_text}' ===\n")
                        f.write(f"  Has __skip_render: {payload.get('__skip_render', False)}\n")
                        f.write(f"  Has __weapon_materials_table: {'__weapon_materials_table' in payload}\n")
            
            # Skip blocks marked for removal
            if payload.get("__skip_render"):
                import logging
                logger = logging.getLogger(__name__)
                first_line_text = ""
                if payload.get("lines") and len(payload["lines"]) > 0:
                    first_line_text = payload["lines"][0].get("spans", [{}])[0].get("text", "")[:40]
                logger.info(f"SKIPPING block with __skip_render, text='{first_line_text}'")
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"SKIPPING block with __skip_render marker, first line: '{first_line_text}'\n")
                # Debug: Check if this is a legend block being skipped
                if payload.get("__legend_entry"):
                    with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                        f.write(f"WARNING: Skipping legend block with __skip_render: '{first_line_text}'\n")
                return ""
            # Check for special Monster Stats table marker (Chapter 5)
            if "__monster_stats_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                print(f"\n🐉 RENDERING MONSTER STATS TABLE!")
                logger.info("Rendering Monster Stats table from marker block")
                table_data = payload["__monster_stats_table"]
                print(f"  Table has {len(table_data.get('rows', []))} rows")
                result = render_table(table_data, table_class=table_class)
                print(f"  Generated {len(result)} chars of HTML")
                return result
            # Check for special Class Requirements table marker
            if "__class_requirements_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Rendering Class Requirements table from marker block")
                table_data = payload["__class_requirements_table"]
                return render_table(table_data, table_class=table_class)
            # Check for special Rangers Followers table marker
            if "__rangers_followers_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Rendering Rangers Followers table from marker block")
                table_data = payload["__rangers_followers_table"]
                return render_table(table_data, table_class=table_class)
            # Check for special Common Wages table marker
            if "__common_wages_table" in payload:
                table_data = payload["__common_wages_table"]
                return render_table(table_data, table_class=table_class)
            # Check for special Initial Character Funds table marker
            if "__initial_character_funds_table" in payload:
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"\n=== Rendering Initial Character Funds table ===\n")
                table_data = payload["__initial_character_funds_table"]
                result = render_table(table_data, table_class=table_class)
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"Table HTML length: {len(result)} chars\n")
                return result
            # Check for special Weapon Materials table marker
            if "__weapon_materials_table" in payload:
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"\n=== Rendering Weapon Materials table ===\n")
                table_data = payload["__weapon_materials_table"]
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"Table data type: {type(table_data)}\n")
                    f.write(f"Table data keys: {list(table_data.keys()) if isinstance(table_data, dict) else 'N/A'}\n")
                    f.write(f"Table data rows: {len(table_data.get('rows', []))} rows\n")
                try:
                    # Render the header text first, then the table
                    header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                    table_html = render_table(table_data, table_class=table_class)
                    result = header_html + table_html
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"Header HTML length: {len(header_html)} chars\n")
                        f.write(f"Table HTML length: {len(table_html)} chars\n")
                    return result
                except Exception as e:
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"ERROR rendering table: {e}\n")
                        import traceback
                        f.write(f"Traceback: {traceback.format_exc()}\n")
                    return ""
            # Check for Household Provisions table marker
            if "__household_provisions_table" in payload:
                table_data = payload["__household_provisions_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Barding table marker
            if "__barding_table" in payload:
                table_data = payload["__barding_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Lair Treasures table marker (Chapter 10)
            if "__lair_treasures_table" in payload:
                table_data = payload["__lair_treasures_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Individual Treasures table marker (Chapter 10)
            if "__individual_treasures_table" in payload:
                table_data = payload["__individual_treasures_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Gem Table marker (Chapter 10)
            if "__gem_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("=" * 80)
                logger.warning("🎯 RENDERING GEM TABLE!")
                logger.warning(f"Page info: page={page.get('page')}, page_number={page.get('page_number')}")
                table_data = payload["__gem_table"]
                logger.warning(f"Gem Table has {len(table_data.get('rows', []))} rows")
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                logger.warning(f"Header HTML: {len(header_html)} chars, Table HTML: {len(table_html)} chars")
                result = header_html + table_html
                logger.warning(f"Total result: {len(result)} chars")
                logger.warning(f"First 200 chars: {result[:200]}")
                logger.warning("=" * 80)
                return result
            # Check for Magical Items List marker (Chapter 10)
            if "__magical_items_list" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Found Magical Items List marker in rendering!")
                return render_magical_items_list(payload, paragraph_breaks=paragraph_breaks)
            # Check for Magical Item Entry marker (Chapter 10)
            if "__magical_item_entry" in payload:
                import logging
                logger = logging.getLogger(__name__)
                item_name = payload["__magical_item_entry"]
                logger.info(f"Rendering magical item entry: {item_name}")
                result = render_magical_item_entry(payload, paragraph_breaks=paragraph_breaks)
                return result
            # Check for Transport table marker
            if "__transport_table" in payload:
                table_data = payload["__transport_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Animals table marker
            if "__animals_table" in payload:
                table_data = payload["__animals_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for New Weapons table marker
            if "__new_weapons_table" in payload:
                table_data = payload["__new_weapons_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Bard Poison table marker (Chapter 3)
            if "__bard_poison_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Found Bard Poison Table marker in rendering!")
                table_data = payload["__bard_poison_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                logger.info(f"Header HTML length: {len(header_html)}, Table HTML length: {len(table_html)}")
                return header_html + table_html
            # Check for Dexterity Adjustments table marker (Chapter 3)
            if "__dexterity_adjustments_table" in payload:
                table_data = payload["__dexterity_adjustments_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Racial Adjustments table marker (Chapter 3)
            if "__racial_adjustments_table" in payload:
                table_data = payload["__racial_adjustments_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Overland Movement table marker (Chapter 14)
            if "overland_movement_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Rendering Overland Movement table from marker")
                
                table_marker = payload["overland_movement_table"]
                headers = table_marker.get("headers", [])
                rows_data = table_marker.get("rows", [])
                legend = table_marker.get("legend", [])
                
                # Build table structure for render_table
                table_rows = []
                
                # Add header row
                header_row = {
                    "cells": [{"text": h} for h in headers]
                }
                table_rows.append(header_row)
                
                # Add data rows
                for row_data in rows_data:
                    row = {
                        "cells": [
                            {"text": row_data.get("race", "")},
                            {"text": row_data.get("movement_points", "")},
                            {"text": row_data.get("force_march", "")}
                        ]
                    }
                    table_rows.append(row)
                
                table_data = {
                    "rows": table_rows,
                    "header_rows": 1
                }
                
                # Render table
                table_html = render_table(table_data, table_class=table_class)
                
                # Render legend as a paragraph below the table
                legend_html = ""
                if legend:
                    legend_items = " ".join(legend)
                    legend_html = f"<p>{legend_items}</p>\n"
                
                logger.info(f"Rendered Overland Movement table with {len(rows_data)} rows")
                return table_html + legend_html
            # Check for Terrain Costs table marker (Chapter 14)
            if "terrain_costs_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("🎯 Rendering Terrain Costs table from marker!")
                
                table_marker = payload["terrain_costs_table"]
                headers = table_marker.get("headers", [])
                rows_data = table_marker.get("rows", [])
                
                # Build table structure for render_table
                table_rows = []
                
                # Add header row
                header_row = {
                    "cells": [{"text": h} for h in headers]
                }
                table_rows.append(header_row)
                
                # Add data rows
                for row_data in rows_data:
                    row = {
                        "cells": [
                            {"text": row_data.get("terrain_type", "")},
                            {"text": row_data.get("movement_cost", "")}
                        ]
                    }
                    table_rows.append(row)
                
                table_data = {
                    "rows": table_rows,
                    "header_rows": 1
                }
                
                # Render table
                table_html = render_table(table_data, table_class=table_class)
                
                logger.info(f"Rendered Terrain Costs table with {len(rows_data)} rows")
                return table_html
            
            # Check for Mounted Movement table marker (Chapter 14)
            if "mounted_movement_table" in payload:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("🎯 Rendering Mounted Movement table from marker!")
                
                table_marker = payload["mounted_movement_table"]
                headers = table_marker.get("headers", [])
                rows_data = table_marker.get("rows", [])
                
                # Build table structure for render_table
                table_rows = []
                
                # Add header row
                header_row = {
                    "cells": [{"text": h} for h in headers]
                }
                table_rows.append(header_row)
                
                # Add data rows
                for row_data in rows_data:
                    row = {
                        "cells": [
                            {"text": row_data.get("mount", "")},
                            {"text": row_data.get("movement_points", "")}
                        ]
                    }
                    table_rows.append(row)
                
                table_data = {
                    "rows": table_rows,
                    "header_rows": 1
                }
                
                # Render table
                table_html = render_table(table_data, table_class=table_class)
                
                logger.info(f"Rendered Mounted Movement table with {len(rows_data)} rows")
                return table_html
            
            # Check for Bonus to AC table marker (Chapter 9)
            # NOTE: This code path is no longer used since we now insert the table directly into the page's tables list
            # Keeping it here for reference in case we need to revert to the marker approach
            if "__bonus_ac_table" in payload:
                table_data = payload["__bonus_ac_table"]
                header_html = render_text_block(payload, paragraph_breaks=paragraph_breaks)
                table_html = render_table(table_data, table_class=table_class)
                return header_html + table_html
            # Check for Section Header marker (Chapter 8, Chapter 9)
            if "__section_header" in payload:
                header_text = payload.get("__header_text", "")
                header_level = payload.get("__header_level", 2)  # Default to H2
                header_id = f"header-{header_text.lower().replace(' ', '-')}"
                return f'<h{header_level} id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h{header_level}>'
            
            # Check for __render_as_h1 marker (Chapter 8)
            # Render as a colored span so it goes through _add_header_anchors and gets roman numerals
            if "__render_as_h1" in payload:
                header_text = payload.get("__header_text", "Individual Class Awards")
                return f'<p><span class="header-h1" style="color: #ca5804">{header_text}</span></p>'
            
            # Check for __render_as_h2 marker (Chapter 8)
            if "__render_as_h2" in payload:
                header_text = payload.get("__header_text", "Individual Class Awards")
                header_id = f"header-{header_text.lower().replace(' ', '-')}"
                
                # Add debug logging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"🎯 _render_item: Rendering H2 header: '{header_text}'")
                
                return f'<h2 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h2>'
            
            # Check for __render_as_h3 marker (Chapter 15)
            if "__render_as_h3" in payload:
                header_text = payload.get("__header_text", "Unknown")
                header_id = f"header-{header_text.lower().replace(' ', '-')}"
                
                # Add debug logging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"🎯 _render_item: Rendering H3 header: '{header_text}'")
                
                return f'<h3 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h3>'
            
            # Check for __render_as_h4 marker (Chapter 3 Geography)
            if "__render_as_h4" in payload:
                header_text = payload.get("__header_text", "Unknown")
                header_id = f"header-{header_text.lower().replace(' ', '-')}"
                
                # Add debug logging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"🎯 _render_item: Rendering H4 header: '{header_text}'")
                
                return f'<h4 id="{header_id}">{header_text} <a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a></h4>'
            
            # Check for __render_as_race_description_h2_with_content marker (Chapter 8)
            # Race header is in the same block as content - extract and render separately
            if "__render_as_race_description_h2_with_content" in payload:
                race_name = payload.get("__race_name", "Unknown")
                # Extract content (everything except the first span of the first line)
                content_text = ""
                if payload.get("lines"):
                    first_line = payload["lines"][0]
                    if first_line.get("spans") and len(first_line["spans"]) > 1:
                        # Skip first span (the header), get rest of first line
                        for span in first_line["spans"][1:]:
                            content_text += span.get("text", "")
                    # Add remaining lines
                    for line in payload["lines"][1:]:
                        for span in line.get("spans", []):
                            content_text += " " + span.get("text", "")
                
                content_text = content_text.strip()
                # Render header and content together
                return f'<p><span class="header-h2" style="color: #ca5804; font-size: 0.9em">{race_name}:</span></p><p>{content_text}</p>'
            
            # Check for __render_as_race_description_h2 marker (Chapter 8)
            # These are race name headers in the descriptive section
            if "__render_as_race_description_h2" in payload:
                race_name = payload.get("__race_name", "Unknown")
                # Render as a paragraph with H2 styling (class="header-h2")
                # This ensures it gets picked up as H2 by the TOC generator
                return f'<p><span class="header-h2" style="color: #ca5804; font-size: 0.9em">{race_name}:</span></p>'
            
            # Check for __render_as_h3_with_list marker (Chapter 8 - trust test headers with lists)
            if "__render_as_h3_with_list" in payload:
                h3_text = payload.get("__h3_text", "Unknown")
                list_items = payload.get("__list_items", [])
                
                # Build the HTML with H3 header and unordered list
                html_output = f'<h3>{h3_text}</h3>\n<ul>\n'
                for item in list_items:
                    html_output += f'  <li>{item}</li>\n'
                html_output += '</ul>'
                return html_output
            
            # Check for Class Award table marker (Chapter 8)
            if "__class_award_table" in payload:
                with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                    f.write(f"Rendering class award table: {payload.get('__table_header', 'UNKNOWN')}\\n")
                table_header = payload.get("__table_header", "")
                table_rows = payload.get("__table_rows", [])
                # Render the table header as H2 (using paragraph style like other chapters)
                header_id = f"header-class-award-{table_header.lower().replace(':', '').replace(' ', '-')}"
                # Extract just the class name without the colon for the header text
                # Also normalize text by removing extra spaces (e.g., "M u l" -> "Mul")
                header_text = table_header.rstrip(':').strip()
                # Collapse multiple spaces into single spaces
                header_text = re.sub(r'\s+', ' ', header_text)
                # For specific cases like "M u l" (spaces between letters), remove all spaces
                if header_text == "M u l":
                    header_text = "Mul"
                # Use the same rendering style as other H2 headers (paragraph with class on p, inline style on span)
                header_html = f'<p id="{header_id}" class="h2-header"><a href="#top" style="font-size: 0.8em; text-decoration: none;">[^]</a> <span style="color: #ca5804; font-size: 0.9em">{header_text}</span></p>'
                # Build table data structure for _render_table
                table_data = {
                    "header_rows": 1,
                    "rows": [
                        {
                            "cells": [
                                {"text": "Action", "bold": True},
                                {"text": "Awards", "bold": True},
                            ]
                        }
                    ]
                }
                # Add data rows
                for row in table_rows:
                    if len(row) == 2:
                        table_data["rows"].append({
                            "cells": [
                                {"text": row[0]},
                                {"text": row[1]},
                            ]
                        })
                    elif len(row) == 1:
                        # Single-cell row (action with no award yet, or award with no action)
                        # This might be a fragment, render as is
                        table_data["rows"].append({
                            "cells": [
                                {"text": row[0]},
                                {"text": ""},
                            ]
                        })
                table_html = render_table(table_data, table_class=table_class)
                
                # Check for legend entries attached to this table
                legend_html = ""
                if "__legend_entries" in payload:
                    legend_entries = payload["__legend_entries"]
                    for legend_text in legend_entries:
                        # Render each legend as a paragraph with force-break to prevent merging
                        legend_html += f'<p data-force-break="true">{html.escape(legend_text)}</p>'
                    with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                        f.write(f"Rendered {len(legend_entries)} legend entries for {table_header}\n")
                
                return header_html + table_html + legend_html
            # All other text blocks render here (including our legend)
            # Debug: Check if legend blocks are reaching this point
            if payload.get("lines"):
                for line in payload.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if text.startswith('*For gladiators') or text.startswith('**The thief'):
                            with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                bbox = payload.get("bbox", [])
                                f.write(f"About to render text block: bbox={bbox}, text='{text[:60]}'\n")
            result = render_text_block(payload, paragraph_breaks=paragraph_breaks)
            # Debug: Check rendering result
            if payload.get("lines"):
                for line in payload.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if text.startswith('*For gladiators') or text.startswith('**The thief'):
                            with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                f.write(f"Rendered result length={len(result)}, content='{result[:200]}'\n")
            return result
        if kind == "table":
            return render_table(payload, table_class=table_class)
        return ""

    page_width = float(page.get("width", 0) or 0)
    column_threshold = max(page_width * 0.08, 60.0) if page_width else 60.0
    column_min_width = page_width * 0.25 if page_width else 150.0
    full_width_cutoff = page_width * 0.7 if page_width else float("inf")

    items_meta = []
    order_counter = 0
    block_counter = 0  # Track block index for debugging
    for block in page.get("blocks", []):
        bbox = [float(coord) for coord in block.get("bbox", [0, 0, 0, 0])]
        # Debug chapter 8 legend blocks
        if block.get("lines"):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if text.startswith('*For gladiators'):
                        with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                            f.write(f"Building meta: Block index {block_counter}, order {order_counter}\n")
                            f.write(f"  bbox (extracted)={bbox}\n")
                            f.write(f"  block.get('bbox')={block.get('bbox', 'NOT_SET')}\n")
                            f.write(f"  __skip_render={block.get('__skip_render')}\n")
                            # Check if this block will be skipped
                            will_skip = bbox == [0.0, 0.0, 0.0, 0.0]
                            f.write(f"  Will be skipped due to zero bbox: {will_skip}\n")
        block_counter += 1
        
        # Skip blocks that have been cleared (bbox set to [0, 0, 0, 0])
        # These are blocks that were marked for removal during processing
        if bbox == [0.0, 0.0, 0.0, 0.0]:
            continue
        
        # Debug: Check for Rangers Followers marker
        if "__rangers_followers_table" in block:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Building items_meta: Found __rangers_followers_table marker at order {order_counter}, bbox={bbox}")
        
        # Debug: Check if this block has the table marker or skip marker
        if "__initial_character_funds_table" in block:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"\n=== Found __initial_character_funds_table marker in block while building meta (order {order_counter}) ===\n")
        if "__weapon_materials_table" in block:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"\n=== Found __weapon_materials_table marker in block while building meta (order {order_counter}) ===\n")
        if block.get("__skip_render"):
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                first_line = ""
                if block.get('lines') and len(block['lines']) > 0:
                    first_line = block['lines'][0].get('spans', [{}])[0].get('text', '')[:30]
                f.write(f"\n=== Found __skip_render marker in block while building meta (order {order_counter}), first line: '{first_line}' ===\n")
        
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
        for table_idx, table in enumerate(page.get("tables", [])):
            # Skip tables marked for removal
            if table.get("__skip_render"):
                import logging
                logger = logging.getLogger(__name__)
                rows = table.get("rows", [])
                first_cell = ""
                if rows and rows[0].get("cells"):
                    first_cell = rows[0]["cells"][0].get("text", "")[:30]
                logger.info(f"Skipping table {table_idx} with __skip_render=True, first_cell='{first_cell}'")
                continue
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
    
    # Check if this page should force single-column rendering
    if page.get("__force_single_column"):
        print(f"  🎯 Forcing single-column rendering for page {page.get('page_number', '?')}")
        columns = []  # Force single-column mode

    if len(columns) <= 1:
        # Debug: Check if we're rendering in single-column mode
        has_table_marker = any("__initial_character_funds_table" in meta.get("payload", {}) for meta in items_meta)
        has_weapon_table_marker = any("__weapon_materials_table" in meta.get("payload", {}) for meta in items_meta)
        if has_table_marker or has_weapon_table_marker:
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"\n=== Single-column rendering mode, table marker in items_meta ===\n")
                if has_table_marker:
                    f.write(f"  Has __initial_character_funds_table\n")
                if has_weapon_table_marker:
                    f.write(f"  Has __weapon_materials_table\n")
        
        # If the page forces single-column, sort by order index to preserve block sequence
        # Otherwise, sort by Y-coordinate for natural reading order
        if page.get("__force_single_column"):
            ordered_html: List[str] = []
            for meta in sorted(items_meta, key=lambda m: m["order"]):
                # Debug: Check payload bbox before calling _render_item
                payload = meta.get("payload", {})
                if payload.get("lines"):
                    for line in payload.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.startswith('*For gladiators'):
                                with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                    f.write(f"\nBEFORE _render_item:\n")
                                    f.write(f"  meta['bbox']={meta.get('bbox')}\n")
                                    f.write(f"  payload.get('bbox')={payload.get('bbox', 'NOT_SET')}\n")
                                    f.write(f"  text='{text[:50]}'\n")
                
                if "__initial_character_funds_table" in meta.get("payload", {}):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"About to call _render_item for __initial_character_funds_table block\n")
                if "__weapon_materials_table" in meta.get("payload", {}):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"About to call _render_item for __weapon_materials_table block\n")
                html_piece = _render_item(meta)
                if html_piece:
                    ordered_html.append(html_piece)
        else:
            ordered_html: List[str] = []
            for meta in sorted(items_meta, key=lambda m: (m["y"], m["x"], m["order"])):
                # Debug: Check payload bbox before calling _render_item
                payload = meta.get("payload", {})
                if payload.get("lines"):
                    for line in payload.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if text.startswith('*For gladiators'):
                                with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                    f.write(f"\nBEFORE _render_item:\n")
                                    f.write(f"  meta['bbox']={meta.get('bbox')}\n")
                                    f.write(f"  payload.get('bbox')={payload.get('bbox', 'NOT_SET')}\n")
                                    f.write(f"  text='{text[:50]}'\n")
                
                if "__initial_character_funds_table" in meta.get("payload", {}):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"About to call _render_item for __initial_character_funds_table block\n")
                if "__weapon_materials_table" in meta.get("payload", {}):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"About to call _render_item for __weapon_materials_table block\n")
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

    def _is_height_weight_table(table_payload: dict) -> bool:
        try:
            rows = table_payload.get("rows", [])
            header_rows = int(table_payload.get("header_rows", 0) or 0)
            scan_rows = rows[: max(header_rows, 2)]
            header_text = " ".join(
                cell.get("text", "") for row in scan_rows for cell in row.get("cells", [])
            ).lower()
            return ("height in inches" in header_text) and ("weight in pounds" in header_text)
        except Exception:
            return False
    
    def _is_starting_age_table(table_payload: dict) -> bool:
        try:
            rows = table_payload.get("rows", [])
            header_rows = int(table_payload.get("header_rows", 0) or 0)
            scan_rows = rows[: max(header_rows, 1)]
            header_text = " ".join(
                cell.get("text", "") for row in scan_rows for cell in row.get("cells", [])
            ).lower()
            return ("base age" in header_text) and ("variable" in header_text) and ("age range" in header_text)
        except Exception:
            return False

    # Debug: Check if table marker is in items_meta for multi-column rendering
    has_table_marker = any("__initial_character_funds_table" in meta.get("payload", {}) for meta in items_meta)
    has_weapon_table_marker = any("__weapon_materials_table" in meta.get("payload", {}) for meta in items_meta)
    if has_table_marker or has_weapon_table_marker:
        with open('/tmp/chapter6_debug.txt', 'a') as f:
            f.write(f"\n=== Multi-column rendering mode ({len(columns)} columns), table marker in items_meta ===\n")
            if has_table_marker:
                f.write(f"  Has __initial_character_funds_table\n")
            if has_weapon_table_marker:
                f.write(f"  Has __weapon_materials_table\n")
    
    for meta in items_meta:
        width = meta["width"]
        kind = meta["kind"]
        
        # Debug: Check if this is the table block
        if "__initial_character_funds_table" in meta.get("payload", {}):
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"Processing __initial_character_funds_table block: width={width}, full_width_cutoff={full_width_cutoff}, kind={kind}, type={meta['payload'].get('type')}\n")
        if "__weapon_materials_table" in meta.get("payload", {}):
            with open('/tmp/chapter6_debug.txt', 'a') as f:
                f.write(f"Processing __weapon_materials_table block: width={width}, full_width_cutoff={full_width_cutoff}, kind={kind}, type={meta['payload'].get('type')}\n")
        
        # Special tables and their headers should always be full-width
        has_special_table = (
            "__rangers_followers_table" in meta.get("payload", {}) or
            "__common_wages_table" in meta.get("payload", {}) or
            "__initial_character_funds_table" in meta.get("payload", {}) or
            "__weapon_materials_table" in meta.get("payload", {}) or
            "__household_provisions_table" in meta.get("payload", {}) or
            "__barding_table" in meta.get("payload", {}) or
            "__transport_table" in meta.get("payload", {}) or
            "__animals_table" in meta.get("payload", {}) or
            "__new_weapons_table" in meta.get("payload", {}) or
            "__class_award_table" in meta.get("payload", {}) or
            "__section_header" in meta.get("payload", {}) or
            "__force_sequential_order" in meta.get("payload", {}) or
            meta.get("payload", {}).get("__followers_header", False)
        )
        
        if width >= full_width_cutoff or (kind == "block" and meta["payload"].get("type") != "text") or has_special_table:
            full_width_items.append(meta)
            if "__initial_character_funds_table" in meta.get("payload", {}):
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"__initial_character_funds_table block added to full_width_items (has_special_table={has_special_table})\n")
            if "__weapon_materials_table" in meta.get("payload", {}):
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"__weapon_materials_table block added to full_width_items (has_special_table={has_special_table})\n")
            continue
        if kind == "table":
            # Treat Height & Weight and Starting Age tables as full-width to preserve ordering
            if _is_height_weight_table(meta["payload"]) or _is_starting_age_table(meta["payload"]):
                full_width_items.append(meta)
            else:
                target_idx = min(range(len(columns)), key=lambda i: abs(meta["center"] - columns[i]))
                column_buckets[target_idx].append(meta)
            continue
        column_idx = min(range(len(columns)), key=lambda i: abs(meta["center"] - columns[i]))
        column_buckets[column_idx].append(meta)

    full_width_items.sort(key=lambda m: (m["y"], m["x"], m["order"]))

    def _coalesce_column_items(items: List[dict]) -> List[dict]:
        combined: List[dict] = []
        buffer: dict | None = None
        for idx, meta in enumerate(items):
            if meta["kind"] != "block" or meta["payload"].get("type") != "text":
                if buffer is not None:
                    combined.append(buffer)
                    buffer = None
                combined.append(meta)
                continue

            # Don't coalesce if this block has a force paragraph break marker, skip render marker, header marker, special rendering marker, table marker, or class award table marker
            if (meta["payload"].get("__force_paragraph_break") or 
                meta["payload"].get("__skip_render") or
                meta["payload"].get("__followers_header") or
                meta["payload"].get("_render_as") or
                meta["payload"].get("__class_award_table") or
                meta["payload"].get("__section_header") or
                meta["payload"].get("__render_as_h1") or
                meta["payload"].get("__render_as_h2") or
                meta["payload"].get("__render_as_h3") or
                meta["payload"].get("__render_as_h4") or
                meta["payload"].get("__render_as_race_description_h2") or
                meta["payload"].get("__render_as_race_description_h2_with_content") or
                meta["payload"].get("__render_as_h3_with_list") or
                # Table markers
                meta["payload"].get("__rangers_followers_table") or
                meta["payload"].get("__common_wages_table") or
                meta["payload"].get("__initial_character_funds_table") or
                meta["payload"].get("__weapon_materials_table") or
                meta["payload"].get("__household_provisions_table") or
                meta["payload"].get("__barding_table") or
                meta["payload"].get("__lair_treasures_table") or
                meta["payload"].get("__individual_treasures_table") or
                meta["payload"].get("__gem_table") or
                meta["payload"].get("__magical_items_list") or
                meta["payload"].get("__magical_item_entry") or
                meta["payload"].get("__transport_table") or
                meta["payload"].get("__animals_table") or
                meta["payload"].get("__new_weapons_table") or
                meta["payload"].get("__bard_poison_table") or
                meta["payload"].get("__dexterity_adjustments_table") or
                meta["payload"].get("__racial_adjustments_table") or
                meta["payload"].get("__wilderness_encounter_table") or
                meta["payload"].get("__bonus_ac_table") or
                meta["payload"].get("overland_movement_table") or
                meta["payload"].get("terrain_costs_table") or
                meta["payload"].get("mounted_movement_table") or
                meta["payload"].get("__class_requirements_table")):
                if buffer is not None:
                    combined.append(buffer)
                    buffer = None
                # Mark this block as column-assigned to prevent re-splitting
                meta["payload"]["__column_assigned"] = True
                combined.append(meta)
                continue

            # Normal text block - add to buffer for coalescing
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
                # Preserve header markers
                if meta["payload"].get("__followers_header"):
                    buffer["payload"]["__followers_header"] = True
                # Preserve table markers
                if meta["payload"].get("__class_requirements_table"):
                    buffer["payload"]["__class_requirements_table"] = meta["payload"]["__class_requirements_table"]
                # Preserve render-as markers (Chapter 15)
                if meta["payload"].get("__render_as_h2"):
                    buffer["payload"]["__render_as_h2"] = True
                    buffer["payload"]["__header_text"] = meta["payload"].get("__header_text")
                if meta["payload"].get("__render_as_h3"):
                    buffer["payload"]["__render_as_h3"] = True
                    buffer["payload"]["__header_text"] = meta["payload"].get("__header_text")
                if meta["payload"].get("__render_as_h4"):
                    buffer["payload"]["__render_as_h4"] = True
                    buffer["payload"]["__header_text"] = meta["payload"].get("__header_text")
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

        # Flush any remaining buffer after the loop
        if buffer is not None:
            combined.append(buffer)
        return combined

    # Sort columns by their X-coordinate (left to right), not just by index
    column_order = sorted(column_buckets.keys(), key=lambda idx: columns[idx])
    
    for idx in column_order:
        # For blocks marked with __force_sequential_order, use their original order index
        # instead of Y-coordinate sorting
        def sort_key(m):
            payload = m.get("payload", {})
            if payload.get("__force_sequential_order"):
                # Use order index as primary sort key for sequential blocks
                return (m["order"], 0, 0)
            else:
                # Use Y-coordinate as primary sort key for normal blocks
                return (99999 + m["y"], m["x"], m["order"])
        
        column_buckets[idx].sort(key=sort_key)
        column_buckets[idx] = _coalesce_column_items(column_buckets[idx])

    ordered_html: List[str] = []
    full_index = 0

    def consume_full(upto_y: float) -> None:
        nonlocal full_index
        while full_index < len(full_width_items) and full_width_items[full_index]["y"] <= upto_y:
            item = full_width_items[full_index]
            
            # Debug: Check if Forgotten Realms header is in full_width_items
            if item.get("payload", {}).get("__render_as_h2"):
                import logging
                logger = logging.getLogger(__name__)
                header_text = item.get("payload", {}).get("__header_text", "Unknown")
                logger.warning(f"🔍 consume_full: Processing header '{header_text}' as full-width item")
            
            if "__weapon_materials_table" in item.get("payload", {}):
                with open('/tmp/chapter6_debug.txt', 'a') as f:
                    f.write(f"consume_full: Rendering __weapon_materials_table at y={item['y']}, upto_y={upto_y}\n")
            html_piece = _render_item(item)
            
            # Debug: Check if html was generated
            if item.get("payload", {}).get("__render_as_h2"):
                logger.warning(f"🔍 consume_full: After _render_item for '{header_text}', html_piece length={len(html_piece) if html_piece else 0}")
            
            if html_piece:
                ordered_html.append(html_piece)
                if "__weapon_materials_table" in item.get("payload", {}):
                    with open('/tmp/chapter6_debug.txt', 'a') as f:
                        f.write(f"consume_full: Appended __weapon_materials_table HTML (length {len(html_piece)})\n")
            full_index += 1

    for idx in column_order:
        for meta in column_buckets[idx]:
            # Debug: Check payload bbox before calling _render_item
            payload = meta.get("payload", {})
            if payload.get("lines"):
                for line in payload.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "")
                        if text.startswith('*For gladiators'):
                            with open('/tmp/chapter8_rendering_debug.txt', 'a') as f:
                                f.write(f"\nBEFORE _render_item (column {idx}):\n")
                                f.write(f"  meta['bbox']={meta.get('bbox')}\n")
                                f.write(f"  payload.get('bbox')={payload.get('bbox', 'NOT_SET')}\n")
                                f.write(f"  text='{text[:50]}'\n")
            
            consume_full(meta["y"])
            html_piece = _render_item(meta)
            
            # Debug: Check if Forgotten Realms header is being generated but discarded
            if meta.get("payload", {}).get("__render_as_h2"):
                import logging
                logger = logging.getLogger(__name__)
                header_text = meta.get("payload", {}).get("__header_text", "Unknown")
                logger.warning(f"🔍 After _render_item: header='{header_text}', html_piece length={len(html_piece) if html_piece else 0}, is_truthy={bool(html_piece)}")
                if not html_piece:
                    logger.error(f"❌ EMPTY HTML for header '{header_text}'!")
            
            if html_piece:
                ordered_html.append(html_piece)

    consume_full(float("inf"))

    if not ordered_html:
        return ""

    page_html = "".join(ordered_html)
    page_html = merge_adjacent_paragraph_html(page_html)
    page_html = wrap_spell_list_items(page_html)
    if wrap_pages:
        return f"<section data-page=\"{page.get('page_number')}\">{page_html}</section>"
    return page_html




def render_pages(
    pages: Iterable[dict],
    *,
    include_tables: bool,
    table_class: str | None,
    wrap_pages: bool,
    paragraph_breaks: List[str],
) -> str:
    import logging
    logger = logging.getLogger(__name__)
    snippets = []
    for page_idx, page in enumerate(pages):
        snippet = render_page(
            page,
            include_tables=include_tables,
            table_class=table_class,
            wrap_pages=wrap_pages,
            paragraph_breaks=paragraph_breaks,
        )
        if snippet:
            snippets.append(snippet)
            logger.debug(f"Page {page_idx}: Generated {len(snippet)} chars of HTML")
        else:
            logger.warning(f"Page {page_idx}: Generated EMPTY HTML (page has {len(page.get('blocks', []))} blocks)")
    
    if not snippets:
        return "<p></p>"
    
    combined_html = "\n".join(snippets)
    
    # [HTML_SINGLE_PAGE] When pages aren't wrapped in sections, merge paragraphs across page boundaries
    if not wrap_pages:
        combined_html = merge_adjacent_paragraph_html(combined_html)
    
    return combined_html




