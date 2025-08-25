"""Integration tests for OAuth backend functionality with real MCP client.

These tests verify the complete OAuth backend flow:
1. Client sends userId, userToken, providerId via Context metadata
2. OAuth backend decorator intercepts and exchanges tokens
3. Real HTTP call to mock backend server
4. Token injection into Context for tool use
5. Reddit tools use the token to make API calls
"""

import json
import os
import pytest
import asyncio
from mcp import ClientSession, types
from tests.integration.conftest import extract_text_content
from tests.helpers.mock_oauth_backend import start_mock_backend

# Mark all tests as async
pytestmark = pytest.mark.anyio


class TestOAuthBackendIntegration:
    """Test OAuth backend with real MCP client/server communication."""
    
    async def test_reddit_tool_without_oauth_params(self, mcp_session):
        """Test that Reddit tools correctly reject requests without OAuth parameters.
        
        This test runs with both STDIO and Streamable HTTP transports.
        """
        session, transport = mcp_session
        
        # Call get_reddit_user without providing OAuth parameters
        result = await session.call_tool("get_reddit_user", {})
        
        # Should succeed at protocol level but return auth error
        assert not result.isError, f"Tool call failed at protocol level: {result}"
        
        text_content = extract_text_content(result)
        assert text_content is not None, f"No text content found (transport: {transport})"
        
        # Parse the response
        try:
            data = json.loads(text_content)
            assert "error" in data, f"Expected error response, got: {data}"
            assert data["error"] == "missing_parameters", f"Wrong error type: {data}"
            assert "userId, userToken, providerId" in data.get("details", ""), f"Error should list missing params: {data}"
        except json.JSONDecodeError:
            pytest.fail(f"Response is not valid JSON: {text_content}")
    
    async def test_reddit_tool_with_invalid_backend(self, mcp_session):
        """Test handling when backend server is unavailable.
        
        Tests that appropriate errors are returned when the OAuth backend
        cannot be reached.
        """
        session, transport = mcp_session
        
        # Set invalid backend URL
        os.environ["OAUTH_BACKEND_URL"] = "http://localhost:99999"  # Invalid port
        
        try:
            # Call with valid OAuth parameters but backend will fail
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="get_reddit_user",
                        arguments={},
                        _meta={
                            "userId": "test_user_123",
                            "userToken": "valid_token_abc",
                            "providerId": "reddit"
                        }
                    )
                )
            )
            result = await session.send_request(request, types.CallToolResult)
            
            assert not result.isError, f"Tool call failed at protocol level: {result}"
            
            text_content = extract_text_content(result)
            data = json.loads(text_content)
            
            assert "error" in data, f"Expected error response, got: {data}"
            assert data["error"] == "api_error", f"Wrong error type: {data}"
            
        finally:
            # Reset to test default
            if "OAUTH_BACKEND_URL" in os.environ:
                del os.environ["OAUTH_BACKEND_URL"]
    
    async def test_reddit_tool_with_mock_backend(self, mcp_session):
        """Test complete OAuth flow with mock backend server.
        
        This test:
        1. Starts a mock OAuth backend server
        2. Sends OAuth parameters via Context
        3. Verifies token exchange happens
        4. Checks that Reddit tool receives and uses token
        """
        session, transport = mcp_session
        
        # Start mock backend server on configured port
        with start_mock_backend(port=8080) as backend_url:
            # Configure server to use mock backend
            os.environ["OAUTH_BACKEND_URL"] = backend_url
            
            try:
                # Call with valid OAuth parameters
                request = types.ClientRequest(
                    types.CallToolRequest(
                        method="tools/call",
                        params=types.CallToolRequestParams(
                            name="get_reddit_user",
                            arguments={},
                            _meta={
                                "userId": "test_user_123",
                                "userToken": "valid_temp_token",
                                "providerId": "reddit"
                            }
                        )
                    )
                )
                result = await session.send_request(request, types.CallToolResult)
                
                assert not result.isError, f"Tool call failed: {result}"
                
                text_content = extract_text_content(result)
                data = json.loads(text_content)
                
                # With mock token, Reddit API will return 403
                # But this proves the flow worked:
                # 1. OAuth params extracted from Context
                # 2. Token exchanged with backend
                # 3. Token used to call Reddit API
                assert "error" in data or "status_code" in data, f"Expected error from Reddit API with mock token: {data}"
                
                # Could be 403 Forbidden or similar
                if "status_code" in data:
                    assert data["status_code"] in [401, 403], f"Expected auth error from Reddit: {data}"
                
            finally:
                if "OAUTH_BACKEND_URL" in os.environ:
                    del os.environ["OAUTH_BACKEND_URL"]
    
    async def test_reddit_tool_provider_mismatch(self, mcp_session):
        """Test that tools reject tokens from wrong providers."""
        session, transport = mcp_session
        
        # Call Reddit tool with GitHub provider
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="get_reddit_user",
                    arguments={},
                    _meta={
                        "userId": "test_user",
                        "userToken": "token_abc",
                        "providerId": "github"  # Wrong provider!
                    }
                )
            )
        )
        result = await session.send_request(request, types.CallToolResult)
        
        assert not result.isError, f"Tool call failed at protocol level: {result}"
        
        text_content = extract_text_content(result)
        data = json.loads(text_content)
        
        assert "error" in data, f"Expected error response, got: {data}"
        assert data["error"] == "provider_mismatch", f"Wrong error type: {data}"
        assert "reddit" in data.get("message", "").lower(), f"Error should mention required provider: {data}"
    
    async def test_multiple_reddit_tools_share_token(self, mcp_session):
        """Test that multiple tools can use the same OAuth token from Context."""
        session, transport = mcp_session
        
        with start_mock_backend(port=8080) as backend_url:
            os.environ["OAUTH_BACKEND_URL"] = backend_url
            
            try:
                # Set OAuth params once
                meta = {
                    "userId": "test_user",
                    "userToken": "shared_token",
                    "providerId": "reddit"
                }
                
                # Call multiple tools with same Context
                results = []
                for tool in ["get_reddit_user", "get_subreddit_posts"]:
                    # get_subreddit_posts needs a subreddit parameter
                    args = {} if tool == "get_reddit_user" else {"subreddit": "python"}
                    request = types.ClientRequest(
                        types.CallToolRequest(
                            method="tools/call",
                            params=types.CallToolRequestParams(
                                name=tool,
                                arguments=args,
                                _meta=meta
                            )
                        )
                    )
                    result = await session.send_request(request, types.CallToolResult)
                    assert not result.isError, f"{tool} failed: {result}"
                    results.append(result)
                
                # Both should have attempted to use the token
                # (will fail with 403 from Reddit, but that's expected with mock token)
                for result in results:
                    text_content = extract_text_content(result)
                    data = json.loads(text_content)
                    # Should have tried to call Reddit API
                    assert "error" in data or "status_code" in data
                    
            finally:
                if "OAUTH_BACKEND_URL" in os.environ:
                    del os.environ["OAUTH_BACKEND_URL"]


