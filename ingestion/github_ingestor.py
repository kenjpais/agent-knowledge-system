"""GitHub PR ingestion module with MCP support."""

from typing import List, Dict, Any
import re
from ingestion.mcp_client import MCPClient


def fetch_merged_prs(
    repo_owner: str, repo_name: str, use_mcp: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetch latest merged PRs from GitHub.

    Args:
        repo_owner: Repository owner/organization
        repo_name: Repository name
        use_mcp: Whether to use MCP (default: True)

    Returns PR objects with:
    - id
    - title
    - description
    - merged_at
    - branch
    - commits[]
    - files_changed[]
    """
    # Try MCP first if enabled
    if use_mcp:
        try:
            mcp_client = MCPClient()
            if mcp_client.is_github_available():
                print("     Using GitHub MCP server...")
                return mcp_client.fetch_github_prs(repo_owner, repo_name, state="closed")
        except NotImplementedError:
            print("     [INFO] GitHub MCP not yet implemented, falling back to mock data")
        except Exception as e:
            print(f"     [WARNING] GitHub MCP failed: {e}, falling back to mock data")

    # Fallback to mock data
    print(f"     [WARNING] Using mock data for {repo_owner}/{repo_name}")
    return _get_mock_prs(repo_owner, repo_name)


def _get_mock_prs(repo_owner: str, repo_name: str) -> List[Dict[str, Any]]:
    """Return mock PR data for testing."""
    # Generate different mock data based on repo
    repo_suffix = repo_name.replace("-", "_")[:3].upper()

    return [
        {
            "id": f"{repo_suffix}-123",
            "repo": f"{repo_owner}/{repo_name}",
            "title": f"[{repo_suffix}-101] Add user authentication feature",
            "description": f"Implements OAuth2 authentication for {repo_name}. Fixes {repo_suffix}-101 and {repo_suffix}-102",
            "merged_at": "2024-03-15T10:30:00Z",
            "branch": "feature/auth",
            "commits": ["a1b2c3d", "e4f5g6h"],
            "files_changed": [
                "auth/oauth.py",
                "auth/middleware.py",
                "api/routes.py",
            ],
        },
        {
            "id": f"{repo_suffix}-124",
            "repo": f"{repo_owner}/{repo_name}",
            "title": f"{repo_suffix}-200: Refactor database connection pool",
            "description": f"Improves connection pooling for {repo_name}",
            "merged_at": "2024-03-16T14:20:00Z",
            "branch": "refactor/db-pool",
            "commits": ["i7j8k9l"],
            "files_changed": ["storage/db.py", "storage/connection_pool.py"],
        },
    ]


def extract_jira_references(pr_data: Dict[str, Any]) -> List[str]:
    """
    Extract JIRA ticket IDs from PR title and description.
    Uses regex pattern: ABC-123 format
    """
    jira_pattern = r"[A-Z]+-\d+"
    jira_ids = []

    # Extract from title
    title = pr_data.get("title", "")
    jira_ids.extend(re.findall(jira_pattern, title))

    # Extract from description
    description = pr_data.get("description", "")
    jira_ids.extend(re.findall(jira_pattern, description))

    # Return unique IDs
    return list(set(jira_ids))
