---
description: Helper guide for managing MCP processes during development - kill, restart, and debug
argument-hint: ""
allowed-tools: ["Bash", "KillBash", "BashOutput"]
---

# MCP Process Management Guide

## Understanding Process Management

**Why process management matters:**
- MCP Inspector locks Python modules while running
- Changes to tools require server restart
- Multiple processes can conflict
- Clean slate ensures latest code runs
- **OLD BROWSER TABS cause connection errors!**

## ⚠️ CRITICAL: The Browser Tab Problem ⚠️

**THE MOST COMMON ISSUE:**
```
🚨 Old MCP Inspector tabs (http://localhost:6274) in ANY browser
   cause "Error Connecting to MCP Inspector Proxy"
   
   This happens even if processes are killed correctly!
   
   ALWAYS check ALL browsers: Chrome, Firefox, Safari, Arc, etc.
```

## Common Process Commands

### 1. Find Running Processes

```bash
# Find all MCP-related processes for THIS project
ps aux | grep -E "mcp|uv run" | grep -v grep | grep {{ cookiecutter.project_slug }}
```

**What to look for:**
- `uv run mcp dev` - MCP Inspector process
- `python.*server/app.py` - Server process
- `streamlit run` - Admin UI process

### 2. Kill Specific Process

```bash
# Kill by PID (process ID)
kill <PID>

# Force kill if regular kill doesn't work
kill -9 <PID>
```

### 3. Kill All Project Processes

```bash
# Find and kill all at once (careful!)
ps aux | grep {{ cookiecutter.project_slug }} | grep -v grep | awk '{print $2}' | xargs kill
```

## When to Kill Processes

### MUST Kill Before:
1. **Modifying tools** - New code won't load
2. **Running tests** - Import conflicts
3. **Generating tests** - Need fresh imports
4. **Switching activities** - Clean transitions

### Safe to Keep Running:
1. **While testing same tool** - No changes
2. **Reading documentation** - No conflicts
3. **Planning changes** - Not executing

## Process Management by Activity

### Starting MCP Inspector

```bash
# 0. FIRST: Close ALL browser tabs with localhost:6274!

# 1. Check for existing processes
ps aux | grep "mcp dev" | grep -v grep

# 2. Kill if found
kill <PID>

# 3. Start fresh
uv run mcp dev server/app.py

# 4. Open in NEW browser tab (never reuse old tabs!)
```

### After Tool Changes

```bash
# 1. You MUST kill Inspector
ps aux | grep "mcp dev" | grep -v grep
kill <PID>

# 2. Restart to load new code
uv run mcp dev server/app.py
```

### Before Running Tests

```bash
# 1. Kill ALL project processes
ps aux | grep {{ cookiecutter.project_slug }} | grep -v grep
# Kill all PIDs shown

# 2. Run tests with clean slate
uv run pytest tests/
```

## Debugging Process Issues

### Problem: "Error Connecting to MCP Inspector Proxy" ⚠️

**MOST COMMON CAUSE: Old browser tabs!**
```bash
# Solution:
1. Close ALL browser tabs with localhost:6274
2. Check ALL your browsers (Chrome, Firefox, Safari, Arc)
3. Kill any Inspector processes
4. Start fresh and open NEW tab
```

### Problem: "Address already in use"

**Solution:**
```bash
# Find what's using the port
lsof -i :6274  # Inspector port
lsof -i :8501  # Streamlit port

# Kill the process
kill <PID>
```

### Problem: "Module already imported"

**Solution:**
```bash
# Python cached the old code
# Kill all Python processes for project
ps aux | grep python | grep {{ cookiecutter.project_slug }}
kill <PIDs>
```

### Problem: "Tool not found" (after adding)

**Solution:**
```bash
# Inspector hasn't reloaded
# Restart the Inspector
ps aux | grep "mcp dev"
kill <PID>
uv run mcp dev server/app.py
```

### Problem: "Changes not reflected"

**Solution:**
```bash
# Full restart sequence
# 1. Kill everything
pkill -f {{ cookiecutter.project_slug }}

# 2. Clear Python cache (optional)
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

# 3. Restart fresh
uv run mcp dev server/app.py
```

## Process Health Check

### Quick Status Check

```bash
# See all your project processes
ps aux | grep {{ cookiecutter.project_slug }} | grep -v grep

# Check specific ports
lsof -i :6274  # MCP Inspector
lsof -i :8501  # Streamlit UI
```

### Clean Slate Script

Create this helper script as `kill_all.sh`:

```bash
#!/bin/bash
echo "Killing all {{ cookiecutter.project_slug }} processes..."
ps aux | grep {{ cookiecutter.project_slug }} | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null
echo "All processes killed. Clean slate ready!"
```

Make it executable: `chmod +x kill_all.sh`
Use it: `./kill_all.sh`

## Best Practices

1. **Always check before starting**: `ps aux | grep {{ cookiecutter.project_slug }}`
2. **Kill gracefully first**: `kill <PID>` before `kill -9`
3. **Explain to user**: "Killing Inspector to load your changes"
4. **Verify kill worked**: Run ps command again
5. **Document in commands**: Add process checks to all commands

## For AI Assistants

**When helping users:**
1. ALWAYS check processes before operations
2. EXPLAIN why killing is needed
3. Be SPECIFIC about which processes
4. VERIFY the kill worked
5. HELP debug if kill fails

**Template for process management:**
```
"Let me check for running processes..."
[Run ps command]

"I see MCP Inspector is running. I need to kill it because [reason]"
[Kill the process]

"Process killed. Now starting fresh..."
[Continue with operation]
```