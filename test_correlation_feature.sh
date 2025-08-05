#!/bin/bash
# Test script for correlation ID feature

set -e

echo "🧪 Testing Correlation ID Feature"
echo "================================"

# Generate a test server
echo "📦 Generating test server from cookiecutter template..."
rm -rf test_correlation_server
cookiecutter . --no-input \
    project_name="Test Correlation Server" \
    project_slug="test_correlation_server" \
    include_admin_ui="yes" \
    include_example_tools="yes" \
    include_parallel_example="yes"

# Set up the test server
echo "🔧 Test server already set up by cookiecutter with UV..."

# Go back to root
cd ..

# Install mcp in the current environment for the test client
echo "📦 Installing MCP SDK for test client..."
pip install mcp[cli] > /dev/null 2>&1

# Run the test client (need to be in the cookie cutter directory)
echo "🚀 Running test client with correlation IDs..."
echo ""
cd /Users/timkitchens/projects/client-repos/saaga-mcp-server-cookie-cutter
python test_correlation_id_client.py test_correlation_server/test_correlation_server/server/app.py

echo ""
echo "✅ Test complete!"
echo ""
echo "📊 To check the logs with correlation IDs:"
echo "   1. cd test_correlation_server"
echo "   2. source .venv/bin/activate"
echo "   3. streamlit run test_correlation_server/ui/app.py"
echo "   4. Go to the Logs page and filter by correlation ID"