{% if cookiecutter.include_oauth_backend == "yes" -%}
# OAuth Backend Token Exchange Documentation

## Overview

This MCP server includes OAuth backend token exchange support, allowing secure authentication with external services through a backend API. The server exchanges temporary tokens for real access tokens via a backend service, keeping sensitive OAuth credentials secure.

## Architecture

### How It Works

1. **Client provides credentials**: MCP client sends `userId`, `userToken`, and `providerId` in the `_meta` parameter
2. **Backend exchange**: The `oauth_backend` decorator calls your backend API to exchange the temp token
3. **Token injection**: The returned access token is injected into the context for tools to use
4. **API calls**: Tools use the access token to call external APIs (Reddit, Google, etc.)

### Key Differences from Passthrough Pattern

| Feature | OAuth Passthrough | OAuth Backend |
|---------|------------------|---------------|
| Client provides | Actual OAuth tokens | Temp tokens + user/provider IDs |
| Backend API | Not required | Required |
| Token storage | Never stored | Never stored |
| Security | Client manages tokens | Backend manages tokens |
| Use case | Direct token access | Enterprise/secure environments |

## Configuration

### Cookiecutter Options

When generating a new server, configure these options:

```yaml
include_oauth_backend: yes           # Enable backend OAuth support
oauth_backend_url: "https://api.example.com"  # Your backend API URL
oauth_backend_mock_mode: no          # Use "yes" for testing without backend
```

### Environment Variables

You can also configure via environment variables:

```bash
export OAUTH_BACKEND_URL="https://api.example.com"
export OAUTH_BACKEND_MOCK_MODE="no"
```

## Backend API Requirements

Your backend API must implement the following endpoint:

### Token Exchange Endpoint

**Endpoint**: `POST /api/connectors/requestAuth`

**Request Body**:
```json
{
  "userId": "user_identifier",
  "userToken": "temporary_token_from_client",
  "providerId": "oauth_provider_name"
}
```

**Success Response** (200 OK):
```json
{
  "accessToken": "decrypted_oauth_access_token"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired temp token
- `403 Forbidden`: User not authorized for provider
- `404 Not Found`: Provider not configured
- `500 Internal Server Error`: Backend error

## Client Usage

### MCP Client Implementation

Clients must pass the required parameters in the `_meta` field:

```python
# Example MCP client code
from mcp.client.session import ClientSession
from mcp import types

# Call a tool with OAuth backend parameters
result = await session.call_tool(
    "get_reddit_user",
    arguments={},
    _meta={
        "userId": "user_123",
        "userToken": "temp_token_abc456",
        "providerId": "reddit"
    }
)
```

### Required Parameters

All three parameters must be provided:
- `userId`: Unique identifier for the user
- `userToken`: Temporary token from your auth system
- `providerId`: OAuth provider name (must match tool's expected provider)

## Tool Implementation

### Creating OAuth Backend Tools

Tools using the OAuth backend pattern follow this structure:

```python
from mcp.server.fastmcp import Context
from typing import Dict, Any

async def get_reddit_user(ctx: Context = None) -> Dict[str, Any]:
    """Get Reddit user information using OAuth backend token."""
    
    # Token is automatically injected by oauth_backend decorator
    if ctx and hasattr(ctx, 'request_context'):
        meta = ctx.request_context.meta
        token = meta.get('current_oauth_token')
        
        if token:
            # Use token to call Reddit API
            headers = {"Authorization": f"Bearer {token}"}
            # Make API call...
            return {"username": "example_user"}
    
    return {"error": "No token available"}

# Export for registration in app.py
oauth_backend_tools = [
    ("reddit", get_reddit_user),
    ("reddit", list_user_subreddits),
]
```

### Important Notes

1. **Context Parameter Required**: All tools MUST include `ctx: Context = None`
2. **Async Functions**: All tools must be async functions
3. **Provider Matching**: The provider in the tuple must match `providerId` from client
4. **Token Access**: Token is available at `ctx.request_context.meta['current_oauth_token']`

## Testing

### Mock Mode Testing

Enable mock mode for testing without a real backend:

```bash
# Set mock mode
export OAUTH_BACKEND_MOCK_MODE="yes"

# Run the test script
python test_oauth_backend.py
```

Mock mode returns provider-specific test tokens:
- Reddit: `mock_reddit_token_123456789`
- GitHub: `gho_mockGitHubToken123456789`
- Google: `ya29.mockGoogleToken123456789`

### Manual Testing Script

Use the provided test script:

```bash
# Test with mock backend
python test_oauth_backend.py

# Test with real backend
python test_oauth_backend.py --backend-url https://api.example.com --no-mock
```

### Unit Tests

Run unit tests for the OAuth backend components:

```bash
pytest tests/unit/test_oauth_backend.py -v
```

## Error Handling

The OAuth backend decorator provides detailed error responses:

### Missing Parameters
```json
{
  "error": "missing_parameters",
  "message": "Missing required OAuth parameters for reddit",
  "provider": "reddit",
  "details": "Required: userId, userToken, providerId. Missing: userToken"
}
```

### Provider Mismatch
```json
{
  "error": "provider_mismatch",
  "message": "This tool requires reddit authentication",
  "provider": "reddit",
  "details": "Received providerId: github"
}
```

### API Error
```json
{
  "error": "api_error",
  "message": "Failed to exchange token with reddit backend",
  "provider": "reddit",
  "details": "Backend API request timed out"
}
```

### Invalid Token Format
```json
{
  "error": "invalid_parameter",
  "message": "Invalid userToken format for reddit",
  "provider": "reddit",
  "details": "userToken must be a non-empty string"
}
```

## Security Considerations

1. **Never Log Tokens**: The implementation avoids logging full tokens
2. **HTTPS Only**: Always use HTTPS for backend API communication
3. **Token Expiry**: Backend should validate token expiry
4. **Rate Limiting**: Implement rate limiting on backend API
5. **Audit Logging**: Log token exchanges for security auditing

## Troubleshooting

### Common Issues

**Issue**: "No backend URL configured"
- **Solution**: Set `oauth_backend_url` in config or `OAUTH_BACKEND_URL` environment variable

**Issue**: "httpx is required for OAuth backend functionality"
- **Solution**: Install httpx: `pip install httpx>=0.27.0`

**Issue**: Provider mismatch errors
- **Solution**: Ensure `providerId` from client matches the provider expected by the tool

**Issue**: Token exchange fails with 401
- **Solution**: Verify temp token is valid and not expired

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Passthrough

If migrating from OAuth passthrough to backend pattern:

1. **Update client code** to send `userId`, `userToken`, `providerId` instead of tokens
2. **Implement backend API** endpoint `/api/connectors/requestAuth`
3. **Update tool registration** in app.py to use `oauth_backend_tools`
4. **Test thoroughly** with mock mode first

## Example Providers

The pattern works with any OAuth provider:

- **Reddit**: See `reddit_backend_tools.py`
- **GitHub**: Implement similar pattern with GitHub API
- **Google**: Use for Google services (Drive, Sheets, etc.)
- **Microsoft**: Access Microsoft Graph API
- **Custom**: Any OAuth 2.0 provider

## Support

For issues or questions:
1. Check the error messages for specific details
2. Review the test scripts for working examples
3. Enable debug logging for more information
4. Ensure all three parameters are provided by the client
{% endif -%}