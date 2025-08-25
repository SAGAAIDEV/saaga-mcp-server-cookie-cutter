---
description: Generate a new MCP test server from cookie cutter, set it up, and launch Inspector + UI
argument-hint: "[project-name] [include-ui]"
allowed-tools: ["Bash", "Read", "Write", "LS"]
---

## Grounding References
- **Template Testing**: See `.reference/cookiecutter-maintenance.md#testing-template-generation` for testing patterns
- **Critical Files**: Verify `.reference/critical-files.md` patterns are preserved in generated server

**MANDATORY EXECUTION SEQUENCE - Execute ALL commands below in exact order:**

**STEP 1 - Kill all existing MCP and Streamlit processes:**
Execute these bash commands in sequence:
- `pkill -f "mcp dev" || true`
- `pkill -f "streamlit run" || true`
- `lsof -i :6274 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true`
- `lsof -i :6277 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true`
- `lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true`

**STEP 2 - Clean up any previous test server:**
Execute: `rm -rf ./generated_servers/test_mcp_server`

**STEP 3 - Generate new server from cookie cutter:**
Execute: `cookiecutter . --no-input project_name="Test MCP Server" project_slug="test_mcp_server" description="Test MCP server generated for development testing" author_name="Test Developer" author_email="test@example.com" --output-dir ./generated_servers`

**STEP 4 - Navigate to generated project directory:**
Execute: `cd ./generated_servers/test_mcp_server`

**STEP 5 - Set up Python environment with UV:**
Execute these commands in sequence from the test_mcp_server directory:
- `cd ./generated_servers/test_mcp_server && uv venv`
- `cd ./generated_servers/test_mcp_server && uv sync`

**STEP 6 - Start MCP Inspector in background:**
Execute: `cd ./generated_servers/test_mcp_server && uv run mcp dev test_mcp_server/server/app.py &`
Then wait 3 seconds by executing: `sleep 3`

**STEP 7 - Start Streamlit UI in background:**
Execute: `cd ./generated_servers/test_mcp_server && uv run streamlit run test_mcp_server/ui/app.py --server.port 8501 &`
Then wait 3 seconds by executing: `sleep 3`

**STEP 8 - Verify processes are running:**
Execute these commands to check status:
- `ps aux | grep "mcp dev" | grep -v grep`
- `ps aux | grep "streamlit run" | grep -v grep`

**STEP 9 - Report access URLs to user:**
Display this information:
- MCP Inspector is available at: http://localhost:6274
- Streamlit Admin UI is available at: http://localhost:8501
- Generated project location: ./generated_servers/test_mcp_server

**STEP 10 - Display available tools:**
List the 6 example tools that are now available for testing:
- echo_tool - Simple string echo
- get_time - Get current time
- calculate_fibonacci - Calculate Fibonacci numbers
- random_number - Generate random numbers
- process_batch_data - Process data in batches (parallel)
- simulate_heavy_computation - Test parallel processing

**CRITICAL REQUIREMENTS:**
- You MUST execute EVERY command listed above in the exact order specified
- Do NOT skip any step
- Do NOT modify any commands
- Do NOT combine steps
- Wait for the specified delays after background processes
- If any step fails, report the error but continue with remaining steps

**CLEANUP REFERENCE (for user's later use):**
To stop the processes later, the user can run:
```bash
pkill -f "mcp dev"
pkill -f "streamlit run"
```