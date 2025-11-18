#!/usr/bin/env python3
"""
Fetches AD&D 2E source materials from archive.org.

FETCH-1: Script MUST fetch content from archive.org collection page.
FETCH-2: Script MUST parse HTML to extract download URLs.
FETCH-3: Script MUST prioritize PDF format, then EPUB, then ZIP.
FETCH-4: Script MUST group files by unique title to avoid duplicates.
FETCH-5: Script MUST only download files that don't already exist in sources/.
FETCH-6: Script MUST log all operations at appropriate levels.
"""

import logging
import os
import re
import sys
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def calculate_optimal_threads() -> int:
    """
    THREADS-1: Calculate optimal thread count for I/O-bound downloads.
    THREADS-2: MUST use CPU count * 3 for I/O-bound operations.
    THREADS-3: MUST have minimum of 4 threads and maximum of 32 threads.
    THREADS-4: MUST handle systems where CPU count is unavailable.
    
    Returns:
        Optimal number of download threads
    """
    try:
        cpu_count = os.cpu_count()
        if cpu_count is None:
            # Fallback if cpu_count() returns None
            logger.warning("Unable to detect CPU count, using default of 8 threads")
            return 8
        
        # For I/O-bound operations (downloads), use 3x CPU cores
        # This is optimal because threads spend most time waiting on network
        optimal = cpu_count * 3
        
        # Clamp between 4 and 32 threads
        # Min 4: Ensure reasonable parallelism on low-core systems
        # Max 32: Avoid overwhelming archive.org or local system
        optimal = max(4, min(32, optimal))
        
        logger.info(
            f"Detected {cpu_count} CPU cores, using {optimal} download threads "
            f"(3x cores for I/O-bound operations)"
        )
        
        return optimal
        
    except Exception as e:
        logger.warning(f"Error calculating optimal threads: {e}, using default of 8")
        return 8


