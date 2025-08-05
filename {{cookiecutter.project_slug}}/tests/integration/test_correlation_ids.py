"""Integration tests for correlation ID functionality.

These tests verify that:
1. Client-provided correlation IDs are properly used and logged
2. Auto-generated correlation IDs follow the expected ULID format
3. All tool executions include correlation IDs in logs
"""

import asyncio
import sqlite3
import uuid
from datetime import timedelta
from typing import Dict, Any

import pytest
import pytest_asyncio
from mcp import ClientSession, types

from .conftest import query_correlation_logs, get_latest_tool_log


class TestCorrelationIDsWithClientProvided:
    """Test correlation ID handling when provided by the client."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name,args,correlation_id", [
        ("echo_tool", {"message": "Testing correlation ID!"}, "test_echo_abc123"),
        ("get_time", {}, "test_time_def456"),
        ("random_number", {"min_value": 1, "max_value": 100}, "test_random_ghi789"),
        ("calculate_fibonacci", {"n": 10}, "test_fib_jkl012"),
        ("simulate_heavy_computation", {"kwargs_list": [{"complexity": 3}]}, "test_compute_mno345"),
        ("process_batch_data", {"kwargs_list": [{"items": ["a", "b"], "operation": "upper"}]}, "test_batch_pqr678"),
    ])
    async def test_client_provided_correlation_id(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection,
        tool_name: str,
        args: dict,
        correlation_id: str
    ):
        """Test that client-provided correlation IDs are properly logged."""
        # Create metadata with correlation ID
        meta = {
            "correlationId": correlation_id,
            "traceId": str(uuid.uuid4()),
            "clientType": "pytest_integration_test"
        }
        
        # Build request with custom metadata
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=tool_name,
                    arguments=args,
                    _meta=meta
                )
            )
        )
        
        # Execute the tool
        result = await mcp_client.send_request(
            request, 
            types.CallToolResult,
            request_read_timeout_seconds=timedelta(seconds=30)
        )
        
        # Verify the tool executed successfully
        assert result is not None
        
        # Wait for logs to be written
        await asyncio.sleep(0.2)
        
        # Query the database for this correlation ID
        logs = query_correlation_logs(db_connection, correlation_id)
        
        # Assertions
        assert len(logs) > 0, f"No logs found for correlation ID: {correlation_id}"
        
        # Verify the log entry
        log_entry = logs[0]
        assert log_entry["correlation_id"] == correlation_id
        assert log_entry["tool_name"] == tool_name
        assert log_entry["status"] == "success"
        assert log_entry["duration_ms"] is not None
        assert log_entry["duration_ms"] >= 0
    
    @pytest.mark.asyncio
    async def test_multiple_tools_same_correlation_id(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection
    ):
        """Test that multiple tool calls can share the same correlation ID."""
        shared_correlation_id = "test_shared_correlation_xyz789"
        
        tools_to_call = [
            ("echo_tool", {"message": "First call"}),
            ("get_time", {}),
            ("random_number", {"min_value": 1, "max_value": 10})
        ]
        
        for tool_name, args in tools_to_call:
            meta = {"correlationId": shared_correlation_id}
            
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name=tool_name,
                        arguments=args,
                        _meta=meta
                    )
                )
            )
            
            await mcp_client.send_request(
                request,
                types.CallToolResult,
                request_read_timeout_seconds=timedelta(seconds=30)
            )
        
        # Wait for all logs to be written
        await asyncio.sleep(0.3)
        
        # Query all logs for this correlation ID
        logs = query_correlation_logs(db_connection, shared_correlation_id)
        
        # Should have logs for all three tools
        assert len(logs) >= 3, f"Expected at least 3 logs, found {len(logs)}"
        
        # Verify all logs have the same correlation ID
        tool_names = {log["tool_name"] for log in logs}
        assert "echo_tool" in tool_names
        assert "get_time" in tool_names
        assert "random_number" in tool_names
        
        # All should have the same correlation ID
        for log in logs:
            assert log["correlation_id"] == shared_correlation_id


class TestCorrelationIDsAutoGenerated:
    """Test correlation ID auto-generation when not provided by client."""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("tool_name,args", [
        ("echo_tool", {"message": "Testing auto-generated ID!"}),
        ("get_time", {}),
        ("random_number", {"min_value": 10, "max_value": 50}),
        ("calculate_fibonacci", {"n": 15}),
        ("simulate_heavy_computation", {"kwargs_list": [{"complexity": 2}]}),
        ("process_batch_data", {"kwargs_list": [{"items": ["test"], "operation": "reverse"}]}),
    ])
    async def test_auto_generated_correlation_id(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection,
        tool_name: str,
        args: dict
    ):
        """Test that correlation IDs are auto-generated when not provided."""
        # Standard MCP call without custom metadata
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name=tool_name,
                    arguments=args
                )
            )
        )
        
        # Execute the tool
        result = await mcp_client.send_request(
            request,
            types.CallToolResult,
            request_read_timeout_seconds=timedelta(seconds=30)
        )
        
        # Verify the tool executed successfully
        assert result is not None
        
        # Wait for logs to be written
        await asyncio.sleep(0.2)
        
        # Get the latest log for this tool
        log_entry = get_latest_tool_log(db_connection, tool_name)
        
        # Assertions
        assert log_entry is not None, f"No log found for tool: {tool_name}"
        
        # Verify auto-generated ID format (should start with req_ and be ULID format)
        correlation_id = log_entry["correlation_id"]
        assert correlation_id is not None
        assert correlation_id.startswith("req_"), f"Expected ID to start with 'req_', got: {correlation_id}"
        assert len(correlation_id) == 30, f"Expected ULID format (30 chars), got {len(correlation_id)} chars"
        
        # ULID format check - should be 26 chars after 'req_'
        ulid_part = correlation_id[4:]
        assert len(ulid_part) == 26, f"ULID part should be 26 chars, got {len(ulid_part)}"
        
        # Basic ULID character validation (Crockford's base32)
        valid_chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        assert all(c in valid_chars for c in ulid_part.upper()), "Invalid characters in ULID"
    
    @pytest.mark.asyncio
    async def test_unique_auto_generated_ids(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection
    ):
        """Test that auto-generated correlation IDs are unique."""
        correlation_ids = []
        
        # Make multiple calls to the same tool
        for i in range(5):
            request = types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(
                        name="echo_tool",
                        arguments={"message": f"Call {i}"}
                    )
                )
            )
            
            await mcp_client.send_request(
                request,
                types.CallToolResult,
                request_read_timeout_seconds=timedelta(seconds=30)
            )
            
            # Small delay between calls
            await asyncio.sleep(0.1)
        
        # Wait for all logs to be written
        await asyncio.sleep(0.3)
        
        # Query all recent echo_tool logs
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT correlation_id 
            FROM unified_logs 
            WHERE tool_name = 'echo_tool' AND status = 'success'
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        cursor.close()
        
        # Extract correlation IDs
        correlation_ids = [row["correlation_id"] for row in rows]
        
        # All IDs should be unique
        assert len(correlation_ids) == len(set(correlation_ids)), "Duplicate correlation IDs found"
        
        # All should follow the expected format
        for cid in correlation_ids:
            assert cid.startswith("req_")
            assert len(cid) == 30


class TestCorrelationIDEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.mark.asyncio
    async def test_tool_error_includes_correlation_id(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection
    ):
        """Test that correlation IDs are logged even when tools fail."""
        correlation_id = "test_error_case_123"
        
        # Call random_number with invalid range (min > max)
        meta = {"correlationId": correlation_id}
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="random_number",
                    arguments={"min_value": 100, "max_value": 10},  # Invalid: min > max
                    _meta=meta
                )
            )
        )
        
        # Tool should raise an error
        with pytest.raises(Exception):
            await mcp_client.send_request(
                request,
                types.CallToolResult,
                request_read_timeout_seconds=timedelta(seconds=30)
            )
        
        # Wait for logs to be written
        await asyncio.sleep(0.2)
        
        # Query logs for this correlation ID
        logs = query_correlation_logs(db_connection, correlation_id)
        
        # Should have an error log
        assert len(logs) > 0, "No logs found for failed tool execution"
        
        log_entry = logs[0]
        assert log_entry["correlation_id"] == correlation_id
        assert log_entry["tool_name"] == "random_number"
        assert log_entry["status"] == "error"
        assert log_entry["error_message"] is not None
        assert "min_value must be less than or equal to max_value" in log_entry["error_message"]
    
    @pytest.mark.asyncio
    async def test_empty_correlation_id_generates_new(
        self,
        mcp_client: ClientSession,
        db_connection: sqlite3.Connection
    ):
        """Test that empty correlation ID triggers auto-generation."""
        # Send empty string as correlation ID
        meta = {"correlationId": ""}
        request = types.ClientRequest(
            types.CallToolRequest(
                method="tools/call",
                params=types.CallToolRequestParams(
                    name="echo_tool",
                    arguments={"message": "Empty correlation ID test"},
                    _meta=meta
                )
            )
        )
        
        await mcp_client.send_request(
            request,
            types.CallToolResult,
            request_read_timeout_seconds=timedelta(seconds=30)
        )
        
        # Wait for logs
        await asyncio.sleep(0.2)
        
        # Get the latest log
        log_entry = get_latest_tool_log(db_connection, "echo_tool")
        
        # Should have auto-generated an ID
        assert log_entry is not None
        assert log_entry["correlation_id"].startswith("req_")
        assert len(log_entry["correlation_id"]) == 30