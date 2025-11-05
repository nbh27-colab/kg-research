from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GenericNode(BaseModel):
    """
    """
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Type of the node")
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties of the node"
    )

    def get_property(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieve a property value by key.

        Args:
            key (str): The property key.
            default (Any): The default value to return if the key is not found.
        Returns:
            Optional[Any]: The property value if it exists, otherwise None.
        """
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """
        Set a property value by key.

        Args:
            key (str): The property key.
            value (Any): The value to set for the property.
        """
        self.properties[key] = value

    def get_display_name(self) -> str:
        """
        Get a human-readable display name for the node.

        Returns:
            str: The display name of the node.
        """
        return self.properties.get("name", f"{self.type}_{self.id}")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GenericNode):
            return NotImplemented
        return self.id == other.id
    

class GenericEdge(BaseModel):
    """
    Represents a directed edge between two GenericNode instances.
    """
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    type: str = Field(..., description="Type of the edge")
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties of the edge"
    )
    directed: bool = Field(
        default=True,
        description="Indicates if the edge is directed"
    )

    def get_property(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieve a property value by key.

        Args:
            key (str): The property key.
            default (Any): The default value to return if the key is not found.
        Returns:
            Optional[Any]: The property value if it exists, otherwise None.
        """
        return self.properties.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """
        Set a property value by key.

        Args:
            key (str): The property key.
            value (Any): The value to set for the property.
        """
        self.properties[key] = value

class GenericGraph(BaseModel):
    """
    Represents a graph consisting of GenericNode and GenericEdge instances.
    """
    nodes: List[GenericNode] = Field(
        default_factory=list,
        description="List of nodes in the graph"
    )
    edges: List[GenericEdge] = Field(
        default_factory=list,
        description="List of edges in the graph"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional metadata for the graph"
    )

    def add_node(self, node: GenericNode) -> None:
        """
        Add a node to the graph.

        Args:
            node (GenericNode): The node to add.
        """
        self.nodes.append(node)

    def add_edge(self, edge: GenericEdge) -> None:
        """
        Add an edge to the graph.

        Args:
            edge (GenericEdge): The edge to add.
        """
        self.edges.append(edge)

    def get_node_by_id(self, node_id: str) -> Optional[GenericNode]:
        """
        Retrieve a node by its ID.

        Args:
            node_id (str): The ID of the node to retrieve.
        Returns:
            Optional[GenericNode]: The node if found, otherwise None.
        """
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_nodes_by_type(self, node_type: str) -> List[GenericNode]:
        """
        Retrieve all nodes of a specific type.

        Args:
            node_type (str): The type of nodes to retrieve.
        Returns:
            List[GenericNode]: A list of nodes matching the specified type.
        """
        return [node for node in self.nodes if node.type.lower() == node_type.lower()]
    
    def get_edges_by_type(self, edge_type: str) -> List[GenericEdge]:
        """
        Retrieve all edges of a specific type.

        Args:
            edge_type (str): The type of edges to retrieve.
        Returns:
            List[GenericEdge]: A list of edges matching the specified type.
        """
        return [edge for edge in self.edges if edge.type.lower() == edge_type.lower()]
    
    def get_edges_from_node(self, node_id: str) -> List[GenericEdge]:
        """
        Retrieve all edges originating from a specific node.

        Args:
            node_id (str): The ID of the source node.
        Returns:
            List[GenericEdge]: A list of edges originating from the specified node.
        """
        return [edge for edge in self.edges if edge.source == node_id]
    
    def get_edges_to_node(self, node_id: str) -> List[GenericEdge]:
        """
        Retrieve all edges pointing to a specific node.

        Args:
            node_id (str): The ID of the target node.
        Returns:
            List[GenericEdge]: A list of edges pointing to the specified node.
        """
        return [edge for edge in self.edges if edge.target == node_id]
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None) -> List[GenericNode]:
        """
        Retrieve all neighboring nodes connected to a specific node.

        Args:
            node_id (str): The ID of the node whose neighbors are to be retrieved.
        Returns:
            List[GenericNode]: A list of neighboring nodes.
        """
        neighbors = []
        for edge in self.edges:
            if edge.source == node_id:
                if edge_type is None or edge.type.lower() == edge_type.lower():
                    neighbor = self.get_node_by_id(edge.target)
                    if neighbor:
                        neighbors.append(neighbor)
            elif edge.target == node_id:
                if edge_type is None or edge.type.lower() == edge_type.lower():
                    neighbor = self.get_node_by_id(edge.source)
                    if neighbor:
                        neighbors.append(neighbor)
        return neighbors
    
    def get_node_types(self) -> List[str]:
        """
        Retrieve a list of unique node types in the graph.

        Returns:
            List[str]: A list of unique node types.
        """
        return list(set(node.type for node in self.nodes))
    
    def get_edge_types(self) -> List[str]:
        """
        Retrieve a list of unique edge types in the graph.

        Returns:
            List[str]: A list of unique edge types.
        """
        return list(set(edge.type for edge in self.edges))
    
    def get_stats(self) -> Dict[str, int]:
        """
        Retrieve statistics about the graph.

        Returns:
            Dict[str, int]: A dictionary containing the number of nodes and edges.
        """
        return {
            "num_nodes": len(self.nodes),
            "num_edges": len(self.edges),
            "node_types": {node_type: len(self.get_nodes_by_type(node_type)) for node_type in self.get_node_types()},
            "edge_types": {edge_type: len(self.get_edges_by_type(edge_type)) for edge_type in self.get_edge_types()},
        }
    
class GraphQueryResult(BaseModel):
    """
    Represents the result of a graph query.
    """
    nodes: List[GenericNode] = Field(default_factory=list)
    edges: List[GenericEdge] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.nodes)