class SourceFile(BaseModel):
    """
    MODEL-1: Represents a source file to be downloaded.
    MODEL-2: MUST include title, URL, format, and local path.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str = Field(..., description="Normalized title of the source material")
    url: HttpUrl = Field(..., description="Download URL for the file")
    format: str = Field(..., description="File format (pdf, epub, zip)")
    local_path: Path = Field(..., description="Local filesystem path for storage")
    priority: int = Field(..., description="Priority for format selection (lower is better)")


class ArchiveOrgFetcher:
    """
    FETCHER-1: Fetches and parses archive.org collection pages.
    FETCHER-2: MUST extract all downloadable items from the collection.
    """

    COLLECTION_URL = "https://archive.org/download/advanced-dungeons-dragons-2nd-edition"
    COLLECTION_BASE_URL = "https://archive.org/download/advanced-dungeons-dragons-2nd-edition"
    FORMAT_PRIORITY = {"pdf": 1, "epub": 2, "zip": 3}

    def __init__(self, sources_dir: Path):
        """
        INIT-1: Initialize fetcher with target directory.
        
        Args:
            sources_dir: Directory where source files will be stored
        """
        self.sources_dir = sources_dir
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized fetcher with sources directory: {sources_dir}")

    def fetch_collection_page(self) -> str:
        """
        FETCH-1: Fetch the HTML content of the collection page.
        
        Returns:
            HTML content as string
            
        Raises:
            requests.RequestException: If the request fails
        """
        logger.info(f"Fetching collection page: {self.COLLECTION_URL}")
        try:
            response = requests.get(self.COLLECTION_URL, timeout=30)
            response.raise_for_status()
            logger.debug(f"Successfully fetched page, size: {len(response.text)} bytes")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch collection page: {e}")
            raise

    def parse_download_links(self, html_content: str) -> List[SourceFile]:
        """
        PARSE-1: Parse HTML to extract download links.
        PARSE-2: MUST filter for PDF, EPUB, and ZIP formats only.
        PARSE-3: MUST normalize titles for grouping.
        PARSE-4: MUST construct proper archive.org download URLs.
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            List of SourceFile objects
        """
        logger.info("Parsing HTML content for download links")
        soup = BeautifulSoup(html_content, "html.parser")
        source_files = []

        # Find all links on the page
        links = soup.find_all("a", href=True)
        logger.debug(f"Found {len(links)} total links")

        for link in links:
            href = link["href"]
            
            # Check if this is a downloadable file
            if not self._is_downloadable_file(href):
                continue

            # Extract file format
            file_format = self._extract_format(href)
            if not file_format:
                continue

            # Extract and normalize title
            title = self._extract_title(href)
            if not title:
                logger.debug(f"Could not extract title from: {href}")
                continue

            # Build full URL - archive.org structure is: base_url/filename
            # The href might be absolute or relative, so handle both cases
            if href.startswith("http"):
                full_url = href
            else:
                # Remove leading slash if present
                filename = href.lstrip("/")
                # Construct proper archive.org download URL
                full_url = f"{self.COLLECTION_BASE_URL}/{filename}"
            
            # Build local path - use just the filename portion
            filename = Path(href).name
            local_path = self.sources_dir / filename

            # Create SourceFile object
            source_file = SourceFile(
                title=title,
                url=full_url,
                format=file_format,
                local_path=local_path,
                priority=self.FORMAT_PRIORITY.get(file_format, 99),
            )
            source_files.append(source_file)
            logger.debug(f"Found: {title} ({file_format}) - {full_url}")

        logger.info(f"Parsed {len(source_files)} downloadable files")
        return source_files

    def _is_downloadable_file(self, href: str) -> bool:
        """
        CHECK-1: Determine if a link points to a downloadable file.
        
        Args:
            href: URL or path to check
            
        Returns:
            True if the link is a downloadable file
        """
        # Skip directory listings, metadata, and thumbnails
        skip_patterns = [
            "__ia_thumb.jpg",
            "_meta.xml",
            "_meta.sqlite",
            "_files.xml",
            "_archive.torrent",
        ]
        
        return not any(pattern in href for pattern in skip_patterns)

    def _extract_format(self, href: str) -> Optional[str]:
        """
        EXTRACT-1: Extract file format from URL.
        EXTRACT-2: MUST return None for unsupported formats.
        
        Args:
            href: URL or path to extract format from
            
        Returns:
            File format (pdf, epub, zip) or None
        """
        href_lower = href.lower()
        
        if href_lower.endswith(".pdf"):
            return "pdf"
        elif href_lower.endswith(".epub"):
            return "epub"
        elif href_lower.endswith(".zip"):
            return "zip"
        
        return None

    def _extract_title(self, href: str) -> Optional[str]:
        """
        EXTRACT-2: Extract and normalize title from URL.
        EXTRACT-3: MUST remove file extensions and archive.org artifacts.
        
        Args:
            href: URL or path to extract title from
            
        Returns:
            Normalized title or None
        """
        # Get filename without path
        filename = Path(href).stem
        
        # Remove common archive.org suffixes
        suffixes_to_remove = ["_djvu", "_text", "_jp2", "_abbyy"]
        for suffix in suffixes_to_remove:
            if filename.endswith(suffix):
                filename = filename[: -len(suffix)]
        
        # Replace underscores and hyphens with spaces
        title = filename.replace("_", " ").replace("-", " ")
        
        # Clean up multiple spaces
        title = re.sub(r"\s+", " ", title).strip()
        
        # Basic validation
        if len(title) < 3:
            return None
        
        return title

    def deduplicate_by_title(self, source_files: List[SourceFile]) -> List[SourceFile]:
        """
        DEDUP-1: Deduplicate files by title, keeping both PDF and EPUB when available.
        DEDUP-2: MUST keep both PDF and EPUB formats for comparison.
        DEDUP-3: MUST skip ZIP if PDF or EPUB exists for that title.
        
        Args:
            source_files: List of source files to deduplicate
            
        Returns:
            Deduplicated list with PDF and EPUB for each title
        """
        logger.info("Deduplicating files by title - keeping both PDF and EPUB")
        
        # Group by title, tracking available formats
        title_formats = {}
        for source_file in source_files:
            title = source_file.title
            
            if title not in title_formats:
                title_formats[title] = {}
            
            # Store by format within each title
            format_type = source_file.format
            if format_type not in title_formats[title]:
                title_formats[title][format_type] = source_file
                logger.debug(f"Added {format_type.upper()} for: {title}")
        
        # Build final list: keep PDF and EPUB, skip ZIP if either exists
        deduplicated = []
        for title, formats in title_formats.items():
            # Always include PDF if available
            if "pdf" in formats:
                deduplicated.append(formats["pdf"])
            
            # Always include EPUB if available
            if "epub" in formats:
                deduplicated.append(formats["epub"])
            
            # Only include ZIP if neither PDF nor EPUB exists
            if "zip" in formats and "pdf" not in formats and "epub" not in formats:
                deduplicated.append(formats["zip"])
                logger.debug(f"Including ZIP (no PDF/EPUB available) for: {title}")

        logger.info(
            f"Deduplicated from {len(source_files)} to {len(deduplicated)} files "
            f"(keeping both PDF and EPUB when available)"
        )
        
        return deduplicated

    def get_extraction_marker_path(self, zip_path: Path) -> Path:
        """
        MARKER-1: Get path to extraction marker file for a ZIP.
        MARKER-2: MUST use .extracted suffix.
        
        Args:
            zip_path: Path to ZIP file
            
        Returns:
            Path to marker file
        """
        return zip_path.parent / f"{zip_path.name}.extracted"

    def filter_existing_files(self, source_files: List[SourceFile]) -> List[SourceFile]:
        """
        FILTER-1: Filter out files that already exist in sources directory.
        FILTER-2: MUST check actual filesystem presence.
        FILTER-3: MUST check for extraction markers for ZIP files.
        
        Args:
            source_files: List of source files to filter
            
        Returns:
            Filtered list containing only missing files
        """
        logger.info("Filtering for files that don't already exist")
        
        missing_files = []
        for source_file in source_files:
            # Check if file exists
            if source_file.local_path.exists():
                logger.debug(f"File already exists: {source_file.local_path.name}")
                continue
            
            # For ZIP files, also check if extraction marker exists
            if source_file.format == "zip":
                marker_path = self.get_extraction_marker_path(source_file.local_path)
                if marker_path.exists():
                    logger.debug(
                        f"ZIP already extracted (marker exists): {source_file.local_path.name}"
                    )
                    continue
            
            # File is missing
            missing_files.append(source_file)
            logger.debug(f"File missing: {source_file.local_path.name}")
        
        logger.info(
            f"Found {len(missing_files)} missing files out of {len(source_files)} total"
        )
        return missing_files

    def download_file(self, source_file: SourceFile, show_progress: bool = True) -> bool:
        """
        DOWNLOAD-1: Download a single file to the sources directory.
        DOWNLOAD-2: MUST skip if file already exists.
        DOWNLOAD-3: MUST show progress bar during download.
        DOWNLOAD-4: MUST extract ZIP files after download.
        
        Args:
            source_file: File to download
            show_progress: Whether to show progress bar (default: True)
            
        Returns:
            True if download succeeded, False otherwise
        """
        logger.info(f"Downloading {source_file.title} from {source_file.url}")
        
        try:
            # Make request with streaming
            response = requests.get(str(source_file.url), stream=True, timeout=60)
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get("content-length", 0))
            
            # Download with progress bar
            with open(source_file.local_path, "wb") as f:
                if show_progress and total_size > 0:
                    with tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=source_file.local_path.name,
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # No progress bar
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            logger.info(f"Successfully downloaded to {source_file.local_path}")
            
            # If it's a ZIP file, extract it
            if source_file.format == "zip":
                logger.info(f"Extracting ZIP file: {source_file.local_path}")
                if self.extract_zip_file(source_file.local_path):
                    logger.info(f"Successfully extracted and removed ZIP: {source_file.local_path}")
                else:
                    logger.warning(f"Failed to extract ZIP: {source_file.local_path}")
            
            return True
            
        except requests.HTTPError as e:
            logger.error(f"HTTP error downloading {source_file.url}: {e}")
            # Clean up partial download
            if source_file.local_path.exists():
                source_file.local_path.unlink()
            return False
            
        except requests.RequestException as e:
            logger.error(f"Network error downloading {source_file.url}: {e}")
            # Clean up partial download
            if source_file.local_path.exists():
                source_file.local_path.unlink()
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error downloading {source_file.url}: {e}", exc_info=True)
            # Clean up partial download
            if source_file.local_path.exists():
                source_file.local_path.unlink()
            return False

    def extract_zip_file(self, zip_path: Path) -> bool:
        """
        EXTRACT-1: Extract ZIP file to the same directory.
        EXTRACT-2: MUST delete ZIP file after successful extraction.
        EXTRACT-3: MUST handle corrupt ZIP files gracefully.
        EXTRACT-4: MUST create marker file to prevent re-downloading.
        
        Args:
            zip_path: Path to ZIP file to extract
            
        Returns:
            True if extraction succeeded, False otherwise
        """
        if not zip_path.exists():
            logger.warning(f"ZIP file does not exist: {zip_path}")
            return False
        
        try:
            # Extract to parent directory
            extract_dir = zip_path.parent
            
            with zipfile.ZipFile(zip_path, "r") as zf:
                # Validate ZIP file
                bad_file = zf.testzip()
                if bad_file:
                    logger.error(f"Corrupt file in ZIP: {bad_file}")
                    return False
                
                # Extract all files
                zf.extractall(extract_dir)
                logger.debug(f"Extracted {len(zf.namelist())} files from {zip_path.name}")
            
            # Create marker file to indicate extraction completed
            marker_path = self.get_extraction_marker_path(zip_path)
            marker_path.write_text(f"Extracted on: {zip_path.stat().st_mtime}\n")
            logger.debug(f"Created extraction marker: {marker_path.name}")
            
            # Delete the ZIP file after successful extraction
            zip_path.unlink()
            logger.debug(f"Deleted ZIP file: {zip_path}")
            
            return True
            
        except zipfile.BadZipFile as e:
            logger.error(f"Invalid ZIP file {zip_path}: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Error extracting {zip_path}: {e}", exc_info=True)
            return False

    def download_files_parallel(
        self,
        source_files: List[SourceFile],
        stats: Dict[str, int],
        max_workers: int = 8,
    ) -> None:
        """
        PARALLEL-1: Download files in parallel using ThreadPoolExecutor.
        PARALLEL-2: MUST use thread-safe statistics tracking.
        PARALLEL-3: MUST handle progress bars for concurrent downloads.
        PARALLEL-4: MUST respect max_workers limit.
        
        Args:
            source_files: List of files to download
            stats: Statistics dictionary (will be updated thread-safely)
            max_workers: Maximum number of concurrent downloads
        """
        # Thread-safe lock for updating statistics
        stats_lock = threading.Lock()
        
        def download_with_stats(source_file: SourceFile, position: int) -> bool:
            """Download a single file and update stats."""
            logger.info(f"Starting download: {source_file.title}")
            
            success = self.download_file(source_file, show_progress=True)
            
            # Thread-safe statistics update
            with stats_lock:
                if success:
                    stats["succeeded"] += 1
                    if source_file.format == "zip":
                        stats["extracted"] += 1
                else:
                    stats["failed"] += 1
            
            return success
        
        logger.info(f"Starting parallel downloads with {max_workers} workers...")
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_file = {
                executor.submit(download_with_stats, source_file, i): source_file
                for i, source_file in enumerate(source_files)
            }
            
            # Process completed downloads
            completed = 0
            for future in as_completed(future_to_file):
                completed += 1
                source_file = future_to_file[future]
                
                try:
                    success = future.result()
                    status = "✅" if success else "❌"
                    logger.info(
                        f"[{completed}/{len(source_files)}] {status} {source_file.title}"
                    )
                except Exception as e:
                    logger.error(f"Exception downloading {source_file.title}: {e}")
                    with stats_lock:
                        stats["failed"] += 1

    def format_statistics(self, stats: Dict[str, int]) -> str:
        """
        STATS-1: Format download statistics as a human-readable string.
        
        Args:
            stats: Dictionary of statistics
            
        Returns:
            Formatted statistics string
        """
        lines = [
            "=" * 80,
            "📊 DOWNLOAD STATISTICS",
            "=" * 80,
            f"Total files: {stats.get('total', 0)}",
            f"✅ Succeeded: {stats.get('succeeded', 0)}",
            f"❌ Failed: {stats.get('failed', 0)}",
            f"⏭️  Skipped: {stats.get('skipped', 0)}",
            f"📦 ZIP files extracted: {stats.get('extracted', 0)}",
            "=" * 80,
        ]
        return "\n".join(lines)


def main(dry_run: bool = False, max_workers: int = None):
    """
    MAIN-1: Main entry point for the script.
    MAIN-2: MUST fetch, parse, deduplicate, and download files.
    MAIN-3: MUST track and display download statistics.
    MAIN-4: MUST support parallel downloads with configurable worker count.
    MAIN-5: MUST auto-detect optimal thread count if not specified.
    
    Args:
        dry_run: If True, only show what would be downloaded without downloading
        max_workers: Maximum number of concurrent downloads (default: auto-detect based on CPU cores)
    """
    # Auto-detect optimal threads if not specified
    if max_workers is None:
        max_workers = calculate_optimal_threads()
    logger.info("=" * 80)
    logger.info("AD&D 2E Source Material Fetcher")
    logger.info("=" * 80)
    
    # Initialize fetcher
    sources_dir = Path(__file__).parent.parent / "sources"
    fetcher = ArchiveOrgFetcher(sources_dir)
    
    # Initialize statistics
    stats = {
        "total": 0,
        "succeeded": 0,
        "failed": 0,
        "skipped": 0,
        "extracted": 0,
    }
    
    try:
        # Step 1: Fetch collection page
        logger.info("\n📥 Step 1: Fetching collection page...")
        html_content = fetcher.fetch_collection_page()
        
        # Step 2: Parse download links
        logger.info("\n🔍 Step 2: Parsing download links...")
        all_files = fetcher.parse_download_links(html_content)
        
        # Step 3: Deduplicate by title
        logger.info("\n🎯 Step 3: Deduplicating by title...")
        unique_files = fetcher.deduplicate_by_title(all_files)
        
        # Step 4: Filter existing files
        logger.info("\n✅ Step 4: Filtering for missing files...")
        missing_files = fetcher.filter_existing_files(unique_files)
        
        stats["total"] = len(missing_files)
        stats["skipped"] = len(unique_files) - len(missing_files)
        
        # Step 5: Display summary
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total files found: {len(all_files)}")
        logger.info(f"Unique titles: {len(unique_files)}")
        logger.info(f"Already downloaded: {stats['skipped']}")
        logger.info(f"Files to download: {len(missing_files)}")
        logger.info("=" * 80)
        
        if dry_run:
            logger.info("\n🔍 DRY RUN MODE - Files that would be downloaded:")
            logger.info("-" * 80)
            for i, source_file in enumerate(missing_files, 1):
                logger.info(
                    f"{i:3d}. [{source_file.format.upper():4s}] {source_file.title}"
                )
                logger.info(f"      URL: {source_file.url}")
                logger.info("")
            return
        
        if not missing_files:
            logger.info("\n✅ All files already present in sources directory!")
            return
        
        # Step 6: Download missing files (in parallel)
        logger.info(f"\n📥 Step 5: Downloading missing files (using {max_workers} threads)...")
        logger.info("-" * 80)
        
        fetcher.download_files_parallel(missing_files, stats, max_workers=max_workers)
        
        # Step 7: Display final statistics
        logger.info("\n" + fetcher.format_statistics(stats))
        
        # Exit with error if any downloads failed
        if stats["failed"] > 0:
            logger.warning(f"\n⚠️  {stats['failed']} file(s) failed to download")
            sys.exit(1)
        else:
            logger.info("\n✅ All downloads completed successfully!")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Download interrupted by user")
        logger.info("\n" + fetcher.format_statistics(stats))
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        logger.info("\n" + fetcher.format_statistics(stats))
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    # Calculate optimal threads before parsing args so we can show it in help
    default_threads = calculate_optimal_threads()
    
    parser = argparse.ArgumentParser(
        description="Fetch AD&D 2E source materials from archive.org"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=default_threads,
        help=f"Number of parallel download threads (default: {default_threads}, auto-detected based on CPU cores)",
    )
    
    args = parser.parse_args()
    main(dry_run=args.dry_run, max_workers=args.threads)

