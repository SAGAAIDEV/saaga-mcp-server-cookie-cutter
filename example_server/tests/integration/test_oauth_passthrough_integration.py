"""Integration tests for OAuth passthrough functionality with real MCP client.

These tests verify that OAuth tokens can be passed through the MCP protocol
from client to server and that the OAuth-protected tools work correctly.
"""

import json
import os
import pytest
from datetime import timedelta
from mcp import ClientSession, types
from tests.integration.conftest import extract_text_content

# Mark all tests as async
pytestmark = pytest.mark.anyio


class TestOAuthPassthroughIntegration:
    """Test OAuth passthrough with real MCP client/server communication."""
    
    async def test_github_tool_without_token(self, mcp_session):
        """Test that GitHub tools correctly reject requests without OAuth tokens.
        
        This test runs with both STDIO and Streamable HTTP transports.
        """
        session, transport = mcp_session
        
        # Call get_github_user without providing OAuth token
        result = await session.call_tool("get_github_user", {})
        
        # Should succeed at protocol level but return auth error
        assert not result.isError, f"Tool call failed at protocol level: {result}"
        
        text_content = extract_text_content(result)
        assert text_content is not None, f"No text content found (transport: {transport})"
        
        # Parse the response
        try:
            data = json.loads(text_content)
            assert "error" in data, f"Expected error response, got: {data}"
            assert data["error"] == "token_not_provided", f"Wrong error type: {data}"
            assert "github" in data.get("message", "").lower(), f"Error message should mention github: {data}"
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {text_content}")
    
    async def test_github_tool_with_mock_token(self, mcp_session):
        """Test that GitHub tools accept tokens via _meta parameter.
        
        This uses a fake token so will get unauthorized from GitHub,
        but proves the token passthrough mechanism works.
        """
        session, transport = mcp_session
        
        # Build request with OAuth token in metadata
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="get_github_user",
                    arguments={},
                    _meta={
                        "oauth_tokens": {
                            "github": "gho_mock_test_token_12345"
                        },
                        "correlationId": "test_oauth_001"
                    }
                )
            )
        )
        
        # Send request with metadata
        result = await session.send_request(
            request,
            types.CallToolResult
        )
        
        # Should succeed at protocol level
        assert not result.isError, f"Protocol error: {result}"
        
        text_content = extract_text_content(result)
        assert text_content is not None
        
        # Parse response
        data = json.loads(text_content)
        
        # Should get unauthorized error from GitHub API (401)
        assert "error" in data, f"Expected error from invalid token, got: {data}"
        assert data["error"] == "unauthorized", f"Expected unauthorized error, got: {data}"
        assert data.get("status_code") == 401, f"Expected 401 status, got: {data}"
    
    async def test_list_repos_without_token(self, mcp_session):
        """Test that list_user_repos correctly rejects requests without tokens."""
        session, transport = mcp_session
        
        result = await session.call_tool("list_user_repos", {
            "per_page": 10,
            "page": 1
        })
        
        assert not result.isError
        
        text_content = extract_text_content(result)
        data = json.loads(text_content)
        
        assert data["error"] == "token_not_provided"
        assert "github" in data.get("message", "").lower()
    
    async def test_create_issue_without_token(self, mcp_session):
        """Test that create_github_issue correctly rejects requests without tokens."""
        session, transport = mcp_session
        
        result = await session.call_tool("create_github_issue", {
            "owner": "test",
            "repo": "test",
            "title": "Test Issue",
            "body": "Test body"
        })
        
        assert not result.isError
        
        text_content = extract_text_content(result)
        data = json.loads(text_content)
        
        assert data["error"] == "token_not_provided"
        assert "github" in data.get("message", "").lower()
    
    @pytest.mark.skipif(
        not os.environ.get("GITHUB_TOKEN"),
        reason="GITHUB_TOKEN environment variable not set"
    )
    async def test_github_tool_with_real_token(self, mcp_session):
        """Test with a real GitHub token from environment.
        
        This test is skipped unless GITHUB_TOKEN is set in environment.
        """
        session, transport = mcp_session
        real_token = os.environ["GITHUB_TOKEN"]
        
        # Build request with real OAuth token
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="get_github_user",
                    arguments={},
                    _meta={
                        "oauth_tokens": {
                            "github": real_token
                        },
                        "correlationId": "test_real_token"
                    }
                )
            )
        )
        
        # Send request with metadata
        result = await session.send_request(
            request,
            types.CallToolResult
        )
        
        assert not result.isError
        
        text_content = extract_text_content(result)
        data = json.loads(text_content)
        
        # Should get successful response with user data
        assert "error" not in data, f"Got error with real token: {data}"
        assert "login" in data, f"Expected user data with 'login' field, got: {data}"
        assert "id" in data, f"Expected user data with 'id' field, got: {data}"
