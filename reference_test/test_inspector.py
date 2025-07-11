#!/usr/bin/env python3
"""Test inspector capability"""

import subprocess
import sys
import signal
import time

def test_inspector_start():
    """Test that inspector can start (but kill it immediately)"""
    
    print("Testing MCP inspector startup...")
    
    # Start inspector and kill it after 3 seconds
    try:
        proc = subprocess.Popen(
            [sys.executable, "-c", "import subprocess; subprocess.run(['mcp', 'dev', 'reference_test.server.app'])"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait 3 seconds then kill
        time.sleep(3)
        proc.terminate()
        
        stdout, stderr = proc.communicate(timeout=2)
        
        if "inspector" in stdout.lower() or "inspector" in stderr.lower():
            print("✅ Inspector started successfully")
            return True
        else:
            print("❌ Inspector failed to start")
            print(f"   stdout: {stdout}")
            print(f"   stderr: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

if __name__ == "__main__":
    test_inspector_start()