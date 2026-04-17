"""JIRA issue ingestion module with MCP support."""

from typing import List, Dict, Any
from ingestion.mcp_client import MCPClient


def fetch_jira_issues(issue_ids: List[str], use_mcp: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch JIRA issues by ID via MCP.

    Args:
        issue_ids: List of JIRA issue keys (e.g., ["ABC-123", "XYZ-456"])
        use_mcp: Whether to use MCP (default: True)

    Returns JIRA objects with:
    - id
    - title
    - description
    - issue_type
    - status
    - epic_link
    - acceptance_criteria
    """
    # Try MCP first if enabled
    if use_mcp:
        try:
            mcp_client = MCPClient()
            if mcp_client.is_jira_available():
                print("     Using JIRA MCP server...")
                return mcp_client.fetch_jira_issues(issue_ids)
        except NotImplementedError:
            print("     [INFO] JIRA MCP not yet implemented, falling back to mock data")
        except Exception as e:
            print(f"     [WARNING] JIRA MCP failed: {e}, falling back to mock data")

    # Fallback to mock data
    print(f"     [WARNING] Using mock data for {len(issue_ids)} JIRA issues")
    return _get_mock_jira_issues(issue_ids)


def _get_mock_jira_issues(issue_ids: List[str]) -> List[Dict[str, Any]]:
    """Return mock JIRA data for testing."""
    return [
        {
            "id": issue_id,
            "key": issue_id,
            "title": f"Mock JIRA Issue {issue_id}",
            "description": f"This is a mock description for {issue_id}. Integrate with JIRA MCP server to fetch real data.",
            "issue_type": "Story",
            "status": "Done",
            "epic_link": None,
            "acceptance_criteria": "Mock acceptance criteria",
        }
        for issue_id in issue_ids
    ]


def search_jira_by_project(
    project_key: str, use_mcp: bool = True
) -> List[Dict[str, Any]]:
    """
    Search JIRA issues by project key via MCP.

    Args:
        project_key: JIRA project key (e.g., "ABC")
        use_mcp: Whether to use MCP (default: True)

    Returns:
        List of JIRA issue objects
    """
    # Try MCP first if enabled
    if use_mcp:
        try:
            mcp_client = MCPClient()
            if mcp_client.is_jira_available():
                jql = f"project = {project_key}"
                return mcp_client.search_jira_issues(jql)
        except NotImplementedError:
            print("     [INFO] JIRA search via MCP not yet implemented")
        except Exception as e:
            print(f"     [WARNING] JIRA search failed: {e}")

    return []
