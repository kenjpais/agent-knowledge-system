"""Repository metadata scanner."""

from typing import Dict, Any, List


def scan_repo_structure(repo_path: str) -> Dict[str, Any]:
    """
    Extract repository structure metadata.

    Returns:
    - file tree
    - markdown docs
    - YAML/CRDs
    """
    # TODO: Implement repo scanning
    return {"files": [], "markdown_docs": [], "yaml_files": []}


def extract_markdown_docs(repo_path: str) -> List[str]:
    """Extract all markdown documentation files."""
    # TODO: Implement markdown extraction
    return []
