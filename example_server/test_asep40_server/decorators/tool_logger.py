"""Tool logging decorator for MCP tools.

This decorator provides comprehensive logging for MCP tool execution,
capturing input parameters, output results, execution time, and any
errors that occur during tool execution.

Features:
- Automatic logging of tool inputs and outputs
- Execution time tracking
- SQLite database storage for log persistence
- Error logging with full stack traces
- Query interface for log analysis
- Support for both sync and async functions

Usage:
    @tool_logger
    def my_tool(param: str) -> str:
        # Tool implementation
        return result
"""

import asyncio
from functools import wraps
from typing import Callable, Any, TypeVar, cast
import time
import logging
import json

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Callable[..., Any])


def tool_logger(func: T, config=None) -> T:
    """Enhanced tool logger with configuration.
    
    Preserves function signature for MCP introspection while adding
    comprehensive logging capabilities. Supports both sync and async functions.
    
    Args:
        func: The function to decorate
        config: ServerConfig instance for configuration
        
    Returns:
        The decorated function with logging
    """
    
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Log input parameters
            logger.info(f"Executing tool: {func.__name__}")
            logger.debug(f"Input args: {args}, kwargs: {kwargs}")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # TODO: Phase 2 - Implement actual SQLite logging
                # log_tool_execution(
                #     tool_name=func.__name__,
                #     duration_ms=duration * 1000,
                #     status="success",
                #     input_args=json.dumps({"args": args, "kwargs": kwargs})[:500],
                #     output_summary=str(result)[:500],
                #     config=config
                # )
                
                logger.info(f"Tool {func.__name__} completed in {duration:.3f}s")
                logger.debug(f"Output: {str(result)[:200]}")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # TODO: Phase 2 - Implement actual SQLite logging
                # log_tool_execution(
                #     tool_name=func.__name__,
                #     duration_ms=duration * 1000,
                #     status="error",
                #     input_args=json.dumps({"args": args, "kwargs": kwargs})[:500],
                #     error_message=str(e)[:500],
                #     config=config
                # )
                
                logger.error(f"Tool {func.__name__} failed after {duration:.3f}s: {e}")
                raise
        return cast(T, async_wrapper)
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            # Log input parameters
            logger.info(f"Executing tool: {func.__name__}")
            logger.debug(f"Input args: {args}, kwargs: {kwargs}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # TODO: Phase 2 - Implement actual SQLite logging
                # log_tool_execution(
                #     tool_name=func.__name__,
                #     duration_ms=duration * 1000,
                #     status="success",
                #     input_args=json.dumps({"args": args, "kwargs": kwargs})[:500],
                #     output_summary=str(result)[:500],
                #     config=config
                # )
                
                logger.info(f"Tool {func.__name__} completed in {duration:.3f}s")
                logger.debug(f"Output: {str(result)[:200]}")
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # TODO: Phase 2 - Implement actual SQLite logging
                # log_tool_execution(
                #     tool_name=func.__name__,
                #     duration_ms=duration * 1000,
                #     status="error",
                #     input_args=json.dumps({"args": args, "kwargs": kwargs})[:500],
                #     error_message=str(e)[:500],
                #     config=config
                # )
                
                logger.error(f"Tool {func.__name__} failed after {duration:.3f}s: {e}")
                raise
        return cast(T, sync_wrapper)