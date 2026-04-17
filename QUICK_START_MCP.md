# Quick Start: MCP Integration

This guide will get you up and running with MCP in 10 minutes.

## Prerequisites

- Node.js 18+ installed
- Python 3.11+ installed
- GitHub Personal Access Token
- JIRA API Token (if using JIRA)

## Step 1: Install MCP Servers (2 minutes)

```bash
# Install GitHub MCP server globally
npm install -g @modelcontextprotocol/server-github

# Verify installation
npx @modelcontextprotocol/server-github --help
```

## Step 2: Configure Claude Desktop (3 minutes)

Create or edit `~/.claude/config.json`:

```bash
mkdir -p ~/.claude
```

Add this configuration (replace tokens):

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_YOUR_GITHUB_TOKEN_HERE"
      }
    }
  }
}
```

**Get a GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo`, `read:org`
4. Copy token and paste above

## Step 3: Test MCP Connection (2 minutes)

```bash
# Test GitHub MCP server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  GITHUB_TOKEN=ghp_YOUR_TOKEN npx @modelcontextprotocol/server-github
```

You should see a list of available tools.

## Step 4: Update Your Project Configuration (1 minute)

Create `.env` file in your project:

```bash
# Multi-repo configuration
GITHUB_REPOS=octocat/Hello-World,your-org/your-repo

# Enable MCP
MCP_GITHUB_ENABLED=true
MCP_GITHUB_SERVER=github
```

## Step 5: Run the Pipeline (2 minutes)

```bash
# Install project dependencies
pip install -e .

# Run the pipeline
python main.py
```

You should see:

```
Multi-Repository Agentic Documentation Pipeline
Data Source: MCP Servers
  - GitHub MCP: github

  1. Fetching PRs from 2 repository(ies)...
     - octocat/Hello-World...
     Using GitHub MCP server...
     Found X PRs
```

## Troubleshooting

### "MCP server not found"
```bash
# Reinstall
npm install -g @modelcontextprotocol/server-github
```

### "Authentication failed"
```bash
# Verify token works
curl -H "Authorization: token ghp_YOUR_TOKEN" https://api.github.com/user
```

### "Command not found: npx"
```bash
# Install Node.js from https://nodejs.org/
node --version  # Should be 18+
```

### Still not working?
- Check `~/.claude/config.json` syntax (valid JSON)
- Ensure GITHUB_TOKEN has correct permissions
- Try running with `--verbose` flag for debug logs

## Next Steps

1. **Add JIRA**: See `MCP_INTEGRATION_GUIDE.md` for JIRA setup
2. **Customize**: Modify `ingestion/mcp_client.py` for your needs
3. **Scale**: Add more repositories to `GITHUB_REPOS`
4. **Monitor**: Check logs in `~/.claude/logs/`

## Example Output

When working correctly, you'll see:

```
================================================================================
Multi-Repository Agentic Documentation Pipeline
================================================================================
Repositories (2):
  1. octocat/Hello-World
  2. your-org/your-repo

Data Source: MCP Servers
  - GitHub MCP: github
================================================================================

  1. Fetching PRs from 2 repository(ies)...
     - octocat/Hello-World...
     Using GitHub MCP server...
       Found 15 PRs
     - your-org/your-repo...
     Using GitHub MCP server...
       Found 23 PRs
     Total PRs fetched: 38
     
  2. Extracting JIRA keys from all PRs...
     Found 12 unique JIRA keys
     
  3. Fetching JIRA issues via MCP...
     Fetched 12 JIRA issues
     
  4. Building features...
     Built 2 feature(s)

Pipeline Status: SUCCESS
✓ Repositories processed: 2
✓ PRs processed: 38
✓ JIRA issues fetched: 12
✓ Features built: 2
```

## Getting Help

- Full guide: `MCP_INTEGRATION_GUIDE.md`
- Examples: `examples/simple_mcp_integration.py`
- MCP Docs: https://modelcontextprotocol.io/
