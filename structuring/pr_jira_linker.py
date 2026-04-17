"""PR to JIRA linking logic."""

from typing import Dict, Any, List
import re


def link_pr_to_jira(pr_data: Dict[str, Any], jira_issues: List[Dict[str, Any]]) -> List[str]:
    """
    Link PR to JIRA issues using rule-based matching.

    Rules (POC):
    - Extract JIRA IDs from PR title/description
    - Match exact ID
    """
    linked_jira_ids = []

    # Extract JIRA IDs from PR title and description
    pr_title = pr_data.get("title", "")
    pr_description = pr_data.get("description", "")

    found_ids = set()
    found_ids.update(extract_jira_id_from_text(pr_title))
    found_ids.update(extract_jira_id_from_text(pr_description))

    # Match against available JIRA issues
    available_jira_ids = {issue.get("id") for issue in jira_issues if issue.get("id")}

    # Return intersection of found IDs and available issues
    linked_jira_ids = list(found_ids.intersection(available_jira_ids))

    return linked_jira_ids


def extract_jira_id_from_text(text: str) -> List[str]:
    """Extract JIRA ticket IDs using regex (e.g., ABC-123)."""
    pattern = r"[A-Z]+-\d+"
    return re.findall(pattern, text)
