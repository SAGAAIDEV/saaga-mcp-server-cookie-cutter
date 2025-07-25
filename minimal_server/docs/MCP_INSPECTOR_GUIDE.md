# MCP Inspector Testing Guide for Minimal Server

This guide helps you test your MCP server tools using the MCP Inspector, including troubleshooting common setup issues.

## Prerequisites

### 1. Virtual Environment Setup

**CRITICAL**: Always ensure you're using the virtual environment's MCP, not any global installation.

```bash
# From your project root
cd minimal_server

# Activate your virtual environment
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Verify MCP is using the correct version
which mcp
# Should show: /path/to/minimal_server/.venv/bin/mcp
# NOT: /opt/homebrew/bin/mcp or /usr/local/bin/mcp
```

**If you see a global path**, you have two options:

1. Use the full path to your venv's mcp:
   ```bash
   .venv/bin/mcp dev minimal_server/server/app.py
   ```

2. Fix your PATH (recommended):
   ```bash
   # Check your PATH order
   echo $PATH | tr ':' '\n' | head -5
   
   # Deactivate and reactivate
   deactivate
   source .venv/bin/activate
   which mcp  # Should now show venv path
   ```

### 2. Install Dependencies

If you haven't already:
```bash
uv sync
```

## Launching MCP Inspector

From your project root (with venv activated):
```bash
mcp dev minimal_server/server/app.py
```

You should see:
- Server logs showing tool registration
- SQLite database initialization
- Inspector URL: http://127.0.0.1:6274

Open the Inspector URL in your browser.

## Viewing Logs

The SAAGA decorators automatically log all tool executions.

### Log Locations

**Text Logs**:
- macOS: `~/Library/Logs/mcp-servers/minimal_server.log`
- Linux: `~/.local/state/mcp-servers/logs/minimal_server.log`
- Windows: `%LOCALAPPDATA%\mcp-servers\logs\minimal_server.log`

**SQLite Database** (tool execution history):
- macOS: `~/Library/Application Support/minimal_server/tool_logs.db`
- Linux: `~/.local/share/minimal_server/tool_logs.db`
- Windows: `%LOCALAPPDATA%\minimal_server\tool_logs.db`

## Common Issues

### ModuleNotFoundError

If you see `ModuleNotFoundError: No module named 'minimal_server'`:

1. Ensure you're in the project root directory
2. Check virtual environment is activated: `which python`
3. Reinstall: `uv sync`
4. Use full mcp path: `.venv/bin/mcp dev minimal_server/server/app.py`

### MCP Inspector Not Loading

1. Check server started without errors
2. Try a different port: `mcp dev minimal_server/server/app.py --port 5174`
3. Clear browser cache and refresh

### Tools Not Appearing

1. Check server logs for registration messages
2. Refresh the Inspector page
3. Verify no import errors in terminal

## Next Steps

Once you've verified the example tools work:

1. Add your own tools in `minimal_server/tools/`
2. Follow the SAAGA decorator pattern for consistency
3. Test thoroughly with the Inspector
4. Check logs for performance metrics

For more details on creating custom tools, see the [SAAGA Decorator Patterns](../DECORATOR_PATTERNS.md) documentation.