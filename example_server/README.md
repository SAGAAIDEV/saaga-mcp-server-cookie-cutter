# Example Server

Example MCP server showcasing SAAGA decorator patterns

## Features

<!-- DEVELOPER NOTE: Update this section to describe what YOUR server does -->

This MCP server provides tools for:
- Text echoing and manipulation
- Time and date operations  
- Random number generation
- Fibonacci calculations
- Heavy computation simulation
- Batch data processing with parallelization
## Installation

### Quick Setup for Claude Desktop

1. Open Claude Desktop settings
2. Navigate to Developer → Model Context Protocol
3. Add this server configuration:

```json
{
  "example_server": {
    "command": "uv",
    "args": ["run", "python", "-m", "example_server.server.app"],
    "cwd": "/Users/timkitchens/projects/client-repos/saaga-mcp-server-cookie-cutter/example_server"
  }
}
```

4. Restart Claude Desktop

### For Other MCP Clients

#### Using UV (Recommended)
```json
{
  "example_server": {
    "command": "uv",
    "args": ["run", "python", "-m", "example_server.server.app"],
    "cwd": "/Users/timkitchens/projects/client-repos/saaga-mcp-server-cookie-cutter/example_server"
  }
}
```

#### Using Python directly
```json
{
  "example_server": {
    "command": "/Users/timkitchens/projects/client-repos/saaga-mcp-server-cookie-cutter/example_server/.venv/bin/python",
    "args": ["-m", "example_server.server.app"]
  }
}
```

### Transport Options

The server supports multiple transport protocols:

#### STDIO (Default)
Standard input/output communication. Used by Claude Desktop and most MCP clients.

```bash
python -m example_server.server.app --transport stdio
```

#### SSE (Server-Sent Events)
HTTP-based transport for web clients. Supports separate endpoints for different operations.

```bash
python -m example_server.server.app --transport sse --port 6272
```

#### Streamable HTTP (Recommended for Web)
Modern HTTP transport with unified `/mcp` endpoint. Supports both POST and GET requests with SSE streaming.

```bash
python -m example_server.server.app --transport streamable-http --port 6272
```

The Streamable HTTP transport offers:
- Single `/mcp` endpoint for all operations
- Support for JSON responses or SSE streams
- Session management and resumability
- Better performance with concurrent connections

## Available Tools

<!-- DEVELOPER NOTE: Replace this section with documentation for YOUR tools after removing examples -->

### echo_tool
Echoes back the provided text.
- **Parameters**: 
  - `text` (string): The text to echo
- **Returns**: The same text

### get_time
Gets the current time in a specified timezone.
- **Parameters**:
  - `timezone` (string, optional): Timezone name (default: "UTC")
- **Returns**: Current time in ISO format

### random_number
Generates a random number within a range.
- **Parameters**:
  - `min` (string): Minimum value
  - `max` (string): Maximum value  
- **Returns**: Random integer in range

### calculate_fibonacci
Calculates the Fibonacci sequence.
- **Parameters**:
  - `n` (string): Length of sequence to generate
- **Returns**: List of Fibonacci numbers

### simulate_heavy_computation
Simulates a computation-intensive task.
- **Parameters**:
  - `seconds` (string): Duration to simulate
- **Returns**: Completion status

### process_batch_data
Processes multiple data items in parallel.
- **Parameters**:
  - `kwargs_list` (array): List of parameter sets
- **Returns**: Results for each item
## Configuration

The server uses a configuration file located at:
- **macOS**: `~/Library/Application Support/example_server/config.yaml`
- **Linux**: `~/.local/share/example_server/config.yaml`
- **Windows**: `%APPDATA%/example_server/config.yaml`

### Configuration Options

```yaml
log_level: INFO  # Logging verbosity
log_retention_days: 30  # How long to keep logs
server_port: 6272  # Port for HTTP transport (if used)
default_transport: stdio  # Default transport protocol
streamable_http_enabled: true  # Enable Streamable HTTP transport
streamable_http_endpoint: "/mcp"  # Endpoint for Streamable HTTP
streamable_http_json_response: false  # Use JSON responses instead of SSE
```

## Admin Interface

This server includes a Streamlit admin UI for monitoring and configuration:

```bash
# Start the admin interface
uv run streamlit run example_server/ui/app.py
```

Access at http://localhost:8501

Features:
- Real-time server status monitoring
- Configuration editor with validation
- Log viewer with filtering and export
- System resource monitoring

## Logs

Server logs are stored in an SQLite database at:
- **macOS**: `~/Library/Application Support/example_server/unified_logs.db`
- **Linux**: `~/.local/share/example_server/unified_logs.db`
- **Windows**: `%APPDATA%/example_server/unified_logs.db`

## Troubleshooting

### Server not appearing in Claude Desktop
1. Check the path in your configuration is correct
2. Ensure Python 3.11 or higher is installed
3. Try using the full path to the Python executable
4. Check Claude Desktop logs for error messages

### Tools not working as expected
1. Check the server logs for error messages
2. Verify parameter types (all parameters are passed as strings)
3. Ensure the server process is running

### Connection errors
1. Restart Claude Desktop
2. Check if the server starts manually: `uv run python -m example_server.server.app`
3. Verify no other process is using the same port

## Support

For issues or questions:
- Check the logs in the platform-specific location above
- Review error messages in your MCP client
- Use the admin UI to check server status and logs
## Development

To contribute or add new tools to this server, see the [Developer Guide](DEVELOPER_GUIDE.md).

## License

[Your license here]

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Uses [SAAGA](https://github.com/SAGAAIDEV) decorator patterns
- Implements [Model Context Protocol](https://github.com/modelcontextprotocol) by Anthropic