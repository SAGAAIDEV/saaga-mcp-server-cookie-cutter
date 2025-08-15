{% if cookiecutter.include_oauth_passthrough == "yes" -%}
"""Unit tests for OAuth token passthrough functionality.

Tests the decorator and tools WITHOUT making actual API calls.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from {{ cookiecutter.project_slug }}.decorators.oauth_passthrough import oauth_passthrough
from {{ cookiecutter.project_slug }}.tools.github_passthrough_tools import (
    get_github_user,
    list_user_repos,
    create_github_issue,
    oauth_passthrough_tools
)


class TestToolOrganization:
    """Test that tools are organized correctly for registration."""
    
    def test_oauth_passthrough_tools_structure(self):
        """Verify OAuth tools are organized with provider information."""
        # Should be list of (provider, function) tuples
        assert len(oauth_passthrough_tools) == 3
        
        # Check each tool has correct structure
        for provider, tool_func in oauth_passthrough_tools:
            assert provider == "github"  # All current tools are GitHub
            assert callable(tool_func)
        
        # Check specific tools are included
        tool_funcs = [func for _, func in oauth_passthrough_tools]
        assert get_github_user in tool_funcs
        assert list_user_repos in tool_funcs
        assert create_github_issue in tool_funcs


class TestOAuthPassthroughDecorator:
    """Test the oauth_passthrough decorator behavior."""
    
    @pytest.mark.asyncio
    async def test_decorator_with_valid_token(self):
        """Test decorator passes through when token is present."""
        # Create a mock function
        mock_func = AsyncMock(return_value={"status": "success"})
        
        # Apply the decorator
        decorated = oauth_passthrough("github")(mock_func)
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = {
            "oauth_tokens": {
                "github": "gho_test_token_123"
            }
        }
        
        # Call the decorated function
        result = await decorated(ctx=mock_ctx)
        
        # Verify the original function was called
        mock_func.assert_called_once_with(ctx=mock_ctx)
        assert result == {"status": "success"}
        
        # Verify token was added to meta
        assert mock_ctx.request_context.meta["current_oauth_token"] == "gho_test_token_123"
        assert mock_ctx.request_context.meta["oauth_provider"] == "github"
    
    @pytest.mark.asyncio
    async def test_decorator_without_token(self):
        """Test decorator returns error when token is missing."""
        # Create a mock function
        mock_func = AsyncMock(return_value={"status": "success"})
        
        # Apply the decorator
        decorated = oauth_passthrough("github")(mock_func)
        
        # Create mock context WITHOUT token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = {
            "oauth_tokens": {}  # No github token
        }
        
        # Call the decorated function
        result = await decorated(ctx=mock_ctx)
        
        # Verify the original function was NOT called
        mock_func.assert_not_called()
        
        # Verify error response
        assert result["error"] == "token_not_provided"
        assert "github" in result["message"].lower()
        assert result["provider"] == "github"
    
    @pytest.mark.asyncio
    async def test_decorator_without_context(self):
        """Test decorator returns error when context is missing."""
        # Create a mock function
        mock_func = AsyncMock(return_value={"status": "success"})
        
        # Apply the decorator
        decorated = oauth_passthrough("github")(mock_func)
        
        # Call without context
        result = await decorated()
        
        # Verify the original function was NOT called
        mock_func.assert_not_called()
        
        # Verify error response
        assert result["error"] == "token_not_provided"
        assert "github" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_decorator_with_wrong_provider_token(self):
        """Test decorator returns error when token is for different provider."""
        # Create a mock function
        mock_func = AsyncMock(return_value={"status": "success"})
        
        # Apply the decorator for GitHub
        decorated = oauth_passthrough("github")(mock_func)
        
        # Create mock context with Google token only
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = {
            "oauth_tokens": {
                "google": "ya29.test_token"  # Wrong provider
            }
        }
        
        # Call the decorated function
        result = await decorated(ctx=mock_ctx)
        
        # Verify the original function was NOT called
        mock_func.assert_not_called()
        
        # Verify error response
        assert result["error"] == "token_not_provided"
        assert "github" in result["message"].lower()


class TestGitHubPassthroughTools:
    """Test GitHub tools with mocked API calls."""
    
    @pytest.mark.asyncio
    @patch('{{ cookiecutter.project_slug }}.tools.github_passthrough_tools.httpx.AsyncClient')
    async def test_get_github_user_success(self, mock_client_class):
        """Test get_github_user with valid token."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "login": "testuser",
            "id": 12345,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        # Mock the client
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = MagicMock()
        mock_ctx.request_context.meta.get.return_value = "gho_test_token_123"
        
        # Call the function
        result = await get_github_user(ctx=mock_ctx)
        
        # Verify API was called correctly
        mock_client.get.assert_called_once_with(
            "https://api.github.com/user",
            headers={
                "Authorization": "Bearer gho_test_token_123",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=10.0
        )
        
        # Verify result
        assert result["login"] == "testuser"
        assert result["id"] == 12345
    
    @pytest.mark.asyncio
    @patch('{{ cookiecutter.project_slug }}.tools.github_passthrough_tools.httpx.AsyncClient')
    async def test_get_github_user_unauthorized(self, mock_client_class):
        """Test get_github_user with invalid token."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # Mock the client
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = MagicMock()
        mock_ctx.request_context.meta.get.return_value = "invalid_token"
        
        # Call the function
        result = await get_github_user(ctx=mock_ctx)
        
        # Verify error response
        assert result["error"] == "unauthorized"
        assert result["status_code"] == 401
        assert "invalid" in result["message"].lower() or "expired" in result["message"].lower()
    
    @pytest.mark.asyncio
    async def test_get_github_user_no_context(self):
        """Test get_github_user without context."""
        # Call without context
        result = await get_github_user()
        
        # Verify error response
        assert result["error"] == "no_context"
        assert "context not available" in result["message"].lower()
    
    @pytest.mark.asyncio
    @patch('{{ cookiecutter.project_slug }}.tools.github_passthrough_tools.httpx.AsyncClient')
    async def test_list_user_repos_success(self, mock_client_class):
        """Test list_user_repos with valid token."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "name": "repo1",
                "full_name": "user/repo1",
                "description": "Test repo 1",
                "private": False,
                "html_url": "https://github.com/user/repo1",
                "language": "Python",
                "stargazers_count": 10,
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "name": "repo2",
                "full_name": "user/repo2",
                "description": "Test repo 2",
                "private": True,
                "html_url": "https://github.com/user/repo2",
                "language": "JavaScript",
                "stargazers_count": 5,
                "updated_at": "2024-01-02T00:00:00Z"
            }
        ]
        
        # Mock the client
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = MagicMock()
        mock_ctx.request_context.meta.get.return_value = "gho_test_token_123"
        
        # Call the function
        result = await list_user_repos(per_page=10, page=1, ctx=mock_ctx)
        
        # Verify API was called correctly
        mock_client.get.assert_called_once_with(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": "Bearer gho_test_token_123",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            params={
                "per_page": 10,
                "page": 1,
                "sort": "updated"
            },
            timeout=10.0
        )
        
        # Verify result
        assert len(result["repositories"]) == 2
        assert result["count"] == 2
        assert result["repositories"][0]["name"] == "repo1"
        assert result["repositories"][1]["private"] == True
    
    @pytest.mark.asyncio
    @patch('{{ cookiecutter.project_slug }}.tools.github_passthrough_tools.httpx.AsyncClient')
    async def test_create_github_issue_success(self, mock_client_class):
        """Test create_github_issue with valid token."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 42,
            "title": "Test Issue",
            "html_url": "https://github.com/owner/repo/issues/42",
            "state": "open",
            "created_at": "2024-01-01T00:00:00Z",
            "body": "Test issue body",
            "labels": [{"name": "bug"}, {"name": "help wanted"}],
            "assignees": [{"login": "user1"}]
        }
        
        # Mock the client
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = MagicMock()
        mock_ctx.request_context.meta.get.return_value = "gho_test_token_123"
        
        # Call the function
        result = await create_github_issue(
            owner="owner",
            repo="repo",
            title="Test Issue",
            body="Test issue body",
            labels=["bug", "help wanted"],
            assignees=["user1"],
            ctx=mock_ctx
        )
        
        # Verify API was called correctly
        mock_client.post.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/issues",
            headers={
                "Authorization": "Bearer gho_test_token_123",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            json={
                "title": "Test Issue",
                "body": "Test issue body",
                "labels": ["bug", "help wanted"],
                "assignees": ["user1"]
            },
            timeout=10.0
        )
        
        # Verify result
        assert result["number"] == 42
        assert result["title"] == "Test Issue"
        assert result["html_url"] == "https://github.com/owner/repo/issues/42"
        assert result["labels"] == ["bug", "help wanted"]
        assert result["assignees"] == ["user1"]
    
    @pytest.mark.asyncio
    @patch('{{ cookiecutter.project_slug }}.tools.github_passthrough_tools.httpx.AsyncClient')
    async def test_create_github_issue_forbidden(self, mock_client_class):
        """Test create_github_issue without permission."""
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        
        # Mock the client
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create mock context with token
        mock_ctx = Mock()
        mock_ctx.request_context = Mock()
        mock_ctx.request_context.meta = MagicMock()
        mock_ctx.request_context.meta.get.return_value = "gho_limited_token"
        
        # Call the function
        result = await create_github_issue(
            owner="owner",
            repo="repo",
            title="Test Issue",
            ctx=mock_ctx
        )
        
        # Verify error response
        assert result["error"] == "forbidden"
        assert result["status_code"] == 403
        assert "permission" in result["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
{% endif -%}