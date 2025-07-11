"""Main module for Fixed MCP Server MCP server.

This module allows the server to be run as a Python module using:
python -m fixed_mcp_server

It delegates to the server application's main function.
"""

from .server.app import main

if __name__ == "__main__":
    main()