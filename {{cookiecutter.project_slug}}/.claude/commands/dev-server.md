---
description: Manage MCP Inspector and Streamlit UI processes reliably with proper cleanup
argument-hint: "[start|stop|restart|status|clean]"
allowed-tools: ["Bash", "Read"]
---

I'll help you manage the MCP Inspector and Streamlit UI processes reliably.

## Parse Command

Command requested: $ARGUMENTS

{% raw %}
{% if 'stop' in ARGUMENTS or 'restart' in ARGUMENTS or 'clean' in ARGUMENTS %}
## Step 1: Stop All Processes

Killing all MCP and Streamlit processes:

```bash
# Kill MCP dev processes
pkill -f "mcp dev" || true

# Kill Streamlit processes  
pkill -f "streamlit run" || true

# Clean up any lingering processes on ports
lsof -i :6274 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
lsof -i :6277 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
lsof -i :8501 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
lsof -i :{{ cookiecutter.server_port }} | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true
```

Verifying all processes are stopped...

{% endif %}

{% if 'start' in ARGUMENTS or 'restart' in ARGUMENTS %}
## Step 2: Check Port Availability

Checking if ports are available:
- MCP Inspector: 6274, 6277
- Streamlit UI: 8501
- MCP Server SSE: {{ cookiecutter.server_port }}

```bash
# Check each port
for port in 6274 6277 8501 {{ cookiecutter.server_port }}; do
    if lsof -i :$port | grep -q LISTEN; then
        echo "WARNING: Port $port is in use. Attempting to free it..."
        lsof -i :$port | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
done
```

## Step 3: Start MCP Inspector

Starting MCP Inspector in the background:

```bash
# Ensure we're in the project directory
cd {{ cookiecutter.project_slug }}

# Start MCP dev inspector
mcp dev {{ cookiecutter.project_slug }}/server/app.py > /tmp/mcp-inspector.log 2>&1 &
MCP_PID=$!
echo "MCP Inspector started with PID: $MCP_PID"

# Wait for it to initialize
sleep 3

# Verify it's running
if ps -p $MCP_PID > /dev/null; then
    echo "✓ MCP Inspector is running"
else
    echo "✗ MCP Inspector failed to start. Check /tmp/mcp-inspector.log"
    cat /tmp/mcp-inspector.log
fi
```

{% if cookiecutter.include_admin_ui == "yes" %}
## Step 4: Start Streamlit UI

Starting Streamlit Admin UI in the background:

```bash
# Start Streamlit UI
streamlit run {{ cookiecutter.project_slug }}/ui/app.py --server.port 8501 > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit UI started with PID: $STREAMLIT_PID"

# Wait for it to initialize
sleep 3

# Verify it's running
if ps -p $STREAMLIT_PID > /dev/null; then
    echo "✓ Streamlit UI is running"
else
    echo "✗ Streamlit UI failed to start. Check /tmp/streamlit.log"
    cat /tmp/streamlit.log
fi
```
{% endif %}

## Step 5: Verify Everything is Running

```bash
# Check all processes
echo "=== Process Status ==="
ps aux | grep -E "mcp dev|streamlit" | grep -v grep || echo "No processes found"

echo -e "\n=== Port Status ==="
for port in 6274 6277 8501 {{ cookiecutter.server_port }}; do
    if lsof -i :$port | grep -q LISTEN; then
        echo "✓ Port $port is active"
    else
        echo "✗ Port $port is not active"
    fi
done
```

{% endif %}

{% if 'status' in ARGUMENTS %}
## Check Current Status

Checking all MCP-related processes and ports:

```bash
echo "=== Running Processes ==="
ps aux | grep -E "mcp dev|streamlit" | grep -v grep || echo "No processes running"

echo -e "\n=== Port Status ==="
echo "MCP Inspector ports (6274, 6277):"
lsof -i :6274 2>/dev/null | grep LISTEN || echo "  Port 6274: Not in use"
lsof -i :6277 2>/dev/null | grep LISTEN || echo "  Port 6277: Not in use"

echo "Streamlit UI port (8501):"
lsof -i :8501 2>/dev/null | grep LISTEN || echo "  Port 8501: Not in use"

echo "MCP Server SSE port ({{ cookiecutter.server_port }}):"
lsof -i :{{ cookiecutter.server_port }} 2>/dev/null | grep LISTEN || echo "  Port {{ cookiecutter.server_port }}: Not in use"

echo -e "\n=== Log Files ==="
[ -f /tmp/mcp-inspector.log ] && echo "MCP Inspector log: /tmp/mcp-inspector.log ($(wc -l < /tmp/mcp-inspector.log) lines)"
[ -f /tmp/streamlit.log ] && echo "Streamlit log: /tmp/streamlit.log ($(wc -l < /tmp/streamlit.log) lines)"
```

{% endif %}

{% if 'clean' in ARGUMENTS %}
## Clean Up Everything

Performing complete cleanup:

```bash
# Remove log files
rm -f /tmp/mcp-inspector.log /tmp/streamlit.log

# Clean Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clean any test artifacts
rm -rf .pytest_cache/ 2>/dev/null || true
rm -f .coverage 2>/dev/null || true

echo "✓ Cleanup complete"
```
{% endif %}
{% endraw %}

## Access URLs

When running, services are available at:

- **MCP Inspector**: http://localhost:6274
  - Use this to test and debug your MCP tools
  - Shows all registered tools and their parameters
  - Allows interactive testing

{% if cookiecutter.include_admin_ui == "yes" %}
- **Streamlit Admin UI**: http://localhost:8501
  - View server status and configuration
  - Monitor tool execution logs
  - Edit configuration
{% endif %}

- **MCP Server (SSE)**: http://localhost:{{ cookiecutter.server_port }}
  - Direct SSE transport endpoint
  - For programmatic access

## Troubleshooting

If services fail to start:

1. **Check ports**: Make sure ports aren't already in use
2. **Check logs**: Review `/tmp/mcp-inspector.log` and `/tmp/streamlit.log`
3. **Virtual environment**: Ensure you're in the correct venv
4. **Dependencies**: Run `pip install -e .` to ensure all deps are installed
5. **Clean restart**: Use `/dev-server clean` then `/dev-server start`

## Tips

- Always use `/dev-server stop` before closing your terminal
- Use `/dev-server status` to check what's running
- Logs are in `/tmp/` for debugging
- If ports get stuck, use `/dev-server clean` for full cleanup