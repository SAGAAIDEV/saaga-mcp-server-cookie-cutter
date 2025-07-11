"""Main module for UI Test Project MCP server.

This module allows the server to be run as a Python module using:
python -m ui_test_project

It delegates to the server application's main function.
"""

from .server.app import main

if __name__ == "__main__":
    main()