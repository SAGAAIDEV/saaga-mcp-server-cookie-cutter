# OAuth Error Handling Documentation

## Overview
The OAuth token passthrough implementation includes comprehensive error handling to ensure that authentication failures and invalid tokens never cause the MCP server to crash. All errors are handled gracefully and return structured error responses.

## Error Types and Responses

### 1. No Token Provided
**Scenario**: Client doesn't provide any OAuth tokens
**Response**:
```json
{
    "error": "token_not_provided",
    "message": "No {provider} token provided by client",
    "provider": "github",
    "details": "The client must provide OAuth tokens via Context in the oauth_tokens dictionary"
}
```

### 2. Invalid Token Format
**Scenario**: Token is empty, whitespace-only, or not a string
**Response**:
```json
{
    "error": "invalid_token_format",
    "message": "Invalid {provider} token format",
    "provider": "github",
    "details": "Token must be a non-empty string"
}
```

### 3. Unauthorized (401)
**Scenario**: Token is invalid or expired according to the provider
**Response**:
```json
{
    "error": "unauthorized",
    "message": "Invalid or expired OAuth token",
    "status_code": 401,
    "provider": "github",
    "details": "The provided token may be invalid, expired, or lack required permissions"
}
```

### 4. Forbidden (403)
**Scenario**: Token lacks required permissions
**Response**:
```json
{
    "error": "forbidden",
    "message": "Token lacks permission to perform this action",
    "status_code": 403,
    "provider": "github"
}
```

### 5. API Timeout
**Scenario**: Provider API request times out
**Response**:
```json
{
    "error": "timeout",
    "message": "Request to GitHub API timed out"
}
```

### 6. Unexpected Errors
**Scenario**: Any unexpected error in OAuth processing
**Response**:
```json
{
    "error": "oauth_processing_error",
    "message": "Error processing OAuth token for {provider}",
    "provider": "github",
    "details": "Specific error message"
}
```

## Implementation Details

### Decorator-Level Validation
The `oauth_passthrough` decorator performs basic validation:
1. Checks if token exists in Context
2. Validates token is a non-empty string
3. Catches all exceptions to prevent crashes
4. Adds logging for debugging

### Tool-Level Error Handling
Each OAuth-protected tool:
1. Handles HTTP status codes from the provider
2. Returns structured error responses
3. Includes provider-specific error details
4. Never throws unhandled exceptions

### Error Enhancement
When authentication errors occur, the decorator adds:
- Provider information
- Helpful context about possible causes
- Suggestions for resolution

## Testing Error Handling

Run the error handling test suite:
```bash
python test_error_handling.py
```

This tests:
- Missing tokens
- Empty tokens
- Invalid tokens
- Whitespace-only tokens
- Network timeouts
- Provider API errors

## Best Practices

1. **Always Return Structured Errors**: Never raise exceptions that could crash the server
2. **Include Context**: Add provider name and helpful details to error messages
3. **Log for Debugging**: Use logging to help diagnose issues without exposing sensitive data
4. **Validate Early**: Check token format before making API calls
5. **Handle All Status Codes**: Provider APIs may return various error codes

## Client Integration

Clients should handle these error responses gracefully:

```python
result = await mcp_client.call_tool("get_github_user", {})
if "error" in result:
    if result["error"] == "token_not_provided":
        # Prompt user to provide token
        pass
    elif result["error"] == "unauthorized":
        # Token is invalid/expired, refresh it
        pass
    elif result["error"] == "forbidden":
        # Token lacks permissions, request new scopes
        pass
```

## Monitoring and Debugging

The OAuth decorator logs at different levels:
- `INFO`: Token not provided (expected case)
- `WARNING`: Invalid token format
- `ERROR`: Unexpected errors

Example log output:
```
INFO: No github token provided in context
WARNING: Invalid github token format provided
ERROR: Unexpected error in oauth_passthrough for github: Connection refused
```

## Security Considerations

1. **Never Log Tokens**: The implementation never logs actual token values
2. **Sanitize Error Messages**: Provider error messages are sanitized before returning
3. **Rate Limiting**: Consider implementing rate limiting for failed auth attempts
4. **Token Validation**: Only basic format validation is performed locally

## Future Enhancements

Potential improvements for error handling:
1. Retry logic with exponential backoff
2. Circuit breaker pattern for provider outages
3. Token refresh hints in error responses
4. Metrics collection for auth failures
5. Provider-specific error code mapping