---
description: Generate a new MCP test server from cookie cutter, set it up, and launch Inspector + UI
usage: /project:generate-test-server [PROJECT-NAME] [INCLUDE-UI]
example: /project:generate-test-server "My Test Server" yes
---

I'll generate a new MCP test server from the SAAGA cookie cutter template and set up a complete testing environment.

## Parse Arguments
Let me extract the project name and UI inclusion preference:
- Arguments provided: $ARGUMENTS
- Expected format: [PROJECT-NAME] [INCLUDE-UI] (e.g., "My Test Server" yes)
- Default: If no arguments provided, I'll use "Test MCP Server" with UI included

## Step 1: Clean Up Any Existing Processes and Previous Generated Server

First, I'll ensure no conflicting processes are running and clean up any previous test server:

!pkill -f "mcp dev" || true
!pkill -f "mcp-inspector" || true
!pkill -f "@modelcontextprotocol/inspector" || true
!pkill -f "streamlit run" || true

Check if a previous test server exists and clean it up:

!if [ -d "./generated_servers/test_mcp_server" ]; then \
  echo "🧹 Cleaning up previous test server at ./generated_servers/test_mcp_server"; \
  rm -rf "./generated_servers/test_mcp_server"; \
fi

## Step 2: Generate Project from Cookie Cutter

I'll use the cookie cutter template to generate a new project:

!cookiecutter . --no-input \
  project_name="Test MCP Server" \
  project_slug="test_mcp_server" \
  description="Test MCP server generated for development testing" \
  author_name="Test Developer" \
  author_email="test@example.com" \
  include_admin_ui="${INCLUDE_UI:-yes}" \
  include_example_tools="yes" \
  include_parallel_example="yes" \
  log_level="DEBUG" \
  --output-dir ./generated_servers

## Step 3: Set Up Virtual Environment

Navigate to the generated project and create a virtual environment:

!PROJECT_DIR="./generated_servers/test_mcp_server" && \
  cd "$PROJECT_DIR" && \
  python -m venv .venv && \
  source .venv/bin/activate && \
  pip install --upgrade pip && \
  pip install -e .

## Step 4: Verify Installation

The installation is complete. The MCP Inspector will verify the server works when it starts.

## Step 5: Start MCP Inspector in Background

Launch the MCP Inspector with the server:

!cd ./generated_servers/test_mcp_server && \
  source .venv/bin/activate && \
  nohup mcp dev test_mcp_server/server/app.py > mcp_inspector.log 2>&1 & \
  echo $! > mcp_inspector.pid && \
  echo "🚀 MCP Inspector started with PID: $(cat mcp_inspector.pid)"

Wait for Inspector to initialize:

!sleep 3

## Step 6: Start Streamlit UI in Background (if included)

If UI was included, start the Streamlit admin interface:

!if [ "${INCLUDE_UI:-yes}" = "yes" ]; then \
  cd ./generated_servers/test_mcp_server && \
  source .venv/bin/activate && \
  nohup streamlit run test_mcp_server/ui/app.py --server.port 8501 > streamlit.log 2>&1 & \
  echo $! > streamlit.pid && \
  echo "🎨 Streamlit UI started with PID: $(cat streamlit.pid)"; \
fi

Wait for Streamlit to initialize:

!sleep 3

## Step 7: Display Access Information

### 🔗 Access URLs:

**MCP Inspector**: http://localhost:6274
- Use this to test and interact with your MCP tools
- All 6 example tools should be available:
  - `echo_tool` - Simple string echo
  - `get_time` - Get current time
  - `calculate_fibonacci` - Calculate Fibonacci numbers
  - `random_number` - Generate random numbers
  - `process_batch_data` - Process data in batches
  - `simulate_heavy_computation` - Test parallel processing

**Streamlit Admin UI**: http://localhost:8501 (if UI included)
- Dashboard: Server status and overview
- Configuration: Edit server settings
- Logs: View and export execution logs

## Step 8: Testing Guide Reference

For detailed testing instructions, refer to the MCP Inspector Guide:

**Guide Location**: `./generated_servers/test_mcp_server/docs/MCP_INSPECTOR_GUIDE.md`

Key testing steps from the guide:
1. Open MCP Inspector at http://localhost:6274
2. Select your server from the dropdown
3. Test each tool with sample parameters
4. Monitor logs in the Streamlit UI
5. Check decorator functionality (logging, error handling, parallelization)

## Step 9: Cleanup Instructions

When you're done testing, stop the processes:

```bash
# Stop MCP Inspector
kill $(cat ./generated_servers/test_mcp_server/mcp_inspector.pid)

# Stop Streamlit UI (if running)
kill $(cat ./generated_servers/test_mcp_server/streamlit.pid) 2>/dev/null || true

# Remove PID files
rm -f ./generated_servers/test_mcp_server/*.pid
```

## Troubleshooting

If you encounter issues:

1. **Port conflicts**: Check if ports 6274 or 8501 are in use:
   ```bash
   lsof -i :6274
   lsof -i :8501
   ```

2. **Process not starting**: Check the log files:
   ```bash
   tail -f ./generated_servers/test_mcp_server/mcp_inspector.log
   tail -f ./generated_servers/test_mcp_server/streamlit.log
   ```

3. **Import errors**: Ensure virtual environment is activated:
   ```bash
   cd ./generated_servers/test_mcp_server
   source .venv/bin/activate
   pip list
   ```

## Summary

Your test MCP server is now running with:
- ✅ MCP Inspector for tool testing
- ✅ Streamlit UI for administration (if included)
- ✅ All SAAGA decorators (exception handling, logging, parallelization)
- ✅ 6 example tools demonstrating various patterns
- ✅ SQLite logging database
- ✅ Platform-aware configuration

**Note**: Each time you run this command, it automatically cleans up any previous test server in the same location. This ensures a fresh environment for each test session.

Start testing your tools now by visiting the URLs above!