{% if cookiecutter.include_oauth_backend == "yes" -%}
"""Unit tests for OAuth backend functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from {{ cookiecutter.project_slug }}.decorators.oauth_backend import oauth_backend
from {{ cookiecutter.project_slug }}.clients.oauth_api_client import OAuthAPIClient


class TestOAuthBackendDecorator:
    """Test the oauth_backend decorator."""
    
    @pytest.mark.asyncio
    async def test_decorator_with_valid_parameters(self):
        """Test decorator with valid userId, tempToken, and providerId."""
        # Create a mock function to decorate
        mock_func = AsyncMock(return_value={"status": "success"})
        
        # Create mock context with OAuth parameters
        ctx = Mock()
        ctx.request_context.meta = {
            "userId": "user123",
            "tempToken": "temp_abc456",
            "providerId": "reddit"
        }
        
        # Mock the API client
        with patch("{{ cookiecutter.project_slug }}.decorators.oauth_backend.OAuthAPIClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.exchange_token = AsyncMock(return_value="access_token_xyz789")
            
            # Apply decorator
            config = {"oauth_backend_url": "https://api.example.com", "oauth_backend_mock_mode": "no"}
            decorated = oauth_backend("reddit")(mock_func, config)
            
            # Call decorated function
            result = await decorated(ctx=ctx)
            
            # Verify token exchange was called
            mock_client.exchange_token.assert_called_once_with(
                user_id="user123",
                temp_token="temp_abc456",
                provider_id="reddit"
            )
            
            # Verify token was injected into context
            assert ctx.request_context.meta["current_oauth_token"] == "access_token_xyz789"
            assert ctx.request_context.meta["oauth_provider"] == "reddit"
            
            # Verify original function was called
            mock_func.assert_called_once()
            assert result == {"status": "success"}
    
    @pytest.mark.asyncio
    async def test_decorator_missing_parameters(self):
        """Test decorator when required parameters are missing."""
        mock_func = AsyncMock()
        
        # Context missing tempToken
        ctx = Mock()
        ctx.request_context.meta = {
            "userId": "user123",
            "providerId": "reddit"
            # Missing tempToken
        }
        
        config = {"oauth_backend_url": "https://api.example.com"}
        decorated = oauth_backend("reddit")(mock_func, config)
        
        result = await decorated(ctx=ctx)
        
        # Should return error for missing parameters
        assert result["error"] == "missing_parameters"
        assert "tempToken" in result["details"]
        
        # Original function should not be called
        mock_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_decorator_provider_mismatch(self):
        """Test decorator when providerId doesn't match expected provider."""
        mock_func = AsyncMock()
        
        ctx = Mock()
        ctx.request_context.meta = {
            "userId": "user123",
            "tempToken": "temp_abc456",
            "providerId": "github"  # Mismatch - decorator expects "reddit"
        }
        
        config = {"oauth_backend_url": "https://api.example.com"}
        decorated = oauth_backend("reddit")(mock_func, config)
        
        result = await decorated(ctx=ctx)
        
        # Should return provider mismatch error
        assert result["error"] == "provider_mismatch"
        assert result["provider"] == "reddit"
        assert "github" in result["details"]
        
        mock_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_decorator_api_error_handling(self):
        """Test decorator handles API errors gracefully."""
        mock_func = AsyncMock()
        
        ctx = Mock()
        ctx.request_context.meta = {
            "userId": "user123",
            "tempToken": "temp_abc456",
            "providerId": "reddit"
        }
        
        with patch("{{ cookiecutter.project_slug }}.decorators.oauth_backend.OAuthAPIClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.exchange_token = AsyncMock(side_effect=Exception("API timeout"))
            
            config = {"oauth_backend_url": "https://api.example.com"}
            decorated = oauth_backend("reddit")(mock_func, config)
            
            result = await decorated(ctx=ctx)
            
            # Should return API error
            assert result["error"] == "api_error"
            assert "API timeout" in result["details"]
            
            mock_func.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_decorator_mock_mode(self):
        """Test decorator in mock mode."""
        mock_func = AsyncMock(return_value={"data": "test"})
        
        ctx = Mock()
        ctx.request_context.meta = {
            "userId": "user123",
            "tempToken": "temp_abc456",
            "providerId": "reddit"
        }
        
        with patch("{{ cookiecutter.project_slug }}.decorators.oauth_backend.OAuthAPIClient") as MockClient:
            mock_client = MockClient.return_value
            mock_client.exchange_token = AsyncMock(return_value="mock_reddit_token_123456789")
            
            config = {"oauth_backend_mock_mode": "yes"}
            decorated = oauth_backend("reddit")(mock_func, config)
            
            result = await decorated(ctx=ctx)
            
            # Mock client should be initialized with mock_mode=True
            MockClient.assert_called_once_with(backend_url="", mock_mode=True)
            
            # Should still exchange token
            mock_client.exchange_token.assert_called_once()
            
            # Function should be called
            mock_func.assert_called_once()
            assert result == {"data": "test"}


class TestOAuthAPIClient:
    """Test the OAuth API client."""
    
    @pytest.mark.asyncio
    async def test_mock_exchange_success(self):
        """Test mock token exchange returns expected tokens."""
        client = OAuthAPIClient(mock_mode=True)
        
        token = await client.exchange_token(
            user_id="user123",
            temp_token="temp_abc",
            provider_id="reddit"
        )
        
        assert token == "mock_reddit_token_123456789"
    
    @pytest.mark.asyncio
    async def test_mock_exchange_error_token(self):
        """Test mock exchange with error token."""
        client = OAuthAPIClient(mock_mode=True)
        
        with pytest.raises(Exception, match="Mock error: Invalid temp token"):
            await client.exchange_token(
                user_id="user123",
                temp_token="error_token",
                provider_id="reddit"
            )
    
    @pytest.mark.asyncio
    async def test_mock_exchange_empty_response(self):
        """Test mock exchange with empty response token."""
        client = OAuthAPIClient(mock_mode=True)
        
        token = await client.exchange_token(
            user_id="user123",
            temp_token="empty_response",
            provider_id="reddit"
        )
        
        assert token is None
    
    @pytest.mark.asyncio
    async def test_real_exchange_success(self):
        """Test real API token exchange with mocked httpx."""
        with patch("{{ cookiecutter.project_slug }}.clients.oauth_api_client.httpx") as mock_httpx:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"accessToken": "real_access_token_xyz"}
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client
            
            client = OAuthAPIClient(backend_url="https://api.example.com", mock_mode=False)
            
            token = await client.exchange_token(
                user_id="user123",
                temp_token="temp_abc",
                provider_id="reddit"
            )
            
            assert token == "real_access_token_xyz"
            
            # Verify correct API call
            mock_client.post.assert_called_once_with(
                "https://api.example.com/api/connectors/requestAuth",
                json={
                    "userId": "user123",
                    "tempToken": "temp_abc",
                    "providerId": "reddit"
                },
                headers={"Content-Type": "application/json"}
            )
    
    @pytest.mark.asyncio
    async def test_real_exchange_unauthorized(self):
        """Test real API exchange with 401 response."""
        with patch("{{ cookiecutter.project_slug }}.clients.oauth_api_client.httpx") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 401
            
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client
            
            client = OAuthAPIClient(backend_url="https://api.example.com", mock_mode=False)
            
            with pytest.raises(Exception, match="Invalid or expired temporary token"):
                await client.exchange_token(
                    user_id="user123",
                    temp_token="invalid_temp",
                    provider_id="reddit"
                )
    
    @pytest.mark.asyncio
    async def test_health_check_mock_mode(self):
        """Test health check in mock mode always returns True."""
        client = OAuthAPIClient(mock_mode=True)
        
        result = await client.health_check()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_real_success(self):
        """Test health check with real backend."""
        with patch("{{ cookiecutter.project_slug }}.clients.oauth_api_client.httpx") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client
            
            client = OAuthAPIClient(backend_url="https://api.example.com", mock_mode=False)
            
            result = await client.health_check()
            assert result is True
{% endif -%}