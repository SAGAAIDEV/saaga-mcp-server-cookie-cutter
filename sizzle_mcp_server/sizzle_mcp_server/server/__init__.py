"""Sizzle MCP Server MCP Server

This module provides the MCP server instance for CLI discovery and client integration.
"""

from sizzle_mcp_server.server.app import server, create_mcp_server

__all__ = ["server", "create_mcp_server"]