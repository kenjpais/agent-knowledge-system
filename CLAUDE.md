# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agentic documentation system that ingests GitHub PRs and JIRA issues, constructs a knowledge graph, and generates navigable documentation (ADRs, execution plans, AGENTS.md, ARCHITECTURE.md) using LLM-based agents.

**Core principle**: The knowledge graph is the source of truth. All documentation is derived from and navigable through the graph.

## Environment Setup

Install dependencies:
```bash
pip install -e .
# Or for development with linting tools:
pip install -e ".[dev]"
```

Required environment variables in `.env`:
```bash
# Multi-Repo Configuration (comma-separated)
GITHUB_REPOS=org1/repo1,org1/repo2,org2/repo3

# MCP Server Configuration
MCP_GITHUB_ENABLED=true
MCP_GITHUB_SERVER=github
MCP_JIRA_ENABLED=true
MCP_JIRA_SERVER=jira

# Fallback: Direct API Configuration (if MCP not available)
GITHUB_TOKEN=your-github-token
JIRA_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-jira-token

# LLM Configuration
GEMINI_API_KEY=your-gemini-api-key  # For doc generation
```

## Development Commands

**Run the full pipeline:**
```bash
python main.py
```

**Run tests:**
```bash
pytest                          # All tests
pytest tests/test_graph.py      # Single test file
pytest -k test_node_creation    # Single test by name
pytest -v --tb=short            # Verbose with short traceback
```

**Linting and formatting:**
```bash
black .                         # Format code (line length 100)
ruff check .                    # Lint code
mypy .                          # Type checking
```

## Architecture

### Pipeline Flow (Strict Execution Order)

1. **Multi-Repo Ingestion** → Fetch data from multiple repositories via MCP
   - Process multiple repositories in parallel (configured via `GITHUB_REPOS`)
   - Fetch merged PRs from all repositories via GitHub MCP server
   - Extract JIRA keys (e.g., ABC-123) from PR titles and descriptions using regex
   - Deduplicate JIRA keys across all repositories
   - Fetch JIRA issues via JIRA MCP server using extracted keys
2. **Structuring** → Link PRs to JIRAs, build Feature objects per repository
3. **Graph Building** → Convert Features into knowledge graph (nodes + edges)
4. **Generation** → LLM creates ADRs, execution plans, AGENTS.md, ARCHITECTURE.md
5. **Retrieval** → Graph-based querying with ≤3 hop traversal
6. **Validation** → Schema validation, graph integrity checks, doc completeness (blocking gate)

### Core Data Contracts

All schemas are defined using Pydantic in their respective modules:

**Feature** (`structuring/feature_builder.py`): Core unit representing linked PR + JIRA
- `feature_id`, `summary`, `problem_statement`, `solution_summary`
- `pr_ids[]`, `jira_ids[]`, `components[]`, `decisions[]`
- `exec_scope`, `incomplete_feature`

**Node** (`graph/schema.py`): Knowledge graph node
- Types: `Document`, `Section`, `Concept`, `Workflow`, `ADR`, `ExecutionPlan`, `EntryPoint`
- Fields: `id`, `type`, `title`, `file_path`, `metadata`

**Edge** (`graph/schema.py`): Knowledge graph edge
- Types: `CONTAINS`, `NEXT`, `DEEP_DIVE`, `RELATED`, `DECIDED_BY`, `PLANNED_IN`, `REFERENCES`, `INDEXES`
- Fields: `from_node`, `to_node`, `type`

### Module Responsibilities

