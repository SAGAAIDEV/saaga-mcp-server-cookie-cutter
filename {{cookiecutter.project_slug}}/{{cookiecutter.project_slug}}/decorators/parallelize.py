"""Parallelization decorator for MCP tools - SAAGA Pattern.

This decorator transforms function signatures to accept List[Dict] parameters
for parallel execution following SAAGA standards:
- Async-only pattern
- Signature transformation: func(args) → func(kwargs_list: List[Dict])
- Batch processing support
- Integration with SAAGA logging and error handling

Features:
- Automatic parallelization of compatible tools
- Signature transformation for batch processing
- Concurrent execution with asyncio.gather
- Error handling for individual batch items
- Graceful degradation for unsupported operations

Usage:
    @parallelize
    async def batch_process_tool(item: str) -> str:
        # Tool implementation that can be parallelized
        return processed_item
    
    # After decoration, signature becomes:
    # async def batch_process_tool(kwargs_list: List[Dict]) -> List[str]
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
        
        if not kwargs_list:
            logger.warning(f"Empty kwargs_list provided to {func.__name__}")
            return []
        
        logger.info(f"Parallel execution of {func.__name__} with {len(kwargs_list)} items")
        
        # Validate all items are dictionaries
        for i, kwargs in enumerate(kwargs_list):
            if not isinstance(kwargs, dict):
                raise ValueError(f"Item {i} in kwargs_list must be a dict, got {type(kwargs).__name__}")
        
        # Execute all calls concurrently
        tasks = []
        for i, kwargs in enumerate(kwargs_list):
            try:
                task = func(**kwargs)
                tasks.append(task)
            except Exception as e:
                # If function call fails immediately, create a failed task
                async def failed_task():
                    raise e
                tasks.append(failed_task())
        
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