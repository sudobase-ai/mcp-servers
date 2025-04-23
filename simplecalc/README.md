# calculator-mcp MCP server

A toy MCP calculator server, exposing `add`, `sub`, `mul`, and `divide` tools.


## Quickstart

### HTTP Server
Create python venv if necessary
```
python3 -m venv env
. env/bin/activate
pip install -e .
```

Start an HTTP server locally (`http://127.0.0.1:8000/sse`):
```
python src/calculator_mcp/server.py --sse
```

### Claude Desktop
To use this server directly (without MCPPro) from Claude desktop, add the following to your Claude desktop config (located at `~/Library/Application\ Support/Claude/claude_desktop_config.json` on Mac)
```
{
    "mcpServers": {
        "simplecalc": {
            "command": "uv",
            "args": [
              "--directory",
              "<path_to_this_directory>",
              "run",
              "simplecalc"
            ]
        }
    }
}
```
