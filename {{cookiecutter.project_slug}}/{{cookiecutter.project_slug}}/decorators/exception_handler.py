"""Exception handling decorator for MCP tools.

This decorator provides graceful error handling and recovery for MCP tools,
ensuring that tool failures don't crash the server and provide meaningful
error messages to users.

Features:
- Automatic exception catching and logging
- Graceful error recovery with fallback responses
- User-friendly error messages
- Integration with SAAGA logging system
- Support for both sync and async functions

Usage:
    @exception_handler
    def my_tool(param: str) -> str:
        # Tool implementation
        return result
"""

import asyncio
from functools import wraps
from typing import Callable, Any, TypeVar, cast
import logging
import traceback

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Callable[..., Any])


def exception_handler(func: T) -> T:
    """Decorator to handle exceptions in MCP tools gracefully.
    
    Preserves function signature for MCP introspection while adding
    exception handling capabilities. Supports both sync and async functions.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function with exception handling
    """
    
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Log the full traceback for debugging
                tb_str = traceback.format_exc()
                logger.error(f"Exception in {func.__name__}: {tb_str}")
                
                # Return error dict that will be serialized
                return {
                    "error": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "tool": func.__name__
                }
        return cast(T, async_wrapper)
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the full traceback for debugging
                tb_str = traceback.format_exc()
                logger.error(f"Exception in {func.__name__}: {tb_str}")
                
                # Return error dict that will be serialized
                return {
                    "error": True,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "tool": func.__name__
                }
        return cast(T, sync_wrapper)