# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Features

<!-- DEVELOPER NOTE: Update this section to describe what YOUR server does -->

This MCP server provides tools for:
{% if cookiecutter.include_example_tools == "yes" -%}
- Text echoing and manipulation
- Time and date operations  
- Random number generation
- Fibonacci calculations
- Heavy computation simulation
{% if cookiecutter.include_parallel_example == "yes" -%}
- Batch data processing with parallelization
{% endif -%}
{% else -%}
- [List your server's features here]
{% endif -%}

## Installation

### Quick Setup for Claude Desktop

1. Open Claude Desktop settings
2. Navigate to Developer → Model Context Protocol
3. Add this server configuration:

```json
{
  "{{cookiecutter.project_slug}}": {
    "command": "uv",
    "args": ["run", "python", "-m", "{{cookiecutter.project_slug}}.server.app"],
    "cwd": "/path/to/{{cookiecutter.project_slug}}"
  }
}
```

4. Restart Claude Desktop

### For Other MCP Clients

#### Using UV (Recommended)
```json
{
  "{{cookiecutter.project_slug}}": {
    "command": "uv",
    "args": ["run", "python", "-m", "{{cookiecutter.project_slug}}.server.app"],
    "cwd": "/path/to/{{cookiecutter.project_slug}}"
  }
}
```

#### Using Python directly
```json
{
  "{{cookiecutter.project_slug}}": {
    "command": "/path/to/{{cookiecutter.project_slug}}/.venv/bin/python",
    "args": ["-m", "{{cookiecutter.project_slug}}.server.app"]
  }
}
```

### Transport Options

The server supports multiple transport protocols:

#### STDIO (Default)
Standard input/output communication. Used by Claude Desktop and most MCP clients.

```bash
python -m {{cookiecutter.project_slug}}.server.app --transport stdio
```

#### SSE (Server-Sent Events)
HTTP-based transport for web clients. Supports separate endpoints for different operations.

```bash
python -m {{cookiecutter.project_slug}}.server.app --transport sse --port {{cookiecutter.server_port}}
```

#### Streamable HTTP (Recommended for Web)
Modern HTTP transport with unified `/mcp` endpoint. Supports both POST and GET requests with SSE streaming.

```bash
python -m {{cookiecutter.project_slug}}.server.app --transport streamable-http --port {{cookiecutter.server_port}}
```

The Streamable HTTP transport offers:
- Single `/mcp` endpoint for all operations
- Support for JSON responses or SSE streams
- Session management and resumability
- Better performance with concurrent connections

## Available Tools

<!-- DEVELOPER NOTE: Replace this section with documentation for YOUR tools after removing examples -->

{% if cookiecutter.include_example_tools == "yes" -%}
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

{% if cookiecutter.include_parallel_example == "yes" -%}
### process_batch_data
Processes multiple data items in parallel.
- **Parameters**:
  - `kwargs_list` (array): List of parameter sets
- **Returns**: Results for each item
{% endif -%}
{% else -%}
[Document your tools here with parameters and return values]
{% endif -%}

## Configuration

The server uses a configuration file located at:
- **macOS**: `~/Library/Application Support/{{cookiecutter.project_slug}}/config.yaml`
- **Linux**: `~/.local/share/{{cookiecutter.project_slug}}/config.yaml`
- **Windows**: `%APPDATA%/{{cookiecutter.project_slug}}/config.yaml`

### Configuration Options

```yaml
log_level: {{cookiecutter.log_level}}  # Logging verbosity
log_retention_days: {{cookiecutter.log_retention_days}}  # How long to keep logs
server_port: {{cookiecutter.server_port}}  # Port for HTTP transport (if used)
default_transport: {{cookiecutter.default_transport}}  # Default transport protocol
streamable_http_enabled: {% if cookiecutter.streamable_http_enabled == "yes" %}true{% else %}false{% endif %}  # Enable Streamable HTTP transport
streamable_http_endpoint: "{{cookiecutter.streamable_http_endpoint}}"  # Endpoint for Streamable HTTP
streamable_http_json_response: {% if cookiecutter.streamable_http_json_response == "yes" %}true{% else %}false{% endif %}  # Use JSON responses instead of SSE
```

{% if cookiecutter.include_admin_ui == "yes" -%}
## Admin Interface

This server includes a Streamlit admin UI for monitoring and configuration:

```bash
# Start the admin interface
uv run streamlit run {{cookiecutter.project_slug}}/ui/app.py
```

Access at http://localhost:8501

Features:
- Real-time server status monitoring
- Configuration editor with validation
- Log viewer with filtering and export
- System resource monitoring

{% endif -%}
## Logs

Server logs are stored in an SQLite database at:
- **macOS**: `~/Library/Application Support/{{cookiecutter.project_slug}}/unified_logs.db`
- **Linux**: `~/.local/share/{{cookiecutter.project_slug}}/unified_logs.db`
- **Windows**: `%APPDATA%/{{cookiecutter.project_slug}}/unified_logs.db`

## Troubleshooting

### Server not appearing in Claude Desktop
1. Check the path in your configuration is correct
2. Ensure Python {{cookiecutter.python_version}} or higher is installed
3. Try using the full path to the Python executable
4. Check Claude Desktop logs for error messages

### Tools not working as expected
1. Check the server logs for error messages
2. Verify parameter types (all parameters are passed as strings)
3. Ensure the server process is running

### Connection errors
1. Restart Claude Desktop
2. Check if the server starts manually: `uv run python -m {{cookiecutter.project_slug}}.server.app`
3. Verify no other process is using the same port

## Support

For issues or questions:
- Check the logs in the platform-specific location above
- Review error messages in your MCP client
{% if cookiecutter.include_admin_ui == "yes" -%}
- Use the admin UI to check server status and logs
{% endif -%}

## Development

To contribute or add new tools to this server, see the [Developer Guide](DEVELOPER_GUIDE.md).

## License

[Your license here]

## Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) framework
- Uses [SAAGA](https://github.com/SAGAAIDEV) decorator patterns
- Implements [Model Context Protocol](https://github.com/modelcontextprotocol) by Anthropic