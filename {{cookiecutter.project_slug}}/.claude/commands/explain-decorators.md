---
description: Explain the SAAGA decorator patterns and how to work with MCP tools in this project
argument-hint: ""
allowed-tools: []
---

# SAAGA Decorator Patterns Explanation

## Overview

This MCP server uses the SAAGA decorator pattern to automatically enhance all tools with logging, error handling, parallelization, and type conversion capabilities. Here's everything you need to know:

## The Decorator Stack

All tools are automatically wrapped with decorators in this specific order:

1. **`@type_converter`** (innermost) - Converts MCP string parameters to expected Python types
2. **`@exception_handler`** - Catches and formats exceptions for MCP clients  
3. **`@tool_logger`** - Logs execution details to SQLite with timing
4. **`@parallelize`** (outermost, only for parallel tools) - Enables concurrent batch processing

### Application Pattern

```python
# This happens automatically in server/app.py:
def apply_decorators(func, is_parallel=False):
    # Start with type conversion (innermost)
    decorated = type_converter(func)
    # Add exception handling
    decorated = exception_handler(decorated)
    # Add logging
    decorated = tool_logger(decorated)
    # Optionally add parallelization (outermost)
    if is_parallel:
        decorated = parallelize(decorated)
    return decorated
```

## Decorator Details

### 1. Type Converter Decorator (`decorators/type_converter.py`)
**Purpose**: Automatically converts MCP string parameters to the types specified in function signatures

**Key Features**:
- Inspects function signatures to determine expected types
- Converts string inputs to int, float, bool, list, dict, etc.
- Preserves None values and handles Optional types
- Falls back to string if conversion fails

**Example**:
```python
def my_tool(count: int, enabled: bool = False) -> dict:
    # MCP sends: {"count": "5", "enabled": "true"}
    # Decorator converts to: count=5, enabled=True
    return {"result": count * 2}
```

### 2. Exception Handler Decorator (`decorators/exception_handler.py`)
**Purpose**: Ensures tools never crash the MCP server

**Key Features**:
- Catches all exceptions from tools
- Re-raises them for MCP to handle properly (important for error reporting)
- Preserves original function signatures for MCP introspection
- Maintains correlation IDs for request tracking

**Example**:
```python
def risky_tool(value: str) -> dict:
    if not value:
        raise ValueError("Value required")  # Decorator catches and re-raises
    return {"processed": value}
```

### 3. Tool Logger Decorator (`decorators/tool_logger.py`)
**Purpose**: Comprehensive logging of all tool executions

**Key Features**:
- Logs to SQLite database with correlation IDs
- Tracks execution time in milliseconds
- Records input arguments and output summaries
- Captures error messages when tools fail
- Thread-safe database operations

**Logged Data**:
- Timestamp, tool name, duration
- Status (success/error)
- Input arguments (as JSON)
- Output summary (truncated)
- Error messages and stack traces
- Correlation ID for request tracking

### 4. Parallelize Decorator (`decorators/parallelize.py`)
**Purpose**: Enable concurrent processing for batch operations

**Key Features**:
- ONLY for tools that process independent items
- Automatically distributes work across threads
- Preserves MCP context during parallel execution
- Configurable max workers (default: 4)

**When to Use**:
- ✅ Batch processing of independent items
- ✅ Multiple API calls that don't depend on each other
- ❌ Sequential operations that depend on previous results
- ❌ Single-item processing

**Example**:
```python
def batch_processor(items: list[str]) -> list[dict]:
    # Processes each item independently in parallel
    return [{"processed": item.upper()} for item in items]
```

## Adding New Tools

### Regular Tool (Most Common)
```python
# In {{ cookiecutter.project_slug }}/tools/my_tools.py
def my_new_tool(text: str, count: int = 10) -> dict:
    """Tool description for MCP."""
    # Type converter handles: text="hello", count="5" → count=5
    result = text * count
    return {"result": result, "length": len(result)}

# In {{ cookiecutter.project_slug }}/tools/__init__.py
from .my_tools import my_new_tool
example_tools.append(my_new_tool)
```

