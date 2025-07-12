# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Quick Start with AI Assistant

**Need help getting started?** Have your AI coding assistant guide you!

Simply tell your AI assistant: *"I have a {{cookiecutter.project_name}} project. Please read and follow [WORKING_WITH_SAAGA_PROMPT.md](WORKING_WITH_SAAGA_PROMPT.md) to help me understand and work with this MCP server."*

**For quick reference**, the [.ai-prompts.md](.ai-prompts.md) file contains a condensed version of key patterns.

**For detailed technical documentation**, see [docs/DECORATOR_PATTERNS.md](docs/DECORATOR_PATTERNS.md).

## Overview

This MCP server was generated using the SAAGA MCP Server Cookie Cutter template. It includes:

- **FastMCP Integration**: Modern MCP framework with dual transport support
- **SAAGA Decorators**: Automatic exception handling, logging, and parallelization
- **Platform-Aware Configuration**: Cross-platform configuration management
{% if cookiecutter.include_admin_ui == "yes" -%}
- **Streamlit Admin UI**: Web-based configuration and monitoring interface
{% endif -%}
- **SQLite Logging**: Comprehensive logging with database persistence

## Installation

### Prerequisites

- Python {{cookiecutter.python_version}} or higher
- pip (Python package manager)

### Install from Source

```bash
git clone <your-repository-url>
cd {{cookiecutter.project_slug}}
pip install -e .
```

### Development Installation

```bash
git clone <your-repository-url>
cd {{cookiecutter.project_slug}}
pip install -e ".[dev]"
```

## Usage

### Running the MCP Server

The server can be run in two modes:

#### 1. STDIO Mode (for MCP clients like Claude Desktop)

```bash
# Run with default settings
python -m {{cookiecutter.project_slug}}.server.app

# Run with custom log level
python -m {{cookiecutter.project_slug}}.server.app --log-level DEBUG

# Run the server directly
python {{cookiecutter.project_slug}}/server/app.py
```

#### 2. SSE Mode (for web-based clients)

```bash
# Run with SSE transport
python -m {{cookiecutter.project_slug}}.server.app --transport sse --port {{cookiecutter.server_port}}

# Run with custom host and port
python -m {{cookiecutter.project_slug}}.server.app --transport sse --host 0.0.0.0 --port 8080
```

### Command Line Options

```bash
python -m {{cookiecutter.project_slug}}.server.app --help
```

Available options:
- `--transport`: Choose between "stdio" (default) or "sse"
- `--host`: Host to bind to for SSE transport (default: 127.0.0.1)
- `--port`: Port to bind to for SSE transport (default: {{cookiecutter.server_port}})
- `--log-level`: Logging level - DEBUG, INFO, WARNING, ERROR (default: {{cookiecutter.log_level}})

### MCP Client Configuration

#### Claude Desktop Configuration

Add the following to your Claude Desktop MCP settings (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "{{cookiecutter.project_slug}}": {
      "command": "python",
      "args": ["-m", "{{cookiecutter.project_slug}}.server.app"]
    }
  }
}
```

#### Advanced Configuration Options

```json
{
  "mcpServers": {
    "{{cookiecutter.project_slug}}": {
      "command": "python",
      "args": [
        "-m", "{{cookiecutter.project_slug}}.server.app",
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
    "{{cookiecutter.project_slug}}": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["-m", "{{cookiecutter.project_slug}}.server.app"]
    }
  }
}
```

#### Configuration File Locations

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

{% if cookiecutter.include_admin_ui == "yes" -%}
### Admin UI

Launch the Streamlit admin interface:

```bash
streamlit run {{cookiecutter.project_slug}}/ui/app.py
```

The admin UI provides:
- Configuration editor
- Log viewer with filtering
- Export capabilities
- System status dashboard

{% endif -%}
## AI Assistant Instructions

When working with this {{cookiecutter.project_name}} MCP server in an AI coding assistant (like Claude, Cursor, or GitHub Copilot):

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
   - macOS: `~/Library/Application Support/{{cookiecutter.project_slug}}/logs.db`
   - Linux: `~/.local/share/{{cookiecutter.project_slug}}/logs.db`
   - Windows: `%APPDATA%/{{cookiecutter.project_slug}}/logs.db`

### Common Tasks

**Adding a new tool:**
```python
# In {{cookiecutter.project_slug}}/tools/my_new_tool.py
def my_new_tool(param: str) -> dict:
    """Description of what this tool does."""
    # Implementation
    return {"result": "processed"}

# In {{cookiecutter.project_slug}}/tools/__init__.py
from .my_new_tool import my_new_tool
example_tools.append(my_new_tool)
```

**Testing with MCP Inspector:**
```bash
# From the project root
mcp dev {{cookiecutter.project_slug}}/server/app.py
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
- **macOS**: `~/Library/Application Support/{{cookiecutter.project_slug}}/`
- **Linux**: `~/.local/share/{{cookiecutter.project_slug}}/`
- **Windows**: `%APPDATA%/{{cookiecutter.project_slug}}/`

### Configuration Options

- `log_level`: Logging level ({{cookiecutter.log_level}})
- `log_retention_days`: Days to retain logs ({{cookiecutter.log_retention_days}})
- `server_port`: HTTP server port ({{cookiecutter.server_port}})

## Development

### Project Structure

```
{{cookiecutter.project_slug}}/
├── {{cookiecutter.project_slug}}/
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

1. Create a new Python file in `{{cookiecutter.project_slug}}/tools/`
2. Define your tool function
3. Import and register it in `server/app.py`

Example:

```python
# {{cookiecutter.project_slug}}/tools/my_tool.py
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
black {{cookiecutter.project_slug}}/
isort {{cookiecutter.project_slug}}/

# Lint code
flake8 {{cookiecutter.project_slug}}/
mypy {{cookiecutter.project_slug}}/
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