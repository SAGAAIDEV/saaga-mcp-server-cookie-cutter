# Test MCP server with Claude using integration test config

param(
    [Parameter(Position=0, Mandatory=$true, ValueFromRemainingArguments=$true)]
    [string[]]$Prompt,
    
    [Parameter()]
    [Alias("c")]
    [string]$Config,
    
    [Parameter()]
    [switch]$Help
)

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Default configuration file
$ConfigFile = Join-Path $ScriptDir "mcp.integration_test.json"

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\test_mcp_with_claude.ps1 [-Config config_file] `"your prompt here`""
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Config, -c     Path to custom MCP config file (default: mcp.integration_test.json)"
    Write-Host "  -Help, -h       Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\test_mcp_with_claude.ps1 `"List all available tools`""
    Write-Host "  .\test_mcp_with_claude.ps1 `"Run the echo_tool with message 'Hello World'`""
    Write-Host "  .\test_mcp_with_claude.ps1 -Config custom_config.json `"Test my MCP server`""
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Use custom config if provided
if ($Config) {
    $ConfigFile = $Config
}

# Check if config file exists
if (-not (Test-Path $ConfigFile)) {
    Write-Host "${Red}Error: Configuration file not found: $ConfigFile${Reset}"
    Write-Host ""
    Write-Host "Make sure you've run the cookiecutter template to generate mcp.integration_test.json"
    Write-Host "Or specify a custom config file with -Config option"
    exit 1
}

# Join prompt array into single string
$PromptString = $Prompt -join " "

# Check if claude command exists
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Host "${Red}Error: 'claude' command not found${Reset}"
    Write-Host "Please install Claude CLI first"
    exit 1
}

# Display what we're doing
Write-Host "${Green}🧪 Testing MCP server with Claude${Reset}"
Write-Host "${Yellow}Config:${Reset} $ConfigFile"
Write-Host "${Yellow}Prompt:${Reset} $PromptString"
Write-Host ""

# Run Claude with the MCP server
& claude -p $PromptString `
    --model sonnet `
    --mcp-config $ConfigFile `
    --dangerously-skip-permissions `
    "@"