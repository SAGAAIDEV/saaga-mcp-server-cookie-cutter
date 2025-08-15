#!/usr/bin/env python
"""Test OAuth error handling with invalid tokens.

This script demonstrates that the OAuth passthrough decorator
handles invalid tokens gracefully without crashing.
"""

import asyncio
import sys
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client, get_default_environment


def extract_text_content(result) -> str:
    """Extract text content from MCP result."""
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return item.text
    return None


async def test_invalid_token_handling():
    """Test that invalid tokens are handled gracefully."""
    
    print("🧪 Testing OAuth Error Handling with Invalid Tokens")
    print("=" * 60)
    
    # Connect to server via STDIO
    async with stdio_client(
        StdioServerParameters(
            command=sys.executable,
            args=["-m", "example_server.server.app"],
            env=get_default_environment()
        )
    ) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("✅ Connected to MCP server")
            print()
            
            # Test 1: No token provided
            print("1️⃣  Testing with no token...")
            result = await session.call_tool("get_github_user", {})
            text = extract_text_content(result)
            data = json.loads(text)
            print(f"   Result: {data}")
            assert data.get("error") == "token_not_provided"
            print("   ✅ Handled gracefully - no crash!\n")
            
            # Test 2: Empty token
            print("2️⃣  Testing with empty token...")
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="get_github_user",
                        arguments={},
                        _meta={
                            "oauth_tokens": {"github": ""},
                            "correlationId": "test_empty"
                        }
                    )
                )
            )
            result = await session.send_request(request, types.CallToolResult)
            text = extract_text_content(result)
            data = json.loads(text)
            print(f"   Result: {data}")
            assert data.get("error") == "invalid_token_format"
            print("   ✅ Handled gracefully - no crash!\n")
            
            # Test 3: Invalid token (will get 401 from GitHub)
            print("3️⃣  Testing with invalid token (expects 401)...")
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="get_github_user",
                        arguments={},
                        _meta={
                            "oauth_tokens": {"github": "gho_invalid_token_123"},
                            "correlationId": "test_invalid"
                        }
                    )
                )
            )
            result = await session.send_request(request, types.CallToolResult)
            text = extract_text_content(result)
            data = json.loads(text)
            print(f"   Result: {data}")
            assert data.get("error") == "unauthorized"
            assert data.get("status_code") == 401
            assert "provider" in data  # Enhanced error info
            print("   ✅ Handled gracefully - no crash!\n")
            
            # Test 4: Whitespace-only token
            print("4️⃣  Testing with whitespace-only token...")
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="get_github_user",
                        arguments={},
                        _meta={
                            "oauth_tokens": {"github": "   "},
                            "correlationId": "test_whitespace"
                        }
                    )
                )
            )
            result = await session.send_request(request, types.CallToolResult)
            text = extract_text_content(result)
            data = json.loads(text)
            print(f"   Result: {data}")
            assert data.get("error") == "invalid_token_format"
            print("   ✅ Handled gracefully - no crash!\n")
            
            # Test 5: Test with wrong provider
            print("5️⃣  Testing with wrong provider (no google token)...")
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="get_github_user",
                        arguments={},
                        _meta={
                            "oauth_tokens": {"google": "some_google_token"},  # Wrong provider
                            "correlationId": "test_wrong_provider"
                        }
                    )
                )
            )
            result = await session.send_request(request, types.CallToolResult)
            text = extract_text_content(result)
            data = json.loads(text)
            print(f"   Result: {data}")
            assert data.get("error") == "token_not_provided"
            assert "github" in data.get("message", "").lower()
            print("   ✅ Handled gracefully - no crash!\n")
            
    print("=" * 60)
    print("✅ All error handling tests passed!")
    print("\nSummary:")
    print("- No tokens: Returns graceful error")
    print("- Empty tokens: Validates and rejects")
    print("- Invalid tokens: Returns 401 with context")
    print("- Whitespace tokens: Validates and rejects")
    print("- Wrong provider: Returns appropriate error")
    print("\n🎉 The OAuth passthrough implementation handles all error cases gracefully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_invalid_token_handling())
    sys.exit(exit_code)
