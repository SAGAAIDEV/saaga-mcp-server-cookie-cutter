"""OAuth Token Passthrough Decorator - NO OAuth flow handling.

This decorator checks for OAuth tokens passed by the client via Context.
It does NOT handle OAuth flows, store tokens, or return auth URLs.
The client/platform is responsible for ALL OAuth logic.
"""

from functools import wraps
from typing import Callable, Any, Awaitable
import logging

def oauth_passthrough(provider: str):
    """Check Context for OAuth tokens - NO OAuth flow handling.
    
    This decorator:
    1. Checks if OAuth tokens are provided in Context
    2. Adds the token to meta for the tool to use
    3. Returns a graceful error if no token provided
    4. Handles token validation errors from the wrapped function
    
    It does NOT:
    - Handle OAuth flows
    - Return auth URLs
    - Store tokens
    - Manage refresh tokens
    
    Args:
        provider: The OAuth provider name (e.g., 'github', 'google')
    
    Returns:
        Decorator function that checks for tokens
    """
    def decorator(func: Callable[..., Awaitable[Any]], config: dict = None) -> Callable[..., Awaitable[Any]]:
        """Apply token passthrough checking to a function.
        
        Args:
            func: The async function to decorate
            config: Optional configuration (unused in passthrough mode)
        
        Returns:
            Wrapped function that checks for tokens
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = logging.getLogger(f'example_server.oauth.{provider}')
            
            try:
                # Get Context from kwargs (following SAAGA pattern)
                ctx = kwargs.get("ctx")
                
                if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
                    meta = ctx.request_context.meta
                    
                    # Check for OAuth tokens in Context
                    oauth_tokens = None
                    if hasattr(meta, 'get'):
                        oauth_tokens = meta.get('oauth_tokens', {})
                    elif hasattr(meta, 'oauth_tokens'):
                        oauth_tokens = getattr(meta, 'oauth_tokens', {})
                    
                    if oauth_tokens and provider in oauth_tokens:
                        token = oauth_tokens[provider]
                        
                        # Basic token validation (non-empty)
                        if not token or not isinstance(token, str) or not token.strip():
                            logger.warning(f"Invalid {provider} token format provided")
                            return {
                                "error": "invalid_token_format",
                                "message": f"Invalid {provider} token format",
                                "provider": provider,
                                "details": "Token must be a non-empty string"
                            }
                        
                        # Add token to meta for tool to use
                        if hasattr(meta, '__setitem__'):
                            meta['current_oauth_token'] = token
                            meta['oauth_provider'] = provider
                        else:
                            setattr(meta, 'current_oauth_token', token)
                            setattr(meta, 'oauth_provider', provider)
                        
                        # Call the wrapped function with token available
                        result = await func(*args, **kwargs)
                        
                        # Check if the result indicates an authentication error
                        # and add helpful context if needed
                        if isinstance(result, dict):
                            error_type = result.get("error")
                            if error_type in ["unauthorized", "forbidden"]:
                                # Add context about token issues
                                if "details" not in result:
                                    result["details"] = "The provided token may be invalid, expired, or lack required permissions"
                                result["provider"] = provider
                        
                        return result
                    
                    # No token for this provider
                    logger.info(f"No {provider} token provided in context")
                    
                else:
                    logger.debug(f"Context structure not suitable for OAuth extraction")
                
                # No token provided - return graceful error
                # NO auth URLs, NO OAuth flow instructions
                return {
                    "error": "token_not_provided",
                    "message": f"No {provider} token provided by client",
                    "provider": provider,
                    "details": "The client must provide OAuth tokens via Context in the oauth_tokens dictionary"
                }
                
            except Exception as e:
                # Catch any unexpected errors to prevent crashes
                logger.error(f"Unexpected error in oauth_passthrough for {provider}: {str(e)}")
                return {
                    "error": "oauth_processing_error",
                    "message": f"Error processing OAuth token for {provider}",
                    "provider": provider,
                    "details": str(e)
                }
        
        return wrapper
    
    return decorator
