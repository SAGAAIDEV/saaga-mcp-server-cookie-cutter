"""Reddit OAuth Backend Tools - Example implementation using backend token exchange.

These tools demonstrate the OAuth backend pattern where:
1. Client provides userId, userToken, and providerId
2. The oauth_backend decorator exchanges userToken for an access token
3. Tools use the access token to call Reddit API

This is an example implementation - replace with your actual OAuth provider tools.
"""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context
import json
from final_mcp.log_system.unified_logger import UnifiedLogger

try:
    import httpx
except ImportError:
    httpx = None

unified_logger = UnifiedLogger.get_logger("reddit_backend_tools")


async def get_reddit_user(ctx: Context = None) -> Dict[str, Any]:
    """Get authenticated Reddit user information.
    
    This tool requires Reddit OAuth authentication via backend token exchange.
    The oauth_backend decorator handles exchanging the temp token for an access token.
    
    Args:
        ctx: MCP Context containing the OAuth token after exchange
    
    Returns:
        Reddit user information or error details
    """
    # Token is available after oauth_backend decorator processes it
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            unified_logger.info(f"Reddit Tool (get_reddit_user): Successfully extracted access token from context")
            unified_logger.info(f"  Token Length: {len(token)} characters")
            unified_logger.info(f"  Token Preview: {token[:10]}... (rest hidden for security)")
            
            # Make REAL Reddit API call
            unified_logger.info("Reddit Tool: Making API call to Reddit")
            unified_logger.info("  URL: https://oauth.reddit.com/api/v1/me")
            unified_logger.info(f"  Authorization: Bearer {token[:10]}... [REST OF TOKEN HIDDEN]")
            
            if not httpx:
                unified_logger.error("httpx not installed - required for Reddit API calls")
                return {
                    "error": "configuration_error",
                    "message": "httpx library not installed",
                    "details": "Install with: pip install httpx"
                }
            
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "MCP-OAuth-Backend/1.0"
                    }
                    
                    response = await client.get(
                        "https://oauth.reddit.com/api/v1/me",
                        headers=headers,
                        timeout=10.0
                    )
                    
                    unified_logger.info(f"Reddit Tool: Received response from Reddit API")
                    unified_logger.info(f"  Status Code: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        unified_logger.info(f"Reddit Tool: Successfully retrieved user data")
                        unified_logger.info(f"  Username: {data.get('name', 'unknown')}")
                        return data
                    
                    elif response.status_code == 401:
                        unified_logger.warning("Reddit Tool: 401 Unauthorized - Invalid or expired token")
                        return {
                            "error": "unauthorized",
                            "message": "Invalid or expired Reddit access token",
                            "status_code": 401,
                            "details": "The token may be expired or invalid. Client should refresh."
                        }
                    
                    elif response.status_code == 403:
                        unified_logger.warning("Reddit Tool: 403 Forbidden - Insufficient permissions")
                        return {
                            "error": "forbidden",
                            "message": "Insufficient permissions for Reddit API",
                            "status_code": 403,
                            "details": "The token lacks required scopes for this operation"
                        }
                    
                    else:
                        unified_logger.error(f"Reddit Tool: Unexpected status code {response.status_code}")
                        return {
                            "error": "api_error",
                            "message": f"Reddit API returned status {response.status_code}",
                            "status_code": response.status_code,
                            "details": response.text[:200]
                        }
                        
            except httpx.TimeoutException:
                unified_logger.error("Reddit Tool: Request to Reddit API timed out")
                return {
                    "error": "timeout",
                    "message": "Reddit API request timed out",
                    "details": "The Reddit API did not respond within 10 seconds"
                }
            
            except httpx.RequestError as e:
                unified_logger.error(f"Reddit Tool: Request error - {str(e)}")
                return {
                    "error": "connection_error",
                    "message": "Failed to connect to Reddit API",
                    "details": str(e)
                }
            
            except Exception as e:
                unified_logger.error(f"Reddit Tool: Unexpected error - {str(e)}")
                return {
                    "error": "unexpected_error",
                    "message": "Unexpected error calling Reddit API",
                    "details": str(e)
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available",
        "details": "oauth_backend decorator should have provided token"
    }


async def list_user_subreddits(limit: int = 10, ctx: Context = None) -> Dict[str, Any]:
    """List subreddits the authenticated user is subscribed to.
    
    Args:
        limit: Maximum number of subreddits to return
        ctx: MCP Context containing the OAuth token
    
    Returns:
        List of subscribed subreddits or error details
    """
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            unified_logger.info(f"Reddit Tool (list_user_subreddits): Successfully extracted access token")
            unified_logger.info(f"  Token Length: {len(token)} characters")
            unified_logger.info(f"  Token Preview: {token[:10]}...")
            unified_logger.info("  Making API call to: https://oauth.reddit.com/subreddits/mine")
            
            if not httpx:
                return {
                    "error": "configuration_error",
                    "message": "httpx library not installed"
                }
            
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "MCP-OAuth-Backend/1.0"
                    }
                    
                    response = await client.get(
                        f"https://oauth.reddit.com/subreddits/mine?limit={limit}",
                        headers=headers,
                        timeout=10.0
                    )
                    
                    unified_logger.info(f"Reddit Tool: Response status {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        subreddits = []
                        for item in data.get('data', {}).get('children', []):
                            sub_data = item.get('data', {})
                            subreddits.append({
                                "name": sub_data.get('display_name'),
                                "url": sub_data.get('url'),
                                "subscribers": sub_data.get('subscribers'),
                                "description": sub_data.get('public_description', '')[:200]
                            })
                        
                        unified_logger.info(f"Reddit Tool: Retrieved {len(subreddits)} subreddits")
                        return {
                            "subreddits": subreddits,
                            "count": len(subreddits)
                        }
                    
                    elif response.status_code == 401:
                        return {
                            "error": "unauthorized",
                            "message": "Invalid or expired Reddit access token",
                            "status_code": 401
                        }
                    
                    else:
                        return {
                            "error": "api_error",
                            "message": f"Reddit API returned status {response.status_code}",
                            "status_code": response.status_code
                        }
                        
            except Exception as e:
                unified_logger.error(f"Reddit Tool: Error - {str(e)}")
                return {
                    "error": "request_failed",
                    "message": str(e)
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available"
    }


async def get_subreddit_posts(subreddit: str, sort: str = "hot", limit: int = 10, ctx: Context = None) -> Dict[str, Any]:
    """Get posts from a specific subreddit.
    
    Args:
        subreddit: Name of the subreddit (without r/ prefix)
        sort: Sort order (hot, new, top, rising)
        limit: Maximum number of posts to return
        ctx: MCP Context containing the OAuth token
    
    Returns:
        List of posts or error details
    """
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            unified_logger.info(f"Reddit Tool (get_subreddit_posts): Successfully extracted access token")
            unified_logger.info(f"  Subreddit: r/{subreddit}")
            unified_logger.info(f"  Token Length: {len(token)} characters")
            unified_logger.info(f"  Token Preview: {token[:10]}...")
            unified_logger.info(f"  Making API call to: https://oauth.reddit.com/r/{subreddit}/{sort}")
            
            if not httpx:
                return {
                    "error": "configuration_error",
                    "message": "httpx library not installed"
                }
            
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "MCP-OAuth-Backend/1.0"
                    }
                    
                    response = await client.get(
                        f"https://oauth.reddit.com/r/{subreddit}/{sort}?limit={limit}",
                        headers=headers,
                        timeout=10.0
                    )
                    
                    unified_logger.info(f"Reddit Tool: Response status {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = []
                        for item in data.get('data', {}).get('children', []):
                            post_data = item.get('data', {})
                            posts.append({
                                "title": post_data.get('title'),
                                "author": post_data.get('author'),
                                "score": post_data.get('score'),
                                "num_comments": post_data.get('num_comments'),
                                "url": post_data.get('url'),
                                "created_utc": post_data.get('created_utc')
                            })
                        
                        unified_logger.info(f"Reddit Tool: Retrieved {len(posts)} posts from r/{subreddit}")
                        return {
                            "subreddit": subreddit,
                            "sort": sort,
                            "posts": posts,
                            "count": len(posts)
                        }
                    
                    elif response.status_code == 401:
                        return {
                            "error": "unauthorized",
                            "message": "Invalid or expired Reddit access token",
                            "status_code": 401
                        }
                    
                    elif response.status_code == 404:
                        return {
                            "error": "not_found",
                            "message": f"Subreddit r/{subreddit} not found",
                            "status_code": 404
                        }
                    
                    else:
                        return {
                            "error": "api_error",
                            "message": f"Reddit API returned status {response.status_code}",
                            "status_code": response.status_code
                        }
                        
            except Exception as e:
                unified_logger.error(f"Reddit Tool: Error - {str(e)}")
                return {
                    "error": "request_failed",
                    "message": str(e)
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available"
    }


async def create_reddit_post(
    subreddit: str,
    title: str,
    text: str = None,
    url: str = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Create a new post in a subreddit.
    
    Args:
        subreddit: Name of the subreddit to post in
        title: Title of the post
        text: Text content for text posts (optional)
        url: URL for link posts (optional)
        ctx: MCP Context containing the OAuth token
    
    Returns:
        Post creation result or error details
    """
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            unified_logger.info(f"Reddit Tool (create_reddit_post): Successfully extracted access token")
            unified_logger.info(f"  Subreddit: r/{subreddit}")
            unified_logger.info(f"  Token Length: {len(token)} characters")
            unified_logger.info(f"  Token Preview: {token[:10]}...")
            unified_logger.info(f"  Making API call to: https://oauth.reddit.com/api/submit")
            
            if not httpx:
                return {
                    "error": "configuration_error",
                    "message": "httpx library not installed"
                }
            
            # Validate input
            if not text and not url:
                return {
                    "error": "invalid_input",
                    "message": "Either text or url must be provided"
                }
            
            try:
                async with httpx.AsyncClient() as client:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "MCP-OAuth-Backend/1.0"
                    }
                    
                    # Prepare post data
                    post_data = {
                        "sr": subreddit,
                        "title": title,
                        "api_type": "json"
                    }
                    
                    if text:
                        post_data["kind"] = "self"
                        post_data["text"] = text
                    else:
                        post_data["kind"] = "link"
                        post_data["url"] = url
                    
                    response = await client.post(
                        "https://oauth.reddit.com/api/submit",
                        headers=headers,
                        data=post_data,
                        timeout=10.0
                    )
                    
                    unified_logger.info(f"Reddit Tool: Response status {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('json', {}).get('errors'):
                            errors = data['json']['errors']
                            unified_logger.warning(f"Reddit Tool: Post creation failed with errors: {errors}")
                            return {
                                "error": "submission_failed",
                                "message": "Reddit rejected the submission",
                                "details": errors
                            }
                        
                        post_data = data.get('json', {}).get('data', {})
                        unified_logger.info(f"Reddit Tool: Successfully created post")
                        return {
                            "success": True,
                            "post_id": post_data.get('id'),
                            "url": post_data.get('url'),
                            "name": post_data.get('name')
                        }
                    
                    elif response.status_code == 401:
                        return {
                            "error": "unauthorized",
                            "message": "Invalid or expired Reddit access token",
                            "status_code": 401
                        }
                    
                    elif response.status_code == 403:
                        return {
                            "error": "forbidden",
                            "message": "Not allowed to post in this subreddit",
                            "status_code": 403
                        }
                    
                    else:
                        return {
                            "error": "api_error",
                            "message": f"Reddit API returned status {response.status_code}",
                            "status_code": response.status_code
                        }
                        
            except Exception as e:
                unified_logger.error(f"Reddit Tool: Error - {str(e)}")
                return {
                    "error": "request_failed",
                    "message": str(e)
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available"
    }


# Export tools for app.py registration
# Each tuple contains (provider, function) for the oauth_backend decorator
oauth_backend_tools = [
    ("reddit", get_reddit_user),
    ("reddit", list_user_subreddits),
    ("reddit", get_subreddit_posts),
    ("reddit", create_reddit_post),
]