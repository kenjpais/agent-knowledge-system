"""Knowledge graph construction logic."""

from typing import List, Dict, Any, Optional
import networkx as nx
from graph.schema import Node, Edge, EdgeType


class KnowledgeGraph:
    """In-memory knowledge graph using NetworkX."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node: Node) -> None:
        """Add a node to the graph."""
        self.graph.add_node(
            node.id,
            type=node.type,
            title=node.title,
            file_path=node.file_path,
            metadata=node.metadata,
        )

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        self.graph.add_edge(edge.from_node, edge.to_node, type=edge.type)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve node data by ID."""
        if node_id in self.graph:
            return self.graph.nodes[node_id]
        return None

    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[str]:
        """Get neighboring nodes, optionally filtered by edge type."""
        if node_id not in self.graph:
            return []

        neighbors = []
        for neighbor in self.graph.successors(node_id):
            edge_data = self.graph.edges[node_id, neighbor]
            if edge_type is None or edge_data.get("type") == edge_type:
                neighbors.append(neighbor)
        return neighbors
