"""Edge case tests for MCP tools to increase coverage.

These tests specifically target error conditions and edge cases
that are not covered by the main integration tests.
"""

import pytest
from mcp import types
from tests.integration.test_example_tools_integration import create_test_session


pytestmark = pytest.mark.anyio


class TestToolEdgeCases:
    """Test edge cases and error conditions for MCP tools."""
    
    def _extract_error_message(self, result: types.CallToolResult) -> str:
        """Extract error message from MCP tool result."""
        for content in result.content:
            if isinstance(content, types.TextContent):
                return content.text
        return ""
    
    async def test_random_number_invalid_range(self):
        """Test random_number with min > max (line 51 coverage)."""
        session, cleanup = await create_test_session()
        try:
            # Test with min_value > max_value
            result = await session.call_tool(
                "random_number",
                arguments={"min_value": 100, "max_value": 10}
            )
            
            # Exception is re-raised for MCP to handle properly
            assert result.isError is True  # Exception is re-raised for MCP to handle
            error_msg = self._extract_error_message(result)
            assert "min_value must be less than or equal to max_value" in error_msg
        finally:
            await cleanup()
    
    async def test_fibonacci_zero_position(self):
        """Test fibonacci with n=0 (line 77 coverage)."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "calculate_fibonacci",
                arguments={"n": 0}
            )
            
            # Should handle n=0 case
            assert result.isError is False
            for content in result.content:
                if isinstance(content, types.TextContent):
                    import json
                    data = json.loads(content.text)
                    assert data["position"] == 0
                    assert data["value"] == 0
        finally:
            await cleanup()
    
    async def test_fibonacci_one_position(self):
        """Test fibonacci with n=1 (line 77 coverage)."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "calculate_fibonacci",
                arguments={"n": 1}
            )
            
            # Should handle n=1 case
            assert result.isError is False
            for content in result.content:
                if isinstance(content, types.TextContent):
                    import json
                    data = json.loads(content.text)
                    assert data["position"] == 1
                    assert data["value"] == 1
        finally:
            await cleanup()

{% if cookiecutter.include_parallel_example == "yes" %}    
    async def test_batch_data_unknown_operation(self):
        """Test process_batch_data with unknown operation (line 122 coverage)."""
        session, cleanup = await create_test_session()
        try:
            # Parallel tools expect kwargs_list parameter
            result = await session.call_tool(
                "process_batch_data",
                arguments={
                    "kwargs_list": [{
                        "items": ["1", "2", "3"],
                        "operation": "unknown_op"
                    }]
                }
            )
            
            # For parallel tools, validation errors come back as isError=True
            error_msg = self._extract_error_message(result)
            # Either way, we should get an error message about unknown operation
            if result.isError:
                # MCP validation error
                assert "Error executing tool" in error_msg or "Exception" in error_msg
            else:
                # SAAGA decorator caught it
                assert "Unknown operation" in error_msg
                assert "Exception" in error_msg
        finally:
            await cleanup()
    
    async def test_heavy_computation_invalid_complexity(self):
        """Test simulate_heavy_computation with invalid complexity (line 146 coverage)."""
        session, cleanup = await create_test_session()
        try:
            # Parallel tools expect kwargs_list parameter
            result = await session.call_tool(
                "simulate_heavy_computation",
                arguments={
                    "kwargs_list": [{"complexity": 15}]
                }
            )
            
            # For parallel tools, validation errors may come back as isError=True
            error_msg = self._extract_error_message(result)
            if result.isError:
                # MCP validation error
                assert "Error executing tool" in error_msg or "Exception" in error_msg
            else:
                # SAAGA decorator caught it
                assert "complexity must be between 1 and 10" in error_msg
                assert "Exception" in error_msg
        finally:
            await cleanup()
    
    async def test_heavy_computation_zero_complexity(self):
        """Test simulate_heavy_computation with complexity=0 (line 146 coverage)."""
        session, cleanup = await create_test_session()
        try:
            # Parallel tools expect kwargs_list parameter
            result = await session.call_tool(
                "simulate_heavy_computation",
                arguments={
                    "kwargs_list": [{"complexity": 0}]
                }
            )
            
            # For parallel tools, validation errors may come back as isError=True
            error_msg = self._extract_error_message(result)
            if result.isError:
                # MCP validation error
                assert "Error executing tool" in error_msg or "Exception" in error_msg
            else:
                # SAAGA decorator caught it
                assert "complexity must be between 1 and 10" in error_msg
                assert "Exception" in error_msg
        finally:
            await cleanup()
{% endif %}