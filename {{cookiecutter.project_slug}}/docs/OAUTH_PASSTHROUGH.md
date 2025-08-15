{% if cookiecutter.include_oauth_passthrough == "yes" -%}
# OAuth Token Passthrough Documentation

## Quick Start - Testing the GitHub OAuth Tools

### 1. Get a GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) and `user`
4. Copy the token (starts with `gho_`)

### 2. Test with the Provided Script
```bash
# Test with a real private repository
python test_oauth_private_repo.py gho_YOUR_TOKEN owner/repo

# Test error handling
python test_oauth_error_handling.py
```

### 3. Use with MCP Inspector (Limited OAuth Support)
MCP Inspector doesn't support passing OAuth tokens via metadata. You'll need a custom MCP client or use the test scripts.

### 4. Use with Claude Desktop or Custom Clients
Claude Desktop and other MCP clients need to be configured to pass OAuth tokens. The client is responsible for:
1. Getting the OAuth token (through their own OAuth flow)
2. Passing it in the `_meta` parameter when calling tools

## Overview

This MCP server includes OAuth token passthrough support, allowing clients to pass OAuth tokens via the MCP Context for authenticating with external services. The server itself does NOT handle OAuth flows - all OAuth logic (getting tokens, refreshing, etc.) is handled by the client.

## Architecture

### How It Works

1. **Client handles OAuth**: The MCP client (e.g., Solve, React app) handles ALL OAuth logic
2. **Token passthrough**: Client passes tokens to MCP server via Context `_meta` parameter
3. **Server uses tokens**: MCP tools extract tokens from Context and use them to call APIs
4. **No server-side OAuth**: The MCP server NEVER stores tokens, handles callbacks, or manages OAuth flows

### Key Points

- **Zero configuration**: No OAuth app registration needed in the MCP server
- **No credentials**: No client_id, client_secret, or redirect URLs in server config
- **Stateless**: Tokens are passed per-request, never stored
- **Multi-tenant ready**: Different clients can pass different tokens

## Implementation

### OAuth Passthrough Decorator

The `oauth_passthrough` decorator checks for tokens in Context:

```python
from {{ cookiecutter.project_slug }}.decorators.oauth_passthrough import oauth_passthrough

@oauth_passthrough("github")
async def get_github_user(ctx: Context = None) -> dict:
    # Token is available in ctx.request_context.meta['current_oauth_token']
    # Use it to call GitHub API
```

### Client Usage

Clients pass tokens via the `_meta` parameter in MCP requests:

```python
# MCP client code
request = types.ClientRequest(
    types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="get_github_user",
            arguments={},
            _meta={
                "oauth_tokens": {
                    "github": "gho_abc123...",
                    "google": "ya29.a0...",
                    "microsoft": "eyJ0eX..."
                },
                "correlationId": "req_123"
            }
        )
    )
)
```

### Tool Implementation

Tools extract and use tokens like this:

```python
async def get_github_user(ctx: Context = None) -> Dict[str, Any]:
    """Get GitHub user using token from Context."""
    
    # Token is added by oauth_passthrough decorator
    meta = ctx.request_context.meta
    token = meta.get('current_oauth_token')
    
    # Use token to call GitHub API
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(
            "https://api.github.com/user",
            headers=headers
        )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        return {
            "error": "unauthorized",
            "message": "Invalid or expired token",
            "status_code": 401
        }
```

## Error Handling

All OAuth errors are handled gracefully without crashes:

### Error Types

1. **No Token Provided**
   ```json
   {
       "error": "token_not_provided",
       "message": "No github token provided by client",
       "provider": "github"
   }
   ```

2. **Invalid Token Format**
   ```json
   {
       "error": "invalid_token_format",
       "message": "Invalid github token format",
       "provider": "github"
   }
   ```

3. **Unauthorized (401)**
   ```json
   {
       "error": "unauthorized",
       "message": "Invalid or expired OAuth token",
       "status_code": 401,
       "provider": "github"
   }
   ```

4. **Forbidden (403)**
   ```json
   {
       "error": "forbidden",
       "message": "Token lacks required permissions",
       "status_code": 403,
       "provider": "github"
   }
   ```

## Testing

### Manual Testing with Private Repos

Test OAuth with a real GitHub token:

```bash
# Get a GitHub token from: https://github.com/settings/tokens
# Required scopes: 'repo' (for private repos) and 'user'

python test_oauth_private_repo.py gho_YOUR_TOKEN owner/repo
```

### Error Handling Tests

Test that invalid tokens are handled gracefully:

```bash
python test_oauth_error_handling.py
```

### Integration Tests

Run automated OAuth tests:

```bash
pytest tests/integration/test_oauth_passthrough_integration.py -v
```

To test with a real token:

```bash
export GITHUB_TOKEN=gho_YOUR_TOKEN
pytest tests/integration/test_oauth_passthrough_integration.py::test_github_tool_with_real_token -v
```

## Adding OAuth to Your Tools

### Step 1: Create Your Tool

```python
from typing import Dict, Any
from mcp.server.fastmcp import Context
import httpx

async def call_api_with_oauth(
    endpoint: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """Call an API using OAuth token from Context."""
    
    # Token is provided by oauth_passthrough decorator
    meta = ctx.request_context.meta
    token = meta.get('current_oauth_token')
    provider = meta.get('oauth_provider')
    
    if not token:
        return {
            "error": "no_token",
            "message": "OAuth token not found in context"
        }
    
    # Use the token
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": "api_error",
                "status_code": response.status_code,
                "message": response.text
            }
```

### Step 2: Register with OAuth Decorator

In your tools module:

```python
# Export tools with their OAuth configuration
oauth_passthrough_tools = [
    ("github", call_api_with_oauth),
    ("google", another_oauth_tool),
]
```

In `server/app.py`, these are automatically registered with the decorator chain.

## Security Considerations

1. **Never log tokens**: The implementation never logs actual token values
2. **Token validation**: Only basic format validation is performed
3. **HTTPS only**: Always use HTTPS when calling external APIs
4. **Scope limitations**: Tokens should have minimal required scopes
5. **Token expiry**: Handle expired tokens gracefully

## Client Implementation Examples

### JavaScript/TypeScript Client

```typescript
const response = await mcpClient.callTool({
  name: "get_github_user",
  arguments: {},
  _meta: {
    oauth_tokens: {
      github: await getGitHubToken(),
    },
    correlationId: generateRequestId(),
  },
});
```

### Python Client

```python
from mcp import ClientSession, types

async with ClientSession(read_stream, write_stream) as session:
    request = types.ClientRequest(
        types.CallToolRequest(
            method="tools/call",
            params=types.CallToolRequestParams(
                name="get_github_user",
                arguments={},
                _meta={
                    "oauth_tokens": {
                        "github": os.environ["GITHUB_TOKEN"]
                    }
                }
            )
        )
    )
    
    result = await session.send_request(request, types.CallToolResult)
```

## FAQ

**Q: Where do tokens come from?**
A: The MCP client is responsible for obtaining tokens through its own OAuth flow.

**Q: Are tokens stored in the MCP server?**
A: No, tokens are never stored. They're passed per-request via Context.

**Q: Can I use refresh tokens?**
A: Refresh token handling must be done by the client, not the MCP server.

**Q: What if a token expires during use?**
A: The tool returns a 401 error, and the client should refresh and retry.

**Q: Can different users pass different tokens?**
A: Yes, each request can have different tokens. The server is stateless.

**Q: Do I need to register an OAuth app?**
A: No, the MCP server needs no OAuth app registration. Only the client does.
{% endif -%}