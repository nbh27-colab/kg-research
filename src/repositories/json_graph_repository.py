"""
JSON-based implementation of GraphRepository.
"""
import json
import os
import logging
from typing import Optional, Dict, Any

from src.interfaces.graph_repository import GraphRepository
from src.data.generic_models import GenericGraph, GenericNode, GenericEdge


logger = logging.getLogger(__name__)


class JsonGraphRepository(GraphRepository):
    """
    Repository for loading and saving graphs in JSON format.
    """
    
    def save(self, graph: GenericGraph, path: str, indent: int = 2) -> bool:
        """
        Save a graph to a JSON file.
        
        Args:
            graph: The graph to save
            path: The path where to save the JSON file
            indent: JSON indentation level (default: 2)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            
            # Convert graph to dict
            graph_dict = graph.model_dump()
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(graph_dict, f, indent=indent, ensure_ascii=False)

            logger.info(f"Successfully saved graph to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving graph to {path}: {e}")
            return False
    
    def load(self, path: str) -> Optional[GenericGraph]:
        """
        Load a graph from a JSON file.
        
        Args:
            path: Path to the JSON file
            
        Returns:
            Optional[GenericGraph]: The loaded graph, or None if failed
        """
        if not self.exists(path):
            logger.error(f"JSON file not found: {path}")
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate basic structure
            if not isinstance(data, dict):
                logger.error(f"JSON file {path} must contain a dictionary/object")
                return None
            
            graph = GenericGraph()
            
            # Load nodes
            nodes_data = data.get('nodes', [])
            if not isinstance(nodes_data, list):
                logger.error("'nodes' field must be a list")
                return None
            
            for node_data in nodes_data:
                try:
                    node = GenericNode(**node_data)
                    graph.add_node(node)
                except Exception as e:
                    logger.warning(f"Failed to load node {node_data.get('id', 'unknown')}: {e}")
                    continue

            logger.info(f"Loaded {len(graph.nodes)} nodes from {path}")

            # Load edges
            edges_data = data.get('edges', [])
            if not isinstance(edges_data, list):
                logger.error("'edges' field must be a list")
                return None
            
            for edge_data in edges_data:
                try:
                    edge = GenericEdge(**edge_data)
                    # Validate that source and target nodes exist
                    if not graph.get_node_by_id(edge.source):
                        logger.warning(f"Edge source node '{edge.source}' not found. Skipping edge.")
                        continue
                    if not graph.get_node_by_id(edge.target):
                        logger.warning(f"Edge target node '{edge.target}' not found. Skipping edge.")
                        continue
                    graph.add_edge(edge)
                except Exception as e:
                    logger.warning(f"Failed to load edge: {e}")
                    continue

            logger.info(f"Loaded {len(graph.edges)} edges from {path}")

            # Load metadata
            graph.metadata = data.get('metadata', {})

            logger.info(f"Successfully loaded graph from {path}")
            logger.debug(f"Graph stats: {graph.get_stats()}")
            
            return graph
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error loading graph from {path}: {e}")
            return None
    
    def exists(self, path: str) -> bool:
        """
        Check if a graph file exists at the specified path.
        
        Args:
            path: The path to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        return os.path.exists(path) and os.path.isfile(path)
    
    def merge(self, graph1: GenericGraph, graph2: GenericGraph) -> GenericGraph:
        """
        Merge two graphs into one, avoiding duplicate nodes.
        
        Args:
            graph1: First graph
            graph2: Second graph
            
        Returns:
            GenericGraph: The merged graph
        """
        merged = GenericGraph()
        
        # Track node IDs to avoid duplicates
        node_ids = set()
        
        # Add nodes from both graphs
        for graph in [graph1, graph2]:
            for node in graph.nodes:
                if node.id not in node_ids:
                    merged.add_node(node)
                    node_ids.add(node.id)
        
        # Add all edges (you might want to deduplicate these too)
        for graph in [graph1, graph2]:
            for edge in graph.edges:
                # Only add edge if both nodes exist in merged graph
                if edge.source in node_ids and edge.target in node_ids:
                    merged.add_edge(edge)
        
        # Merge metadata
        merged.metadata = {**graph1.metadata, **graph2.metadata}
        
        logger.info(f"Merged graphs: {len(merged.nodes)} nodes, {len(merged.edges)} edges")
        return merged
    
    def load_and_merge_multiple(self, paths: list[str]) -> Optional[GenericGraph]:
        """
        Load multiple graph files and merge them into one.
        
        Args:
            paths: List of paths to JSON files
            
        Returns:
            Optional[GenericGraph]: The merged graph, or None if all loads failed
        """
        merged_graph = None
        
        for path in paths:
            graph = self.load(path)
            if graph:
                if merged_graph is None:
                    merged_graph = graph
                else:
                    merged_graph = self.merge(merged_graph, graph)
        
        return merged_graph
