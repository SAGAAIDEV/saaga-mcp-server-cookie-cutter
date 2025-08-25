"""OAuth API Client for backend token exchange.

This module handles communication with the backend API service
to exchange temporary tokens for actual OAuth access tokens.
"""

import asyncio
from typing import Optional, Dict, Any
import json
from {{ cookiecutter.project_slug }}.log_system.unified_logger import UnifiedLogger

try:
    import httpx
except ImportError:
    httpx = None

unified_logger = UnifiedLogger.get_logger('oauth_api_client')


class OAuthAPIClient:
    """Client for OAuth backend API communication."""
    
    def __init__(self, backend_url: str, timeout: int = 30):
        """Initialize the OAuth API client.
        
        Args:
            backend_url: The backend API base URL (e.g., "http://localhost:8080")
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url.rstrip('/')
        self.timeout = timeout
        self.endpoint = "/api/connectors/requestAuth"
        
        if not httpx:
            raise ImportError(
                "httpx is required for OAuth backend functionality. "
                "Install it with: pip install httpx"
            )
    
    async def exchange_token(
        self,
        user_id: str,
        user_token: str,
        provider_id: str
    ) -> Optional[str]:
        """Exchange a user token for an access token.
        
        Args:
            user_id: The user identifier
            user_token: The user token from the client
            provider_id: The OAuth provider identifier
        
        Returns:
            The access token if successful, None otherwise
        """
        try:
            return await self._real_exchange(user_id, user_token, provider_id)
        except Exception as e:
            unified_logger.error(f"Token exchange failed: {str(e)}")
            raise
    async def _real_exchange(
        self,
        user_id: str,
        user_token: str,
        provider_id: str
    ) -> Optional[str]:
        """Exchange token with real backend API.
        
        Args:
            user_id: The user identifier
            user_token: The user token from the client
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
            "userToken": user_token,
            "providerId": provider_id
        }
        
        unified_logger.info(f"OAuth API Client: Sending token exchange request to backend")
        unified_logger.info(f"  Backend URL: {url}")
        unified_logger.info(f"  Request Body:")
        unified_logger.info(f"    userId: {user_id}")
        unified_logger.info(f"    userToken: {user_token[:20]}... (length: {len(user_token)} chars)")
        unified_logger.info(f"    providerId: {provider_id}")
        
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
                        unified_logger.warning("Backend returned 200 but no accessToken in response")
                        return None
                    
                    unified_logger.info(f"OAuth API Client: Successfully received access token from backend")
                    unified_logger.info(f"  Token Length: {len(access_token)} characters")
                    unified_logger.info(f"  Token Preview: {access_token[:10]}... (hidden for security)")
                    
                    return access_token
                
                elif response.status_code == 401:
                    unified_logger.warning(f"OAuth API Client: Backend returned 401 Unauthorized")
                    unified_logger.warning(f"  Provider: {provider_id}")
                    unified_logger.warning(f"  Reason: Invalid or expired temporary token")
                    raise ValueError("Invalid or expired temporary token")
                
                elif response.status_code == 403:
                    unified_logger.warning(f"OAuth API Client: Backend returned 403 Forbidden")
                    unified_logger.warning(f"  User: {user_id}")
                    unified_logger.warning(f"  Provider: {provider_id}")
                    raise ValueError("User not authorized for this provider")
                
                elif response.status_code == 404:
                    unified_logger.warning(f"OAuth API Client: Backend returned 404 Not Found")
                    unified_logger.warning(f"  Provider: {provider_id}")
                    raise ValueError(f"Provider {provider_id} not configured")
                
                else:
                    unified_logger.error(f"OAuth API Client: Unexpected response from backend")
                    unified_logger.error(f"  Status Code: {response.status_code}")
                    unified_logger.error(f"  Response: {response.text[:200]}...")
                    raise ValueError(f"Backend returned status {response.status_code}: {response.text}")
                    
            except httpx.TimeoutException:
                unified_logger.error(f"OAuth API Client: Request timeout after {self.timeout} seconds")
                raise ValueError("Backend API request timed out")
            
            except httpx.RequestError as e:
                unified_logger.error(f"OAuth API Client: Request failed - {str(e)}")
                raise ValueError(f"Failed to connect to backend API: {str(e)}")
            
            except json.JSONDecodeError as e:
                unified_logger.error(f"OAuth API Client: Invalid JSON response - {str(e)}")
                raise ValueError("Backend returned invalid JSON response")
    
    async def health_check(self) -> bool:
        """Check if the backend API is reachable.
        
        Returns:
            True if the backend is healthy, False otherwise
        """
        if not self.backend_url:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Try a simple GET to the base URL or a health endpoint
                response = await client.get(f"{self.backend_url}/health")
                return response.status_code in [200, 204, 404]  # 404 is ok if health endpoint doesn't exist
        except Exception as e:
            unified_logger.warning(f"Health check failed: {str(e)}")
            return False