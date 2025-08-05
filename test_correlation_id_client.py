#!/usr/bin/env python3
"""Test MCP client that can pass correlation IDs via metadata.

This client demonstrates how to pass custom metadata (including correlation IDs)
to MCP servers using the protocol's _meta field.
"""

import asyncio
import uuid
from datetime import timedelta
from typing import Optional
from mcp import ClientSession, types
from mcp.client.stdio import stdio_client, StdioServerParameters
import click


class CorrelationIDClient:
    """MCP client that adds correlation IDs to all tool calls."""
    
    def __init__(self, session: ClientSession):
        self.session = session
        self.trace_id = str(uuid.uuid4())
    
    async def call_tool_with_correlation(
        self, 
        tool_name: str, 
        arguments: dict,
        correlation_id: Optional[str] = None,
        progress_callback = None
    ):
        """Call an MCP tool with a correlation ID in metadata.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            correlation_id: Optional correlation ID (generates one if not provided)
            progress_callback: Optional callback for progress updates
        
        Returns:
            Tool result
        """
        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = f"client_{uuid.uuid4().hex[:12]}"
        
        # Create metadata with correlation ID
        meta = {
            "correlationId": correlation_id,
            "traceId": self.trace_id,
            "timestamp": asyncio.get_event_loop().time(),
            "clientVersion": "1.0.0",
            "source": "test_correlation_client"
        }
        
        # Build request with custom metadata
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=tool_name,
                    arguments=arguments,
                    _meta=meta  # Custom metadata here
                )
            )
        )
        
        # Send request with all features preserved
        print(f"📤 Calling tool '{tool_name}' with correlation ID: {correlation_id}")
        
        result = await self.session.send_request(
            request, 
            types.CallToolResult,
            progress_callback=progress_callback,
            request_read_timeout_seconds=timedelta(seconds=30)
        )
        
        return result


async def test_correlation_ids(server_script_path: str):
    """Test correlation ID passing with various tools."""
    
    # Server params for stdio transport
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path, "--transport", "stdio"],
        env=None
    )
    
    print(f"🚀 Starting MCP server from: {server_script_path}")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the client
            client = CorrelationIDClient(session)
            
            # Initialize the session
            await session.initialize()
            
            print("\n📋 Available tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "=" * 60)
            print("🧪 Testing correlation ID passing...")
            print("=" * 60)
            
            # Test 1: Echo tool with custom correlation ID
            print("\n1️⃣ Testing echo_tool with custom correlation ID...")
            custom_correlation_id = "frontend_req_abc123"
            
            try:
                result = await client.call_tool_with_correlation(
                    "echo_tool",
                    {"text": "Hello from client with correlation ID!"},
                    correlation_id=custom_correlation_id
                )
                print(f"✅ Result: {result.content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 2: Random number without correlation ID (should generate one)
            print("\n2️⃣ Testing get_random_number without correlation ID...")
            try:
                result = await client.call_tool_with_correlation(
                    "get_random_number",
                    {"min": 1, "max": 100}
                    # No correlation_id - should generate one
                )
                print(f"✅ Result: {result.content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 3: Time tool with another custom correlation ID
            print("\n3️⃣ Testing get_time with custom correlation ID...")
            custom_correlation_id_2 = "mobile_app_req_xyz789"
            
            try:
                result = await client.call_tool_with_correlation(
                    "get_time",
                    {},
                    correlation_id=custom_correlation_id_2
                )
                print(f"✅ Result: {result.content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 4: Heavy computation with progress callback
            print("\n4️⃣ Testing simulate_heavy_computation with correlation ID and progress...")
            computation_correlation_id = "compute_task_123"
            
            def on_progress(progress, total, message):
                print(f"  📊 Progress: {progress}/{total} - {message}")
            
            try:
                result = await client.call_tool_with_correlation(
                    "simulate_heavy_computation",
                    {"iterations": 5},
                    correlation_id=computation_correlation_id,
                    progress_callback=on_progress
                )
                print(f"✅ Result: {result.content}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n" + "=" * 60)
            print("✨ Test complete! Check the server logs to verify correlation IDs were used.")
            print("💡 Look for log entries with the following correlation IDs:")
            print(f"   - frontend_req_abc123")
            print(f"   - mobile_app_req_xyz789")
            print(f"   - compute_task_123")
            print(f"   - client_* (auto-generated)")


@click.command()
@click.argument('server_script_path', type=click.Path(exists=True))
def main(server_script_path: str):
    """Test MCP server with correlation ID passing.
    
    Args:
        server_script_path: Path to the server's app.py file
    """
    asyncio.run(test_correlation_ids(server_script_path))


if __name__ == "__main__":
    main()