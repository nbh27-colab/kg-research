"""
Graph Query Service - Handles querying operations on knowledge graphs.
"""
import logging
from typing import List, Optional, Any

from src.data.generic_models import GenericGraph, GenericNode, GenericEdge


logger = logging.getLogger(__name__)


class GraphQueryService:
    """
    Service for querying knowledge graphs.
    """
    
    def __init__(self, graph: Optional[GenericGraph] = None):
        """
        Initialize the query service with an optional graph.
        
        Args:
            graph: The graph to query. Can be set later via set_graph()
        """
        self.graph = graph or GenericGraph()
    
    def set_graph(self, graph: GenericGraph) -> None:
        """Set the graph to query."""
        self.graph = graph
    
    def get_graph(self) -> GenericGraph:
        """Get the current graph."""
        return self.graph
    
    def get_node_by_id(self, node_id: str) -> Optional[GenericNode]:
        """Get a node by its ID."""
        return self.graph.get_node_by_id(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[GenericNode]:
        """Get all nodes of a specific type."""
        return self.graph.get_nodes_by_type(node_type)
    
    def get_nodes_by_property(self, property_key: str, property_value: Any) -> List[GenericNode]:
        """
        Find nodes that have a specific property value.
        Case-insensitive for string values.
        """
        results = []
        for node in self.graph.nodes:
            node_value = node.get_property(property_key)
            if node_value is not None:
                # Case-insensitive comparison for strings
                if isinstance(node_value, str) and isinstance(property_value, str):
                    if node_value.lower() == property_value.lower():
                        results.append(node)
                elif node_value == property_value:
                    results.append(node)
        return results
    
    def search_nodes(self, query: str, search_in_properties: Optional[List[str]] = None) -> List[GenericNode]:
        """
        Search for nodes by text query.
        Searches in node ID, type, and specified properties.
        
        Args:
            query: Search text (case-insensitive)
            search_in_properties: List of property keys to search in. 
                                 If None, searches in all properties.
        
        Returns:
            List of matching nodes
        """
        query_lower = query.lower()
        results = []
        
        for node in self.graph.nodes:
            # Search in ID and type
            if query_lower in node.id.lower() or query_lower in node.type.lower():
                results.append(node)
                continue
            
            # Search in properties
            for key, value in node.properties.items():
                if search_in_properties and key not in search_in_properties:
                    continue
                
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(node)
                    break
        
        return results
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None, 
                     direction: str = 'both') -> List[GenericNode]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: ID of the source node
            edge_type: Optional filter by edge type
            direction: 'outgoing', 'incoming', or 'both'
        
        Returns:
            List of neighboring nodes
        """
        neighbors = []
        
        if direction in ['outgoing', 'both']:
            for edge in self.graph.edges:
                if edge.source == node_id:
                    if edge_type is None or edge.type.lower() == edge_type.lower():
                        neighbor = self.graph.get_node_by_id(edge.target)
                        if neighbor and neighbor not in neighbors:
                            neighbors.append(neighbor)
        
        if direction in ['incoming', 'both']:
            for edge in self.graph.edges:
                if edge.target == node_id:
                    if edge_type is None or edge.type.lower() == edge_type.lower():
                        neighbor = self.graph.get_node_by_id(edge.source)
                        if neighbor and neighbor not in neighbors:
                            neighbors.append(neighbor)
        
        return neighbors
    
    def get_edges_between(self, source_id: str, target_id: str) -> List[GenericEdge]:
        """Get all edges between two nodes."""
        return [edge for edge in self.graph.edges 
                if edge.source == source_id and edge.target == target_id]
    
    def get_edges_by_type(self, edge_type: str) -> List[GenericEdge]:
        """Get all edges of a specific type."""
        return self.graph.get_edges_by_type(edge_type)
    
    def get_subgraph(self, node_ids: List[str], include_edges: bool = True) -> GenericGraph:
        """
        Extract a subgraph containing specified nodes.
        
        Args:
            node_ids: List of node IDs to include
            include_edges: Whether to include edges between these nodes
        
        Returns:
            A new GenericGraph containing the subgraph
        """
        subgraph = GenericGraph()
        
        # Add nodes
        for node_id in node_ids:
            node = self.graph.get_node_by_id(node_id)
            if node:
                subgraph.add_node(node)
        
        # Add edges if requested
        if include_edges:
            for edge in self.graph.edges:
                if edge.source in node_ids and edge.target in node_ids:
                    subgraph.add_edge(edge)
        
        return subgraph
    
    def get_all_nodes(self) -> List[GenericNode]:
        """Get all nodes in the graph."""
        return self.graph.nodes
    
    def get_all_edges(self) -> List[GenericEdge]:
        """Get all edges in the graph."""
        return self.graph.edges
    
    def get_stats(self) -> dict:
        """Get graph statistics."""
        return self.graph.get_stats()
