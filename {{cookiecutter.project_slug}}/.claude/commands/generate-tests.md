---
description: Generate comprehensive unit and integration tests for MCP tools by studying test patterns
argument-hint: "[tool-name-or-module]"
allowed-tools: ["Read", "Write", "Grep", "Glob"]
---

I'll generate comprehensive tests for your MCP tool by following the established test patterns.

## Step 1: Study Test Patterns

First, let me review the canonical test patterns:

Reading .reference/patterns/integration_test_patterns.py for MCP client test patterns...
Reading .reference/patterns/unit_test_patterns.py for unit test patterns...

Key patterns I'll follow:
- Integration tests use `create_test_session()` for MCP client
- Always use try/finally with cleanup()
- Check `result.isError` based on expected behavior
- Test both success and error cases

## Step 2: Analyze the Tool to Test

Looking for the tool: "$ARGUMENTS"

Reading the tool implementation to understand:
- Parameters (required vs optional)
- Return type
- Error conditions
- Validation logic
- Whether it's a parallel tool

## Step 3: Generate Integration Tests

Creating comprehensive integration tests following the pattern from .reference/patterns/integration_test_patterns.py:

### Test Cases to Generate:
1. **Successful execution** - Happy path with valid inputs
2. **Parameter conversion** - Test string-to-type conversion
3. **Error handling** - Invalid inputs that raise exceptions
4. **Missing parameters** - Required parameters not provided
5. **Edge cases** - Boundary conditions, empty inputs, etc.

### Critical Test Pattern:
```python
async def test_[tool_name]_[scenario]():
    session, cleanup = await create_test_session()
    try:
        result = await session.call_tool("[tool_name]", arguments={...})
        # Assertions based on expected behavior
        assert result.isError is False  # or True for errors
    finally:
        await cleanup()
```

## Step 4: Generate Unit Tests (if applicable)

If testing decorator behavior or specific functions:

Following patterns from .reference/patterns/unit_test_patterns.py:
- Test signature preservation
- Test decorator chaining
- Use mocks for external dependencies

## Step 5: Create Test Files

Creating test file(s):
- Integration: tests/integration/test_[module_name].py
- Unit (if needed): tests/unit/test_[module_name].py

Each test includes:
- Clear docstrings explaining what's being tested
- Proper assertions with helpful failure messages
- Coverage of success and failure paths

## Step 6: Test Execution Instructions

To run your new tests:

```bash
# Run specific test file
pytest tests/integration/test_[your_module].py -v

# Run with coverage
pytest tests/integration/test_[your_module].py --cov=[module_name]

# Run specific test
pytest tests/integration/test_[your_module].py::TestClassName::test_method_name
```

## Important Testing Notes

Based on the patterns in .reference/:
- When exceptions are raised in tools, `result.isError` will be `True`
- MCP sends all parameters as strings - test type conversion
- Parallel tools expect `kwargs_list` parameter
- Always extract content with helper methods, don't assume structure

Tests have been generated following the exact patterns from your .reference/ directory!