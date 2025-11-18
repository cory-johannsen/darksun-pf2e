#!/usr/bin/env python3
"""
Unit test for table cell bold formatting functionality.

Tests that cells with the 'bold' property are rendered with <strong> tags
instead of having escaped HTML in the cell text.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.pdf_pipeline.transformers.journal import _render_table


def test_bold_cell_formatting():
    """Test that cells with bold=True are rendered with <strong> tags."""
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Header 1"},
                    {"text": "Header 2"}
                ]
            },
            {
                "cells": [
                    {"text": "Bold Section", "bold": True},
                    {"text": ""}
                ]
            },
            {
                "cells": [
                    {"text": "Regular cell"},
                    {"text": "Another cell"}
                ]
            }
        ],
        "header_rows": 1
    }
    
    result = _render_table(table_data, table_class="ds-table")
    
    # Verify the structure
    assert '<table class="ds-table">' in result
    
    # Verify header row
    assert '<th>Header 1</th>' in result
    assert '<th>Header 2</th>' in result
    
    # Verify bold cell is rendered with <strong> tags
    assert '<td><strong>Bold Section</strong></td>' in result
    
    # Verify that HTML tags are NOT escaped
    assert '&lt;strong&gt;' not in result
    assert '&lt;/strong&gt;' not in result
    
    # Verify regular cells don't have bold
    assert '<td>Regular cell</td>' in result
    assert '<td>Another cell</td>' in result
    
    print("✓ Bold cell formatting test passed")


def test_no_bold_property():
    """Test that cells without bold property render normally."""
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Header 1"},
                    {"text": "Header 2"}
                ]
            },
            {
                "cells": [
                    {"text": "Normal cell 1"},
                    {"text": "Normal cell 2"}
                ]
            }
        ],
        "header_rows": 1
    }
    
    result = _render_table(table_data, table_class="ds-table")
    
    # Verify no bold tags appear
    assert '<strong>' not in result
    assert '</strong>' not in result
    
    # Verify cells render normally
    assert '<td>Normal cell 1</td>' in result
    assert '<td>Normal cell 2</td>' in result
    
    print("✓ No bold property test passed")


def test_bold_with_special_characters():
    """Test that bold cells with special characters are properly escaped."""
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Section <test>", "bold": True},
                    {"text": "Price & Value"}
                ]
            }
        ],
        "header_rows": 0
    }
    
    result = _render_table(table_data, table_class=None)
    
    # Verify special characters are escaped within the bold tags
    assert '<td><strong>Section &lt;test&gt;</strong></td>' in result
    
    # Verify ampersand is escaped in regular cell
    assert '<td>Price &amp; Value</td>' in result
    
    print("✓ Bold with special characters test passed")


def test_transport_table_structure():
    """Test the Transport table structure with section headers."""
    # Simulate the Transport table structure from chapter_6_processing
    table_data = {
        "rows": [
            {
                "cells": [
                    {"text": "Type"},
                    {"text": "Price"}
                ]
            },
            {
                "cells": [
                    {"text": "Chariot", "bold": True},
                    {"text": ""}
                ]
            },
            {
                "cells": [
                    {"text": "one kank, one"},
                    {"text": "10 sp"}
                ]
            },
            {
                "cells": [
                    {"text": "Howdah", "bold": True},
                    {"text": ""}
                ]
            },
            {
                "cells": [
                    {"text": "inix"},
                    {"text": "10 sp"}
                ]
            }
        ],
        "header_rows": 1
    }
    
    result = _render_table(table_data, table_class="ds-table")
    
    # Verify section headers are bold
    assert '<td><strong>Chariot</strong></td>' in result
    assert '<td><strong>Howdah</strong></td>' in result
    
    # Verify data rows are not bold
    assert '<td>one kank, one</td>' in result
    assert '<td>10 sp</td>' in result
    assert '<td>inix</td>' in result
    
    # Verify no escaped HTML tags
    assert '&lt;strong&gt;Chariot&lt;/strong&gt;' not in result
    assert '&lt;strong&gt;Howdah&lt;/strong&gt;' not in result
    
    print("✓ Transport table structure test passed")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TABLE CELL BOLD FORMATTING TESTS")
    print("=" * 70 + "\n")
    
    test_bold_cell_formatting()
    test_no_bold_property()
    test_bold_with_special_characters()
    test_transport_table_structure()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70 + "\n")

