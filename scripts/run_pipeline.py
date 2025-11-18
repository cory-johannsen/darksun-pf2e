"""Unified CLI entry point for pipeline execution.

This script provides a command-line interface for running the complete
pipeline or individual stages.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_repo_path() -> None:
    """Add repository root to Python path."""
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Run the Dark Sun conversion pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python scripts/run_pipeline.py --config data/pipeline_config.json
  
  # Run specific stage only
  python scripts/run_pipeline.py --stage extract
  
  # Resume from specific stage
  python scripts/run_pipeline.py --from-stage transform
  
  # Dry run to validate configuration
  python scripts/run_pipeline.py --dry-run
        """
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/pipeline_config.json"),
        help="Path to pipeline configuration JSON (default: data/pipeline_config.json)",
    )
    
    parser.add_argument(
        "--stage",
        type=str,
        help="Run specific stage only (extract, transform, validate, rules_conversion, foundry_build)",
    )
    
    parser.add_argument(
        "--from-stage",
        type=str,
        help="Resume pipeline from specific stage",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without executing",
    )
    
    parser.add_argument(
        "--parallel",
        action="store_true",
        default=None,
        help="Enable parallel execution (overrides config)",
    )
    
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel execution (overrides config)",
    )
    
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers (overrides config)",
    )
    
    parser.add_argument(
        "--checkpoint",
        type=str,
        help="Save checkpoint with given ID after execution",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    return parser.parse_args()


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the pipeline.
    
    Args:
        verbose: Enable debug-level logging
    """
    import logging
    
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def run_stage_only(config_path: Path, stage_name: str, verbose: bool = False) -> int:
    """Run a specific stage only.
    
    Args:
        config_path: Path to pipeline configuration
        stage_name: Name of stage to run
        verbose: Enable verbose logging
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    from tools.pdf_pipeline.pipeline import PipelineEngine
    
    try:
        engine = PipelineEngine.from_config(config_path)
        
        # Find the transformer containing the stage
        found = False
        for transformer in engine.pipeline.transformers:
            if transformer.name == stage_name or any(
                stage.spec.name == stage_name for stage in transformer.stages
            ):
                found = True
                print(f"Running stage: {stage_name}")
                
                # Execute just this transformer
                from tools.pdf_pipeline.domain import ProcessorInput, ExecutionContext
                context = ExecutionContext(pipeline_name=engine.spec.name)
                result = transformer.transform(
                    ProcessorInput(data=None, metadata={}),
                    context
                )
                
                if result.success:
                    print(f"Stage '{stage_name}' completed successfully")
                    print(f"Items processed: {context.items_processed}")
                    return 0
                else:
                    print(f"Stage '{stage_name}' failed")
                    for error in context.errors:
                        print(f"  Error: {error}")
                    return 1
        
        if not found:
            print(f"Error: Stage '{stage_name}' not found in pipeline")
            print(f"Available stages: {[t.name for t in engine.pipeline.transformers]}")
            return 1
            
    except Exception as e:
        print(f"Error running stage: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    _add_repo_path()
    
    args = parse_args()
    setup_logging(args.verbose)
    
    # Validate config path
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        return 1
    
    # Handle stage-only execution
    if args.stage:
        return run_stage_only(args.config, args.stage, args.verbose)
    
    # Run full pipeline
    try:
        from tools.pdf_pipeline.pipeline import PipelineEngine
        
        print(f"Loading pipeline configuration: {args.config}")
        engine = PipelineEngine.from_config(args.config)
        
        # Apply CLI overrides for parallel execution
        if args.parallel:
            engine.spec.parallel = True
            print("Parallel execution ENABLED (via --parallel)")
        elif args.no_parallel:
            engine.spec.parallel = False
            print("Parallel execution DISABLED (via --no-parallel)")
        
        # Apply max_workers override to all stages if specified
        if args.max_workers is not None:
            print(f"Setting max_workers={args.max_workers} for all stages")
            for transformer_spec in engine.spec.transformers:
                for stage_spec in transformer_spec.stages:
                    if stage_spec.processor_spec.config is None:
                        stage_spec.processor_spec.config = {}
                    stage_spec.processor_spec.config["max_workers"] = args.max_workers
                    if stage_spec.postprocessor_spec and stage_spec.postprocessor_spec.config is not None:
                        stage_spec.postprocessor_spec.config["max_workers"] = args.max_workers
        
        print(f"Pipeline: {engine.spec.name} v{engine.spec.version}")
        print(f"Transformers: {len(engine.pipeline.transformers)}")
        print(f"Parallel execution: {'ENABLED' if engine.spec.parallel else 'DISABLED'}")
        
        # Execute pipeline
        result = engine.execute(
            start_from=args.from_stage,
            dry_run=args.dry_run,
        )
        
        # Save checkpoint if requested
        if args.checkpoint and not args.dry_run:
            engine.save_checkpoint(args.checkpoint, result)
        
        # Print summary
        print("\n" + "=" * 60)
        print("PIPELINE EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"Items processed: {result.context.items_processed}")
        print(f"Errors: {len(result.context.errors)}")
        print(f"Warnings: {len(result.context.warnings)}")
        
        if result.context.elapsed_time:
            print(f"Duration: {result.context.elapsed_time:.2f}s")
        
        if result.context.errors:
            print("\nErrors:")
            for error in result.context.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(result.context.errors) > 10:
                print(f"  ... and {len(result.context.errors) - 10} more")
        
        if result.context.warnings:
            print("\nWarnings:")
            for warning in result.context.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(result.context.warnings) > 10:
                print(f"  ... and {len(result.context.warnings) - 10} more")
        
        print("=" * 60)
        
        return 0 if result.success else 1
        
    except Exception as e:
        print(f"Fatal error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

