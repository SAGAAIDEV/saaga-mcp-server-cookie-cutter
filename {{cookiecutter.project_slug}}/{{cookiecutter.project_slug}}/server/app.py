"""{{ cookiecutter.project_name }} - MCP Server with SAAGA Decorators

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

from {{ cookiecutter.project_slug }}.config import ServerConfig, get_config
{% if cookiecutter.include_example_tools == "yes" -%}
from {{ cookiecutter.project_slug }}.tools.example_tools import example_tools, parallel_example_tools
{% endif -%}

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
    
    mcp_server = FastMCP(config.name or "{{ cookiecutter.project_name }}")
    
{% if cookiecutter.include_example_tools == "yes" -%}
    # Import SAAGA decorators
    from {{ cookiecutter.project_slug }}.decorators.exception_handler import exception_handler
    from {{ cookiecutter.project_slug }}.decorators.tool_logger import tool_logger
    from {{ cookiecutter.project_slug }}.decorators.parallelize import parallelize
    
    # Register regular tools with SAAGA decorators
    for tool_func in example_tools:
        @mcp_server.tool(
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"Tool: {tool_func.__name__}"
        )
        def create_tool_wrapper(func=tool_func, bound_func=tool_func):
            def tool_wrapper(*args, **kwargs) -> types.TextContent:
                """MCP wrapper that applies SAAGA decorators."""
                # Apply SAAGA decorator chain: exception_handler → tool_logger
                decorated_func = exception_handler(tool_logger(bound_func, config))
                
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
            return tool_wrapper
        
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    {% if cookiecutter.include_parallel_example == "yes" -%}
    # Register parallel tools with SAAGA decorators
    for tool_func in parallel_example_tools:
        @mcp_server.tool(
            name=tool_func.__name__,
            description=tool_func.__doc__ or f"Parallel tool: {tool_func.__name__}"
        )
        def create_parallel_tool_wrapper(func=tool_func, bound_func=tool_func):
            def parallel_tool_wrapper(*args, **kwargs) -> types.TextContent:
                """MCP wrapper that applies SAAGA decorators with parallelization."""
                # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
                decorated_func = exception_handler(tool_logger(parallelize(bound_func), config))
                
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
            return parallel_tool_wrapper
        
        logger.info(f"Registered parallel tool: {tool_func.__name__}")
    {% endif -%}
{% else -%}
    # No example tools included
    logger.info("No example tools configured. Add your tools and register them here.")
{% endif -%}
    
    logger.info(f"Server '{mcp_server.name}' initialized with SAAGA decorators")
    return mcp_server

# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()

@click.command()
@click.option(
    "--port",
    default={{ cookiecutter.server_port }},
    help="Port to listen on for SSE transport"
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)"
)
def main(port: int, transport: str) -> int:
    """Run the {{ cookiecutter.project_name }} server with specified transport."""
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