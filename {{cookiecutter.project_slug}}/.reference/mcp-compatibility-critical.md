# MCP COMPATIBILITY: CRITICAL RULES FOR TOOL PARAMETERS

## ⚠️ NEVER USE Optional[...] - IT BREAKS MCP CLIENTS

Some MCP clients fail when tools use `Optional[...]` parameter types. The solution is simple: use concrete types with sensible defaults.

### ❌ WRONG - Breaks Some MCP Clients
```python
from typing import Optional, List

async def my_tool(
    directories: Optional[List[str]] = None,  # ❌ BREAKS
    max_tokens: Optional[int] = None,         # ❌ BREAKS  
    branch: Optional[str] = None,             # ❌ BREAKS
    include_hidden: Optional[bool] = None,    # ❌ BREAKS
    ctx: Context = None
) -> dict:
    ...
```

### ✅ CORRECT - Works With ALL MCP Clients
```python
async def my_tool(
    directories: List[str] = [],      # ✅ Empty list default
    max_tokens: int = 20000,          # ✅ Sensible numeric default
    branch: str = "",                 # ✅ Empty string default
    include_hidden: bool = False,     # ✅ Boolean default
    ctx: Context = None
) -> dict:
    # Convert empty values to None internally if needed
    directories = directories if directories else None
    branch = branch or None
    ...
```

## The Rule Is Simple

**NEVER use `Optional[T]` for ANY parameter type.**

Instead:
- `List[str] = []` instead of `Optional[List[str]]`
- `str = ""` instead of `Optional[str]`
- `int = 0` or `int = -1` instead of `Optional[int]`
- `bool = False` instead of `Optional[bool]`

## Why This Matters

The MCP protocol and some clients have validation issues with Optional parameters. By using concrete types with defaults, your tools will work with ALL MCP clients.

## Remember

This is NOT a bug in your server - it's a client compatibility issue. Follow this pattern and your tools will work everywhere.