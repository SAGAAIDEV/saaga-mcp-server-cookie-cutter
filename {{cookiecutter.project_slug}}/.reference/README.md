# Reference Patterns Directory

## ⚠️ DO NOT DELETE THIS DIRECTORY ⚠️

This `.reference/` directory contains permanent reference patterns that are used by AI assistants to help you develop MCP tools and tests. These patterns remain available even after you've removed all example code.

## Purpose

When you use commands like `/add-tool` or `/generate-tests`, the AI assistant reads these reference patterns first to ensure consistent, correct code generation that follows the established patterns of this MCP server architecture.

## Contents

### `/patterns/` - Core Implementation Patterns

- **tool_patterns.py** - All MCP tool patterns with detailed explanations
- **integration_test_patterns.py** - MCP client integration test patterns  
- **unit_test_patterns.py** - Unit test patterns for decorators
- **decorator_patterns.py** - How decorators work and chain together

### `/templates/` - Code Generation Templates

- **new_tool_template.py.jinja** - Template for generating new tools
- **integration_test_template.py.jinja** - Template for integration tests
- **unit_test_template.py.jinja** - Template for unit tests

## How It Works

1. AI assistants ALWAYS read from `.reference/` first before generating code
2. Your actual code (which may diverge over time) is analyzed second
3. The AI combines reference patterns with your current code style

## Key Patterns Explained

### MCP Tool Pattern
```python
async def tool_name(param: type, ctx: Context = None) -> ReturnType:
    """Docstring explaining the tool."""
    # Implementation
    return result
```

### Integration Test Pattern
```python
async def test_tool_name():
    session, cleanup = await create_test_session()
    try:
        result = await session.call_tool("tool_name", arguments={...})
        assert result.isError is False  # or True for error cases
    finally:
        await cleanup()
```

### Decorator Application Order
- Regular tools: `@exception_handler → @tool_logger → tool`
- Parallel tools: `@exception_handler → @tool_logger → @parallelize → tool`

## Never Modify These Files

These reference patterns are carefully crafted to work with the SAAGA decorator system and MCP protocol. Modifying them could cause AI assistants to generate incorrect code.