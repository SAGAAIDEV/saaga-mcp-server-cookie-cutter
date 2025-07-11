"""{{ cookiecutter.project_name }} MCP Server

This module provides the MCP server instance for CLI discovery and client integration.
"""

from {{ cookiecutter.project_slug }}.server.app import server, create_mcp_server

__all__ = ["server", "create_mcp_server"]