#!/usr/bin/env python3
"""Quick test to verify integration test fixes."""

import subprocess
import sys

def run_tests():
    """Run the integration tests with proper configuration."""
    
    print("Running correlation ID integration tests...")
    print("-" * 60)
    
    # Run pytest with the integration tests
    cmd = [
        sys.executable,
        "-m", "pytest",
        "tests/integration/test_correlation_ids.py",
        "-v",
        "-s",  # Show print statements
        "--tb=short"  # Short traceback format
    ]
    
    result = subprocess.run(cmd, cwd=".")
    
    if result.returncode == 0:
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed")
        print("Please check the output above for details")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())