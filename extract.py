"""
CLI tool for extracting knowledge graphs from various sources.
Refactored to use dependency injection and proper separation of concerns.
"""
import os
import argparse
import logging

from src.services.text_extractor import TextExtractor
from src.services.url_extractor import URLExtractor
from src.services.file_extractor import FileExtractor
from src.repositories.json_graph_repository import JsonGraphRepository
from src.core.config import app_settings
from src.utils.logging_config import setup_logging



logger = logging.getLogger(__name__)


class GraphExtractionCLI:
    """CLI for knowledge graph extraction operations."""
    
    def __init__(self):
        """Initialize extractors and repository with dependency injection."""
        self.text_extractor = TextExtractor()
        self.url_extractor = URLExtractor(text_extractor=self.text_extractor)
        self.file_extractor = FileExtractor(text_extractor=self.text_extractor)
        self.repository = JsonGraphRepository()
    
    def extract_from_text(self, text: str) -> None:
        """Extract and display graph from text."""
        logger.info("Extracting graph from text...")
        
        try:
            graph = self.text_extractor.extract(text)
            stats = graph.get_stats()
            logger.info(f"Extraction complete: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
            logger.info(f"Node types: {stats['node_types']}")
            logger.info(f"Edge types: {stats['edge_types']}")
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
    
    def extract_from_url(self, url: str, output_dir: str) -> None:
        """Extract graph from URL and save to files."""
        logger.info(f"Extracting graph from URL: {url}")
        
        try:
            # Extract text and save it
            text_path = self.url_extractor.extract_and_save_text(url, output_dir)
            
            # Extract graph
            graph = self.url_extractor.extract(url)
            
            # Save graph
            filename = os.path.basename(text_path).replace(".txt", "_graph.json")
            json_path = os.path.join(output_dir, filename)
            self.repository.save(graph, json_path)
            
            stats = graph.get_stats()
            logger.info(f"Extraction complete: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
            
        except Exception as e:
            logger.error(f"Extraction from URL failed: {e}")
            raise
    
    def extract_from_url_list(self, file_path: str, output_dir: str) -> None:
        """Extract graphs from a list of URLs in a file."""
        logger.info(f"Extracting graphs from URL list: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Found {len(urls)} URLs to process")
            
            for idx, url in enumerate(urls, start=1):
                logger.info(f"Processing URL {idx}/{len(urls)}: {url}")
                try:
                    self.extract_from_url(url, output_dir)
                except Exception as e:
                    logger.error(f"Failed to extract from URL {url}: {e}")
            
            logger.info("All URLs processed")
            
        except Exception as e:
            logger.error(f"Extraction from URL list failed: {e}")
            raise
    
    def merge_graphs(self, input_dir: str, output_path: str) -> None:
        """Merge all graph JSON files in a directory."""
        logger.info(f"Merging graphs from directory: {input_dir}")
        
        try:
            # Find all graph JSON files
            json_files = [
                os.path.join(input_dir, f) 
                for f in os.listdir(input_dir) 
                if f.endswith("_graph.json")
            ]
            
            if not json_files:
                logger.warning(f"No graph JSON files found in {input_dir}")
                return
            
            logger.info(f"Found {len(json_files)} graph files to merge")
            
            # Load and merge all graphs
            merged_graph = self.repository.load_and_merge_multiple(json_files)
            
            if merged_graph:
                # Save merged graph
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                self.repository.save(merged_graph, output_path)
                
                stats = merged_graph.get_stats()
                logger.info(f"Merged graph saved to {output_path}")
                logger.info(f"Total: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
            else:
                logger.error("Failed to merge graphs")
                
        except Exception as e:
            logger.error(f"Merging graphs failed: {e}")
            raise



def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract knowledge graphs from text, URLs, or files."
    )
    parser.add_argument(
        "--text", 
        type=str, 
        help="Input text to extract graph from"
    )
    parser.add_argument(
        "--url", 
        type=str, 
        help="Input URL to extract graph from"
    )
    parser.add_argument(
        "--url_list_file", 
        type=str, 
        help="Path to a file containing URLs (one per line)"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default=app_settings.DEFAULT_EXTRACTED_DIR,
        help=f"Directory to save extracted graphs (default: {app_settings.DEFAULT_EXTRACTED_DIR})"
    )
    parser.add_argument(
        "--merge", 
        action="store_true", 
        help="Merge all graph JSON files in the output directory"
    )
    parser.add_argument(
        "--merge_output",
        type=str,
        default=os.path.join(app_settings.DEFAULT_MERGED_DIR, "merged_graphs.json"),
        help="Output path for merged graph"
    )
    parser.add_argument(
        "--log_level",
        type=str,
        default=app_settings.DEFAULT_LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Logging level (default: {app_settings.DEFAULT_LOG_LEVEL})"
    )

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    
    # Create CLI instance
    cli = GraphExtractionCLI()
    
    try:
        if args.text:
            cli.extract_from_text(args.text)
        elif args.url:
            cli.extract_from_url(args.url, args.output_dir)
        elif args.url_list_file:
            cli.extract_from_url_list(args.url_list_file, args.output_dir)
        elif args.merge:
            cli.merge_graphs(args.output_dir, args.merge_output)
        else:
            parser.print_help()
            logger.error("Please provide --text, --url, --url_list_file, or --merge")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()