"""{% if cookiecutter.include_admin_ui == "yes" %}
Utility functions for {{cookiecutter.project_name}} Admin UI

This module provides helper functions for the Streamlit admin interface,
including server status checking, configuration management, and data processing.
{% else %}
Placeholder for optional Streamlit admin UI utilities.
{% endif %}"""

{% if cookiecutter.include_admin_ui == "yes" %}
import os
import sys
import platform
import socket
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import json
import yaml
import sqlite3

def check_server_status() -> str:
    """
    Check if the MCP server is running
    
    Returns:
        str: Server status ("running", "stopped", "unknown")
    """
    try:
        # Try to connect to the server port
        port = {{cookiecutter.server_port}}
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return "running" if result == 0 else "stopped"
    except Exception:
        return "unknown"

def get_project_info() -> Dict[str, Any]:
    """
    Get project information and metadata
    
    Returns:
        Dict containing project details
    """
    return {
        "name": "{{cookiecutter.project_name}}",
        "description": "{{cookiecutter.description}}",
        "author": "{{cookiecutter.author_name}}",
        "email": "{{cookiecutter.author_email}}",
        "version": "0.1.0",
        "python_version": "{{cookiecutter.python_version}}",
        "server_port": {{cookiecutter.server_port}},
        "log_level": "{{cookiecutter.log_level}}",
        "log_retention_days": {{cookiecutter.log_retention_days}},
        "features": {
            "admin_ui": True,
            "example_tools": {{cookiecutter.include_example_tools == "yes"}},
            "parallel_examples": {{cookiecutter.include_parallel_example == "yes"}}
        }
    }

def get_system_info() -> Dict[str, Any]:
    """
    Get system and runtime information
    
    Returns:
        Dict containing system details
    """
    try:
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "python_executable": sys.executable,
            "current_directory": str(Path.cwd()),
            "config_path": get_config_path(),
            "log_path": get_log_path(),
            "data_path": get_data_path()
        }
    except Exception as e:
        return {"error": str(e)}

def get_config_path() -> str:
    """Get the platform-appropriate configuration directory path"""
    if platform.system() == "Windows":
        base_path = Path(os.environ.get("APPDATA", "~")).expanduser()
    elif platform.system() == "Darwin":  # macOS
        base_path = Path("~/Library/Application Support").expanduser()
    else:  # Linux and others
        base_path = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser()
    
    return str(base_path / "{{cookiecutter.project_slug}}")

def get_log_path() -> str:
    """Get the platform-appropriate log directory path"""
    if platform.system() == "Windows":
        base_path = Path(os.environ.get("LOCALAPPDATA", "~")).expanduser()
    elif platform.system() == "Darwin":  # macOS
        base_path = Path("~/Library/Logs").expanduser()
    else:  # Linux and others
        base_path = Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser()
    
    return str(base_path / "{{cookiecutter.project_slug}}")

