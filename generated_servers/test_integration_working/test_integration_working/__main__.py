"""Main module for Test Integration Working MCP server.

This module allows the server to be run as a Python module using:
python -m test_integration_working

It delegates to the server application's main function.
"""

from test_integration_working.server.app import main

if __name__ == "__main__":
    main()