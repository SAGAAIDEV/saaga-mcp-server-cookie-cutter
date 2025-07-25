"""Configuration management for Test Config Server

This module provides platform-aware configuration management using platformdirs
to ensure configuration files are stored in appropriate locations across different
operating systems.
"""

import os
import yaml
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import platformdirs


@dataclass
class ServerConfig:
    """Configuration class for the MCP server."""
    
    # Server settings
    name: str = "Test Config Server"
    description: str = "MCP server with SAAGA decorators"
    
    # Logging configuration
    log_level: str = "INFO"
    log_retention_days: int = 30
    
    # Server transport settings
    default_transport: str = "stdio"
    default_host: str = "127.0.0.1"
    default_port: int = 3001
    
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
            self.config_dir = Path(platformdirs.user_config_dir("test_config_server"))
        if self.data_dir is None:
            self.data_dir = Path(platformdirs.user_data_dir("test_config_server"))
        if self.log_dir is None:
            self.log_dir = Path(platformdirs.user_log_dir("test_config_server"))
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set file paths
        self.config_file_path = self.config_dir / "config.yaml"
        self.log_file_path = self.log_dir / "test_config_server.log"
        self.database_path = self.data_dir / "test_config_server.db"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "log_level": self.log_level,
            "log_retention_days": self.log_retention_days,
            "default_transport": self.default_transport,
            "default_host": self.default_host,
            "default_port": self.default_port,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        """Create configuration from dictionary."""
        return cls(
            name=data.get("name", "Test Config Server"),
            description=data.get("description", "MCP server with SAAGA decorators"),
            log_level=data.get("log_level", "INFO"),
            log_retention_days=data.get("log_retention_days", 30),
            default_transport=data.get("default_transport", "stdio"),
            default_host=data.get("default_host", "127.0.0.1"),
            default_port=data.get("default_port", 3001),
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
                        return loaded_config
            except Exception as e:
                print(f"Warning: Could not load configuration: {e}")
        
        # Save default configuration
        config.save()
        return config
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"ServerConfig(name='{self.name}', log_level='{self.log_level}', transport='{self.default_transport}')"


def validate_config_file(config_path: Path) -> Dict[str, Any]:
    """
    Validate configuration file structure and content.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dict with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "version": None
    }
    
    try:
        if not config_path.exists():
            results["errors"].append(f"Configuration file not found: {config_path}")
            results["valid"] = False
            return results
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not config:
            results["errors"].append("Configuration file is empty or invalid YAML")
            results["valid"] = False
            return results
        
        # Check version
        version = config.get("version", 0)
        results["version"] = version
        
        if version == 0:
            results["warnings"].append("Configuration version not specified, assuming version 0")
        
        # Validate required sections
        required_sections = ["server", "logging", "tools", "features"]
        for section in required_sections:
            if section not in config:
                results["errors"].append(f"Missing required section: {section}")
                results["valid"] = False
        
        # Validate server section
        if "server" in config:
            server = config["server"]
            
            # Validate port
            port = server.get("port")
            if not isinstance(port, int) or not (1 <= port <= 65535):
                results["errors"].append("Server port must be an integer between 1 and 65535")
                results["valid"] = False
            
            # Validate log level
            log_level = server.get("log_level", "").upper()
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if log_level not in valid_levels:
                results["errors"].append(f"Log level must be one of: {', '.join(valid_levels)}")
                results["valid"] = False
        
        # Validate tools section
        if "tools" in config:
            tools = config["tools"]
            if "tool_timeout_seconds" in tools:
                timeout = tools["tool_timeout_seconds"]
                if not isinstance(timeout, int) or timeout <= 0:
                    results["errors"].append("tool_timeout_seconds must be a positive integer")
                    results["valid"] = False
        
    except yaml.YAMLError as e:
        results["errors"].append(f"Invalid YAML syntax: {str(e)}")
        results["valid"] = False
    except Exception as e:
        results["errors"].append(f"Configuration validation error: {str(e)}")
        results["valid"] = False
    
    return results


def check_config_compatibility(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check configuration version compatibility.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict with compatibility information
    """
    current_version = 1
    config_version = config.get("version", 0)
    
    return {
        "compatible": config_version <= current_version,
        "version": config_version,
        "current_version": current_version,
        "upgrade_needed": config_version < current_version,
        "downgrade_needed": config_version > current_version,
        "migration_available": config_version < current_version,
        "supported_versions": [0, 1]
    }


def migrate_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate old configuration to current version.
    
    Args:
        old_config: Configuration dictionary to migrate
        
    Returns:
        Migrated configuration dictionary
    """
    migrated_config = old_config.copy()
    old_version = old_config.get("version", 0)
    
    # Migration from version 0 to 1
    if old_version == 0:
        # Add version field
        migrated_config["version"] = 1
        
        # Migrate server section
        if "server" not in migrated_config:
            migrated_config["server"] = {}
        
        # Add missing server fields with defaults
        server_defaults = {
            "name": "Test Config Server",
            "description": "MCP server with SAAGA decorators",
            "port": 3001,
            "host": "127.0.0.1",
            "transport": "stdio",
            "log_level": "INFO",
            "log_retention_days": 30
        }
        
        for key, value in server_defaults.items():
            if key not in migrated_config["server"]:
                migrated_config["server"][key] = value
        
        # Migrate logging section
        if "logging" not in migrated_config:
            migrated_config["logging"] = {
                "level": migrated_config["server"].get("log_level", "INFO"),
                "retention_days": migrated_config["server"].get("log_retention_days", 30),
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "database_logging": True,
                "file_logging": True
            }
        
        # Migrate tools section
        if "tools" not in migrated_config:
            migrated_config["tools"] = {
                "enabled_tools": [],
                "tool_timeout_seconds": 300
            }
        
        # Migrate features section
        if "features" not in migrated_config:
            migrated_config["features"] = {
                "admin_ui": False,
                "example_tools": True,
                "parallel_examples": True,
                "database_logging": True,
                "file_logging": True,
                "auto_reload": False
            }
    
    return migrated_config


def backup_config(config_path: Path) -> bool:
    """
    Create backup of configuration file before updates.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        True if backup successful, False otherwise
    """
    try:
        if not config_path.exists():
            return True  # No file to backup
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.parent / f"{config_path.stem}.backup.{timestamp}{config_path.suffix}"
        
        shutil.copy2(config_path, backup_path)
        
        # Clean up old backups (keep only last 5)
        backup_pattern = f"{config_path.stem}.backup.*{config_path.suffix}"
        backup_files = sorted(config_path.parent.glob(backup_pattern), key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_backup in backup_files[5:]:
            old_backup.unlink()
        
        return True
    except Exception:
        return False


def get_example_configurations() -> Dict[str, Dict[str, Any]]:
    """
    Get example configurations for common use cases.
    
    Returns:
        Dict with example configuration scenarios
    """
    return {
        "development": {
            "version": 1,
            "server": {
                "name": "Test Config Server Dev",
                "port": 3001,
                "log_level": "DEBUG"
            },
            "development": {
                "debug_mode": True,
                "auto_reload": True,
                "profiling_enabled": True
            },
            "features": {
                "admin_ui": True,
                "example_tools": True
            }
        },
        "production": {
            "version": 1,
            "server": {
                "name": "Test Config Server Prod",
                "port": 3001,
                "log_level": "INFO"
            },
            "security": {
                "enable_cors": True,
                "api_key_required": True,
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            },
            "performance": {
                "cache_enabled": True,
                "connection_pool_size": 20
            }
        },
        "testing": {
            "version": 1,
            "server": {
                "name": "Test Config Server Test",
                "port": 3001,
                "log_level": "WARNING"
            },
            "development": {
                "mock_external_services": True
            },
            "features": {
                "admin_ui": False,
                "example_tools": True
            }
        }
    }


def perform_config_health_check(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Perform comprehensive health check on configuration.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Dict with health check results
    """
    if config_path is None:
        config_path = ServerConfig().config_file_path
    
    health_status = {
        "overall_health": "healthy",
        "checks": {},
        "recommendations": [],
        "warnings": [],
        "errors": []
    }
    
    try:
        # File existence check
        health_status["checks"]["file_exists"] = config_path.exists()
        if not config_path.exists():
            health_status["errors"].append("Configuration file does not exist")
            health_status["overall_health"] = "critical"
            return health_status
        
        # File validation check
        validation_result = validate_config_file(config_path)
        health_status["checks"]["file_valid"] = validation_result["valid"]
        health_status["errors"].extend(validation_result["errors"])
        health_status["warnings"].extend(validation_result["warnings"])
        
        if not validation_result["valid"]:
            health_status["overall_health"] = "critical"
            return health_status
        
        # Load configuration for further checks
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Version compatibility check
        compatibility = check_config_compatibility(config)
        health_status["checks"]["version_compatible"] = compatibility["compatible"]
        
        if compatibility["upgrade_needed"]:
            health_status["recommendations"].append(f"Configuration version {compatibility['version']} can be upgraded to {compatibility['current_version']}")
            health_status["overall_health"] = "warning" if health_status["overall_health"] == "healthy" else health_status["overall_health"]
        
        if compatibility["downgrade_needed"]:
            health_status["errors"].append(f"Configuration version {compatibility['version']} is newer than supported version {compatibility['current_version']}")
            health_status["overall_health"] = "critical"
        
        # Port availability check (simplified)
        server_port = config.get("server", {}).get("port", 3001)
        health_status["checks"]["port_valid"] = isinstance(server_port, int) and 1 <= server_port <= 65535
        
        # Directory permissions check
        config_dir = config_path.parent
        health_status["checks"]["directory_writable"] = os.access(config_dir, os.W_OK)
        
        if not health_status["checks"]["directory_writable"]:
            health_status["errors"].append(f"Configuration directory is not writable: {config_dir}")
            health_status["overall_health"] = "critical"
        
        # Set overall health based on errors and warnings
        if health_status["errors"]:
            health_status["overall_health"] = "critical"
        elif health_status["warnings"] or health_status["recommendations"]:
            health_status["overall_health"] = "warning"
        
    except Exception as e:
        health_status["errors"].append(f"Health check failed: {str(e)}")
        health_status["overall_health"] = "critical"
    
    return health_status


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


def get_platform_info() -> Dict[str, str]:
    """Get platform-specific directory information."""
    return {
        "config_dir": str(platformdirs.user_config_dir("test_config_server")),
        "data_dir": str(platformdirs.user_data_dir("test_config_server")),
        "log_dir": str(platformdirs.user_log_dir("test_config_server")),
        "cache_dir": str(platformdirs.user_cache_dir("test_config_server")),
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--validate":
        # Configuration validation mode
        config = get_config()
        validation_result = validate_config_file(config.config_file_path)
        
        if validation_result["valid"]:
            print("✅ Configuration is valid")
            sys.exit(0)
        else:
            print("❌ Configuration validation failed:")
            for error in validation_result["errors"]:
                print(f"  - {error}")
            sys.exit(1)
    
    elif len(sys.argv) > 1 and sys.argv[1] == "--health-check":
        # Configuration health check mode
        config = get_config()
        health_status = perform_config_health_check(config.config_file_path)
        
        print(f"🏥 Configuration Health: {health_status['overall_health'].upper()}")
        
        if health_status["errors"]:
            print("\n❌ Errors:")
            for error in health_status["errors"]:
                print(f"  - {error}")
        
        if health_status["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in health_status["warnings"]:
                print(f"  - {warning}")
        
        if health_status["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in health_status["recommendations"]:
                print(f"  - {rec}")
        
        sys.exit(0 if health_status["overall_health"] in ["healthy", "warning"] else 1)
    
    else:
        # Default: Test configuration loading
        config = get_config()
        print(f"Configuration loaded: {config}")
        print(f"Platform info: {get_platform_info()}")
        print(f"Config file: {config.config_file_path}")
        print(f"Log file: {config.log_file_path}")
        print(f"Database: {config.database_path}")