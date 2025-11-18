"""
Chapter Three: Athasian Geography post-processing in the extract stage.

This post-processor handles paragraph breaks for Chapter Three: Athasian Geography
by modifying the raw extracted data before it enters the transform stage.
"""

import logging
import json
from pathlib import Path
from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
from tools.pdf_pipeline.utils.header_conversion import convert_all_styled_headers_to_semantic

logger = logging.getLogger(__name__)


def normalize_plain_text(text: str) -> str:
    """Normalize text for comparison (remove extra whitespace, etc.)."""
    return " ".join(text.split())


def update_block_bbox(block: dict) -> None:
    """Update block bounding box based on its lines."""
    lines = block.get("lines", [])
    if not lines:
        block["bbox"] = [0.0, 0.0, 0.0, 0.0]
        return
    
    x0 = min(line["bbox"][0] for line in lines)
    y0 = min(line["bbox"][1] for line in lines)
    x1 = max(line["bbox"][2] for line in lines)
    y1 = max(line["bbox"][3] for line in lines)
    block["bbox"] = [x0, y0, x1, y1]


def mark_geography_headers(page: dict) -> None:
    """
    Mark specific headers as H2 or H3 in Chapter Three: Athasian Geography.
    
    Args:
        page: Page dictionary containing blocks to process
    """
    h2_headers = [
        "Mudflats",
        "Estuaries",
        "Islands",
        "Flying Creatures",
        "Giants",
        "Mudfiends",
        "Silt Horrors",
        "Travel in the Tablelands",
        "Geography of the Tablelands",
        "Cities",
        "Villages",
        "Caravans",
        "People of the Tablelands",
        "Animals",
        "Methods of Travel",
        "The Foothills",
        "The Canyons",
    ]
    
    h3_headers = [
        "Ruins",
        "Fabled City of Plenty",
        "Walking",
        "Riding",
        "Stony Barrens",
        "Sandy Wastes",
        "Flora and Fauna",
    ]
    
    h4_headers = [
        "Flora and Fauna",
        "Wave dunes",
        "Crescent dunes",
        "Star dunes",
    ]
    
    blocks = page.get("blocks", [])
    
    for block in blocks:
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Get the text of the first line
        first_line_text = normalize_plain_text(
            "".join(span.get("text", "") for span in lines[0].get("spans", []))
        )
        
        # Check if this matches an H2 header
        for h2_header in h2_headers:
            if first_line_text.strip() == h2_header:
                block["__render_as_h2"] = True
                block["__header_text"] = h2_header
                logger.info(f"Marked '{first_line_text}' as H2 header")
                break
        
        # Check if this matches an H3 header
        for h3_header in h3_headers:
            if first_line_text.strip() == h3_header:
                block["__render_as_h3"] = True
                block["__header_text"] = h3_header
                logger.info(f"Marked '{first_line_text}' as H3 header")
                break
        
        # Check if this matches an H4 header
        for h4_header in h4_headers:
            if first_line_text.strip() == h4_header:
                block["__render_as_h4"] = True
                block["__header_text"] = h4_header
                logger.info(f"Marked '{first_line_text}' as H4 header")
                break