### Parallel Processing Tool
```python
# In {{ cookiecutter.project_slug }}/tools/batch_tools.py
def process_urls(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    # Each URL is processed independently
    results = []
    for url in urls:
        # This will be parallelized
        results.append(fetch_url(url))
    return results

# In {{ cookiecutter.project_slug }}/tools/__init__.py  
from .batch_tools import process_urls
parallel_example_tools.append(process_urls)
```

## Important Rules

### DO:
- ✅ Use explicit parameter types in function signatures
- ✅ Let decorators handle type conversion automatically
- ✅ Raise exceptions freely (decorator handles them)
- ✅ Use descriptive function and parameter names
- ✅ Include docstrings for MCP tool descriptions
- ✅ Return dict or simple types that serialize to JSON

### DON'T:
- ❌ Manually apply decorators (server does this)
- ❌ Create wrapper functions (breaks introspection)
- ❌ Use `**kwargs` in signatures (use explicit parameters)
- ❌ Handle type conversion manually (decorator does this)
- ❌ Catch all exceptions (let decorator handle them)
- ❌ Use parallelize for sequential operations

## Testing Your Tools

### Using MCP Inspector
```bash
# Start the inspector
mcp dev {{ cookiecutter.project_slug }}/server/app.py

# Your tools will appear with:
# - Correct parameter names and types (not "kwargs")
# - Automatic type conversion from strings
# - Error handling for exceptions
# - Logging to SQLite database
```

### Checking Logs
```bash
# View recent logs
sqlite3 ~/Library/Application\ Support/{{ cookiecutter.project_slug }}/logs.db \
  "SELECT * FROM unified_logs ORDER BY timestamp DESC LIMIT 10;"

# View tool execution times
sqlite3 ~/Library/Application\ Support/{{ cookiecutter.project_slug }}/logs.db \
  "SELECT tool_name, duration_ms, status FROM unified_logs WHERE tool_name IS NOT NULL;"
```

### Using Streamlit UI
```bash
# Start the admin UI
streamlit run {{ cookiecutter.project_slug }}/ui/app.py

# Navigate to Logs page to:
# - View execution history
# - Filter by tool name, status, date
# - Export logs as CSV
# - See error details
```

## Debugging Common Issues

### "kwargs" appears in MCP Inspector
**Problem**: Function signature is hidden by improper wrapping
**Solution**: Ensure tool is in example_tools or parallel_example_tools list, not manually decorated

### Type conversion not working
**Problem**: Parameters arriving as strings
**Solution**: 
1. Ensure type_converter decorator is applied (check server/app.py)
2. Use type hints in function signature
3. Check that parameter names match exactly

### Parallel tool running sequentially
**Problem**: Tool not in parallel_example_tools list
**Solution**: Add tool to parallel_example_tools in tools/__init__.py

### Logs not appearing
**Problem**: Logging not initialized or database error
**Solution**:
1. Check UnifiedLogger initialization in server/app.py
2. Verify database path permissions
3. Check for initialization errors in server output

## Architecture Details

### Decorator Order Matters
The order ensures proper functionality:
1. Type conversion happens first (innermost)
2. Then exception handling wraps that
3. Then logging wraps everything
4. Finally parallelization (if needed) wraps all

### Correlation IDs
Every request gets a unique correlation ID that flows through all decorators and logs, making it easy to track a single request across multiple log entries.

### Database Schema
```sql
CREATE TABLE unified_logs (
    id INTEGER PRIMARY KEY,
    correlation_id TEXT,
    timestamp TEXT,
    level TEXT,
    log_type TEXT,
    message TEXT,
    tool_name TEXT,
    duration_ms REAL,
    status TEXT,
    input_args TEXT,  -- JSON
    output_summary TEXT,
    error_message TEXT,
    -- ... additional fields
);
```

## Quick Reference

- **Config Location**: `~/Library/Application Support/{{ cookiecutter.project_slug }}/` (macOS)
- **Log Database**: `~/Library/Application Support/{{ cookiecutter.project_slug }}/logs.db`
- **Tools Directory**: `{{ cookiecutter.project_slug }}/tools/`
- **Decorators**: `{{ cookiecutter.project_slug }}/decorators/`
- **Server**: `{{ cookiecutter.project_slug }}/server/app.py`

For more implementation details, see `docs/DECORATOR_PATTERNS.md`.