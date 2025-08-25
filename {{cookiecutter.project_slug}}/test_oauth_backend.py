{% if cookiecutter.include_oauth_backend == "yes" -%}
#!/usr/bin/env python
"""Test script for OAuth backend functionality.

This script tests the OAuth backend pattern where:
1. Client provides userId, tempToken, and providerId
2. The backend exchanges tempToken for accessToken
3. Tools use the accessToken to make API calls

Usage:
    # Test with mock backend (no real API needed)
    python test_oauth_backend.py
    
    # Test with real backend
    python test_oauth_backend.py --backend-url https://api.example.com
"""

import asyncio
import sys
import json
import argparse
from typing import Dict, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import types


async def test_oauth_backend(backend_url: str = None, mock_mode: bool = True):
    """Test OAuth backend functionality.
    
    Args:
        backend_url: Optional backend API URL for real testing
        mock_mode: If True, use mock responses (default)
    """
    print(f"\n{'='*60}")
    print("OAuth Backend Test Script")
    print(f"{'='*60}\n")
    
    if mock_mode:
        print("🔧 Using MOCK mode - no real backend required")
    else:
        print(f"🌐 Using REAL backend at: {backend_url}")
    
    # Start the server with appropriate config
    env = {
        "OAUTH_BACKEND_MOCK_MODE": "yes" if mock_mode else "no"
    }
    if backend_url:
        env["OAUTH_BACKEND_URL"] = backend_url
    
    server_params = types.StdioServerParameters(
        command="python",
        args=["-m", "{{ cookiecutter.project_slug }}.server.app"],
        env=env
    )
    
    print("\n📡 Starting MCP server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            print("✅ Server connected successfully")
            print(f"   Server: {session.server_info.name if session.server_info else 'Unknown'}")
            print(f"   Version: {session.server_info.version if session.server_info else 'Unknown'}")
            
            # List available tools
            tools_response = await session.list_tools()
            backend_tools = [
                tool for tool in tools_response.tools 
                if "reddit" in tool.name.lower()
            ]
            
            if backend_tools:
                print(f"\n📦 Found {len(backend_tools)} Reddit OAuth backend tools:")
                for tool in backend_tools:
                    print(f"   - {tool.name}: {tool.description or 'No description'}")
            else:
                print("\n⚠️ No Reddit OAuth backend tools found!")
                print("   Make sure include_oauth_backend=yes in your config")
                return
            
            # Test 1: Call without OAuth parameters (should fail gracefully)
            print("\n\n🧪 Test 1: Call without OAuth parameters")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "get_reddit_user",
                    arguments={}
                )
                
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        if response.get("error") == "missing_parameters":
                            print("✅ Correctly returned missing parameters error")
                            print(f"   Error: {response.get('message')}")
                            print(f"   Details: {response.get('details')}")
                        else:
                            print(f"❌ Unexpected response: {response}")
                
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
            
            # Test 2: Call with valid OAuth backend parameters
            print("\n\n🧪 Test 2: Call with valid OAuth backend parameters")
            print("-" * 40)
            
            try:
                # Simulate what the client would send
                result = await session.call_tool(
                    "get_reddit_user",
                    arguments={},
                    _meta={
                        "userId": "test_user_123",
                        "tempToken": "temp_token_abc456",
                        "providerId": "reddit"
                    }
                )
                
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        
                        if "error" not in response:
                            print("✅ Successfully exchanged token and got user data!")
                            print(f"   User: {response.get('name', 'Unknown')}")
                            print(f"   Karma: {response.get('link_karma', 0)} link, {response.get('comment_karma', 0)} comment")
                        else:
                            print(f"❌ Error: {response.get('message')}")
                            print(f"   Details: {response.get('details')}")
                
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
            
            # Test 3: Call with wrong provider ID (should fail)
            print("\n\n🧪 Test 3: Call with mismatched provider ID")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "get_reddit_user",
                    arguments={},
                    _meta={
                        "userId": "test_user_123",
                        "tempToken": "temp_token_abc456",
                        "providerId": "github"  # Wrong provider!
                    }
                )
                
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        if response.get("error") == "provider_mismatch":
                            print("✅ Correctly detected provider mismatch")
                            print(f"   Error: {response.get('message')}")
                        else:
                            print(f"❌ Unexpected response: {response}")
                
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
            
            # Test 4: Test list_user_subreddits with parameters
            print("\n\n🧪 Test 4: Call list_user_subreddits with limit")
            print("-" * 40)
            
            try:
                result = await session.call_tool(
                    "list_user_subreddits",
                    arguments={"limit": 5},
                    _meta={
                        "userId": "test_user_123",
                        "tempToken": "temp_token_abc456",
                        "providerId": "reddit"
                    }
                )
                
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        
                        if "subreddits" in response:
                            print(f"✅ Successfully got {len(response['subreddits'])} subreddits")
                            for sub in response['subreddits'][:3]:
                                print(f"   - {sub['display_name']}: {sub['subscribers']:,} subscribers")
                        else:
                            print(f"❌ Error: {response.get('message', 'Unknown error')}")
                
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
            
            print(f"\n{'='*60}")
            print("✅ OAuth Backend Tests Complete!")
            print(f"{'='*60}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test OAuth backend functionality")
    parser.add_argument(
        "--backend-url",
        help="Backend API URL (e.g., https://api.example.com)"
    )
    parser.add_argument(
        "--no-mock",
        action="store_true",
        help="Disable mock mode and use real backend"
    )
    
    args = parser.parse_args()
    
    # Determine if we're using mock mode
    mock_mode = not args.no_mock
    
    # Run the test
    asyncio.run(test_oauth_backend(
        backend_url=args.backend_url,
        mock_mode=mock_mode
    ))


if __name__ == "__main__":
    main()
{% endif -%}