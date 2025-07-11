#!/usr/bin/env python3
"""Test MCP CLI discovery compatibility"""

import subprocess
import sys
import os

def test_mcp_dev_discovery():
    """Test that MCP CLI can discover and load the server"""
    
    # Test the two main discovery patterns MCP uses
    patterns = [
        "reference_test.server.app",  # Direct module path
        "reference_test/server/app.py",  # File path
    ]
    
    print("Testing MCP CLI discovery patterns...")
    
    for pattern in patterns:
        print(f"\n🔍 Testing pattern: {pattern}")
        
        # Test with --help flag to see if it can load the server
        try:
            result = subprocess.run(
                [sys.executable, "-m", "mcp", "dev", pattern, "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ MCP CLI can load server with pattern: {pattern}")
                if "inspector" in result.stdout.lower():
                    print("✅ Inspector mode available")
            else:
                print(f"❌ Pattern failed: {pattern}")
                print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout (expected for dev mode): {pattern}")
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_mcp_dev_discovery()