def force_geography_paragraph_breaks(page: dict) -> None:
    """
    Force paragraph breaks at specific points in Chapter Three: Athasian Geography.
    
    This function splits text blocks at designated break points to ensure proper
    paragraph separation in the final output.
    
    Args:
        page: Page dictionary containing blocks to process
    """
    # Define all break points for this chapter
    # These patterns must match the START of the first line in the raw JSON
    # They should be SHORT enough to match just the beginning, not the full sentence
    break_points = [
        # Main intro (3 paragraphs)
        "It is beyond my modest capabilities",
        "There are hundreds of different kinds",
        # Sea of Silt section (9 paragraphs)
        "I have met travelers who claim",
        "On a still day, which is so rare",
        "Usually, however, the Sea of Silt",
        "When the wind blows more strongly",
        "On stormy days, the wind roars",
        "The wind may blow for only",
        "Even when the wind is not blowing",
        "As one might imagine,",
        # Flying section (2 paragraphs)
        "Of course, it is possible to use magic",
        # Wading section (7 paragraphs)
        "When someone steps into one of the many",
        "It should also be noted",
        "I have spoken at length",
        "I should add that many advanced",
        "Some humans employ various",
        "At least one dwarven community",
        # Levitation section (5 paragraphs)
        "By this means, a would-be traveler",
        "The trouble with sails",
        "Poles work better",
        "Of course, levitation suffers",
        # Geography of the Sea of Silt - Mudflats section (4 paragraphs)
        "Sometimes,",
        "The traveler",
        "The plants and animals",
        # Geography of the Sea of Silt - Estuaries section (2 paragraphs)
        "As in the Sea of Silt itself",
        # Geography of the Sea of Silt - Islands section (5 paragraphs)
        "Because they are rarely visited",
        "The only oases in the Sea of Silt",
        "The islands have an abundance of plant",
        "The giants keep the islands",
        # Geography of the Sea of Silt - Ruins subsection (2 paragraphs)
        "Many of the islands also have ruins",
        # Geography of the Sea of Silt - Fabled City of Plenty subsection (4 paragraphs)
        "After the storm passed",
        "No one I know has ever",
        "What the secret of the fabled city is",
        # Encounters in the Sea of Silt - Flying Creatures (2 paragraphs)
        "These encounters seem to occur",
        # Encounters in the Sea of Silt - Giants (2 paragraphs)
        "On the other hand",
        # Encounters in the Sea of Silt - Mudfiends (4 paragraphs)
        "The most dangerous of these beasts",
        "Usually, it happens this way",
        "When the wind has exposed",
        # Encounters in the Sea of Silt - Silt Horrors (2 paragraphs)
        "No one seems",
        # Tablelands (4 paragraphs)
        "Generally, the Tablelands",
        "The plains of the Tablelands",
        "This is not, by any means,",
        # Travel in the Tablelands - Walking (6 paragraphs)
        "At this rate",
        "First, travelers",
        "Of course,",
        "Further, of course,",
        "Walking is fine",
        # Travel in the Tablelands - Riding (7 paragraphs)
        "Kanks need no water",
        "Wagon travel is used",
        "Despite their toughness,",
        "Second, they must drink",
        "Third, the huge wagons",
        "Finally, the only thing that a mekillot",
        # Geography of the Tablelands - Stony Barrens (3 paragraphs)
        "If you have any other",
        "On the other hand",
        # Geography of the Tablelands - Flora and Fauna (3 paragraphs)
        "If you are not familiar",
        "The fauna of",
        # Geography of the Tablelands - Sandy Wastes (2 paragraphs)
        "Where there are strong",
        # Geography of the Tablelands - Star dunes - Flora and Fauna (2 paragraphs)
        "As in the stony barrens,",
        # Geography of the Tablelands - Salt Flats (2 paragraphs)
        "They should also carry an ample",
        # Geography of the Tablelands - Rocky Badlands (3 paragraphs)
        "Traveling in the badlands",
        "Mountains often",
        # Geography of the Tablelands - Scrub Plains (6 paragraphs)
        "What the herders",
        "Give the",
        "The druids treat",
        "In cases of",
        "Travel in",
        # Geography of the Tablelands - Inland Silt Basins (2 paragraphs)
        "Those traveling",
        # Geography of the Tablelands - Ruins (9 paragraphs)
        "The achitecture",
        "The most common",
        "Although not",
        "The largest castles",
        "In the Tablelands",
        "The eight cities that",
        "Two of the ruined",
        "Of course, there may well",
        # Encounters in the Tablelands - Cities (3 paragraphs)
        "Of course, it is always possible",
        "In the Tyr region",
        # Encounters in the Tablelands - Villages (3 paragraphs)
        "The reception given a party of strangers",
        "Some villages are described in the",
        # Encounters in the Tablelands - Caravans (3 paragraphs)
        "Small caravans",
        "For more information",
        # Encounters in the Tablelands - People of the Tablelands (2 paragraphs)
        "When you meet a group of natives",
        "Each of the groups mentioned",
        # Encounters in the Tablelands - Animals (3 paragraphs)
        "If the herbivores",
        "Most of the creatures",
        # The Ringing Mountains (5 paragraphs)
        "I have visited only the mountains",
        "It is entirely conceivable",
        "From a distance of a hundred miles",
        "At this point",
        # Methods of Travel (6 paragraphs)
        "Therefore, if you are going",
        "In addition to the extra",
        "There is one last",
        "I have seen full-grown",
        "Given all of the complications",
        # Geography of the Ringing Mountains (3 paragraphs)
        "Other times, the transitions are more obvious",
        "Whether the transition is gradual or sudden",
        # The Foothills (6 paragraphs)
        "There are a few differences, however",
        "Assuming you're going toward",
        "When traveling along these seemingly",
        "It is also fairly easy to travel",
        "Traveling parallel to the spine",
        # The Canyons (11 paragraphs)
        "The first five or ten miles",
        "These sandy fans",
        "Further up, the",
        "The greatest hazard",
        "Near the top of the canyon",
        "As you step or jump",
        "Above the boulder field",
        "Sometimes, a hermit",
        "Occasionally, these high",
        "The only exception to this",
    ]
    
    blocks_to_insert = []
    blocks = page.get("blocks", [])
    
    for idx, block in enumerate(list(blocks)):
        if block.get("type") != "text":
            continue
        
        lines = block.get("lines", [])
        if not lines:
            continue
        
        # Check each line to see if it contains a break point
        for line_idx, line in enumerate(lines):
            line_text = normalize_plain_text(
                "".join(span.get("text", "") for span in line.get("spans", []))
            )
            
            # Check if line starts with any break point
            starts_with_break = any(line_text.startswith(bp) for bp in break_points)
            
            # For start-of-line breaks, split the block at this line if not the first line
            if starts_with_break and line_idx > 0:
                # Split this block at this line
                first_part_lines = lines[:line_idx]
                second_part_lines = lines[line_idx:]
                
                logger.info(f"Splitting block at line {line_idx}: '{line_text[:60]}...'")
                
                # Update the current block to only contain the first part
                block["lines"] = first_part_lines
                update_block_bbox(block)
                
                # Create a new block for the second part
                second_block = {
                    "type": "text",
                    "lines": second_part_lines,
                    "__force_paragraph_break": True
                }
                update_block_bbox(second_block)
                
                # Schedule this new block to be inserted
                blocks_to_insert.append((idx + 1, second_block))
                
                # Don't process more lines in this block, move to next block
                break
            elif starts_with_break and line_idx == 0:
                # Mark the entire block for a forced break
                block["__force_paragraph_break"] = True
    
    # Insert all new blocks (in reverse order to maintain indices)
    for insert_idx, new_block in reversed(blocks_to_insert):
        blocks.insert(insert_idx, new_block)
        logger.info(f"Inserted new block at index {insert_idx}")
    
    logger.info(f"Geography paragraph breaks complete: split {len(blocks_to_insert)} blocks")


