# SAAGA MCP Server Cookie Cutter - Project Overview
**Last Updated**: August 13, 2025

## What This Is
A production-ready cookiecutter template for creating MCP (Model Context Protocol) servers with SAAGA decorator patterns. It generates fully-functional MCP servers that AI assistants like Claude can use to execute tools and interact with external systems.

## Core Technologies
- **MCP (Model Context Protocol)**: Anthropic's protocol for AI-tool communication
- **FastMCP**: High-level Python framework for building MCP servers
- **SAAGA Decorators**: Enterprise patterns for exception handling, logging, and parallelization
- **Transports**: STDIO (default), SSE, and Streamable HTTP support
- **Storage**: SQLite for unified logging with correlation ID tracking
- **Admin UI**: Optional Streamlit dashboard for monitoring and configuration

## Key Architecture Decisions

### Package Structure
- **log_system** package (NOT "logging" - avoid Python stdlib conflicts!)
- Unified logging with pluggable destinations (SQLite v1, future: Elasticsearch, Postgres)
- Correlation IDs track requests across entire lifecycle

### SAAGA Decorator Pattern (Applied Automatically)
1. **exception_handler**: Catches all exceptions, returns SAAGA-standard error format
2. **tool_logger**: Tracks execution metrics, logs to SQLite with correlation IDs
3. **parallelize**: (Optional) Transforms function signatures for batch processing
4. **oauth_passthrough**: (Optional) Checks Context for OAuth tokens passed by client

**CRITICAL**: All tools MUST be async functions with `ctx: Context = None` parameter:
```python
from mcp.server.fastmcp import Context

async def my_tool(param: str, ctx: Context = None) -> dict:
    # Context parameter is REQUIRED for correlation IDs to work
    return {"result": "success"}
```

## Recent Critical Fixes (August 2025)

### 1. Correlation ID Support Fixed
- **Problem**: Client-provided correlation IDs weren't being captured
- **Root Cause**: Tools were missing `ctx: Context = None` parameter
- **Solution**: Added Context parameter to all tools, updated tool_logger decorator to extract IDs from Context metadata
- **Impact**: Correlation IDs now work with both client-provided and auto-generated values

### 2. Circular Import Resolution  
- **Problem**: Package named "logging" conflicted with Python's stdlib
- **Solution**: Renamed entire package from `logging/` to `log_system/`
- **Files Affected**: All imports, decorators, server initialization

### 3. Async/Sync Context Handling
- **Problem**: SQLite writes failed in sync contexts (RuntimeWarning about unawaited coroutines)
- **Solution**: Added `write_sync()` method to SQLite destination, UnifiedLogger detects context and uses appropriate method

### 4. Database Filename Correction
- **Changed**: `logs.db` → `unified_logs.db` in all documentation and code

## Project Structure
```
{{cookiecutter.project_slug}}/
├── {{cookiecutter.project_slug}}/
│   ├── server/
│   │   └── app.py              # Main server with transport support
│   ├── tools/
│   │   └── example_tools.py    # Tool implementations (with Context params!)
│   ├── decorators/
│   │   ├── exception_handler.py
│   │   ├── tool_logger.py      # Extracts correlation IDs from Context
│   │   └── parallelize.py
│   ├── log_system/              # Renamed from "logging" to avoid conflicts
│   │   ├── unified_logger.py   # Core logging with async/sync support
│   │   ├── correlation.py      # Correlation ID management
│   │   └── destinations/
│   │       └── sqlite.py       # Has both write() and write_sync() methods
│   └── ui/                     # Optional Streamlit admin interface
├── tests/
│   ├── integration/
│   │   ├── conftest.py         # Parameterized fixtures for STDIO & Streamable HTTP
│   │   └── test_*.py           # Integration tests run on multiple transports
│   └── unit/
└── docs/
    ├── DECORATOR_PATTERNS.md   # Explains Context parameter requirement
    └── UNIFIED_LOGGING.md      # Details on correlation IDs

```

## OAuth Token Passthrough (Optional Feature) - COMPLETED August 2025

