"""Test Bazel MCP Server

This module provides the MCP server instance for CLI discovery and client integration.
"""

from test_bazel.server.app import server, create_mcp_server

__all__ = ["server", "create_mcp_server"]