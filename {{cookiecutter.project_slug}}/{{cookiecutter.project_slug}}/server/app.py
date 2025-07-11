"""{{ cookiecutter.project_name }} - MCP Server with SAAGA Decorators

This module implements the core MCP server using FastMCP with dual transport support
and automatic application of SAAGA decorators (exception handling, logging, parallelization).
"""

import asyncio
import sys
from typing import Optional

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
    """Register all MCP tools with the server using reference implementation pattern"""
    
    # Import SAAGA decorators
    from {{ cookiecutter.project_slug }}.decorators.exception_handler import exception_handler
    from {{ cookiecutter.project_slug }}.decorators.tool_logger import tool_logger
    from {{ cookiecutter.project_slug }}.decorators.parallelize import parallelize
    
    # Register regular tools with SAAGA decorators
    for tool_func in example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger
        decorated_func = exception_handler(tool_logger(tool_func, config))
        
        # Create a wrapper function following reference implementation pattern
        # This preserves exact signatures and return types for MCP protocol
        if tool_func.__name__ == "echo_tool":
            @mcp_server.tool(
                name="echo_tool",
                description="Echo back the input message. This is a simple example tool that demonstrates basic MCP tool functionality.",
            )
            def echo_tool_wrapper(message: str) -> types.TextContent:
                """Wrapper around the echo_tool implementation with SAAGA decorators"""
                result = decorated_func(message)
                # Ensure we return TextContent for MCP protocol compliance
                if isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
                    
        elif tool_func.__name__ == "get_time":
            @mcp_server.tool(
                name="get_time", 
                description="Get the current time. Returns the current time in a human-readable format.",
            )
            def get_time_wrapper() -> types.TextContent:
                """Wrapper around the get_time implementation with SAAGA decorators"""
                result = decorated_func()
                if isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
                    
        elif tool_func.__name__ == "random_number":
            @mcp_server.tool(
                name="random_number",
                description="Generate a random number within a specified range.",
            )
            def random_number_wrapper(min_value: int = 1, max_value: int = 100) -> types.TextContent:
                """Wrapper around the random_number implementation with SAAGA decorators"""
                result = decorated_func(min_value, max_value)
                if isinstance(result, (dict, list)):
                    import json
                    return types.TextContent(type="text", text=json.dumps(result, indent=2))
                elif isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
                    
        elif tool_func.__name__ == "calculate_fibonacci":
            @mcp_server.tool(
                name="calculate_fibonacci",
                description="Calculate the nth Fibonacci number. This is a more computationally intensive example.",
            )
            def calculate_fibonacci_wrapper(n: int) -> types.TextContent:
                """Wrapper around the calculate_fibonacci implementation with SAAGA decorators"""
                result = decorated_func(n)
                if isinstance(result, (dict, list)):
                    import json
                    return types.TextContent(type="text", text=json.dumps(result, indent=2))
                elif isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
        
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    {% if cookiecutter.include_parallel_example == "yes" -%}
    # Register parallel tools with SAAGA decorators  
    for tool_func in parallel_example_tools:
        # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
        decorated_func = exception_handler(tool_logger(parallelize(tool_func), config))
        
        if tool_func.__name__ == "process_batch_data":
            @mcp_server.tool(
                name="process_batch_data",
                description="Process a batch of data items. This is an example of a tool that benefits from parallelization.",
            )
            def process_batch_data_wrapper(data: list) -> types.TextContent:
                """Wrapper around the process_batch_data implementation with SAAGA decorators"""
                result = decorated_func(data)
                if isinstance(result, (dict, list)):
                    import json
                    return types.TextContent(type="text", text=json.dumps(result, indent=2))
                elif isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
                    
        elif tool_func.__name__ == "simulate_heavy_computation":
            @mcp_server.tool(
                name="simulate_heavy_computation",
                description="Simulate a heavy computational task. This tool demonstrates parallel processing capabilities.",
            )
            def simulate_heavy_computation_wrapper(iterations: int = 1000) -> types.TextContent:
                """Wrapper around the simulate_heavy_computation implementation with SAAGA decorators"""
                result = decorated_func(iterations)
                if isinstance(result, (dict, list)):
                    import json
                    return types.TextContent(type="text", text=json.dumps(result, indent=2))
                elif isinstance(result, str):
                    return types.TextContent(type="text", text=result)
                elif hasattr(result, 'text'):
                    return result
                else:
                    return types.TextContent(type="text", text=str(result))
        
        logger.info(f"Registered parallel tool: {tool_func.__name__}")
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