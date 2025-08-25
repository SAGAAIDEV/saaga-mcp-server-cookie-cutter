#!/usr/bin/env bash
# MCP Integration Testing Script
# Tests MCP tools using the actual MCP client protocol

set -e

echo "🧪 Running MCP Integration Tests..."
echo "=================================="

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   Consider activating a virtual environment first."
    echo ""
fi

# Run the integration tests
python -m final_mcp.tests.integration.cli "$@"

# Exit with the same code as the tests
exit $?