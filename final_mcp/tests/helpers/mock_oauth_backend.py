"""
Lightweight Mock OAuth Backend Server for Testing

This module provides a real HTTP server for testing OAuth backend integration.
It uses pytest-httpserver to create an actual HTTP endpoint that the OAuth
backend decorator will call, allowing you to see real HTTP interactions.

Usage in tests:
    from tests.helpers.mock_oauth_backend import start_mock_backend
    
    with start_mock_backend() as backend_url:
        # Your MCP server will make real HTTP calls to backend_url
        # The mock server will respond with test tokens
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Generator, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

# Mock tokens that will be returned by the backend
MOCK_TOKENS = {
    "reddit": {
        "default": "reddit_access_token_mock_xyz789",
        "test_user_123": "reddit_token_for_test_user_abc456",
    },
    "github": {
        "default": "gho_mockGitHubAccessToken123456",
        "test_user_123": "gho_github_token_for_test_user",
    },
    "google": {
        "default": "ya29.mockGoogleAccessToken789012",
        "test_user_123": "ya29.google_token_for_test_user",
    }
}


def setup_oauth_backend_routes(httpserver):
    """
    Configure the mock OAuth backend server routes.
    
    This sets up the /api/connectors/requestAuth endpoint to handle
    token exchange requests just like a real backend would.
    
    Args:
        httpserver: The HTTPServer instance from pytest-httpserver
    """
    from werkzeug import Response
    
    def handle_token_exchange(request):
        """Handle the token exchange request."""
        try:
            # Parse the request body
            # pytest-httpserver uses request.data instead of request.body
            body = json.loads(request.data.decode('utf-8'))
            user_id = body.get("userId")
            user_token = body.get("userToken")
            provider_id = body.get("providerId")
            
            logger.info(f"Mock backend received: userId={user_id}, "
                       f"providerId={provider_id}, userToken={user_token[:10]}...")
            
            # Simulate special test cases
            if user_token == "invalid_token":
                return Response(
                    json.dumps({"error": "Invalid or expired temporary token"}),
                    status=401,
                    headers={"Content-Type": "application/json"}
                )
            
            if user_token == "forbidden_token":
                return Response(
                    json.dumps({"error": f"User not authorized for provider {provider_id}"}),
                    status=403,
                    headers={"Content-Type": "application/json"}
                )
            
            if user_token == "error_token":
                return Response(
                    json.dumps({"error": "Internal server error during token exchange"}),
                    status=500,
                    headers={"Content-Type": "application/json"}
                )
            
            # Check if provider is supported
            if provider_id not in MOCK_TOKENS:
                return Response(
                    json.dumps({"error": f"Provider {provider_id} not configured"}),
                    status=404,
                    headers={"Content-Type": "application/json"}
                )
            
            # Get mock token for the provider
            provider_tokens = MOCK_TOKENS[provider_id]
            
            # Try to get user-specific token, otherwise use default
            if user_id in provider_tokens:
                access_token = provider_tokens[user_id]
            else:
                access_token = provider_tokens["default"]
            
            # Add timestamp to make it unique
            access_token = f"{access_token}_{datetime.now().strftime('%H%M%S')}"
            
            logger.info(f"Mock backend returning token for {provider_id}: {access_token[:20]}...")
            
            # Return the access token
            return Response(
                json.dumps({"accessToken": access_token}),
                status=200,
                headers={"Content-Type": "application/json"}
            )
            
        except Exception as e:
            logger.error(f"Error in mock backend: {e}")
            return Response(
                json.dumps({"error": str(e)}),
                status=500,
                headers={"Content-Type": "application/json"}
            )
    
    # Register the endpoint
    httpserver.expect_request(
        "/api/connectors/requestAuth",
        method="POST"
    ).respond_with_handler(handle_token_exchange)
    
    # Also add a health check endpoint
    httpserver.expect_request(
        "/health",
        method="GET"
    ).respond_with_json({"status": "healthy"})
    
    logger.info(f"Mock OAuth backend configured at {httpserver.url_for('/')}")


@contextmanager
def start_mock_backend(port: int = 0) -> Generator[str, None, None]:
    """
    Start a mock OAuth backend server for testing.
    
    This creates a real HTTP server that listens on localhost and responds
    to token exchange requests. The OAuth backend decorator will make actual
    HTTP calls to this server.
    
    Args:
        port: Port to bind to (0 for automatic selection)
    
    Yields:
        str: The base URL of the mock backend server
    
    Example:
        ```python
        with start_mock_backend() as backend_url:
            # Configure your MCP server to use backend_url
            # The server will make real HTTP calls to exchange tokens
            os.environ["OAUTH_BACKEND_URL"] = backend_url
            os.environ["OAUTH_BACKEND_MOCK_MODE"] = "no"  # Use real HTTP!
            
            # Now test your OAuth backend tools
            # You'll see real HTTP requests in the logs
        ```
    """
    try:
        from pytest_httpserver import HTTPServer
    except ImportError:
        raise ImportError(
            "pytest-httpserver is required for mock backend testing. "
            "Install it with: pip install pytest-httpserver"
        )
    
    # Create and start the server
    with HTTPServer(host="127.0.0.1", port=port) as httpserver:
        # Set up the OAuth backend routes
        setup_oauth_backend_routes(httpserver)
        
        # The server auto-starts in the context manager, no need to call start()
        backend_url = httpserver.url_for("/").rstrip("/")
        
        logger.info(f"Mock OAuth backend started at {backend_url}")
        print(f"\n🚀 Mock OAuth Backend Server running at: {backend_url}")
        print(f"   - POST {backend_url}/api/connectors/requestAuth")
        print(f"   - GET  {backend_url}/health\n")
        
        yield backend_url
        
        # Server automatically stops when context exits
        logger.info("Mock OAuth backend stopped")


def create_standalone_mock_server():
    """
    Create a standalone mock server that runs until interrupted.
    
    This is useful for manual testing where you want the mock backend
    to keep running while you test your MCP server.
    
    Usage:
        python -c "from tests.helpers.mock_oauth_backend import create_standalone_mock_server; create_standalone_mock_server()"
    """
    try:
        from pytest_httpserver import HTTPServer
    except ImportError:
        print("Error: pytest-httpserver is required.")
        print("Install it with: pip install pytest-httpserver")
        return
    
    print("\n" + "="*60)
    print("🚀 Mock OAuth Backend Server (Standalone Mode)")
    print("="*60)
    
    with HTTPServer(host="127.0.0.1", port=8000) as httpserver:
        setup_oauth_backend_routes(httpserver)
        # Server auto-starts in context manager
        backend_url = httpserver.url_for("/").rstrip("/")
        
        print(f"\nServer running at: {backend_url}")
        print(f"\nEndpoints:")
        print(f"  - POST {backend_url}/api/connectors/requestAuth")
        print(f"  - GET  {backend_url}/health")
        print(f"\nTest tokens:")
        print(f"  - Use 'invalid_token' as userToken → 401 Unauthorized")
        print(f"  - Use 'forbidden_token' as userToken → 403 Forbidden")
        print(f"  - Use 'error_token' as userToken → 500 Server Error")
        print(f"\nPress Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        try:
            # Keep the server running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down mock backend server...")


if __name__ == "__main__":
    # Run as standalone server for manual testing
    create_standalone_mock_server()
