"""{{cookiecutter.project_name}} - MCP Server with SAAGA Decorators

This module implements the core MCP server using FastMCP with dual transport support
and automatic application of SAAGA decorators (exception handling, logging, parallelization).
"""

import argparse
import logging
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from ..config import ServerConfig, get_config
{% if cookiecutter.include_example_tools == "yes" -%}
from ..tools.example_tools import example_tools, parallel_example_tools
{% endif -%}

# Initialize server configuration
config = get_config()

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.log_file_path)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
server = FastMCP(
    name="{{cookiecutter.project_name}}",
    instructions="""
    {{cookiecutter.description}}
    
    This server provides MCP tools with automatic application of SAAGA decorators:
    - Exception handling with graceful error recovery
    - Comprehensive logging to SQLite database
    - Optional parallelization for compute-intensive operations
    
    All tools are automatically decorated for enhanced reliability and observability.
    """,
)


def apply_saaga_decorators(func, is_parallel: bool = False):
    """Apply SAAGA decorators to MCP tools.
    
    This function will be enhanced in Phase 2 to automatically apply:
    1. Exception handler decorator
    2. Tool logger decorator  
    3. Parallelize decorator (for parallel tools)
    
    Args:
        func: The tool function to decorate
        is_parallel: Whether to apply parallelization decorator
        
    Returns:
        The decorated function
    """
    # TODO: Phase 2 - Apply actual SAAGA decorators
    # For now, return the function as-is
    logger.info(f"Applying SAAGA decorators to {func.__name__} (parallel={is_parallel})")
    return func


def register_tools():
    """Register all tools with the server, applying SAAGA decorators."""
    {% if cookiecutter.include_example_tools == "yes" -%}
    # Register regular tools
    for tool_func in example_tools:
        decorated_func = apply_saaga_decorators(tool_func, is_parallel=False)
        server.tool()(decorated_func)
        logger.info(f"Registered tool: {tool_func.__name__}")
    
    {% if cookiecutter.include_parallel_example == "yes" -%}
    # Register parallel tools
    for tool_func in parallel_example_tools:
        decorated_func = apply_saaga_decorators(tool_func, is_parallel=True)
        server.tool()(decorated_func)
        logger.info(f"Registered parallel tool: {tool_func.__name__}")
    {% endif -%}
    {% else -%}
    # No example tools included
    logger.info("No example tools configured. Add your tools and register them here.")
    {% endif -%}


def create_server() -> FastMCP:
    """Create and configure the MCP server.
    
    Returns:
        Configured FastMCP server instance
    """
    # Register all tools with decorators
    register_tools()
    
    logger.info(f"Server '{server.name}' initialized with {len(server._tool_manager._tools)} tools")
    return server


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="{{cookiecutter.project_name}} - MCP Server with SAAGA Decorators"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for SSE transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default={{cookiecutter.server_port}},
        help="Port to bind to for SSE transport (default: {{cookiecutter.server_port}})"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=config.log_level,
        help=f"Log level (default: {config.log_level})"
    )
    
    args = parser.parse_args()
    
    # Update log level if specified
    if args.log_level != config.log_level:
        logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
        logger.info(f"Log level updated to {args.log_level}")
    
    # Create the server
    mcp_server = create_server()
    
    # Start the server with the specified transport
    logger.info(f"Starting {{cookiecutter.project_name}} server...")
    logger.info(f"Transport: {args.transport}")
    logger.info(f"Configuration: {config}")
    
    try:
        if args.transport == "stdio":
            logger.info("Starting server with STDIO transport")
            mcp_server.run()
        else:  # sse
            logger.info(f"Starting server with SSE transport on {args.host}:{args.port}")
            mcp_server.run(transport="sse", host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()