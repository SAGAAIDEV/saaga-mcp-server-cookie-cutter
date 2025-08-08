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
- Client-provided correlation ID support via MCP metadata
- Error logging with full stack traces
- Query interface for log analysis
- Async-only pattern for consistency

Usage:
    @tool_logger
    async def my_tool(param: str) -> str:
        # Tool implementation
        return result

Correlation ID Support:
    MCP clients can pass a correlation ID through request metadata:
    - Client includes {"correlationId": "client_req_123"} in _meta field
    - Decorator checks ctx.request_context.meta for correlationId
    - Uses client-provided ID if present, otherwise generates one
    - Enables end-to-end request tracing from frontend to backend
"""

import asyncio
from functools import wraps
from typing import Callable, Any, Awaitable
import time
import json
import inspect

from mcp.server.fastmcp import Context

from sizzle_mcp_server.logging.correlation import set_correlation_id, get_correlation_id, clear_correlation_id, generate_correlation_id
from sizzle_mcp_server.logging.unified_logger import UnifiedLogger


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
        # Check if MCP client provided a correlation ID via context metadata
        correlation_id = None
        
        # Get function signature to find Context parameter
        sig = inspect.signature(func)
        params = sig.parameters
        
        # Check if function expects a Context parameter
        context_param_name = None
        for param_name, param in params.items():
            if param.annotation == Context or param_name == 'ctx':
                context_param_name = param_name
                break
        
        # Extract Context from kwargs if present
        ctx = None
        if context_param_name and context_param_name in kwargs:
            ctx = kwargs[context_param_name]
            
            # Extract correlation ID from context metadata
            if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
                meta = ctx.request_context.meta
                if meta:
                    # Meta can be a dict or object with attributes
                    if hasattr(meta, 'get'):
                        correlation_id = meta.get('correlationId')
                    elif hasattr(meta, 'correlationId'):
                        correlation_id = getattr(meta, 'correlationId', None)
        
        # If no correlation ID from client, generate one
        if not correlation_id:
            correlation_id = f"req_{generate_correlation_id().split('_')[1]}"
        
        # Set the correlation ID for this request
        set_correlation_id(correlation_id)
        
        # Get correlation-aware logger
        logger = UnifiedLogger.get_logger(f"tool.{func.__name__}")
        
        start_time = time.time()
        tool_name = func.__name__
        
        # Prepare input args for logging
        # MCP passes parameters directly as keyword arguments
        try:
            # For MCP tools, we only have kwargs (no positional args)
            # Exclude Context objects which can't be pickled
            input_args_dict = {k: v for k, v in kwargs.items() if not isinstance(v, Context)} if kwargs else {}
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
            result = await func(*args, **kwargs)
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