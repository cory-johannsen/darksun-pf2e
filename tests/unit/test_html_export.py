"""Unit tests for html_export postprocessor."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools.pdf_pipeline.domain import ExecutionContext, ProcessorOutput
from tools.pdf_pipeline.postprocessors.html_export import (
    HTMLExportPostProcessor,
    _export_html_task,
    _fix_letter_spacing,
    _reposition_chapter2_tables,
    _generate_html_template,
)


class TestFixLetterSpacing(unittest.TestCase):
    """Test the _fix_letter_spacing function."""
    
    def test_fix_basic_letter_spacing(self):
        """Test fixing spaced letters like 'M u l e'."""
        # Note: _fix_letter_spacing requires 5+ letters in sequence
        input_text = "The M u l e s carried goods"
        result = _fix_letter_spacing(input_text)
        # Should combine at least some of the spaced letters
        self.assertLess(result.count(' u '), input_text.count(' u '))
    
    def test_fix_multiple_spaced_sequences(self):
        """Test fixing multiple spaced letter sequences."""
        input_text = "A c a c i a trees and b a o b a b bushes"
        result = _fix_letter_spacing(input_text)
        # Should combine the spaced letters
        self.assertNotIn("c a c", result)
        self.assertNotIn("o b a b", result)
    
    def test_preserve_normal_spacing(self):
        """Test that normal word spacing is preserved."""
        input_text = "This is normal text with proper spacing"
        result = _fix_letter_spacing(input_text)
        self.assertEqual(result, input_text)
    
    def test_fix_after_numbers(self):
        """Test fixing spaced letters after numbers."""
        input_text = "12:00 e a s t e r n time"
        result = _fix_letter_spacing(input_text)
        # Should combine the spaced letters
        self.assertIn("eastern", result.lower())
    
    def test_empty_string(self):
        """Test handling empty string."""
        result = _fix_letter_spacing("")
        self.assertEqual(result, "")


class TestRepositionChapter2Tables(unittest.TestCase):
    """Test the _reposition_chapter2_tables function."""
    
    def test_reposition_height_weight_table(self):
        """Test repositioning Height & Weight table after its header."""
        html = """
        <p id="header-1-height-and-weight">Height and Weight</p>
        <p>Some intervening text</p>
        <table>
            <tr><th>Height in Inches</th><th>Weight in Pounds</th></tr>
            <tr><td>60</td><td>150</td></tr>
        </table>
        """
        result = _reposition_chapter2_tables(html)
        # Table should come immediately after header
        header_pos = result.index('height-and-weight')
        table_pos = result.index('<table>')
        text_pos = result.index('Some intervening text')
        self.assertLess(header_pos, table_pos)
        self.assertLess(table_pos, text_pos)
    
    def test_reposition_starting_age_table(self):
        """Test repositioning Starting Age table after its header."""
        html = """
        <p id="header-2-starting-age">Starting Age</p>
        <p>Some text between</p>
        <table>
            <tr><th>Base Age</th><th>Variable</th><th>Max Age Range</th></tr>
            <tr><td>15</td><td>1d6</td><td>40+2d10</td></tr>
        </table>
        """
        result = _reposition_chapter2_tables(html)
        # Table should come immediately after header
        header_pos = result.index('starting-age')
        table_pos = result.index('<table>')
        text_pos = result.index('Some text between')
        self.assertLess(header_pos, table_pos)
        self.assertLess(table_pos, text_pos)
    
    def test_reposition_aging_effects_table(self):
        """Test repositioning Aging Effects table after its header."""
        html = """
        <p id="header-3-aging-effects">Aging Effects</p>
        <p>Descriptive text</p>
        <table>
            <tr><th>Race</th><th>Middle Age</th><th>Old Age</th><th>Venerable</th></tr>
            <tr><td>Human</td><td>40</td><td>60</td><td>80</td></tr>
        </table>
        """
        result = _reposition_chapter2_tables(html)
        # Table should come immediately after header
        header_pos = result.index('aging-effects')
        table_pos = result.index('<table>')
        text_pos = result.index('Descriptive text')
        self.assertLess(header_pos, table_pos)
        self.assertLess(table_pos, text_pos)
    
    def test_no_changes_when_already_positioned(self):
        """Test that already correctly positioned tables are not affected."""
        html = """
        <p id="header-1-height-and-weight">Height and Weight</p>
        <table>
            <tr><th>Height in Inches</th><th>Weight in Pounds</th></tr>
        </table>
        <p>Following text</p>
        """
        result = _reposition_chapter2_tables(html)
        # Should remain mostly unchanged (may have minor whitespace differences)
        self.assertIn('height-and-weight', result)
        self.assertIn('<table>', result)


class TestGenerateHtmlTemplate(unittest.TestCase):
    """Test the _generate_html_template function."""
    
    def test_basic_template_structure(self):
        """Test that template has all required elements."""
        title = "Test Chapter"
        toc_html = '<nav id="table-of-contents"><ul><li>Item</li></ul></nav>'
        main_content = "<p>Main content here</p>"
        slug = "test-chapter"
        title_prefix = "Dark Sun - "
        
        result = _generate_html_template(title, toc_html, main_content, slug, title_prefix)
        
        # Check essential elements
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<html lang=\"en\">", result)
        self.assertIn("<title>Dark Sun - Test Chapter</title>", result)
        self.assertIn('meta name="slug" content="test-chapter"', result)
        self.assertIn('<link rel="stylesheet" href="styles.css">', result)
        self.assertIn('<h1>Test Chapter</h1>', result)
        self.assertIn('<a href="table_of_contents.html">Back to Table of Contents</a>', result)
        self.assertIn(toc_html, result)
        self.assertIn(main_content, result)
    
    def test_empty_toc(self):
        """Test template with no TOC."""
        result = _generate_html_template("Title", "", "<p>Content</p>", "slug", "Prefix - ")
        self.assertIn("<p>Content</p>", result)
        self.assertIn("<!DOCTYPE html>", result)
    
    def test_custom_title_prefix(self):
        """Test custom title prefix."""
        result = _generate_html_template("My Chapter", "", "<p>Text</p>", "my-slug", "Custom: ")
        self.assertIn("<title>Custom: My Chapter</title>", result)


class TestExportHtmlTask(unittest.TestCase):
    """Test the _export_html_task worker function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_simple_journal(self):
        """Test exporting a simple journal file."""
        # Create test journal JSON
        journal_data = {
            "slug": "test-chapter",
            "data": {
                "title": "Test Chapter",
                "content": "<p>Test content here</p>"
            }
        }
        json_file = self.temp_path / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(journal_data, f)
        
        # Create task
        task = {
            "json_file": str(json_file),
            "output_dir": str(self.temp_path),
            "title_prefix": "Test - "
        }
        
        # Execute
        result = _export_html_task(task)
        
        # Verify result
        self.assertEqual(result["items"], 1)
        self.assertEqual(len(result["warnings"]), 0)
        self.assertEqual(len(result["errors"]), 0)
        self.assertIsNotNone(result["output_file"])
        
        # Verify HTML file was created
        output_file = Path(result["output_file"])
        self.assertTrue(output_file.exists())
        
        # Verify HTML content
        html_content = output_file.read_text(encoding="utf-8")
        self.assertIn("Test Chapter", html_content)
        self.assertIn("Test content here", html_content)
    
    def test_export_journal_with_toc(self):
        """Test exporting journal with table of contents."""
        journal_data = {
            "slug": "chapter-with-toc",
            "data": {
                "title": "Chapter With TOC",
                "content": '<nav id="table-of-contents"><ul><li>Section 1</li></ul></nav><p>Main content</p>'
            }
        }
        json_file = self.temp_path / "toc.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(journal_data, f)
        
        task = {
            "json_file": str(json_file),
            "output_dir": str(self.temp_path),
            "title_prefix": ""
        }
        
        result = _export_html_task(task)
        self.assertEqual(result["items"], 1)
        
        # Verify TOC is in output
        output_file = Path(result["output_file"])
        html_content = output_file.read_text(encoding="utf-8")
        self.assertIn('table-of-contents', html_content)
        self.assertIn('Section 1', html_content)
    
    def test_export_empty_content_warning(self):
        """Test that empty content generates a warning."""
        journal_data = {
            "slug": "empty",
            "data": {
                "title": "Empty",
                "content": ""
            }
        }
        json_file = self.temp_path / "empty.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(journal_data, f)
        
        task = {
            "json_file": str(json_file),
            "output_dir": str(self.temp_path),
            "title_prefix": ""
        }
        
        result = _export_html_task(task)
        self.assertEqual(result["items"], 0)
        self.assertGreater(len(result["warnings"]), 0)
        self.assertIsNone(result["output_file"])
    
    def test_export_missing_file_error(self):
        """Test that missing file generates an error."""
        task = {
            "json_file": str(self.temp_path / "nonexistent.json"),
            "output_dir": str(self.temp_path),
            "title_prefix": ""
        }
        
        result = _export_html_task(task)
        self.assertEqual(result["items"], 0)
        self.assertGreater(len(result["errors"]), 0)


