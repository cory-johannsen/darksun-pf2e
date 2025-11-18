"""Post-processor to reorder the Bonus to AC section in Chapter 9 HTML output."""

from pathlib import Path
import re
from ..base import BaseProcessor
from ..domain import ExecutionContext, ProcessorInput, ProcessorOutput
import logging

logger = logging.getLogger(__name__)


class Chapter9HTMLReorder(BaseProcessor):
    """Reorders the Bonus to AC section to appear after Important Considerations in the HTML output."""
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Reorder Chapter 9 HTML sections.
        
        Args:
            input_data: Output from previous processor
            context: Execution context
            
        Returns:
            ProcessorOutput with reordered HTML
        """
        html_output_dir = Path(self.config.get("html_output_dir", "data/html_output"))
        chapter_9_file = html_output_dir / "chapter-nine-combat.html"
        
        if not chapter_9_file.exists():
            logger.debug("Chapter 9 HTML file not found, skipping reordering")
            return ProcessorOutput(data=input_data.data, metadata={"skipped": True})
        
        logger.info(f"Reordering Bonus to AC section in {chapter_9_file.name}")
        
        # Read the HTML
        with open(chapter_9_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Extract the Bonus to AC header and table
        # Pattern: <h3 id="header-bonus...">...</h3>...paragraphs...<table...>...</table>...paragraphs...
        # Find the H3 header
        bonus_header_pattern = r'<h3 id="header-bonus-to-ac-per-type-of-piece">.*?</h3>'
        bonus_header_match = re.search(bonus_header_pattern, html, re.DOTALL)
        
        if not bonus_header_match:
            logger.warning("Could not find Bonus to AC header in HTML")
            return ProcessorOutput(data=input_data.data, metadata={"skipped": "no_bonus_header"})
        
        # Find the table that follows (may have some text in between)
        # Look for the next table after the header
        search_start = bonus_header_match.end()
        table_pattern = r'<table class="ds-table">.*?</table>'
        table_match = re.search(table_pattern, html[search_start:search_start + 5000], re.DOTALL)
        
        if not table_match:
            logger.warning("Could not find Bonus to AC table in HTML")
            return ProcessorOutput(data=input_data.data, metadata={"skipped": "no_bonus_table"})
        
        # Get the full content from header to end of table
        bonus_start = bonus_header_match.start()
        bonus_end = search_start + table_match.end()
        bonus_content = html[bonus_start:bonus_end]
        
        # Also capture the paragraphs after the table until the next header
        post_table_pattern = r'</table>(.*?)(?=<(?:p|h\d) id="header-|<section|$)'
        post_table_match = re.search(post_table_pattern, html[bonus_end:bonus_end + 2000], re.DOTALL)
        if post_table_match:
            bonus_content += post_table_match.group(1)
            bonus_end += post_table_match.end(1)
        
        # Remove the Bonus to AC section from its current location
        html = html[:bonus_start] + html[bonus_end:]
        
        # Find the Important Considerations header
        ic_pattern = r'<p id="header-21-important-considerations">.*?</p>'
        ic_match = re.search(ic_pattern, html, re.DOTALL)
        
        if not ic_match:
            logger.warning("Could not find Important Considerations header")
            return ProcessorOutput(data=input_data.data, metadata={"skipped": "no_ic_header"})
        
        # The IC paragraphs are currently AFTER the Bonus section (which we just removed)
        # So we need to find them and insert them before we re-insert the Bonus section
        # Look for paragraphs containing the IC content after where the Bonus section was
        ic_para1_pattern = r'<p>Although piecemeal armor is lighter.*?</p>'
        ic_para2_pattern = r'<p>Characters wearing piecemeal metal armor.*?</p>'
        
        para1_match = re.search(ic_para1_pattern, html, re.DOTALL)
        para2_match = re.search(ic_para2_pattern, html, re.DOTALL)
        
        ic_paragraphs = ""
        if para1_match and para2_match:
            # Extract both paragraphs
            # They should be consecutive, so get from start of para1 to end of para2
            para_start = para1_match.start()
            para_end = para2_match.end()
            ic_paragraphs = html[para_start:para_end]
            # Remove them from their current location
            html = html[:para_start] + html[para_end:]
            logger.info(f"Found and extracted 2 Important Considerations paragraphs")
        else:
            logger.warning(f"Could not find IC paragraphs (para1: {para1_match is not None}, para2: {para2_match is not None})")
        
        # Now find where to insert: after the IC header
        # Re-search for IC header since positions may have changed after removing paragraphs
        ic_match = re.search(ic_pattern, html, re.DOTALL)
        if not ic_match:
            logger.warning("Lost track of Important Considerations header after removing paragraphs")
            return ProcessorOutput(data=input_data.data, metadata={"skipped": "lost_ic_header"})
        
        insert_pos = ic_match.end()
        
        # Insert: IC paragraphs first, then Bonus section
        html = html[:insert_pos] + ic_paragraphs + bonus_content + html[insert_pos:]
        logger.info(f"Successfully reordered sections: IC header -> IC paragraphs -> Bonus section")
        
        # Write the modified HTML
        with open(chapter_9_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        context.items_processed = 1
        
        return ProcessorOutput(
            data={"html_reordered": 1},
            metadata={"chapter_9_html_reordered": True}
        )

