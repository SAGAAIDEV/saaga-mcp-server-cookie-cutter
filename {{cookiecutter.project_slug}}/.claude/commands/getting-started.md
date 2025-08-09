---
description: Interactive guided tour of your MCP server architecture explaining components and patterns
argument-hint: ""
allowed-tools: ["Read", "Grep", "Glob", "LS"]
---

# 🚀 Welcome to Your MCP Server with SAAGA Decorators!

I'll give you a comprehensive tour of this MCP server architecture, explaining how everything works together.

## 📁 Project Structure Overview

Let me first show you the project layout:

```
{{ cookiecutter.project_slug }}/
├── .reference/           # ← PERMANENT reference patterns (never delete!)
│   ├── patterns/        # Canonical implementations
│   └── templates/       # Code generation templates
├── {{ cookiecutter.project_slug }}/
│   ├── server/          # MCP server with FastMCP
│   │   └── app.py      # Main server entry point
│   ├── decorators/      # SAAGA decorator system
│   │   ├── exception_handler.py
│   │   ├── tool_logger.py
│   │   ├── parallelize.py
│   │   └── type_converter.py
│   ├── tools/           # Your MCP tools go here
│   │   └── example_tools.py
│   └── ui/             # Optional Streamlit admin UI
├── tests/
│   ├── integration/     # MCP client integration tests
│   └── unit/           # Decorator unit tests
└── pyproject.toml      # Project configuration
```

## 🎯 What Makes This Special?

This isn't just a standard MCP server. It includes the **SAAGA Decorator Pattern** - an advanced system that automatically adds:

1. **Exception Handling** - Graceful error management
2. **SQLite Logging** - Every tool execution is logged
3. **Parallelization** - Batch processing support
4. **Type Conversion** - Automatic parameter type handling

## 🔧 How MCP Tools Work Here

Let me show you a real example from your codebase:

Reading {{ cookiecutter.project_slug }}/tools/example_tools.py...

### Basic Tool Pattern
```python
async def your_tool(param1: str, param2: int = 42, ctx: Context = None) -> Dict[str, Any]:
    """Your tool description."""
    # Tool logic here
    return {"result": "success"}
```

**Key Rules:**
- MUST be `async` functions
- MUST have `ctx: Context = None` as last parameter
- MUST have type hints
- NEVER use generic `**kwargs`

## 🎭 The Decorator Magic

Your tools are automatically wrapped with decorators in `server/app.py`:

### For Regular Tools:
```python
@exception_handler  # Catches and re-raises exceptions
@tool_logger       # Logs to SQLite database
async def tool():
    pass
```

### For Parallel Tools:
```python
@exception_handler  # Catches exceptions
@tool_logger       # Logs execution
@parallelize       # Transforms for batch processing
async def batch_tool():
    pass
```

## 🧪 Testing Your Tools

This project uses **MCP Client Integration Testing**:

Reading tests/integration/test_mcp_integration.py pattern...

```python
async def test_your_tool():
    session, cleanup = await create_test_session()
    try:
        result = await session.call_tool("your_tool", arguments={...})
        assert result.isError is False  # Success!
    finally:
        await cleanup()
```

**Important:** When tools raise exceptions, `result.isError` is `True`

## 📊 Admin UI (if enabled)

{% if cookiecutter.include_admin_ui == "yes" %}
You have the Streamlit Admin UI enabled! It provides:
- Server status monitoring
- Configuration editor
- SQLite log viewer
- Real-time metrics

Access it at: http://localhost:8501 (after starting with `/dev-server start`)
{% else %}
The Admin UI is not enabled. You can enable it by regenerating with `include_admin_ui="yes"`
{% endif %}

## 🚦 Getting Started Workflow

Here's your typical development workflow:

### 1. Start Development Server
```bash
/dev-server start
```
This starts MCP Inspector (port 6274) and Streamlit UI (port 8501)

### 2. Add a New Tool
```bash
/add-tool "Tool that fetches weather data"
```
This creates a properly structured tool following all patterns

### 3. Generate Tests
```bash
/generate-tests weather_tool
```
This creates comprehensive integration tests

### 4. Run Tests
```bash
pytest tests/integration/test_weather_tool.py -v
```

### 5. Test in MCP Inspector
Open http://localhost:6274 and test your tool interactively

## 🔍 Understanding the Flow

When a client calls your tool:

1. **MCP Client** sends request with parameters (as strings)
2. **Type Converter** converts strings to correct Python types
3. **Tool Logger** records the start of execution
4. **Your Tool** executes with converted parameters
5. **Tool Logger** records completion/error
6. **Exception Handler** re-raises any exceptions for MCP
7. **MCP Server** sends response back to client

## 📚 Reference Documentation

The `.reference/` directory contains permanent patterns:
- `patterns/tool_patterns.py` - All tool implementation patterns
- `patterns/integration_test_patterns.py` - Testing patterns
- `patterns/decorator_patterns.py` - How decorators work

These files are PERMANENT - they remain even if you delete example code!

## 🎯 Next Steps

1. **Explore Example Tools**: Check `{{ cookiecutter.project_slug }}/tools/example_tools.py`
2. **Run Example Tests**: `pytest tests/integration/ -v`
3. **Start Inspector**: `/dev-server start` and visit http://localhost:6274
4. **Add Your First Tool**: `/add-tool "your tool description"`
5. **Read Patterns**: Study `.reference/patterns/` for deep understanding

## ⚠️ Common Pitfalls to Avoid

1. **Don't use `**kwargs`** - Always use specific parameter names
2. **Don't forget `ctx: Context = None`** - Required for all tools
3. **Don't skip type hints** - Required for type conversion
4. **Don't modify `.reference/`** - It's the source of truth
5. **Don't forget cleanup in tests** - Always use try/finally

## 🆘 Getting Help

- **Commands**: Type `/` to see available commands
- **Patterns**: Check `.reference/patterns/` for examples
- **Tests**: Look at existing tests for patterns
- **Logs**: Check SQLite logs in the Admin UI

Ready to build something awesome? Start with `/add-tool`! 🚀