# Elfa MCP Server

A Model Context Protocol (MCP) server for integrating the Elfa API with LLM applications like Claude Desktop.

## Features

This MCP server provides tools for:

- Getting API key status and usage information
- Finding tweets with significant smart engagement
- Searching for mentions of specific tokens or keywords
- Discovering trending tokens and their performance
- Analyzing Twitter account stats and engagement metrics

## Installation

### Prerequisites

- Python 3.10 or higher
- An Elfa API key (get one at [elfa.ai](https://elfa.ai))

### Install via pip

```bash
pip install elfa-mcp
```

## Docker Usage

The Elfa MCP server can be run in a Docker container for easier deployment and isolation.

### Building the Docker image

```bash
docker build -t elfa-mcp .
```

### Running with Docker

```bash
docker run -e ELFA_API_KEY=your-api-key-here -it elfa-mcp
```

### Using Docker Compose

1. Create a .env file with your API key:

```
ELFA_API_KEY=your-api-key-here
```

2. Run the container

```bash
docker-compose up
```

### With Claude Desktop

1. Create or edit your Claude Desktop configuration file:

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

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

### From command line

You can also run the server directly:

```bash
ELFA_API_KEY=your-api-key-here elfa-mcp
```

## Available Tools

- `get_api_key_info` - Check your API key status and usage
- `get_smart_engagement_mentions` - Find tweets with significant engagement
- `get_top_ticker_mentions` - Get top mentions for a specific ticker
- `search_keyword_mentions` - Search for mentions containing specific keywords
- `get_trending_tokens` - Find trending tokens by mention count
- `get_account_stats` - Analyze Twitter account engagement metrics
