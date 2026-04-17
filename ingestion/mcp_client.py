"""MCP (Model Context Protocol) client for GitHub and JIRA - Simple Subprocess Approach."""

from typing import List, Dict, Any
import os
import json
import subprocess
from pathlib import Path


class MCPClient:
    """Simple MCP client using subprocess calls to MCP servers."""

    def __init__(self):
        """Initialize MCP client."""
        self.github_enabled = os.getenv("MCP_GITHUB_ENABLED", "false").lower() == "true"
        self.jira_enabled = os.getenv("MCP_JIRA_ENABLED", "false").lower() == "true"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load MCP server configuration from ~/.claude/config.json"""
        config_path = Path.home() / ".claude" / "config.json"
        if not config_path.exists():
            return {}

        try:
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"     [WARNING] Failed to load MCP config: {e}")
            return {}

    def is_github_available(self) -> bool:
        """Check if GitHub MCP server is available."""
        if not self.github_enabled:
            return False
        servers = self.config.get("mcpServers", {})
        return "github" in servers

    def is_jira_available(self) -> bool:
        """Check if JIRA MCP server is available."""
        if not self.jira_enabled:
            return False
        servers = self.config.get("mcpServers", {})
        return "jira" in servers

    def _call_mcp_tool(
        self, server_name: str, tool: str, arguments: Dict[str, Any], timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Call MCP tool via subprocess.

        Args:
            server_name: MCP server name (e.g., "github", "jira")
            tool: Tool name (e.g., "github_list_pulls")
            arguments: Tool arguments
            timeout: Timeout in seconds

        Returns:
            MCP tool result
        """
        servers = self.config.get("mcpServers", {})
        server_config = servers.get(server_name)

        if not server_config:
            raise ValueError(
                f"MCP server '{server_name}' not configured in ~/.claude/config.json"
            )

        # Build JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
        }

        # Prepare command
        cmd = [server_config["command"]] + server_config.get("args", [])
        env = {**os.environ, **server_config.get("env", {})}

        try:
            # Call MCP server
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Send request and get response
            request_json = json.dumps(request) + "\n"
            stdout, stderr = process.communicate(request_json.encode(), timeout=timeout)

            if process.returncode != 0:
                raise RuntimeError(f"MCP server failed: {stderr.decode()}")

            # Parse response
            response = json.loads(stdout.decode())

            if "error" in response:
                raise RuntimeError(f"MCP error: {response['error']}")

            return response.get("result", {})

        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"MCP call to {server_name} timed out after {timeout}s")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse MCP response: {e}")
        except Exception as e:
            raise RuntimeError(f"MCP call failed: {e}")

    def fetch_github_prs(
        self, repo_owner: str, repo_name: str, state: str = "closed", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch PRs from GitHub via MCP.

        Args:
            repo_owner: Repository owner/organization
            repo_name: Repository name
            state: PR state (open, closed, all)
            limit: Maximum number of PRs to fetch

        Returns:
            List of PR objects in our format
        """
        if not self.is_github_available():
            raise RuntimeError("GitHub MCP server not available")

        # Call GitHub MCP server
        result = self._call_mcp_tool(
            "github",
            "github_list_pulls",
            {"owner": repo_owner, "repo": repo_name, "state": state, "per_page": limit},
        )

        # Extract pulls from MCP response
        pulls = result.get("content", [])

        # Transform to our format
        return [
            {
                "id": str(pr.get("number", "")),
                "repo": f"{repo_owner}/{repo_name}",
                "title": pr.get("title", ""),
                "description": pr.get("body", ""),
                "merged_at": pr.get("merged_at"),
                "branch": pr.get("head", {}).get("ref", ""),
                "commits": [],  # Would need separate API call
                "files_changed": [],  # Would need separate API call
            }
            for pr in pulls
        ]

    def fetch_jira_issues(self, issue_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch JIRA issues via MCP.

        Args:
            issue_keys: List of JIRA issue keys (e.g., ["ABC-123", "XYZ-456"])

        Returns:
            List of JIRA issue objects in our format
        """
        if not self.is_jira_available():
            raise RuntimeError("JIRA MCP server not available")

        issues = []
        for key in issue_keys:
            try:
                # Call JIRA MCP server for each issue
                result = self._call_mcp_tool("jira", "jira_get_issue", {"issue_key": key})

                # Extract issue from MCP response
                issue_data = result.get("content", {})
                fields = issue_data.get("fields", {})

                issues.append(
                    {
                        "id": key,
                        "key": key,
                        "title": fields.get("summary", ""),
                        "description": fields.get("description", ""),
                        "issue_type": fields.get("issuetype", {}).get("name", ""),
                        "status": fields.get("status", {}).get("name", ""),
                        "epic_link": fields.get("customfield_10014"),
                        "acceptance_criteria": fields.get("customfield_10015"),
                    }
                )
            except Exception as e:
                print(f"     [WARNING] Failed to fetch JIRA issue {key}: {e}")
                # Add placeholder for failed issue
                issues.append(
                    {
                        "id": key,
                        "key": key,
                        "title": f"Failed to fetch {key}",
                        "description": str(e),
                        "issue_type": "Unknown",
                        "status": "Error",
                        "epic_link": None,
                        "acceptance_criteria": None,
                    }
                )

        return issues

    def search_jira_issues(self, jql: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search JIRA issues using JQL via MCP.

        Args:
            jql: JIRA Query Language string
            max_results: Maximum number of results

        Returns:
            List of JIRA issue objects
        """
        if not self.is_jira_available():
            raise RuntimeError("JIRA MCP server not available")

        # Call JIRA MCP server
        result = self._call_mcp_tool(
            "jira", "jira_search", {"jql": jql, "maxResults": max_results}
        )

        # Extract issues from MCP response
        issues = result.get("content", {}).get("issues", [])

        # Transform to our format
        return [
            {
                "id": issue.get("key"),
                "key": issue.get("key"),
                "title": issue.get("fields", {}).get("summary"),
                "description": issue.get("fields", {}).get("description"),
                "issue_type": issue.get("fields", {}).get("issuetype", {}).get("name"),
                "status": issue.get("fields", {}).get("status", {}).get("name"),
            }
            for issue in issues
        ]
