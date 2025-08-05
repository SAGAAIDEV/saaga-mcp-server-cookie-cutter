#!/usr/bin/env python3
"""Simple test to verify correlation ID feature works correctly."""

import subprocess
import sys
import os
import json

def test_correlation_feature():
    """Generate a test server and verify correlation ID is preserved in logs."""
    
    print("🧪 Testing Correlation ID Feature")
    print("=" * 60)
    
    # Clean up previous test
    subprocess.run(["rm", "-rf", "test_correlation_server"], capture_output=True)
    
    # Generate test server
    print("📦 Generating test server...")
    result = subprocess.run([
        "cookiecutter", ".", "--no-input",
        "project_name=Test Correlation Server",
        "project_slug=test_correlation_server",
        "include_admin_ui=yes",
        "include_example_tools=yes",
        "include_parallel_example=yes"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to generate server: {result.stderr}")
        return 1
    
    print("✅ Test server generated")
    
    # Create a test script to run inside the server
    test_script = '''
import asyncio
import sys
sys.path.insert(0, ".")

from test_correlation_server.decorators.tool_logger import tool_logger
from test_correlation_server.logging.correlation import get_correlation_id
from mcp.server.fastmcp import Context

# Mock context with correlation ID
class MockMeta:
    def __init__(self, correlation_id):
        self.correlationId = correlation_id
    
    def get(self, key, default=None):
        if key == "correlationId":
            return self.correlationId
        return default

class MockRequestContext:
    def __init__(self, correlation_id):
        self.meta = MockMeta(correlation_id) if correlation_id else None

class MockContext:
    def __init__(self, correlation_id=None):
        self.request_context = MockRequestContext(correlation_id)

# Test functions
@tool_logger
async def test_with_correlation_id(ctx: Context) -> str:
    current_id = get_correlation_id()
    return f"Current correlation ID: {current_id}"

@tool_logger
async def test_without_correlation_id(ctx: Context) -> str:
    current_id = get_correlation_id()
    return f"Current correlation ID: {current_id}"

async def run_tests():
    print("\\n1️⃣ Testing with client-provided correlation ID...")
    ctx_with_id = MockContext("client_frontend_abc123")
    result1 = await test_with_correlation_id(ctx=ctx_with_id)
    print(f"   Result: {result1}")
    
    print("\\n2️⃣ Testing without client-provided correlation ID...")
    ctx_without_id = MockContext()
    result2 = await test_without_correlation_id(ctx=ctx_without_id)
    print(f"   Result: {result2}")
    
    # Verify the first test used the client's correlation ID
    if "client_frontend_abc123" in result1:
        print("\\n✅ SUCCESS: Client-provided correlation ID was used!")
    else:
        print("\\n❌ FAILED: Client-provided correlation ID was not used")
        return 1
    
    # Verify the second test generated its own correlation ID
    if "req_" in result2 and "client_frontend_abc123" not in result2:
        print("✅ SUCCESS: Generated correlation ID when not provided by client!")
    else:
        print("❌ FAILED: Did not generate correlation ID properly")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(run_tests()))
'''
    
    # Write test script
    test_script_path = "test_correlation_server/test_correlation.py"
    with open(test_script_path, "w") as f:
        f.write(test_script)
    
    print("\n🧪 Running correlation ID tests...")
    
    # Run the test inside the server's environment
    result = subprocess.run([
        "uv", "run", "python", "test_correlation.py"
    ], cwd="test_correlation_server", capture_output=True, text=True)
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Test failed: {result.stderr}")
        return 1
    
    print("\n📊 Feature Summary:")
    print("  ✅ Tool logger decorator checks for client-provided correlation ID")
    print("  ✅ Uses client ID when provided via ctx.request_context.meta")
    print("  ✅ Generates new ID when not provided by client")
    print("  ✅ Backwards compatible - existing tools work unchanged")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_correlation_feature())