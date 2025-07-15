# SAAGA Decorator Migration Guide

## Executive Summary

This guide provides a comprehensive plan to transition the cookie cutter template's decorator implementation from the current approach to match the SAAGA base implementation patterns. The migration preserves internal functionality while aligning external interfaces with SAAGA standards.

## Key Architectural Changes

### 1. **Async-Only Pattern**
- **Current**: Decorators support both sync and async functions
- **SAAGA**: All decorators are async-only
- **Impact**: All MCP tools must be converted to async functions

### 2. **Signature Transformation for Parallelization**
- **Current**: Decorators preserve original function signatures
- **SAAGA**: Parallelize decorator transforms signatures to accept `List[Dict[str, Any]]`
- **Impact**: Parallel tools will have completely different calling conventions

### 3. **Error Response Format**
- **Current**: `{"error": True, "error_type": "...", "error_message": "...", "tool": "..."}`
- **SAAGA**: `{"Status": "Exception", "Message": "...", "ExceptionType": "...", "Traceback": "..."}`
- **Impact**: Error handling consistency across all tools

## Migration Steps

### Step 1: Update Exception Handler Decorator

**File**: `{{cookiecutter.project_slug}}/decorators/exception_handler.py`

```python
import functools
import traceback
from typing import Any, Callable, Dict, TypeVar, cast

T = TypeVar("T", bound=Callable[..., Any])

def exception_handler(func: T) -> T:
    """SAAGA-compatible exception handler decorator.
    
    Async-only decorator that catches exceptions and returns
    standardized error responses.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.exception(tb_str)
            error_return = {
                "Status": "Exception",
                "Message": str(e),
                "ExceptionType": type(e).__name__,
                "Traceback": tb_str,
            }
            return error_return
    
    return cast(T, wrapper)
```

### Step 2: Update Tool Logger Decorator

**File**: `{{cookiecutter.project_slug}}/decorators/tool_logger.py`

```python
import functools
import time
from typing import Any, Callable, TypeVar, cast
from {{cookiecutter.project_slug}}.decorators.sqlite_logger import log_tool_execution

T = TypeVar("T", bound=Callable[..., Any])

def tool_logger(func: T, config=None) -> T:
    """SAAGA-compatible tool logger with preserved SQLite functionality.
    
    Maintains internal SQLite logging while conforming to SAAGA's
    async-only pattern.
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        
        # Add tool context for logging
        logger.info(f"Executing tool: {func.__name__}")
        logger.debug(f"Input args: {args}, kwargs: {kwargs}")
        
        try:
            # Execute the async function
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log to SQLite (preserve our enhanced logging)
            log_tool_execution(
                tool_name=func.__name__,
                duration_ms=duration * 1000,
                status="success",
                input_args={"args": list(args), "kwargs": kwargs},
                output_summary=str(result)[:500]
            )
            
            logger.info(f"Tool {func.__name__} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error to SQLite
            log_tool_execution(
                tool_name=func.__name__,
                duration_ms=duration * 1000,
                status="error",
                input_args={"args": list(args), "kwargs": kwargs},
                error_message=str(e)[:500]
            )
            
            logger.error(f"Tool {func.__name__} failed after {duration:.3f}s: {e}")
            raise  # Re-raise for exception_handler to catch
    
    return cast(T, wrapper)
```

### Step 3: Implement SAAGA Parallelize Decorator

**File**: `{{cookiecutter.project_slug}}/decorators/parallelize.py`

