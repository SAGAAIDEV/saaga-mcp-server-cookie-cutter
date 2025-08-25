# Test Example Tools

This file contains test commands for verifying all example tools in the MCP server are working correctly.
Explain that you are running this tool to make sure that claude can access these tools through the mcp.stdio.json config file
by runnning ./test_mcp_with_claude.sh


## Prerequisites


## Test Script Method
Run these tools in PARALLEL with the bash tool.

Use the test script to verify individual tools:

### 1. Echo Tool
```bash
./test_mcp_with_claude.sh "Run the echo_tool with message 'Hello World'"

```

### 2. Get Time Tool
```bash
./test_mcp_with_claude.sh "Run the get_time tool to get current time"

```

### 3. Random Number Tool
```bash
./test_mcp_with_claude.sh "Generate a random number between 1 and 100"


```

### 4. Calculate Fibonacci Tool
```bash
./test_mcp_with_claude.sh "Calculate the 10th Fibonacci number"

```

### 5. Search Tool (with optional parameters)
```bash
./test_mcp_with_claude.sh "Use search_tool to search for 'test query'"

```

### 6. Elicit Example Tool
```bash
./test_mcp_with_claude.sh "Book a table for 4 people on 2025-02-14 at 7:00 PM"

```

### 7. Notification Example Tool
```bash
./test_mcp_with_claude.sh "Process data 'test-data-123' with logging"
```

### 8. Progress Example Tool
```bash
./test_mcp_with_claude.sh "Run progress_example for task_name='File Processing' with default steps"

```



## Expected Outputs

### Echo Tool
- Should return: "Echo: [your message]"

### Get Time
- Should return current time in human-readable format

### Random Number
- Should return a dictionary with the random number and range info

### Calculate Fibonacci
- Should return the calculated Fibonacci number with calculation info

### Search Tool
- Should return search results with applied filters

### Elicit Example
- Should check availability and return booking status

### Notification Example
- Should process data with logging notifications

### Progress Example
- Should execute task with progress updates for each step

## Troubleshooting

If any test fails:

1. Check MCP server is running:
   ```bash
   ps aux | grep mcp-server-reddit
   ```

2. Verify configuration:
   ```bash
   cat mcp.stdio.json
   ```

3. Check server logs for errors

4. Ensure all dependencies are installed:
   ```bash
   uv sync
   ```

5. Test with verbose output:
   ```bash
   SAAGA_LOG_LEVEL=DEBUG ./test_mcp_with_claude.sh "Run echo_tool with message 'Debug Test'"
   ```

On a sucessfull run explain that the user can now run the setup command.