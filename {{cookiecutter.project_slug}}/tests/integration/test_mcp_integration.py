"""MCP Client Integration Tests - ASEP-66.

This test suite validates MCP tools work correctly when accessed via the actual
MCP client, testing the complete protocol flow including:
- Tool discovery and registration
- Parameter serialization (string → typed conversion)
- Error response formatting
- SAAGA decorator integration
- Real client-server interaction

These tests complement the unit tests by validating the full MCP protocol flow
rather than testing decorators in isolation.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import pytest
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


# Use anyio instead of pytest-asyncio to match SDK approach
pytestmark = pytest.mark.anyio


async def create_test_session():
    """Create an MCP client session for testing.
    
    Returns a tuple of (session, cleanup_func) where cleanup_func
    must be called to properly close the session.
    """
    # Get the project root and server module path
    project_root = Path(__file__).parent.parent.parent
    server_module = f"{{ cookiecutter.project_slug }}.server.app"
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
        env=None
    )
    
    # Start the stdio client
    stdio_context = stdio_client(server_params)
    read, write = await stdio_context.__aenter__()
    
    # Create and initialize session
    session = ClientSession(read, write)
    await session.__aenter__()
    await session.initialize()
    
    # Define cleanup function
    async def cleanup():
        try:
            await session.__aexit__(None, None, None)
        except Exception:
            pass
        try:
            await stdio_context.__aexit__(None, None, None)
        except Exception:
            pass
    
    return session, cleanup


class TestMCPToolDiscovery:
    """Test MCP tool discovery functionality."""
    
    async def test_all_tools_discoverable(self):
        """Test that all expected tools are discoverable via list_tools()."""
        session, cleanup = await create_test_session()
        try:
            tools_response = await session.list_tools()
            
            # Extract tool names
            tool_names = [tool.name for tool in tools_response.tools]
            
            # Verify expected tools exist
            expected_tools = [
                "echo_tool", 
                "get_time", 
                "random_number", 
                "calculate_fibonacci"
            ]
            
            # Add conditional tools based on template configuration
            {% if cookiecutter.include_parallel_example == "yes" %}
            expected_tools.extend([
                "process_batch_data", 
                "simulate_heavy_computation"
            ])
            {% endif %}
            
            for expected in expected_tools:
                assert expected in tool_names, f"Tool {expected} not found in {tool_names}"
        finally:
            await cleanup()
    
    async def test_no_kwargs_in_tool_schemas(self):
        """Test that no tool has a 'kwargs' parameter (MCP compatibility)."""
        session, cleanup = await create_test_session()
        try:
            tools_response = await session.list_tools()
            
            for tool in tools_response.tools:
                if tool.inputSchema:
                    properties = tool.inputSchema.get("properties", {})
                    assert "kwargs" not in properties, (
                        f"Tool {tool.name} has kwargs parameter which breaks MCP compatibility"
                    )
        finally:
            await cleanup()
    
    async def test_tool_metadata_present(self):
        """Test that tools have proper metadata (description, schema)."""
        session, cleanup = await create_test_session()
        try:
            tools_response = await session.list_tools()
            
            for tool in tools_response.tools:
                # Every tool should have a description
                assert tool.description, f"Tool {tool.name} missing description"
                
                # Tools should have input schemas
                assert tool.inputSchema is not None, f"Tool {tool.name} missing input schema"
                assert tool.inputSchema.get("type") == "object", (
                    f"Tool {tool.name} schema type should be 'object'"
                )
        finally:
            await cleanup()


class TestMCPToolExecution:
    """Test MCP tool execution with various parameter scenarios."""
    
    def _extract_text_content(self, result: types.CallToolResult) -> Optional[str]:
        """Extract text content from MCP tool result."""
        for content in result.content:
            if isinstance(content, types.TextContent):
                return content.text
        return None
    
    async def test_echo_tool_execution(self):
        """Test echo_tool works correctly via MCP client."""
        session, cleanup = await create_test_session()
        try:
            # Call tool with string parameter (as MCP sends)
            result = await session.call_tool("echo_tool", {"message": "Hello MCP World"})
            
            # Check result structure
            assert not result.isError, f"Tool execution failed: {result}"
            assert len(result.content) > 0, "No content returned"
            
            # Parse text content
            text_content = self._extract_text_content(result)
            assert text_content is not None, "No text content found"
            assert "Hello MCP World" in text_content, f"Expected message not in response: {text_content}"
        finally:
            await cleanup()
    
    async def test_get_time_execution(self):
        """Test get_time tool execution."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool("get_time", {})
            
            assert not result.isError, f"Tool execution failed: {result}"
            
            text_content = self._extract_text_content(result)
            assert text_content is not None, "No text content found"
            
            # Should contain time-related text
            assert any(keyword in text_content.lower() for keyword in ["time", ":", "am", "pm", "utc"]), (
                f"Response doesn't appear to contain time: {text_content}"
            )
        finally:
            await cleanup()
    
    async def test_random_number_with_defaults(self):
        """Test random_number tool with default parameters."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool("random_number", {})
            
            assert not result.isError, f"Tool execution failed: {result}"
            
            text_content = self._extract_text_content(result)
            # Try to parse the response as JSON (tools return structured data)
            try:
                data = json.loads(text_content)
                assert "number" in data, f"Response missing 'number' field: {data}"
                assert isinstance(data["number"], int), f"Number should be int: {data['number']}"
                assert 1 <= data["number"] <= 100, f"Number out of default range: {data['number']}"
            except (json.JSONDecodeError, ValueError):
                # If not JSON, try to extract number directly
                pytest.fail(f"Could not parse response as JSON: {text_content}")
        finally:
            await cleanup()
    
    async def test_random_number_parameter_conversion(self):
        """Test string parameter conversion (MCP sends all params as strings)."""
        session, cleanup = await create_test_session()
        try:
            # MCP protocol sends all parameters as strings
            result = await session.call_tool("random_number", {
                "min_value": "10",
                "max_value": "20"
            })
            
            assert not result.isError, "Tool should handle string-to-int conversion"
            
            text_content = self._extract_text_content(result)
            try:
                data = json.loads(text_content)
                number = data["number"]
                assert 10 <= number <= 20, f"Number {number} out of specified range [10, 20]"
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                pytest.fail(f"Failed to parse response: {e}, content: {text_content}")
        finally:
            await cleanup()
    
    async def test_calculate_fibonacci_execution(self):
        """Test calculate_fibonacci with various inputs."""
        session, cleanup = await create_test_session()
        try:
            # Test with a reasonable value
            result = await session.call_tool("calculate_fibonacci", {"n": "10"})
            
            assert not result.isError, f"Tool execution failed: {result}"
            
            text_content = self._extract_text_content(result)
            try:
                data = json.loads(text_content)
                assert data["position"] == 10, f"Wrong position: {data}"
                assert data["value"] == 55, f"Wrong Fibonacci value for n=10: {data}"
            except (json.JSONDecodeError, KeyError) as e:
                pytest.fail(f"Failed to parse response: {e}, content: {text_content}")
        finally:
            await cleanup()
    
    {% if cookiecutter.include_parallel_example == "yes" %}
    async def test_process_batch_data_parallel_execution(self):
        """Test process_batch_data parallel tool execution."""
        session, cleanup = await create_test_session()
        try:
            # Parallel tools expect a specific format
            kwargs_list = [
                {"items": ["hello", "world"], "operation": "upper"},
                {"items": ["foo", "bar"], "operation": "lower"},
                {"items": ["test"], "operation": "reverse"}
            ]
            
            result = await session.call_tool("process_batch_data", {
                "kwargs_list": kwargs_list
            })
            
            assert not result.isError, f"Tool execution failed: {result}"
            
            # Parallel tools return multiple TextContent items, one for each result
            # Extract all content items
            results = []
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        results.append(json.loads(content.text))
                    except json.JSONDecodeError:
                        pass
            
            assert len(results) == 3, f"Expected 3 results, got {len(results)}"
            
            # Verify each result
            assert results[0]["processed"] == ["HELLO", "WORLD"]
            assert results[1]["processed"] == ["foo", "bar"]
            assert results[2]["processed"] == ["tset"]
        finally:
            await cleanup()
    
    async def test_simulate_heavy_computation_execution(self):
        """Test simulate_heavy_computation parallel tool."""
        session, cleanup = await create_test_session()
        try:
            kwargs_list = [
                {"complexity": "3"},
                {"complexity": "5"}
            ]
            
            result = await session.call_tool("simulate_heavy_computation", {
                "kwargs_list": kwargs_list
            })
            
            assert not result.isError, f"Tool execution failed: {result}"
            
            # Parallel tools return multiple TextContent items, one for each result
            results = []
            for content in result.content:
                if isinstance(content, types.TextContent):
                    try:
                        results.append(json.loads(content.text))
                    except json.JSONDecodeError:
                        pass
            
            assert len(results) == 2, f"Expected 2 results, got {len(results)}"
            
            # Check that results have expected structure
            for i, res in enumerate(results):
                assert "complexity" in res, f"Result {i} missing complexity"
                assert "iterations" in res, f"Result {i} missing iterations"
                assert "result" in res, f"Result {i} missing result"
                assert "computation_time" in res, f"Result {i} missing computation_time"
        finally:
            await cleanup()
    {% endif %}


class TestMCPErrorHandling:
    """Test MCP error handling scenarios."""
    
    def _extract_text_content(self, result: types.CallToolResult) -> Optional[str]:
        """Extract text content from MCP tool result."""
        for content in result.content:
            if isinstance(content, types.TextContent):
                return content.text
        return None
    
    def _extract_error_text(self, result: types.CallToolResult) -> Optional[str]:
        """Extract error text from MCP error result."""
        if result.isError and result.content:
            return self._extract_text_content(result)
        return None
    
    async def test_missing_required_parameter(self):
        """Test error handling when required parameter is missing."""
        session, cleanup = await create_test_session()
        try:
            # Call echo_tool without required 'message' parameter
            result = await session.call_tool("echo_tool", {})
            
            # Should return error
            assert result.isError, "Should return error for missing required parameter"
            
            # Check error content
            error_text = self._extract_error_text(result)
            assert error_text, "No error text found"
            assert any(keyword in error_text.lower() for keyword in ["error", "missing", "required"]), (
                f"Error message doesn't indicate missing parameter: {error_text}"
            )
        finally:
            await cleanup()
    
    async def test_invalid_parameter_type(self):
        """Test error handling with invalid parameter types."""
        session, cleanup = await create_test_session()
        try:
            # Send invalid type that can't be converted
            result = await session.call_tool("calculate_fibonacci", {
                "n": "not_a_number"
            })
            
            assert result.isError, "Should return error for invalid parameter type"
            
            error_text = self._extract_error_text(result)
            assert error_text, "No error text found"
            assert any(keyword in error_text.lower() for keyword in ["error", "invalid", "type", "int"]), (
                f"Error message doesn't indicate type error: {error_text}"
            )
        finally:
            await cleanup()
    
    async def test_tool_exception_handling(self):
        """Test SAAGA error format when tool raises exception."""
        session, cleanup = await create_test_session()
        try:
            # Negative Fibonacci should raise an error
            result = await session.call_tool("calculate_fibonacci", {"n": "-1"})
            
            # May or may not be marked as error depending on exception handling
            text_content = self._extract_text_content(result) or self._extract_error_text(result)
            assert text_content, "No content found in response"
            
            # Check for SAAGA error format
            try:
                data = json.loads(text_content)
                if isinstance(data, dict) and data.get("Status") == "Exception":
                    # Verify SAAGA error format
                    assert "Message" in data, "SAAGA error missing Message"
                    assert "ExceptionType" in data, "SAAGA error missing ExceptionType"
                    assert "Traceback" in data, "SAAGA error missing Traceback"
            except json.JSONDecodeError:
                # Not JSON, check for error keywords
                assert any(keyword in text_content.lower() for keyword in ["error", "negative", "invalid"]), (
                    f"Response doesn't indicate error: {text_content}"
                )
        finally:
            await cleanup()
    
    async def test_nonexistent_tool(self):
        """Test error when calling non-existent tool."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool("nonexistent_tool", {"param": "value"})
            
            assert result.isError, "Should return error for non-existent tool"
            
            error_text = self._extract_error_text(result)
            assert error_text, "No error text found"
            assert any(keyword in error_text.lower() for keyword in ["not found", "unknown", "invalid"]), (
                f"Error doesn't indicate unknown tool: {error_text}"
            )
        finally:
            await cleanup()
    
    {% if cookiecutter.include_parallel_example == "yes" %}
    async def test_parallel_tool_invalid_format(self):
        """Test error handling for parallel tools with invalid input format."""
        session, cleanup = await create_test_session()
        try:
            # Send non-list to parallel tool
            result = await session.call_tool("process_batch_data", {
                "kwargs_list": "not_a_list"
            })
            
            assert result.isError, "Should return error for invalid parallel tool input"
            
            error_text = self._extract_error_text(result)
            assert error_text, "No error text found"
            assert any(keyword in error_text.lower() for keyword in ["list", "type", "error"]), (
                f"Error doesn't indicate type issue: {error_text}"
            )
        finally:
            await cleanup()
    {% endif %}


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance and edge cases."""
    
    def _extract_text_content(self, result: types.CallToolResult) -> Optional[str]:
        """Extract text content from MCP tool result."""
        for content in result.content:
            if isinstance(content, types.TextContent):
                return content.text
        return None
    
    async def test_multiple_tools_in_sequence(self):
        """Test calling multiple tools in sequence."""
        session, cleanup = await create_test_session()
        try:
            # Call multiple tools to ensure session remains stable
            tools_to_test = [
                ("get_time", {}),
                ("echo_tool", {"message": "test"}),
                ("random_number", {"min_value": "1", "max_value": "10"}),
            ]
            
            for tool_name, params in tools_to_test:
                result = await session.call_tool(tool_name, params)
                assert not result.isError, f"Tool {tool_name} failed: {result}"
                assert len(result.content) > 0, f"Tool {tool_name} returned no content"
        finally:
            await cleanup()
    
    async def test_concurrent_tool_calls(self):
        """Test that tools handle concurrent calls correctly."""
        session, cleanup = await create_test_session()
        try:
            # Create multiple concurrent tool calls
            tasks = [
                session.call_tool("random_number", {"min_value": "1", "max_value": "100"}),
                session.call_tool("echo_tool", {"message": "concurrent test"}),
                session.call_tool("get_time", {}),
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all succeeded
            for i, result in enumerate(results):
                assert not isinstance(result, Exception), f"Task {i} raised exception: {result}"
                assert not result.isError, f"Task {i} returned error: {result}"
        finally:
            await cleanup()
    
    async def test_large_parameter_handling(self):
        """Test handling of large parameters."""
        session, cleanup = await create_test_session()
        try:
            # Create a large message
            large_message = "x" * 10000  # 10KB message
            
            result = await session.call_tool("echo_tool", {"message": large_message})
            
            assert not result.isError, f"Failed with large parameter: {result}"
            
            text_content = self._extract_text_content(result)
            assert large_message in text_content, "Large message not properly echoed"
        finally:
            await cleanup()


# Test runner for direct execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])