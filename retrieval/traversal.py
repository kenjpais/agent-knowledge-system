"""Graph traversal utilities."""

from typing import List, Tuple, Optional
from graph.graph_builder import KnowledgeGraph
from graph.schema import EdgeType


def bfs_traversal(
    graph: KnowledgeGraph,
    start_node: str,
    max_depth: int = 3,
    edge_types: Optional[List[EdgeType]] = None,
) -> List[Tuple[str, int]]:
    """
    BFS traversal with depth constraint.

    Returns list of (node_id, depth) tuples.
    """
    if edge_types is None:
        edge_types = [EdgeType.DEEP_DIVE, EdgeType.RELATED, EdgeType.NEXT]

    visited = set()
    queue = [(start_node, 0)]
    result = []

    while queue:
        node_id, depth = queue.pop(0)

        if node_id in visited or depth > max_depth:
            continue

        visited.add(node_id)
        result.append((node_id, depth))

        # Add neighbors to queue
        for neighbor in graph.get_neighbors(node_id):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return result
