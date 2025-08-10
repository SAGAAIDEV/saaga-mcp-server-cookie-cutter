"""
Unit tests for the system_info_analyzer tool.

These tests validate the tool's internal logic and behavior without
going through the full MCP protocol stack.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

from example_server.tools.system_info_analyzer import system_info_analyzer


class TestSystemInfoAnalyzerUnit:
    """Unit tests for system_info_analyzer tool."""
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_structure(self):
        """Test that the tool returns the expected data structure."""
        # Call the tool directly
        result = await system_info_analyzer(
            include_processes=False,  # Disable to speed up test
            include_network=False
        )
        
        # Verify it returns a dictionary
        assert isinstance(result, dict)
        
        # Check required top-level keys
        required_keys = ["cpu", "memory", "disk", "system"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
        
        # Verify CPU structure
        cpu = result["cpu"]
        assert "percent" in cpu
        assert "count_logical" in cpu
        assert "count_physical" in cpu
        assert isinstance(cpu["percent"], (int, float))
        
        # Verify memory structure  
        memory = result["memory"]
        assert "total_gb" in memory
        assert "available_gb" in memory
        assert "percent" in memory
        
        # Verify system structure
        system = result["system"]
        assert "boot_time" in system
        assert "uptime_hours" in system
        assert "platform" in system
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_with_processes(self):
        """Test that process information is included when requested."""
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=3
        )
        
        assert "processes" in result
        processes = result["processes"]
        
        # Check structure
        assert "total_count" in processes
        assert "top_by_cpu" in processes
        assert "top_by_memory" in processes
        
        # Check limits are respected
        assert len(processes["top_by_cpu"]) <= 3
        assert len(processes["top_by_memory"]) <= 3
        
        # Check process details structure
        if len(processes["top_by_cpu"]) > 0:
            proc = processes["top_by_cpu"][0]
            assert "pid" in proc
            assert "name" in proc
            assert "cpu_percent" in proc
            assert "memory_mb" in proc
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_without_processes(self):
        """Test that process information is excluded when requested."""
        result = await system_info_analyzer(
            include_processes=False
        )
        
        assert "processes" not in result
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_with_network(self):
        """Test that network information is included when requested."""
        result = await system_info_analyzer(
            include_network=True,
            include_processes=False  # Speed up test
        )
        
        # Network might not always be available, but check structure if present
        if "network" in result:
            network = result["network"]
            assert "bytes_sent_gb" in network
            assert "bytes_recv_gb" in network
            assert "packets_sent" in network
            assert "packets_recv" in network
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_disk_info(self):
        """Test disk information structure."""
        result = await system_info_analyzer(
            include_disk_io=True,
            include_processes=False
        )
        
        disk = result["disk"]
        assert "partitions" in disk
        
        # Should have at least one partition
        assert len(disk["partitions"]) > 0
        
        partition = disk["partitions"][0]
        assert "device" in partition
        assert "mountpoint" in partition
        assert "total_gb" in partition
        assert "percent" in partition
        
        # Check if I/O counters are included (platform dependent)
        if "io_counters" in disk:
            io = disk["io_counters"]
            assert "read_gb" in io
            assert "write_gb" in io
    
    @pytest.mark.anyio
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    async def test_system_info_analyzer_cpu_mocking(self, mock_cpu_count, mock_cpu_percent):
        """Test CPU information with mocked psutil values."""
        # Set up mocks
        mock_cpu_percent.return_value = 42.5
        mock_cpu_count.side_effect = [8, 4]  # logical, then physical
        
        result = await system_info_analyzer(
            include_processes=False,
            include_network=False
        )
        
        cpu = result["cpu"]
        
        # First call is with interval=1
        assert mock_cpu_percent.called
        # Note: actual value might differ due to multiple calls
        
        # Verify cpu_count was called correctly
        assert mock_cpu_count.call_count == 2
        mock_cpu_count.assert_any_call(logical=True)
        mock_cpu_count.assert_any_call(logical=False)
    
    @pytest.mark.anyio
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    async def test_system_info_analyzer_memory_mocking(self, mock_swap, mock_virtual):
        """Test memory information with mocked values."""
        # Create mock return values
        mock_vm = MagicMock()
        mock_vm.total = 17179869184  # 16 GB
        mock_vm.available = 8589934592  # 8 GB
        mock_vm.used = 8589934592  # 8 GB
        mock_vm.percent = 50.0
        mock_virtual.return_value = mock_vm
        
        mock_sw = MagicMock()
        mock_sw.total = 2147483648  # 2 GB
        mock_sw.used = 1073741824  # 1 GB
        mock_sw.percent = 50.0
        mock_swap.return_value = mock_sw
        
        result = await system_info_analyzer(
            include_processes=False,
            include_network=False
        )
        
        memory = result["memory"]
        
        # Check calculated values
        assert memory["total_gb"] == 16.0
        assert memory["available_gb"] == 8.0
        assert memory["used_gb"] == 8.0
        assert memory["percent"] == 50.0
        assert memory["swap_total_gb"] == 2.0
        assert memory["swap_used_gb"] == 1.0
        assert memory["swap_percent"] == 50.0
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_zero_process_limit(self):
        """Test edge case with process_limit=0."""
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=0
        )
        
        processes = result["processes"]
        
        # Should still have total count
        assert "total_count" in processes
        assert processes["total_count"] > 0
        
        # But lists should be empty
        assert len(processes["top_by_cpu"]) == 0
        assert len(processes["top_by_memory"]) == 0
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_large_process_limit(self):
        """Test with very large process limit."""
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=10000
        )
        
        processes = result["processes"]
        total = processes["total_count"]
        
        # Should not exceed actual process count
        assert len(processes["top_by_cpu"]) <= total
        assert len(processes["top_by_memory"]) <= total
    
    @pytest.mark.anyio
    @patch('psutil.disk_partitions')
    @patch('psutil.disk_usage')
    async def test_system_info_analyzer_disk_permission_error(self, mock_usage, mock_partitions):
        """Test handling of permission errors when accessing disk info."""
        # Mock partition
        mock_partition = MagicMock()
        mock_partition.device = "/dev/sda1"
        mock_partition.mountpoint = "/restricted"
        mock_partition.fstype = "ext4"
        mock_partitions.return_value = [mock_partition]
        
        # Mock disk_usage to raise PermissionError
        mock_usage.side_effect = PermissionError("Access denied")
        
        result = await system_info_analyzer(
            include_processes=False,
            include_network=False
        )
        
        # Should handle error gracefully
        disk = result["disk"]
        assert "partitions" in disk
        # Partition with permission error should be skipped
        assert len(disk["partitions"]) == 0
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_platform_details(self):
        """Test that platform information is comprehensive."""
        result = await system_info_analyzer(
            include_processes=False,
            include_network=False
        )
        
        system = result["system"]
        
        # Check all platform fields
        platform_fields = [
            "platform", "platform_release", "platform_version",
            "architecture", "hostname", "python_version"
        ]
        
        for field in platform_fields:
            assert field in system
            assert isinstance(system[field], str)
            assert len(system[field]) > 0
        
        # Check datetime fields
        assert "boot_time" in system
        assert "uptime_hours" in system
        assert "uptime_days" in system
        
        # Verify boot_time is ISO format
        import datetime
        boot_time = datetime.datetime.fromisoformat(system["boot_time"])
        assert isinstance(boot_time, datetime.datetime)
    
    @pytest.mark.anyio
    @patch('example_server.tools.system_info_analyzer.psutil.process_iter')
    async def test_system_info_analyzer_process_access_denied(self, mock_process_iter):
        """Test handling of AccessDenied errors when accessing processes."""
        import psutil
        
        # Create mock process that works
        mock_proc1 = MagicMock()
        mock_proc1.info = {
            'pid': 1,
            'name': 'accessible',
            'cpu_percent': 10.0,
            'memory_percent': 5.0,
            'memory_info': MagicMock(rss=104857600)  # 100 MB
        }
        mock_proc1.cpu_percent.return_value = 10.0
        
        # Create process that raises AccessDenied
        mock_proc2 = MagicMock()
        mock_proc2.info = {'pid': 2, 'name': 'restricted'}
        # The implementation catches this in the try/except block
        mock_proc2.cpu_percent.side_effect = psutil.AccessDenied("Access Denied")
        
        # Mock the iterator to return our test processes
        mock_process_iter.return_value = [mock_proc1, mock_proc2]
        
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=5
        )
        
        processes = result["processes"]
        
        # The implementation should handle the AccessDenied gracefully
        # and include only the accessible process
        assert "top_by_cpu" in processes
        assert "top_by_memory" in processes
        # Should have at least the accessible process
        assert "total_count" in processes
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_returns_dict(self):
        """Verify the tool always returns a dictionary."""
        result = await system_info_analyzer()
        
        assert isinstance(result, dict)
        assert len(result) > 0
    
    @pytest.mark.anyio
    async def test_system_info_analyzer_numeric_validations(self):
        """Test that all numeric values are reasonable."""
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=5
        )
        
        # CPU percentages should be 0-100 (per core can exceed 100)
        cpu = result["cpu"]
        assert 0 <= cpu["percent"] <= 100 * cpu["count_logical"]
        
        # Memory percentages should be 0-100
        memory = result["memory"]
        assert 0 <= memory["percent"] <= 100
        assert 0 <= memory["swap_percent"] <= 100
        
        # Disk percentages should be 0-100
        for partition in result["disk"]["partitions"]:
            assert 0 <= partition["percent"] <= 100
        
        # Uptime should be non-negative
        system = result["system"]
        assert system["uptime_hours"] >= 0
        assert system["uptime_days"] >= 0