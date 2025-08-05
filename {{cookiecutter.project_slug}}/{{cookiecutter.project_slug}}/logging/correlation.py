"""
Correlation ID management for request tracking.

This module provides thread-safe correlation ID generation and propagation
using Python's contextvars to ensure IDs are properly isolated between
concurrent requests.
"""

from contextvars import ContextVar
from typing import Optional
from ulid import ULID


# Thread-safe context variable for storing correlation IDs
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

# Thread-safe context variable for storing tool names
tool_name_var: ContextVar[Optional[str]] = ContextVar('tool_name', default=None)

# Module-level initialization correlation ID for server startup
_initialization_correlation_id: Optional[str] = None


def generate_correlation_id() -> str:
    """Generate a unique correlation ID using ULID.
    
    ULID provides:
    - Lexicographically sortable IDs
    - Timestamp encoding in the first 48 bits (millisecond precision)
    - 80 bits of randomness 
    - 128-bit UUID compatibility
    - Case-insensitive encoding using Crockford's base32
    
    Returns:
        A unique ID in the format 'req_01ARZ3NDEKTSV4RRFFQ69G5FAV'
    """
    return f"req_{str(ULID())}"


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set the correlation ID for the current context.
    
    If no ID is provided, a new one will be generated. This ID will be
    available to all code running in the same async context.
    
    Args:
        correlation_id: Optional correlation ID to set. If None, generates a new one.
        
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID.
    
    Returns None if no correlation ID is set in the current context.
    This prevents auto-generation of IDs outside of explicit request contexts.
    
    Returns:
        The current correlation ID or None if not set
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear the correlation ID from the current context.
    
    This is typically called at the end of a request to ensure clean state.
    """
    correlation_id_var.set(None)


def set_initialization_correlation_id(correlation_id: str) -> None:
    """Set the module-level initialization correlation ID.
    
    This is used during server startup to provide a consistent correlation ID
    across all initialization logs, regardless of async context boundaries.
    
    Args:
        correlation_id: The initialization correlation ID to set
    """
    global _initialization_correlation_id
    _initialization_correlation_id = correlation_id


def get_initialization_correlation_id() -> Optional[str]:
    """Get the current initialization correlation ID.
    
    Returns:
        The initialization correlation ID or None if not set
    """
    return _initialization_correlation_id


def clear_initialization_correlation_id() -> None:
    """Clear the initialization correlation ID.
    
    This should be called after server initialization is complete.
    """
    global _initialization_correlation_id
    _initialization_correlation_id = None


def set_tool_name(tool_name: str) -> None:
    """Set the tool name for the current context.
    
    This is typically called by the tool_logger decorator at the start of
    tool execution to make the tool name available to all logging within
    that tool's execution context.
    
    Args:
        tool_name: The name of the tool being executed
    """
    tool_name_var.set(tool_name)


def get_tool_name() -> Optional[str]:
    """Get the current tool name from context.
    
    Returns None if no tool name is set in the current context.
    
    Returns:
        The current tool name or None if not set
    """
    return tool_name_var.get()


def clear_tool_name() -> None:
    """Clear the tool name from the current context.
    
    This is typically called by the tool_logger decorator at the end of
    tool execution to ensure clean state.
    """
    tool_name_var.set(None)


class CorrelationContext:
    """Context manager for correlation ID scope.
    
    This ensures a correlation ID is set for the duration of a block and
    optionally cleaned up afterwards.
    
    Example:
        async with CorrelationContext() as correlation_id:
            # All code here will have access to the same correlation ID
            logger.info("Processing request")
    """
    
    def __init__(self, correlation_id: Optional[str] = None, clear_on_exit: bool = True):
        """Initialize the correlation context.
        
        Args:
            correlation_id: Optional correlation ID to use. If None, generates a new one.
            clear_on_exit: Whether to clear the correlation ID when exiting the context.
        """
        self.correlation_id = correlation_id
        self.clear_on_exit = clear_on_exit
        self._previous_id: Optional[str] = None
    
    def __enter__(self) -> str:
        """Enter the correlation context."""
        self._previous_id = correlation_id_var.get()
        return set_correlation_id(self.correlation_id)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the correlation context."""
        if self.clear_on_exit:
            clear_correlation_id()
        elif self._previous_id is not None:
            correlation_id_var.set(self._previous_id)
    
    async def __aenter__(self) -> str:
        """Async enter the correlation context."""
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async exit the correlation context."""
        return self.__exit__(exc_type, exc_val, exc_tb)