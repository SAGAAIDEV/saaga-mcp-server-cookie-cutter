{% if cookiecutter.include_oauth_backend == "yes" -%}
"""OAuth API Client for backend token exchange.

This module handles communication with the backend API service
to exchange temporary tokens for actual OAuth access tokens.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
import json

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)


class OAuthAPIClient:
    """Client for OAuth backend API communication."""
    
    def __init__(self, backend_url: str = "", mock_mode: bool = False, timeout: int = 30):
        """Initialize the OAuth API client.
        
        Args:
            backend_url: The backend API base URL (e.g., "https://api.example.com")
            mock_mode: If True, return mock tokens instead of calling API
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url.rstrip('/')
        self.mock_mode = mock_mode
        self.timeout = timeout
        self.endpoint = "/api/connectors/requestAuth"
        
        if not mock_mode and not httpx:
            raise ImportError(
                "httpx is required for OAuth backend functionality. "
                "Install it with: pip install httpx"
            )
    
    async def exchange_token(
        self,
        user_id: str,
        temp_token: str,
        provider_id: str
    ) -> Optional[str]:
        """Exchange a temporary token for an access token.
        
        Args:
            user_id: The user identifier
            temp_token: The temporary token from the client
            provider_id: The OAuth provider identifier
        
        Returns:
            The access token if successful, None otherwise
        """
        if self.mock_mode:
            return await self._mock_exchange(user_id, temp_token, provider_id)
        
        try:
            return await self._real_exchange(user_id, temp_token, provider_id)
        except Exception as e:
            logger.error(f"Token exchange failed: {str(e)}")
            raise
    
    async def _mock_exchange(
        self,
        user_id: str,
        temp_token: str,
        provider_id: str
    ) -> str:
        """Return mock access tokens for testing.
        
        Args:
            user_id: The user identifier
            temp_token: The temporary token from the client
            provider_id: The OAuth provider identifier
        
        Returns:
            A mock access token
        """
        logger.info(f"Mock mode: Returning test token for {provider_id}")
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Return provider-specific mock tokens
        mock_tokens = {
            "reddit": "mock_reddit_token_123456789",
            "github": "gho_mockGitHubToken123456789",
            "google": "ya29.mockGoogleToken123456789",
            "microsoft": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Ik1vY2tNaWNyb3NvZnRUb2tlbjEyMzQ1Njc4OSJ9",
        }
        
        # Special cases for testing error scenarios
        if temp_token == "error_token":
            raise Exception("Mock error: Invalid temp token")
        
        if temp_token == "empty_response":
            return None
        
        return mock_tokens.get(provider_id, f"mock_{provider_id}_token_{user_id}")
    
    async def _real_exchange(
        self,
        user_id: str,
        temp_token: str,
        provider_id: str
    ) -> Optional[str]:
        """Exchange token with real backend API.
        
        Args:
            user_id: The user identifier
            temp_token: The temporary token from the client
            provider_id: The OAuth provider identifier
        
        Returns:
            The access token if successful, None otherwise
        
        Raises:
            Exception: If the API call fails
        """
        if not self.backend_url:
            raise ValueError("Backend URL is required when mock mode is disabled")
        
        url = f"{self.backend_url}{self.endpoint}"
        
        # Prepare request body with exact parameter names from JIRA
        request_body = {
            "userId": user_id,
            "tempToken": temp_token,
            "providerId": provider_id
        }
        
        logger.info(f"Exchanging token with backend: {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check response status
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get("accessToken")
                    
                    if not access_token:
                        logger.warning("Backend returned 200 but no accessToken in response")
                        return None
                    
                    return access_token
                
                elif response.status_code == 401:
                    logger.warning(f"Unauthorized: Invalid temp token for {provider_id}")
                    raise Exception("Invalid or expired temporary token")
                
                elif response.status_code == 403:
                    logger.warning(f"Forbidden: User {user_id} not authorized for {provider_id}")
                    raise Exception("User not authorized for this provider")
                
                elif response.status_code == 404:
                    logger.warning(f"Not found: Provider {provider_id} not configured")
                    raise Exception(f"Provider {provider_id} not configured")
                
                else:
                    logger.error(f"Unexpected status code: {response.status_code}")
                    raise Exception(f"Backend returned status {response.status_code}: {response.text}")
                    
            except httpx.TimeoutException:
                logger.error(f"Request timeout after {self.timeout} seconds")
                raise Exception("Backend API request timed out")
            
            except httpx.RequestError as e:
                logger.error(f"Request failed: {str(e)}")
                raise Exception(f"Failed to connect to backend API: {str(e)}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response: {str(e)}")
                raise Exception("Backend returned invalid JSON response")
    
    async def health_check(self) -> bool:
        """Check if the backend API is reachable.
        
        Returns:
            True if the backend is healthy, False otherwise
        """
        if self.mock_mode:
            return True
        
        if not self.backend_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Try a simple GET to the base URL or a health endpoint
                response = await client.get(f"{self.backend_url}/health")
                return response.status_code in [200, 204, 404]  # 404 is ok if health endpoint doesn't exist
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            return False
{% endif -%}