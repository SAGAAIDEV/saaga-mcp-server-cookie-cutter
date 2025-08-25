{% if cookiecutter.include_oauth_backend == "yes" -%}
#!/usr/bin/env python
"""
Test OAuth Backend with Real HTTP Calls

This script demonstrates the OAuth backend integration with actual HTTP calls
to a mock backend server. You'll see real HTTP requests happening!

Usage:
    # Install pytest-httpserver first
    pip install pytest-httpserver
    
    # Then run this script
    python test_oauth_backend_with_real_http.py
"""

import os
import sys
import asyncio
import subprocess
import time
import signal
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from tests.helpers.mock_oauth_backend import start_mock_backend


def test_with_real_http():
    """Test OAuth backend with real HTTP calls to mock server."""
    
    print("\n" + "="*70)
    print("🧪 OAuth Backend Test with Real HTTP Calls")
    print("="*70)
    print("\nThis test will:")
    print("1. Start a real mock HTTP server on localhost")
    print("2. Configure the MCP server to use it (no mock mode!)")
    print("3. Make real HTTP calls from the OAuth backend decorator")
    print("4. You'll see the actual HTTP traffic!\n")
    
    # Start the mock backend server
    with start_mock_backend() as backend_url:
        print(f"✅ Mock backend server started at: {backend_url}")
        
        # Set environment variables for the MCP server
        env = os.environ.copy()
        env["OAUTH_BACKEND_URL"] = backend_url
        env["OAUTH_BACKEND_MOCK_MODE"] = "no"  # IMPORTANT: Real HTTP mode!
        
        print(f"\n📝 Configuration:")
        print(f"   OAUTH_BACKEND_URL = {backend_url}")
        print(f"   OAUTH_BACKEND_MOCK_MODE = no (real HTTP calls!)")
        
        # Start the MCP server in a subprocess
        print(f"\n🚀 Starting MCP server with Streamable HTTP transport...")
        server_process = subprocess.Popen(
            ["python", "-m", "{{ cookiecutter.project_slug }}.server.app", 
             "--transport", "streamable-http", "--port", "3001"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Give the server time to start
        time.sleep(2)
        
        print(f"✅ MCP server started on http://localhost:3001/mcp")
        
        print("\n" + "-"*70)
        print("📋 Test Instructions:")
        print("-"*70)
        print("\n1. The mock backend is running and waiting for requests")
        print("2. The MCP server is configured to use the real backend URL")
        print("3. Now you can test with a client!\n")
        
        print("Option A: Use curl to test directly:")
        print("-"*40)
        print("""
curl -X POST http://localhost:3001/mcp \\
  -H "Content-Type: application/json" \\
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_reddit_user",
      "arguments": {},
      "_meta": {
        "userId": "test_user_123",
        "userToken": "my_temp_token_abc123",
        "providerId": "reddit"
      }
    },
    "id": 1
  }'
""")
        
        print("\nOption B: Use the MCP Inspector or your client:")
        print("-"*40)
        print("1. Connect to: http://localhost:3001/mcp")
        print("2. Call the 'get_reddit_user' tool")
        print("3. Pass the _meta parameters:")
        print('   - userId: "test_user_123"')
        print('   - userToken: "my_temp_token_abc123"')
        print('   - providerId: "reddit"')
        
        print("\n" + "-"*70)
        print("🔍 What to Look For:")
        print("-"*70)
        print("\n1. Check the console output - you'll see:")
        print("   - The OAuth backend decorator extracting parameters")
        print("   - The HTTP call to the mock backend")
        print("   - The mock backend receiving and processing the request")
        print("   - The access token being returned")
        print("\n2. The flow is:")
        print("   Client → MCP Server → OAuth Backend Decorator → HTTP → Mock Backend")
        print("   Mock Backend → Access Token → OAuth Backend Decorator → Tool → Client")
        
        print("\n" + "="*70)
        print("Press Ctrl+C to stop both servers")
        print("="*70 + "\n")
        
        try:
            # Keep running until interrupted
            while True:
                # Check if server is still running
                if server_process.poll() is not None:
                    print("\n⚠️ MCP server stopped unexpectedly")
                    break
                    
                # Print any server output
                line = server_process.stdout.readline()
                if line:
                    print(f"[MCP Server] {line.strip()}")
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down servers...")
            server_process.terminate()
            server_process.wait()
            print("✅ Servers stopped")


def run_standalone_mock_backend():
    """Run just the mock backend server standalone."""
    print("\n" + "="*70)
    print("🚀 Starting Standalone Mock OAuth Backend")
    print("="*70)
    print("\nThis will run just the mock backend server.")
    print("You can then configure your MCP server to use it.\n")
    
    from tests.helpers.mock_oauth_backend import create_standalone_mock_server
    create_standalone_mock_server()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OAuth Backend with Real HTTP")
    parser.add_argument(
        "--standalone-backend",
        action="store_true",
        help="Run only the mock backend server"
    )
    
    args = parser.parse_args()
    
    if args.standalone_backend:
        run_standalone_mock_backend()
    else:
        # First check if pytest-httpserver is installed
        try:
            import pytest_httpserver
        except ImportError:
            print("\n❌ Error: pytest-httpserver is not installed")
            print("\nPlease install it first:")
            print("  pip install pytest-httpserver")
            print("\nOr add it to your pyproject.toml:")
            print('  dependencies = [..., "pytest-httpserver>=1.0.0"]')
            sys.exit(1)
        
        test_with_real_http()
{% endif -%}