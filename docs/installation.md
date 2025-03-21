# Installation Guide

This guide will help you install and set up the Elfa MCP server on your system.

## Prerequisites

Before installing the Elfa MCP server, ensure you have:

1. **Python 3.10 or higher** installed on your system
2. **An Elfa API key** - Get one from [dev.elfa.ai](https://elfa.ai)
3. **Claude Desktop** (or another MCP client) installed

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The simplest way to install is using pip:

```bash
pip install elfa-mcp
```

### Method 2: Install from Source

For the latest development version:

```bash
git clone https://github.com/elfa-ai/elfa-mcp.git
cd elfa-mcp/python
pip install -e .
```

## Configuration

### Setting up with Claude Desktop

1. Create or edit your Claude Desktop configuration file:
   * macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   * Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the Elfa MCP server configuration:

```json
{
  "mcpServers": {
    "elfa": {
      "command": "python",
      "args": ["-m", "elfa_mcp.server"],
      "env": {
        "ELFA_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

3. Restart Claude Desktop

## Verifying Installation

1. Open Claude Desktop
2. Look for the hammer icon in the bottom right of the input box
3. Click it to see the available tools from the Elfa MCP server
4. Try a query like "What are the trending tokens in the last 24 hours?"

## Troubleshooting

### Common Issues

1. **API Key Invalid**: Ensure your API key is correct and has not expired
2. **Server Not Found**: Check that the path to the server module is correct
3. **Connection Issues**: Verify Claude Desktop is correctly configured

### Getting Logs

To debug issues, you can check the MCP logs:

* macOS: `~/Library/Logs/Claude/mcp*.log`
* Windows: `%APPDATA%\Claude\logs\mcp*.log`

For additional help, check the GitHub repository or open an issue.