"""
Chapter 5: Monsters of Athas - Table Extraction Fixer

Detects and reconstructs the 2-column monster stat tables that pdfplumber misses.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any

from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput

logger = logging.getLogger(__name__)

# Monster stats labels in order (21 rows)
MONSTER_STATS_LABELS = [
    "CLIMATE/TERRAIN",
    "FREQUENCY",
    "ORGANIZATION",
    "ACTIVITY CYCLE",
    "DIET",
    "INTELLIGENCE",
    "TREASURE",
    "ALIGNMENT",
    "NO. APPEARING",
    "ARMOR CLASS",
    "MOVEMENT",
    "HIT DICE",
    "THAC0",
    "NO. OF ATTACKS",
    "DAMAGE/ATTACK",
    "SPECIAL ATTACKS",
    "SPECIAL DEFENSES",
    "MAGIC RESISTANCE",
    "SIZE",
    "MORALE",
    "XP VALUE"
]


def _extract_text_from_blocks(blocks: List[Dict]) -> str:
    """Extract plain text from a list of blocks."""
    text_parts = []
    for block in blocks:
        if block.get("type") == "text":
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text_parts.append(span.get("text", ""))
                text_parts.append(" ")
    return " ".join(text_parts)


def _parse_monster_stats_from_pdf(page_blocks: List[Dict]) -> Dict[str, str]:
    """
    Parse monster stats from PDF blocks using the source PDF structure.
    
    The PDF has stats in a 2-column table format where labels are in the left column
    and values are in the right column.
    """
    text = _extract_text_from_blocks(page_blocks)
    
    # Normalize common spacing issues
    text = re.sub(r'MOR\s+A\s+L\s+E', 'MORALE', text)
    text = re.sub(r'TRE\s+AS\s+U\s+R\s+E', 'TREASURE', text)
    
    stats = {}
    
    for i, label in enumerate(MONSTER_STATS_LABELS):
        # Create pattern that matches the label with optional colon/semicolon
        label_pattern = label.replace('/', r'\s*/\s*').replace(' ', r'\s+')
        
        # Try to find the value after the label
        if i < len(MONSTER_STATS_LABELS) - 1:
            next_label = MONSTER_STATS_LABELS[i + 1]
            next_pattern = next_label.replace('/', r'\s*/\s*').replace(' ', r'\s+')
            # Match everything between this label and the next
            pattern = rf'{label_pattern}\s*[:;]?\s*(.*?)(?={next_pattern}\s*[:;]?|$)'
        else:
            # Last stat - match until description starts
            pattern = rf'{label_pattern}\s*[:;]?\s*(.*?)(?=PSIONICS\s+SUMMARY|At first|It is difficult|Fortunately|The anakore|The gaj|Athasian giants|The gith|This small|The silk wyrm|The tembo|$)'
        
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            # Clean up the value
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = re.sub(r'[:;]\s*$', '', value)  # Remove trailing colons/semicolons
            stats[label] = value
        else:
            stats[label] = ""
    
    return stats


def _create_monster_stats_table(stats: Dict[str, str]) -> Dict:
    """
    Create a table structure from parsed monster stats.
    """
    rows = []
    
    for label in MONSTER_STATS_LABELS:
        value = stats.get(label, "")
        rows.append({
            "cells": [
                {"text": f"{label}:", "bold": True},
                {"text": value, "bold": False}
            ]
        })
    
    return {
        "bbox": [0, 0, 0, 0],
        "rows": rows,
        "header_rows": 0,
        "class": "monster-stats"  # Custom class for monster stat tables
    }


class Chapter5TableFixer(BaseProcessor):
    """
    Reconstructs monster stat tables for Chapter 5: Monsters of Athas.
    
    The monster stat tables are 2-column tables that pdfplumber doesn't detect
    properly. This processor finds them by looking for monster stat labels and
    reconstructs them as proper table structures.
    """
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """
        Process Chapter 5 section to reconstruct monster stat tables.
        """
        # Get sections directory from config
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        monster_names = [
            "Belgoi", "Braxat", "Dragon of Tyr", "Dune Freak (Anakore)",
            "Gaj", "Giant, Athasian", "Gith", "Jozhal", "Silk Wyrm", "Tembo"
        ]
        
        # Find Chapter 5 section file
        chapter_5_file = sections_dir / "02-184-chapter-five-monsters-of-athas.json"
        
        if not chapter_5_file.exists():
            logger.warning(f"Chapter 5 file not found: {chapter_5_file}")
            return ProcessorOutput(data={"items": 0, "warnings": ["Chapter 5 file not found"], "errors": []})
        
        logger.info(f"Processing Chapter 5 monster tables: {chapter_5_file}")
        
        # Load section data
        with open(chapter_5_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        tables_added = 0
        
        # Process each page
        for page in section_data.get("pages", []):
            page_num = page.get("page_number")
            blocks = page.get("blocks", [])
            
            # Check if this page has a monster
            page_text = _extract_text_from_blocks(blocks)
            monster_found = None
            for monster_name in monster_names:
                if monster_name in page_text:
                    monster_found = monster_name
                    break
            
            if not monster_found:
                continue
            
            logger.info(f"  Found {monster_found} on page {page_num}")
            
            # Parse stats from the page
            stats = _parse_monster_stats_from_pdf(blocks)
            
            # Count non-empty stats
            filled_count = sum(1 for v in stats.values() if v)
            logger.info(f"  Parsed {filled_count}/21 stats")
            
            if filled_count > 10:  # Only add if we got reasonable coverage
                # Create table structure
                table = _create_monster_stats_table(stats)
                
                # Add to page's tables list
                if "tables" not in page:
                    page["tables"] = []
                
                page["tables"].insert(0, table)  # Insert at beginning
                tables_added += 1
                logger.info(f"  ✅ Added monster stats table with {filled_count}/21 fields")
            else:
                logger.warning(f"  ⚠️  Only parsed {filled_count}/21 stats, skipping table creation")
        
        # Save updated section data
        with open(chapter_5_file, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ Added {tables_added} monster stat tables to Chapter 5")
        
        return ProcessorOutput(
            data=input_data.data,
            metadata={"items": tables_added, "warnings": [], "errors": []}
        )

