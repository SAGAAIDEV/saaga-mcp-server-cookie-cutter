---
description: Test MCP endpoints using Claude subprocess with real data
argument-hint: "[TOOL-NAME] [ADDITIONAL-PARAMS]"
allowed-tools: ["Bash"]
---

I'll test the MCP tool "$ARGUMENTS" using Claude subprocess.

## Preparing Test Command

The test will use the following Claude subprocess command:

```bash
test_mcp_with_claude.sh "<Prompt that explains what tool to run.>" 
```



## Next Steps

Use the bash to call the test_mcp_with_claude script and pass in instructions of how to use the tool that was just made.

After the test completes, I'll:
1. Analyze the output for correctness, the tool that was made, should run and return relevant information.
2. Check if the tool handled parameters properly
3. Verify the response format matches expectations
4. Document any issues or unexpected behaviors

You can also provide specific test scenarios or parameters to test edge cases.