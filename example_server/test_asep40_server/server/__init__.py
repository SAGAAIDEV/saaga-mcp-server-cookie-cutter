"""Test ASEP40 Server MCP Server

This module provides the MCP server instance for CLI discovery and client integration.
"""

from test_asep40_server.server.app import server, create_mcp_server

__all__ = ["server", "create_mcp_server"]