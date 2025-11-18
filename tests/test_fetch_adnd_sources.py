#!/usr/bin/env python3
"""
Tests for the AD&D source fetcher script.

TEST-1: Tests MUST verify URL parsing and extraction logic.
TEST-2: Tests MUST verify deduplication by title and format priority.
TEST-3: Tests MUST verify file existence checking.
TEST-4: Tests MUST verify download functionality.
TEST-5: Tests MUST verify ZIP extraction functionality.
TEST-6: Tests MUST verify error handling for failed downloads.
"""

import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

import pytest
import requests

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from fetch_adnd_sources import ArchiveOrgFetcher, SourceFile, calculate_optimal_threads


class TestOptimalThreads:
    """Tests for optimal thread calculation."""
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_normal(self, mock_cpu_count):
        """TEST: Optimal threads calculated correctly for normal CPU count."""
        mock_cpu_count.return_value = 12
        
        # 12 cores * 3 = 36 threads (clamped to 32 max)
        result = calculate_optimal_threads()
        assert result == 32
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_low_cores(self, mock_cpu_count):
        """TEST: Optimal threads respects minimum of 4."""
        mock_cpu_count.return_value = 1
        
        # 1 core * 3 = 3, but minimum is 4
        result = calculate_optimal_threads()
        assert result == 4
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_medium_cores(self, mock_cpu_count):
        """TEST: Optimal threads calculated correctly for medium CPU count."""
        mock_cpu_count.return_value = 4
        
        # 4 cores * 3 = 12 threads
        result = calculate_optimal_threads()
        assert result == 12
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_high_cores(self, mock_cpu_count):
        """TEST: Optimal threads clamped at maximum of 32."""
        mock_cpu_count.return_value = 16
        
        # 16 cores * 3 = 48, but max is 32
        result = calculate_optimal_threads()
        assert result == 32
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_none_fallback(self, mock_cpu_count):
        """TEST: Falls back to 8 when cpu_count returns None."""
        mock_cpu_count.return_value = None
        
        result = calculate_optimal_threads()
        assert result == 8
    
    @patch("fetch_adnd_sources.os.cpu_count")
    def test_calculate_optimal_threads_exception_fallback(self, mock_cpu_count):
        """TEST: Falls back to 8 when exception occurs."""
        mock_cpu_count.side_effect = Exception("Test exception")
        
        result = calculate_optimal_threads()
        assert result == 8


class TestSourceFileModel:
    """Tests for the SourceFile Pydantic model."""

    def test_source_file_creation(self):
        """TEST: SourceFile model creation with valid data."""
        source = SourceFile(
            title="Test Book",
            url="https://example.com/test.pdf",
            format="pdf",
            local_path=Path("/tmp/test.pdf"),
            priority=1,
        )
        assert source.title == "Test Book"
        assert source.format == "pdf"
        assert source.priority == 1

    def test_source_file_priority_ordering(self):
        """TEST: SourceFile priority correctly orders formats."""
        pdf = SourceFile(
            title="Book",
            url="https://example.com/book.pdf",
            format="pdf",
            local_path=Path("/tmp/book.pdf"),
            priority=1,
        )
        epub = SourceFile(
            title="Book",
            url="https://example.com/book.epub",
            format="epub",
            local_path=Path("/tmp/book.epub"),
            priority=2,
        )
        zip_file = SourceFile(
            title="Book",
            url="https://example.com/book.zip",
            format="zip",
            local_path=Path("/tmp/book.zip"),
            priority=3,
        )
        
        files = sorted([zip_file, epub, pdf], key=lambda x: x.priority)
        assert files[0].format == "pdf"
        assert files[1].format == "epub"
        assert files[2].format == "zip"


