"""
CLI tool for visualizing knowledge graphs.
Refactored to use dependency injection and proper separation of concerns.
"""
import os
import argparse
import logging

from src.repositories.json_graph_repository import JsonGraphRepository
from src.services.graph_visualization_service import GraphVisualizationService
from src.core.config import app_settings
from src.utils.logging_config import setup_logging


logger = logging.getLogger(__name__)


class GraphVisualizationCLI:
    """CLI for knowledge graph visualization operations."""
    
    def __init__(self):
        """Initialize repository and visualization service with dependency injection."""
        self.repository = JsonGraphRepository()
        self.viz_service = GraphVisualizationService()
    
    def visualize_graph(
        self,
        json_path: str,
        output_path: str,
        physics_enabled: bool = True,
        height: str = "800px",
        width: str = "100%"
    ) -> None:
        """Load and visualize a graph from JSON file."""
        logger.info(f"Loading graph from {json_path}")
        
        # Load graph
        graph = self.repository.load(json_path)
        if not graph:
            logger.error(f"Failed to load graph from {json_path}")
            return
        
        # Display stats
        stats = graph.get_stats()
        logger.info(f"Graph has {stats['num_nodes']} nodes and {stats['num_edges']} edges")
        logger.info(f"Node types: {stats['node_types']}")
        logger.info(f"Edge types: {stats['edge_types']}")
        
        # Create visualization
        logger.info(f"Creating visualization...")
        html_content = self.viz_service.create_html(
            graph,
            output_path=output_path,
            physics_enabled=physics_enabled,
            height=height,
            width=width
        )
        
        if html_content and len(html_content) > 1000:
            logger.info(f"Visualization saved to {output_path}")
        else:
            logger.error("Failed to create visualization")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Visualize knowledge graphs from JSON files."
    )
    parser.add_argument(
        "--json_path",
        type=str,
        required=True,
        help="Path to the JSON file containing the graph data"
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default=os.path.join(app_settings.DEFAULT_VISUALIZATION_DIR, "graph.html"),
        help=f"Output path for the HTML visualization (default: {os.path.join(app_settings.DEFAULT_VISUALIZATION_DIR, 'graph.html')})"
    )
    parser.add_argument(
        "--no_physics",
        action="store_true",
        help="Disable physics simulation"
    )
    parser.add_argument(
        "--height",
        type=str,
        default=app_settings.DEFAULT_VIZ_HEIGHT,
        help=f"Height of the visualization (default: {app_settings.DEFAULT_VIZ_HEIGHT})"
    )
    parser.add_argument(
        "--width",
        type=str,
        default=app_settings.DEFAULT_VIZ_WIDTH,
        help=f"Width of the visualization (default: {app_settings.DEFAULT_VIZ_WIDTH})"
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
    cli = GraphVisualizationCLI()
    
    try:
        cli.visualize_graph(
            json_path=args.json_path,
            output_path=args.output_path,
            physics_enabled=not args.no_physics,
            height=args.height,
            width=args.width
        )
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
