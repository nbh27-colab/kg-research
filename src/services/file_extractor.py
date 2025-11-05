"""
File-based extractor implementation.
"""
import os
import logging
from typing import Optional, List

from src.interfaces.base_extractor import BaseExtractor
from src.data.generic_models import GenericGraph
from src.services.text_extractor import TextExtractor


logger = logging.getLogger(__name__)


class FileExtractor(BaseExtractor):
    """
    Extracts knowledge graphs from text files.
    Reads the file and uses TextExtractor for graph extraction.
    """
    
    def __init__(self, text_extractor: Optional[TextExtractor] = None):
        """
        Initialize the file extractor.
        
        Args:
            text_extractor: TextExtractor instance to use (creates new if None)
        """
        self.text_extractor = text_extractor or TextExtractor()
    
    def validate_source(self, source: str) -> bool:
        """
        Validate that the source is a valid file path.
        
        Args:
            source: The file path to validate
            
        Returns:
            bool: True if valid file, False otherwise
        """
        return isinstance(source, str) and os.path.isfile(source)
    
    def extract(self, source: str, context: Optional[str] = None) -> GenericGraph:
        """
        Extract a knowledge graph from a text file.
        
        Args:
            source: The file path to extract from
            context: Optional additional context to guide extraction
            
        Returns:
            GenericGraph: The extracted knowledge graph
            
        Raises:
            ValueError: If source is not a valid file
            Exception: If extraction fails
        """
        if not self.validate_source(source):
            raise ValueError(f"Source must be a valid file path: {source}")
        
        logger.info(f"Extracting graph from file: {source}")
        
        try:
            # Read file content
            with open(source, 'r', encoding='utf-8') as f:
                text = f.read()
            
            logger.info(f"Read {len(text)} characters from {source}")
            
            # Extract graph using text extractor
            graph = self.text_extractor.extract(text, context)
            
            # Add file path to metadata
            if graph.metadata is None:
                graph.metadata = {}
            graph.metadata['source_file'] = source
            graph.metadata['extractor_type'] = 'FileExtractor'
            
            logger.info(f"Successfully extracted graph from file: {source}")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to extract from file {source}: {e}", exc_info=True)
            raise
    
    def extract_from_multiple(self, file_paths: List[str], context: Optional[str] = None) -> List[GenericGraph]:
        """
        Extract graphs from multiple files.
        
        Args:
            file_paths: List of file paths to extract from
            context: Optional additional context for all extractions
            
        Returns:
            List[GenericGraph]: List of extracted graphs
        """
        graphs = []
        
        for file_path in file_paths:
            try:
                graph = self.extract(file_path, context)
                graphs.append(graph)
            except Exception as e:
                logger.error(f"Failed to extract from {file_path}: {e}")
                continue
        
        logger.info(f"Extracted {len(graphs)} graphs from {len(file_paths)} files")
        return graphs