class TestArchiveOrgFetcher:
    """Tests for the ArchiveOrgFetcher class."""

    @pytest.fixture
    def temp_sources_dir(self):
        """Create a temporary sources directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def fetcher(self, temp_sources_dir):
        """Create a fetcher instance with temp directory."""
        return ArchiveOrgFetcher(temp_sources_dir)

    def test_fetcher_initialization(self, temp_sources_dir):
        """TEST: Fetcher initializes with correct directory."""
        fetcher = ArchiveOrgFetcher(temp_sources_dir)
        assert fetcher.sources_dir == temp_sources_dir
        assert temp_sources_dir.exists()

    def test_is_downloadable_file_skips_metadata(self, fetcher):
        """TEST: Metadata files are correctly skipped."""
        assert not fetcher._is_downloadable_file("test__ia_thumb.jpg")
        assert not fetcher._is_downloadable_file("test_meta.xml")
        assert not fetcher._is_downloadable_file("test_meta.sqlite")
        assert not fetcher._is_downloadable_file("test_files.xml")
        assert not fetcher._is_downloadable_file("test_archive.torrent")
        assert fetcher._is_downloadable_file("test.pdf")

    def test_extract_format_identifies_correct_formats(self, fetcher):
        """TEST: File format extraction works correctly."""
        assert fetcher._extract_format("book.pdf") == "pdf"
        assert fetcher._extract_format("book.epub") == "epub"
        assert fetcher._extract_format("book.zip") == "zip"
        assert fetcher._extract_format("book.txt") is None
        assert fetcher._extract_format("BOOK.PDF") == "pdf"  # case insensitive

    def test_extract_title_normalizes_correctly(self, fetcher):
        """TEST: Title extraction and normalization."""
        assert fetcher._extract_title("TSR_Inc_-_Book_Name.pdf") == "TSR Inc Book Name"
        assert fetcher._extract_title("TSR_Inc_-_Book_Name_djvu.pdf") == "TSR Inc Book Name"
        assert fetcher._extract_title("TSR_Inc_-_Book_Name_text.pdf") == "TSR Inc Book Name"
        assert fetcher._extract_title("a.pdf") is None  # too short

    def test_parse_download_links_extracts_files(self, fetcher):
        """TEST: HTML parsing extracts download links."""
        html = """
        <html>
            <body>
                <a href="Book_One.pdf">Book One PDF</a>
                <a href="Book_One.epub">Book One EPUB</a>
                <a href="Book_One_meta.xml">Metadata</a>
                <a href="Book_Two.zip">Book Two ZIP</a>
            </body>
        </html>
        """
        
        files = fetcher.parse_download_links(html)
        
        # Should extract 3 files (skip metadata)
        assert len(files) == 3
        formats = [f.format for f in files]
        assert "pdf" in formats
        assert "epub" in formats
        assert "zip" in formats

    def test_deduplicate_by_title_keeps_pdf_and_epub(self, fetcher, temp_sources_dir):
        """TEST: Deduplication keeps both PDF and EPUB, skips ZIP."""
        files = [
            SourceFile(
                title="Book",
                url="https://example.com/book.epub",
                format="epub",
                local_path=temp_sources_dir / "book.epub",
                priority=2,
            ),
            SourceFile(
                title="Book",
                url="https://example.com/book.pdf",
                format="pdf",
                local_path=temp_sources_dir / "book.pdf",
                priority=1,
            ),
            SourceFile(
                title="Book",
                url="https://example.com/book.zip",
                format="zip",
                local_path=temp_sources_dir / "book.zip",
                priority=3,
            ),
        ]
        
        deduplicated = fetcher.deduplicate_by_title(files)
        
        # Should keep both PDF and EPUB, skip ZIP
        assert len(deduplicated) == 2
        formats = {f.format for f in deduplicated}
        assert "pdf" in formats
        assert "epub" in formats
        assert "zip" not in formats

    def test_deduplicate_keeps_zip_when_no_pdf_epub(self, fetcher, temp_sources_dir):
        """TEST: Deduplication keeps ZIP if neither PDF nor EPUB exists."""
        files = [
            SourceFile(
                title="Book",
                url="https://example.com/book.zip",
                format="zip",
                local_path=temp_sources_dir / "book.zip",
                priority=3,
            ),
        ]
        
        deduplicated = fetcher.deduplicate_by_title(files)
        
        # Should keep ZIP when it's the only format available
        assert len(deduplicated) == 1
        assert deduplicated[0].format == "zip"

    def test_deduplicate_keeps_different_titles(self, fetcher, temp_sources_dir):
        """TEST: Deduplication keeps files with different titles."""
        files = [
            SourceFile(
                title="Book One",
                url="https://example.com/book1.pdf",
                format="pdf",
                local_path=temp_sources_dir / "book1.pdf",
                priority=1,
            ),
            SourceFile(
                title="Book Two",
                url="https://example.com/book2.pdf",
                format="pdf",
                local_path=temp_sources_dir / "book2.pdf",
                priority=1,
            ),
        ]
        
        deduplicated = fetcher.deduplicate_by_title(files)
        
        assert len(deduplicated) == 2

    def test_get_extraction_marker_path(self, fetcher, temp_sources_dir):
        """TEST: Extraction marker path is constructed correctly."""
        zip_path = temp_sources_dir / "archive.zip"
        marker_path = fetcher.get_extraction_marker_path(zip_path)
        
        assert marker_path == temp_sources_dir / "archive.zip.extracted"

    def test_filter_existing_files(self, fetcher, temp_sources_dir):
        """TEST: Existing files are filtered out."""
        # Create one existing file
        existing_file = temp_sources_dir / "existing.pdf"
        existing_file.write_text("content")
        
        files = [
            SourceFile(
                title="Existing",
                url="https://example.com/existing.pdf",
                format="pdf",
                local_path=existing_file,
                priority=1,
            ),
            SourceFile(
                title="Missing",
                url="https://example.com/missing.pdf",
                format="pdf",
                local_path=temp_sources_dir / "missing.pdf",
                priority=1,
            ),
        ]
        
        missing = fetcher.filter_existing_files(files)
        
        assert len(missing) == 1
        assert missing[0].title == "Missing"

    def test_filter_existing_files_with_zip_marker(self, fetcher, temp_sources_dir):
        """TEST: ZIP files with extraction markers are filtered out."""
        zip_path = temp_sources_dir / "archive.zip"
        marker_path = fetcher.get_extraction_marker_path(zip_path)
        
        # Create marker file (simulating previous extraction)
        marker_path.write_text("Extracted")
        
        files = [
            SourceFile(
                title="Archive",
                url="https://example.com/archive.zip",
                format="zip",
                local_path=zip_path,
                priority=3,
            ),
            SourceFile(
                title="Missing",
                url="https://example.com/missing.pdf",
                format="pdf",
                local_path=temp_sources_dir / "missing.pdf",
                priority=1,
            ),
        ]
        
        filtered = fetcher.filter_existing_files(files)
        
        # Archive should be filtered out due to marker, only Missing should remain
        assert len(filtered) == 1
        assert filtered[0].title == "Missing"

    @patch("fetch_adnd_sources.requests.get")
    def test_download_file_success(self, mock_get, fetcher, temp_sources_dir):
        """TEST: File download succeeds with valid response."""
        # Mock successful download
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b"chunk1", b"chunk2"])
        mock_response.headers = {"content-length": "12"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        source_file = SourceFile(
            title="Test",
            url="https://example.com/test.pdf",
            format="pdf",
            local_path=temp_sources_dir / "test.pdf",
            priority=1,
        )
        
        result = fetcher.download_file(source_file)
        
        assert result is True
        assert source_file.local_path.exists()
        assert source_file.local_path.read_bytes() == b"chunk1chunk2"

    @patch("fetch_adnd_sources.requests.get")
    def test_download_file_handles_network_error(self, mock_get, fetcher, temp_sources_dir):
        """TEST: Download handles network errors gracefully."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        source_file = SourceFile(
            title="Test",
            url="https://example.com/test.pdf",
            format="pdf",
            local_path=temp_sources_dir / "test.pdf",
            priority=1,
        )
        
        result = fetcher.download_file(source_file)
        
        assert result is False
        assert not source_file.local_path.exists()

    @patch("fetch_adnd_sources.requests.get")
    def test_download_file_handles_http_error(self, mock_get, fetcher, temp_sources_dir):
        """TEST: Download handles HTTP errors (404, 500, etc.)."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock(side_effect=requests.HTTPError("404"))
        mock_get.return_value = mock_response
        
        source_file = SourceFile(
            title="Test",
            url="https://example.com/test.pdf",
            format="pdf",
            local_path=temp_sources_dir / "test.pdf",
            priority=1,
        )
        
        result = fetcher.download_file(source_file)
        
        assert result is False

    def test_extract_zip_file_success(self, fetcher, temp_sources_dir):
        """TEST: ZIP extraction works correctly and creates marker file."""
        # Create a test ZIP file
        zip_path = temp_sources_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
        
        result = fetcher.extract_zip_file(zip_path)
        
        assert result is True
        assert not zip_path.exists()  # ZIP should be deleted after extraction
        
        # Check marker file was created
        marker_path = fetcher.get_extraction_marker_path(zip_path)
        assert marker_path.exists()
        assert "Extracted on:" in marker_path.read_text()
        assert (temp_sources_dir / "file1.txt").exists()
        assert (temp_sources_dir / "file2.txt").exists()
        assert (temp_sources_dir / "file1.txt").read_text() == "content1"

    def test_extract_zip_file_handles_corrupt_zip(self, fetcher, temp_sources_dir):
        """TEST: Corrupt ZIP files are handled gracefully."""
        # Create a corrupt ZIP file
        zip_path = temp_sources_dir / "corrupt.zip"
        zip_path.write_bytes(b"not a zip file")
        
        result = fetcher.extract_zip_file(zip_path)
        
        assert result is False
        assert zip_path.exists()  # Should not delete on error

    def test_extract_zip_file_skips_nonexistent(self, fetcher, temp_sources_dir):
        """TEST: Extraction handles non-existent files."""
        zip_path = temp_sources_dir / "nonexistent.zip"
        
        result = fetcher.extract_zip_file(zip_path)
        
        assert result is False

    @patch("fetch_adnd_sources.requests.get")
    def test_download_and_extract_zip(self, mock_get, fetcher, temp_sources_dir):
        """TEST: ZIP files are automatically extracted after download."""
        # Create a mock ZIP file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            zf.writestr("extracted.pdf", "pdf content")
        zip_content = zip_buffer.getvalue()
        
        # Mock the download
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[zip_content])
        mock_response.headers = {"content-length": str(len(zip_content))}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        source_file = SourceFile(
            title="Test",
            url="https://example.com/test.zip",
            format="zip",
            local_path=temp_sources_dir / "test.zip",
            priority=3,
        )
        
        result = fetcher.download_file(source_file)
        
        assert result is True
        # ZIP should be extracted and removed
        assert not (temp_sources_dir / "test.zip").exists()
        assert (temp_sources_dir / "extracted.pdf").exists()

    def test_calculate_statistics(self, fetcher):
        """TEST: Download statistics are calculated correctly."""
        stats = {
            "total": 10,
            "succeeded": 7,
            "failed": 2,
            "skipped": 1,
            "extracted": 3,
        }
        
        summary = fetcher.format_statistics(stats)
        
        assert "Total files: 10" in summary
        assert "Succeeded: 7" in summary
        assert "Failed: 2" in summary
        assert "Skipped: 1" in summary
        assert "extracted: 3" in summary


class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.fixture
    def temp_sources_dir(self):
        """Create a temporary sources directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @patch("fetch_adnd_sources.requests.get")
    def test_full_workflow_with_mixed_formats(self, mock_get, temp_sources_dir):
        """TEST: Complete workflow with PDF, EPUB, and ZIP files."""
        fetcher = ArchiveOrgFetcher(temp_sources_dir)
        
        # Mock HTML response
        html = """
        <html>
            <a href="book.pdf">Book PDF</a>
            <a href="book.epub">Book EPUB</a>
            <a href="archive.zip">Archive ZIP</a>
        </html>
        """
        
        # Mock file downloads
        def mock_download(url, **kwargs):
            response = Mock()
            response.raise_for_status = Mock()
            
            if url.endswith(".zip"):
                # Create a ZIP file in memory
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    zf.writestr("from_zip.txt", "extracted content")
                response.iter_content = Mock(return_value=[zip_buffer.getvalue()])
                response.headers = {"content-length": str(len(zip_buffer.getvalue()))}
            else:
                content = b"file content"
                response.iter_content = Mock(return_value=[content])
                response.headers = {"content-length": str(len(content))}
            
            return response
        
        mock_get.side_effect = mock_download
        
        # Parse files
        files = fetcher.parse_download_links(html)
        assert len(files) == 3

        # Deduplicate (should keep both PDF and EPUB for "book", plus archive.zip)
        deduplicated = fetcher.deduplicate_by_title(files)
        assert len(deduplicated) == 3  # book.pdf, book.epub, and archive.zip
        formats = {f.format for f in deduplicated}
        assert "pdf" in formats
        assert "epub" in formats
        assert "zip" in formats
        
        # Download files
        for source_file in deduplicated:
            result = fetcher.download_file(source_file)
            assert result is True
        
        # Verify results
        assert (temp_sources_dir / "book.pdf").exists()
        assert (temp_sources_dir / "book.epub").exists()  # Now we download both
        assert not (temp_sources_dir / "archive.zip").exists()  # Should be extracted
        assert (temp_sources_dir / "from_zip.txt").exists()


