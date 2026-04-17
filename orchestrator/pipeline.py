"""Main pipeline orchestrator with multi-repo and MCP support."""

from typing import Dict, Any, Optional, List
import os
from ingestion.github_ingestor import fetch_merged_prs, extract_jira_references
from ingestion.jira_ingestor import fetch_jira_issues
from structuring.feature_builder import build_feature


def run_pipeline(
    repos: Optional[List[str]] = None,
    github_token: Optional[str] = None,
    jira_token: Optional[str] = None,
    use_mcp: bool = True,
) -> Dict[str, Any]:
    """
    Execute full agentic documentation pipeline for multiple repositories.

    Args:
        repos: List of repository names (e.g., ["org/repo1", "org/repo2"])
               If None, uses GITHUB_REPOS from env
        github_token: GitHub token (optional, used for direct API)
        jira_token: JIRA token (optional, used for direct API)
        use_mcp: Whether to use MCP for data fetching (default: True)

    Steps:
    1. Ingest GitHub + JIRA from multiple repos (extract JIRA keys from PRs)
    2. Build features
    3. Build graph
    4. Generate docs
    5. Validate everything
    6. Export outputs

    Returns:
    {
        "status": "success" | "failed",
        "validation_score": float,
        "issues": List[ValidationIssue],
        "outputs": {...}
    }
    """
    try:
        # Get repository list
        if repos is None:
            repos_str = os.getenv("GITHUB_REPOS", "")
            if repos_str:
                repos = [r.strip() for r in repos_str.split(",") if r.strip()]
            else:
                raise ValueError("No repositories specified in GITHUB_REPOS env var")

        if not repos:
            raise ValueError("Repository list is empty")

        # Step 1: Ingest data from all repos
        all_pr_data, all_jira_data = ingest_multi_repo_data(repos, use_mcp)

        # Step 2: Build features
        features = build_features(all_pr_data, all_jira_data)

        # TODO: Step 3-6 implementation
        # build_knowledge_graph()
        # generate_documentation()
        # validate_outputs()
        # export_results()

        return {
            "status": "success",
            "validation_score": 100.0,
            "issues": [],
            "outputs": {
                "agents_md": "",
                "architecture_md": "",
                "graph_path": "",
                "repos_processed": len(repos),
                "features_count": len(features),
                "prs_count": len(all_pr_data),
                "jira_count": len(all_jira_data),
            },
        }
    except Exception as e:
        return {
            "status": "failed",
            "validation_score": 0.0,
            "issues": [{"type": "pipeline_error", "description": str(e)}],
            "outputs": {"agents_md": "", "architecture_md": "", "graph_path": ""},
        }


def ingest_multi_repo_data(
    repos: List[str], use_mcp: bool = True
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Ingest GitHub and JIRA data from multiple repositories.

    Process:
    1. Fetch merged PRs from all repositories
    2. Extract JIRA keys from all PRs
    3. Fetch JIRA issues using extracted keys (deduplicated)

    Args:
        repos: List of repository names (e.g., ["org/repo1", "org/repo2"])
        use_mcp: Whether to use MCP for fetching

    Returns:
        tuple: (all_pr_data, all_jira_data)
    """
    print(f"  1. Fetching PRs from {len(repos)} repository(ies)...")

    all_prs = []
    all_jira_keys = set()

    # Fetch PRs from each repository
    for repo in repos:
        if "/" in repo:
            repo_owner, repo_name = repo.split("/", 1)
        else:
            print(f"     [WARNING] Invalid repo format: {repo}, skipping")
            continue

        print(f"     - {repo_owner}/{repo_name}...")
        try:
            prs = fetch_merged_prs(repo_owner, repo_name, use_mcp=use_mcp)
            all_prs.extend(prs)
            print(f"       Found {len(prs)} PRs")
        except Exception as e:
            print(f"       [ERROR] Failed to fetch PRs: {e}")
            continue

    print(f"     Total PRs fetched: {len(all_prs)}")

    # Extract all JIRA keys from all PRs
    print("  2. Extracting JIRA keys from all PRs...")
    for pr in all_prs:
        keys = extract_jira_references(pr)
        all_jira_keys.update(keys)

    print(f"     Found {len(all_jira_keys)} unique JIRA keys: {sorted(all_jira_keys)}")

    # Fetch JIRA issues using extracted keys
    if all_jira_keys:
        print(
            "  3. Fetching JIRA issues via MCP..." if use_mcp else "  3. Fetching JIRA issues..."
        )
        try:
            jira_data = fetch_jira_issues(list(all_jira_keys), use_mcp=use_mcp)
            print(f"     Fetched {len(jira_data)} JIRA issues")
        except Exception as e:
            print(f"     [ERROR] Failed to fetch JIRA issues: {e}")
            jira_data = []
    else:
        print("  3. No JIRA keys found, skipping JIRA fetch")
        jira_data = []

    return all_prs, jira_data


def build_features(
    pr_data: List[Dict[str, Any]], jira_data: List[Dict[str, Any]]
) -> List[Any]:
    """
    Build feature objects from PR and JIRA data.

    In multi-repo scenarios, features may span multiple repositories.
    """
    print("  4. Building features from multi-repo data...")

    if not pr_data:
        print("     No PRs available, skipping feature building")
        return []

    # Group PRs by repository
    repos_map: Dict[str, List[Dict[str, Any]]] = {}
    for pr in pr_data:
        repo = pr.get("repo", "unknown")
        if repo not in repos_map:
            repos_map[repo] = []
        repos_map[repo].append(pr)

    # For POC, build one feature per repository
    # In production, this would group related PRs/JIRAs into features
    # potentially spanning multiple repos
    features = []
    for repo, prs in repos_map.items():
        print(f"     Building feature for {repo} ({len(prs)} PRs)...")
        feature = build_feature(prs, jira_data)
        features.append(feature)

    print(f"     Built {len(features)} feature(s) across {len(repos_map)} repo(s)")
    return features


def build_knowledge_graph() -> None:
    """Step 3: Construct knowledge graph."""
    pass


def generate_documentation() -> None:
    """Step 4: Generate ADRs and execution plans."""
    pass


def validate_outputs() -> None:
    """Step 5: Run validation checks."""
    pass


def export_results() -> None:
    """Step 6: Export final documentation."""
    pass
