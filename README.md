# SAAGA MCP Server Cookie Cutter

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for creating MCP (Model Context Protocol) servers with SAAGA decorators, platform-aware configuration, and optional Streamlit administrative UI.

## Features

- **FastMCP Integration**: Built on the modern FastMCP framework with dual transport support (stdio/SSE)
- **SAAGA Decorators**: Automatic application of exception handling, logging, and parallelization decorators
- **Platform-Aware Configuration**: Cross-platform configuration management using `platformdirs`
- **Optional Streamlit UI**: Administrative interface for configuration and log viewing
- **SQLite Logging**: Comprehensive logging system with database persistence
- **Developer-Friendly**: Pre-commit hooks, GitHub Actions, and comprehensive documentation

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [Cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html)

### Installation

```bash
pip install cookiecutter
```

### Usage

Generate a new MCP server project:

```bash
cookiecutter https://github.com/SAGAAIDEV/saaga-mcp-server-cookie-cutter.git
```

Or from a local checkout:

```bash
cookiecutter /path/to/saaga-mcp-server-cookie-cutter
```

### Configuration Options

You'll be prompted for the following configuration options:

- `project_name`: Human-readable project name
- `project_slug`: Python package name (auto-generated)
- `description`: Project description
- `author_name`: Your name
- `author_email`: Your email address
- `python_version`: Target Python version (3.11 or 3.12)
- `include_admin_ui`: Include Streamlit administrative UI (yes/no)
- `include_example_tools`: Include example MCP tools (yes/no)
- `include_parallel_example`: Include parallel processing example (yes/no)
- `server_port`: Default server port for HTTP transport
- `log_level`: Default logging level (INFO, DEBUG, WARNING, ERROR)
- `log_retention_days`: Number of days to retain logs

## Generated Project Structure

```
your-project/
├── your_project/
│   ├── __init__.py
│   ├── config.py              # Platform-aware configuration
│   ├── server/
│   │   └── app.py             # FastMCP server with auto-decorators
│   ├── tools/                 # Your MCP tools
│   │   └── example_tools.py   # Example tools (optional)
│   ├── decorators/            # SAAGA decorators
│   │   ├── exceptions.py      # Exception handling
│   │   ├── logging.py         # SQLite logging
│   │   └── parallelize.py     # Parallelization support
│   └── ui/                    # Streamlit admin UI (optional)
│       ├── app.py
│       ├── pages/
│       └── lib/
├── tests/                     # Test suite
├── docs/                      # Documentation
├── pyproject.toml            # Project configuration
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
└── LICENSE                  # MIT license
```

## Key Features

### SAAGA Decorators

The template automatically applies three key decorators to your MCP tools:

1. **Exception Handler**: Graceful error handling with logging
2. **Tool Logger**: Comprehensive logging to SQLite database
3. **Parallelize**: Optional parallel processing for compute-intensive tools

### Platform-Aware Configuration

Configuration files are automatically placed in appropriate locations:
- macOS: `~/Library/Application Support/your-project/`
- Linux: `~/.local/share/your-project/`
- Windows: `%APPDATA%/your-project/`

### Optional Streamlit UI

When enabled, provides:
- Configuration editor
- Log viewer with filtering
- Export capabilities
- System status dashboard

## Development

### Setting Up for Development

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install pre-commit hooks: `pre-commit install`

### Testing

Run the test suite:

```bash
pytest tests/
```

Test template generation:

```bash
cookiecutter . --no-input
```

### Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Architecture

### MCP Server Lifecycle

MCP servers are launched by MCP clients (Claude Desktop, Cursor, etc.) through configuration. The generated server:

1. Loads configuration from platform-specific locations
2. Applies SAAGA decorators automatically
3. Registers tools with the FastMCP framework
4. Handles client connections via stdio or SSE transport

### Decorator Application Pattern

```python
def create_decorated_server(name, tools, parallel_tools):
    server = FastMCP(name)
    
    # Regular tools: exception_handler → tool_logger
    for func in tools:
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        server.tool()(decorated)
    
    # Parallel tools: exception_handler → tool_logger → parallelize
    for func in parallel_tools:
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        decorated = parallelize(decorated)
        server.tool()(decorated)
    
    return server
```

## Examples

### Basic MCP Tool

```python
from your_project.server.app import server

@server.tool
def example_tool(message: str) -> str:
    """Example MCP tool with automatic decorators."""
    return f"Processed: {message}"
```

### Parallel Processing Tool

```python
from your_project.server.app import server

@server.tool
def compute_intensive_tool(data: list) -> list:
    """Tool that will be automatically parallelized."""
    # This tool will be wrapped with the parallelize decorator
    return [expensive_computation(item) for item in data]
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter) for the templating system
- [SAAGA](https://github.com/SAGAAIDEV) for the decorator patterns