- **ingestion/**: Multi-repo GitHub/JIRA data fetching via MCP, repo file scanning
  - `mcp_client.py` - MCP (Model Context Protocol) client for GitHub and JIRA servers
  - `github_ingestor.py` - GitHub PR fetching with MCP support
  - `jira_ingestor.py` - JIRA issue fetching with MCP support
- **structuring/**: PR↔JIRA linking, Feature object construction per repository
- **graph/**: Schema definitions, graph builder, JSON persistence (NetworkX backend)
- **generation/**: LLM prompts and generators for ADRs, execution plans, AGENTS.md
- **retrieval/**: Graph traversal, node resolution, ranking, context bundling (≤700 lines)
- **validation/**: Schema validation, graph integrity (no orphans, ≤3-hop reachability), doc completeness
- **orchestrator/**: Multi-repo pipeline runner, request routing
- **storage/**: Optional SQLite metadata store

## Critical Design Rules

1. **Graph is source of truth**: Documentation never defines structure; graph does
2. **Retrieval agent is only access path**: No direct repo scanning in generation agents
3. **≤3 hop constraint**: All nodes must be reachable from AGENTS.md within 3 hops; retrieval queries limited to 3-hop traversal
4. **Validation is blocking**: Invalid output cannot be written to docs; validation loop runs up to 3 iterations
5. **Deterministic graph construction preferred**: Avoid LLM-based graph building in POC; use rule-based approach
6. **No hallucination**: All generated content must be grounded in input data (PRs, JIRAs, Features)
7. **Schema enforcement**: All agents must produce strictly conforming Pydantic-validated outputs

## LLM Agent Usage

When invoking Gemini API (via `google-generativeai`):
- Use prompts from `PROMPT_LIBRARY.md` or `generation/doc_prompts.py`
- Enforce global prompt rules (see PROMPT_LIBRARY.md section 0)
- All outputs must be JSON (for structured data) or Markdown (for docs)
- No chain-of-thought in outputs; structured results only

**Agent types and their schemas:**
- Feature Builder → Feature JSON
- ADR Generator → Markdown with strict template
- Execution Plan Generator → Markdown with strict template
- Retrieval Agent → JSON with visited_path, selected_nodes, context_bundle
- Validation Agent → JSON with valid, score, issues[], recommendations[]

## Testing Strategy

**Unit tests**: Individual component logic (ingestion parsing, node creation)
**Integration tests**: Full flows (GitHub → Feature → Graph → ADR)
**Graph tests**: No orphan nodes, AGENTS.md reachability
**Retrieval tests**: Query correctness within 3-hop constraint
**Validation tests**: Schema rejection, loop termination

## Output Artifacts

After pipeline completion:
- `graph_store/graph.json` - Serialized knowledge graph
- `docs_output/AGENTS.md` - Central navigation document (entry point)
- `docs_output/ARCHITECTURE.md` - System architecture (graph-derived)
- `docs_output/agentic/decisions/*.md` - Architecture Decision Records
- `docs_output/agentic/exec-plans/active/*.md` - Execution plans

## Common Gotchas

- **Multi-repo processing**: The pipeline processes multiple repositories in a single run (configured via `GITHUB_REPOS` env var). PRs are fetched from all repos, JIRA keys are deduplicated across repos, and features are built per repository.
- **MCP-first approach**: Data fetching prioritizes MCP servers (GitHub MCP, JIRA MCP). If MCP is not available, falls back to mock data. Direct API integration is planned for future.
- **JIRA extraction flow**: JIRA issues are NOT fetched independently. The pipeline first fetches PRs from all repos, extracts JIRA keys from PR titles/descriptions (e.g., "ABC-123", "XYZ-456"), deduplicates across repos, then fetches only those JIRA issues once.
- **JIRA deduplication**: If multiple repos reference the same JIRA issue (e.g., ABC-123), it's only fetched once and shared across features.
- **Incomplete features**: If PR has no linked JIRA or vice versa, mark `incomplete_feature=True` but still process
- **Graph orphans**: Validation will reject graphs with unreachable nodes
- **Context size**: Retrieval context bundles must be ≤700 lines to fit LLM context windows
- **Edge types matter**: Use correct edge type for relationships (e.g., DECIDED_BY for Concept→ADR, not RELATED)
- **AGENTS.md is EntryPoint node**: It's not just a file; it's a graph node with INDEXES edges to all major concepts
- **Mock data**: If MCP servers are not configured, the system uses mock data for testing
