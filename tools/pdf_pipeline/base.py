"""Base classes for Processors and PostProcessors.

This module provides abstract base classes that enforce the interface contract
for all processors and postprocessors in the pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .domain import (
    ExecutionContext,
    ProcessorInput,
    ProcessorOutput,
    ProcessorSpec,
    PostProcessorSpec,
)


class BaseProcessor(ABC):
    """Abstract base class for all Processors.
    
    Processors perform one isolated unit of work, taking input data and
    producing output data according to a specification.
    
    All concrete processors must inherit from this class and implement
    the process() method.
    """
    
    def __init__(self, spec: ProcessorSpec):
        """Initialize the processor with its specification.
        
        Args:
            spec: ProcessorSpec containing configuration and metadata
        """
        self.spec = spec
        self.name = spec.name
        self.config = spec.config
    
    @abstractmethod
    def process(self, input_data: ProcessorInput, context: ExecutionContext) -> ProcessorOutput:
        """Process the input data according to the specification.
        
        This method must be implemented by all concrete processors.
        
        Args:
            input_data: Input data to process
            context: Execution context for tracking state and metrics
            
        Returns:
            ProcessorOutput containing the transformed data
            
        Raises:
            Exception: If processing fails. The exception will be caught
                      by the TransformerStage and recorded in the result.
        """
        pass
    
    def validate_input(self, input_data: ProcessorInput) -> bool:
        """Validate input data before processing.
        
        Override this method to add custom validation logic.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def validate_output(self, output_data: ProcessorOutput) -> bool:
        """Validate output data after processing.
        
        Override this method to add custom validation logic.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True


class BasePostProcessor(ABC):
    """Abstract base class for all PostProcessors.
    
    PostProcessors perform secondary processing on the output of a Processor,
    applying additional transformations, formatting, or validation.
    
    All concrete postprocessors must inherit from this class and implement
    the postprocess() method.
    """
    
    def __init__(self, spec: PostProcessorSpec):
        """Initialize the postprocessor with its specification.
        
        Args:
            spec: PostProcessorSpec containing configuration and metadata
        """
        self.spec = spec
        self.name = spec.name
        self.config = spec.config
    
    @abstractmethod
    def postprocess(self, input_data: ProcessorOutput, context: ExecutionContext) -> ProcessorOutput:
        """Post-process the data according to the specification.
        
        This method must be implemented by all concrete postprocessors.
        
        Args:
            input_data: Data to post-process (output from a Processor)
            context: Execution context for tracking state and metrics
            
        Returns:
            ProcessorOutput containing the post-processed data
            
        Raises:
            Exception: If post-processing fails. The exception will be caught
                      by the TransformerStage and recorded in the result.
        """
        pass
    
    def validate_input(self, input_data: ProcessorOutput) -> bool:
        """Validate input data before post-processing.
        
        Override this method to add custom validation logic.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def validate_output(self, output_data: ProcessorOutput) -> bool:
        """Validate output data after post-processing.
        
        Override this method to add custom validation logic.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True


class NoOpPostProcessor(BasePostProcessor):
    """A no-op postprocessor that passes data through unchanged.
    
    Useful as a default when no post-processing is needed.
    """
    
    def postprocess(self, input_data: ProcessorOutput, context: ExecutionContext) -> ProcessorOutput:
        """Pass the data through unchanged.
        
        Args:
            input_data: Data to pass through
            context: Execution context
            
        Returns:
            The same data unchanged
        """
        return input_data

