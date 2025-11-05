"""
URL-based extractor implementation.
"""
import os
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional

from src.interfaces.base_extractor import BaseExtractor
from src.data.generic_models import GenericGraph
from src.services.text_extractor import TextExtractor


logger = logging.getLogger(__name__)


class URLExtractor(BaseExtractor):
    """
    Extracts knowledge graphs from web URLs.
    Fetches the webpage, extracts text, and uses TextExtractor for graph extraction.
    """
    
    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    
    def __init__(self, text_extractor: Optional[TextExtractor] = None, 
                 timeout: int = 30, user_agent: Optional[str] = None):
        """
        Initialize the URL extractor.
        
        Args:
            text_extractor: TextExtractor instance to use (creates new if None)
            timeout: Request timeout in seconds
            user_agent: Custom user agent string
        """
        self.text_extractor = text_extractor or TextExtractor()
        self.timeout = timeout
        self.user_agent = user_agent or self.DEFAULT_USER_AGENT
    
    def validate_source(self, source: str) -> bool:
        """
        Validate that the source is a valid URL.
        
        Args:
            source: The URL to validate
            
        Returns:
            bool: True if valid URL, False otherwise
        """
        return isinstance(source, str) and (source.startswith('http://') or source.startswith('https://'))
    
    def extract(self, source: str, context: Optional[str] = None) -> GenericGraph:
        """
        Extract a knowledge graph from a URL.
        
        Args:
            source: The URL to extract from
            context: Optional additional context to guide extraction
            
        Returns:
            GenericGraph: The extracted knowledge graph
            
        Raises:
            ValueError: If source is not a valid URL
            Exception: If extraction fails
        """
        if not self.validate_source(source):
            raise ValueError("Source must be a valid URL starting with http:// or https://")
        
        logger.info(f"Extracting graph from URL: {source}")
        
        try:
            # Fetch webpage content
            text = self._fetch_and_parse_url(source)
            
            # Extract graph using text extractor
            graph = self.text_extractor.extract(text, context)
            
            # Add URL to metadata
            if graph.metadata is None:
                graph.metadata = {}
            graph.metadata['source_url'] = source
            graph.metadata['extractor_type'] = 'URLExtractor'
            
            logger.info(f"Successfully extracted graph from URL: {source}")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to extract from URL {source}: {e}", exc_info=True)
            raise
    
    def _fetch_and_parse_url(self, url: str) -> str:
        """
        Fetch webpage content and extract clean text.
        
        Args:
            url: The URL to fetch
            
        Returns:
            str: Cleaned text content
            
        Raises:
            requests.RequestException: If request fails
        """
        logger.info("Fetching webpage content...")
        
        headers = {
            "User-Agent": self.user_agent
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator='\n')

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            logger.info(f"Extracted {len(text)} characters of text from {url}")
            return text
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            raise
    
    def extract_and_save_text(self, url: str, output_dir: str) -> str:
        """
        Fetch URL and save the extracted text to a file.
        
        Args:
            url: The URL to fetch
            output_dir: Directory to save the text file
            
        Returns:
            str: Path to the saved text file
        """
        text = self._fetch_and_parse_url(url)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename based on URL
        filename = url.replace("http://", "").replace("https://", "").replace("/", "_") + ".txt"
        text_path = os.path.join(output_dir, filename)
        
        # Save text to file
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        logger.info(f"Saved extracted text to {text_path}")
        return text_path
