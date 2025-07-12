# SAAGA Decorator Patterns in {{ cookiecutter.project_name }}

This document explains the decorator patterns used in your MCP server and provides guidance on when and how to use them.

## Overview

Your MCP server automatically applies SAAGA decorators to all tools. These decorators provide:
- **Exception handling**: Consistent error responses
- **Logging**: Comprehensive execution tracking
- **Parallelization**: Concurrent execution for suitable tools

## The Three Decorators

### 1. Exception Handler (Applied to ALL tools)

The exception handler ensures consistent error handling across all tools:

```python
@exception_handler
def my_tool(param: str) -> dict:
    if not param:
        raise ValueError("Parameter required")
    return {"result": param.upper()}
```

**What it does:**
- Catches any exception thrown by your tool
- Returns a structured error response that MCP clients understand
- Logs the error with full stack trace
- Your tool can raise exceptions freely

### 2. Tool Logger (Applied to ALL tools)

Tracks execution metrics and logs all tool invocations:

```python
# Automatically applied - you don't need to do anything
def my_tool(param: str) -> dict:
    # Logger tracks:
    # - Start time
    # - Input parameters
    # - Execution duration
    # - Output (summarized)
    # - Any errors
    return {"result": "processed"}
```

**What it logs:**
- Tool name and parameters
- Execution time in milliseconds
- Success/failure status
- Output summary (first 500 chars)
- Error messages and stack traces

### 3. Parallelize (Applied ONLY to specific tools)

**⚠️ IMPORTANT**: This decorator is only applied to tools in the `parallel_example_tools` list.

## When to Use the Parallelize Decorator

The parallelize decorator is **NOT** suitable for all tools. Use it ONLY when:

### ✅ Good Candidates for Parallelization

1. **Batch Processing Tools**
   ```python
   def process_batch_data(items: List[str]) -> List[dict]:
       """Process multiple independent items."""
       results = []
       for item in items:
           # Each item processed independently
           results.append(expensive_computation(item))
       return results
   ```

2. **Independent Computations**
   ```python
   def analyze_documents(doc_ids: List[str]) -> List[dict]:
       """Analyze multiple documents independently."""
       return [analyze_single_doc(doc_id) for doc_id in doc_ids]
   ```

3. **Parallel API Calls**
   ```python
   def fetch_multiple_resources(urls: List[str]) -> List[dict]:
       """Fetch multiple URLs in parallel."""
       return [fetch_url(url) for url in urls]
   ```

### ❌ Bad Candidates for Parallelization

1. **Sequential Operations**
   ```python
   def sequential_process(data: str) -> str:
       """Operations that depend on order."""
       step1 = process_step1(data)
       step2 = process_step2(step1)  # Depends on step1
       return process_step3(step2)   # Depends on step2
   ```

2. **Shared State Operations**
   ```python
   def update_database(records: List[dict]) -> dict:
       """Operations that modify shared state."""
       # Database transactions need careful handling
       # NOT suitable for naive parallelization
   ```

3. **Single Item Operations**
   ```python
   def get_user_info(user_id: str) -> dict:
       """Single item operations don't benefit."""
       return fetch_user(user_id)
   ```

## How the Parallelize Decorator Works

The decorator detects if the input is iterable (list, tuple, etc.) and processes each item in parallel:

```python
# Original function
def process_item(item: str) -> dict:
    return expensive_computation(item)

# When called with a list, automatically parallelized:
result = process_item(["item1", "item2", "item3"])
# Returns: [result1, result2, result3]
```

## Adding Tools to Your Server

### Regular Tools (Most Common)

Add to the `example_tools` list in `tools/__init__.py`:

```python
# tools/my_tools.py
def my_regular_tool(param: str) -> dict:
    """A regular tool with automatic exception handling and logging."""
    return {"processed": param}

# tools/__init__.py
from .my_tools import my_regular_tool
example_tools.append(my_regular_tool)
```

### Parallel Tools (Use Sparingly)

Add to the `parallel_example_tools` list ONLY if suitable:

```python
# tools/batch_tools.py
def batch_processor(items: List[str]) -> List[dict]:
    """Process multiple items in parallel."""
    # Each item processed independently
    return [{"processed": item} for item in items]

# tools/__init__.py
from .batch_tools import batch_processor
parallel_example_tools.append(batch_processor)
```

## Understanding the Registration Process

Your server's `app.py` automatically applies decorators in the correct order:

```python
# For regular tools:
# exception_handler → tool_logger → your function
decorated = exception_handler(tool_logger(your_tool))

# For parallel tools:
# exception_handler → tool_logger → parallelize → your function
decorated = exception_handler(tool_logger(parallelize(your_tool)))
```

## Common Patterns and Examples

### Pattern 1: Type Conversion

MCP passes parameters as strings. Handle conversion in your tools:

```python
def calculate(a: str, b: str) -> dict:
    """Handle string inputs from MCP."""
    try:
        num_a = float(a)
        num_b = float(b)
        return {"sum": num_a + num_b}
    except ValueError as e:
        # Exception handler will catch and format this
        raise ValueError(f"Invalid number format: {e}")
```

### Pattern 2: Async Tools

Both sync and async tools are supported:

```python
async def fetch_data(url: str) -> dict:
    """Async tools work automatically."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return {"data": await response.json()}
```

### Pattern 3: Progress Reporting

For long-running operations, log progress:

```python
import logging
logger = logging.getLogger(__name__)

def long_operation(data: str) -> dict:
    """Log progress for long operations."""
    logger.info("Starting phase 1...")
    result1 = phase1(data)
    
    logger.info("Starting phase 2...")
    result2 = phase2(result1)
    
    logger.info("Operation complete")
    return {"result": result2}
```

## Debugging Your Tools

1. **Check MCP Inspector Output**
   - Parameters should show proper names (not "kwargs")
   - Return values should be JSON-serializable

2. **Enable Debug Logging**
   ```bash
   python -m {{ cookiecutter.project_slug }}.server.app --log-level DEBUG
   ```

3. **Check SQLite Logs**
   - Location: `{{ cookiecutter.project_slug }}/logs.db`
   - Contains all tool executions with timings

4. **Test Parallelization**
   ```python
   # Test with small batches first
   result = parallel_tool(["item1", "item2"])
   # Verify results are in correct order
   ```

## Best Practices

1. **Let exceptions bubble up** - The exception handler will catch them
2. **Return JSON-serializable data** - dict, list, str, int, float, bool
3. **Use type hints** - Helps with documentation and IDE support
4. **Log important operations** - Use the standard logging module
5. **Test with MCP Inspector** - Verify parameters and outputs
6. **Be careful with parallelization** - Only use when truly beneficial

## Summary

- **All tools** get exception handling and logging automatically
- **Only specific tools** get parallelization (those in `parallel_example_tools`)
- Parallelization is for batch/independent operations only
- The decorators preserve function signatures for MCP introspection
- You don't manually apply decorators - the server does it for you