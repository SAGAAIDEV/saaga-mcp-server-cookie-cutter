"""Tool logging decorator for MCP tools - SAAGA Pattern.

This decorator provides comprehensive logging following SAAGA standards:
- Async-only pattern
- Unified logging with correlation IDs
- Performance timing
- Input/output logging

Features:
- Automatic logging of tool inputs and outputs
- Execution time tracking with microsecond precision
- Unified logging system with pluggable destinations
- Correlation ID tracking across related logs
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
import json

from {{ cookiecutter.project_slug }}.logging.correlation import set_correlation_id, get_correlation_id, clear_correlation_id, generate_correlation_id
from {{ cookiecutter.project_slug }}.logging.unified_logger import UnifiedLogger


def tool_logger(func: Callable[..., Awaitable[Any]] = None, config: dict = None) -> Callable[..., Awaitable[Any]]:
    """Enhanced tool logger with configuration - SAAGA Pattern.
    
    Preserves function signature for MCP introspection while adding
    comprehensive logging capabilities. Async-only pattern following SAAGA standards.
    
    Can be used as:
        @tool_logger
        async def my_tool(...): ...
        
    Or with config:
        decorated = tool_logger(my_tool, config)
    
    Args:
        func: The async function to decorate
        config: Optional configuration dictionary
        
    Returns:
        The decorated async function with logging
    """
    
    def decorator(f: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(f)
        async def wrapper(*args, **kwargs) -> Any:
            # Check for client-provided correlation ID in MCP metadata
            correlation_id = None
            if kwargs.get('_meta') and isinstance(kwargs['_meta'], dict):
                correlation_id = kwargs['_meta'].get('correlation_id')
                # Remove _meta from kwargs so it doesn't get passed to the tool
                kwargs.pop('_meta', None)
            
            # If no client-provided ID, generate one
            if not correlation_id:
                correlation_id = f"req_{generate_correlation_id().split('_')[1]}"
            
            # Set the correlation ID for this execution context
            set_correlation_id(correlation_id)
            
            # Get correlation-aware logger
            logger = UnifiedLogger.get_logger(f"tool.{f.__name__}")
            
            start_time = time.time()
            tool_name = f.__name__
            
            # Prepare input args for logging
            # MCP passes parameters directly as keyword arguments
            try:
                # For MCP tools, we only have kwargs (no positional args)
                input_args_dict = kwargs if kwargs else {}
                input_args_str = json.dumps(input_args_dict, default=str)
            except Exception:
                input_args_dict = {}
                input_args_str = f"<{len(kwargs)} parameters>"
            
            logger.info(
                f"Starting tool: {tool_name}",
                log_type="tool_execution",
                tool_name=tool_name,
                status="running",
                input_args=input_args_dict
            )
            
            try:
                result = await f(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Prepare output summary
                try:
                    output_summary = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                except Exception:
                    output_summary = f"<{type(result).__name__}>"
                
                logger.info(
                    f"Tool completed: {tool_name}",
                    log_type="tool_execution",
                    tool_name=tool_name,
                    duration_ms=duration_ms,
                    status="success",
                    input_args=input_args_dict,
                    output_summary=output_summary
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Tool failed: {tool_name}",
                    log_type="tool_execution",
                    tool_name=tool_name,
                    duration_ms=duration_ms,
                    status="error",
                    input_args=input_args_dict,
                    error_message=str(e)
                )
                
                raise  # Re-raise for exception_handler
            finally:
                # Clear correlation ID after tool execution
                clear_correlation_id()
        
        return wrapper
    
    # Handle being called as @tool_logger (without parentheses)
    if func is not None:
        return decorator(func)
    
    # Handle being called as tool_logger(func, config)
    return decorator