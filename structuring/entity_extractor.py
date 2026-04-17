"""Entity extraction from PR and JIRA data."""

from typing import List


def extract_components(pr_files: List[str]) -> List[str]:
    """Extract affected components from PR file changes."""
    # TODO: Implement component extraction
    return []


def extract_decisions(pr_description: str, jira_description: str) -> List[str]:
    """Extract architectural decisions from descriptions."""
    # TODO: Implement decision extraction
    return []
