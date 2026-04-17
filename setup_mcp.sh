#!/bin/bash

# MCP Setup Script - Easiest approach
# This script sets up GitHub and JIRA MCP servers

set -e

echo "=========================================="
echo "MCP Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "1. Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js not found${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ npm found: $(npm --version)${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

echo ""
echo "2. Installing GitHub MCP Server..."
npm install -g @modelcontextprotocol/server-github
echo -e "${GREEN}✓ GitHub MCP server installed${NC}"

echo ""
echo "3. Creating Claude Desktop configuration directory..."
mkdir -p ~/.claude
echo -e "${GREEN}✓ Directory created${NC}"

echo ""
echo "=========================================="
echo "Configuration Required"
echo "=========================================="
echo ""
echo "Please provide the following information:"
echo ""

# Get GitHub token
read -p "Enter your GitHub Personal Access Token (ghp_...): " GITHUB_TOKEN
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠ No GitHub token provided. You'll need to add it manually.${NC}"
    GITHUB_TOKEN="YOUR_GITHUB_TOKEN_HERE"
fi

# Ask about JIRA
echo ""
read -p "Do you want to configure JIRA MCP? (y/n): " SETUP_JIRA

if [ "$SETUP_JIRA" = "y" ] || [ "$SETUP_JIRA" = "Y" ]; then
    read -p "Enter JIRA URL (https://your-domain.atlassian.net): " JIRA_URL
    read -p "Enter JIRA Email: " JIRA_EMAIL
    read -p "Enter JIRA API Token: " JIRA_TOKEN
    read -p "Path to JIRA MCP server script (or press Enter to skip): " JIRA_SCRIPT

    if [ -z "$JIRA_SCRIPT" ]; then
        echo -e "${YELLOW}⚠ JIRA MCP server script not provided. You'll need to set it up manually.${NC}"
        SETUP_JIRA="n"
    fi
fi

echo ""
echo "4. Creating MCP configuration..."

# Create config.json
if [ "$SETUP_JIRA" = "y" ] || [ "$SETUP_JIRA" = "Y" ]; then
    cat > ~/.claude/config.json << EOF
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      }
    },
    "jira": {
      "command": "python",
      "args": [
        "$JIRA_SCRIPT"
      ],
      "env": {
        "JIRA_URL": "$JIRA_URL",
        "JIRA_EMAIL": "$JIRA_EMAIL",
        "JIRA_API_TOKEN": "$JIRA_TOKEN"
      }
    }
  }
}
EOF
else
    cat > ~/.claude/config.json << EOF
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
EOF
fi

echo -e "${GREEN}✓ Configuration created at ~/.claude/config.json${NC}"

echo ""
echo "5. Creating project .env file..."

# Get repo list
read -p "Enter repository names (comma-separated, e.g., org/repo1,org/repo2): " REPOS
if [ -z "$REPOS" ]; then
    REPOS="octocat/Hello-World"
fi

cat > .env << EOF
# Multi-Repo Configuration
GITHUB_REPOS=$REPOS

# MCP Server Configuration
MCP_GITHUB_ENABLED=true
MCP_GITHUB_SERVER=github
EOF

if [ "$SETUP_JIRA" = "y" ] || [ "$SETUP_JIRA" = "Y" ]; then
    cat >> .env << EOF
MCP_JIRA_ENABLED=true
MCP_JIRA_SERVER=jira
EOF
else
    cat >> .env << EOF
MCP_JIRA_ENABLED=false
MCP_JIRA_SERVER=jira
EOF
fi

cat >> .env << EOF

# Fallback tokens (if MCP not available)
GITHUB_TOKEN=$GITHUB_TOKEN
EOF

if [ "$SETUP_JIRA" = "y" ] || [ "$SETUP_JIRA" = "Y" ]; then
    cat >> .env << EOF
JIRA_URL=$JIRA_URL
JIRA_EMAIL=$JIRA_EMAIL
JIRA_API_TOKEN=$JIRA_TOKEN
EOF
fi

echo -e "${GREEN}✓ .env file created${NC}"

echo ""
echo "6. Testing MCP connection..."
echo ""

# Test GitHub MCP
echo "Testing GitHub MCP server..."
if echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | GITHUB_TOKEN="$GITHUB_TOKEN" npx -y @modelcontextprotocol/server-github > /dev/null 2>&1; then
    echo -e "${GREEN}✓ GitHub MCP server is working!${NC}"
else
    echo -e "${YELLOW}⚠ GitHub MCP server test failed. Check your token.${NC}"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install project dependencies:"
echo "   pip install -e ."
echo ""
echo "2. Test the integration:"
echo "   python examples/simple_mcp_integration.py"
echo ""
echo "3. Run the pipeline:"
echo "   python main.py"
echo ""
echo "Configuration files created:"
echo "  - ~/.claude/config.json (MCP server config)"
echo "  - .env (project configuration)"
echo ""
echo "To update tokens later, edit ~/.claude/config.json"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
