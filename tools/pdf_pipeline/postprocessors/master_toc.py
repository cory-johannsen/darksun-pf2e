"""Generate master table of contents for all chapters.

[TOC_DOCUMENT] The output should contain a top level table of contents that contains 
all the converted chapters, in order. This should be stored in a file named 
"table_of_contents.{format}" where format is the output format (html, json, etc)
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from tools.pdf_pipeline.base import BaseProcessor
from tools.pdf_pipeline.domain import ExecutionContext, ProcessorInput, ProcessorOutput
import json
import logging


class MasterTOCGenerator(BaseProcessor):
    """Generate master table_of_contents.html for all chapters."""
    
    # [ORDER_OF_CONTENT] from RULES.md
    CHAPTER_ORDER = [
        "chapter-one-ability-scores",
        "chapter-two-player-character-races",
        "chapter-three-player-character-classes",
        "chapter-four-alignment",
        "chapter-five-proficiencies",
        "chapter-six-money-and-equipment",
        "chapter-seven-magic",
        "chapter-eight-experience",
        "chapter-nine-combat",
        "chapter-ten-treasure",
        "chapter-eleven-encounters",
        "chapter-twelve-npcs",
        "chapter-thirteen-vision-and-light",
        "chapter-fourteen-time-and-movement",
        "chapter-fifteen-new-spells",
        "chapter-one-the-world-of-athas",
        "chapter-two-athasian-society",
        "chapter-three-athasian-geography",
        "chapter-four-atlas-of-the-tyr-region",
        "chapter-five-monsters-of-athas",
        "a-little-knowledge",
        "a-flip-book-adventure",
        "kluzd",
        "wezer",
    ]
    
    def __init__(self, spec: Any):
        """Initialize the master TOC generator.
        
        Args:
            spec: ProcessorSpec with config containing:
                - html_dir: Directory containing HTML files
                - output_file: Path to output table_of_contents.html
                - manifest_path: Optional path to pdf_manifest.json (for ordering)
        """
        config = spec.config if hasattr(spec, 'config') else spec
        self.html_dir = Path(config.get("html_dir", "data/html_output"))
        self.output_file = Path(config.get("output_file", "data/html_output/table_of_contents.html"))
        self.manifest_path = Path(config.get("manifest_path", "data/raw/pdf_manifest.json"))
        self.logger = logging.getLogger(__name__)
    
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Generate master table of contents HTML file.
        
        Args:
            input_data: Input from previous stage
            context: Execution context
            
        Returns:
            ProcessorOutput with TOC generation results
        """
        self.logger.debug("Generating master TOC from %s", self.html_dir)
        # Find all HTML files
        if not self.html_dir.exists():
            return ProcessorOutput(
                data={
                    "status": "error",
                    "message": f"HTML directory not found: {self.html_dir}"
                },
                metadata={
                    "chapters_found": 0,
                    "chapters_missing": len(self.CHAPTER_ORDER)
                }
            )
        
        html_files = {f.stem: f for f in self.html_dir.glob("*.html") if f.stem != "table_of_contents"}
        
        # Build TOC entries in the correct order
        toc_entries = []
        missing_chapters = []
        
        desired_order = self._derive_order_from_manifest()
        if not desired_order:
            # Fallback to static order if manifest missing or invalid
            self.logger.warning("Manifest not found or invalid; falling back to static CHAPTER_ORDER")
            desired_order = self.CHAPTER_ORDER[:]
        
        for chapter_slug in desired_order:
            file_entry = html_files.get(chapter_slug)
            if file_entry:
                toc_entries.append({
                    "slug": chapter_slug,
                    "title": self._format_title(chapter_slug),
                    "file": file_entry.name
                })
            else:
                missing_chapters.append(chapter_slug)
        
        # Generate HTML
        html_content = self._generate_html(toc_entries, missing_chapters)
        
        # Write to file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # [HTML_INDEX] Generate index.html redirect to table_of_contents.html
        index_file = self.html_dir / "index.html"
        index_html = self._generate_index_html()
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        context.items_processed = 2  # Generated 1 master TOC file + 1 index file
        
        return ProcessorOutput(
            data={
                "status": "success",
                "message": f"Generated master TOC at {self.output_file} and index at {index_file}",
                "output_file": str(self.output_file),
                "index_file": str(index_file),
                "chapters_found": len(toc_entries),
                "chapters_missing": len(missing_chapters)
            },
            metadata={
                "toc_entries": len(toc_entries),
                "missing_chapters": missing_chapters
            }
        )
    
    def _derive_order_from_manifest(self) -> List[str]:
        """Derive chapter order from the PDF manifest if available."""
        try:
            if not self.manifest_path.exists():
                return []
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            sections = manifest.get("sections", [])
            order: List[str] = []
            for top in sections:
                # If children exist, list them; some top-levels also have a duplicate child (e.g., A Little Knowledge)
                children = top.get("children", [])
                for child in children:
                    slug = child.get("slug")
                    if slug:
                        order.append(slug)
            # Include top-level entries that have no children but have a slug themselves
            for top in sections:
                if not top.get("children") and top.get("slug"):
                    order.append(top["slug"])
            # Deduplicate while preserving order
            seen = set()
            deduped = []
            for s in order:
                if s not in seen:
                    deduped.append(s)
                    seen.add(s)
            return deduped
        except Exception as e:
            self.logger.error("Failed to derive order from manifest: %s", e)
            return []
    
    def _load_hierarchical_structure(self) -> List[Dict[str, Any]]:
        """Load hierarchical section structure from manifest.
        
        Returns a list of sections with their children:
        [
            {
                "title": "Rules Book",
                "slug": "table-of-contents-rules-book", 
                "children": [{"slug": "chapter-one-ability-scores", "title": "..."}, ...]
            },
            ...
        ]
        """
        try:
            if not self.manifest_path.exists():
                return []
            
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            sections = manifest.get("sections", [])
            
            result = []
            for section in sections:
                # Extract section title, removing "Table of Contents--" prefix if present
                section_title = section.get("title", "")
                if section_title.startswith("Table of Contents--"):
                    section_title = section_title[len("Table of Contents--"):]
                
                section_data = {
                    "title": section_title,
                    "slug": section.get("slug", ""),
                    "children": []
                }
                
                # Add children
                for child in section.get("children", []):
                    child_slug = child.get("slug")
                    if child_slug:
                        section_data["children"].append({
                            "slug": child_slug,
                            "title": child.get("title", "")
                        })
                
                result.append(section_data)
            
            return result
            
        except Exception as e:
            self.logger.error("Failed to load hierarchical structure from manifest: %s", e)
            return []
    
    def _generate_index_html(self) -> str:
        """Generate index.html that redirects to table_of_contents.html.
        
        [HTML_INDEX] The output html should contain an index.html page that 
        redirects to the table of contents.
        """
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url=table_of_contents.html">
    <meta name="generator" content="Dark Sun PF2E Pipeline">
    <title>Dark Sun - Redirecting...</title>
    <style>
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background-color: #1a1a1a;
            color: #e8e6e3;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .redirect-message {
            max-width: 600px;
            padding: 2rem;
        }
        h1 {
            color: #ca5804;
            margin-bottom: 1rem;
        }
        a {
            color: #8ab4f8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="redirect-message">
        <h1>Dark Sun</h1>
        <p>Redirecting to Table of Contents...</p>
        <p>If you are not redirected automatically, <a href="table_of_contents.html">click here</a>.</p>
    </div>
</body>
</html>
'''
    
    def _format_title(self, slug: str) -> str:
        """Convert slug to human-readable title."""
        # Remove leading numbers and hyphens, then title case
        parts = slug.split('-')
        
        # Handle special cases
        if slug.startswith("chapter-"):
            # Extract chapter number and title
            if len(parts) >= 3:
                if parts[1].isdigit():
                    chapter_num = parts[1]
                    title_parts = parts[2:]
                else:
                    # Handle "chapter-one", "chapter-two", etc.
                    chapter_num = parts[1]
                    title_parts = parts[2:]
                
                title = ' '.join(word.capitalize() for word in title_parts)
                return f"Chapter {chapter_num.capitalize()}: {title}"
        
        # For non-chapter entries, just title case
        return ' '.join(word.capitalize() for word in parts)
    
    def _generate_html(self, toc_entries: List[Dict], missing_chapters: List[str]) -> str:
        """Generate the master TOC HTML with hierarchical structure."""
        # Load hierarchical structure from manifest
        hierarchical_sections = self._load_hierarchical_structure()
        
        # Build a map of slugs to file entries for quick lookup
        slug_to_entry = {entry["slug"]: entry for entry in toc_entries}
        
        # Build hierarchical TOC HTML
        toc_html = []
        
        if hierarchical_sections:
            # Use hierarchical structure from manifest
            for section in hierarchical_sections:
                section_title = section["title"]
                children = section["children"]
                
                # Filter to only children that have been converted
                available_children = [
                    child for child in children 
                    if child["slug"] in slug_to_entry
                ]
                
                # Skip sections with no converted children
                if not available_children:
                    continue
                
                # Add section header
                toc_html.append(f'<h3 class="toc-section-header">{section_title}</h3>')
                toc_html.append('<ul class="toc-section-chapters">')
                
                # Add chapters under this section
                for child in available_children:
                    entry = slug_to_entry[child["slug"]]
                    toc_html.append(
                        f'    <li class="toc-chapter"><a href="{entry["file"]}">{entry["title"]}</a></li>'
                    )
                
                toc_html.append('</ul>')
        else:
            # Fallback to flat list if hierarchical structure not available
            toc_html.append('<ul>')
            for entry in toc_entries:
                toc_html.append(
                    f'<li><a href="{entry["file"]}">{entry["title"]}</a></li>'
                )
            toc_html.append('</ul>')
        
        toc_content = '\n'.join(toc_html)
        
        # Build missing chapters list (if any)
        missing_html = ""
        if missing_chapters:
            missing_items = [f'<li>{self._format_title(slug)}</li>' for slug in missing_chapters]
            missing_html = f'''
<section class="missing-chapters">
    <h2>Chapters Not Yet Converted</h2>
    <ul>
        {''.join(missing_items)}
    </ul>
</section>
'''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Dark Sun PF2E Pipeline">
    <meta name="source" content="AD&D 2E Dark Sun Box Set">
    <title>Dark Sun - Table of Contents</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>Dark Sun - Master Table of Contents</h1>
    
    <section>
        <h2>Available Chapters</h2>
        {toc_content}
    </section>
    
    {missing_html}
    
    <footer>
        <p>Generated from AD&D 2E Dark Sun Box Set</p>
        <p>Conversion Pipeline for Foundry VTT / Pathfinder 2E</p>
    </footer>
</body>
</html>
'''