def get_data_path() -> str:
    """Get the platform-appropriate data directory path"""
    if platform.system() == "Windows":
        base_path = Path(os.environ.get("LOCALAPPDATA", "~")).expanduser()
    elif platform.system() == "Darwin":  # macOS
        base_path = Path("~/Library/Application Support").expanduser()
    else:  # Linux and others
        base_path = Path(os.environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser()
    
    return str(base_path / "{{cookiecutter.project_slug}}")

def load_configuration(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Dict containing configuration
    """
    if config_path is None:
        config_path = Path(get_config_path()) / "config.yaml"
    else:
        config_path = Path(config_path)
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        else:
            # Return default configuration
            return get_default_configuration()
    except Exception as e:
        return {"error": f"Failed to load configuration: {str(e)}"}

def get_default_configuration() -> Dict[str, Any]:
    """Get the default configuration"""
    return {
        "server": {
            "name": "{{cookiecutter.project_name}}",
            "port": {{cookiecutter.server_port}},
            "log_level": "{{cookiecutter.log_level}}"
        },
        "logging": {
            "level": "{{cookiecutter.log_level}}",
            "retention_days": {{cookiecutter.log_retention_days}},
            "database_path": str(Path(get_data_path()) / "logs.db")
        },
        "features": {
            "admin_ui": True,
            "example_tools": {{cookiecutter.include_example_tools == "yes"}},
            "parallel_examples": {{cookiecutter.include_parallel_example == "yes"}}
        },
        "paths": {
            "config": get_config_path(),
            "logs": get_log_path(),
            "data": get_data_path()
        }
    }

def validate_configuration(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration structure and values
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Dict with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Check required sections
        required_sections = ["server", "logging", "features", "paths"]
        for section in required_sections:
            if section not in config:
                results["errors"].append(f"Missing required section: {section}")
                results["valid"] = False
        
        # Validate server configuration
        if "server" in config:
            server_config = config["server"]
            
            # Check port
            port = server_config.get("port")
            if not isinstance(port, int) or not (1 <= port <= 65535):
                results["errors"].append("Server port must be an integer between 1 and 65535")
                results["valid"] = False
            
            # Check log level
            log_level = server_config.get("log_level", "").upper()
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if log_level not in valid_levels:
                results["errors"].append(f"Log level must be one of: {', '.join(valid_levels)}")
                results["valid"] = False
        
        # Validate paths
        if "paths" in config:
            paths_config = config["paths"]
            for path_name, path_value in paths_config.items():
                if path_value and not isinstance(path_value, str):
                    results["warnings"].append(f"Path '{path_name}' should be a string")
        
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Configuration validation error: {str(e)}")
    
    return results

def save_configuration(config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary to save
        config_path: Optional path to save configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    if config_path is None:
        config_path = Path(get_config_path()) / "config.yaml"
    else:
        config_path = Path(config_path)
    
    try:
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return True
    except Exception:
        return False

def load_logs_from_database(db_path: Optional[str] = None, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Load log entries from SQLite database
    
    Args:
        db_path: Optional path to database file
        limit: Maximum number of entries to load
        
    Returns:
        List of log entries
    """
    if db_path is None:
        db_path = Path(get_data_path()) / "logs.db"
    
    try:
        if not Path(db_path).exists():
            return []
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception:
        return []

def filter_logs(logs: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter log entries based on criteria
    
    Args:
        logs: List of log entries
        filters: Filter criteria
        
    Returns:
        Filtered list of log entries
    """
    filtered_logs = logs.copy()
    
    try:
        # Filter by level
        if filters.get("level"):
            filtered_logs = [log for log in filtered_logs 
                           if log.get("level") == filters["level"]]
        
        # Filter by tool
        if filters.get("tool"):
            filtered_logs = [log for log in filtered_logs 
                           if log.get("tool_name") == filters["tool"]]
        
        # Filter by status
        if filters.get("status"):
            filtered_logs = [log for log in filtered_logs 
                           if log.get("status") == filters["status"]]
        
        # Filter by date range
        if filters.get("date_from") or filters.get("date_to"):
            # This would require proper date parsing
            pass
        
        # Filter by search term
        if filters.get("search"):
            search_term = filters["search"].lower()
            filtered_logs = [log for log in filtered_logs 
                           if search_term in str(log.get("input_args", "")).lower() or
                              search_term in str(log.get("output_summary", "")).lower()]
    
    except Exception:
        # Return original logs if filtering fails
        pass
    
    return filtered_logs

def export_logs(logs: List[Dict[str, Any]], format: str, filename: str) -> Optional[bytes]:
    """
    Export log entries to specified format
    
    Args:
        logs: List of log entries
        format: Export format ('csv', 'json', 'excel')
        filename: Output filename
        
    Returns:
        Exported data as bytes, or None if failed
    """
    try:
        if format.lower() == "json":
            data = json.dumps(logs, indent=2, default=str)
            return data.encode('utf-8')
        
        # CSV and Excel export would require additional libraries
        # This is a placeholder for Phase 4, Issue 3
        return None
    
    except Exception:
        return None

def get_log_statistics(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics from log entries
    
    Args:
        logs: List of log entries
        
    Returns:
        Dict containing statistics
    """
    if not logs:
        return {
            "total_logs": 0,
            "error_rate": 0,
            "avg_duration_ms": 0,
            "active_tools": 0
        }
    
    try:
        total_logs = len(logs)
        error_count = len([log for log in logs if log.get("status") == "error"])
        error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
        
        durations = [log.get("duration_ms", 0) for log in logs if log.get("duration_ms")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        unique_tools = len(set(log.get("tool_name") for log in logs if log.get("tool_name")))
        
        return {
            "total_logs": total_logs,
            "error_rate": error_rate,
            "avg_duration_ms": avg_duration,
            "active_tools": unique_tools,
            "error_count": error_count
        }
    
    except Exception:
        return {
            "total_logs": len(logs),
            "error_rate": 0,
            "avg_duration_ms": 0,
            "active_tools": 0
        }

def format_uptime(start_time: datetime) -> str:
    """
    Format uptime duration
    
    Args:
        start_time: Server start timestamp
        
    Returns:
        Formatted uptime string
    """
    try:
        uptime = datetime.now() - start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    except Exception:
        return "Unknown"

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    try:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    except Exception:
        return "Unknown"

def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for use
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False
{% endif %}