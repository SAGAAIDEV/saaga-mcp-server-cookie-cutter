# MCP Beginners Guide - Essential Concepts

This guide explains the minimum you need to know about MCP to use this template effectively. It focuses ONLY on what this template implements, not the entire MCP specification.

## What is MCP?

**MCP (Model Context Protocol)** is a standard way for AI assistants (like Claude) to use external tools. Without MCP, AI can only respond with text. With MCP, AI can actually DO things - run calculations, access databases, call APIs.

Think of it like this:
- **Without MCP**: "Here's how you would check the weather..."
- **With MCP**: *Actually checks the weather and returns real data*

## Core Concept: Tools

In this template, everything revolves around **tools**. A tool is just a Python function that:
1. Takes inputs (parameters)
2. Does something (calculation, API call, etc.)
3. Returns a result

### Anatomy of an MCP Tool

```python
async def get_weather(city: str, ctx: Context = None) -> dict:
    """Get current weather for a city."""
    # Your code here
    return {"temp": 72, "conditions": "sunny"}
```

**Key Requirements**:
- `async def` - Must be asynchronous
- Type hints - `city: str` tells MCP what type to expect
- Docstring - Describes the tool for AI and users
- JSON return - Must return data MCP can serialize

## How MCP Communication Works

```
AI Assistant ←→ MCP Client ←→ Your Server ←→ Your Tools
```

1. **AI decides** to use a tool
2. **MCP Client** sends request to your server
3. **Your server** runs the tool
4. **Tool returns** result
5. **AI uses** the result in its response

## The Context Object

The `Context` parameter is optional but powerful. It lets your tool:

```python
async def process_data(data: str, ctx: Context = None) -> str:
    if ctx:
        ctx.info("Starting processing...")  # Logs to AI/user
        ctx.report_progress(50, 100)        # Shows progress
    
    result = do_processing(data)
    
    if ctx:
        ctx.info("Processing complete!")
    
    return result
```

## Transport: How AI Connects to Your Server

This template supports two ways:

### 1. STDIO (Standard Input/Output)
- Used by: Claude Desktop app
- How: Through command line pipes
- When: Desktop AI applications

### 2. SSE (Server-Sent Events)
- Used by: Web applications
- How: Through HTTP connections
- When: Browser-based AI interfaces

## The SAAGA Difference

This template adds "decorators" that automatically:
1. **Convert types** - MCP sends strings, we convert to correct types
2. **Log everything** - Every tool call is recorded
3. **Handle errors** - Errors are caught and reported properly
4. **Enable parallelization** - Some tools can process batches

You don't need to understand decorators deeply - they just make your tools more robust.

## Practical Example: Your First Tool

Let's say you want a tool that calculates sales tax:

```python
async def calculate_tax(amount: float, rate: float = 0.08, ctx: Context = None) -> dict:
    """Calculate sales tax for a given amount.
    
    Args:
        amount: The purchase amount
        rate: Tax rate (default 8%)
    
    Returns:
        Dictionary with amount, tax, and total
    """
    tax = amount * rate
    total = amount + tax
    
    if ctx:
        ctx.info(f"Calculated tax for ${amount:.2f} at {rate*100:.1f}%")
    
    return {
        "amount": amount,
        "tax": round(tax, 2),
        "total": round(total, 2),
        "rate_percent": rate * 100
    }
```

## Common Patterns

### Pattern 1: Simple Query
```python
async def get_info(query: str, ctx: Context = None) -> str:
    # Fetch and return information
    return fetch_from_database(query)
```

### Pattern 2: Data Processing
```python
async def process_items(items: list, ctx: Context = None) -> dict:
    results = []
    for i, item in enumerate(items):
        if ctx:
            ctx.report_progress(i, len(items))
        results.append(process_item(item))
    return {"processed": results, "count": len(results)}
```

### Pattern 3: External API Call
```python
async def call_api(endpoint: str, ctx: Context = None) -> dict:
    if ctx:
        ctx.info(f"Calling API: {endpoint}")
    
    response = await make_api_call(endpoint)
    
    if ctx:
        ctx.info(f"API returned status: {response.status}")
    
    return response.json()
```

## What You DON'T Need to Know

For basic usage, you can ignore:
- Resources (file serving)
- Prompts (template management)
- Completions (auto-complete)
- Advanced transports (WebSocket, StreamableHTTP)
- Authentication (OAuth)
- The full MCP specification

## Quick Checklist

When creating a tool, ask yourself:
- [ ] Is it an `async` function?
- [ ] Does it have type hints for all parameters?
- [ ] Does it have a docstring explaining what it does?
- [ ] Does it return JSON-serializable data?
- [ ] Does it include `ctx: Context = None` if it needs logging?

## Testing Your Tools

1. **Start the server**:
   ```bash
   mcp dev your_project/server/app.py
   ```

2. **Open MCP Inspector**: http://localhost:6274

3. **Test your tool**:
   - Select your tool from the list
   - Enter test parameters
   - Click "Run"
   - Check the response

## Next Steps

Now that you understand the basics:
1. Look at the example tools in `tools/example_tools.py`
2. Try modifying an example tool
3. Create your own simple tool
4. Test it with MCP Inspector
5. Integrate with Claude Desktop

Remember: Start simple, test often, and build complexity gradually!