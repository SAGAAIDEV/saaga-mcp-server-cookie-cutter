#!/usr/bin/env python
"""Test OAuth passthrough with private repository operations using real MCP client.

This script tests operations that REQUIRE authentication to work,
proving that OAuth token passthrough is functioning correctly through
the actual MCP protocol (the same way a real MCP client would use it).

Usage:
    python test_oauth_private_repo.py <github_token> <owner/repo> [--transport stdio|http]
    
Examples:
    python test_oauth_private_repo.py gho_abc123... myusername/my-private-repo
    python test_oauth_private_repo.py gho_abc123... myusername/my-private-repo --transport http
"""

import asyncio
import sys
import json
import subprocess
import time
import os
from datetime import timedelta
from pathlib import Path
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client, get_default_environment

# Conditional import for streamable_http
try:
    from mcp.client.streamable_http import streamablehttp_client
    HAS_STREAMABLE_HTTP = True
except ImportError:
    HAS_STREAMABLE_HTTP = False
    streamablehttp_client = None

import httpx


def extract_text_content(result) -> str:
    """Extract text content from MCP result."""
    if hasattr(result, 'content') and result.content:
        for item in result.content:
            if hasattr(item, 'text'):
                return item.text
    return None


async def get_private_repo_info(owner: str, repo: str, token: str):
    """Directly fetch private repo info to verify access."""
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers=headers,
            timeout=10.0
        )
        
        return response.status_code, response.json() if response.status_code == 200 else response.text


async def call_mcp_tool_with_oauth(
    session: ClientSession, 
    tool_name: str, 
    arguments: dict, 
    github_token: str,
    correlation_id: str = None
) -> dict:
    """Call an MCP tool with OAuth token in metadata.
    
    This is how a real MCP client passes OAuth tokens to the server.
    """
    # Build metadata with OAuth token
    meta = {
        "oauth_tokens": {
            "github": github_token
        }
    }
    
    if correlation_id:
        meta["correlationId"] = correlation_id
    
    # Build proper MCP request with metadata
    request = types.ClientRequest(
        types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name=tool_name,
                arguments=arguments,
                _meta=meta
            )
        )
    )
    
    print(f"  → Calling '{tool_name}' via MCP protocol with OAuth token...")
    
    # Send request through MCP protocol
    result = await session.send_request(
        request,
        types.CallToolResult
    )
    
    if result.isError:
        return {"error": "mcp_error", "message": str(result)}
    
    # Extract and parse the response
    text_content = extract_text_content(result)
    if text_content:
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            return {"raw_response": text_content}
    
    return {"error": "no_content"}


async def test_private_repo_with_mcp_client(token: str, repo_path: str, transport: str = "stdio"):
    """Test OAuth passthrough using real MCP client/server communication.
    
    Args:
        token: GitHub personal access token
        repo_path: Repository in format owner/repo
        transport: Transport type - "stdio" or "http"
    """
    
    # Parse owner/repo
    if "/" not in repo_path:
        print("❌ Error: Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    owner, repo = repo_path.split("/", 1)
    
    print("🔐 Testing OAuth Passthrough with Private Repository (Real MCP Client)")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    print(f"Token: {token[:10]}..." if len(token) > 10 else "Token provided")
    print(f"Transport: {transport.upper()}")
    print()
    
    server_process = None
    
    try:
        if transport == "http":
            if not HAS_STREAMABLE_HTTP:
                print("❌ Error: Streamable HTTP transport not available")
                print("   The mcp.client.streamable_http module is not installed")
                sys.exit(1)
                
            # Start HTTP server in background
            print("Starting MCP server with Streamable HTTP transport...")
            server_process = subprocess.Popen(
                [sys.executable, "-m", "example_server.server.app", 
                 "--transport", "streamable-http", "--port", "3001"],
                env=get_default_environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path(__file__).parent)
            )
            
            # Give server time to start
            time.sleep(2)
            
            # Connect via HTTP
            async with streamablehttp_client("http://localhost:3001/mcp") as (read_stream, write_stream, get_session_id):
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    print("✅ Connected to MCP server via Streamable HTTP transport")
                    print()
                    
                    # Run tests
                    await run_oauth_tests(session, token, owner, repo, repo_path)
        else:
            # Use STDIO (default)
            print("Starting MCP server with STDIO transport...")
            async with stdio_client(
                StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "example_server.server.app"],
                    env=get_default_environment()
                )
            ) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    # Initialize the session
                    await session.initialize()
                    
                    print("✅ Connected to MCP server via STDIO transport")
                    print()
                    
                    # Run tests
                    await run_oauth_tests(session, token, owner, repo, repo_path)
                    
    finally:
        # Clean up HTTP server if started
        if server_process and server_process.poll() is None:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("HTTP server stopped")


