"""Domain models for the PDF processing pipeline.

This module implements the complete domain model from SPEC.md, providing
a formal class hierarchy for Pipeline → Transformer → TransformerStage → Processor/PostProcessor.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)


# ============================================================================
# I/O Type Definitions
# ============================================================================

class ProcessorInput(BaseModel):
    """Generic input data for a Processor.
    
    Can contain any data structure depending on the processor's requirements.
    """
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class ProcessorOutput(BaseModel):
    """Generic output data from a Processor.
    
    Can contain any data structure produced by the processor.
    """
    data: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


# TransformerInput and TransformerOutput are aliases for stage I/O
TransformerInput = ProcessorInput
TransformerOutput = ProcessorOutput


# ============================================================================
# Specification Models (Pydantic)
# ============================================================================

class ProcessorSpec(BaseModel):
    """Base specification for a Processor.
    
    Contains metadata, rules, and configuration necessary to execute
    the transformation.
    """
    name: str
    description: Optional[str] = None
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution hints
    timeout: Optional[int] = None  # seconds
    retry_count: int = 0
    
    model_config = ConfigDict(extra="allow")


class PostProcessorSpec(BaseModel):
    """Base specification for a PostProcessor.
    
    Contains metadata and rules for secondary post-processing.
    """
    name: str
    description: Optional[str] = None
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    
    # Execution hints
    timeout: Optional[int] = None  # seconds
    
    model_config = ConfigDict(extra="allow")


class TransformerStageSpec(BaseModel):
    """Specification for a single TransformerStage.
    
    Bundles processor and postprocessor specifications.
    """
    name: str
    description: Optional[str] = None
    processor_spec: ProcessorSpec
    postprocessor_spec: Optional[PostProcessorSpec] = None
    
    # Input/output configuration
    input_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    
    model_config = ConfigDict(extra="allow")


class TransformerSpec(BaseModel):
    """Specification for a Transformer.
    
    Defines input/output types and the sequence of stages.
    """
    name: str
    description: Optional[str] = None
    stages: List[TransformerStageSpec]
    
    # Type hints for the transformer
    input_type: Optional[str] = None
    output_type: Optional[str] = None
    
    model_config = ConfigDict(extra="allow")


class PipelineSpec(BaseModel):
    """Top-level pipeline configuration.
    
    Defines the complete sequence of transformers and global settings.
    """
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    
    # Global paths
    workspace_root: Path = Field(default=Path("."))
    
    # Transformer specifications
    transformers: List[TransformerSpec]
    
    # Global settings
    parallel: bool = False
    fail_fast: bool = True
    checkpoint_enabled: bool = True
    checkpoint_dir: Optional[Path] = None
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Execution Context
# ============================================================================

class ExecutionContext(BaseModel):
    """Context information passed through the pipeline execution.
    
    Tracks state, metrics, and metadata as data flows through stages.
    """
    pipeline_name: str
    transformer_name: Optional[str] = None
    stage_name: Optional[str] = None
    
    # Execution state
    start_time: Optional[float] = None
    elapsed_time: Optional[float] = None
    
    # Metrics
    items_processed: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Checkpoint information
    checkpoint_id: Optional[str] = None
    
    # Custom metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(extra="allow")


# ============================================================================
# Result Models
# ============================================================================

class StageResult(BaseModel):
    """Result from executing a TransformerStage."""
    stage_name: str
    success: bool
    output: Optional[ProcessorOutput] = None
    error: Optional[str] = None
    context: ExecutionContext
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class TransformerResult(BaseModel):
    """Result from executing a Transformer."""
    transformer_name: str
    success: bool
    stage_results: List[StageResult]
    context: ExecutionContext
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class PipelineResult(BaseModel):
    """Result from executing the complete Pipeline."""
    pipeline_name: str
    success: bool
    transformer_results: List[TransformerResult]
    context: ExecutionContext
    
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


# ============================================================================
# Abstract Execution Interfaces
# ============================================================================

class Processor(ABC):
    """Abstract base class for all Processors.
    
    Processors perform isolated units of work, transforming input to output
    according to a specification.
    """
    
    def __init__(self, spec: ProcessorSpec):
        self.spec = spec
    
    @abstractmethod
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Process the input data according to the specification.
        
        Args:
            input_data: Input data to process
            context: Execution context for tracking state
            
        Returns:
            Processed output data
            
        Raises:
            Exception: If processing fails
        """
        pass


class PostProcessor(ABC):
    """Abstract base class for all PostProcessors.
    
    PostProcessors perform secondary processing on the output of a Processor.
    """
    
    def __init__(self, spec: PostProcessorSpec):
        self.spec = spec
    
    @abstractmethod
    def postprocess(self, input_data: ProcessorOutput, context: ExecutionContext) -> ProcessorOutput:
        """Post-process the data according to the specification.
        
        Args:
            input_data: Data to post-process (output from a Processor)
            context: Execution context for tracking state
            
        Returns:
            Post-processed output data
            
        Raises:
            Exception: If post-processing fails
        """
        pass


# ============================================================================
# Execution Classes
# ============================================================================