class TestParallelDownloads:
    """Tests for parallel download functionality."""
    
    @pytest.fixture
    def temp_sources_dir(self):
        """Create a temporary sources directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @patch("fetch_adnd_sources.requests.get")
    def test_parallel_download_success(self, mock_get, temp_sources_dir):
        """TEST: Parallel downloads complete successfully."""
        fetcher = ArchiveOrgFetcher(temp_sources_dir)
        
        # Mock file downloads
        def mock_download(url, **kwargs):
            response = Mock()
            response.raise_for_status = Mock()
            content = b"file content"
            response.iter_content = Mock(return_value=[content])
            response.headers = {"content-length": str(len(content))}
            return response
        
        mock_get.side_effect = mock_download
        
        # Create test files
        files = [
            SourceFile(
                title=f"Book {i}",
                url=f"https://example.com/book{i}.pdf",
                format="pdf",
                local_path=temp_sources_dir / f"book{i}.pdf",
                priority=1,
            )
            for i in range(5)
        ]
        
        stats = {"total": 5, "succeeded": 0, "failed": 0, "skipped": 0, "extracted": 0}
        
        # Download in parallel
        fetcher.download_files_parallel(files, stats, max_workers=3)
        
        # Verify all succeeded
        assert stats["succeeded"] == 5
        assert stats["failed"] == 0
        assert all((temp_sources_dir / f"book{i}.pdf").exists() for i in range(5))
    
    @patch("fetch_adnd_sources.requests.get")
    def test_parallel_download_with_failures(self, mock_get, temp_sources_dir):
        """TEST: Parallel downloads handle mixed success and failure."""
        fetcher = ArchiveOrgFetcher(temp_sources_dir)
        
        # Mock: First 2 succeed, last 2 fail
        call_count = [0]
        
        def mock_download(url, **kwargs):
            call_count[0] += 1
            response = Mock()
            
            if call_count[0] <= 2:
                # Success
                response.raise_for_status = Mock()
                content = b"file content"
                response.iter_content = Mock(return_value=[content])
                response.headers = {"content-length": str(len(content))}
            else:
                # Failure
                response.raise_for_status = Mock(
                    side_effect=requests.HTTPError("404 Not Found")
                )
            
            return response
        
        mock_get.side_effect = mock_download
        
        # Create test files
        files = [
            SourceFile(
                title=f"Book {i}",
                url=f"https://example.com/book{i}.pdf",
                format="pdf",
                local_path=temp_sources_dir / f"book{i}.pdf",
                priority=1,
            )
            for i in range(4)
        ]
        
        stats = {"total": 4, "succeeded": 0, "failed": 0, "skipped": 0, "extracted": 0}
        
        # Download in parallel
        fetcher.download_files_parallel(files, stats, max_workers=2)
        
        # Verify mixed results
        assert stats["succeeded"] == 2
        assert stats["failed"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

