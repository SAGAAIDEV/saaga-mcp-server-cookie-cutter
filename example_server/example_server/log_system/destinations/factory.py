"""
Factory for creating log destinations based on configuration.
"""
from typing import Dict, List, Type, Optional, Any
from dataclasses import dataclass
import asyncio

from .base import LogDestination, LogEntry
from .sqlite import SQLiteDestination


@dataclass
class DestinationConfig:
    """Configuration for a single log destination."""
    type: str
    enabled: bool = True
    settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}


class MultiDestination(LogDestination):
    """Composite destination that writes to multiple destinations concurrently."""
    
    def __init__(self, destinations: List[LogDestination]):
        self.destinations = destinations
    
    async def write(self, entry: LogEntry) -> None:
        """Write to all destinations concurrently, ignoring individual failures."""
        if not self.destinations:
            return
            
        # Create tasks for all destinations
        tasks = []
        for dest in self.destinations:
            task = asyncio.create_task(self._write_ignore_errors(dest, entry))
            tasks.append(task)
        
        # Wait for all to complete (but don't raise exceptions)
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _write_ignore_errors(self, dest: LogDestination, entry: LogEntry) -> None:
        """Write to a single destination, ignoring errors."""
        try:
            await dest.write(entry)
        except Exception:
            # Silently ignore errors from individual destinations
            pass
    
    async def query(self, **filters) -> List[LogEntry]:
        """Query the first destination that supports querying."""
        for dest in self.destinations:
            try:
                return await dest.query(**filters)
            except NotImplementedError:
                continue
            except Exception:
                continue
        return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get stats from the first destination that supports it."""
        for dest in self.destinations:
            try:
                if hasattr(dest, 'get_stats'):
                    return await dest.get_stats()
            except Exception:
                continue
        return {}
    
    async def close(self) -> None:
        """Close all destinations."""
        tasks = []
        for dest in self.destinations:
            task = asyncio.create_task(self._close_ignore_errors(dest))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _close_ignore_errors(self, dest: LogDestination) -> None:
        """Close a single destination, ignoring errors."""
        try:
            await dest.close()
        except Exception:
            pass


class LogDestinationFactory:
    """Factory for creating log destinations based on configuration."""
    
    # Registry of available destination types
    _destinations: Dict[str, Type[LogDestination]] = {
        'sqlite': SQLiteDestination,
    }
    
    @classmethod
    def register_destination(cls, type_name: str, destination_class: Type[LogDestination]) -> None:
        """Register a new destination type."""
        cls._destinations[type_name] = destination_class
    
    @classmethod
    def create_destination(
        cls,
        config: DestinationConfig,
        server_config: Any
    ) -> Optional[LogDestination]:
        """Create a single destination from configuration."""
        if not config.enabled:
            return None
            
        destination_class = cls._destinations.get(config.type)
        if not destination_class:
            # Unknown destination type - skip it
            return None
        
        try:
            # Create destination with server config and any additional settings
            return destination_class(server_config, **config.settings)
        except Exception:
            # Failed to create destination - skip it
            return None
    
    @classmethod
    def create_from_config(
        cls,
        destinations_config: List[DestinationConfig],
        server_config: Any
    ) -> LogDestination:
        """Create log destination(s) from configuration."""
        # Create all enabled destinations
        destinations = []
        for dest_config in destinations_config:
            dest = cls.create_destination(dest_config, server_config)
            if dest:
                destinations.append(dest)
        
        # Return appropriate destination
        if len(destinations) == 0:
            # No destinations configured - fall back to SQLite
            return SQLiteDestination(server_config)
        elif len(destinations) == 1:
            # Single destination
            return destinations[0]
        else:
            # Multiple destinations
            return MultiDestination(destinations)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of registered destination types."""
        return list(cls._destinations.keys())


# Future destinations can be added here when needed
# Example of how to add Elasticsearch later:
"""
try:
    from .elasticsearch import ElasticsearchDestination
    LogDestinationFactory.register_destination('elasticsearch', ElasticsearchDestination)
except ImportError:
    # Elasticsearch not available - that's OK
    pass
"""