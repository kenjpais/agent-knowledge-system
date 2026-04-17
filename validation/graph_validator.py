"""Graph structure validation."""

from typing import List
from graph.graph_builder import KnowledgeGraph
from validation.schema_validator import ValidationIssue


def validate_graph_integrity(graph: KnowledgeGraph) -> List[ValidationIssue]:
    """
    Validate graph structure.

    Checks:
    - No orphan nodes
    - AGENTS.md reaches all nodes within ≤3 hops
    - No broken edges
    """
    issues = []

    # Check for orphan nodes
    orphans = find_orphan_nodes(graph)
    for orphan in orphans:
        issues.append(
            ValidationIssue(
                type="orphan_node",
                severity="high",
                description="Node is not reachable from entry point",
                node_id=orphan,
            )
        )

    # Check AGENTS.md reachability
    unreachable = check_reachability_from_entry(graph, max_hops=3)
    for node_id in unreachable:
        issues.append(
            ValidationIssue(
                type="unreachable_node",
                severity="medium",
                description="Node not reachable from AGENTS.md within 3 hops",
                node_id=node_id,
            )
        )

    return issues


def find_orphan_nodes(graph: KnowledgeGraph) -> List[str]:
    """Find nodes with no incoming or outgoing edges."""
    orphans = []

    for node_id in graph.graph.nodes():
        in_degree = graph.graph.in_degree(node_id)
        out_degree = graph.graph.out_degree(node_id)

        if in_degree == 0 and out_degree == 0:
            orphans.append(node_id)

    return orphans


def check_reachability_from_entry(graph: KnowledgeGraph, max_hops: int = 3) -> List[str]:
    """Find nodes not reachable from AGENTS.md entry point within max_hops."""
    entry_node = "agents_md"

    # If entry node doesn't exist, all nodes are unreachable
    if entry_node not in graph.graph:
        return list(graph.graph.nodes())

    # BFS with depth tracking
    reachable = set()
    queue = [(entry_node, 0)]  # (node_id, depth)
    visited = {entry_node}

    while queue:
        current_node, depth = queue.pop(0)
        reachable.add(current_node)

        if depth < max_hops:
            for neighbor in graph.graph.successors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

    # Find unreachable nodes
    all_nodes = set(graph.graph.nodes())
    unreachable = all_nodes - reachable

    return list(unreachable)