class ChapterThreeGeographyProcessor(BaseProcessor):
    """Processes Chapter Three: Athasian Geography to add paragraph breaks."""
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Apply paragraph breaks to Chapter Three: Athasian Geography.
        
        Args:
            input_data: Output from previous processor
            context: Execution context
            
        Returns:
            ProcessorOutput with processed data
        """
        sections_dir = Path(self.config.get("sections_dir", "data/raw_structured/sections"))
        
        # Find the Chapter Three Geography file
        chapter_file = None
        for file in sections_dir.glob("*chapter-three-athasian-geography.json"):
            chapter_file = file
            break
        
        if not chapter_file or not chapter_file.exists():
            logger.info("Chapter Three Geography file not found, skipping")
            return input_data
        
        logger.info("=" * 80)
        logger.info("!!! PROCESSING CHAPTER THREE: ATHASIAN GEOGRAPHY !!!")
        logger.info("=" * 80)
        
        # Load the chapter data
        with open(chapter_file, 'r', encoding='utf-8') as f:
            section_data = json.load(f)
        
        pages = section_data.get("pages", [])
        if not pages:
            logger.info("No pages found in Chapter Three Geography")
            return input_data
        
        logger.info(f"Chapter Three Geography has {len(pages)} pages")
        
        # Apply header markings and paragraph breaks to all pages
        for page_idx, page in enumerate(pages):
            mark_geography_headers(page)
            force_geography_paragraph_breaks(page)
        
        # Write back to disk
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, indent=2, ensure_ascii=False)
        
        logger.info("=== Chapter Three: Athasian Geography processing complete ===")
        
        return ProcessorOutput(
            data=input_data.data,
            metadata={"chapter_three_geography_processed": True}
        )

