{% if cookiecutter.include_oauth_backend == "yes" -%}
"""OAuth Backend Decorator - Exchanges temp tokens for access tokens via backend API.

This decorator handles OAuth token exchange with a backend service.
It extracts userId, userToken, and providerId from Context metadata,
calls a backend API to exchange the temp token for a real access token,
and injects that token into the context for tools to use.
"""

from functools import wraps
from typing import Callable, Any, Awaitable, Optional, Dict
import asyncio
from {{ cookiecutter.project_slug }}.log_system.unified_logger import UnifiedLogger

def oauth_backend(provider: str):
    """Exchange temp tokens for access tokens via backend API.
    
    This decorator:
    1. Checks Context for userId, userToken, and providerId
    2. Calls backend API to exchange temp token for access token
    3. Injects the access token into context for tools to use
    4. Returns graceful errors if token exchange fails
    
    Args:
        provider: The OAuth provider name (e.g., 'reddit', 'google')
    
    Returns:
        Decorator function that handles token exchange
    """
    def decorator(func: Callable[..., Awaitable[Any]], config: dict = None) -> Callable[..., Awaitable[Any]]:
        """Apply OAuth backend token exchange to a function.
        
        Args:
            func: The async function to decorate
            config: Configuration dict with backend_url and other settings
        
        Returns:
            Wrapped function that handles token exchange
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            from {{ cookiecutter.project_slug }}.clients.oauth_api_client import OAuthAPIClient
            
            unified_logger = UnifiedLogger.get_logger(f'oauth_backend.{provider}')
            
            try:
                # Get Context from kwargs (following SAAGA pattern)
                ctx = kwargs.get("ctx")
                
                if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
                    meta = ctx.request_context.meta
                    
                    # Extract OAuth backend parameters from meta
                    user_id = None
                    user_token = None
                    provider_id = None
                    
                    if hasattr(meta, 'get'):
                        user_id = meta.get('userId')
                        user_token = meta.get('userToken')
                        provider_id = meta.get('providerId')
                    elif hasattr(meta, 'userId'):
                        user_id = getattr(meta, 'userId', None)
                        user_token = getattr(meta, 'userToken', None)
                        provider_id = getattr(meta, 'providerId', None)
                    
                    # Check if all required parameters are present
                    if user_id and user_token and provider_id:
                        unified_logger.info(f"OAuth Backend: Received token exchange request")
                        unified_logger.info(f"  Provider: {provider}")
                        unified_logger.info(f"  User ID: {user_id}")
                        unified_logger.info(f"  User Token: {user_token[:20]}... (length: {len(user_token)} chars)")
                        unified_logger.info(f"  Provider ID: {provider_id}")
                        # Validate parameters
                        if not isinstance(user_id, str) or not user_id.strip():
                            unified_logger.warning(f"OAuth Backend: Invalid userId format for {provider}")
                            return {
                                "error": "invalid_parameter",
                                "message": f"Invalid userId format for {provider}",
                                "provider": provider,
                                "details": "userId must be a non-empty string"
                            }
                        
                        if not isinstance(user_token, str) or not user_token.strip():
                            unified_logger.warning(f"OAuth Backend: Invalid userToken format for {provider}")
                            return {
                                "error": "invalid_parameter",
                                "message": f"Invalid userToken format for {provider}",
                                "provider": provider,
                                "details": "userToken must be a non-empty string"
                            }
                        
                        if not isinstance(provider_id, str) or not provider_id.strip():
                            unified_logger.warning(f"OAuth Backend: Invalid providerId format for {provider}")
                            return {
                                "error": "invalid_parameter",
                                "message": f"Invalid providerId format for {provider}",
                                "provider": provider,
                                "details": "providerId must be a non-empty string"
                            }
                        
                        # Check if provider matches
                        if provider_id != provider:
                            unified_logger.info(f"OAuth Backend: Provider mismatch - expected {provider}, got {provider_id}")
                            return {
                                "error": "provider_mismatch",
                                "message": f"This tool requires {provider} authentication",
                                "provider": provider,
                                "details": f"Received providerId: {provider_id}"
                            }
                        
                        # Initialize API client
                        backend_url = config.get('oauth_backend_url', '') if config else ''
                        
                        if not backend_url:
                            unified_logger.error("OAuth Backend: No backend URL configured")
                            return {
                                "error": "configuration_error",
                                "message": "OAuth backend not configured",
                                "provider": provider,
                                "details": "Backend URL is required"
                            }
                        
                        client = OAuthAPIClient(backend_url=backend_url)
                        
                        # Exchange temp token for access token
                        unified_logger.info(f"OAuth Backend: Exchanging user token for {provider} access token")
                        
                        try:
                            access_token = await client.exchange_token(
                                user_id=user_id,
                                user_token=user_token,
                                provider_id=provider_id
                            )
                            
                            if not access_token:
                                unified_logger.warning(f"OAuth Backend: No access token returned for {provider}")
                                return {
                                    "error": "token_exchange_failed",
                                    "message": f"Failed to obtain {provider} access token",
                                    "provider": provider,
                                    "details": "Backend returned empty token"
                                }
                            
                            # Inject access token into context
                            if hasattr(meta, '__setitem__'):
                                meta['current_oauth_token'] = access_token
                                meta['oauth_provider'] = provider
                            else:
                                setattr(meta, 'current_oauth_token', access_token)
                                setattr(meta, 'oauth_provider', provider)
                            
                            unified_logger.info(f"OAuth Backend: Successfully obtained {provider} access token")
                            unified_logger.info(f"  Injecting token into Context metadata for tool use")
                            
                            # Call the wrapped function with token available
                            result = await func(*args, **kwargs)
                            
                            # Check if the result indicates an authentication error
                            if isinstance(result, dict):
                                error_type = result.get("error")
                                if error_type in ["unauthorized", "forbidden"]:
                                    # Add context about token issues
                                    if "details" not in result:
                                        result["details"] = "The access token may be invalid, expired, or lack required permissions"
                                    result["provider"] = provider
                            
                            return result
                            
                        except Exception as api_error:
                            unified_logger.error(f"OAuth Backend: API call failed for {provider}: {str(api_error)}")
                            return {
                                "error": "api_error",
                                "message": f"Failed to exchange token with {provider} backend",
                                "provider": provider,
                                "details": str(api_error)
                            }
                    
                    # Missing required parameters
                    missing = []
                    if not user_id:
                        missing.append("userId")
                    if not user_token:
                        missing.append("userToken")
                    if not provider_id:
                        missing.append("providerId")
                    
                    unified_logger.info(f"OAuth Backend: Missing required parameters for {provider}: {', '.join(missing)}")
                    return {
                        "error": "missing_parameters",
                        "message": f"Missing required OAuth parameters for {provider}",
                        "provider": provider,
                        "details": f"Required: userId, userToken, providerId. Missing: {', '.join(missing)}"
                    }
                    
                else:
                    unified_logger.debug(f"OAuth Backend: Context structure not suitable for OAuth backend extraction")
                    return {
                        "error": "invalid_context",
                        "message": f"Invalid context structure for {provider} OAuth",
                        "provider": provider,
                        "details": "Context must contain request_context.meta with OAuth parameters"
                    }
                    
            except Exception as e:
                # Catch any unexpected errors to prevent crashes
                unified_logger.error(f"OAuth Backend: Unexpected error for {provider}: {str(e)}")
                return {
                    "error": "oauth_processing_error",
                    "message": f"Error processing OAuth backend for {provider}",
                    "provider": provider,
                    "details": str(e)
                }
        
        return wrapper
    
    return decorator
{%- endif %}