"""
Simple example of MCP integration for GitHub and JIRA.

This example shows the simplest way to integrate MCP servers.
Choose the approach that best fits your needs.
"""

import os
import json
import subprocess
from typing import List, Dict, Any
from pathlib import Path


# ============================================================================
# Approach 1: Direct Subprocess Calls (Simplest)
# ============================================================================


def call_github_mcp_simple(tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call GitHub MCP server directly via subprocess.

    Pros: Simple, no dependencies
    Cons: Synchronous, no connection reuse
    """
    # Build JSON-RPC request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }

    # Call MCP server
    cmd = ["npx", "-y", "@modelcontextprotocol/server-github"]
    env = {**os.environ, "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")}

    process = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
    )

    # Send request and get response
    request_json = json.dumps(request) + "\n"
    stdout, stderr = process.communicate(request_json.encode(), timeout=30)

    if process.returncode != 0:
        raise RuntimeError(f"MCP failed: {stderr.decode()}")

    response = json.loads(stdout.decode())

    if "error" in response:
        raise RuntimeError(f"MCP error: {response['error']}")

    return response.get("result", {})


def fetch_prs_simple(owner: str, repo: str) -> List[Dict]:
    """Fetch PRs using simple MCP approach."""
    result = call_github_mcp_simple(
        "github_list_pulls", {"owner": owner, "repo": repo, "state": "closed", "per_page": 10}
    )

    pulls = result.get("content", [])
    return pulls


# ============================================================================
# Approach 2: Configuration-Based (Recommended)
# ============================================================================


class SimpleMCPClient:
    """
    Simple MCP client that reads configuration from ~/.claude/config.json

    Pros: Reusable, follows standard config
    Cons: Still synchronous
    """

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load MCP server config from Claude Desktop."""
        config_path = Path.home() / ".claude" / "config.json"
        if not config_path.exists():
            return {}

        with open(config_path) as f:
            return json.load(f)

    def call_tool(self, server_name: str, tool: str, arguments: Dict) -> Dict:
        """Call MCP tool on specified server."""
        servers = self.config.get("mcpServers", {})
        server_config = servers.get(server_name)

        if not server_config:
            raise ValueError(f"MCP server '{server_name}' not configured in ~/.claude/config.json")

        # Build request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }

        # Prepare command
        cmd = [server_config["command"]] + server_config.get("args", [])
        env = {**os.environ, **server_config.get("env", {})}

        # Execute
        process = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
        )

        request_json = json.dumps(request) + "\n"
        stdout, stderr = process.communicate(request_json.encode(), timeout=30)

        if process.returncode != 0:
            raise RuntimeError(f"MCP server failed: {stderr.decode()}")

        response = json.loads(stdout.decode())

        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error']}")

        return response.get("result", {})

    def fetch_github_prs(self, owner: str, repo: str, state: str = "closed") -> List[Dict]:
        """Fetch GitHub PRs via MCP."""
        result = self.call_tool(
            "github", "github_list_pulls", {"owner": owner, "repo": repo, "state": state, "per_page": 50}
        )

        pulls = result.get("content", [])

        # Transform to our format
        return [
            {
                "id": str(pr["number"]),
                "repo": f"{owner}/{repo}",
                "title": pr["title"],
                "description": pr.get("body", ""),
                "merged_at": pr.get("merged_at"),
                "branch": pr.get("head", {}).get("ref"),
                "commits": [],
                "files_changed": [],
            }
            for pr in pulls
        ]

    def fetch_jira_issue(self, issue_key: str) -> Dict:
        """Fetch JIRA issue via MCP."""
        result = self.call_tool("jira", "jira_get_issue", {"issue_key": issue_key})

        issue = result.get("content", {})
        fields = issue.get("fields", {})

        return {
            "id": issue_key,
            "key": issue_key,
            "title": fields.get("summary"),
            "description": fields.get("description"),
            "issue_type": fields.get("issuetype", {}).get("name"),
            "status": fields.get("status", {}).get("name"),
        }


# ============================================================================
# Example Usage
# ============================================================================


def example_simple_usage():
    """Example: Simple MCP usage without configuration."""
    print("=== Simple MCP Usage ===\n")

    try:
        prs = fetch_prs_simple("octocat", "Hello-World")
        print(f"Fetched {len(prs)} PRs")
        for pr in prs[:3]:
            print(f"  - #{pr['number']}: {pr['title']}")
    except Exception as e:
        print(f"Error: {e}")


def example_config_based_usage():
    """Example: Configuration-based MCP usage."""
    print("\n=== Configuration-Based MCP Usage ===\n")

    client = SimpleMCPClient()

    # Fetch GitHub PRs
    try:
        print("Fetching GitHub PRs...")
        prs = client.fetch_github_prs("your-org", "your-repo")
        print(f"Fetched {len(prs)} PRs")
        for pr in prs[:3]:
            print(f"  - {pr['id']}: {pr['title']}")
    except Exception as e:
        print(f"GitHub error: {e}")

    # Fetch JIRA issues
    try:
        print("\nFetching JIRA issues...")
        issue = client.fetch_jira_issue("PROJ-123")
        print(f"Issue: {issue['key']} - {issue['title']}")
        print(f"Status: {issue['status']}")
    except Exception as e:
        print(f"JIRA error: {e}")


def example_multi_repo():
    """Example: Fetch from multiple repositories."""
    print("\n=== Multi-Repo Example ===\n")

    client = SimpleMCPClient()
    repos = [("your-org", "repo1"), ("your-org", "repo2"), ("another-org", "repo3")]

    all_prs = []
    for owner, repo in repos:
        try:
            print(f"Fetching PRs from {owner}/{repo}...")
            prs = client.fetch_github_prs(owner, repo)
            all_prs.extend(prs)
            print(f"  Found {len(prs)} PRs")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nTotal PRs across all repos: {len(all_prs)}")


if __name__ == "__main__":
    print("MCP Integration Examples\n")
    print("Before running, ensure:")
    print("1. MCP servers are installed")
    print("2. ~/.claude/config.json is configured")
    print("3. GITHUB_TOKEN environment variable is set")
    print("=" * 60)

    # Run examples
    example_simple_usage()
    example_config_based_usage()
    example_multi_repo()
