# MCP Integration Testing Script for Windows
# Tests MCP tools using the actual MCP client protocol

Write-Host "🧪 Running MCP Integration Tests..." -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue

# Check if virtual environment is active
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Warning: No virtual environment detected." -ForegroundColor Yellow
    Write-Host "   Consider activating a virtual environment first." -ForegroundColor Yellow
    Write-Host ""
}

# Run the integration tests
python -m example_server.tests.integration.cli $args

# Capture exit code
$exitCode = $LASTEXITCODE

# Exit with the same code as the tests
if ($exitCode -ne 0) {
    exit $exitCode
}