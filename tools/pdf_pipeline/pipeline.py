"""Pipeline orchestration engine.

This module implements the PipelineEngine that loads configuration,
instantiates transformers and stages, and executes the complete pipeline.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

from .base import BasePostProcessor, BaseProcessor, NoOpPostProcessor
from .domain import (
    ExecutionContext,
    Pipeline,
    PipelineResult,
    PipelineSpec,
    PostProcessorSpec,
    ProcessorInput,
    ProcessorSpec,
    Transformer,
    TransformerSpec,
    TransformerStage,
    TransformerStageSpec,
)
from .loader import load_postprocessor, load_processor, REGISTRY

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PipelineEngine:
    """Main orchestration engine for the pipeline.
    
    Loads pipeline configuration, instantiates all components, and executes
    the complete transformation workflow.
    """
    
    def __init__(self, config_path: Path):
        """Initialize the pipeline engine.
        
        Args:
            config_path: Path to pipeline configuration JSON
        """
        self.config_path = config_path
        self.spec: Optional[PipelineSpec] = None
        self.pipeline: Optional[Pipeline] = None
        
    def load_config(self) -> PipelineSpec:
        """Load and parse pipeline configuration.
        
        Returns:
            Parsed PipelineSpec
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Pipeline config not found: {self.config_path}")
        
        config_data = json.loads(self.config_path.read_text(encoding="utf-8"))
        
        try:
            self.spec = PipelineSpec(**config_data)
            logger.info(f"Loaded pipeline config: {self.spec.name} v{self.spec.version}")
            return self.spec
        except Exception as e:
            raise ValueError(f"Invalid pipeline configuration: {e}")
    
    def build_pipeline(self) -> Pipeline:
        """Build the pipeline from the loaded specification.
        
        Returns:
            Configured Pipeline instance
            
        Raises:
            ValueError: If spec not loaded or building fails
        """
        if not self.spec:
            raise ValueError("Pipeline spec not loaded. Call load_config() first.")
        
        transformers: List[Transformer] = []
        
        for transformer_spec in self.spec.transformers:
            logger.info(f"Building transformer: {transformer_spec.name}")
            stages = self._build_stages(transformer_spec)
            transformer = Transformer(transformer_spec, stages)
            transformers.append(transformer)
        
        self.pipeline = Pipeline(self.spec, transformers)
        logger.info(f"Pipeline built with {len(transformers)} transformers")
        return self.pipeline
    
    def _build_stages(self, transformer_spec: TransformerSpec) -> List[TransformerStage]:
        """Build stages for a transformer.
        
        Args:
            transformer_spec: Transformer specification
            
        Returns:
            List of configured TransformerStage instances
        """
        stages: List[TransformerStage] = []
        
        for stage_spec in transformer_spec.stages:
            logger.info(f"  Building stage: {stage_spec.name}")
            
            # Load processor
            processor = self._load_processor(stage_spec.processor_spec)
            
            # Load postprocessor if specified
            postprocessor: Optional[BasePostProcessor] = None
            if stage_spec.postprocessor_spec:
                postprocessor = self._load_postprocessor(stage_spec.postprocessor_spec)
            
            stage = TransformerStage(stage_spec, processor, postprocessor)
            stages.append(stage)
        
        return stages
    
    def _load_processor(self, spec: ProcessorSpec) -> BaseProcessor:
        """Load a processor from its specification.
        
        Args:
            spec: Processor specification
            
        Returns:
            Instantiated processor
        """
        if not spec.module_path or not spec.class_name:
            raise ValueError(f"Processor spec missing module_path or class_name: {spec.name}")
        
        try:
            processor = load_processor(
                spec.module_path,
                spec.class_name,
                spec,
                registry=REGISTRY
            )
            logger.debug(f"    Loaded processor: {spec.class_name}")
            return processor
        except Exception as e:
            logger.error(f"Failed to load processor {spec.class_name}: {e}")
            raise
    
    def _load_postprocessor(self, spec: PostProcessorSpec) -> BasePostProcessor:
        """Load a postprocessor from its specification.
        
        Args:
            spec: Postprocessor specification
            
        Returns:
            Instantiated postprocessor
        """
        if not spec.module_path or not spec.class_name:
            logger.warning(f"Postprocessor spec missing module_path or class_name: {spec.name}")
            return NoOpPostProcessor(spec)
        
        try:
            postprocessor = load_postprocessor(
                spec.module_path,
                spec.class_name,
                spec,
                registry=REGISTRY
            )
            logger.debug(f"    Loaded postprocessor: {spec.class_name}")
            return postprocessor
        except Exception as e:
            logger.error(f"Failed to load postprocessor {spec.class_name}: {e}")
            raise
    
    def execute(
        self,
        start_from: Optional[str] = None,
        dry_run: bool = False,
    ) -> PipelineResult:
        """Execute the pipeline.
        
        Args:
            start_from: Name of transformer to start from (for resuming)
            dry_run: If True, validate configuration without executing
            
        Returns:
            PipelineResult containing execution results
        """
        if not self.pipeline:
            raise ValueError("Pipeline not built. Call build_pipeline() first.")
        
        if dry_run:
            logger.info("Dry run mode - validating configuration only")
            return self._dry_run_validate()
        
        logger.info(f"Starting pipeline execution: {self.spec.name}")
        start_time = time.time()
        
        # Execute pipeline with global parallel flag
        result = self.pipeline.execute(start_from=start_from, global_parallel=self.spec.parallel)
        
        elapsed_time = time.time() - start_time
        result.context.elapsed_time = elapsed_time
        
        # Log results
        if result.success:
            logger.info(f"Pipeline completed successfully in {elapsed_time:.2f}s")
        else:
            logger.error(f"Pipeline failed after {elapsed_time:.2f}s")
            for error in result.context.errors:
                logger.error(f"  Error: {error}")
        
        # Log warnings
        for warning in result.context.warnings:
            logger.warning(f"  Warning: {warning}")
        
        return result
    
    def _dry_run_validate(self) -> PipelineResult:
        """Validate pipeline configuration without executing.
        
        Returns:
            PipelineResult with validation status
        """
        context = ExecutionContext(pipeline_name=self.spec.name)
        
        # Validate all transformers and stages
        for transformer in self.pipeline.transformers:
            logger.info(f"Validating transformer: {transformer.name}")
            for stage in transformer.stages:
                logger.info(f"  Validating stage: {stage.spec.name}")
                # Check that processor is instantiated
                if not stage.processor:
                    context.errors.append(f"Stage {stage.spec.name} has no processor")
        
        success = len(context.errors) == 0
        
        if success:
            logger.info("Dry run validation passed")
        else:
            logger.error("Dry run validation failed")
            for error in context.errors:
                logger.error(f"  {error}")
        
        return PipelineResult(
            pipeline_name=self.spec.name,
            success=success,
            transformer_results=[],
            context=context,
        )
    
    def save_checkpoint(self, checkpoint_id: str, result: PipelineResult) -> Path:
        """Save a checkpoint of the pipeline execution.
        
        Args:
            checkpoint_id: Identifier for the checkpoint
            result: Pipeline result to checkpoint
            
        Returns:
            Path to the checkpoint file
        """
        if not self.spec.checkpoint_enabled:
            logger.warning("Checkpointing is disabled")
            return None
        
        checkpoint_dir = Path(self.spec.checkpoint_dir or "data/.checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"{checkpoint_id}.json"
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "pipeline_name": self.spec.name,
            "timestamp": time.time(),
            "success": result.success,
            "context": {
                "items_processed": result.context.items_processed,
                "errors": result.context.errors,
                "warnings": result.context.warnings,
            }
        }
        
        checkpoint_file.write_text(
            json.dumps(checkpoint_data, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"Checkpoint saved: {checkpoint_file}")
        return checkpoint_file
    
    @classmethod
    def from_config(cls, config_path: Path) -> PipelineEngine:
        """Create and configure a pipeline engine from a config file.
        
        Args:
            config_path: Path to pipeline configuration
            
        Returns:
            Configured PipelineEngine ready to execute
        """
        engine = cls(config_path)
        engine.load_config()
        engine.build_pipeline()
        return engine

