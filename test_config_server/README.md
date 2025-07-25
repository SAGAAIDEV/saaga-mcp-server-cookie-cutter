# Test Config Server

MCP server with SAAGA decorators

## Quick Start with AI Assistant

**Need help getting started?** Have your AI coding assistant guide you!

Simply tell your AI assistant: *"I have a Test Config Server project. Please read and follow [WORKING_WITH_SAAGA_PROMPT.md](WORKING_WITH_SAAGA_PROMPT.md) to help me understand and work with this MCP server."*

**For quick reference**, the [.ai-prompts.md](.ai-prompts.md) file contains a condensed version of key patterns.

**For detailed technical documentation**, see [docs/DECORATOR_PATTERNS.md](docs/DECORATOR_PATTERNS.md).

## Testing with MCP Inspector

**Ready to test your MCP server?** The [MCP Inspector Guide](docs/MCP_INSPECTOR_GUIDE.md) provides:

- Step-by-step setup instructions with virtual environment troubleshooting
- Test examples for all included tools
- JSON mode instructions for parallel tools
- Common issues and solutions

Quick start:
```bash
source .venv/bin/activate  # Or use: uv shell
uv run mcp dev test_config_server/server/app.py
```

## Overview

This MCP server was generated using the SAAGA MCP Server Cookie Cutter template. It includes:

- **FastMCP Integration**: Modern MCP framework with dual transport support
- **SAAGA Decorators**: Automatic exception handling, logging, and parallelization
- **Platform-Aware Configuration**: Cross-platform configuration management with validation
- **SQLite Logging**: Comprehensive logging with database persistence
- **Configuration Templates**: Pre-configured templates for common use cases
- **Health Monitoring**: Built-in configuration health checks and validation

## Installation

### Prerequisites

- Python 3.11 or higher
- [UV](https://github.com/astral-sh/uv) - An extremely fast Python package manager

### Install from Source

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # On macOS/Linux
# Or visit https://github.com/astral-sh/uv for Windows instructions

git clone <your-repository-url>
cd test_config_server
uv venv
uv sync
```

### Development Installation

```bash
git clone <your-repository-url>
cd test_config_server
uv venv
uv sync --extra dev
```

## Usage

### Running the MCP Server

The server can be run in two modes:

#### 1. STDIO Mode (for MCP clients like Claude Desktop)

```bash
# Run with default settings
uv run python -m test_config_server.server.app

# Run with custom log level
uv run python -m test_config_server.server.app --log-level DEBUG

# Run the server directly
uv run python test_config_server/server/app.py

uv run test_config_server-server
```

#### 2. SSE Mode (for web-based clients)

```bash
# Run with SSE transport
uv run python -m test_config_server.server.app --transport sse --port 3001

# Run with custom host and port
uv run python -m test_config_server.server.app --transport sse --host 0.0.0.0 --port 8080
```

### Command Line Options

```bash
uv run python -m test_config_server.server.app --help
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
    "test_config_server": {
      "command": "uv",
      "args": ["run", "python", "-m", "test_config_server.server.app"],
      "cwd": "/home/waiwe/projects/example/saaga-mcp-server-cookie-cutter/test_config_server"
    }
  }
}
```

#### Advanced Configuration Options

```json
{
  "mcpServers": {
    "test_config_server": {
      "command": "uv",
      "args": [
        "run", "python", "-m", "test_config_server.server.app",
        "--log-level", "DEBUG"
      ],
      "cwd": "/home/waiwe/projects/example/saaga-mcp-server-cookie-cutter/test_config_server",
      "env": {
        "UV_PROJECT_ENVIRONMENT": "/home/waiwe/projects/example/saaga-mcp-server-cookie-cutter/test_config_server/.venv"
      }
    }
  }
}
```

#### Using with System Python (Alternative)

```json
{
  "mcpServers": {
    "test_config_server": {
      "command": "/home/waiwe/projects/example/saaga-mcp-server-cookie-cutter/test_config_server/.venv/bin/python",
      "args": ["-m", "test_config_server.server.app"]
    }
  }
}
```

#### Using with uv tool

```json
{
  "mcpServers": {
    "test_config_server": {
      "command": "uv",
      "args": ["--directory=/home/waiwe/projects/example/saaga-mcp-server-cookie-cutter/test_config_server", "run" ,"test_config_server-server"]
    }
  }
}
```

#### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

## AI Assistant Instructions

When working with this Test Config Server MCP server in an AI coding assistant (like Claude, Cursor, or GitHub Copilot):

### Understanding the Server Architecture

This server uses SAAGA decorators that automatically wrap all MCP tools with:
- **Exception handling**: All errors are caught and returned as structured error responses
- **Comprehensive logging**: All tool invocations are logged with timing and parameters
- **Optional parallelization**: Tools marked for parallel execution run concurrently

### Key Points for AI Assistants

1. **Tool Registration Pattern**: Tools are registered with decorators already applied. Do NOT manually wrap tools with decorators - this is handled automatically in `server/app.py`.

2. **Parameter Types**: MCP passes all parameters as strings from the client. Ensure your tools handle type conversion:
   ```python
   def my_tool(count: str) -> dict:
       # Convert string to int
       count_int = int(count)
       return {"result": count_int * 2}
   ```

3. **Error Handling**: Tools can raise exceptions freely - the exception_handler decorator will catch them and return proper error responses.

4. **Async Support**: Both sync and async tools are supported. The decorators automatically detect and handle both patterns.

5. **Logging**: Check logs at the platform-specific data directory for debugging:
   - macOS: `~/Library/Application Support/test_config_server/logs.db`
   - Linux: `~/.local/share/test_config_server/logs.db`
   - Windows: `%APPDATA%/test_config_server/logs.db`

### Common Tasks

**Adding a new tool:**
```python
# In test_config_server/tools/my_new_tool.py
def my_new_tool(param: str) -> dict:
    """Description of what this tool does."""
    # Implementation
    return {"result": "processed"}

# In test_config_server/tools/__init__.py
from .my_new_tool import my_new_tool
example_tools.append(my_new_tool)
```

**Testing with MCP Inspector:**
```bash
# From the project root
uv run mcp dev test_config_server/server/app.py
```

**Debugging a tool:**
1. Check the SQLite logs for error messages
2. Run with `--log-level DEBUG` for verbose output
3. Test directly with MCP Inspector to see parameter handling

### Important Implementation Notes

- The server uses the standard MCP SDK (`from mcp.server.fastmcp import FastMCP`)
- Function signatures are preserved through careful decorator implementation
- The `register_tools()` function in `server/app.py` handles all decorator application
- Tools should return JSON-serializable Python objects (dict, list, str, int, etc.)

## Configuration

Configuration files are stored in platform-specific locations:
- **macOS**: `~/Library/Application Support/test_config_server/`
- **Linux**: `~/.local/share/test_config_server/`
- **Windows**: `%APPDATA%/test_config_server/`

### Configuration Options

- `log_level`: Logging level (INFO)
- `log_retention_days`: Days to retain logs (30)
- `server_port`: HTTP server port (3001)

## Development

### Project Structure

```
test_config_server/
├── test_config_server/
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

1. Create a new Python file in `test_config_server/tools/`
2. Define your tool function
3. Import and register it in `server/app.py`

Example:

```python
# test_config_server/tools/my_tool.py
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
black test_config_server/
isort test_config_server/

# Lint code
flake8 test_config_server/
mypy test_config_server/
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