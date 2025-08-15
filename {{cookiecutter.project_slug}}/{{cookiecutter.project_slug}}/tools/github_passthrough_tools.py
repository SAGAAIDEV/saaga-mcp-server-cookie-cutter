{% if cookiecutter.include_oauth_passthrough == "yes" -%}
"""GitHub tools that expect OAuth tokens from Context.

These tools demonstrate the token passthrough pattern where:
1. The client handles all OAuth logic
2. The client passes tokens via Context
3. These tools just USE the tokens to call GitHub API

NO OAuth flow handling, NO token storage, NO auth URLs.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import Context

# Set up logging for internal feedback
logger = logging.getLogger('{{ cookiecutter.project_slug }}.github_tools')

async def get_github_user(ctx: Context = None) -> Dict[str, Any]:
    """Get authenticated GitHub user information.
    
    Retrieves information about the authenticated user using the
    OAuth token passed via Context.
    
    Args:
        ctx: MCP Context containing OAuth token
        
    Returns:
        Dict containing user information or error
    """
    logger.info("Attempting to get GitHub user information")
    
    if not ctx or not hasattr(ctx, 'request_context') or not hasattr(ctx.request_context, 'meta'):
        logger.error("Context not available or improperly structured")
        return {
            "error": "no_context",
            "message": "Context not available for OAuth token extraction"
        }
    
    # Token should be added by oauth_passthrough decorator
    meta = ctx.request_context.meta
    token = None
    
    # Try different ways to get the token from meta
    if hasattr(meta, 'get'):
        token = meta.get('current_oauth_token')
    elif hasattr(meta, 'current_oauth_token'):
        token = getattr(meta, 'current_oauth_token', None)
    
    if not token:
        # This shouldn't happen if oauth_passthrough decorator is working
        logger.error("OAuth token not found in context meta")
        return {
            "error": "no_token",
            "message": "OAuth token not found in context"
        }
    
    logger.info(f"Using OAuth token (first 10 chars): {token[:10]}...")
    
    # Use the token to call GitHub API
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            logger.info("Making request to GitHub API")
            response = await client.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=10.0
            )
            
            logger.info(f"GitHub API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully retrieved user: {data.get('login', 'unknown')}")
                return data
            elif response.status_code == 401:
                logger.error("GitHub API returned 401 Unauthorized")
                return {
                    "error": "unauthorized",
                    "message": "Invalid or expired OAuth token",
                    "status_code": 401
                }
            else:
                logger.error(f"GitHub API returned unexpected status: {response.status_code}")
                return {
                    "error": "api_error",
                    "message": f"GitHub API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
    except httpx.TimeoutException:
        logger.error("Request to GitHub API timed out")
        return {
            "error": "timeout",
            "message": "Request to GitHub API timed out"
        }
    except Exception as e:
        logger.error(f"Unexpected error calling GitHub API: {e}")
        return {
            "error": "request_failed",
            "message": f"Failed to call GitHub API: {str(e)}"
        }


async def list_user_repos(
    per_page: int = 30,
    page: int = 1,
    sort: str = "updated",
    ctx: Context = None
) -> Dict[str, Any]:
    """List repositories for the authenticated user.
    
    Args:
        per_page: Number of results per page (max 100)
        page: Page number for pagination
        sort: How to sort repositories (created, updated, pushed, full_name)
        ctx: MCP Context containing OAuth token
        
    Returns:
        Dict containing list of repositories or error
    """
    logger.info(f"Attempting to list user repos (page={page}, per_page={per_page}, sort={sort})")
    
    if not ctx or not hasattr(ctx, 'request_context') or not hasattr(ctx.request_context, 'meta'):
        logger.error("Context not available or improperly structured")
        return {
            "error": "no_context",
            "message": "Context not available for OAuth token extraction"
        }
    
    # Get token from meta
    meta = ctx.request_context.meta
    token = None
    
    if hasattr(meta, 'get'):
        token = meta.get('current_oauth_token')
    elif hasattr(meta, 'current_oauth_token'):
        token = getattr(meta, 'current_oauth_token', None)
    
    if not token:
        logger.error("OAuth token not found in context meta")
        return {
            "error": "no_token",
            "message": "OAuth token not found in context"
        }
    
    logger.info(f"Using OAuth token to list repositories")
    
    # Validate parameters
    per_page = min(max(1, per_page), 100)  # GitHub max is 100
    page = max(1, page)
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            params = {
                "per_page": per_page,
                "page": page,
                "sort": sort
            }
            
            logger.info(f"Making request to GitHub API with params: {params}")
            response = await client.get(
                "https://api.github.com/user/repos",
                headers=headers,
                params=params,
                timeout=10.0
            )
            
            logger.info(f"GitHub API response status: {response.status_code}")
            
            if response.status_code == 200:
                repos = response.json()
                logger.info(f"Successfully retrieved {len(repos)} repositories")
                
                # Extract key information from each repo
                simplified_repos = []
                for repo in repos:
                    simplified_repos.append({
                        "name": repo.get("name"),
                        "full_name": repo.get("full_name"),
                        "description": repo.get("description"),
                        "private": repo.get("private"),
                        "html_url": repo.get("html_url"),
                        "language": repo.get("language"),
                        "stargazers_count": repo.get("stargazers_count"),
                        "updated_at": repo.get("updated_at")
                    })
                
                return {
                    "repositories": simplified_repos,
                    "count": len(simplified_repos),
                    "page": page,
                    "per_page": per_page
                }
            elif response.status_code == 401:
                logger.error("GitHub API returned 401 Unauthorized")
                return {
                    "error": "unauthorized",
                    "message": "Invalid or expired OAuth token",
                    "status_code": 401
                }
            else:
                logger.error(f"GitHub API returned unexpected status: {response.status_code}")
                return {
                    "error": "api_error",
                    "message": f"GitHub API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
    except httpx.TimeoutException:
        logger.error("Request to GitHub API timed out")
        return {
            "error": "timeout",
            "message": "Request to GitHub API timed out"
        }
    except Exception as e:
        logger.error(f"Unexpected error calling GitHub API: {e}")
        return {
            "error": "request_failed",
            "message": f"Failed to call GitHub API: {str(e)}"
        }


async def create_github_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """Create an issue in a GitHub repository.
    
    Args:
        owner: Repository owner (username or org)
        repo: Repository name
        title: Issue title
        body: Issue body/description
        labels: List of label names to apply
        assignees: List of usernames to assign
        ctx: MCP Context containing OAuth token
        
    Returns:
        Dict containing created issue information or error
    """
    logger.info(f"Attempting to create issue in {owner}/{repo}: {title}")
    
    if not ctx or not hasattr(ctx, 'request_context') or not hasattr(ctx.request_context, 'meta'):
        logger.error("Context not available or improperly structured")
        return {
            "error": "no_context",
            "message": "Context not available for OAuth token extraction"
        }
    
    # Get token from meta
    meta = ctx.request_context.meta
    token = None
    
    if hasattr(meta, 'get'):
        token = meta.get('current_oauth_token')
    elif hasattr(meta, 'current_oauth_token'):
        token = getattr(meta, 'current_oauth_token', None)
    
    if not token:
        logger.error("OAuth token not found in context meta")
        return {
            "error": "no_token",
            "message": "OAuth token not found in context"
        }
    
    logger.info(f"Using OAuth token to create issue")
    
    # Build request payload
    payload = {"title": title}
    if body:
        payload["body"] = body
    if labels:
        payload["labels"] = labels
    if assignees:
        payload["assignees"] = assignees
    
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            logger.info(f"Making POST request to create issue with payload: {payload}")
            response = await client.post(
                f"https://api.github.com/repos/{owner}/{repo}/issues",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            logger.info(f"GitHub API response status: {response.status_code}")
            
            if response.status_code == 201:
                issue = response.json()
                logger.info(f"Successfully created issue #{issue.get('number')}")
                return {
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "html_url": issue.get("html_url"),
                    "state": issue.get("state"),
                    "created_at": issue.get("created_at"),
                    "body": issue.get("body"),
                    "labels": [l.get("name") for l in issue.get("labels", [])],
                    "assignees": [a.get("login") for a in issue.get("assignees", [])]
                }
            elif response.status_code == 401:
                logger.error("GitHub API returned 401 Unauthorized")
                return {
                    "error": "unauthorized",
                    "message": "Invalid or expired OAuth token",
                    "status_code": 401
                }
            elif response.status_code == 403:
                logger.error("GitHub API returned 403 Forbidden")
                return {
                    "error": "forbidden",
                    "message": "Token lacks permission to create issues in this repository",
                    "status_code": 403
                }
            elif response.status_code == 404:
                logger.error("GitHub API returned 404 Not Found")
                return {
                    "error": "not_found",
                    "message": f"Repository {owner}/{repo} not found",
                    "status_code": 404
                }
            else:
                logger.error(f"GitHub API returned unexpected status: {response.status_code}")
                return {
                    "error": "api_error",
                    "message": f"GitHub API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
    except httpx.TimeoutException:
        logger.error("Request to GitHub API timed out")
        return {
            "error": "timeout",
            "message": "Request to GitHub API timed out"
        }
    except Exception as e:
        logger.error(f"Unexpected error calling GitHub API: {e}")
        return {
            "error": "request_failed",
            "message": f"Failed to call GitHub API: {str(e)}"
        }


# Export tools with their OAuth configuration
# This allows app.py to remain tool-agnostic while still providing
# the necessary provider information for the oauth_passthrough decorator

oauth_passthrough_tools = [
    # Each tuple is (provider, tool_function)
    ("github", get_github_user),
    ("github", list_user_repos),
    ("github", create_github_issue),
]

# If we add other providers, they go in the same list:
# oauth_passthrough_tools.extend([
#     ("google", get_google_calendar),
#     ("google", create_google_event),
#     ("microsoft", get_outlook_mail),
# ])
{% endif -%}