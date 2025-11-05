"""
Abstract base class for knowledge graph extractors.
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.data.generic_models import GenericGraph


class BaseExtractor(ABC):
    """
    Abstract base class for extracting knowledge graphs from various sources.
    """
    
    @abstractmethod
    def extract(self, source: str, context: Optional[str] = None) -> GenericGraph:
        """
        Extract a knowledge graph from the given source.
        
        Args:
            source: The source to extract from (text, URL, file path, etc.)
            context: Optional additional context to guide extraction
            
        Returns:
            GenericGraph: The extracted knowledge graph
            
        Raises:
            Exception: If extraction fails
        """
        pass
    
    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """
        Validate that the source is appropriate for this extractor.
        
        Args:
            source: The source to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pass
