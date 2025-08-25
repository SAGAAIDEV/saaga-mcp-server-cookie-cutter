{% if cookiecutter.include_oauth_backend == "yes" -%}
"""Reddit OAuth Backend Tools - Example implementation using backend token exchange.

These tools demonstrate the OAuth backend pattern where:
1. Client provides userId, tempToken, and providerId
2. The oauth_backend decorator exchanges tempToken for an access token
3. Tools use the access token to call Reddit API

This is an example implementation - replace with your actual OAuth provider tools.
"""

from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context
import logging
import json

# Mock Reddit API responses for demonstration
# In production, you would use httpx or requests to call actual Reddit API

logger = logging.getLogger(__name__)


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
            # In production, make actual Reddit API call with token
            # headers = {"Authorization": f"Bearer {token}"}
            # response = await httpx.get("https://oauth.reddit.com/api/v1/me", headers=headers)
            
            # Mock response for demonstration
            logger.info(f"Fetching Reddit user with token: {token[:10]}...")
            
            # Simulate different responses based on token
            if "mock_reddit" in token:
                return {
                    "id": "t2_demo123",
                    "name": "demo_user",
                    "link_karma": 1234,
                    "comment_karma": 5678,
                    "created_utc": 1609459200,
                    "is_gold": False,
                    "is_mod": True,
                    "verified": True,
                    "has_verified_email": True
                }
            else:
                # Simulate API error for non-mock tokens in demo
                return {
                    "error": "api_error",
                    "message": "Reddit API call failed",
                    "details": "This is a demo - use mock mode for testing"
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available",
        "details": "oauth_backend decorator should have provided token"
    }


async def list_user_subreddits(limit: int = 10, ctx: Context = None) -> Dict[str, Any]:
    """List subreddits the authenticated user is subscribed to.
    
    This tool requires Reddit OAuth authentication via backend token exchange.
    
    Args:
        limit: Maximum number of subreddits to return (default: 10)
        ctx: MCP Context containing the OAuth token after exchange
    
    Returns:
        List of subscribed subreddits or error details
    """
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            logger.info(f"Fetching user subreddits with token: {token[:10]}...")
            
            # Mock response for demonstration
            if "mock_reddit" in token:
                return {
                    "subreddits": [
                        {
                            "name": "programming",
                            "display_name": "r/programming",
                            "subscribers": 4500000,
                            "user_is_subscriber": True
                        },
                        {
                            "name": "python",
                            "display_name": "r/python",
                            "subscribers": 1200000,
                            "user_is_subscriber": True
                        },
                        {
                            "name": "machinelearning",
                            "display_name": "r/MachineLearning",
                            "subscribers": 2800000,
                            "user_is_subscriber": True
                        }
                    ][:limit],
                    "total": 3
                }
            else:
                return {
                    "error": "api_error",
                    "message": "Reddit API call failed",
                    "details": "This is a demo - use mock mode for testing"
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available",
        "details": "oauth_backend decorator should have provided token"
    }


async def get_subreddit_posts(
    subreddit: str,
    sort: str = "hot",
    limit: int = 10,
    ctx: Context = None
) -> Dict[str, Any]:
    """Get posts from a specific subreddit.
    
    This tool requires Reddit OAuth authentication via backend token exchange.
    
    Args:
        subreddit: Name of the subreddit (without r/ prefix)
        sort: Sort order - "hot", "new", "top", "rising" (default: "hot")
        limit: Maximum number of posts to return (default: 10)
        ctx: MCP Context containing the OAuth token after exchange
    
    Returns:
        List of subreddit posts or error details
    """
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            logger.info(f"Fetching r/{subreddit} posts with token: {token[:10]}...")
            
            # Validate sort parameter
            valid_sorts = ["hot", "new", "top", "rising"]
            if sort not in valid_sorts:
                return {
                    "error": "invalid_parameter",
                    "message": f"Invalid sort parameter: {sort}",
                    "details": f"Must be one of: {', '.join(valid_sorts)}"
                }
            
            # Mock response for demonstration
            if "mock_reddit" in token:
                return {
                    "subreddit": f"r/{subreddit}",
                    "sort": sort,
                    "posts": [
                        {
                            "id": "abc123",
                            "title": f"Example post in r/{subreddit}",
                            "author": "demo_author",
                            "score": 1234,
                            "num_comments": 56,
                            "created_utc": 1609459200,
                            "url": f"https://reddit.com/r/{subreddit}/comments/abc123"
                        },
                        {
                            "id": "def456",
                            "title": f"Another post in r/{subreddit}",
                            "author": "another_user",
                            "score": 789,
                            "num_comments": 23,
                            "created_utc": 1609455600,
                            "url": f"https://reddit.com/r/{subreddit}/comments/def456"
                        }
                    ][:limit],
                    "total": 2
                }
            else:
                return {
                    "error": "api_error",
                    "message": "Reddit API call failed",
                    "details": "This is a demo - use mock mode for testing"
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available",
        "details": "oauth_backend decorator should have provided token"
    }


async def create_reddit_post(
    subreddit: str,
    title: str,
    text: Optional[str] = None,
    url: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Create a new post in a subreddit.
    
    This tool requires Reddit OAuth authentication via backend token exchange.
    Either text or url must be provided (not both).
    
    Args:
        subreddit: Name of the subreddit to post in
        title: Title of the post
        text: Text content for a text post (optional)
        url: URL for a link post (optional)
        ctx: MCP Context containing the OAuth token after exchange
    
    Returns:
        Created post details or error details
    """
    # Validate input
    if not text and not url:
        return {
            "error": "invalid_parameter",
            "message": "Either text or url must be provided",
            "details": "Provide text for a text post or url for a link post"
        }
    
    if text and url:
        return {
            "error": "invalid_parameter",
            "message": "Cannot provide both text and url",
            "details": "Choose either text post or link post, not both"
        }
    
    if ctx and hasattr(ctx, 'request_context') and hasattr(ctx.request_context, 'meta'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token') if hasattr(meta, 'get') else getattr(meta, 'current_oauth_token', None)
        
        if token:
            logger.info(f"Creating post in r/{subreddit} with token: {token[:10]}...")
            
            # Mock response for demonstration
            if "mock_reddit" in token:
                post_type = "text" if text else "link"
                return {
                    "success": True,
                    "post": {
                        "id": "newpost123",
                        "subreddit": f"r/{subreddit}",
                        "title": title,
                        "type": post_type,
                        "author": "demo_user",
                        "url": f"https://reddit.com/r/{subreddit}/comments/newpost123",
                        "created_utc": 1609459200
                    },
                    "message": f"Successfully created {post_type} post in r/{subreddit}"
                }
            else:
                return {
                    "error": "api_error",
                    "message": "Reddit API call failed",
                    "details": "This is a demo - use mock mode for testing"
                }
    
    return {
        "error": "no_token",
        "message": "No Reddit access token available",
        "details": "oauth_backend decorator should have provided token"
    }


# Export tools for app.py registration
# Each tuple contains (provider, function) for the oauth_backend decorator
oauth_backend_tools = [
    ("reddit", get_reddit_user),
    ("reddit", list_user_subreddits),
    ("reddit", get_subreddit_posts),
    ("reddit", create_reddit_post),
]
{% endif -%}