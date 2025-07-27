#!/bin/bash
# Test MCP server with Claude using integration test config

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default configuration file
CONFIG_FILE="${SCRIPT_DIR}/mcp.integration_test.json"

# Parse command line arguments
PROMPT=""
CUSTOM_CONFIG=""

# Function to show usage
usage() {
    echo "Usage: $0 [-c config_file] \"your prompt here\""
    echo ""
    echo "Options:"
    echo "  -c, --config    Path to custom MCP config file (default: mcp.integration_test.json)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 \"List all available tools\""
    echo "  $0 \"Run the echo_tool with message 'Hello World'\""
    echo "  $0 -c custom_config.json \"Test my MCP server\""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CUSTOM_CONFIG="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            # Collect all remaining arguments as the prompt
            PROMPT="$*"
            break
            ;;
    esac
done

# Use custom config if provided
if [ -n "$CUSTOM_CONFIG" ]; then
    CONFIG_FILE="$CUSTOM_CONFIG"
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found: $CONFIG_FILE${NC}"
    echo ""
    echo "Make sure you've run the cookiecutter template to generate mcp.integration_test.json"
    echo "Or specify a custom config file with -c option"
    exit 1
fi

# Check if prompt is provided
if [ -z "$PROMPT" ]; then
    echo -e "${RED}Error: No prompt provided${NC}"
    echo ""
    usage
    exit 1
fi

# Check if claude command exists
if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: 'claude' command not found${NC}"
    echo "Please install Claude CLI first"
    exit 1
fi

# Display what we're doing
echo -e "${GREEN}🧪 Testing MCP server with Claude${NC}"
echo -e "${YELLOW}Config:${NC} $CONFIG_FILE"
echo -e "${YELLOW}Prompt:${NC} $PROMPT"
echo ""

# Run Claude with the MCP server
claude -p "$PROMPT" \
    --model sonnet \
    --mcp-config "$CONFIG_FILE" \
    --dangerously-skip-permissions \
    "@"