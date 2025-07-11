# Fixed MCP Server

MCP server with SAAGA decorators

## Overview

This MCP server was generated using the SAAGA MCP Server Cookie Cutter template. It includes:

- **FastMCP Integration**: Modern MCP framework with dual transport support
- **SAAGA Decorators**: Automatic exception handling, logging, and parallelization
- **Platform-Aware Configuration**: Cross-platform configuration management
- **SQLite Logging**: Comprehensive logging with database persistence

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Install from Source

```bash
git clone <your-repository-url>
cd fixed_mcp_server
pip install -e .
```

### Development Installation

```bash
git clone <your-repository-url>
cd fixed_mcp_server
pip install -e ".[dev]"
```

## Usage

### Running the MCP Server

The server can be run in two modes:

#### 1. STDIO Mode (for MCP clients like Claude Desktop)

```bash
# Run with default settings
python -m fixed_mcp_server.server.app

# Run with custom log level
python -m fixed_mcp_server.server.app --log-level DEBUG

# Run the server directly
python fixed_mcp_server/server/app.py
```

#### 2. SSE Mode (for web-based clients)

```bash
# Run with SSE transport
python -m fixed_mcp_server.server.app --transport sse --port 3001

# Run with custom host and port
python -m fixed_mcp_server.server.app --transport sse --host 0.0.0.0 --port 8080
```

### Command Line Options

```bash
python -m fixed_mcp_server.server.app --help
```

Available options:
- `--transport`: Choose between "stdio" (default) or "sse"
- `--host`: Host to bind to for SSE transport (default: 127.0.0.1)
- `--port`: Port to bind to for SSE transport (default: 3001)
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)

### MCP Client Configuration

#### Claude Desktop Configuration

Add the following to your Claude Desktop MCP settings (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fixed_mcp_server": {
      "command": "python",
      "args": ["-m", "fixed_mcp_server.server.app"]
    }
  }
}
```

#### Advanced Configuration Options

```json
{
  "mcpServers": {
    "fixed_mcp_server": {
      "command": "python",
      "args": [
        "-m", "fixed_mcp_server.server.app",
        "--log-level", "DEBUG"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

#### Using with Virtual Environment

```json
{
  "mcpServers": {
    "fixed_mcp_server": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "fixed_mcp_server.server.app"]
    }
  }
}
```

#### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

## Configuration

Configuration files are stored in platform-specific locations:
- **macOS**: `~/Library/Application Support/fixed_mcp_server/`
- **Linux**: `~/.local/share/fixed_mcp_server/`
- **Windows**: `%APPDATA%/fixed_mcp_server/`

### Configuration Options

- `log_level`: Logging level (INFO)
- `log_retention_days`: Days to retain logs (30)
- `server_port`: HTTP server port (3001)

## Development

### Project Structure

```
fixed_mcp_server/
├── fixed_mcp_server/
│   ├── config.py              # Platform-aware configuration
│   ├── server/
│   │   └── app.py             # FastMCP server with decorators
│   ├── tools/                 # Your MCP tools
│   ├── decorators/            # SAAGA decorators
│   └── ui/                    # Streamlit admin UI
├── tests/                     # Test suite
├── docs/                      # Documentation
└── pyproject.toml            # Project configuration
```

### Adding New Tools

1. Create a new Python file in `fixed_mcp_server/tools/`
2. Define your tool function
3. Import and register it in `server/app.py`

Example:

```python
# fixed_mcp_server/tools/my_tool.py
def my_tool(message: str) -> str:
    """Example MCP tool."""
    return f"Processed: {message}"

# The server will automatically apply SAAGA decorators
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

This project uses several code quality tools:

```bash
# Format code
black fixed_mcp_server/
isort fixed_mcp_server/

# Lint code
flake8 fixed_mcp_server/
mypy fixed_mcp_server/
```

## SAAGA Decorators

This server automatically applies three key decorators to your MCP tools:

1. **Exception Handler**: Graceful error handling with logging
2. **Tool Logger**: Comprehensive logging to SQLite database
3. **Parallelize**: Optional parallel processing for compute-intensive tools

## Logging

Logs are stored in a SQLite database with the following schema:
- `timestamp`: When the tool was called
- `tool_name`: Name of the MCP tool
- `duration_ms`: Execution time in milliseconds
- `status`: Success/failure status
- `input_args`: Tool input arguments
- `output_summary`: Summary of tool output
- `error_message`: Error details (if any)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` directory
- Review the test suite for usage examples

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP framework
- [SAAGA](https://github.com/SAGAAIDEV) for the decorator patterns
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter) for the templating system