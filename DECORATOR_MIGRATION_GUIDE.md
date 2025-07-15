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

## Complete Decorator Implementations

### 1. Exception Handler (SAAGA Pattern)

```python
"""Exception handling decorator for MCP tools - SAAGA Pattern.

This decorator provides graceful error handling following SAAGA standards:
- Async-only pattern
- Standard SAAGA error response format
- Full traceback preservation
"""

import asyncio
from functools import wraps
from typing import Callable, Any, Awaitable
import logging
import traceback

logger = logging.getLogger(__name__)


def exception_handler(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """Decorator to handle exceptions in MCP tools gracefully - SAAGA Pattern.
    
    Args:
        func: The async function to decorate
        
    Returns:
        The decorated async function with exception handling
    """
    
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log the full traceback for debugging
            tb_str = traceback.format_exc()
            logger.error(f"Exception in {func.__name__}: {tb_str}")
            
            # Return SAAGA-format error response
            return {
                "Status": "Exception",
                "Message": str(e),
                "ExceptionType": type(e).__name__,
                "Traceback": tb_str
            }
    
    return wrapper
```

### 2. Tool Logger (SAAGA Pattern with SQLite)

```python
"""Tool logging decorator for MCP tools - SAAGA Pattern.

This decorator provides comprehensive logging following SAAGA standards:
- Async-only pattern
- SQLite database integration
- Performance timing
- Input/output logging
"""

import asyncio
import time
from functools import wraps
from typing import Callable, Any, Awaitable
import logging
import json

from .sqlite_logger import log_tool_execution

logger = logging.getLogger(__name__)


def tool_logger(func: Callable[..., Awaitable[Any]], config: dict = None) -> Callable[..., Awaitable[Any]]:
    """Decorator to log MCP tool execution - SAAGA Pattern.
    
    Args:
        func: The async function to decorate
        config: Optional configuration dictionary
        
    Returns:
        The decorated async function with logging
    """
    
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        tool_name = func.__name__
        
        # Log input parameters (sanitized)
        try:
            input_args = json.dumps({"args": args, "kwargs": kwargs}, default=str)
        except Exception:
            input_args = f"args={len(args)}, kwargs={len(kwargs)}"
        
        logger.info(f"Starting tool: {tool_name}")
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            try:
                output_summary = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            except Exception:
                output_summary = f"<{type(result).__name__}>"
            
            # Log to SQLite database
            log_tool_execution(
                tool_name=tool_name,
                duration_ms=duration_ms,
                status="success",
                input_args=input_args,
                output_summary=output_summary,
                error_message=None
            )
            
            logger.info(f"Completed tool: {tool_name} in {duration_ms}ms")
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log failed execution
            log_tool_execution(
                tool_name=tool_name,
                duration_ms=duration_ms,
                status="error",
                input_args=input_args,
                output_summary=None,
                error_message=str(e)
            )
            
            logger.error(f"Tool {tool_name} failed after {duration_ms}ms: {e}")
            raise  # Re-raise for exception_handler
    
    return wrapper
```

### 3. Parallelize Decorator (SAAGA Pattern)

```python
"""Parallelization decorator for MCP tools - SAAGA Pattern.

This decorator transforms function signatures to accept List[Dict] parameters
for parallel execution following SAAGA standards:
- Async-only pattern
- Signature transformation: func(args) → func(kwargs_list: List[Dict])
- Batch processing support
"""

import asyncio
from functools import wraps
from typing import Callable, Any, Awaitable, List, Dict
import logging

logger = logging.getLogger(__name__)


def parallelize(func: Callable[..., Awaitable[Any]]) -> Callable[[List[Dict]], Awaitable[List[Any]]]:
    """Decorator to enable parallel execution of MCP tools - SAAGA Pattern.
    
    Transforms function signature from:
        async def func(param1: str, param2: int) -> str
    To:
        async def func(kwargs_list: List[Dict]) -> List[str]
    
    Args:
        func: The async function to decorate
        
    Returns:
        The decorated function that accepts List[Dict] and returns List[results]
    """
    
    @wraps(func)
    async def wrapper(kwargs_list: List[Dict]) -> List[Any]:
        """Execute function in parallel for each kwargs dict."""
        
        if not isinstance(kwargs_list, list):
            raise ValueError("Parallel tools require List[Dict] parameter")
        
        logger.info(f"Parallel execution of {func.__name__} with {len(kwargs_list)} items")
        
        # Execute all calls concurrently
        tasks = []
        for kwargs in kwargs_list:
            if not isinstance(kwargs, dict):
                raise ValueError("Each item in kwargs_list must be a dict")
            task = func(**kwargs)
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error format for consistency
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "Status": "Exception",
                    "Message": str(result),
                    "ExceptionType": type(result).__name__,
                    "Index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    return wrapper
```

## Tool Migration Examples

### Converting Regular Tools to Async

**Before (sync):**
```python
def echo_tool(message: str) -> str:
    return f"Echo: {message}"
```

**After (async):**
```python
async def echo_tool(message: str) -> str:
    return f"Echo: {message}"
```

### Converting Parallel Tools

**Before (sync, single item):**
```python
def process_item(item: str) -> str:
    return item.upper()
```

**After (async, batch processing):**
```python
async def process_item(item: str) -> str:
    return item.upper()

# Note: parallelize decorator will transform this to:
# async def process_item(kwargs_list: List[Dict]) -> List[str]
```

## Tool Registration Updates

### Regular Tools
```python
# Apply decorators in order: exception_handler → tool_logger
for tool_func in regular_tools:
    decorated_func = exception_handler(tool_logger(tool_func, config))
    mcp_server.tool(name=tool_func.__name__)(decorated_func)
```

### Parallel Tools
```python
# Apply decorators in order: exception_handler → tool_logger → parallelize
for tool_func in parallel_tools:
    decorated_func = exception_handler(tool_logger(parallelize(tool_func), config))
    mcp_server.tool(name=tool_func.__name__)(decorated_func)
```

## Testing Parallel Tools

### MCP Inspector Usage
```python
# Regular tool call
result = await echo_tool(message="Hello")

# Parallel tool call (transformed signature)
results = await process_batch_data(kwargs_list=[
    {"item": "hello"},
    {"item": "world"},
    {"item": "test"}
])
```

### Expected Results
```python
# Regular tool result
"Echo: Hello"

# Parallel tool results
["HELLO", "WORLD", "TEST"]
```

## Migration Checklist

- [ ] Update exception_handler.py with SAAGA async-only pattern
- [ ] Update tool_logger.py with SAAGA async-only pattern  
- [ ] Implement parallelize.py with signature transformation
- [ ] Convert all example tools to async functions
- [ ] Update tool registration logic for parallel tools
- [ ] Test with MCP Inspector for correct signatures
- [ ] Verify error responses match SAAGA format
- [ ] Confirm SQLite logging still functions
- [ ] Update documentation for new calling conventions

## Breaking Changes

1. **All tools must be async**: No more sync function support
2. **Parallel tool signatures**: Accept `List[Dict]` instead of individual parameters
3. **Error format**: New SAAGA-standard error response format
4. **Client impact**: Code calling these tools may need updates

This migration ensures full compatibility with SAAGA base patterns while preserving our enhanced SQLite logging functionality.
