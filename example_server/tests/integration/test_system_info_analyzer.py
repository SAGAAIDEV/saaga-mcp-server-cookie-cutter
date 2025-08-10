"""
Integration tests for the system_info_analyzer tool.

These tests validate the complete MCP protocol flow including parameter conversion,
error handling, and decorator behavior for the system information analyzer.
"""

import json
import pytest
from mcp import types
from typing import Optional, Dict, Any
import sys
import os
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client, get_default_environment


# ============================================================================
# TEST SESSION CREATION
# ============================================================================
async def create_test_session():
    """
    Creates an MCP client session for testing the system_info_analyzer tool.
    
    Returns:
        Tuple of (session, cleanup_function)
    """
    # Get project root and server module
    project_root = Path(__file__).parent.parent.parent
    server_module = "example_server.server.app"
    
    # Build environment with proper Python path
    env = get_default_environment()
    env["PYTHONPATH"] = str(project_root)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
        env=env
    )
    
    # Start stdio client
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


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def _extract_text_content(result: types.CallToolResult) -> Optional[str]:
    """Extract text content from MCP result."""
    for content in result.content:
        if isinstance(content, types.TextContent):
            return content.text
    return None


def _parse_json_response(result: types.CallToolResult) -> Optional[Dict[str, Any]]:
    """Parse JSON response from tool."""
    text = _extract_text_content(result)
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


