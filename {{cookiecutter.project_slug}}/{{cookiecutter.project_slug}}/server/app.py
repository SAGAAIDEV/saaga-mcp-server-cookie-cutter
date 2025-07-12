"""{{ cookiecutter.project_name }} - MCP Server with SAAGA Decorators

This module implements the core MCP server using FastMCP with dual transport support
and automatic application of SAAGA decorators (exception handling, logging, parallelization).
"""

import asyncio
import sys
from typing import Optional, Callable, Any

import click
from mcp import types
from mcp.server.fastmcp import FastMCP

from {{ cookiecutter.project_slug }}.config import ServerConfig, get_config
from {{ cookiecutter.project_slug }}.logging_config import setup_logging, logger
{% if cookiecutter.include_example_tools == "yes" -%}
from {{ cookiecutter.project_slug }}.tools.example_tools import example_tools, parallel_example_tools
{% endif -%}

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
    
    mcp_server = FastMCP(config.name or "{{ cookiecutter.project_name }}")
    
    {% if cookiecutter.include_example_tools == "yes" -%}
    # Register all tools with the server
    register_tools(mcp_server, config)
    {% else -%}
    # No example tools included
    logger.info("No example tools configured. Add your tools and register them here.")
    {% endif -%}
    
    return mcp_server


{% if cookiecutter.include_example_tools == "yes" -%}
def register_tools(mcp_server: FastMCP, config: ServerConfig) -> None:
    """Register all MCP tools with the server using SAAGA decorators.
    
    Registers decorated functions directly with MCP to preserve function signatures
    for proper parameter introspection.
    """
    
    # Import SAAGA decorators
    from {{ cookiecutter.project_slug }}.decorators.exception_handler import exception_handler
    from {{ cookiecutter.project_slug }}.decorators.tool_logger import tool_logger
    from {{ cookiecutter.project_slug }}.decorators.parallelize import parallelize
    
    # Register regular tools with SAAGA decorators
    for tool_func in example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger
        decorated_func = exception_handler(tool_logger(tool_func, config))
        
        # Extract metadata from the original function
        tool_name = tool_func.__name__
        tool_description = tool_func.__doc__ or f"{tool_name} - No description provided"
        
        # Register the decorated function directly with MCP
        # This preserves the function signature for parameter introspection
        mcp_server.tool(
            name=tool_name,
            description=tool_description
        )(decorated_func)
        
        logger.info(f"Registered tool: {tool_name}")
    
    {% if cookiecutter.include_parallel_example == "yes" -%}
    # Register parallel tools with SAAGA decorators  
    for tool_func in parallel_example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
        decorated_func = exception_handler(tool_logger(parallelize(tool_func), config))
        
        # Extract metadata
        tool_name = tool_func.__name__
        tool_description = tool_func.__doc__ or f"{tool_name} - No description provided"
        
        # Register directly with MCP
        mcp_server.tool(
            name=tool_name,
            description=tool_description
        )(decorated_func)
        
        logger.info(f"Registered parallel tool: {tool_name}")
    {% endif -%}
    
    logger.info(f"Server '{mcp_server.name}' initialized with SAAGA decorators")
{% endif -%}

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