# Setup Instructions for SAAGA MCP Server Cookie Cutter

Please help me set up a new MCP server project using the SAAGA cookie cutter template. Follow these steps:

## 1. Install Prerequisites

First, ensure Python 3.11 or higher is installed:
```bash
python --version
```

Install cookiecutter if not already installed:
```bash
pip install cookiecutter
```

## 2. Generate the Project

Run the cookiecutter command to generate a new MCP server:
```bash
cookiecutter https://github.com/SAGAAIDEV/saaga-mcp-server-cookie-cutter.git
```

You'll be prompted for several values. Here are suggested defaults:

- **project_name**: Give it a descriptive name like "My MCP Tools Server"
- **project_slug**: Accept the default (auto-generated from project name)
- **description**: Brief description of what your server will do
- **author_name**: Your name
- **author_email**: Your email
- **python_version**: Choose 3.11 or 3.12
- **include_admin_ui**: Choose "yes" if you want a web UI for configuration and logs
- **include_example_tools**: Choose "yes" to see example implementations
- **include_parallel_example**: Choose "yes" to see parallelization examples
- **server_port**: Accept default (3001) or choose your preferred port
- **log_level**: Choose "INFO" for normal use or "DEBUG" for development
- **log_retention_days**: Accept default (30) or adjust as needed

## 3. Navigate to Your Project

```bash
cd <your-project-slug>
```

## 4. Create and Activate Virtual Environment

**IMPORTANT**: Always use a virtual environment for Python projects!

On macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

## 5. Install the Project

Install in development mode with all dependencies:
```bash
pip install -e .
```

## 6. Test the Server

Test with MCP Inspector to verify everything works:
```bash
mcp dev your_project/server/app.py
```

This will:
- Start your MCP server
- Open MCP Inspector in your browser
- Show all available tools with proper parameter names

Click "Connect" in the Inspector and test the example tools to ensure they work correctly.

## 7. Understanding the Structure

Your generated project has this structure:

```
your-project/
├── your_project/
│   ├── server/app.py        # Main server with automatic decorator application
│   ├── tools/               # Your MCP tools go here
│   ├── decorators/          # SAAGA decorators (don't modify these)
│   └── ui/                  # Optional Streamlit admin UI
├── docs/
│   └── DECORATOR_PATTERNS.md # Detailed explanation of the decorator system
├── .ai-prompts.md           # Quick reference for AI assistants
└── README.md                # Your project documentation
```

## 8. Key Concepts to Understand

The SAAGA MCP Server uses automatic decorator application:

1. **All tools** automatically get:
   - `@exception_handler` - Catches errors and returns structured responses
   - `@tool_logger` - Logs execution time and parameters

2. **Tools in `parallel_example_tools`** also get:
   - `@parallelize` - Enables parallel processing for batch operations

3. **Important**: You don't manually apply decorators. The server does it automatically!

## 9. Next Steps

1. If you included example tools, examine them in `tools/example_tools.py`
2. Read `docs/DECORATOR_PATTERNS.md` to understand the decorator system
3. Try adding your own tool by copying an example
4. If you included the admin UI, run it with: `streamlit run your_project/ui/app.py`

## 10. Configure Claude Desktop (Optional)

To use your server with Claude Desktop, add to your Claude config:

```json
{
  "mcpServers": {
    "your-project": {
      "command": "python",
      "args": ["-m", "your_project.server.app"]
    }
  }
}
```

## Common Issues

- **"kwargs" in MCP Inspector**: This means function signatures are hidden. The template should prevent this.
- **Type errors**: Remember MCP passes all parameters as strings. Handle conversion in your tools.
- **Import errors**: Make sure you activated the virtual environment and ran `pip install -e .`

Now show me the generated project structure and explain what each part does!