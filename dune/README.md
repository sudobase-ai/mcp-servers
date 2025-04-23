# Dune MCP Server

## Installation

Add this server to MCP client config as
```
{
  "mcpServers": {
    "dune": {
      "command": "uv",
      "args": [
        "--directory",
        "<path to this directory>",
        "run",
        "dune"
      ],
      "env": {
        "DUNE_API_KEY": "<your dune API key>"
      }
  }
}
```

Here's a free-tier key: `DUNE_API_KEY=eJQofvYEFL2idBvNVRwhLuSQUrCtdHEi`
