"""Source Fetch Stage - Downloads required source materials.

This stage is responsible for fetching AD&D 2E and PF2E source materials
from archive.org and other sources before the pipeline begins processing.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add scripts directory to path to import fetch_adnd_sources
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

from fetch_adnd_sources import ArchiveOrgFetcher, calculate_optimal_threads

from tools.pdf_pipeline.base import BaseProcessor
from tools.pdf_pipeline.domain import (
    ExecutionContext,
    ProcessorInput,
    ProcessorOutput,
)

logger = logging.getLogger(__name__)


class SourceFetchProcessor(BaseProcessor):
    """
    FETCH-1: Processor to fetch source materials before pipeline execution.
    FETCH-2: MUST download PDF and EPUB formats when available.
    FETCH-3: MUST skip files that already exist.
    FETCH-4: MUST use parallel downloads with auto-detected thread count.
    FETCH-5: MUST extract ZIP files and create markers.
    """

    def process(
        self, input_data: ProcessorInput, context: ExecutionContext
    ) -> ProcessorOutput:
        """
        Fetch source materials from configured sources.

        Args:
            input_data: Not used for this processor (no input required)
            context: Execution context for tracking progress

        Returns:
            ProcessorOutput containing download statistics
        """
        logger.info("=" * 80)
        logger.info("Starting Source Fetch Stage")
        logger.info("=" * 80)

        # Get configuration
        sources_dir = Path(self.config.get("sources_dir", "sources"))
        archive_url = self.config.get(
            "archive_url",
            "https://archive.org/download/advanced-dungeons-dragons-2nd-edition"
        )
        max_workers = self.config.get("max_workers", None)
        
        # Auto-detect optimal threads if not specified
        if max_workers is None:
            max_workers = calculate_optimal_threads()
            logger.info(f"Auto-detected {max_workers} download threads")

        # Initialize fetcher
        sources_dir.mkdir(parents=True, exist_ok=True)
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
            context.items_processed += 1

            # Step 2: Parse download links
            logger.info("\n🔍 Step 2: Parsing download links...")
            all_files = fetcher.parse_download_links(html_content)
            logger.info(f"Found {len(all_files)} total files")

            # Step 3: Deduplicate by title
            logger.info("\n🎯 Step 3: Deduplicating by title...")
            unique_files = fetcher.deduplicate_by_title(all_files)
            logger.info(
                f"Deduplicated to {len(unique_files)} files (keeping PDF + EPUB)"
            )

            # Step 4: Filter existing files
            logger.info("\n✅ Step 4: Filtering for missing files...")
            missing_files = fetcher.filter_existing_files(unique_files)

            stats["total"] = len(missing_files)
            stats["skipped"] = len(unique_files) - len(missing_files)

            # Display summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total files found: {len(all_files)}")
            logger.info(f"Unique titles: {len(unique_files)}")
            logger.info(f"Already downloaded: {stats['skipped']}")
            logger.info(f"Files to download: {len(missing_files)}")
            logger.info("=" * 80)

            if not missing_files:
                logger.info("\n✅ All files already present in sources directory!")
                context.items_processed += len(unique_files)  # Count as processed
                return ProcessorOutput(
                    data={"statistics": stats, "files_downloaded": []},
                    metadata={
                        "total_files": len(all_files),
                        "unique_files": len(unique_files),
                        "skipped": stats["skipped"],
                    },
                )

            # Step 5: Download missing files (in parallel)
            logger.info(
                f"\n📥 Step 5: Downloading missing files (using {max_workers} threads)..."
            )
            logger.info("-" * 80)

            fetcher.download_files_parallel(missing_files, stats, max_workers=max_workers)
            context.items_processed += len(missing_files)

            # Display final statistics
            logger.info("\n" + fetcher.format_statistics(stats))

            # Check for failures
            if stats["failed"] > 0:
                logger.warning(f"\n⚠️  {stats['failed']} file(s) failed to download")
                context.warnings.append(
                    f"{stats['failed']} source files failed to download"
                )
            else:
                logger.info("\n✅ All downloads completed successfully!")

            return ProcessorOutput(
                data={
                    "statistics": stats,
                    "files_downloaded": [str(f.local_path) for f in missing_files],
                },
                metadata={
                    "total_files": len(all_files),
                    "unique_files": len(unique_files),
                    "downloaded": stats["succeeded"],
                    "failed": stats["failed"],
                    "skipped": stats["skipped"],
                    "extracted": stats["extracted"],
                },
            )

        except KeyboardInterrupt:
            logger.warning("\n\n⚠️  Download interrupted by user")
            context.warnings.append("Source fetch interrupted by user")
            return ProcessorOutput(
                data={"statistics": stats, "files_downloaded": []},
                metadata={"interrupted": True},
            )

        except Exception as e:
            logger.error(f"\n❌ Fatal error during source fetch: {e}", exc_info=True)
            context.errors.append(f"Source fetch failed: {str(e)}")
            raise


class PF2ESourceFetchProcessor(BaseProcessor):
    """
    Processor to fetch Pathfinder 2E source materials.
    
    NOTE: Currently a stub. PF2E sources are already in the repository.
    This can be enhanced later if needed to download additional PF2E resources.
    """

    def process(
        self, input_data: ProcessorInput, context: ExecutionContext
    ) -> ProcessorOutput:
        """
        Check for PF2E source materials.

        Args:
            input_data: Not used
            context: Execution context

        Returns:
            ProcessorOutput indicating PF2E sources are present
        """
        logger.info("Checking PF2E source materials...")

        sources_dir = Path(self.config.get("sources_dir", "sources"))
        required_files = self.config.get("required_files", [
            "PZO12001E.pdf",  # Player Core
            "PZO12002E.pdf",  # GM Core
            "PZO12003E_Monster_Core.pdf",  # Monster Core
            "PZO12004E.pdf",  # Player Core 2
        ])

        missing = []
        for filename in required_files:
            file_path = sources_dir / filename
            if not file_path.exists():
                missing.append(filename)
                logger.warning(f"Missing PF2E source: {filename}")
                context.warnings.append(f"Missing PF2E source: {filename}")

        if missing:
            logger.warning(
                f"⚠️  {len(missing)} PF2E source file(s) not found. "
                "Add them to sources/ directory."
            )
        else:
            logger.info(f"✅ All {len(required_files)} PF2E source files present")

        return ProcessorOutput(
            data={"required_files": required_files, "missing_files": missing},
            metadata={
                "total_required": len(required_files),
                "found": len(required_files) - len(missing),
                "missing": len(missing),
            },
        )

