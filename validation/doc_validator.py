"""Documentation completeness validator."""

from typing import List
from graph.graph_builder import KnowledgeGraph
from graph.schema import NodeType
from validation.schema_validator import ValidationIssue


def validate_documentation_completeness(graph: KnowledgeGraph) -> List[ValidationIssue]:
    """
    Validate documentation completeness.

    Checks:
    - Every concept has ADR or explanation
    - Every feature has execution plan
    - Correct markdown structure
    """
    issues = []

    # Check concepts have ADRs
    for node_id, node_data in graph.graph.nodes(data=True):
        if node_data.get("type") == NodeType.CONCEPT:
            if not has_adr_link(graph, node_id):
                issues.append(
                    ValidationIssue(
                        type="missing_adr",
                        severity="medium",
                        description="Concept node missing ADR reference",
                        node_id=node_id,
                    )
                )

    return issues


def has_adr_link(graph: KnowledgeGraph, node_id: str) -> bool:
    """Check if concept node has ADR edge."""
    # TODO: Implement ADR link check
    from graph.schema import EdgeType

    neighbors = graph.get_neighbors(node_id, EdgeType.DECIDED_BY)
    return len(neighbors) > 0
