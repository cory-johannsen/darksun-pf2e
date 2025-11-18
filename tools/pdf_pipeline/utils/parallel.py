"""Parallel execution utilities for the PDF pipeline.

Provides process-based parallelism for CPU-bound tasks with proper error handling,
aggregation, and MacOS-safe spawn context.
"""

from __future__ import annotations

import logging
import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any, Callable, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)


def run_process_pool(
    tasks: Iterable[Any],
    worker: Callable[[Any], Dict[str, Any]],
    max_workers: Optional[int] = None,
    chunksize: int = 1,
    desc: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute tasks in parallel using a process pool.
    
    Args:
        tasks: Iterable of task arguments to pass to worker
        worker: Worker function that takes a task and returns a result dict with:
            - items: int (number of items processed)
            - warnings: List[str] (warnings encountered)
            - errors: List[str] (errors encountered)
            - Any other data to collect
        max_workers: Maximum number of worker processes (default: min(4, cpu_count))
        chunksize: Number of tasks to batch per worker (default: 1)
        desc: Optional description for logging
        
    Returns:
        Aggregated result dict with:
            - items_processed: Total items processed
            - warnings: List of all warnings
            - errors: List of all errors
            - results: List of all worker results
            - success: True if no errors occurred
    """
    if max_workers is None:
        max_workers = min(4, os.cpu_count() or 1)
    
    # Convert tasks to list to get count
    task_list = list(tasks)
    if not task_list:
        return {
            "items_processed": 0,
            "warnings": [],
            "errors": [],
            "results": [],
            "success": True,
        }
    
    desc_str = f" ({desc})" if desc else ""
    logger.info(f"Starting parallel execution with {max_workers} workers, {len(task_list)} tasks{desc_str}")
    
    # Aggregate results
    items_processed = 0
    warnings: List[str] = []
    errors: List[str] = []
    results: List[Dict[str, Any]] = []
    
    # Use spawn context for MacOS safety
    ctx = mp.get_context("spawn")
    
    try:
        with ProcessPoolExecutor(max_workers=max_workers, mp_context=ctx) as executor:
            # Submit all tasks and track futures
            futures = {executor.submit(worker, task): task for task in task_list}
            
            # Process completed tasks as they finish
            completed = 0
            for future in as_completed(futures):
                completed += 1
                try:
                    result = future.result()
                    
                    # Aggregate counts
                    items_processed += result.get("items", 0)
                    
                    # Collect warnings and errors
                    if "warnings" in result:
                        warnings.extend(result["warnings"])
                    if "errors" in result:
                        errors.extend(result["errors"])
                    
                    # Store full result
                    results.append(result)
                    
                    # Log progress
                    if completed % max(1, len(task_list) // 10) == 0:
                        logger.debug(f"Progress: {completed}/{len(task_list)} tasks completed")
                
                except Exception as e:
                    # Worker raised an exception
                    task = futures[future]
                    error_msg = f"Worker failed on task {task}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    results.append({
                        "items": 0,
                        "warnings": [],
                        "errors": [error_msg],
                        "success": False,
                    })
    
    except Exception as e:
        # Pool execution failed
        error_msg = f"Process pool execution failed: {e}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    success = len(errors) == 0
    logger.info(f"Parallel execution completed: {items_processed} items, {len(errors)} errors, {len(warnings)} warnings")
    
    return {
        "items_processed": items_processed,
        "warnings": warnings,
        "errors": errors,
        "results": results,
        "success": success,
    }


def get_max_workers(config: Dict[str, Any], default: int = 4) -> int:
    """Get max_workers from config with sensible default.
    
    Args:
        config: Configuration dict
        default: Default value if not specified
        
    Returns:
        Number of workers to use
    """
    max_workers = config.get("max_workers")
    if max_workers is None:
        max_workers = min(default, os.cpu_count() or 1)
    return max(1, int(max_workers))


def should_parallelize(config: Dict[str, Any], global_parallel: bool = False) -> bool:
    """Determine if parallelization should be enabled for a stage.
    
    Args:
        config: Stage configuration dict
        global_parallel: Global parallel flag from pipeline config
        
    Returns:
        True if parallel execution should be used
    """
    # Stage-level config takes precedence
    if "parallel" in config:
        return bool(config["parallel"])
    
    # Fall back to global config
    return global_parallel

