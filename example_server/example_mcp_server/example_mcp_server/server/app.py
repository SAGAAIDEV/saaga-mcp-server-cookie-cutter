"""Example MCP Server - MCP Server with SAAGA Decorators

This module implements the core MCP server using FastMCP with dual transport support
and automatic application of SAAGA decorators (exception handling, logging, parallelization).
"""

import asyncio
import sys
from typing import Optional, Callable, Any

import click
from mcp import types
from mcp.server.fastmcp import FastMCP

from example_mcp_server.config import ServerConfig, get_config
from example_mcp_server.logging_config import setup_logging, logger
from example_mcp_server.tools.example_tools import example_tools, parallel_example_tools
def create_mcp_server(config: Optional[ServerConfig] = None) -> FastMCP:
    """Create and configure the MCP server with SAAGA decorators.
    
    Args:
        config: Optional server configuration
        
    Returns:
        Configured FastMCP server instance
    """
    if config is None:
        config = get_config()
    
    # Set up logging first using reference implementation pattern
    setup_logging(config)
    
    mcp_server = FastMCP(config.name or "Example MCP Server")
    
    # Register all tools with the server
    register_tools(mcp_server, config)
    return mcp_server


def register_tools(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Register all MCP tools with the server using SAAGA decorators.
    
    Registers decorated functions directly with MCP to preserve function signatures
    for proper parameter introspection.
    """
    
    # Import SAAGA decorators
    from example_mcp_server.decorators.exception_handler import exception_handler
    from example_mcp_server.decorators.tool_logger import tool_logger
    from example_mcp_server.decorators.parallelize import parallelize
    
    # Register regular tools with SAAGA decorators
    for tool_func in example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger
        decorated_func = exception_handler(tool_logger(tool_func, config.__dict__))
        
        # Extract metadata from the original function
        tool_name = tool_func.__name__
        
        # Register the decorated function directly with MCP
        # This preserves the function signature for parameter introspection
        mcp_server.tool(
            name=tool_name
        )(decorated_func)
        
        logger.info(f"Registered tool: {tool_name}")
    
    # Register parallel tools with SAAGA decorators  
    for tool_func in parallel_example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
        decorated_func = exception_handler(tool_logger(parallelize(tool_func), config.__dict__))
        
        # Extract metadata
        tool_name = tool_func.__name__
        
        # Register directly with MCP
        mcp_server.tool(
            name=tool_name
        )(decorated_func)
        
        logger.info(f"Registered parallel tool: {tool_name}")
    logger.info(f"Server '{mcp_server.name}' initialized with SAAGA decorators")
# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()

@click.command()
@click.option(
    "--port",
    default=3001,
    help="Port to listen on for SSE transport"
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)"
)
def main(port: int, transport: str) -> int:
    """Run the Example MCP Server server with specified transport."""
    try:
        if transport == "stdio":
            logger.info("Starting server with STDIO transport")
            asyncio.run(server.run_stdio_async())
        else:
            logger.info(f"Starting server with SSE transport on port {port}")
            server.settings.port = port
            asyncio.run(server.run_sse_async())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())