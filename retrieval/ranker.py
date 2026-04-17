"""Node ranking utilities for retrieval."""

from typing import List, Dict, Any


def rank_nodes(
    nodes: List[str], query: str, node_data: Dict[str, Any], depths: Dict[str, int]
) -> List[str]:
    """
    Rank nodes by relevance.

    Scoring factors:
    - Node type match with intent
    - Distance penalty (depth)
    - Keyword overlap
    """
    # TODO: Implement ranking logic
    return nodes


def calculate_keyword_overlap(text: str, query: str) -> float:
    """Calculate keyword overlap score."""
    # TODO: Implement keyword matching
    return 0.0
