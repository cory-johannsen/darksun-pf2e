"""Unit tests for master_toc postprocessor."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from tools.pdf_pipeline.domain import ExecutionContext, ProcessorInput, ProcessorOutput
from tools.pdf_pipeline.postprocessors.master_toc import MasterTOCGenerator


class TestMasterTOCGenerator(unittest.TestCase):
    """Test the MasterTOCGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.html_dir = self.temp_path / "html"
        self.html_dir.mkdir()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test processor initialization."""
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "output_file": str(self.temp_path / "toc.html"),
            "manifest_path": str(self.temp_path / "manifest.json")
        }
        
        generator = MasterTOCGenerator(spec)
        self.assertEqual(generator.html_dir, self.html_dir)
        self.assertEqual(generator.output_file, self.temp_path / "toc.html")
        self.assertEqual(generator.manifest_path, self.temp_path / "manifest.json")
    
    def test_format_title_chapter(self):
        """Test _format_title for chapter slugs."""
        spec = Mock()
        spec.config = {"html_dir": str(self.html_dir)}
        generator = MasterTOCGenerator(spec)
        
        # Test numeric chapter
        result = generator._format_title("chapter-1-ability-scores")
        self.assertEqual(result, "Chapter 1: Ability Scores")
        
        # Test word chapter
        result = generator._format_title("chapter-one-ability-scores")
        self.assertEqual(result, "Chapter One: Ability Scores")
        
        # Test multi-word title
        result = generator._format_title("chapter-three-player-character-classes")
        self.assertEqual(result, "Chapter Three: Player Character Classes")
    
    def test_format_title_non_chapter(self):
        """Test _format_title for non-chapter slugs."""
        spec = Mock()
        spec.config = {"html_dir": str(self.html_dir)}
        generator = MasterTOCGenerator(spec)
        
        result = generator._format_title("a-little-knowledge")
        self.assertEqual(result, "A Little Knowledge")
        
        result = generator._format_title("kluzd")
        self.assertEqual(result, "Kluzd")
    
    def test_generate_index_html(self):
        """Test _generate_index_html creates valid redirect."""
        spec = Mock()
        spec.config = {"html_dir": str(self.html_dir)}
        generator = MasterTOCGenerator(spec)
        
        result = generator._generate_index_html()
        
        # Check for essential elements
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn('meta http-equiv="refresh"', result)
        self.assertIn('url=table_of_contents.html', result)
        self.assertIn('<a href="table_of_contents.html">click here</a>', result)
        self.assertIn("Dark Sun", result)
    
    def test_derive_order_from_manifest(self):
        """Test _derive_order_from_manifest with valid manifest."""
        # Create test manifest
        manifest = {
            "sections": [
                {
                    "title": "Part One",
                    "children": [
                        {"slug": "chapter-one-ability-scores", "title": "Chapter One"},
                        {"slug": "chapter-two-player-character-races", "title": "Chapter Two"}
                    ]
                },
                {
                    "title": "Part Two",
                    "children": [
                        {"slug": "chapter-three-player-character-classes", "title": "Chapter Three"}
                    ]
                },
                {
                    "slug": "standalone-chapter",
                    "title": "Standalone"
                }
            ]
        }
        manifest_file = self.temp_path / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "manifest_path": str(manifest_file)
        }
        generator = MasterTOCGenerator(spec)
        
        result = generator._derive_order_from_manifest()
        
        # Check order
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], "chapter-one-ability-scores")
        self.assertEqual(result[1], "chapter-two-player-character-races")
        self.assertEqual(result[2], "chapter-three-player-character-classes")
        self.assertEqual(result[3], "standalone-chapter")
    
    def test_derive_order_missing_manifest(self):
        """Test _derive_order_from_manifest with missing manifest."""
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "manifest_path": str(self.temp_path / "nonexistent.json")
        }
        generator = MasterTOCGenerator(spec)
        
        result = generator._derive_order_from_manifest()
        self.assertEqual(result, [])
    
    def test_generate_html_with_entries(self):
        """Test _generate_html with TOC entries."""
        spec = Mock()
        spec.config = {"html_dir": str(self.html_dir)}
        generator = MasterTOCGenerator(spec)
        
        toc_entries = [
            {"slug": "chapter-one", "title": "Chapter One", "file": "chapter-one.html"},
            {"slug": "chapter-two", "title": "Chapter Two", "file": "chapter-two.html"}
        ]
        missing_chapters = []
        
        result = generator._generate_html(toc_entries, missing_chapters)
        
        # Check structure
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<title>Dark Sun - Table of Contents</title>", result)
        self.assertIn('<link rel="stylesheet" href="styles.css">', result)
        self.assertIn('<a href="chapter-one.html">Chapter One</a>', result)
        self.assertIn('<a href="chapter-two.html">Chapter Two</a>', result)
        self.assertIn("Available Chapters", result)
    
    def test_generate_html_with_missing_chapters(self):
        """Test _generate_html with missing chapters."""
        spec = Mock()
        spec.config = {"html_dir": str(self.html_dir)}
        generator = MasterTOCGenerator(spec)
        
        toc_entries = [
            {"slug": "chapter-one", "title": "Chapter One", "file": "chapter-one.html"}
        ]
        missing_chapters = ["chapter-two-player-character-races", "chapter-three"]
        
        result = generator._generate_html(toc_entries, missing_chapters)
        
        # Check that missing chapters section exists
        self.assertIn("Chapters Not Yet Converted", result)
        self.assertIn("Chapter Two: Player Character Races", result)
    
    def test_process_no_html_dir(self):
        """Test process when HTML directory doesn't exist."""
        spec = Mock()
        spec.config = {
            "html_dir": str(self.temp_path / "nonexistent"),
            "output_file": str(self.temp_path / "toc.html")
        }
        generator = MasterTOCGenerator(spec)
        
        context = ExecutionContext(pipeline_name="test")
        input_data = ProcessorInput(data={}, metadata={})
        
        result = generator.process(input_data, context)
        
        # Should return error status
        self.assertEqual(result.data["status"], "error")
        self.assertEqual(result.metadata["chapters_found"], 0)
    
    def test_process_with_html_files(self):
        """Test process with actual HTML files."""
        # Create test HTML files
        chapters = [
            "chapter-one-ability-scores",
            "chapter-two-player-character-races",
            "chapter-three-player-character-classes"
        ]
        for slug in chapters:
            html_file = self.html_dir / f"{slug}.html"
            html_file.write_text(f"<html><body>{slug}</body></html>", encoding="utf-8")
        
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "output_file": str(self.html_dir / "table_of_contents.html"),
            "manifest_path": str(self.temp_path / "manifest.json")
        }
        generator = MasterTOCGenerator(spec)
        
        context = ExecutionContext(pipeline_name="test")
        input_data = ProcessorInput(data={}, metadata={})
        
        result = generator.process(input_data, context)
        
        # Check success
        self.assertEqual(result.data["status"], "success")
        self.assertEqual(result.data["chapters_found"], 3)
        # The CHAPTER_ORDER has many chapters, so most will be missing
        self.assertGreater(result.data["chapters_missing"], 0)
        
        # Check files were created
        toc_file = Path(result.data["output_file"])
        index_file = Path(result.data["index_file"])
        self.assertTrue(toc_file.exists())
        self.assertTrue(index_file.exists())
        
        # Check TOC content
        toc_content = toc_file.read_text(encoding="utf-8")
        self.assertIn("chapter-one-ability-scores.html", toc_content)
        self.assertIn("chapter-two-player-character-races.html", toc_content)
        self.assertIn("chapter-three-player-character-classes.html", toc_content)
        
        # Check index redirect
        index_content = index_file.read_text(encoding="utf-8")
        self.assertIn("table_of_contents.html", index_content)
        self.assertIn("refresh", index_content.lower())
    
    def test_process_with_missing_chapters(self):
        """Test process with some chapters missing."""
        # Create only one HTML file
        html_file = self.html_dir / "chapter-one-ability-scores.html"
        html_file.write_text("<html><body>Chapter One</body></html>", encoding="utf-8")
        
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "output_file": str(self.html_dir / "table_of_contents.html"),
            "manifest_path": str(self.temp_path / "manifest.json")
        }
        generator = MasterTOCGenerator(spec)
        
        context = ExecutionContext(pipeline_name="test")
        input_data = ProcessorInput(data={}, metadata={})
        
        result = generator.process(input_data, context)
        
        # Should succeed but report missing chapters
        self.assertEqual(result.data["status"], "success")
        self.assertEqual(result.data["chapters_found"], 1)
        self.assertGreater(result.data["chapters_missing"], 0)
        self.assertGreater(len(result.metadata["missing_chapters"]), 0)
    
    def test_process_excludes_toc_file_itself(self):
        """Test that table_of_contents.html is excluded from TOC entries."""
        # Create HTML files including table_of_contents.html
        html_file1 = self.html_dir / "chapter-one.html"
        html_file1.write_text("<html><body>Chapter</body></html>", encoding="utf-8")
        
        toc_file = self.html_dir / "table_of_contents.html"
        toc_file.write_text("<html><body>TOC</body></html>", encoding="utf-8")
        
        spec = Mock()
        spec.config = {
            "html_dir": str(self.html_dir),
            "output_file": str(toc_file),
            "manifest_path": str(self.temp_path / "manifest.json")
        }
        generator = MasterTOCGenerator(spec)
        
        context = ExecutionContext(pipeline_name="test")
        input_data = ProcessorInput(data={}, metadata={})
        
        result = generator.process(input_data, context)
        
        # Should only count chapter-one, not table_of_contents
        # Since we're using the static CHAPTER_ORDER and chapter-one isn't in it,
        # chapters_found will be 0, but this tests the exclusion logic
        toc_content = toc_file.read_text(encoding="utf-8")
        # TOC should not link to itself
        self.assertNotIn('href="table_of_contents.html"', toc_content)


if __name__ == "__main__":
    unittest.main()

