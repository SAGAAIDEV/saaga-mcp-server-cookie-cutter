# Working with SAAGA MCP Servers

I'm working with a SAAGA MCP server that uses automatic decorator patterns. Please help me understand and work with this codebase effectively.

## Key Architecture Concepts

### 1. SAAGA Decorators

This server automatically applies decorators to all MCP tools:

- **@exception_handler**: Applied to ALL tools
  - Catches any exceptions and returns structured error responses
  - Ensures MCP clients get proper error messages
  - You can raise exceptions freely in your tools

- **@tool_logger**: Applied to ALL tools
  - Logs execution time, parameters, and results
  - Stores logs in SQLite database
  - Helps with debugging and performance monitoring

- **@parallelize**: Applied ONLY to tools in `parallel_example_tools`
  - Enables parallel processing for batch operations
  - Only use for tools that process lists of independent items
  - Not suitable for sequential operations or single-item tools

### 2. Function Signature Preservation

**CRITICAL**: The decorators preserve function signatures for MCP introspection. This means:
- MCP Inspector shows actual parameter names (not "kwargs")
- Parameter types and descriptions are visible to clients
- Claude Desktop and other MCP clients can validate inputs

### 3. Parameter Type Conversion

**IMPORTANT**: MCP passes all parameters as strings. Your tools must handle conversion:

```python
def my_tool(count: str, threshold: str) -> dict:
    # Convert string parameters to proper types
    count_int = int(count)
    threshold_float = float(threshold)
    
    # Process with converted values
    return {"result": count_int * threshold_float}
```

## Common Development Tasks

### Adding a Regular Tool

1. Create a new function in `tools/` directory
2. Add it to the `example_tools` list
3. The server automatically applies decorators

Example:
```python
# In tools/my_tools.py
def fetch_data(url: str, timeout: str = "30") -> dict:
    """Fetch data from a URL with timeout."""
    timeout_int = int(timeout)
    # Implementation here
    return {"data": "fetched content", "timeout_used": timeout_int}

# In tools/__init__.py
from .my_tools import fetch_data
example_tools.append(fetch_data)
```

### Adding a Parallel Processing Tool

Only add to `parallel_example_tools` if the tool:
- Processes a list of independent items
- Each item can be processed without depending on others
- Benefits from parallel execution

Example:
```python
def process_urls(urls: List[str]) -> List[dict]:
    """Process multiple URLs independently."""
    # Each URL processed separately
    return [fetch_url(url) for url in urls]

# In tools/__init__.py
parallel_example_tools.append(process_urls)
```

### Testing Your Tools

1. Use MCP Inspector:
   ```bash
   mcp dev your_project/server/app.py
   ```

2. Check the logs:
   - Location varies by platform (check README)
   - SQLite database contains all execution logs

3. Enable debug logging:
   ```bash
   python -m your_project.server.app --log-level DEBUG
   ```

## Important Files to Know

- **server/app.py**: Contains the decorator registration logic. Look at `register_tools()` function.
- **decorators/**: The three SAAGA decorators. Don't modify these unless you understand the impact.
- **tools/**: Where all your MCP tools live.
- **docs/DECORATOR_PATTERNS.md**: Detailed technical documentation about the decorator system.
- **WORKING_WITH_SAAGA_PROMPT.md**: This file - a guide for AI assistants and developers.

## Best Practices

1. **Let exceptions bubble up**: The exception handler will catch them
2. **Use type hints**: Helps with documentation and IDE support
3. **Write clear docstrings**: These become tool descriptions in MCP
4. **Test with real MCP clients**: Not just MCP Inspector
5. **Check the example_server**: Reference implementation showing all patterns

## Common Pitfalls to Avoid

1. **Don't manually apply decorators**: The server does this automatically
2. **Don't use **kwargs in tool signatures**: This hides parameters from MCP
3. **Don't forget string conversion**: All MCP parameters arrive as strings
4. **Don't parallelize everything**: Only batch/independent operations
5. **Don't modify decorator order**: The server applies them correctly

## Getting Help

- Check `docs/DECORATOR_PATTERNS.md` for detailed technical information
- Look at the example tools for working patterns
- The `example_server/` directory has a complete reference implementation
- Enable DEBUG logging to see detailed execution traces

Now, what would you like to work on? I can help you:
- Add new tools with proper patterns
- Debug issues with parameter handling
- Understand the decorator chain
- Work with the parallel processing features
- Set up testing and logging