```python
import asyncio
import functools
import inspect
from typing import Any, Callable, Coroutine, Dict, List, TypeVar, cast, get_type_hints

T = TypeVar("T", bound=Callable[..., Coroutine[Any, Any, Any]])

def _get_original_param_details(func: Callable) -> str:
    """Helper to format original parameter details for the docstring."""
    original_params_list = []
    try:
        sig = inspect.signature(func)
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}

        for name, param in sig.parameters.items():
            annotation_display = "Any"
            if name in type_hints:
                hint = type_hints[name]
                annotation_display = str(hint).replace('typing.', '')
            elif param.annotation is not inspect.Parameter.empty:
                annotation_display = str(param.annotation).replace('typing.', '')
            
            original_params_list.append(f" - `{name}: {annotation_display}`")
    except (ValueError, TypeError):
        pass
    
    return "\\n".join(original_params_list) if original_params_list else " - No parameters"

def parallelize(func: T) -> T:
    """SAAGA parallelize decorator that transforms function signatures.
    
    Transforms a function to accept a list of keyword argument dictionaries
    and executes them in parallel using asyncio.gather().
    
    Example:
        Original: async def process(item: str, operation: str) -> str
        After decoration: async def process(kwargs_list: List[Dict[str, Any]]) -> List[Any]
        
        Call as: results = await process([
            {"item": "apple", "operation": "upper"},
            {"item": "banana", "operation": "upper"}
        ])
    """
    
    @functools.wraps(func)
    async def wrapper(kwargs_list: List[Dict[str, Any]]) -> List[Any]:
        """Execute function in parallel with multiple parameter sets.
        
        Args:
            kwargs_list: List of dictionaries containing keyword arguments
                        for each parallel execution.
                        
        Returns:
            List of results in the same order as the input list.
            
        Raises:
            TypeError: If kwargs_list is not a list or contains non-dict items.
        """
        # Validate input
        if not isinstance(kwargs_list, list):
            raise TypeError(
                f"Expected list of dicts, got {type(kwargs_list).__name__}. "
                f"Original function parameters:\\n{_get_original_param_details(func)}"
            )
        
        for i, kwargs in enumerate(kwargs_list):
            if not isinstance(kwargs, dict):
                raise TypeError(
                    f"Expected dict at index {i}, got {type(kwargs).__name__}. "
                    f"Original function parameters:\\n{_get_original_param_details(func)}"
                )
        
        # Create tasks for parallel execution
        tasks = [func(**kwargs) for kwargs in kwargs_list]
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)
        
        return results
    
    # Update wrapper's docstring to include original parameters
    if func.__doc__:
        wrapper.__doc__ = (
            f"{func.__doc__}\\n\\n"
            f"**Parallelized Function**\\n"
            f"Original parameters:\\n{_get_original_param_details(func)}\\n\\n"
            f"Now accepts: kwargs_list: List[Dict[str, Any]]"
        )
    
    # Preserve the original function as an attribute for introspection
    wrapper._original_func = func
    
    return cast(T, wrapper)
```

### Step 4: Convert All Tools to Async

**Example conversion for existing tools:**

```python
# BEFORE (sync tool)
def echo_tool(message: str) -> str:
    """Echo back the input message."""
    return f"Echo: {message}"

# AFTER (async tool)
async def echo_tool(message: str) -> str:
    """Echo back the input message."""
    return f"Echo: {message}"

# For tools with time.sleep or I/O operations
import asyncio

# BEFORE
def process_batch_data(items: List[str], operation: str = "upper") -> List[Dict[str, Any]]:
    results = []
    for i, item in enumerate(items):
        time.sleep(0.1)  # Simulate processing
        # ... processing logic ...
    return results

# AFTER
async def process_batch_data(items: List[str], operation: str = "upper") -> List[Dict[str, Any]]:
    results = []
    for i, item in enumerate(items):
        await asyncio.sleep(0.1)  # Async sleep
        # ... processing logic ...
    return results
```

### Step 5: Update Tool Registration

**File**: `{{cookiecutter.project_slug}}/server/app.py`

