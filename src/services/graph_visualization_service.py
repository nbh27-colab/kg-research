"""
Graph Visualization Service - Creates interactive HTML visualizations.
"""
import os
import html
import logging
import networkx as nx
from pyvis.network import Network
from typing import Dict, Optional

from src.data.generic_models import GenericGraph, GenericNode, GenericEdge


logger = logging.getLogger(__name__)


class GraphVisualizationService:
    """
    Service for creating interactive HTML visualizations of knowledge graphs.
    """
    
    # Predefined color palette for node types
    DEFAULT_NODE_COLORS = [
        '#90EE90',  # Light Green
        '#FFD700',  # Gold
        '#87CEEB',  # Sky Blue
        '#FFB6C1',  # Light Pink
        '#DDA0DD',  # Plum
        '#F0E68C',  # Khaki
        '#98FB98',  # Pale Green
        '#FFA07A',  # Light Salmon
        '#20B2AA',  # Light Sea Green
        '#B0C4DE',  # Light Steel Blue
    ]
    
    # Default edge colors for relationship types
    DEFAULT_EDGE_COLORS = [
        'gray',
        'darkblue',
        'darkgreen',
        'gold',
        'lightcoral',
        'purple',
        'orange',
        'teal',
    ]
    
    def __init__(self):
        """Initialize the visualization service."""
        self.type_to_color_map: Dict[str, str] = {}
        self.edge_type_to_color_map: Dict[str, str] = {}
    
    def _assign_colors_to_types(self, graph: GenericGraph) -> None:
        """Automatically assign colors to node and edge types."""
        # Assign colors to node types
        node_types = graph.get_node_types()
        for i, node_type in enumerate(node_types):
            color_index = i % len(self.DEFAULT_NODE_COLORS)
            self.type_to_color_map[node_type] = self.DEFAULT_NODE_COLORS[color_index]
        
        # Assign colors to edge types
        edge_types = graph.get_edge_types()
        for i, edge_type in enumerate(edge_types):
            color_index = i % len(self.DEFAULT_EDGE_COLORS)
            self.edge_type_to_color_map[edge_type] = self.DEFAULT_EDGE_COLORS[color_index]
    
    def _clean_text(self, text: any) -> str:
        """Clean and escape text for HTML display."""
        if text is None:
            return 'N/A'
        text_str = str(text).replace('\n', ' ').replace('\r', '')
        return html.escape(text_str)
    
    def _create_node_title(self, node: GenericNode) -> str:
        """Create a tooltip/title for a node showing all its properties."""
        lines = [
            f"Type: {self._clean_text(node.type)}",
            f"ID: {self._clean_text(node.id)}",
            "---"
        ]
        
        # Add all properties
        for key, value in node.properties.items():
            lines.append(f"{key}: {self._clean_text(value)}")
        
        return "\n".join(lines)
    
    def _create_edge_title(self, edge: GenericEdge, graph: GenericGraph) -> str:
        """Create a tooltip/title for an edge."""
        source_node = graph.get_node_by_id(edge.source)
        target_node = graph.get_node_by_id(edge.target)
        
        source_name = source_node.get_display_name() if source_node else edge.source
        target_name = target_node.get_display_name() if target_node else edge.target
        
        title = f"{self._clean_text(source_name)} --{edge.type}--> {self._clean_text(target_name)}"
        
        # Add edge properties if any
        if edge.properties:
            title += "\n---"
            for key, value in edge.properties.items():
                title += f"\n{key}: {self._clean_text(value)}"
        
        return title
    
    def _calculate_node_size(self, node: GenericNode, graph: GenericGraph) -> int:
        """Calculate node size based on number of connections."""
        # Count edges
        incoming = len(graph.get_edges_to_node(node.id))
        outgoing = len(graph.get_edges_from_node(node.id))
        total_connections = incoming + outgoing
        
        # Base size + size based on connections
        base_size = 15
        connection_size = min(total_connections * 3, 30)  # Cap at 30
        
        return base_size + connection_size
    
    def create_html(self, 
                   graph: GenericGraph,
                   output_path: Optional[str] = None,
                   height: str = "750px",
                   width: str = "100%",
                   physics_enabled: bool = True) -> str:
        """
        Generate an interactive HTML visualization of the knowledge graph.
        
        Args:
            graph: GenericGraph to visualize
            output_path: Optional path to save the HTML file
            height: Height of the visualization
            width: Width of the visualization
            physics_enabled: Whether to enable physics simulation
        
        Returns:
            str: HTML content of the visualization
        """
        logger.info("Creating knowledge graph visualization...")
        
        if not graph.nodes:
            logger.warning("Graph has no nodes. Cannot create visualization.")
            return "<h3>No data to visualize. Graph is empty.</h3>"
        
        try:
            # Assign colors to types
            self._assign_colors_to_types(graph)
            
            # Create NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes to NetworkX
            for node in graph.nodes:
                node_id = node.id
                label = node.get_display_name()
                title = self._create_node_title(node)
                size = self._calculate_node_size(node, graph)
                color = self.type_to_color_map.get(node.type, '#CCCCCC')
                
                G.add_node(
                    node_id,
                    label=label,
                    group=node.type,
                    title=title,
                    size=size,
                    color=color,
                    font={'color': 'black'}
                )

            logger.info(f"Added {len(graph.nodes)} nodes to NetworkX graph")

            # Add edges to NetworkX
            for edge in graph.edges:
                if G.has_node(edge.source) and G.has_node(edge.target):
                    edge_title = self._create_edge_title(edge, graph)
                    edge_color = self.edge_type_to_color_map.get(edge.type, 'gray')
                    
                    G.add_edge(
                        edge.source,
                        edge.target,
                        title=edge_title,
                        label=edge.type,
                        color=edge_color,
                        width=2,
                        arrows='to' if edge.directed else ''
                    )
                else:
                    logger.warning(f"Skipping edge {edge.source} -> {edge.target}: nodes not found")

            logger.info(f"Added {len(graph.edges)} edges to NetworkX graph")

            # Create Pyvis Network
            net = Network(
                height=height,
                width=width,
                bgcolor="#47414167",
                font_color="white",
                notebook=False,
                directed=True,
                select_menu=True,
                cdn_resources='remote'
            )
            
            # Load from NetworkX
            net.from_nx(G)
            
            # Set visualization options
            physics_config = "true" if physics_enabled else "false"
            
            # Build groups configuration for colors
            groups_config = ",\n                ".join([
                f'"{node_type}": {{ "color": "{color}" }}'
                for node_type, color in self.type_to_color_map.items()
            ])
            
            net.set_options(f"""
            {{
              "physics": {{
                "enabled": {physics_config},
                "barnesHut": {{
                  "gravitationalConstant": -2000,
                  "centralGravity": 0.3,
                  "springLength": 95,
                  "springConstant": 0.04,
                  "damping": 0.3,
                  "avoidOverlap": 0.1
                }},
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "barnesHut"
              }},
              "interaction": {{
                "hover": true,
                "navigationButtons": true,
                "zoomView": true,
                "dragView": true
              }},
              "nodes": {{
                "font": {{
                  "size": 12
                }},
                "color": {{ 
                  "highlight": {{ 
                    "border": "rgba(255,255,255,1)", 
                    "background": "rgba(255,255,255,0.5)" 
                  }},
                  "hover": {{ 
                    "border": "rgba(255,255,255,1)",
                    "background": "rgba(255,255,255,0.5)"
                  }}
                }}
              }},
              "edges": {{
                "font": {{
                  "size": 10,
                  "color": "white" 
                }},
                "arrows": {{
                  "to": {{
                    "enabled": true,
                    "scaleFactor": 0.5
                  }}
                }},
                "smooth": {{
                    "enabled": true,
                    "type": "dynamic"
                }}
              }},
              "groups": {{
                {groups_config}
              }}
            }}
            """)
            
            # Generate HTML
            html_content = net.generate_html()
            
            # Add legend
            html_content = self._add_legend_to_html(html_content, graph)
            
            # Validate HTML
            if not html_content or len(html_content) < 1000:
                logger.error(f"Generated HTML is too small or empty. Length: {len(html_content)}")
                return "<h3>Error: Generated HTML content is invalid.</h3>"
            
            # Save to file if path provided
            if output_path:
                os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Saved knowledge graph HTML to {output_path}")

            logger.info("Knowledge graph HTML generated successfully")
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating knowledge graph: {e}", exc_info=True)
            return f"<h3>Error generating knowledge graph: {e}</h3>"
    
    def _add_legend_to_html(self, html_content: str, graph: GenericGraph) -> str:
        """Add a draggable legend to the HTML showing node types and colors."""
        # Build legend items
        legend_items = []
        for node_type in sorted(self.type_to_color_map.keys()):
            color = self.type_to_color_map[node_type]
            count = len(graph.get_nodes_by_type(node_type))
            legend_items.append(f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="display: inline-block; width: 20px; height: 20px; border-radius: 50%; background-color: {color}; margin-right: 10px; border: 1px solid #777;"></span>
                    <span>{node_type} ({count})</span>
                </div>
            """)
        
        legend_html = f"""
        <div id="kg-legend" style="position: absolute; top: 10px; left: 10px; background: rgba(50, 50, 50, 0.9); padding: 15px; border-radius: 8px; color: white; font-family: Arial, sans-serif; font-size: 14px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); z-index: 1000; cursor: grab; max-width: 250px;">
            <h4 style="margin-top: 0; margin-bottom: 12px; color: #87CEEB;">Node Types</h4>
            {''.join(legend_items)}
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #666; font-size: 12px; color: #aaa;">
                <div>Total: {len(graph.nodes)} nodes, {len(graph.edges)} edges</div>
            </div>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var legend = document.getElementById('kg-legend');
                var isDragging = false;
                var currentX, currentY, initialX, initialY;
                var xOffset = 0, yOffset = 0;

                legend.addEventListener('mousedown', dragStart);
                legend.addEventListener('mouseup', dragEnd);
                document.addEventListener('mousemove', drag);

                function dragStart(e) {{
                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;
                    isDragging = true;
                    legend.style.cursor = 'grabbing';
                }}

                function dragEnd(e) {{
                    initialX = currentX;
                    initialY = currentY;
                    isDragging = false;
                    legend.style.cursor = 'grab';
                }}

                function drag(e) {{
                    if (isDragging) {{
                        e.preventDefault();
                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;
                        xOffset = currentX;
                        yOffset = currentY;
                        legend.style.transform = "translate3d(" + currentX + "px, " + currentY + "px, 0)";
                    }}
                }}
            }});
        </script>
        """
        
        # Insert legend after <body> tag
        body_index = html_content.find("<body>")
        if body_index != -1:
            html_content = html_content[:body_index + len("<body>")] + legend_html + html_content[body_index + len("<body>"):]
        else:
            logger.warning("Could not find <body> tag to insert legend")
        
        return html_content
