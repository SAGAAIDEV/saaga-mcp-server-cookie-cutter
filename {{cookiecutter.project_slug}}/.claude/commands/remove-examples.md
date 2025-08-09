---
description: Remove example tools and tests to prepare for production development
argument-hint: "[keep-one-example?]"
allowed-tools: ["Read", "Edit", "Bash", "Grep"]
---

I'll help you remove the example tools and prepare your project for production development.

## Step 1: Analyze Current State

Let me check what example code exists:

- Checking for example_tools.py
- Checking for example tests in tests/
- Checking server/app.py for example tool registration
- Determining if you want to keep one example for reference

Keep one example: $ARGUMENTS

## Step 2: Backup Reference

**Important**: The `.reference/` directory will remain intact with all patterns!
You can always refer back to it for implementation patterns.

## Step 3: Remove Example Tools

{% raw %}
{% if 'keep' not in ARGUMENTS and 'yes' not in ARGUMENTS %}

### Removing ALL example tools:

1. Delete example_tools.py:
```bash
rm {{ cookiecutter.project_slug }}/tools/example_tools.py
```

2. Update server/app.py to remove example tool imports and registration:
- Remove: `from {{ cookiecutter.project_slug }}.tools.example_tools import example_tools, parallel_example_tools`
- Remove the registration loops for example tools

3. Create placeholder for your tools:
```python
# {{ cookiecutter.project_slug }}/tools/__init__.py
"""
Your MCP tools will go here.

To add a new tool:
1. Create a new module (e.g., my_tools.py)
2. Define async functions with ctx: Context = None parameter
3. Register them in server/app.py

See .reference/patterns/tool_patterns.py for examples.
"""
```

{% else %}

### Keeping one example for reference:

Keeping `echo_tool` as a minimal reference example while removing others:

1. Simplify example_tools.py to just one tool
2. Update server/app.py to only register the one example
3. Remove complex parallel examples

{% endif %}
{% endraw %}

## Step 4: Clean Up Tests

### Remove example-specific integration tests:

```bash
# Remove edge case tests for examples
rm tests/integration/test_mcp_edge_cases.py

# Keep the main test file but remove example-specific tests
# Will update test_mcp_integration.py to remove example references
```

### Update remaining tests:
- Remove assertions for specific example tools
- Keep the test infrastructure (create_test_session, etc.)
- Add placeholder for your own tests

## Step 5: Update Server Registration

Updating server/app.py with a clean structure for your tools:

```python
# Your tools will be registered here
custom_tools = []  # Add your tools to this list
parallel_tools = []  # Add parallel tools here

# Register custom tools
for tool_func in custom_tools:
    decorated = type_converter(tool_func)
    decorated = tool_logger(decorated, config)
    decorated = exception_handler(decorated)
    mcp_server.tool()(decorated)

# Register parallel tools
for tool_func in parallel_tools:
    decorated = parallelize(tool_func)
    decorated = type_converter(decorated)
    decorated = tool_logger(decorated, config)
    decorated = exception_handler(decorated)
    mcp_server.tool()(decorated)
```

## Step 6: Create Tool Template

Creating a template for your first tool:

```python
# {{ cookiecutter.project_slug }}/tools/my_tools.py
from typing import Dict, Any
from mcp.server.fastmcp import Context


async def my_first_tool(
    param: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Your first custom tool.
    
    Args:
        param: Input parameter
        ctx: MCP context (provided by runtime)
    
    Returns:
        Dictionary with results
    """
    # TODO: Implement your tool logic
    return {
        "status": "success",
        "input": param,
        "message": "Tool executed successfully"
    }


# Export your tools
my_tools = [my_first_tool]
```

## Step 7: Verification

Let me verify the cleanup was successful:

```bash
# Check no example imports remain
grep -r "example_tools" {{ cookiecutter.project_slug }}/ --exclude-dir=.reference

# Verify server can still start
python -c "from {{ cookiecutter.project_slug }}.server.app import app; print('✓ Server imports successfully')"
```

## ✅ Cleanup Complete!

Your project is now ready for production development:

1. **Examples removed** - No example clutter
2. **Structure preserved** - All infrastructure intact
3. **Patterns available** - Check `.reference/` anytime
4. **Ready to build** - Add your tools to `tools/` directory

## Next Steps

1. **Create your first tool**:
   ```
   /add-tool "Description of your tool"
   ```

2. **Generate tests**:
   ```
   /generate-tests your_tool_name
   ```

3. **Start development server**:
   ```
   /dev-server start
   ```

4. **Reference patterns** in `.reference/patterns/` anytime you need help

The `.reference/` directory will always be there with complete examples, even though the example code is gone!