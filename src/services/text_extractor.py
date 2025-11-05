"""
Text-based extractor implementation.
"""
import json
import logging
from typing import Optional
from datetime import datetime
from openai import OpenAI

from src.interfaces.base_extractor import BaseExtractor
from src.data.generic_models import GenericGraph, GenericNode, GenericEdge
from src.core.config import app_config


logger = logging.getLogger(__name__)


class TextExtractor(BaseExtractor):
    """
    Extracts knowledge graphs from plain text using LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the text extractor.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model_name: Model name to use (defaults to config)
        """
        self.client = OpenAI(api_key=api_key or app_config.OPENAI_API_KEY)
        self.model_name = model_name or app_config.LLM_MODEL_NAME_ANALYSIS
    
    def validate_source(self, source: str) -> bool:
        """
        Validate that the source is a non-empty string.
        
        Args:
            source: The text to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(source, str) and len(source.strip()) > 0
    
    def extract(self, source: str, context: Optional[str] = None, temperature: float = 0.0) -> GenericGraph:
        """
        Extract a knowledge graph from text.
        
        Args:
            source: The text to extract from
            context: Optional additional context to guide extraction
            temperature: Sampling temperature for the LLM
            
        Returns:
            GenericGraph: The extracted knowledge graph
            
        Raises:
            ValueError: If source is invalid
            Exception: If extraction fails
        """
        if not self.validate_source(source):
            raise ValueError("Source must be a non-empty string")
        
        logger.info(f"Extracting graph from text ({len(source)} characters)...")
        
        try:
            # Create the prompt
            prompt = self._create_extraction_prompt(source, context)

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )

            # Parse the response
            response_content = response.choices[0].message.content

            # Parse JSON content
            extracted_data = json.loads(response_content)

            # Create Graph
            graph = GenericGraph()

            # Add metadata
            graph.metadata = {
                "extraction_timestamp": datetime.utcnow().isoformat(),
                "model_name": self.model_name,
                "source_text_length": len(source),
                "context_provided": context,
                "extractor_type": "TextExtractor"
            }

            # Add nodes
            nodes_data = extracted_data.get("nodes", [])
            for node_data in nodes_data:
                try:
                    node = GenericNode(**node_data)
                    graph.add_node(node)
                except Exception as e:
                    logger.warning(f"Error adding node: {e} - Data: {node_data}")
            
            # Add edges
            edges_data = extracted_data.get("edges", [])
            for edge_data in edges_data:
                try:
                    if "directed" not in edge_data:
                        edge_data["directed"] = True
                    edge = GenericEdge(**edge_data)
                    # Validate that source and target nodes exist
                    if graph.get_node_by_id(edge.source) and graph.get_node_by_id(edge.target):
                        graph.add_edge(edge)
                    else:
                        logger.warning(f"Edge references non-existent nodes: {edge_data}")
                except Exception as e:
                    logger.warning(f"Error adding edge: {e} - Data: {edge_data}")
            
            stats = graph.get_stats()
            logger.info(f"Extraction complete: {stats['num_nodes']} nodes, {stats['num_edges']} edges")
            
            return graph
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}", exc_info=True)
            raise
    
    def _create_extraction_prompt(self, text: str, context: Optional[str] = None) -> str:
        """
        Create a prompt for extracting graph from text.
        """
        prompt = f"""You are an expert at extracting structured information from unstructured text.

Your task is to analyze the given text and extract:
1. **Entities (Nodes)**: People, organizations, locations, or any significant items mentioned.
2. **Relationships (Edges)**: Connections or relationships between the entities.

IMPORTANT RULES:
- Extract ALL meaningful entities, regardless of type
- DO NOT limit to predefined categories - create appropriate types as needed
- Each entity should have a unique ID, a type, and relevant properties
- Relationships should be meaningful and directional
- Use clear, descriptive relationship types (WORKS_AT, LOCATED_IN, etc.)
- Include as much detail as possible in properties
- Generate proper JSON format as specified below

OUTPUT FORMAT:
{{
    "nodes": [
        {{
        "id": "unique_entity_id",
        "type": "EntityType",
        "properties": {{
            "name": "Entity Name",
            "additional_property": "value"
        }}
        }}
    ],
    "edges": [
        {{
        "source": "source_entity_id",
        "target": "target_entity_id",
        "type": "RELATIONSHIP_TYPE",
        "properties": {{
            "detail": "value"
        }},
        "directed": true
        }}
    ]
}}

TEXT TO ANALYZE:
{text}
"""
        if context:
            prompt += f"\nADDITIONAL CONTEXT: {context}\n\n"
        prompt += """
Only return valid JSON, no additional text.
"""
        return prompt
