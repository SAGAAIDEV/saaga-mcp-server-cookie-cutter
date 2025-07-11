"""Fixed MCP Server - MCP Server with SAAGA Decorators

This module implements the core MCP server using FastMCP with dual transport support
and automatic application of SAAGA decorators (exception handling, logging, parallelization).
"""

import asyncio
import logging
import sys
from typing import Optional

import click
from mcp.server.fastmcp import FastMCP
from mcp import types

from fixed_mcp_server.config import ServerConfig, get_config
from fixed_mcp_server.tools.example_tools import example_tools, parallel_example_tools
logger = logging.getLogger(__name__)

def create_mcp_server(config: Optional[ServerConfig] = None) -> FastMCP:
    """Create and configure the MCP server with SAAGA decorators.
    
    Args:
        config: Optional server configuration
        
    Returns:
        Configured FastMCP server instance
    """
    if config is None:
        config = get_config()
    
    # Configure logging (file only to avoid interfering with MCP JSON protocol)
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file_path)
        ]
    )
    
    mcp_server = FastMCP(config.name or "Fixed MCP Server")
    
# Import SAAGA decorators
    from fixed_mcp_server.decorators.exception_handler import exception_handler
    from fixed_mcp_server.decorators.tool_logger import tool_logger
    from fixed_mcp_server.decorators.parallelize import parallelize
    
    # Register regular tools with SAAGA decorators
    for tool_func in example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger
        decorated_func = exception_handler(tool_logger(tool_func, config))
        
        # Create MCP wrapper that preserves original function signature
        def create_mcp_wrapper(original_func, decorated_func):
            def mcp_wrapper(*args, **kwargs) -> types.TextContent:
                """MCP wrapper that converts result to TextContent."""
                try:
                    result = decorated_func(*args, **kwargs)
                    # Convert result to MCP TextContent
                    if isinstance(result, str):
                        return types.TextContent(type="text", text=result)
                    elif isinstance(result, (dict, list)):
                        import json
                        return types.TextContent(type="text", text=json.dumps(result, indent=2))
                    else:
                        return types.TextContent(type="text", text=str(result))
                except Exception as e:
                    return types.TextContent(type="text", text=f"Error: {str(e)}")
            
            # Copy the original function's signature and metadata
            import functools
            mcp_wrapper = functools.wraps(original_func)(mcp_wrapper)
            return mcp_wrapper
        
        # Register the properly wrapped function
        mcp_server.tool(
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"Tool: {tool_func.__name__}"
        )(create_mcp_wrapper(tool_func, decorated_func))
        
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    # Register parallel tools with SAAGA decorators
    for tool_func in parallel_example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
        decorated_func = exception_handler(tool_logger(parallelize(tool_func), config))
        
        # Create MCP wrapper that preserves original function signature
        def create_parallel_mcp_wrapper(original_func, decorated_func):
            def parallel_mcp_wrapper(*args, **kwargs) -> types.TextContent:
                """MCP wrapper that converts result to TextContent."""
                try:
                    result = decorated_func(*args, **kwargs)
                    # Convert result to MCP TextContent
                    if isinstance(result, str):
                        return types.TextContent(type="text", text=result)
                    elif isinstance(result, (dict, list)):
                        import json
                        return types.TextContent(type="text", text=json.dumps(result, indent=2))
                    else:
                        return types.TextContent(type="text", text=str(result))
                except Exception as e:
                    return types.TextContent(type="text", text=f"Error: {str(e)}")
            
            # Copy the original function's signature and metadata
            import functools
            parallel_mcp_wrapper = functools.wraps(original_func)(parallel_mcp_wrapper)
            return parallel_mcp_wrapper
        
        # Register the properly wrapped function
        mcp_server.tool(
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"Parallel tool: {tool_func.__name__}"
        )(create_parallel_mcp_wrapper(tool_func, decorated_func))
        
        logger.info(f"Registered parallel tool: {tool_func.__name__}")
    logger.info(f"Server '{mcp_server.name}' initialized with SAAGA decorators")
    return mcp_server

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
    """Run the Fixed MCP Server server with specified transport."""
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