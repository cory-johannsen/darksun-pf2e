"""
Unit test for Chapter 11 Plant-Based Monsters paragraph merging
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.pdf_pipeline.transformers.chapter_11_processing import _merge_plant_based_monsters_text


def test_plant_based_monsters_single_paragraph():
    """
    Test that Plant-Based Monsters text is marked for single paragraph rendering.
    
    The Plant-Based Monsters section should have the text:
    "Defiling magic destroys all plant-life within its area of effect without 
    exception. A plant-based monster can thus be destroyed (or injured if it 
    isn't wholly contained within the area of effect), with no save allowed."
    
    This text appears across multiple lines in the PDF but should be rendered
    as a single paragraph.
    """
    # Create mock data with Plant-Based Monsters section
    section_data = {
        "pages": [{
            "number": 80,
            "blocks": [
                # Plant-Based Monsters header
                {
                    "type": "text",
                    "bbox": [288.0, 353.0, 400.0, 365.0],
                    "lines": [{
                        "bbox": [288.0, 353.0, 400.0, 365.0],
                        "spans": [{
                            "text": "Plant-Based Monsters: ",
                            "font": "MSTT31c5c6",
                            "size": 8.88,
                            "flags": 4,
                            "color": "#ca5804"
                        }, {
                            "text": "Defiling magic destroys",
                            "font": "MSTT31c5c6",
                            "size": 8.88,
                            "flags": 0
                        }]
                    }]
                },
                # Continuation text (separate block)
                {
                    "type": "text",
                    "bbox": [288.0, 367.0, 400.0, 395.0],
                    "lines": [
                        {
                            "bbox": [288.0, 367.0, 400.0, 380.0],
                            "spans": [{
                                "text": "all plant-life within its area of effect without excep-",
                                "font": "MSTT31c5c6",
                                "size": 8.88,
                                "flags": 0
                            }]
                        },
                        {
                            "bbox": [288.0, 380.5, 400.0, 395.0],
                            "spans": [{
                                "text": "tion. A plant-based monster can thus be destroyed",
                                "font": "MSTT31c5c6",
                                "size": 8.88,
                                "flags": 0
                            }]
                        }
                    ]
                }
            ]
        }]
    }
    
    # Apply the merging function
    _merge_plant_based_monsters_text(section_data)
    
    # Check that lines in the Plant-Based Monsters block are marked to prevent breaks
    pages = section_data["pages"]
    found_header = False
    found_merged_text = False
    
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") != "text":
                continue
            
            # Check for the header
            first_line = block.get("lines", [{}])[0]
            first_span_text = first_line.get("spans", [{}])[0].get("text", "")
            
            if "Plant-Based Monsters:" in first_span_text:
                found_header = True
                # The header block should have a marker to merge with the next block
                assert block.get("__merge_with_next", False), "Header block should be marked to merge with next"
                continue
            
            # After the header, check for merged text
            if found_header and not found_merged_text:
                # Check if this block contains the continuation text
                all_text = ""
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        all_text += span.get("text", "")
                
                if "all plant-life" in all_text or "tion. A plant-based monster" in all_text:
                    found_merged_text = True
                    # This block should be marked to merge with the previous block
                    assert block.get("__merge_with_prev", False), "Continuation block should be marked to merge with previous"
    
    assert found_header, "Should find Plant-Based Monsters header"
    assert found_merged_text, "Should find merged text after header"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

