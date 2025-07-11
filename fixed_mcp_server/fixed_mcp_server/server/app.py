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
    
    # Configure logging (stderr + file, never stdout to avoid interfering with MCP STDIO protocol)
    import sys
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file_path),
            logging.StreamHandler(sys.stderr)  # Add stderr handler for immediate feedback
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
        
        # Create wrapper with early binding to fix closure capture
        def create_tool_wrapper(original_func=tool_func, decorated_func=decorated_func):
            """Create tool wrapper with proper variable capture."""
            import functools
            
            @functools.wraps(original_func)  
            def tool_wrapper(*args, **kwargs):
                """Wrapper that applies SAAGA decorators and returns raw Python values."""
                # FastMCP expects raw Python values, not MCP protocol objects
                # It will handle the conversion to TextContent automatically
                return decorated_func(*args, **kwargs)
            
            return tool_wrapper
        
        # Register the tool - let FastMCP handle schema generation automatically
        wrapped_tool = create_tool_wrapper()
        mcp_server.tool()(wrapped_tool)
        
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    # Register parallel tools with SAAGA decorators
    for tool_func in parallel_example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
        decorated_func = exception_handler(tool_logger(parallelize(tool_func), config))
        
        # Create wrapper with early binding to fix closure capture
        def create_parallel_tool_wrapper(original_func=tool_func, decorated_func=decorated_func):
            """Create parallel tool wrapper with proper variable capture."""
            import functools
            
            @functools.wraps(original_func)
            def parallel_tool_wrapper(*args, **kwargs):
                """Wrapper that applies SAAGA decorators and returns raw Python values."""
                # FastMCP expects raw Python values, not MCP protocol objects
                # It will handle the conversion to TextContent automatically
                return decorated_func(*args, **kwargs)
            
            return parallel_tool_wrapper
        
        # Register the tool - let FastMCP handle schema generation automatically
        wrapped_parallel_tool = create_parallel_tool_wrapper()
        mcp_server.tool()(wrapped_parallel_tool)
        
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