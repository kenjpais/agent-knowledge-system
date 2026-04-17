"""Knowledge graph schema definitions."""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class NodeType(str, Enum):
    """Valid node types in the knowledge graph."""

    DOCUMENT = "Document"
    SECTION = "Section"
    CONCEPT = "Concept"
    WORKFLOW = "Workflow"
    ADR = "ADR"
    EXECUTION_PLAN = "ExecutionPlan"
    ENTRY_POINT = "EntryPoint"


class EdgeType(str, Enum):
    """Valid edge types in the knowledge graph."""

    CONTAINS = "CONTAINS"
    NEXT = "NEXT"
    DEEP_DIVE = "DEEP_DIVE"
    RELATED = "RELATED"
    DECIDED_BY = "DECIDED_BY"
    PLANNED_IN = "PLANNED_IN"
    REFERENCES = "REFERENCES"
    INDEXES = "INDEXES"


class Node(BaseModel):
    """Knowledge graph node."""

    id: str
    type: NodeType
    title: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Edge(BaseModel):
    """Knowledge graph edge."""

    from_node: str
    to_node: str
    type: EdgeType
