"""Dynamic module loader for processors and postprocessors.

This module provides utilities for dynamically loading processor and postprocessor
classes from module paths, supporting the loading of chapter-specific processing
files like chapter_#_processing.py.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Optional, Type

from .base import BasePostProcessor, BaseProcessor
from .domain import PostProcessorSpec, ProcessorSpec


class ProcessorRegistry:
    """Registry for dynamically loaded processors and postprocessors.
    
    Maintains a cache of loaded classes to avoid redundant imports.
    """
    
    def __init__(self):
        self._processors: Dict[str, Type[BaseProcessor]] = {}
        self._postprocessors: Dict[str, Type[BasePostProcessor]] = {}
    
    def register_processor(self, name: str, processor_class: Type[BaseProcessor]) -> None:
        """Register a processor class.
        
        Args:
            name: Unique name for the processor
            processor_class: Processor class to register
        """
        self._processors[name] = processor_class
    
    def register_postprocessor(self, name: str, postprocessor_class: Type[BasePostProcessor]) -> None:
        """Register a postprocessor class.
        
        Args:
            name: Unique name for the postprocessor
            postprocessor_class: Postprocessor class to register
        """
        self._postprocessors[name] = postprocessor_class
    
    def get_processor(self, name: str) -> Optional[Type[BaseProcessor]]:
        """Retrieve a registered processor class.
        
        Args:
            name: Name of the processor
            
        Returns:
            Processor class or None if not found
        """
        return self._processors.get(name)
    
    def get_postprocessor(self, name: str) -> Optional[Type[BasePostProcessor]]:
        """Retrieve a registered postprocessor class.
        
        Args:
            name: Name of the postprocessor
            
        Returns:
            Postprocessor class or None if not found
        """
        return self._postprocessors.get(name)
    
    def list_processors(self) -> list[str]:
        """List all registered processor names.
        
        Returns:
            List of processor names
        """
        return list(self._processors.keys())
    
    def list_postprocessors(self) -> list[str]:
        """List all registered postprocessor names.
        
        Returns:
            List of postprocessor names
        """
        return list(self._postprocessors.keys())


# Global registry instance
REGISTRY = ProcessorRegistry()


def load_module_from_path(module_path: str, module_name: Optional[str] = None) -> any:
    """Load a Python module from a file path.
    
    Args:
        module_path: Path to the Python file (can be relative or absolute)
        module_name: Optional name for the module (generated if not provided)
        
    Returns:
        The loaded module
        
    Raises:
        ImportError: If the module cannot be loaded
        FileNotFoundError: If the module file does not exist
    """
    path = Path(module_path)
    
    if not path.is_absolute():
        # Try to resolve relative to the current working directory
        path = Path.cwd() / path
        if not path.exists():
            # Try relative to the tools/pdf_pipeline directory
            pipeline_dir = Path(__file__).parent
            path = pipeline_dir / module_path
    
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    # Generate module name if not provided
    if module_name is None:
        module_name = path.stem
    
    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module


def load_module_from_dotted_path(dotted_path: str) -> any:
    """Load a Python module from a dotted path (e.g., 'tools.pdf_pipeline.extract').
    
    Args:
        dotted_path: Dotted module path
        
    Returns:
        The loaded module
        
    Raises:
        ImportError: If the module cannot be loaded
    """
    return importlib.import_module(dotted_path)


def load_processor(
    module_path: str,
    class_name: str,
    spec: ProcessorSpec,
    registry: Optional[ProcessorRegistry] = None,
) -> BaseProcessor:
    """Load a processor class and instantiate it with a specification.
    
    Supports both file paths (e.g., 'chapter_3_processing.py') and dotted paths
    (e.g., 'tools.pdf_pipeline.stages.extract').
    
    Args:
        module_path: Path to the module (file path or dotted path)
        class_name: Name of the processor class in the module
        spec: ProcessorSpec to pass to the processor constructor
        registry: Optional registry to cache the loaded class
        
    Returns:
        Instantiated processor
        
    Raises:
        ImportError: If the module cannot be loaded
        AttributeError: If the class is not found in the module
        TypeError: If the class is not a subclass of BaseProcessor
    """
    # Determine if this is a dotted path or file path
    if '/' in module_path or module_path.endswith('.py'):
        # File path
        module = load_module_from_path(module_path)
    else:
        # Dotted path
        module = load_module_from_dotted_path(module_path)
    
    # Get the class from the module
    if not hasattr(module, class_name):
        raise AttributeError(f"Module {module_path} does not have class {class_name}")
    
    processor_class = getattr(module, class_name)
    
    # Verify it's a processor
    if not issubclass(processor_class, BaseProcessor):
        raise TypeError(f"Class {class_name} is not a subclass of BaseProcessor")
    
    # Register if registry provided
    if registry:
        registry.register_processor(spec.name, processor_class)
    
    # Instantiate and return
    return processor_class(spec)


def load_postprocessor(
    module_path: str,
    class_name: str,
    spec: PostProcessorSpec,
    registry: Optional[ProcessorRegistry] = None,
) -> BasePostProcessor:
    """Load a postprocessor class and instantiate it with a specification.
    
    Supports both file paths (e.g., 'chapter_3_processing.py') and dotted paths
    (e.g., 'tools.pdf_pipeline.stages.extract').
    
    Args:
        module_path: Path to the module (file path or dotted path)
        class_name: Name of the postprocessor class in the module
        spec: PostProcessorSpec to pass to the postprocessor constructor
        registry: Optional registry to cache the loaded class
        
    Returns:
        Instantiated postprocessor
        
    Raises:
        ImportError: If the module cannot be loaded
        AttributeError: If the class is not found in the module
        TypeError: If the class is not a subclass of BasePostProcessor
    """
    # Determine if this is a dotted path or file path
    if '/' in module_path or module_path.endswith('.py'):
        # File path
        module = load_module_from_path(module_path)
    else:
        # Dotted path
        module = load_module_from_dotted_path(module_path)
    
    # Get the class from the module
    if not hasattr(module, class_name):
        raise AttributeError(f"Module {module_path} does not have class {class_name}")
    
    postprocessor_class = getattr(module, class_name)
    
    # Verify it's a postprocessor
    if not issubclass(postprocessor_class, BasePostProcessor):
        raise TypeError(f"Class {class_name} is not a subclass of BasePostProcessor")
    
    # Register if registry provided
    if registry:
        registry.register_postprocessor(spec.name, postprocessor_class)
    
    # Instantiate and return
    return postprocessor_class(spec)


def auto_discover_processors(
    search_dir: Path,
    pattern: str = "chapter_*_processing.py",
    registry: Optional[ProcessorRegistry] = None,
) -> Dict[str, Type[BaseProcessor]]:
    """Auto-discover processor classes in a directory.
    
    Scans a directory for files matching a pattern and imports all BaseProcessor
    subclasses found in them.
    
    Args:
        search_dir: Directory to search
        pattern: Glob pattern for files to search
        registry: Optional registry to cache discovered classes
        
    Returns:
        Dict mapping processor names to classes
    """
    discovered = {}
    
    for file_path in search_dir.glob(pattern):
        try:
            module = load_module_from_path(str(file_path))
            
            # Find all BaseProcessor subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, BaseProcessor) and
                    attr is not BaseProcessor
                ):
                    discovered[attr_name] = attr
                    if registry:
                        registry.register_processor(attr_name, attr)
        except Exception as e:
            # Log error but continue discovery
            print(f"Warning: Failed to load {file_path}: {e}")
    
    return discovered


def auto_discover_postprocessors(
    search_dir: Path,
    pattern: str = "chapter_*_postprocessing.py",
    registry: Optional[ProcessorRegistry] = None,
) -> Dict[str, Type[BasePostProcessor]]:
    """Auto-discover postprocessor classes in a directory.
    
    Scans a directory for files matching a pattern and imports all BasePostProcessor
    subclasses found in them.
    
    Args:
        search_dir: Directory to search
        pattern: Glob pattern for files to search
        registry: Optional registry to cache discovered classes
        
    Returns:
        Dict mapping postprocessor names to classes
    """
    discovered = {}
    
    for file_path in search_dir.glob(pattern):
        try:
            module = load_module_from_path(str(file_path))
            
            # Find all BasePostProcessor subclasses in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type) and
                    issubclass(attr, BasePostProcessor) and
                    attr is not BasePostProcessor
                ):
                    discovered[attr_name] = attr
                    if registry:
                        registry.register_postprocessor(attr_name, attr)
        except Exception as e:
            # Log error but continue discovery
            print(f"Warning: Failed to load {file_path}: {e}")
    
    return discovered

