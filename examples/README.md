# MCP Integration Examples

This directory contains example code and configurations for integrating MCP servers with the agent-knowledge-system.

## Files

### `simple_mcp_integration.py`
Standalone example showing different approaches to MCP integration:
- **Approach 1**: Direct subprocess calls (simplest)
- **Approach 2**: Configuration-based client (recommended)
- Examples for single-repo, multi-repo, and JIRA fetching

**Run it:**
```bash
python examples/simple_mcp_integration.py
```

### `claude_config_example.json`
Example `~/.claude/config.json` configuration showing:
- GitHub MCP server setup
- JIRA MCP server setup
- Filesystem MCP server (bonus)
- PostgreSQL MCP server (bonus)

**Use it:**
```bash
# Copy to Claude config location
cp examples/claude_config_example.json ~/.claude/config.json

# Edit with your tokens
nano ~/.claude/config.json
```

## Quick Test

### Test GitHub MCP Server

```bash
# 1. Install MCP server
npm install -g @modelcontextprotocol/server-github

# 2. Test it works
export GITHUB_TOKEN=ghp_your_token_here
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  npx @modelcontextprotocol/server-github
```

### Test Python Integration

```python
from examples.simple_mcp_integration import SimpleMCPClient

# Create client (reads from ~/.claude/config.json)
client = SimpleMCPClient()

# Fetch PRs
prs = client.fetch_github_prs("octocat", "Hello-World")
print(f"Fetched {len(prs)} PRs")

# Fetch JIRA issue
issue = client.fetch_jira_issue("PROJ-123")
print(f"Issue: {issue['title']}")
```

## Integration Approaches

### 1. Subprocess (Simplest)
**Pros**: No dependencies, easy to understand  
**Cons**: No connection reuse, synchronous only  
**Best for**: Quick prototypes, simple scripts

```python
from examples.simple_mcp_integration import fetch_prs_simple
prs = fetch_prs_simple("owner", "repo")
```

### 2. Config-Based Client (Recommended)
**Pros**: Reusable, follows standards, easy to configure  
**Cons**: Still synchronous  
**Best for**: Production use, multiple servers

```python
from examples.simple_mcp_integration import SimpleMCPClient
client = SimpleMCPClient()
prs = client.fetch_github_prs("owner", "repo")
```

### 3. Async SDK (Most Powerful)
**Pros**: Async, connection pooling, full featured  
**Cons**: More complex, requires async/await  
**Best for**: High-performance, many concurrent requests

See `MCP_INTEGRATION_GUIDE.md` for full async example.

## Available MCP Servers

### Official Servers

| Server | Package | Use Case |
|--------|---------|----------|
| GitHub | `@modelcontextprotocol/server-github` | PRs, issues, repos |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File operations |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Database queries |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | Web scraping |

### Community Servers

| Server | Use Case |
|--------|----------|
| JIRA | Issue tracking |
| Confluence | Documentation |
| Slack | Messaging |
| Linear | Project management |

## Testing Your Integration

### 1. Test MCP Server Directly

```bash
# List available tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  GITHUB_TOKEN=$GITHUB_TOKEN npx @modelcontextprotocol/server-github

# Call a tool
echo '{
  "jsonrpc":"2.0",
  "id":1,
  "method":"tools/call",
  "params":{
    "name":"github_list_pulls",
    "arguments":{"owner":"octocat","repo":"Hello-World","state":"closed"}
  }
}' | GITHUB_TOKEN=$GITHUB_TOKEN npx @modelcontextprotocol/server-github
```

### 2. Test Python Client

```bash
# Run example
python examples/simple_mcp_integration.py

# Should output:
# === Simple MCP Usage ===
# Fetched 10 PRs
#   - #1: First PR
#   - #2: Second PR
```

### 3. Test Full Pipeline

```bash
# Configure
export GITHUB_REPOS=octocat/Hello-World
export MCP_GITHUB_ENABLED=true

# Run
python main.py
```

## Common Issues

### "MCP server not found"
```bash
# Reinstall globally
npm install -g @modelcontextprotocol/server-github

# Or use npx to auto-install
npx -y @modelcontextprotocol/server-github
```

### "Authentication failed"
```bash
# Check token is set
echo $GITHUB_TOKEN

# Verify token works
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### "JSON parse error"
- Check `~/.claude/config.json` is valid JSON
- Use a JSON validator: `cat ~/.claude/config.json | python -m json.tool`

### "Timeout"
- Increase timeout in subprocess calls
- Check network connectivity
- Verify server is running

## Next Steps

1. **Start Simple**: Use `simple_mcp_integration.py` to understand the basics
2. **Configure**: Set up `~/.claude/config.json` with your servers
3. **Test**: Run examples and verify they work
4. **Integrate**: Update `ingestion/mcp_client.py` with real implementation
5. **Scale**: Add more servers and repositories

## Resources

- **Quick Start**: `../QUICK_START_MCP.md`
- **Full Guide**: `../MCP_INTEGRATION_GUIDE.md`
- **MCP Docs**: https://modelcontextprotocol.io/
- **GitHub MCP**: https://github.com/modelcontextprotocol/servers
