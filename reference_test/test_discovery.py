#!/usr/bin/env python3
"""Test MCP discovery pattern"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Test how MCP dev discovers the server
try:
    from reference_test.server import app as server_module
    print("✅ Module loaded successfully")
    print(f"✅ Has server attribute: {hasattr(server_module, 'server')}")
    if hasattr(server_module, 'server'):
        print(f"✅ Server type: {type(server_module.server)}")
        print(f"✅ Server name: {server_module.server.name}")
        print(f"✅ Server is FastMCP: {'FastMCP' in str(type(server_module.server))}")
    else:
        print("❌ No server attribute found")
        print("Available attributes:", [attr for attr in dir(server_module) if not attr.startswith('_')])
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()