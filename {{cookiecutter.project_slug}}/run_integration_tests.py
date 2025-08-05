#!/usr/bin/env python3
"""Run integration tests for {{ cookiecutter.project_name }}.

This script provides a convenient way to run integration tests with proper
environment setup and reporting.

Usage:
    python run_integration_tests.py              # Run all integration tests
    python run_integration_tests.py -v           # Run with verbose output
    python run_integration_tests.py -k "auto"    # Run only tests matching "auto"
    python run_integration_tests.py --markers    # Show available test markers
"""

import sys
import subprocess
from pathlib import Path

import click


@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.option('-k', '--keyword', help='Only run tests matching this keyword')
@click.option('--markers', is_flag=True, help='Show available test markers')
@click.option('--no-cov', is_flag=True, help='Disable coverage reporting')
def main(verbose: bool, keyword: str, markers: bool, no_cov: bool):
    """Run integration tests for correlation ID functionality."""
    
    if markers:
        # Show available markers
        subprocess.run([sys.executable, "-m", "pytest", "--markers", "tests/integration/"])
        return
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/integration/"]
    
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    if keyword:
        cmd.extend(["-k", keyword])
    
    if no_cov:
        cmd.append("--no-cov")
    
    # Add color output if terminal supports it
    cmd.append("--color=yes")
    
    # Run the tests
    print(f"Running integration tests: {' '.join(cmd)}")
    print("=" * 80)
    
    result = subprocess.run(cmd)
    
    # Return the exit code
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()