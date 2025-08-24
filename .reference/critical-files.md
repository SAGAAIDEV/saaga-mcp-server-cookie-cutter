# Critical Files - Do Not Break

This document lists files and patterns that are critical to the template's functionality. Breaking these will cause generated MCP servers to fail.

## Critical File Map

### 1. Decorator System Files

**Location**: `{{cookiecutter.project_slug}}/decorators/`

**Critical Files**:
- `type_converter.py` - Converts MCP string params to correct types
- `tool_logger.py` - Logs all tool executions with correlation IDs
- `exception_handler.py` - Ensures MCP-compatible error handling
- `parallelize.py` - Enables batch processing

**Why Critical**: 
- MCP sends all parameters as strings
- Without type_converter, tools break on non-string types
- Without proper exception handling, MCP client disconnects
- Decorator order in app.py MUST be preserved

**What Not to Change**:
```python
# This order is SACRED - do not change!
tool = type_converter(tool)
tool = tool_logger(tool) 
tool = exception_handler(tool)
```

### 2. Context Parameter Pattern

**Location**: All files in `{{cookiecutter.project_slug}}/tools/`

**Critical Pattern**:
```python
async def any_tool(param1: str, param2: int, ctx: Context = None) -> dict:
    """Every tool MUST have ctx: Context = None as last parameter"""
    pass
```

**Why Critical**:
- Correlation IDs are passed via Context
- OAuth tokens are passed via Context._meta
- Removing Context breaks request tracking

**What Not to Change**:
- The parameter name must be `ctx`
- Type must be `Context`
- Default must be `None`
- Must be the last parameter

### 3. Log System Package

**Location**: `{{cookiecutter.project_slug}}/log_system/`

**Critical Constraint**: 
- Package MUST be named `log_system` not `logging`

**Why Critical**:
- `logging` conflicts with Python's standard library
- Causes circular imports and runtime errors
- All imports throughout template use `log_system`

**What Not to Change**:
```python
# NEVER change this package name
from log_system.unified_logger import UnifiedLogger  # ✓ Correct
from logging.unified_logger import UnifiedLogger     # ✗ Will break
```

### 4. Server Initialization

**Location**: `{{cookiecutter.project_slug}}/server/app.py`

**Critical Code**:
```python
# Decorator application order
for tool_func in tool_functions:
    # This exact order is required
    tool_func = type_converter(tool_func)
    if needs_parallel:
        tool_func = parallelize(tool_func)
    tool_func = tool_logger(tool_func)
    tool_func = exception_handler(tool_func)
```

**Why Critical**:
- Type conversion must happen first
- Exception handler must be outermost
- Logger needs converted parameters

### 5. Reference Documentation

**Location**: `{{cookiecutter.project_slug}}/.reference/`

**Critical Files**:
- `saaga-mcp-integration.md` - Explains decorator chain
- `patterns/tool_patterns.py` - Shows correct tool structure
- `patterns/decorator_patterns.py` - Explains application order

**Why Critical**:
- AI assistants rely on these for code generation
- Removing breaks `/add-tool` and other commands
- Documents the "why" behind critical patterns

### 6. Test Infrastructure

**Location**: `{{cookiecutter.project_slug}}/tests/`

**Critical Files**:
- `conftest.py` - Sets up MCP test clients
- `integration/conftest.py` - Parameterized transport fixtures

**Critical Pattern**:
```python
@pytest.fixture(params=["stdio", "sse"])
def transport(request):
    """Tests MUST run against multiple transports"""
    return request.param
```

**Why Critical**:
- Ensures compatibility with all MCP transports
- Catches transport-specific bugs
- Required for production deployments

## Dependency Chains

### Chain 1: MCP Tool Execution
```
MCP Client → FastMCP → exception_handler → tool_logger → type_converter → Tool Function
```
Break any link = broken server

### Chain 2: Correlation Tracking
```
Client Context → ctx parameter → tool_logger → SQLite destination
```
Break any link = no request tracking

### Chain 3: OAuth Passthrough
```
Client _meta → Context → oauth_passthrough decorator → Tool validation
```
Break any link = OAuth fails

## Testing Critical Paths

After any changes, verify:

```bash
# 1. Generate a test server
cookiecutter . --no-input -o test_output

# 2. Run critical tests
cd test_output/my_mcp_server
pytest tests/integration/test_example_tools_integration.py -v

# 3. Test correlation IDs
python test_correlation_id_integration.py

# 4. Test MCP connection
python -m my_mcp_server.server.app --help
```

## Recovery Procedures

If you accidentally break a critical file:

1. **Check Git**: `git status` and `git diff` to see changes
2. **Revert**: `git checkout -- <critical_file>`
3. **Test**: Run the critical path tests above
4. **Document**: If the change was intentional, update this document

## Never Do This

1. ❌ Rename `log_system` package to `logging`
2. ❌ Remove `ctx: Context = None` from tools
3. ❌ Change decorator application order
4. ❌ Delete `.reference/` directory
5. ❌ Use `**kwargs` in tool signatures
6. ❌ Make tools synchronous (remove `async`)
7. ❌ Remove type hints from tool parameters

## If You Must Change Critical Files

1. Document the change in this file
2. Update all dependent files
3. Test with multiple configurations
4. Update `.reference/` documentation
5. Consider if it needs a major version bump
6. Provide migration guide for existing users