class TransformerStage:
    """Bundles a processor, postprocessor, and specifications.
    
    Executes the Transform() operation for one stage of a transformer.
    """
    
    def __init__(
        self,
        spec: TransformerStageSpec,
        processor: Processor,
        postprocessor: Optional[PostProcessor] = None,
    ):
        self.spec = spec
        self.processor = processor
        self.postprocessor = postprocessor
    
    def transform(self, input_data: TransformerInput, context: ExecutionContext) -> StageResult:
        """Execute the transformation stage.
        
        Args:
            input_data: Input data for the stage
            context: Execution context
            
        Returns:
            StageResult containing the output or error
        """
        context.stage_name = self.spec.name
        
        try:
            # Execute processor
            output = self.processor.process(input_data, context)
            
            # Execute postprocessor if present
            if self.postprocessor:
                output = self.postprocessor.postprocess(output, context)
            
            return StageResult(
                stage_name=self.spec.name,
                success=True,
                output=output,
                error=None,
                context=context,
            )
        except Exception as e:
            context.errors.append(str(e))
            return StageResult(
                stage_name=self.spec.name,
                success=False,
                output=None,
                error=str(e),
                context=context,
            )


class Transformer:
    """Contains a name, description, and list of TransformerStages.
    
    Orchestrates the execution of multiple stages in sequence.
    """
    
    def __init__(
        self,
        spec: TransformerSpec,
        stages: List[TransformerStage],
    ):
        self.spec = spec
        self.name = spec.name
        self.description = spec.description
        self.stages = stages
    
    def transform(self, input_data: TransformerInput, context: ExecutionContext) -> TransformerResult:
        """Execute all stages of the transformer in sequence.
        
        Args:
            input_data: Initial input data
            context: Execution context
            
        Returns:
            TransformerResult containing results from all stages
        """
        context.transformer_name = self.name
        stage_results: List[StageResult] = []
        current_input = input_data
        
        total_stages = len(self.stages)
        logger.info(f"Transformer '{self.name}' starting ({total_stages} stages)")
        
        for stage_num, stage in enumerate(self.stages, 1):
            logger.info(f"  Stage {stage_num}/{total_stages}: {stage.spec.name}")
            result = stage.transform(current_input, context)
            stage_results.append(result)
            
            if not result.success:
                # Stage failed
                logger.error(f"  Stage {stage_num}/{total_stages}: {stage.spec.name} FAILED")
                return TransformerResult(
                    transformer_name=self.name,
                    success=False,
                    stage_results=stage_results,
                    context=context,
                )
            
            # Log completion with item count if available
            items_msg = f" ({result.context.items_processed} items)" if result.context.items_processed > 0 else ""
            logger.info(f"  Stage {stage_num}/{total_stages}: {stage.spec.name} completed{items_msg}")
            
            # Pass output to next stage
            if result.output:
                current_input = TransformerInput(
                    data=result.output.data,
                    metadata=result.output.metadata,
                )
        
        logger.info(f"Transformer '{self.name}' completed successfully")
        return TransformerResult(
            transformer_name=self.name,
            success=True,
            stage_results=stage_results,
            context=context,
        )


class Pipeline:
    """Orchestrates transformer execution in sequence.
    
    The top-level pipeline controller that manages the complete transformation workflow.
    """
    
    def __init__(
        self,
        spec: PipelineSpec,
        transformers: List[Transformer],
    ):
        self.spec = spec
        self.name = spec.name
        self.description = spec.description
        self.transformers = transformers
    
    def execute(
        self,
        initial_input: Optional[TransformerInput] = None,
        start_from: Optional[str] = None,
        global_parallel: bool = False,
    ) -> PipelineResult:
        """Execute the complete pipeline.
        
        Args:
            initial_input: Initial input data (optional, may be loaded from config)
            start_from: Name of transformer to start from (for resuming)
            global_parallel: Global parallel execution flag
            
        Returns:
            PipelineResult containing results from all transformers
        """
        context = ExecutionContext(pipeline_name=self.name)
        context.metadata["parallel"] = global_parallel
        transformer_results: List[TransformerResult] = []
        
        # Determine starting point
        start_index = 0
        if start_from:
            for i, transformer in enumerate(self.transformers):
                if transformer.name == start_from:
                    start_index = i
                    break
        
        # Execute transformers in sequence
        current_input = initial_input or TransformerInput(data=None, metadata={})
        
        total_transformers = len(self.transformers) - start_index
        logger.info(f"Pipeline '{self.name}' starting ({total_transformers} transformers)")
        
        for trans_num, transformer in enumerate(self.transformers[start_index:], 1):
            logger.info(f"\nRunning transformer {trans_num}/{total_transformers}: {transformer.name}")
            result = transformer.transform(current_input, context)
            transformer_results.append(result)
            
            if not result.success and self.spec.fail_fast:
                # Transformer failed and fail_fast is enabled
                logger.error(f"Transformer {trans_num}/{total_transformers}: {transformer.name} FAILED (fail_fast enabled)")
                return PipelineResult(
                    pipeline_name=self.name,
                    success=False,
                    transformer_results=transformer_results,
                    context=context,
                )
            
            # Pass output to next transformer
            # For now, we don't chain transformer outputs automatically
            # This will be handled by the PipelineEngine
        
        all_success = all(r.success for r in transformer_results)
        status = "successfully" if all_success else "with errors"
        logger.info(f"\nPipeline '{self.name}' completed {status}")
        
        return PipelineResult(
            pipeline_name=self.name,
            success=all_success,
            transformer_results=transformer_results,
            context=context,
        )