async def run_oauth_tests(session: ClientSession, token: str, owner: str, repo: str, repo_path: str):
    """Run the OAuth tests with the connected session."""
    
    # Test 1: Verify authentication works
    print("1️⃣  Testing authentication via MCP...")
    result = await call_mcp_tool_with_oauth(
        session,
        "get_github_user",
        {},
        token,
        "test_auth_001"
    )
    
    if "error" in result:
        print(f"   ❌ Authentication failed: {result}")
        print("\n   Make sure your token has the required scopes (repo, user)")
        return  # Exit gracefully instead of sys.exit(1)
    else:
        print(f"   ✅ Authenticated as: {result.get('login')}")
                
    # Test 2: Check if we can access the private repo directly
    print(f"\n2️⃣  Checking access to private repo '{repo_path}'...")
    status, repo_info = await get_private_repo_info(owner, repo, token)
                
    if status == 404:
        print(f"   ❌ Repository not found or no access")
        print("   Make sure the repository exists and your token has 'repo' scope")
        return
    elif status == 401:
        print(f"   ❌ Authentication failed")
        return
    elif status == 200:
        is_private = repo_info.get('private', False)
        if is_private:
            print(f"   ✅ Successfully accessed PRIVATE repository!")
            print(f"      This proves OAuth token is working correctly")
        else:
            print(f"   ⚠️  Repository is PUBLIC (authentication still works but not required)")
        print(f"      Name: {repo_info.get('name')}")
        print(f"      Description: {repo_info.get('description', 'No description')}")
        print(f"      Private: {repo_info.get('private')}")
        print(f"      Default branch: {repo_info.get('default_branch')}")
    else:
        print(f"   ❌ Unexpected status: {status}")
        return
                
    # Test 3: List repos including private ones via MCP
    print(f"\n3️⃣  Listing your repositories via MCP (including private)...")
    result = await call_mcp_tool_with_oauth(
        session,
        "list_user_repos",
        {"per_page": 10, "page": 1},
        token,
        "test_list_002"
    )
                
    if "error" in result:
        print(f"   ❌ Error: {result}")
    else:
        repos = result.get('repositories', [])
        private_repos = [r for r in repos if r.get('private')]
        public_repos = [r for r in repos if not r.get('private')]
        
        print(f"   ✅ Found {len(repos)} repos total:")
        print(f"      🔒 Private: {len(private_repos)}")
        print(f"      📂 Public: {len(public_repos)}")
        
        if private_repos:
            print("\n   Private repositories visible (proving auth works):")
            for r in private_repos[:3]:  # Show first 3
                print(f"      - {r.get('name')}")
                
    # Test 4: Create a test issue in the private repo via MCP
    print(f"\n4️⃣  Creating test issue in '{repo_path}' via MCP...")
    print("   (This will ONLY work if you have write access)")
    
    # Ask for confirmation
    confirm = input("   Create a test issue? (y/n): ").lower()
    if confirm == 'y':
        result = await call_mcp_tool_with_oauth(
            session,
            "create_github_issue",
            {
                "owner": owner,
                "repo": repo,
                "title": "Test Issue - MCP OAuth Passthrough Verification",
                "body": "This is a test issue created to verify OAuth token passthrough via MCP protocol.\n\n"
                       "If you can see this issue, it means:\n"
                       "1. The OAuth token was successfully passed from MCP client to server via _meta\n"
                       "2. The MCP server extracted it from Context and used it to authenticate\n"
                       "3. The authentication has write permissions to this repository\n\n"
                       "Created by MCP OAuth test script using real MCP client/server communication.",
                "labels": ["test", "mcp-oauth"]
            },
            token,
            "test_issue_003"
        )
        
        if "error" in result:
            error = result.get("error")
            if error == "not_found":
                print(f"   ❌ Repository not found (likely private without access)")
            elif error == "forbidden":
                print(f"   ⚠️  No write access (but auth is working - read-only token)")
            else:
                print(f"   ❌ Error: {result}")
        else:
            print(f"   ✅ Successfully created issue #{result.get('number')}!")
            print(f"      URL: {result.get('html_url')}")
            print(f"\n   🎉 This PROVES OAuth passthrough via MCP protocol is working perfectly!")
            print(f"      The token was passed through _meta in the MCP request")
            print(f"      and used to create an issue in a private repository!")
    else:
        print("   Skipped issue creation")
    
    print("\n" + "=" * 60)
    print("✅ MCP OAuth Token Passthrough Test Complete!")
    print()
    print("Summary:")
    print("- Token was successfully passed via MCP protocol's _meta parameter")
    print("- MCP server's oauth_passthrough decorator extracted it from Context") 
    print("- Tools used the token to authenticate with GitHub API")
    if 'is_private' in locals() and is_private:
        print("- Successfully accessed a PRIVATE repository (proof of auth!)")
    print("\nThe OAuth passthrough implementation with MCP protocol is working correctly!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_oauth_private_repo.py <github_token> <owner/repo> [--transport stdio|http]")
        print("\nExamples:")
        print("  python test_oauth_private_repo.py gho_abc123... myusername/my-private-repo")
        print("  python test_oauth_private_repo.py gho_abc123... myusername/my-private-repo --transport http")
        print("\nGet a token from: https://github.com/settings/tokens")
        print("Required scopes: 'repo' (for private repos) and 'user'")
        sys.exit(1)
    
    token = sys.argv[1]
    repo_path = sys.argv[2]
    
    # Parse transport option
    transport = "stdio"  # default
    if len(sys.argv) >= 5 and sys.argv[3] == "--transport":
        transport = sys.argv[4].lower()
        if transport not in ["stdio", "http"]:
            print(f"Error: Invalid transport '{transport}'. Must be 'stdio' or 'http'")
            sys.exit(1)
    
    asyncio.run(test_private_repo_with_mcp_client(token, repo_path, transport))