class TestHTMLExportPostProcessor(unittest.TestCase):
    """Test the HTMLExportPostProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.input_dir = self.temp_path / "input"
        self.output_dir = self.temp_path / "output"
        self.input_dir.mkdir()
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test processor initialization."""
        spec = Mock()
        spec.config = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "title_prefix": "Test - "
        }
        
        processor = HTMLExportPostProcessor(spec)
        self.assertEqual(processor.input_dir, self.input_dir)
        self.assertEqual(processor.output_dir, self.output_dir)
        self.assertEqual(processor.title_prefix, "Test - ")
    
    def test_postprocess_creates_output_dir(self):
        """Test that postprocess creates output directory."""
        # Create a test journal
        journal_data = {
            "slug": "test",
            "data": {"title": "Test", "content": "<p>Content</p>"}
        }
        json_file = self.input_dir / "test.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(journal_data, f)
        
        spec = Mock()
        spec.config = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir)
        }
        
        processor = HTMLExportPostProcessor(spec)
        context = ExecutionContext(pipeline_name="test")
        output = ProcessorOutput(data={}, metadata={})
        
        result = processor.postprocess(output, context)
        
        # Output directory should be created
        self.assertTrue(self.output_dir.exists())
        self.assertTrue(self.output_dir.is_dir())
    
    def test_postprocess_no_journal_files_warning(self):
        """Test warning when no journal files found."""
        spec = Mock()
        spec.config = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir)
        }
        
        processor = HTMLExportPostProcessor(spec)
        context = ExecutionContext(pipeline_name="test")
        output = ProcessorOutput(data={}, metadata={})
        
        result = processor.postprocess(output, context)
        
        # Should generate a warning
        self.assertGreater(len(context.warnings), 0)
    
    def test_postprocess_sequential_export(self):
        """Test sequential export of multiple journals."""
        # Create multiple test journals
        for i in range(3):
            journal_data = {
                "slug": f"chapter-{i}",
                "data": {"title": f"Chapter {i}", "content": f"<p>Content {i}</p>"}
            }
            json_file = self.input_dir / f"chapter-{i}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(journal_data, f)
        
        spec = Mock()
        spec.config = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "parallel": False
        }
        
        processor = HTMLExportPostProcessor(spec)
        context = ExecutionContext(pipeline_name="test")
        context.metadata = {"parallel": False}
        output = ProcessorOutput(data={}, metadata={})
        
        result = processor.postprocess(output, context)
        
        # Should process all 3 files
        self.assertEqual(context.items_processed, 3)
        self.assertEqual(result.metadata["html_export_count"], 3)
        
        # All HTML files should exist
        for i in range(3):
            html_file = self.output_dir / f"chapter-{i}.html"
            self.assertTrue(html_file.exists())
    
    def test_generate_html_method(self):
        """Test the _generate_html method."""
        spec = Mock()
        spec.config = {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "title_prefix": "Prefix: "
        }
        
        processor = HTMLExportPostProcessor(spec)
        result = processor._generate_html(
            "Test Title",
            "<p>Content</p>",
            "test-slug"
        )
        
        self.assertIn("Prefix: Test Title", result)
        self.assertIn("test-slug", result)
        self.assertIn("<p>Content</p>", result)


if __name__ == "__main__":
    unittest.main()

