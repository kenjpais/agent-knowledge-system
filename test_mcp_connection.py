#!/usr/bin/env python3
"""
Test MCP connection to GitHub and JIRA servers.
Run this after setting up MCP to verify everything works.
"""

import os
from ingestion.mcp_client import MCPClient


def test_github_mcp():
    """Test GitHub MCP connection."""
    print("=" * 60)
    print("Testing GitHub MCP Connection")
    print("=" * 60)

    client = MCPClient()

    if not client.is_github_available():
        print("❌ GitHub MCP not available")
        print("   - Check MCP_GITHUB_ENABLED=true in .env")
        print("   - Check ~/.claude/config.json has 'github' server")
        return False

    print("✓ GitHub MCP server configured")

    # Try to fetch PRs from a public repo
    try:
        print("\nFetching PRs from octocat/Hello-World...")
        prs = client.fetch_github_prs("octocat", "Hello-World", state="closed", limit=5)
        print(f"✓ Successfully fetched {len(prs)} PRs")

        if prs:
            print("\nFirst PR:")
            pr = prs[0]
            print(f"  ID: {pr['id']}")
            print(f"  Title: {pr['title']}")
            print(f"  Merged: {pr['merged_at']}")
        return True

    except Exception as e:
        print(f"❌ GitHub MCP failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify GitHub token in ~/.claude/config.json")
        print("  2. Test MCP server directly:")
        print("     echo '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}' | \\")
        print("       GITHUB_TOKEN=your_token npx @modelcontextprotocol/server-github")
        return False


def test_jira_mcp():
    """Test JIRA MCP connection."""
    print("\n" + "=" * 60)
    print("Testing JIRA MCP Connection")
    print("=" * 60)

    client = MCPClient()

    if not client.is_jira_available():
        print("⚠ JIRA MCP not available (optional)")
        print("   To enable:")
        print("   - Set MCP_JIRA_ENABLED=true in .env")
        print("   - Configure 'jira' server in ~/.claude/config.json")
        return None

    print("✓ JIRA MCP server configured")

    # Try to fetch a JIRA issue (you'll need to provide a real issue key)
    issue_key = os.getenv("TEST_JIRA_ISSUE", "TEST-123")
    print(f"\nAttempting to fetch issue {issue_key}...")
    print("(Set TEST_JIRA_ISSUE env var to test a real issue)")

    try:
        issues = client.fetch_jira_issues([issue_key])
        if issues:
            issue = issues[0]
            print("✓ Successfully fetched issue")
            print(f"  Key: {issue['key']}")
            print(f"  Title: {issue['title']}")
            print(f"  Status: {issue['status']}")
            return True
    except Exception as e:
        print(f"❌ JIRA MCP failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify JIRA credentials in ~/.claude/config.json")
        print("  2. Check JIRA MCP server is running")
        print("  3. Verify JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        return False


def print_configuration():
    """Print current configuration."""
    print("\n" + "=" * 60)
    print("Current Configuration")
    print("=" * 60)

    # Read .env
    github_enabled = os.getenv("MCP_GITHUB_ENABLED", "false")
    jira_enabled = os.getenv("MCP_JIRA_ENABLED", "false")
    repos = os.getenv("GITHUB_REPOS", "")

    print(f"MCP GitHub: {github_enabled}")
    print(f"MCP JIRA: {jira_enabled}")
    print(f"Repositories: {repos if repos else 'Not configured'}")

    # Check config file
    from pathlib import Path
    import json

    config_path = Path.home() / ".claude" / "config.json"
    if config_path.exists():
        print(f"\n✓ MCP config found: {config_path}")
        try:
            with open(config_path) as f:
                config = json.load(f)
                servers = config.get("mcpServers", {})
                print(f"  Configured servers: {', '.join(servers.keys())}")
        except Exception as e:
            print(f"  ⚠ Failed to read config: {e}")
    else:
        print(f"\n❌ MCP config not found: {config_path}")
        print("   Run: ./setup_mcp.sh")


def main():
    """Run all tests."""
    from dotenv import load_dotenv

    load_dotenv()

    print("\n" + "=" * 60)
    print("MCP Connection Test")
    print("=" * 60)

    print_configuration()

    github_ok = test_github_mcp()
    jira_ok = test_jira_mcp()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if github_ok:
        print("✓ GitHub MCP: Working")
    else:
        print("❌ GitHub MCP: Failed")

    if jira_ok is True:
        print("✓ JIRA MCP: Working")
    elif jira_ok is False:
        print("❌ JIRA MCP: Failed")
    else:
        print("⚠ JIRA MCP: Not configured")

    print("\nNext steps:")
    if github_ok:
        print("  ✓ You're ready to run: python main.py")
    else:
        print("  1. Run: ./setup_mcp.sh")
        print("  2. Or follow: QUICK_START_MCP.md")

    print("=" * 60)


if __name__ == "__main__":
    main()
