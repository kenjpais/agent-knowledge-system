"""Execution plan generator."""

from typing import List, Optional
from structuring.feature_builder import Feature


def generate_execution_plan(feature: Feature, adr_refs: Optional[List[str]] = None) -> str:
    """
    Generate execution plan from feature.

    Output format:
    # Execution Plan: <Title>

    ## Goal
    <what is being achieved>

    ## Approach
    <high-level approach>

    ## Steps
    1. ...
    2. ...

    ## Dependencies
    - ...

    ## Risks
    - ...

    ## Rollback Plan
    - ...

    ## Related ADRs
    - <adr_ids>
    """
    # TODO: Implement execution plan generation
    return ""


def build_exec_plan_prompt(feature: Feature, adr_refs: List[str]) -> str:
    """Build execution plan prompt from feature."""
    # TODO: Implement prompt construction
    return ""
