#!/usr/bin/env python
"""Integration test for all transport protocols.

This script tests that all three transport protocols (STDIO, SSE, Streamable HTTP)
can be generated and started successfully.
"""

import subprocess
import tempfile
import shutil
import sys
import time
from pathlib import Path
import json
import os


def run_command(cmd, cwd=None, capture_output=True):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=capture_output,
        text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result


def test_transport(project_dir, transport):
    """Test a specific transport protocol."""
    print(f"\n{'='*60}")
    print(f"Testing {transport.upper()} transport")
    print('='*60)
    
    # Create virtual environment
    venv_dir = project_dir / ".venv"
    print("Creating virtual environment...")
    result = run_command([sys.executable, "-m", "venv", str(venv_dir)], cwd=project_dir)
    if result is None:
        return False
    
    # Install project
    pip_path = venv_dir / "bin" / "pip" if sys.platform != "win32" else venv_dir / "Scripts" / "pip.exe"
    print("Installing project dependencies...")
    result = run_command([str(pip_path), "install", "-e", "."], cwd=project_dir)
    if result is None:
        return False
    
    # Start the server with the specified transport
    python_path = venv_dir / "bin" / "python" if sys.platform != "win32" else venv_dir / "Scripts" / "python.exe"
    
    cmd = [str(python_path), "-m", "test_mcp_server.server.app", "--transport", transport]
    if transport in ["sse", "streamable-http"]:
        cmd.extend(["--port", "3001"])
    
    print(f"Starting server with {transport} transport...")
    # Start the server process
    process = subprocess.Popen(
        cmd,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    time.sleep(2)
    
    # Check if process is still running
    if process.poll() is not None:
        # Process has terminated
        stdout, stderr = process.communicate()
        print(f"Server failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False
    
    # For STDIO, just check that it started
    # For SSE and Streamable HTTP, we could make HTTP requests to test
    print(f"✓ {transport.upper()} transport started successfully")
    
    # Terminate the server
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    
    return True


def main():
    """Main test function."""
    print("MCP Server Transport Integration Test")
    print("="*60)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        print(f"Test directory: {tmpdir}")
        
        # Test each transport configuration
        transports = [
            ("stdio", {}),
            ("sse", {}),
            ("streamable-http", {"streamable_http_enabled": "yes"}),
        ]
        
        results = []
        
        for transport, extra_config in transports:
            # Generate a project with cookiecutter
            print(f"\nGenerating project for {transport} transport...")
            
            config = {
                "project_name": "Test MCP Server",
                "project_slug": "test_mcp_server",
                "description": f"Test server for {transport} transport",
                "author_name": "Test Author",
                "author_email": "test@example.com",
                "python_version": "3.11",
                "include_admin_ui": "no",
                "include_example_tools": "yes",
                "include_parallel_example": "no",
                "mcp_config_file_path": "",
                "server_port": "3001",
                "default_transport": transport,
                "streamable_http_enabled": extra_config.get("streamable_http_enabled", "no"),
                "streamable_http_endpoint": "/mcp",
                "streamable_http_json_response": "no",
                "log_level": "INFO",
                "log_retention_days": "30",
                "configure_bazel_build_files": "no",
                "update_aws_parameter_store": "no",
                "jira_project_key": ""
            }
            
            # Save config to file
            config_file = tmpdir / f"config_{transport}.json"
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            # Run cookiecutter
            project_dir = tmpdir / f"test_{transport.replace('-', '_')}"
            
            # Get the template directory (parent of this script)
            template_dir = Path(__file__).parent.parent
            
            result = run_command([
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "--config-file", str(config_file),
                "--output-dir", str(tmpdir)
            ])
            
            if result is None:
                print(f"✗ Failed to generate project for {transport}")
                results.append((transport, False))
                continue
            
            # The project will be created at tmpdir/test_mcp_server
            actual_project_dir = tmpdir / "test_mcp_server"
            if actual_project_dir.exists() and project_dir != actual_project_dir:
                # Rename to avoid conflicts
                if project_dir.exists():
                    shutil.rmtree(project_dir)
                actual_project_dir.rename(project_dir)
            
            # Test the transport
            success = test_transport(project_dir, transport)
            results.append((transport, success))
            
            # Clean up the project directory
            if project_dir.exists():
                shutil.rmtree(project_dir)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    
    all_passed = True
    for transport, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{transport.upper():20} {status}")
        if not success:
            all_passed = False
    
    print("="*60)
    if all_passed:
        print("✓ All transport tests passed!")
        return 0
    else:
        print("✗ Some transport tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())