"""ADR (Architecture Decision Record) generator."""

from typing import Any
from structuring.feature_builder import Feature


def generate_adr(feature: Feature, llm_client: Any = None) -> str:
    """
    Generate ADR from feature context.

    Uses prompt from PROMPT_LIBRARY.md (ADR Generation Agent).

    Output format:
    # ADR: <Title>

    ## Context
    <brief context>

    ## Decision
    <explicit architectural decision>

    ## Alternatives Considered
    <bullet list>

    ## Consequences
    <positive and negative impacts>

    ## Related Features
    <feature_id>
    """
    # TODO: Implement ADR generation with LLM
    return ""


def build_adr_prompt(feature: Feature) -> str:
    """Build ADR generation prompt from feature data."""
    # TODO: Implement prompt construction
    return ""
