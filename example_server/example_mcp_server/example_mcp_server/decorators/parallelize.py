"""Parallelization decorator for MCP tools - SAAGA Pattern.

This decorator transforms function signatures to accept List[Dict] parameters
for parallel execution following SAAGA standards:
- Async-only pattern
- Signature transformation: func(args) → func(kwargs_list: List[Dict])
- Batch processing support
- Integration with SAAGA logging and error handling
- Fail-fast behavior: if any item fails, the entire batch fails

Features:
- Automatic parallelization of compatible tools
- Signature transformation for batch processing
- Concurrent execution with asyncio.gather
- Fail-fast error handling (SAAGA standard)
- Type validation for input parameters

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
from typing import Callable, Any, Awaitable, List, Dict, Union
import logging
import inspect

logger = logging.getLogger(__name__)


def _set_parallelized_signature_and_annotations(
    wrapper_func: Callable, 
    param_name: str, 
    param_annotation: Any, 
    return_annotation: Any
):
    """Sets the __signature__ and __annotations__ for the wrapper function."""
    new_param = inspect.Parameter(
        name=param_name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=param_annotation
    )
    
    new_sig = inspect.Signature(
        parameters=[new_param],
        return_annotation=return_annotation
    )
    
    wrapper_func.__signature__ = new_sig
    wrapper_func.__annotations__ = {
        param_name: param_annotation,
        'return': return_annotation
    }

def _build_parallelized_docstring(func: Callable) -> str:
    """Constructs the docstring for the parallelized wrapper function."""
    original_doc = func.__doc__.strip() if func.__doc__ else "No original docstring provided."
    func_name = func.__name__
    
    sig = inspect.signature(func)
    params = []
    for name, param in sig.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            params.append(f"{name}: {param.annotation}")
        else:
            params.append(name)
    params_str = ", ".join(params)

    return f"""Parallelized version of `{func_name}`.

This function accepts a list of keyword argument dictionaries and executes
`{func_name}` concurrently for each set of arguments.

Original function signature: {func_name}({params_str})

Args:
    kwargs_list (List[Dict[str, Any]]): A list of dictionaries, where each
                                      dictionary provides the keyword arguments
                                      for a single call to `{func_name}`.

Returns:
    List[Any]: A list containing the results of each call to `{func_name}`,
               in the same order as the input `kwargs_list`.

Original docstring:
{original_doc}
"""


def parallelize(func: Callable[..., Awaitable[Any]]) -> Callable[[List[Dict]], Awaitable[List[Any]]]:
    """Decorator to enable parallel execution of MCP tools - SAAGA Pattern.
    
    Transforms function signature from:
        async def func(param1: str, param2: int) -> str
    To:
        async def func(kwargs_list: List[Dict]) -> List[str]
    
    Uses fail-fast behavior: if any task fails, the entire batch fails immediately.
    This maintains SAAGA compatibility and prevents partial results.
    
    The decorator preserves the original function's parameter information for
    better introspection and documentation, while transforming the execution
    signature to accept batch parameters.
    
    Args:
        func: The async function to decorate
        
    Returns:
        The decorated function that accepts List[Dict] and returns List[results]
        
    Raises:
        TypeError: If kwargs_list is not a List[Dict]
        Exception: Any exception from the first failing task (fail-fast)
    """
    
    # Store original function signature for introspection
    original_signature = inspect.signature(func)
    
    @wraps(func)
    async def wrapper(kwargs_list: List[Dict]) -> List[Any]:
        """Execute function in parallel for each kwargs dict."""
        
        if not isinstance(kwargs_list, list):
            raise TypeError("Parallel tools require List[Dict] parameter")
        
        if not kwargs_list:
            logger.warning(f"Empty kwargs_list provided to {func.__name__}")
            return []
        
        logger.info(f"Parallel execution of {func.__name__} with {len(kwargs_list)} items")
        
        # Validate all items are dictionaries
        for i, kwargs in enumerate(kwargs_list):
            if not isinstance(kwargs, dict):
                raise TypeError(f"Item {i} in kwargs_list must be a dict, got {type(kwargs).__name__}")
        
        # Execute all calls concurrently
        tasks = []
        for i, kwargs in enumerate(kwargs_list):
            try:
                # Validate parameters against original function signature
                bound_args = original_signature.bind(**kwargs)
                bound_args.apply_defaults()
                
                task = func(**kwargs)
                tasks.append(task)
            except Exception as e:
                # If function call fails immediately, create a failed task
                async def failed_task():
                    raise e
                tasks.append(failed_task())
        
        # Wait for all tasks to complete - SAAGA fail-fast behavior
        results = await asyncio.gather(*tasks)
        
        return results
    
    # Update the docstring and signature for the wrapper function
    wrapper.__doc__ = _build_parallelized_docstring(func)
    _set_parallelized_signature_and_annotations(
        wrapper_func=wrapper,
        param_name="kwargs_list",
        param_annotation=List[Dict[str, Any]],
        return_annotation=List[Any]
    )
    
    return wrapper