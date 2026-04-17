"""Graph loading utilities."""

from graph.graph_builder import KnowledgeGraph
from graph.schema import Node, Edge
import json


def load_graph_from_json(json_path: str) -> KnowledgeGraph:
    """Load knowledge graph from JSON file."""
    with open(json_path, "r") as f:
        data = json.load(f)

    graph = KnowledgeGraph()

    for node_data in data.get("nodes", []):
        node = Node(**node_data)
        graph.add_node(node)

    for edge_data in data.get("edges", []):
        edge = Edge(**edge_data)
        graph.add_edge(edge)

    return graph
