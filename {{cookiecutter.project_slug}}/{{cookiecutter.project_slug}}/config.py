"""Configuration management for {{cookiecutter.project_name}}

This module provides platform-aware configuration management using platformdirs
to ensure configuration files are stored in appropriate locations across different
operating systems.
"""

import os
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional

import platformdirs


@dataclass
class ServerConfig:
    """Configuration class for the MCP server."""
    
    # Server settings
    name: str = "{{cookiecutter.project_name}}"
    description: str = "{{cookiecutter.description}}"
    
    # Logging configuration (hardcoded defaults)
    log_level: str = "INFO"
    log_retention_days: int = 30
    
    # Logging destinations configuration
    logging_destinations: Dict[str, Any] = None
    
    # Server transport settings (hardcoded default)
    default_transport: str = "stdio"
    default_host: str = "127.0.0.1"
    default_port: int = {{cookiecutter.server_port}}
    
    # Streamable HTTP transport settings (always enabled, hardcoded defaults)
    streamable_http_enabled: bool = True
    streamable_http_endpoint: str = "/mcp"
    streamable_http_json_response: bool = False  # If True, return JSON responses instead of SSE streams
    
    {% if cookiecutter.include_oauth_backend == "yes" -%}
    # OAuth backend settings (from cookiecutter, can be overridden by environment)
    oauth_backend_url: str = "http://localhost:{{cookiecutter.oauth_backend_port}}"
    {% endif -%}
    
    # Platform-aware paths
    config_dir: Path = None
    data_dir: Path = None
    log_dir: Path = None
    
    # File paths (computed from directories)
    config_file_path: Path = None
    log_file_path: Path = None
    database_path: Path = None
    
    def __post_init__(self):
        """Initialize platform-aware paths after dataclass creation."""
        if self.config_dir is None:
            self.config_dir = Path(platformdirs.user_config_dir("{{cookiecutter.project_slug}}"))
        if self.data_dir is None:
            self.data_dir = Path(platformdirs.user_data_dir("{{cookiecutter.project_slug}}"))
        if self.log_dir is None:
            self.log_dir = Path(platformdirs.user_log_dir("{{cookiecutter.project_slug}}"))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set file paths
        self.config_file_path = self.config_dir / "config.yaml"
        self.log_file_path = self.log_dir / "{{cookiecutter.project_slug}}.log"
        self.database_path = self.data_dir / "{{cookiecutter.project_slug}}.db"
        
        # Initialize default logging destinations if not set
        if self.logging_destinations is None:
            self.logging_destinations = {
                "destinations": [
                    {
                        "type": "sqlite",
                        "enabled": True,
                        "settings": {}
                    }
                ]
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "log_level": self.log_level,
            "log_retention_days": self.log_retention_days,
            "logging_destinations": self.logging_destinations,
            "default_transport": self.default_transport,
            "default_host": self.default_host,
            "default_port": self.default_port,
            "streamable_http_enabled": self.streamable_http_enabled,
            "streamable_http_endpoint": self.streamable_http_endpoint,
            "streamable_http_json_response": self.streamable_http_json_response,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        """Create configuration from dictionary."""
        return cls(
            name=data.get("name", "{{cookiecutter.project_name}}"),
            description=data.get("description", "{{cookiecutter.description}}"),
            log_level=data.get("log_level", "INFO"),
            log_retention_days=data.get("log_retention_days", 30),
            logging_destinations=data.get("logging_destinations"),
            default_transport=data.get("default_transport", "stdio"),
            default_host=data.get("default_host", "127.0.0.1"),
            default_port=data.get("default_port", {{cookiecutter.server_port}}),
            streamable_http_enabled=data.get("streamable_http_enabled", True),
            streamable_http_endpoint=data.get("streamable_http_endpoint", "/mcp"),
            streamable_http_json_response=data.get("streamable_http_json_response", False),
        )
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file_path, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except Exception as e:
            print(f"Warning: Could not save configuration: {e}")
    
    @classmethod
    def load(cls) -> "ServerConfig":
        """Load configuration from file, creating default if not found."""
        config = cls()  # Create with defaults
        
        if config.config_file_path.exists():
            try:
                with open(config.config_file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        # Update with loaded values
                        loaded_config = cls.from_dict(data)
                        # Preserve the paths from the original config
                        loaded_config.config_dir = config.config_dir
                        loaded_config.data_dir = config.data_dir
                        loaded_config.log_dir = config.log_dir
                        loaded_config.config_file_path = config.config_file_path
                        loaded_config.log_file_path = config.log_file_path
                        loaded_config.database_path = config.database_path
                        config = loaded_config  # Use loaded config
            except Exception as e:
                print(f"Warning: Could not load configuration: {e}")
        
        # Override with environment variables if present
        # This allows temporary overrides without editing config.yaml
        if os.environ.get('LOG_LEVEL'):
            config.log_level = os.environ['LOG_LEVEL']
        if os.environ.get('LOG_RETENTION_DAYS'):
            config.log_retention_days = int(os.environ['LOG_RETENTION_DAYS'])
        if os.environ.get('DEFAULT_TRANSPORT'):
            config.default_transport = os.environ['DEFAULT_TRANSPORT']
        if os.environ.get('DEFAULT_PORT'):
            config.default_port = int(os.environ['DEFAULT_PORT'])
        if os.environ.get('DEFAULT_HOST'):
            config.default_host = os.environ['DEFAULT_HOST']
        {% if cookiecutter.include_oauth_backend == "yes" -%}
        if os.environ.get('OAUTH_BACKEND_URL'):
            config.oauth_backend_url = os.environ['OAUTH_BACKEND_URL']
        {% endif -%}
        
        # Save default configuration
        config.save()
        return config
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ServerConfig(name='{self.name}', log_level='{self.log_level}', transport='{self.default_transport}')"


@dataclass
class UIConfig:
    """Configuration class for the Streamlit admin UI."""
    
    # UI settings
    page_title: str = "{{cookiecutter.project_name}} Admin"
    page_icon: str = "🔧"
    layout: str = "wide"
    
    # Server connection settings
    server_host: str = "127.0.0.1"
    server_port: int = {{cookiecutter.server_port}}
    
    # UI features
    show_logs: bool = True
    show_config: bool = True
    show_tools: bool = True
    
    # Shared configuration (from ServerConfig)
    server_config: Optional[ServerConfig] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert UI configuration to dictionary."""
        return {
            "page_title": self.page_title,
            "page_icon": self.page_icon,
            "layout": self.layout,
            "server_host": self.server_host,
            "server_port": self.server_port,
            "show_logs": self.show_logs,
            "show_config": self.show_config,
            "show_tools": self.show_tools,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UIConfig":
        """Create UI configuration from dictionary."""
        return cls(
            page_title=data.get("page_title", "{{cookiecutter.project_name}} Admin"),
            page_icon=data.get("page_icon", "🔧"),
            layout=data.get("layout", "wide"),
            server_host=data.get("server_host", "127.0.0.1"),
            server_port=data.get("server_port", {{cookiecutter.server_port}}),
            show_logs=data.get("show_logs", True),
            show_config=data.get("show_config", True),
            show_tools=data.get("show_tools", True),
        )


# Global configuration instance
_config: Optional[ServerConfig] = None


def get_config() -> ServerConfig:
    """Get the global configuration instance, loading it if necessary."""
    global _config
    if _config is None:
        _config = ServerConfig.load()
    return _config


def reload_config() -> ServerConfig:
    """Reload configuration from file."""
    global _config
    _config = ServerConfig.load()
    return _config


def get_ui_config() -> UIConfig:
    """Get UI configuration with shared server config."""
    server_config = get_config()
    ui_config = UIConfig()
    ui_config.server_config = server_config
    return ui_config


def get_platform_info() -> Dict[str, str]:
    """Get platform-specific directory information."""
    return {
        "config_dir": str(platformdirs.user_config_dir("{{cookiecutter.project_slug}}")),
        "data_dir": str(platformdirs.user_data_dir("{{cookiecutter.project_slug}}")),
        "log_dir": str(platformdirs.user_log_dir("{{cookiecutter.project_slug}}")),
        "cache_dir": str(platformdirs.user_cache_dir("{{cookiecutter.project_slug}}")),
    }


if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(f"Configuration loaded: {config}")
    print(f"Platform info: {get_platform_info()}")
    print(f"Config file: {config.config_file_path}")
    print(f"Log file: {config.log_file_path}")
    print(f"Database: {config.database_path}")