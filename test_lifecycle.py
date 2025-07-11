#!/usr/bin/env python3
"""
Test script to understand the exact lifecycle of tool registration.
Simulates MCP server loading and tool registration to identify the real problem.
"""

print("=" * 60)
print("TOOL REGISTRATION LIFECYCLE TEST")
print("=" * 60)

# Mock decorator
def simple_decorator(func):
    """Simple decorator to track when it gets applied"""
    print(f"🎯 DECORATOR: Applied to {func.__name__}")
    def wrapper(*args, **kwargs):
        print(f"🔧 WRAPPER: Calling {func.__name__} with args={args}")
        result = func(*args, **kwargs)
        print(f"✅ WRAPPER: {func.__name__} returned: {result}")
        return result
    print(f"🎯 DECORATOR: Returning wrapper for {func.__name__}")
    return wrapper

# Mock tool function
def echo_tool(message: str) -> str:
    """Simple tool function"""
    return f"Echo: {message}"

# Mock MCP server
class MockMCPServer:
    def __init__(self):
        self.tools = {}
        print("🏗️  SERVER: MockMCPServer created")
    
    def tool(self, name: str, description: str):
        """Mock MCP tool decorator - this is what @mcp_server.tool() does"""
        print(f"📝 SERVER.tool() called with name='{name}', description='{description}'")
        
        def decorator(func):
            print(f"📝 SERVER.tool() decorator received function: {func}")
            print(f"📝 SERVER.tool() registering '{name}' -> {func}")
            self.tools[name] = {
                'function': func,
                'description': description
            }
            print(f"📝 SERVER.tool() registration complete for '{name}'")
            return func
        
        print(f"📝 SERVER.tool() returning decorator")
        return decorator
    
    def call_tool(self, name: str, *args, **kwargs):
        """Simulate calling a registered tool"""
        print(f"\n🚀 CALLING TOOL: '{name}' with args={args}")
        if name not in self.tools:
            return f"Tool '{name}' not found"
        
        tool_func = self.tools[name]['function']
        print(f"🚀 FOUND TOOL FUNCTION: {tool_func}")
        result = tool_func(*args, **kwargs)
        print(f"🚀 TOOL RESULT: {result}")
        return result

print("\n" + "─" * 40)
print("PHASE 1: Module Load Time (MCP Server Creation)")
print("─" * 40)

# Simulate module load - creating server
mcp_server = MockMCPServer()

# Simulate tools list (what we get from example_tools)
tools_list = [echo_tool]
print(f"📦 TOOLS LIST: {tools_list}")

print("\n" + "─" * 40)
print("PHASE 2: Tool Registration (Current BROKEN Approach)")
print("─" * 40)

print("\n--- Simulating Current Loop Registration ---")
for tool_func in tools_list:
    print(f"\n🔄 LOOP: Processing {tool_func.__name__}")
    
    @mcp_server.tool(
        name=tool_func.__name__,
        description=tool_func.__doc__ or f"Tool: {tool_func.__name__}"
    )
    def create_tool_wrapper(func=tool_func):
        print(f"🏭 create_tool_wrapper called with func={func.__name__}")
        
        def tool_wrapper(*args, **kwargs):
            print(f"🎭 tool_wrapper called with args={args}")
            # Apply decorator
            decorated_func = simple_decorator(func)
            result = decorated_func(*args, **kwargs)
            return f"Wrapped: {result}"
        
        print(f"🏭 create_tool_wrapper returning tool_wrapper function")
        return tool_wrapper  # ✅ FIXED: Return function, don't call it
    
    print(f"🔄 LOOP: Completed processing {tool_func.__name__}")

print(f"\n📊 REGISTERED TOOLS: {list(mcp_server.tools.keys())}")

print("\n" + "─" * 40)
print("PHASE 3: Runtime Tool Execution")
print("─" * 40)

# Test the registered tool
try:
    result = mcp_server.call_tool("echo_tool", "Hello World")
    print(f"\n🎉 FINAL RESULT: {result}")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "─" * 40)
print("PHASE 4: Demonstrating the ORIGINAL Problem")
print("─" * 40)

print("\n--- What happens with return tool_wrapper() ---")

# Create new server for broken version
mcp_server_broken = MockMCPServer()

for tool_func in tools_list:
    print(f"\n🔄 BROKEN LOOP: Processing {tool_func.__name__}")
    
    @mcp_server_broken.tool(
        name=f"broken_{tool_func.__name__}",
        description=tool_func.__doc__ or f"Tool: {tool_func.__name__}"
    )
    def create_broken_tool_wrapper(func=tool_func):
        print(f"🏭 create_broken_tool_wrapper called with func={func.__name__}")
        
        def tool_wrapper(*args, **kwargs):
            print(f"🎭 tool_wrapper called with args={args}")
            decorated_func = simple_decorator(func)
            result = decorated_func(*args, **kwargs)
            return f"Wrapped: {result}"
        
        print(f"🏭 create_broken_tool_wrapper about to CALL tool_wrapper()")
        return tool_wrapper()  # ❌ BROKEN: Calling the function immediately
    
    print(f"🔄 BROKEN LOOP: Completed processing {tool_func.__name__}")

print(f"\n📊 BROKEN REGISTERED TOOLS: {list(mcp_server_broken.tools.keys())}")
print(f"📊 BROKEN TOOL CONTENTS: {mcp_server_broken.tools}")

print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)
print("1. Tool registration happens at MODULE LOAD TIME")
print("2. The @mcp_server.tool() decorator runs immediately")
print("3. The function passed to @mcp_server.tool() gets stored")
print("4. Later, MCP calls that stored function with arguments")
print("5. Problem: return tool_wrapper() executes immediately, returns result")
print("6. Solution: return tool_wrapper (the function object)")
print("7. The elegant loop approach IS FINE - just fix the return statement")