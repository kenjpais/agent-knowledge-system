"""Schema validation for nodes and edges."""

from typing import List, Dict, Any, Optional
from graph.schema import Node, Edge
from pydantic import BaseModel, ValidationError


class ValidationIssue(BaseModel):
    """Validation issue tracker."""

    type: str
    severity: str
    description: str
    node_id: Optional[str] = None


def validate_node_schema(node_data: Dict[str, Any]) -> List[ValidationIssue]:
    """Validate node conforms to schema."""
    issues = []

    try:
        Node(**node_data)
    except ValidationError as e:
        for error in e.errors():
            issues.append(
                ValidationIssue(
                    type="schema_violation",
                    severity="high",
                    description=f"Node schema error: {error['msg']}",
                    node_id=node_data.get("id"),
                )
            )

    return issues


def validate_edge_schema(edge_data: Dict[str, Any]) -> List[ValidationIssue]:
    """Validate edge conforms to schema."""
    issues = []

    try:
        Edge(**edge_data)
    except ValidationError as e:
        for error in e.errors():
            issues.append(
                ValidationIssue(
                    type="schema_violation",
                    severity="high",
                    description=f"Edge schema error: {error['msg']}",
                )
            )

    return issues
