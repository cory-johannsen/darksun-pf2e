"""
Half-elves race specific processing for Chapter 2.

This module handles PDF-level adjustments for half-elves character race,
including text ordering, paragraph breaks, and special formatting.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import List

from ..journal import (
    _normalize_plain_text,
    _collect_cells_from_blocks,
    _build_matrix_from_cells,
    _table_from_rows,
    _compute_bbox_from_cells,
)
from .common import update_block_bbox, find_block


def fix_half_elves_section_paragraph_breaks(pages: list) -> None:
    """Fix paragraph breaks in the Half-Elves section on pages 4-5.
    
    The Half-Elves section has 11 paragraphs but they get merged together.
    We need to force paragraph breaks at specific sentences.
    """
    paragraph_starts = [
        "Elves and humans travel",          # Para 1 - Introduction
        "A half-elf is generally tall",     # Para 2 - Physical description
        "A half-elf'salife is typically",   # Para 3 - Social hardships (note: typo in PDF, no space)
        # Para 4 handled separately - sentence starts mid-line: ". Rarely do half-"
        "Intolerance, however, has given",  # Para 5 - Self-reliance
        "The skills involved in survival",  # Para 6 - Survival skills
        "Coincidentally, faced with",       # Para 7 - Alien races
        "Also, some half-elves turn",       # Para 8 - Animal companions
        "Half-elves add one to their",      # Para 9 - Ability scores
        "A half-elf character can choose",  # Para 10 - Class options
        "A half-elf gains some benefits",   # Para 11 - Level benefits
    ]
    
    # Process pages 4 and 5
    for page_idx in [4, 5]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block in page.get("blocks", []):
            if not block.get("lines"):
                continue
            
            # Check each line in the block
            for line in block["lines"]:
                line_text = _normalize_plain_text("".join(span.get("text", "") for span in line.get("spans", []))).strip()
                
                # Check for regular paragraph starts
                for para_start in paragraph_starts:
                    if line_text.startswith(para_start):
                        # Mark this line to force a paragraph break
                        line["__force_line_break"] = True
                        break
                
                # Special case: "Rarely" starts mid-line after a period
                # The sentence ". Rarely do half-elves" spans pages 4-5
                if ". Rarely do half" in line_text:
                    # This line needs to be split - mark it for special handling
                    line["__split_at_rarely"] = True
                
                # Special case: "Also" starts mid-line after a period
                # The sentence ". Also, some half-elves turn" 
                if ". Also, some half-elves" in line_text:
                    # This line needs to be split - mark it for special handling
                    line["__split_at_also"] = True




def fix_half_elves_roleplaying_paragraph_breaks(pages: list) -> None:
    """Fix paragraph breaks in the Half-elves Roleplaying section on pages 5-6.
    
    The Roleplaying section has 3 paragraphs but they get heavily fragmented
    across two-column layout. We need to mark blocks to prevent unwanted splits.
    
    Note: Due to PDF layout, "For example..." appears before the "Roleplaying:" header
    in the block order, so we need to handle it specially.
    """
    # Mark the specific blocks that should start new paragraphs
    paragraph_start_texts = [
        "For example, when a half-elf",     # Para 2
        "Despite their self-reliance",      # Para 3
    ]
    
    # First pass: find the Roleplaying section and mark all blocks
    roleplaying_start_idx = -1
    roleplaying_end_idx = -1
    for_example_idx = -1
    
    for page_idx in [5, 6]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            if not block.get("lines"):
                continue
            
            first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in block["lines"][0].get("spans", []))).strip()
            
            if "For example, when a half-elf" in first_line_text:
                for_example_idx = (page_idx, block_idx)
            elif "Roleplaying: Half-elves pride" in first_line_text:
                roleplaying_start_idx = (page_idx, block_idx)
            elif "Half-giants" in first_line_text:
                roleplaying_end_idx = (page_idx, block_idx)
                break
    
    # Second pass: mark the blocks
    in_roleplaying_section = False
    for page_idx in [5, 6]:
        if page_idx >= len(pages):
            continue
        page = pages[page_idx]
        
        for block_idx, block in enumerate(page.get("blocks", [])):
            if not block.get("lines"):
                continue
            
            # Check if this is the "For example" block (special case before header)
            if for_example_idx and (page_idx, block_idx) == for_example_idx:
                block["__roleplaying_section"] = True
                block["__force_paragraph_break"] = True
                continue
            
            # Check if this is the start of the Roleplaying section
            if roleplaying_start_idx and (page_idx, block_idx) == roleplaying_start_idx:
                in_roleplaying_section = True
                block["__roleplaying_section"] = True
                continue
            
            # Check if we've reached the end
            if roleplaying_end_idx and (page_idx, block_idx) == roleplaying_end_idx:
                in_roleplaying_section = False
                break
            
            # If we're in the Roleplaying section, mark the block
            if in_roleplaying_section:
                block["__roleplaying_section"] = True
                
                # Check if this block should start a new paragraph
                first_line_text = _normalize_plain_text("".join(span.get("text", "") for span in block["lines"][0].get("spans", []))).strip()
                for para_start in paragraph_start_texts:
                    if first_line_text.startswith(para_start):
                        block["__force_paragraph_break"] = True
                        break




