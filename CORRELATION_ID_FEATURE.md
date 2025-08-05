# Frontend-Driven Correlation IDs in SAAGA MCP Server

## Overview

The SAAGA MCP Server Cookie Cutter now supports client-provided correlation IDs, enabling end-to-end request tracing from frontend applications through MCP tools to backend logging systems.

## How It Works

### 1. Client Passes Correlation ID

MCP clients can include a correlation ID in the request metadata using the `_meta` field:

```python
# Using the MCP SDK's send_request method
request = types.ClientRequest(
    types.CallToolRequest(
        method="tools/call",
        params=types.CallToolRequestParams(
            name="my_tool",
            arguments={"param": "value"},
            _meta={
                "correlationId": "frontend_req_abc123",
                # Other metadata fields...
            }
        )
    )
)

result = await session.send_request(request, types.CallToolResult)
```

### 2. Tool Logger Decorator Checks for Client ID

The `tool_logger` decorator automatically:
1. Checks if the Context parameter contains metadata with a correlation ID
2. Uses the client-provided ID if present
3. Otherwise generates a new correlation ID (current behavior)

```python
@tool_logger
async def my_tool(param: str, ctx: Context) -> str:
    # Correlation ID is automatically set by the decorator
    # All logs within this tool will use the same correlation ID
    return "Result"
```

### 3. Correlation ID Propagates Through Logs

All log entries created during tool execution will include the correlation ID:
- Whether client-provided or auto-generated
- Across all configured logging destinations (SQLite, console, etc.)
- Through the entire request lifecycle

## Integration Examples

### Next.js/Vercel AI SDK Integration

```typescript
import { generateText } from 'ai';
import { v4 as uuidv4 } from 'uuid';

// Generate correlation ID in frontend
const correlationId = `frontend_${uuidv4().substring(0, 12)}`;

// Pass through custom MCP client wrapper
const result = await mcpClient.callToolWithCorrelation(
  'process_data',
  { data: userInput },
  correlationId
);

// Track logs in real-time using correlation ID
const logs = await convex.query(api.logs.getByCorrelationId, { 
  correlationId 
});
```

### Custom MCP Client Example

See `test_correlation_id_client.py` for a complete example of how to build an MCP client that passes correlation IDs.

## Benefits

1. **End-to-End Tracing**: Track requests from frontend UI through MCP tools to backend services
2. **Debugging**: Easily find all logs related to a specific user interaction
3. **Performance Monitoring**: Measure complete request lifecycles
4. **Error Tracking**: Associate errors with specific frontend requests
5. **Real-time Updates**: Frontend can subscribe to logs by correlation ID

## Backwards Compatibility

This feature is fully backwards compatible:
- Existing MCP clients that don't pass correlation IDs continue to work
- Tools automatically generate correlation IDs when not provided
- No changes required to existing tool implementations
- Function signatures remain unchanged

## Testing

Run the included test to verify the feature works:

```bash
python test_correlation_simple.py
```

This will:
1. Generate a test server from the cookie cutter
2. Test with client-provided correlation ID
3. Test without correlation ID (auto-generation)
4. Verify both scenarios work correctly

## Future Enhancements

While not implemented in this PR, the following enhancements could be added:

1. **Dynamic Docstring Updates**: Add logging configuration info to tool docstrings
2. **Log Access Instructions**: Include MCP tool information for querying logs
3. **Real-time Log Streaming**: WebSocket support for live log updates
4. **Correlation ID Chains**: Support for parent-child correlation IDs