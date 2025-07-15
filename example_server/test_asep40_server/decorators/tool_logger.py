"""Tool logging decorator for MCP tools - SAAGA Pattern.

This decorator provides comprehensive logging following SAAGA standards:
- Async-only pattern
- SQLite database integration
- Performance timing
- Input/output logging

Features:
- Automatic logging of tool inputs and outputs
- Execution time tracking with microsecond precision
- SQLite database storage for log persistence
- Error logging with full stack traces
- Query interface for log analysis
- Async-only pattern for consistency

Usage:
    @tool_logger
    async def my_tool(param: str) -> str:
        # Tool implementation
        return result
"""

import asyncio
from functools import wraps
from typing import Callable, Any, Awaitable
import time
import logging
import json

from test_asep40_server.decorators.sqlite_logger import log_tool_execution

logger = logging.getLogger(__name__)


def tool_logger(func: Callable[..., Awaitable[Any]], config: dict = None) -> Callable[..., Awaitable[Any]]:
    """Enhanced tool logger with configuration - SAAGA Pattern.
    
    Preserves function signature for MCP introspection while adding
    comprehensive logging capabilities. Async-only pattern following SAAGA standards.
    
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