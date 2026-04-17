"""Main entry point for the agentic documentation system with multi-repo support."""

import os
from dotenv import load_dotenv
from orchestrator.pipeline import run_pipeline


def main():
    """Run the full multi-repo pipeline."""
    load_dotenv()

    # Get repository list from env
    repos_str = os.getenv("GITHUB_REPOS", "example-org/repo1,example-org/repo2")
    repos = [r.strip() for r in repos_str.split(",") if r.strip()]

    # MCP configuration
    use_mcp = os.getenv("MCP_GITHUB_ENABLED", "true").lower() == "true"
    github_mcp = os.getenv("MCP_GITHUB_SERVER", "github")
    jira_mcp = os.getenv("MCP_JIRA_SERVER", "jira")

    # Fallback tokens
    github_token = os.getenv("GITHUB_TOKEN")
    jira_token = os.getenv("JIRA_API_TOKEN")

    print("=" * 80)
    print("Multi-Repository Agentic Documentation Pipeline")
    print("=" * 80)
    print(f"Repositories ({len(repos)}):")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo}")
    print()
    print(f"Data Source: {'MCP Servers' if use_mcp else 'Direct API'}")
    if use_mcp:
        print(f"  - GitHub MCP: {github_mcp}")
        print(f"  - JIRA MCP: {jira_mcp}")
    else:
        print(f"  - GitHub Token: {'✓' if github_token else '✗'}")
        print(f"  - JIRA Token: {'✓' if jira_token else '✗'}")
    print("=" * 80)
    print()

    result = run_pipeline(
        repos=repos, github_token=github_token, jira_token=jira_token, use_mcp=use_mcp
    )

    print()
    print("=" * 80)
    print(f"Pipeline Status: {result.get('status', 'unknown').upper()}")
    print("=" * 80)

    if result.get("status") == "success":
        outputs = result.get("outputs", {})
        print(f"✓ Repositories processed: {outputs.get('repos_processed', 0)}")
        print(f"✓ PRs processed: {outputs.get('prs_count', 0)}")
        print(f"✓ JIRA issues fetched: {outputs.get('jira_count', 0)}")
        print(f"✓ Features built: {outputs.get('features_count', 0)}")
        print(f"✓ Validation score: {result.get('validation_score')}%")
    else:
        print("✗ Pipeline failed")
        if result.get("issues"):
            print(f"✗ Issues found: {len(result['issues'])}")
            for issue in result.get("issues", []):
                print(f"  - {issue.get('type')}: {issue.get('description')}")

    print("=" * 80)

    return result


if __name__ == "__main__":
    main()