```python
def register_tools(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Register tools with SAAGA decorators following SAAGA patterns."""
    
    # Import SAAGA decorators
    from {{ cookiecutter.project_slug }}.decorators.exception_handler import exception_handler
    from {{ cookiecutter.project_slug }}.decorators.tool_logger import tool_logger
    from {{ cookiecutter.project_slug }}.decorators.parallelize import parallelize
    
    # Register regular tools (no parallelization)
    for tool_func in example_tools:
        # Apply decorator chain: exception_handler → tool_logger
        # Order matters: exception handler is outermost
        decorated_func = exception_handler(tool_logger(tool_func, config))
        
        # Register with MCP
        mcp_server.tool(
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"{tool_func.__name__} - No description"
        )(decorated_func)
        
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    # Register parallel tools (with signature transformation)
    for tool_func in parallel_example_tools:
        # Apply decorator chain: exception_handler → tool_logger → parallelize
        # Parallelize is innermost, transforms the signature first
        decorated_func = exception_handler(
            tool_logger(
                parallelize(tool_func), 
                config
            )
        )
        
        # Update the description to indicate parallel execution
        description = (
            f"{tool_func.__doc__ or tool_func.__name__}\\n\\n"
            f"**Parallel Execution**: This tool accepts a list of parameter "
            f"dictionaries for batch processing."
        )
        
        # Register with MCP
        mcp_server.tool(
            name=tool_func.__name__,
            description=description
        )(decorated_func)
        
        logger.info(f"Registered parallel tool: {tool_func.__name__}")
```

### Step 6: Update Example Tools Usage

**For parallel tools, update documentation and examples:**

```python
# Example of calling a parallelized tool
# BEFORE: 
# result = process_batch_data(["apple", "banana"], "upper")

# AFTER:
result = await process_batch_data([
    {"items": ["apple"], "operation": "upper"},
    {"items": ["banana"], "operation": "upper"},
    {"items": ["cherry"], "operation": "upper"}
])
# Returns: [result1, result2, result3]
```

## Testing Strategy

### 1. Unit Tests for Decorators

```python
# Test exception handler
async def test_exception_handler():
    @exception_handler
    async def failing_tool():
        raise ValueError("Test error")
    
    result = await failing_tool()
    assert result["Status"] == "Exception"
    assert result["ExceptionType"] == "ValueError"
    assert result["Message"] == "Test error"

# Test parallelize
async def test_parallelize():
    @parallelize
    async def add(a: int, b: int) -> int:
        return a + b
    
    results = await add([
        {"a": 1, "b": 2},
        {"a": 3, "b": 4},
        {"a": 5, "b": 6}
    ])
    assert results == [3, 7, 11]
```

### 2. MCP Inspector Testing

1. Run the server with MCP Inspector
2. Verify regular tools show normal signatures
3. Verify parallel tools show `kwargs_list: List[Dict[str, Any]]` parameter
4. Test calling both tool types
5. Verify error responses match SAAGA format

### 3. Integration Testing

Test with actual MCP clients (Claude Desktop, etc.) to ensure:
- Tools are discoverable
- Parallel tools can be called with list of dicts
- Error handling works correctly
- Logging captures all tool executions

## Migration Checklist

- [ ] Convert all tools to async functions
- [ ] Update exception_handler.py to async-only with SAAGA error format
- [ ] Update tool_logger.py to async-only while preserving SQLite functionality
- [ ] Implement parallelize.py with signature transformation
- [ ] Update server/app.py registration logic
- [ ] Update all tool documentation to reflect async and parallel patterns
- [ ] Create unit tests for all decorators
- [ ] Test with MCP Inspector
- [ ] Test with real MCP clients
- [ ] Update README and examples

## Important Notes

1. **Breaking Change**: Parallel tools will have completely different signatures. Users must call them with `List[Dict]` instead of normal parameters.

2. **Async Requirement**: All tools must be async. This may require adding `asyncio.sleep(0)` in some places just to make them async.

3. **Error Format**: The new error format is more verbose but provides better debugging information with full tracebacks.

4. **Performance**: The parallel decorator truly enables concurrent execution, which can significantly improve performance for batch operations.

5. **Backwards Compatibility**: This is NOT backwards compatible. Existing users of tools will need to update their code.

## Rollback Plan

If issues arise:
1. Keep backup of current decorator implementations
2. The changes are isolated to decorator files and server registration
3. Tools themselves only need async/await added
4. Can revert decorator files and remove async keywords to restore original behavior