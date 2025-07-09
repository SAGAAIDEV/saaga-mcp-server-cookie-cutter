# {{cookiecutter.project_name}}

{{cookiecutter.description}}

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
python -m {{cookiecutter.project_slug}}.server.app
```

#### 2. HTTP Mode (for web-based clients)

```bash
python -m {{cookiecutter.project_slug}}.server.app --transport http --port {{cookiecutter.server_port}}
```

### MCP Client Configuration

To use this server with Claude Desktop, add the following to your MCP settings:

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