### Implementation Journey (JIRA: ASEP-77)
**Initial Requirement**: Implement OAuth support for MCP servers with ZERO pre-configuration
**Challenge**: Traditional OAuth requires app registration, which violates zero-config requirement
**Solution**: Token Passthrough Pattern (Option 1) - Client handles OAuth, server uses tokens

### Final Implementation
- **Client-Side OAuth**: The MCP client (Solve/React/etc) handles ALL OAuth logic
- **Token Passthrough**: Client passes tokens via Context `_meta` parameter in `oauth_tokens` dictionary
- **No OAuth Flow**: MCP server NEVER handles OAuth flow, callbacks, or token storage
- **Zero Configuration**: No OAuth app registration, client_id, or client_secret needed

### What We Built
When `include_oauth_passthrough=yes`:
1. **oauth_passthrough decorator**: 
   - Checks Context for tokens in `oauth_tokens` dictionary
   - Validates token format (non-empty strings)
   - Returns graceful errors for all failure cases
   - Adds provider context to authentication errors
   - NEVER crashes the server

2. **GitHub example tools** (3 tools):
   - `get_github_user`: Gets authenticated user info
   - `list_user_repos`: Lists user's repositories
   - `create_github_issue`: Creates issues in repos
   - All handle 401/403/404 errors gracefully

3. **Test Scripts**:
   - `test_oauth_private_repo.py`: Tests with real GitHub tokens
   - `test_oauth_error_handling.py`: Validates error handling
   - Integration tests that use real MCP client

4. **Error Handling Improvements**:
   - Token validation (empty, whitespace, invalid format)
   - Enhanced error messages with provider context
   - Try-catch blocks prevent all crashes
   - Graceful degradation for missing streamable_http

### Key Architecture Decisions
1. **No OAuth in MCP Server**: Server is a "dumb consumer" of tokens
2. **Decorator Pattern**: `oauth_passthrough` applied programmatically (NOT @syntax)
3. **Tool Organization**: Tools export `oauth_passthrough_tools` list with (provider, function) tuples
4. **App.py Remains Generic**: No provider-specific logic in app.py

### Testing OAuth
```bash
# Test with private GitHub repo (requires real token)
python test_oauth_private_repo.py gho_YOUR_TOKEN owner/repo

# Test error handling with invalid tokens
python test_oauth_error_handling.py

# Run integration tests
pytest tests/integration/test_oauth_passthrough_integration.py -v
```

### Important Limitations
- **MCP Inspector**: Cannot test OAuth (doesn't support `_meta` parameter)
- **Clients Must**: Handle OAuth flow and pass tokens via `_meta`
- **Test Scripts Required**: Use provided scripts for OAuth testing

### Lessons Learned
1. **Naming Consistency**: Scripts named `test_oauth_*` not just `test_*`
2. **Conditional Imports**: Handle missing `streamable_http` gracefully
3. **Documentation Critical**: Clear examples of token format and testing
4. **Error Messages Matter**: Users frustrated by crashes, need graceful errors

### If Resuming OAuth Work
- All OAuth code is in cookiecutter template
- Test with `include_oauth_passthrough=yes`
- GitHub tools are examples - pattern works for any OAuth provider
- Remember: MCP server NEVER handles OAuth flow, only uses tokens

## Testing Configuration
- **Automated Tests**: STDIO and Streamable HTTP transports
- **Not Automated**: SSE transport (can be tested manually)
- **Fixture**: `mcp_session` in conftest.py with transport parameterization

## Known Limitations
- **MCP Inspector**: No UI for setting correlation IDs or OAuth tokens (auto-generates IDs only)
- **SSE Transport**: Not included in automated test suite
- **Correlation IDs**: Require custom MCP clients to provide them in metadata
- **OAuth Tokens**: Require custom MCP clients to pass them via Context

## Quick Validation
After generating a new server:
```bash
# Test server starts
uv run python -m {{project_slug}}.server.app --help

# Run tests
uv run pytest

# Check correlation IDs work
uv run python -m {{project_slug}}.tools.example_tools
```

## Remember When Debugging
1. Always check tools have `ctx: Context = None` parameter
2. Package is `log_system`, not `logging`
3. Database is `unified_logs.db`, not `logs.db`
4. Correlation IDs need custom clients (not MCP Inspector)
5. All tools must be async functions