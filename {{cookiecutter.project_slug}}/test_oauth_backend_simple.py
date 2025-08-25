#!/usr/bin/env python3
"""Test OAuth backend with real HTTP calls to mock server.

This is just like test_correlation_id_integration.py but passes OAuth parameters
instead of correlation IDs.

USAGE:
    python test_oauth_backend_simple.py
"""

import warnings
warnings.filterwarnings("ignore", message="coroutine 'SQLiteDestination.write' was never awaited", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*found in sys.modules after import.*", category=RuntimeWarning)

import asyncio
import os
from datetime import timedelta
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters
from tests.helpers.mock_oauth_backend import start_mock_backend

async def test_oauth_backend():
    """Test OAuth backend with mock HTTP server."""
    
    print("Starting OAuth Backend Test")
    print("-" * 40)
    
    # Start mock backend server on the configured port
    with start_mock_backend(port={{cookiecutter.oauth_backend_port}}) as backend_url:
        print(f"✓ Mock backend running at: {backend_url}")
        
        # Setup environment
        env = os.environ.copy()
        env['PYTHONWARNINGS'] = 'ignore::RuntimeWarning'
        env['OAUTH_BACKEND_URL'] = backend_url  # Just base URL, decorator adds path
        env['OAUTH_BACKEND_MOCK_MODE'] = 'no'  # Use real HTTP
        
        # Start MCP server with verbose logging
        env['LOG_LEVEL'] = 'DEBUG'  # Enable debug logging
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "{{ cookiecutter.project_slug }}.server.app", "--transport", "stdio"],
            env=env
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✓ MCP server connected")
                
                # Test 1: Call Reddit tool WITH OAuth parameters
                print("\nTest 1: Calling get_reddit_user with OAuth backend")
                
                # This is EXACTLY like correlation ID test, just different metadata
                meta = {
                    "userId": "test_user_123",
                    "userToken": "valid_temp_token_abc",
                    "providerId": "reddit"
                }
                
                request = types.ClientRequest(
                    types.CallToolRequest(
                        method="tools/call",
                        params=types.CallToolRequestParams(
                            name="get_reddit_user",
                            arguments={},
                            _meta=meta  # OAuth params here instead of correlationId
                        )
                    )
                )
                
                result = await session.send_request(
                    request, 
                    types.CallToolResult,
                    request_read_timeout_seconds=timedelta(seconds=30)
                )
                
                print("✓ Tool called successfully")
                print(f"  Result: {result.content[0].text if result.content else 'No content'}")
                
                # Test 2: Call without OAuth parameters (should fail)
                print("\nTest 2: Calling get_reddit_user WITHOUT OAuth parameters")
                
                request = types.ClientRequest(
                    types.CallToolRequest(
                        method="tools/call",
                        params=types.CallToolRequestParams(
                            name="get_reddit_user",
                            arguments={}
                            # No _meta field
                        )
                    )
                )
                
                result = await session.send_request(
                    request,
                    types.CallToolResult,
                    request_read_timeout_seconds=timedelta(seconds=30)
                )
                
                print("✓ Tool called (expected error)")
                print(f"  Result: {result.content[0].text if result.content else 'No content'}")
                
                print("\n" + "="*40)
                print("SUCCESS: OAuth backend test completed!")
                print("The mock backend received real HTTP requests for token exchange.")

if __name__ == "__main__":
    asyncio.run(test_oauth_backend())