"""Feature object builder from PR and JIRA data."""

from typing import Dict, Any, List
from pydantic import BaseModel


class Feature(BaseModel):
    """Core Feature object schema."""

    feature_id: str
    summary: str
    problem_statement: str
    solution_summary: str
    pr_ids: List[str]
    jira_ids: List[str]
    components: List[str]
    decisions: List[str]
    exec_scope: str
    incomplete_feature: bool = False


def build_feature(pr_data: List[Dict[str, Any]], jira_data: List[Dict[str, Any]]) -> Feature:
    """
    Convert linked PR + JIRA data into a Feature object.

    Ensures:
    - Every feature has at least 1 PR and 1 JIRA (if possible)
    - Marks incomplete_feature = True if missing data
    """
    # Extract PR IDs
    pr_ids = [pr.get("id", "") for pr in pr_data if pr.get("id")]

    # Extract JIRA IDs
    jira_ids = [jira.get("id", "") for jira in jira_data if jira.get("id")]

    # Check if feature is incomplete
    incomplete = len(pr_ids) == 0 or len(jira_ids) == 0

    # Build summary from PR titles
    pr_titles = [pr.get("title", "") for pr in pr_data if pr.get("title")]
    summary = pr_titles[0] if pr_titles else "Untitled feature"

    # Extract problem statement from JIRA
    jira_descriptions = [j.get("description", "") for j in jira_data if j.get("description")]
    problem_statement = jira_descriptions[0] if jira_descriptions else "No problem statement"

    # Extract solution from PR descriptions
    pr_descriptions = [pr.get("description", "") for pr in pr_data if pr.get("description")]
    solution_summary = pr_descriptions[0] if pr_descriptions else "No solution description"

    # Generate feature ID
    feature_id = f"feature-{pr_ids[0] if pr_ids else 'unknown'}"

    # Extract components (placeholder logic)
    components = []
    for pr in pr_data:
        files_changed = pr.get("files_changed", [])
        for file_path in files_changed:
            if isinstance(file_path, str) and "/" in file_path:
                component = file_path.split("/")[0]
                if component not in components:
                    components.append(component)

    return Feature(
        feature_id=feature_id,
        summary=summary[:200],  # Limit length
        problem_statement=problem_statement[:500],
        solution_summary=solution_summary[:500],
        pr_ids=pr_ids,
        jira_ids=jira_ids,
        components=components[:10],  # Limit to 10 components
        decisions=[],  # To be filled by analysis
        exec_scope="minor" if len(pr_ids) == 1 else "major",
        incomplete_feature=incomplete,
    )