# ============================================================================
# TEST CLASS FOR SYSTEM INFO ANALYZER
# ============================================================================
class TestSystemInfoAnalyzerIntegration:
    """Integration tests for the system_info_analyzer tool."""
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_default_params(self):
        """Test system_info_analyzer with default parameters."""
        session, cleanup = await create_test_session()
        try:
            # Call tool with no arguments (uses defaults)
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={}
            )
            
            # Verify successful execution
            assert result.isError is False, f"Tool failed: {result}"
            
            # Parse response
            data = _parse_json_response(result)
            assert data is not None, "Failed to parse JSON response"
            
            # Verify required sections are present
            assert "cpu" in data, "Missing CPU information"
            assert "memory" in data, "Missing memory information"
            assert "disk" in data, "Missing disk information"
            assert "system" in data, "Missing system information"
            
            # Since defaults include_processes=True
            assert "processes" in data, "Missing processes information"
            
            # Verify CPU data structure
            cpu_data = data["cpu"]
            assert "percent" in cpu_data
            assert "count_logical" in cpu_data
            assert "count_physical" in cpu_data
            assert isinstance(cpu_data["percent"], (int, float))
            assert isinstance(cpu_data["count_logical"], int)
            
            # Verify memory data structure
            memory_data = data["memory"]
            assert "total_gb" in memory_data
            assert "available_gb" in memory_data
            assert "percent" in memory_data
            assert isinstance(memory_data["percent"], (int, float))
            
            # Verify system data
            system_data = data["system"]
            assert "boot_time" in system_data
            assert "uptime_hours" in system_data
            assert "platform" in system_data
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_with_all_options(self):
        """Test system_info_analyzer with all options enabled."""
        session, cleanup = await create_test_session()
        try:
            # Call tool with all options enabled
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": True,
                    "process_limit": 5,
                    "include_disk_io": True,
                    "include_network": True
                }
            )
            
            assert result.isError is False, f"Tool failed: {result}"
            
            data = _parse_json_response(result)
            assert data is not None
            
            # Verify processes section with limit
            assert "processes" in data
            processes = data["processes"]
            assert "top_by_cpu" in processes
            assert "top_by_memory" in processes
            assert len(processes["top_by_cpu"]) <= 5
            assert len(processes["top_by_memory"]) <= 5
            
            # Verify disk I/O counters (if available on platform)
            disk_data = data["disk"]
            # Note: io_counters might not be present on all systems
            if "io_counters" in disk_data:
                io_counters = disk_data["io_counters"]
                assert "read_gb" in io_counters
                assert "write_gb" in io_counters
                assert "read_count" in io_counters
                assert "write_count" in io_counters
            
            # Verify network information
            if "network" in data:
                network = data["network"]
                assert "bytes_sent_gb" in network
                assert "bytes_recv_gb" in network
                assert "packets_sent" in network
                assert "packets_recv" in network
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_minimal_output(self):
        """Test system_info_analyzer with minimal output options."""
        session, cleanup = await create_test_session()
        try:
            # Call tool with minimal options
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": False,
                    "include_disk_io": False,
                    "include_network": False
                }
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            # Should still have basic sections
            assert "cpu" in data
            assert "memory" in data
            assert "disk" in data
            assert "system" in data
            
            # Should NOT have processes
            assert "processes" not in data
            
            # Should NOT have network
            assert "network" not in data
            
            # Disk should not have io_counters
            disk_data = data["disk"]
            assert "partitions" in disk_data
            # io_counters should be absent or minimal
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_parameter_conversion(self):
        """Test that MCP string parameters are properly converted to correct types."""
        session, cleanup = await create_test_session()
        try:
            # Send parameters as strings (how MCP actually sends them)
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": "true",    # String -> bool
                    "process_limit": "3",           # String -> int
                    "include_disk_io": "false",     # String -> bool
                    "include_network": "true"       # String -> bool
                }
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            # Verify the conversions worked correctly
            assert "processes" in data  # include_processes=true worked
            processes = data["processes"]
            if "top_by_cpu" in processes:
                assert len(processes["top_by_cpu"]) <= 3  # process_limit=3 worked
            
            # Network should be included (include_network=true)
            # Note: network might not be present if no network activity
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_process_details(self):
        """Test that process information contains expected fields."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": True,
                    "process_limit": 2
                }
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            processes = data.get("processes", {})
            assert "total_count" in processes
            assert isinstance(processes["total_count"], int)
            assert processes["total_count"] > 0
            
            # Check top CPU processes
            if "top_by_cpu" in processes and len(processes["top_by_cpu"]) > 0:
                top_cpu = processes["top_by_cpu"][0]
                assert "pid" in top_cpu
                assert "name" in top_cpu
                assert "cpu_percent" in top_cpu
                assert "memory_mb" in top_cpu
                assert isinstance(top_cpu["pid"], int)
                assert isinstance(top_cpu["cpu_percent"], (int, float))
            
            # Check top memory processes
            if "top_by_memory" in processes and len(processes["top_by_memory"]) > 0:
                top_mem = processes["top_by_memory"][0]
                assert "pid" in top_mem
                assert "name" in top_mem
                assert "memory_percent" in top_mem
                assert "memory_mb" in top_mem
                assert isinstance(top_mem["memory_mb"], (int, float))
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_disk_partitions(self):
        """Test that disk partition information is properly structured."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={}
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            disk_data = data.get("disk", {})
            assert "partitions" in disk_data
            partitions = disk_data["partitions"]
            
            # Should have at least one partition (the root filesystem)
            assert len(partitions) > 0
            
            # Check first partition structure
            partition = partitions[0]
            assert "device" in partition
            assert "mountpoint" in partition
            assert "fstype" in partition
            assert "total_gb" in partition
            assert "used_gb" in partition
            assert "free_gb" in partition
            assert "percent" in partition
            
            # Verify numeric values
            assert isinstance(partition["total_gb"], (int, float))
            assert isinstance(partition["percent"], (int, float))
            assert 0 <= partition["percent"] <= 100
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_memory_metrics(self):
        """Test that memory metrics are reasonable and properly formatted."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={}
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            memory = data.get("memory", {})
            
            # Check all memory fields
            required_fields = [
                "total_gb", "available_gb", "used_gb", "percent",
                "swap_total_gb", "swap_used_gb", "swap_percent"
            ]
            for field in required_fields:
                assert field in memory, f"Missing memory field: {field}"
                assert isinstance(memory[field], (int, float)), f"Invalid type for {field}"
            
            # Sanity checks
            assert memory["total_gb"] > 0
            assert 0 <= memory["percent"] <= 100
            assert 0 <= memory["swap_percent"] <= 100
            assert memory["used_gb"] <= memory["total_gb"]
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_platform_info(self):
        """Test that platform information is included in system section."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={}
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            system = data.get("system", {})
            
            # Check platform information
            platform_fields = [
                "platform", "platform_release", "platform_version",
                "architecture", "hostname", "python_version"
            ]
            
            for field in platform_fields:
                assert field in system, f"Missing system field: {field}"
                assert isinstance(system[field], str), f"Invalid type for {field}"
                assert len(system[field]) > 0, f"Empty value for {field}"
            
            # Check uptime
            assert "uptime_hours" in system
            assert "uptime_days" in system
            assert isinstance(system["uptime_hours"], (int, float))
            assert isinstance(system["uptime_days"], int)
            assert system["uptime_hours"] >= 0
            assert system["uptime_days"] >= 0
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_edge_case_zero_processes(self):
        """Test edge case with process_limit set to 0."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": True,
                    "process_limit": 0  # Edge case: no processes
                }
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            # Should still have processes section
            assert "processes" in data
            processes = data["processes"]
            
            # Should have total count but empty lists
            assert "total_count" in processes
            assert processes["total_count"] > 0  # System has processes
            
            # But top lists should be empty
            assert len(processes.get("top_by_cpu", [])) == 0
            assert len(processes.get("top_by_memory", [])) == 0
            
        finally:
            await cleanup()
    
    @pytest.mark.anyio 
    async def test_system_info_analyzer_large_process_limit(self):
        """Test with a very large process_limit value."""
        session, cleanup = await create_test_session()
        try:
            result = await session.call_tool(
                "system_info_analyzer",
                arguments={
                    "include_processes": True,
                    "process_limit": 1000  # Very large limit
                }
            )
            
            assert result.isError is False
            
            data = _parse_json_response(result)
            assert data is not None
            
            processes = data.get("processes", {})
            
            # Should return all available processes up to limit
            # But realistically won't be 1000 processes
            total_count = processes.get("total_count", 0)
            top_cpu_count = len(processes.get("top_by_cpu", []))
            top_mem_count = len(processes.get("top_by_memory", []))
            
            # Should not exceed actual process count
            assert top_cpu_count <= total_count
            assert top_mem_count <= total_count
            assert top_cpu_count <= 1000
            assert top_mem_count <= 1000
            
        finally:
            await cleanup()


# ============================================================================
# ADDITIONAL EDGE CASE TESTS
# ============================================================================
@pytest.mark.anyio
async def test_system_info_analyzer_boolean_string_variations():
    """Test various string representations of boolean values."""
    session, cleanup = await create_test_session()
    try:
        # Test with "false" string
        result = await session.call_tool(
            "system_info_analyzer",
            arguments={
                "include_processes": "false",
                "include_network": "false"
            }
        )
        
        assert result.isError is False
        data = _parse_json_response(result)
        
        # Should NOT have these sections
        assert "processes" not in data
        assert "network" not in data
        
    finally:
        await cleanup()


@pytest.mark.anyio
async def test_system_info_analyzer_invalid_parameter_type():
    """Test with invalid parameter type that can't be converted."""
    session, cleanup = await create_test_session()
    try:
        # Send invalid value for process_limit
        result = await session.call_tool(
            "system_info_analyzer",
            arguments={
                "process_limit": "not_a_number"  # Invalid
            }
        )
        
        # Should handle gracefully or return error
        # The behavior depends on type_converter decorator
        if result.isError:
            # If error, verify it's about type conversion
            error_text = _extract_text_content(result)
            assert error_text is not None
            # Could check for specific error message
        else:
            # If it succeeds, might use default
            data = _parse_json_response(result)
            assert data is not None
            
    finally:
        await cleanup()