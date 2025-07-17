# MCP Inspector Test Guide

This guide provides manual test examples for all tools in the SAAGA MCP Server template when using the MCP Inspector.

## Prerequisites

1. Generate a project from this template with example tools enabled:
   ```bash
   cookiecutter . --no-input \
       project_name="Test Project" \
       include_example_tools="yes" \
       include_parallel_example="yes"
   ```

2. Set up and launch the MCP Inspector:
   ```bash
   cd test_project
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   mcp dev test_project/server/app.py
   ```

3. Open the inspector at: http://localhost:5173

## Regular Tools (Form Mode)

These tools work with the standard form interface in MCP Inspector.

### 1. echo_tool

**Description**: Echoes back the input message with a prefix.

**Test Examples**:
```
message: "Hello, MCP!"
Expected: "Echo: Hello, MCP!"

message: "Testing SAAGA decorators"
Expected: "Echo: Testing SAAGA decorators"
```

### 2. get_time

**Description**: Returns the current time in human-readable format.

**Test Examples**:
- Click "Run Tool" (no parameters needed)
- Expected: Current time like "2025-07-17 10:30:45"

### 3. random_number

**Description**: Generates a random number within a specified range.

**Test Examples**:
```
min_value: 1
max_value: 10
Expected: {"number": 7, "min": 1, "max": 10}

min_value: 100
max_value: 200
Expected: {"number": 147, "min": 100, "max": 200}
```

### 4. calculate_fibonacci

**Description**: Calculates the nth Fibonacci number.

**Test Examples**:
```
n: 5
Expected: {"position": 5, "value": 5, "calculation_time": 0.000123}

n: 10
Expected: {"position": 10, "value": 55, "calculation_time": 0.000234}

n: 20
Expected: {"position": 20, "value": 6765, "calculation_time": 0.000345}
```

## Parallel Tools (JSON Mode Required)

⚠️ **Important**: The MCP Inspector's form interface doesn't properly handle `List[Dict]` parameters. You must switch to JSON mode for these tools.

### How to Use JSON Mode:
1. Select the parallel tool (process_batch_data or simulate_heavy_computation)
2. Click "Switch to JSON" button
3. Replace the contents with the JSON examples below
4. Click "Run Tool"

### 5. process_batch_data

**Description**: Processes multiple batches of data in parallel.

**Test Examples**:

Example 1 - Mixed operations:
```json
[
  {"items": ["hello", "world"], "operation": "upper"},
  {"items": ["FOO", "BAR"], "operation": "lower"},
  {"items": ["test"], "operation": "reverse"}
]
```
Expected output:
```json
[
  {"processed": ["HELLO", "WORLD"], "count": 2, "operation": "upper"},
  {"processed": ["foo", "bar"], "count": 2, "operation": "lower"},
  {"processed": ["tset"], "count": 1, "operation": "reverse"}
]
```

Example 2 - Large batch:
```json
[
  {"items": ["apple", "banana", "cherry"], "operation": "upper"},
  {"items": ["DOG", "CAT", "BIRD"], "operation": "lower"},
  {"items": ["hello", "world"], "operation": "reverse"},
  {"items": ["TEST", "DATA"], "operation": "upper"}
]
```

### 6. simulate_heavy_computation

**Description**: Simulates parallel heavy computation tasks with varying complexity.

**Test Examples**:

Example 1 - Light computations:
```json
[
  {"complexity": 1},
  {"complexity": 2},
  {"complexity": 3}
]
```
Expected: Three results with increasing computation times

Example 2 - Mixed complexity:
```json
[
  {"complexity": 5},
  {"complexity": 1},
  {"complexity": 10},
  {"complexity": 3}
]
```
Expected: Four results with computation times proportional to complexity

## Troubleshooting

### "Add Item" doesn't work for parallel tools
This is a known limitation of the MCP Inspector. Always use JSON mode for parallel tools.

### JSON parse errors
Ensure your JSON is valid:
- Use double quotes for strings
- No trailing commas
- Proper array/object structure

### Tool not appearing
1. Check that the server started successfully
2. Refresh the inspector page
3. Check the terminal for any error messages

## Testing Error Handling

To test the SAAGA exception handling decorator:

1. **Invalid input types**:
   - For `calculate_fibonacci`, try: `n: -5` (negative number)
   - For `random_number`, try: `min_value: 100, max_value: 1` (min > max)

2. **Empty inputs**:
   - For parallel tools, try: `[]` (empty array)

3. **Invalid operations**:
   - For `process_batch_data`, try: `{"items": ["test"], "operation": "invalid"}`

## Viewing Logs

The SAAGA decorators automatically log all tool executions to:
- **macOS**: `~/Library/Logs/mcp-servers/{project_name}.log`
- **Windows**: `%LOCALAPPDATA%\{project_name}\logs\{project_name}.log`
- **Linux**: `~/.local/state/{project_name}/logs/{project_name}.log`

SQLite logs are stored in:
- **macOS**: `~/Library/Application Support/{project_name}/tool_logs.db`
- **Windows**: `%LOCALAPPDATA%\{project_name}\tool_logs.db`
- **Linux**: `~/.local/share/{project_name}/tool_logs.db`