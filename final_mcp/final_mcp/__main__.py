"""Main module for final mcp MCP server.

This module allows the server to be run as a Python module using:
python -m final_mcp

It delegates to the server application's main function.
"""

from final_mcp.server.app import main

if __name__ == "__main__":
    main()