"""System Information Analyzer Tool

This module provides a comprehensive system information analyzer tool that
collects CPU, memory, disk, and process metrics from the local machine.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

import psutil
from mcp.server.fastmcp import Context


async def system_info_analyzer(
    include_processes: bool = True,
    process_limit: int = 10,
    include_disk_io: bool = True,
    include_network: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    """Analyze and collect comprehensive system information.
    
    Collects detailed metrics about CPU, memory, disk, processes, and optionally
    network statistics from the local machine.
    
    Args:
        include_processes: Whether to include detailed process information (default: True)
        process_limit: Maximum number of top processes to return (default: 10)
        include_disk_io: Whether to include disk I/O statistics (default: True)
        include_network: Whether to include network I/O statistics (default: False)
        ctx: MCP Context object (provided by MCP runtime)
        
    Returns:
        Dictionary containing comprehensive system metrics including:
        - CPU: utilization, core counts, frequency, load average
        - Memory: total, available, used, percentage, swap info
        - Disk: partitions with usage, optional I/O counters
        - Processes: top processes by CPU and memory (if included)
        - Network: I/O statistics (if included)
        - System: boot time and uptime
    """
    result = {}
    
    # CPU Information
    cpu_info = {
        "percent": psutil.cpu_percent(interval=1),
        "count_logical": psutil.cpu_count(logical=True),
        "count_physical": psutil.cpu_count(logical=False),
        "per_core_percent": psutil.cpu_percent(interval=0.1, percpu=True)
    }
    
    # Add CPU frequency if available
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info["frequency_mhz"] = cpu_freq.current
            cpu_info["frequency_min_mhz"] = cpu_freq.min
            cpu_info["frequency_max_mhz"] = cpu_freq.max
    except Exception:
        # Not available on all platforms
        pass
    
    # Add load average (Unix-like systems only)
    try:
        load_avg = psutil.getloadavg()
        cpu_info["load_average"] = list(load_avg)  # 1, 5, 15 minute averages
    except (AttributeError, OSError):
        # Not available on Windows
        cpu_info["load_average"] = None
    
    result["cpu"] = cpu_info
    
    # Memory Information
    vm = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    memory_info = {
        "total_gb": round(vm.total / (1024**3), 2),
        "available_gb": round(vm.available / (1024**3), 2),
        "used_gb": round(vm.used / (1024**3), 2),
        "percent": vm.percent,
        "swap_total_gb": round(swap.total / (1024**3), 2),
        "swap_used_gb": round(swap.used / (1024**3), 2),
        "swap_percent": swap.percent
    }
    result["memory"] = memory_info
    
    # Disk Information
    disk_info = {"partitions": []}
    
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partition_info = {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent": usage.percent
            }
            disk_info["partitions"].append(partition_info)
        except PermissionError:
            # This can happen on Windows
            continue
    
    # Disk I/O Counters (if requested)
    if include_disk_io:
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                disk_info["io_counters"] = {
                    "read_gb": round(disk_io.read_bytes / (1024**3), 2),
                    "write_gb": round(disk_io.write_bytes / (1024**3), 2),
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count,
                    "read_time_ms": disk_io.read_time,
                    "write_time_ms": disk_io.write_time
                }
        except Exception:
            # May not be available on all systems
            pass
    
    result["disk"] = disk_info
    
    # Process Information (if requested)
    if include_processes:
        processes_info = {
            "total_count": len(psutil.pids())
        }
        
        # Get all processes with their info
        process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                pinfo = proc.info
                # Get CPU percent (non-blocking)
                pinfo['cpu_percent'] = proc.cpu_percent(interval=0)
                process_list.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        top_cpu = sorted(
            process_list,
            key=lambda x: x.get('cpu_percent', 0),
            reverse=True
        )[:process_limit]
        
        # Sort by memory usage
        top_memory = sorted(
            process_list,
            key=lambda x: x.get('memory_percent', 0),
            reverse=True
        )[:process_limit]
        
        # Format process info for output
        processes_info["top_by_cpu"] = [
            {
                "pid": p['pid'],
                "name": p['name'],
                "cpu_percent": round(p.get('cpu_percent', 0), 2),
                "memory_mb": round(p['memory_info'].rss / (1024**2), 2) if 'memory_info' in p else 0
            }
            for p in top_cpu
        ]
        
        processes_info["top_by_memory"] = [
            {
                "pid": p['pid'],
                "name": p['name'],
                "memory_percent": round(p.get('memory_percent', 0), 2),
                "memory_mb": round(p['memory_info'].rss / (1024**2), 2) if 'memory_info' in p else 0
            }
            for p in top_memory
        ]
        
        result["processes"] = processes_info
    
    # Network Information (if requested)
    if include_network:
        try:
            net_io = psutil.net_io_counters()
            network_info = {
                "bytes_sent_gb": round(net_io.bytes_sent / (1024**3), 2),
                "bytes_recv_gb": round(net_io.bytes_recv / (1024**3), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_in": net_io.errin,
                "errors_out": net_io.errout,
                "drop_in": net_io.dropin,
                "drop_out": net_io.dropout
            }
            result["network"] = network_info
        except Exception:
            # May not be available on all systems
            pass
    
    # System Information
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    
    system_info = {
        "boot_time": boot_time.isoformat(),
        "uptime_hours": round(uptime.total_seconds() / 3600, 2),
        "uptime_days": uptime.days
    }
    
    # Add platform info
    import platform
    system_info["platform"] = platform.system()
    system_info["platform_release"] = platform.release()
    system_info["platform_version"] = platform.version()
    system_info["architecture"] = platform.machine()
    system_info["hostname"] = platform.node()
    system_info["python_version"] = platform.python_version()
    
    result["system"] = system_info
    
    return result


# Export the tool for registration
system_analyzer_tools = [system_info_analyzer]


if __name__ == "__main__":
    # Test the tool
    async def test():
        print("Testing System Information Analyzer...")
        result = await system_info_analyzer(
            include_processes=True,
            process_limit=5,
            include_disk_io=True,
            include_network=True
        )
        
        import json
        print(json.dumps(result, indent=2))
    
    asyncio.run(test())