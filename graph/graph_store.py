"""Graph persistence layer."""

import json
from typing import Dict, Any
from pathlib import Path
from graph.graph_builder import KnowledgeGraph
from graph.schema import Node, Edge


def save_graph(graph: KnowledgeGraph, output_path: str = "graph_store/graph.json") -> None:
    """Persist graph to JSON file."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    graph_data: Dict[str, Any] = {"nodes": [], "edges": []}

    for node_id, node_data in graph.graph.nodes(data=True):
        graph_data["nodes"].append({"id": node_id, **node_data})

    for from_node, to_node, edge_data in graph.graph.edges(data=True):
        graph_data["edges"].append({"from_node": from_node, "to_node": to_node, **edge_data})

    with open(output_path, "w") as f:
        json.dump(graph_data, f, indent=2)


def load_graph(input_path: str = "graph_store/graph.json") -> KnowledgeGraph:
    """Load graph from JSON file."""
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Graph file not found: {input_path}")

    with open(input_path, "r") as f:
        graph_data = json.load(f)

    graph = KnowledgeGraph()

    # Load nodes
    for node_data in graph_data.get("nodes", []):
        node = Node(**node_data)
        graph.add_node(node)

    # Load edges
    for edge_data in graph_data.get("edges", []):
        edge = Edge(**edge_data)
        graph.add_edge(edge)

    return graph
