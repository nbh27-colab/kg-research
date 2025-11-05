"""
Abstract repository interface for graph persistence.
"""
from abc import ABC, abstractmethod
from typing import Optional

from src.data.generic_models import GenericGraph


class GraphRepository(ABC):
    """
    Abstract repository for loading and saving knowledge graphs.
    """
    
    @abstractmethod
    def save(self, graph: GenericGraph, path: str) -> bool:
        """
        Save a graph to the specified path.
        
        Args:
            graph: The graph to save
            path: The path where to save the graph
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> Optional[GenericGraph]:
        """
        Load a graph from the specified path.
        
        Args:
            path: The path to load from
            
        Returns:
            Optional[GenericGraph]: The loaded graph, or None if failed
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a graph exists at the specified path.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def merge(self, graph1: GenericGraph, graph2: GenericGraph) -> GenericGraph:
        """
        Merge two graphs into one.
        
        Args:
            graph1: First graph
            graph2: Second graph
            
        Returns:
            GenericGraph: The merged graph
        """
        pass
