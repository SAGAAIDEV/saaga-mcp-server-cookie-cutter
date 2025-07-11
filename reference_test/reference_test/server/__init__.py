"""MCP server package initialization"""

from reference_test.config import load_config
from reference_test.server.app import create_mcp_server

# Create server instance with default configuration
server = create_mcp_server(load_config())

__all__ = ["server", "create_mcp_server"]
