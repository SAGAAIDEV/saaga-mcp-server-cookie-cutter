---
description: Design and implement a new MCP tool based on your requirements by studying existing patterns
argument-hint: "[brief-description-of-tool]"
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

I'll help you design and implement a new MCP tool. Let me start by understanding the existing patterns in this codebase.

## Step 1: Study Reference Patterns

First, let me examine the canonical patterns that this project uses:

Reading .reference/patterns/tool_patterns.py to understand the correct tool structure...
Reading .reference/patterns/decorator_patterns.py to understand how decorators are applied...

## Step 2: Understand Your Requirements

Based on your request: "$ARGUMENTS"

Let me gather more context:
1. What parameters does this tool need?
2. What should it return?
3. Does it need to process items in parallel?
4. What validation is required?

## Step 3: Analyze Current Codebase Structure

Let me check your current project structure to determine where to place the new tool:

- Checking if example_tools.py exists (for reference)
- Looking for existing tool modules in {{ cookiecutter.project_slug }}/tools/
- Checking server/app.py to see how tools are registered

## Step 4: Design the Tool

Based on the patterns and your requirements, here's the tool design:

### Tool Signature
Following the pattern from .reference/patterns/tool_patterns.py:
- Must be an async function
- Must include `ctx: Context = None` as the last parameter
- Must have type hints for all parameters
- Must have a comprehensive docstring

### Implementation Plan
1. Create a new module if needed (not in example_tools.py)
2. Implement the tool following the exact patterns
3. Add proper error handling and validation
4. Register it in server/app.py

## Step 5: Implement the Tool

Creating the tool implementation following the established patterns...

[The tool will be created in an appropriate module with full implementation]

## Step 6: Register the Tool

Updating server/app.py to register the new tool with appropriate decorators:
- For regular tools: @exception_handler → @tool_logger
- For parallel tools: @exception_handler → @tool_logger → @parallelize

## Step 7: Next Steps

Tool created! Here's what to do next:

1. **Generate tests**: Use `/generate-tests [tool_name]` to create integration tests
2. **Test with Inspector**: Use `/dev-server start` then test in MCP Inspector
3. **Run tests**: `pytest tests/integration/test_[your_tool].py`

The tool follows all the patterns from .reference/ and is ready for testing.