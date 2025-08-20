# Factory Pattern Implementation for Logging Destinations

## Overview

The logging system now uses a factory pattern that makes it trivial to add new destinations. Currently, only SQLite is implemented, but the architecture is designed for easy extension.

## Current Implementation

### 1. Factory Pattern Structure

```
logging/destinations/
├── __init__.py          # Exports and registration
├── base.py              # LogDestination interface
├── sqlite.py            # SQLite implementation (default)
├── factory.py           # Factory and MultiDestination
└── elasticsearch_example.py  # Example for future implementation
```

### 2. Core Components

#### LogDestinationFactory (`factory.py`)
- Registry of available destination types
- Creates destinations from configuration
- Falls back to SQLite if no destinations configured

#### MultiDestination (`factory.py`)
- Writes to multiple destinations concurrently
- Handles errors gracefully (fire-and-forget)
- Queries from first available destination

#### DestinationConfig (`factory.py`)
- Simple dataclass for destination configuration
- Type, enabled flag, and settings dict

### 3. Configuration

In `config.yaml`:
```yaml
logging_destinations:
  destinations:
    - type: "sqlite"
      enabled: true
      settings: {}
```

## Adding Elasticsearch (Future)

### Step 1: Implement the Destination

Create `logging/destinations/elasticsearch.py`:
```python
from .base import LogDestination, LogEntry

class ElasticsearchDestination(LogDestination):
    def __init__(self, server_config, **settings):
        # Initialize with settings like host, port, index
        pass
    
    async def write(self, entry: LogEntry) -> None:
        # Write to Elasticsearch
        pass
    
    async def query(self, **filters) -> List[LogEntry]:
        # Query from Elasticsearch
        pass
    
    async def close(self) -> None:
        # Cleanup
        pass
```

### Step 2: Register the Destination

In `logging/destinations/__init__.py`:
```python
try:
    from .elasticsearch import ElasticsearchDestination
    LogDestinationFactory.register_destination('elasticsearch', ElasticsearchDestination)
except ImportError:
    pass  # Optional destination not available
```

### Step 3: Update Dependencies

In `pyproject.toml`:
```toml
[project.optional-dependencies]
elasticsearch = ["elasticsearch[async]>=8.0.0"]
```

### Step 4: Configure It

In `config.yaml`:
```yaml
logging_destinations:
  destinations:
    - type: "sqlite"
      enabled: true
      settings: {}
    - type: "elasticsearch"
      enabled: true
      settings:
        host: "localhost"
        port: 9200
        index: "mcp-logs"
```

That's it! The factory automatically handles:
- Creating both destinations
- Writing to both concurrently
- Falling back if one fails
- Querying from available destinations

## Key Benefits

1. **Minimal Code**: Just implement the interface
2. **No Core Changes**: Factory handles everything
3. **Configuration Driven**: Enable/disable via YAML
4. **Multiple Destinations**: Automatic concurrent writes
5. **Graceful Degradation**: Failures don't break the system

## Testing

Generate a test project and verify:
```bash
cookiecutter . --no-input
cd my_mcp_server
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m my_mcp_server.server.app
```

The server will log: "Unified logging initialized with 1 available destination types"

When Elasticsearch is added, it will show: "Unified logging initialized with 2 available destination types"