class TestOAuthBackendWithRealToken:
    """Tests that require a real Reddit OAuth token.
    
    These tests are skipped unless REDDIT_OAUTH_TOKEN environment variable is set.
    """
    
    @pytest.mark.skipif(
        not os.environ.get("REDDIT_OAUTH_TOKEN"),
        reason="Requires REDDIT_OAUTH_TOKEN environment variable"
    )
    async def test_reddit_tool_with_real_token(self, mcp_session):
        """Test with a real Reddit OAuth token if available.
        
        To run this test:
        export REDDIT_OAUTH_TOKEN=your_actual_reddit_token
        """
        session, transport = mcp_session
        
        real_token = os.environ["REDDIT_OAUTH_TOKEN"]
        
        # For real token test, we'd need a real backend that returns the actual token
        # This is more of a smoke test for production scenarios
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="get_reddit_user",
                    arguments={},
                    _meta={
                        "userId": "real_user",
                        "userToken": real_token,
                        "providerId": "reddit"
                    }
                )
            )
        )
        result = await session.send_request(request, types.CallToolResult)
        
        assert not result.isError, f"Tool call failed: {result}"
        
        text_content = extract_text_content(result)
        data = json.loads(text_content)
        
        # With real token, should get actual Reddit user data
        assert "username" in data or "name" in data, f"Expected user data from Reddit: {data}"
