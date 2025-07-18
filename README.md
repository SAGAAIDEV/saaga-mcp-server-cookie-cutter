# SAAGA MCP Server Cookie Cutter

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for creating MCP (Model Context Protocol) servers with SAAGA decorators, platform-aware configuration, and optional Streamlit administrative UI.

## Quick Start with AI Assistant

**Want to create a new MCP server?** Have your AI coding assistant guide you through the entire process!

Simply tell your AI assistant: *"I want to create a new MCP server using the SAAGA template. Please read and execute the setup instructions in [SETUP_ASSISTANT_PROMPT.md](SETUP_ASSISTANT_PROMPT.md)"*

This will guide you through:
- Installing cookiecutter
- Generating your new MCP server project
- Understanding the SAAGA decorator patterns
- Setting up your development environment
- Testing with MCP Inspector

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
- [UV](https://github.com/astral-sh/uv) - An extremely fast Python package manager
- [Cookiecutter](https://cookiecutter.readthedocs.io/en/latest/installation.html)

### Installation

```bash
# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # On macOS/Linux
# Or visit https://github.com/astral-sh/uv for Windows instructions

# Install cookiecutter as a UV tool
uv tool install cookiecutter
```

### Usage

Generate a new MCP server project:

```bash
# Using UV tool
uv tool run cookiecutter https://github.com/SAGAAIDEV/saaga-mcp-server-cookie-cutter.git

# Or if you installed cookiecutter globally
cookiecutter https://github.com/SAGAAIDEV/saaga-mcp-server-cookie-cutter.git
```

Or from a local checkout:

```bash
# Using UV tool
uv tool run cookiecutter /path/to/saaga-mcp-server-cookie-cutter

# Or if you installed cookiecutter globally
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

## Example Server Reference Implementation

The `example_server/` directory contains a fully functional MCP server that demonstrates all the features of this template:

- ✅ Working SAAGA decorators with proper parameter introspection
- ✅ Dual transport support (STDIO and SSE)
- ✅ Example tools showing both sync and async patterns
- ✅ Complete configuration management
- ✅ Proper logging setup

### Testing the Example Server

```bash
cd example_server/test_asep40_server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
# Or simply use: uv shell

uv sync

# Test with MCP Inspector
uv run mcp dev test_asep40_server/server/app.py

# Or run directly
uv run python -m test_asep40_server.server.app
```

For detailed testing instructions and examples for each tool in the MCP Inspector, see [MCP_INSPECTOR_TEST_GUIDE.md](docs/MCP_INSPECTOR_TEST_GUIDE.md).

Use the example server as a reference when building your own MCP tools to understand:
- How decorators preserve function signatures
- Proper tool registration patterns
- Configuration management best practices
- Logging and error handling approaches

For detailed information about the decorator patterns, see [DECORATOR_PATTERNS.md](docs/DECORATOR_PATTERNS.md). This documentation is also included in every generated project.

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
│       ├── app.py            # Main UI entry point with navigation
│       ├── pages/            # Multi-page structure
│       │   ├── 1_🏠_Home.py # Dashboard with server status
│       │   ├── 2_⚙️_Configuration.py # Config management
│       │   └── 3_📊_Logs.py # Log viewer and analysis
│       └── lib/              # Shared UI components
│           ├── components.py # Reusable UI elements
│           ├── styles.py     # CSS and theming
│           └── utils.py      # Helper functions
├── tests/                     # Test suite
├── docs/                      # Documentation
│   └── DECORATOR_PATTERNS.md # Detailed decorator guidance
├── BUILD.bazel               # Bazel build configuration
├── .ai-prompts.md            # AI assistant context
├── pyproject.toml            # Project configuration
├── README.md                 # Project documentation
├── .gitignore               # Git ignore rules
└── LICENSE                  # MIT license
```

## Key Features

### Bazel Integration

Generated projects include a `BUILD.bazel` file for seamless integration with the SAAGA build system. This enables:
- Automatic registration with the SAAGA infrastructure
- Consistent dependency management through Bazel
- Easy integration with other SAAGA components

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

### Optional Streamlit Admin UI

When `include_admin_ui=yes`, the template generates a comprehensive web-based administrative interface:

#### Dashboard
![Streamlit Admin UI Dashboard](docs/images/streamlit-ui-dashboard.png)

The dashboard provides real-time server status monitoring, project information, and quick access to common actions.

#### Configuration Editor
![Streamlit Admin UI Configuration](docs/images/streamlit-ui-configuration.png)

The configuration page allows you to edit server settings, with features like:
- Real-time validation
- Diff preview showing changes
- Export/import functionality (JSON & YAML)
- Reset to defaults with confirmation

#### Log Viewer
![Streamlit Admin UI Logs](docs/images/streamlit-ui-logs.png)

The logs page provides comprehensive log analysis with:
- Date range filtering
- Status filtering (success/error)
- Tool-specific filtering
- Export capabilities

#### Features
- **🏠 Dashboard**: Server status monitoring, project information, and quick actions
- **⚙️ Configuration**: Server configuration management with validation and diff preview
- **📊 Logs**: Log viewer with advanced filtering and export capabilities
- **🎨 Modern UI**: Professional interface with custom CSS and responsive design
- **🔄 Real-time Status**: Live server monitoring via port checking
- **🛡️ Error Handling**: Graceful degradation and fallback modes

#### Running the Admin UI

After generating your project with `include_admin_ui=yes`:

```bash
# Install your project
cd your-project
uv venv
uv sync

# Start the admin UI
uv run streamlit run your_project/ui/app.py

# In another terminal, start your MCP server (for status monitoring)
uv run python -m your_project --transport sse --port 3001
```

The admin UI will be available at `http://localhost:8501` and can monitor your MCP server running on port 3001.

#### UI Structure

```
ui/
├── app.py              # Main Streamlit entry point with navigation
├── pages/              # Multi-page structure
│   ├── 1_🏠_Home.py   # Dashboard with server status
│   ├── 2_⚙️_Configuration.py  # Config management
│   └── 3_📊_Logs.py   # Log viewer with filtering
└── lib/               # Shared utilities
    ├── components.py  # Reusable UI components
    ├── styles.py      # CSS styling and themes
    └── utils.py       # Helper functions and server status checks
```

#### Independent Operation

The admin UI works independently of the MCP server:
- ✅ **Server Running**: Shows real-time status and monitoring
- ✅ **Server Stopped**: Functions with fallback data and placeholders
- ✅ **Standalone Mode**: All UI features work without server dependencies

## Development

### Setting Up for Development

1. Clone this repository
2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   uv sync --extra dev
   ```
3. Install pre-commit hooks: `uv run pre-commit install`

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

## For Template Developers

If you're working on improving or maintaining this cookiecutter template, please note:

### 🚨 Critical Architecture Decisions

1. **SAAGA Decorators are Core**: The decorator pattern is fundamental to this template. Changes to decorator behavior will impact all generated projects.

2. **Async-Only Pattern**: All decorators require async functions. This is a SAAGA standard that must be maintained.

3. **Signature Transformation**: The `parallelize` decorator intentionally transforms function signatures. This enables batch processing but requires careful handling.

4. **Registration Pattern**: Tools are registered via lists (`example_tools`, `parallel_example_tools`) rather than decorators. This allows proper decorator chaining.

### 📚 Technical Documentation

For detailed technical information about the decorator implementation:
- See [docs/DECORATOR_PATTERNS.md](docs/DECORATOR_PATTERNS.md) for implementation details
- Review `example_server/` for a working reference implementation
- Check the generated project's documentation to understand end-user experience

### ⚠️ Before Making Changes

1. **Understand the current pattern**: The decorator chain order matters
2. **Test with MCP Inspector**: Ensure parameter introspection still works
3. **Verify signature transformation**: Parallel tools must show `kwargs_list: List[Dict]`
4. **Update all documentation**: Both template and generated project docs

## Architecture

### MCP Server Lifecycle

MCP servers are launched by MCP clients (Claude Desktop, Cursor, etc.) through configuration. The generated server:

1. Loads configuration from platform-specific locations
2. Applies SAAGA decorators automatically
3. Registers tools with the FastMCP framework
4. Handles client connections via stdio or SSE transport

### Decorator Application Pattern

The template automatically applies SAAGA decorators to all tools during server initialization. Here's the actual pattern used:

```python
# From server/app.py - How decorators are applied
for tool_func in example_tools:
    # Apply SAAGA decorator chain: exception_handler → tool_logger
    decorated_func = exception_handler(tool_logger(tool_func, config.__dict__))
    mcp_server.tool(name=tool_func.__name__)(decorated_func)

for tool_func in parallel_example_tools:
    # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
    decorated_func = exception_handler(tool_logger(parallelize(tool_func), config.__dict__))
    mcp_server.tool(name=tool_func.__name__)(decorated_func)
```

**⚠️ Important**: All SAAGA decorators require async functions. The parallel decorator also transforms the function signature.

## Examples

### Basic MCP Tool

Tools are defined as async functions and automatically decorated when added to the `example_tools` list:

```python
# In your_project/tools/my_tools.py
async def example_tool(message: str) -> str:
    """Example MCP tool with automatic decorators."""
    return f"Processed: {message}"

# Add to example_tools list to register
example_tools = [example_tool]
```

### Parallel Processing Tool

Parallel tools must be async and will have their signature transformed to accept `List[Dict]`:

```python
# Original function definition
async def process_item(item: str, operation: str = "upper") -> str:
    """Process a single item - will be parallelized."""
    if operation == "upper":
        return item.upper()
    elif operation == "lower":
        return item.lower()

# Add to parallel_example_tools list
parallel_example_tools = [process_item]

# After decoration, MCP clients call it with:
# [{"item": "hello", "operation": "upper"}, {"item": "world", "operation": "lower"}]
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework
- [Cookiecutter](https://github.com/cookiecutter/cookiecutter) for the templating system