#!/usr/bin/env python3
"""
Test script to demonstrate decorator functionality can work with simpler registration pattern.
This is NOT MCP-related - just pure Python to prove the concept.
"""

from typing import Optional, Any
import json

# Mock SAAGA decorators (simplified versions)
def exception_handler(func):
    """Mock exception handler decorator"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print(f"✅ exception_handler: {func.__name__} succeeded")
            return result
        except Exception as e:
            print(f"❌ exception_handler: {func.__name__} failed with {e}")
            return f"Error: {str(e)}"
    return wrapper

def tool_logger(func, config=None):
    """Mock tool logger decorator"""
    def wrapper(*args, **kwargs):
        print(f"📝 tool_logger: Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"📝 tool_logger: {func.__name__} returned: {result}")
        return result
    return wrapper

def parallelize(func):
    """Mock parallelize decorator"""
    def wrapper(*args, **kwargs):
        print(f"⚡ parallelize: Running {func.__name__} in parallel mode")
        result = func(*args, **kwargs)
        print(f"⚡ parallelize: {func.__name__} completed")
        return result
    return wrapper

# Mock TextContent class
class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text
    
    def __str__(self):
        return f"TextContent(type='{self.type}', text='{self.text}')"

# Mock config object
class Config:
    pass

config = Config()

# Example tool functions (like those in our cookiecutter)
def echo_tool(message: str) -> str:
    """Simple echo function"""
    return f"Echo: {message}"

def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """Generate a random number"""
    import random
    return f"Random number: {random.randint(min_val, max_val)}"

def process_batch_data(data: str) -> dict:
    """Process batch data (parallel tool example)"""
    return {"processed": True, "data": data, "length": len(data)}

# Mock server class to simulate MCP registration
class MockMCPServer:
    def __init__(self):
        self.tools = {}
    
    def tool(self, name: str, description: str):
        """Mock MCP tool decorator"""
        def decorator(func):
            print(f"🔧 Registering tool: {name}")
            self.tools[name] = {
                'function': func,
                'description': description
            }
            return func
        return decorator
    
    def call_tool(self, name: str, *args, **kwargs):
        """Simulate calling a registered tool"""
        if name not in self.tools:
            return f"Tool '{name}' not found"
        
        try:
            result = self.tools[name]['function'](*args, **kwargs)
            return result
        except Exception as e:
            return f"Tool execution failed: {e}"

# Test 1: BROKEN APPROACH (Current Implementation)
print("=" * 60)
print("TEST 1: BROKEN APPROACH (Current Implementation)")
print("=" * 60)

server_broken = MockMCPServer()
tools_list = [echo_tool, random_number]

print("\n--- Simulating Broken Registration Pattern ---")
for tool_func in tools_list:
    @server_broken.tool(
        name=tool_func.__name__,
        description=tool_func.__doc__ or f"Tool: {tool_func.__name__}"
    )
    def create_tool_wrapper(func=tool_func):  # Variable capture issue
        def tool_wrapper(*args, **kwargs):
            # Apply SAAGA decorators
            decorated_func = exception_handler(tool_logger(func, config))
            result = decorated_func(*args, **kwargs)
            
            # Convert to TextContent
            if isinstance(result, str):
                return TextContent(type="text", text=result)
            elif isinstance(result, dict):
                return TextContent(type="text", text=json.dumps(result))
            else:
                return TextContent(type="text", text=str(result))
        
        return tool_wrapper()  # ❌ BROKEN: Calling instead of returning

print(f"\nRegistered tools: {list(server_broken.tools.keys())}")

print("\n--- Testing Broken Tools ---")
try:
    result = server_broken.call_tool("echo_tool", "Hello World")
    print(f"echo_tool result: {result}")
except Exception as e:
    print(f"❌ echo_tool failed: {e}")

try:
    result = server_broken.call_tool("random_number", 1, 10)
    print(f"random_number result: {result}")
except Exception as e:
    print(f"❌ random_number failed: {e}")

# Test 2: FIXED APPROACH (Simple Registration with Decorators)
print("\n" + "=" * 60)
print("TEST 2: FIXED APPROACH (Simple Registration with Decorators)")
print("=" * 60)

server_fixed = MockMCPServer()

print("\n--- Registering Tools with Simple Pattern + Decorators ---")

# Register echo tool
@server_fixed.tool(
    name="echo_tool",
    description="Echo back the input message with SAAGA decorators"
)
def echo_tool_wrapper(message: str) -> TextContent:
    """MCP wrapper that applies SAAGA decorators"""
    # Apply SAAGA decorator chain
    decorated_func = exception_handler(tool_logger(echo_tool, config))
    result = decorated_func(message)
    
    # Convert to TextContent
    return TextContent(type="text", text=result)

# Register random number tool
@server_fixed.tool(
    name="random_number",
    description="Generate random number with SAAGA decorators"
)
def random_number_wrapper(min_val: int = 1, max_val: int = 100) -> TextContent:
    """MCP wrapper that applies SAAGA decorators"""
    # Apply SAAGA decorator chain
    decorated_func = exception_handler(tool_logger(random_number, config))
    result = decorated_func(min_val, max_val)
    
    # Convert to TextContent
    return TextContent(type="text", text=result)

# Register parallel tool
@server_fixed.tool(
    name="process_batch_data",
    description="Process batch data with parallel SAAGA decorators"
)
def process_batch_data_wrapper(data: str) -> TextContent:
    """MCP wrapper that applies SAAGA decorators with parallelization"""
    # Apply SAAGA decorator chain: exception_handler → tool_logger → parallelize
    decorated_func = exception_handler(tool_logger(parallelize(process_batch_data), config))
    result = decorated_func(data)
    
    # Convert to TextContent
    if isinstance(result, dict):
        return TextContent(type="text", text=json.dumps(result, indent=2))
    else:
        return TextContent(type="text", text=str(result))

print(f"\nRegistered tools: {list(server_fixed.tools.keys())}")

print("\n--- Testing Fixed Tools ---")
try:
    result = server_fixed.call_tool("echo_tool", "Hello World")
    print(f"✅ echo_tool result: {result}")
except Exception as e:
    print(f"❌ echo_tool failed: {e}")

try:
    result = server_fixed.call_tool("random_number", 1, 10)
    print(f"✅ random_number result: {result}")
except Exception as e:
    print(f"❌ random_number failed: {e}")

try:
    result = server_fixed.call_tool("process_batch_data", "test data")
    print(f"✅ process_batch_data result: {result}")
except Exception as e:
    print(f"❌ process_batch_data failed: {e}")

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("✅ SAAGA decorators CAN work with the simple registration pattern")
print("✅ The reference cookiecutter approach is compatible with decorators")
print("✅ We just need to apply decorators inside individual wrapper functions")
print("❌ The loop-based approach has fundamental Python issues")
print("❌ The 'return tool_wrapper()' pattern breaks MCP registration")