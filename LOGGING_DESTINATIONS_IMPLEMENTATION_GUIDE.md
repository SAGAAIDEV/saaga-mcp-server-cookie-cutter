# Logging Destinations Implementation Guide

## Overview

This guide provides comprehensive implementation details for extending the SAAGA MCP Server Cookie Cutter's logging system to support multiple destination backends beyond SQLite. The architecture supports pluggable destinations with a fire-and-forget pattern optimized for MCP's quick-return requirements.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Fire-and-Forget Pattern](#fire-and-forget-pattern)
4. [Implementation Guide](#implementation-guide)
5. [Destination Implementations](#destination-implementations)
6. [Cookie Cutter Integration](#cookie-cutter-integration)
7. [Testing Strategy](#testing-strategy)
8. [Configuration Examples](#configuration-examples)

## Architecture Overview

```
┌─────────────────────┐     ┌──────────────────┐
│   Tool/App Code     │────▶│  Unified Logger  │
└─────────────────────┘     └────────┬─────────┘
                                     │
                            ┌────────▼─────────┐
                            │  LogDestination  │
                            │   Interface      │
                            └────────┬─────────┘
                                     │
                ┌────────────────────┼────────────────────┐
                │                    │                    │
        ┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
        │SQLiteDestination│  │    Kafka        │  │ Elasticsearch   │
        │  (Implemented)  │  │   Destination   │  │   Destination   │
        └────────────────┘  └────────────────┘  └────────────────┘
```

### Design Principles

1. **Fire-and-forget writes** - MCP tools cannot wait for logging operations
2. **Configurable quick retries** - Best effort delivery without blocking tool execution
3. **Dual destination support** - Local (SQLite) + Production (Kafka/ES/Convex)
4. **Cookie cutter configuration** - Select destinations at project generation time
5. **Runtime toggles** - Enable/disable destinations via environment variables
6. **No queuing complexity** - Keep it simple, accept potential log loss
7. **Graceful degradation** - Failed logs don't crash tools

## Core Components

### 1. LogEntry Dataclass (`logging/destinations/base.py`)

Unified structure for all log entries:

```python
@dataclass
class LogEntry:
    """Unified log entry structure for all destinations."""
    correlation_id: str
    timestamp: datetime
    level: str
    log_type: str  # 'tool_execution', 'internal', 'framework'
    message: str
    tool_name: Optional[str] = None
    duration_ms: Optional[float] = None
    status: Optional[str] = None
    input_args: Optional[Dict[str, Any]] = None
    output_summary: Optional[str] = None
    error_message: Optional[str] = None
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None
    thread_name: Optional[str] = None
    process_id: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
```

### 2. LogDestination Abstract Base Class

```python
class LogDestination(ABC):
    """Abstract base class for all log destinations."""
    
    @abstractmethod
    async def write(self, entry: LogEntry) -> None:
        """Write a log entry to the destination."""
        pass
    
    @abstractmethod
    async def query(self, **filters) -> List[LogEntry]:
        """Query logs with filters (for UI/debugging)."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        pass
```

Note: For write-only destinations, `query()` can raise `NotImplementedError`.

### 3. UnifiedLogger (`logging/unified_logger.py`)

- Intercepts Loguru messages
- Converts to LogEntry objects
- Calls `destination.write(entry)` asynchronously
- Handles correlation ID context

## Fire-and-Forget Pattern

### Async Fire-and-Forget Implementation

```python
async def write(self, entry: LogEntry) -> None:
    """Fire-and-forget write to destination."""
    # Create a task to handle retries without awaiting
    asyncio.create_task(self._write_with_retries(entry))
```

### Retry Wrapper Pattern

```python
class RetryWrapper(LogDestination):
    """Wraps a destination with retry logic."""
    
    def __init__(self, destination: LogDestination, max_attempts: int = 2, retry_delay_ms: int = 50):
        self.destination = destination
        self.max_attempts = max_attempts
        self.retry_delay_ms = retry_delay_ms
    
    async def _write_with_retries(self, entry: LogEntry):
        """Internal method to handle retries."""
        for attempt in range(self.max_attempts):
            try:
                await asyncio.wait_for(
                    self.destination.write(entry),
                    timeout=self.retry_delay_ms / 1000.0
                )
                return  # Success
            except asyncio.TimeoutError:
                if attempt < self.max_attempts - 1:
                    await asyncio.sleep(self.retry_delay_ms / 1000.0)
```

### Composite Destination Pattern

```python
class CompositeDestination(LogDestination):
    """Writes to multiple destinations simultaneously."""
    
    async def write(self, entry: LogEntry) -> None:
        """Fire-and-forget write to all destinations."""
        tasks = []
        for dest in self.destinations:
            task = asyncio.create_task(self._write_ignore_errors(dest, entry))
            tasks.append(task)
        # Don't await - let tasks complete in background
```

## Implementation Guide

### Step 1: Create Factory Function

```python
def create_log_destination(config: ServerConfig) -> LogDestination:
    """Create configured log destination(s) with retry logic."""
    destinations = []
    
    # Local destination (if enabled)
    if config.enable_local_logging:
        local_dest = SQLiteDestination(config)
        destinations.append(local_dest)
    
    # Production destination (if enabled)
    if config.enable_production_logging:
        prod_dest = create_production_destination(config)
        if prod_dest:
            wrapped_dest = RetryWrapper(
                prod_dest,
                max_attempts=config.log_retry_attempts,
                retry_delay_ms=config.log_retry_delay_ms
            )
            destinations.append(wrapped_dest)
    
    if len(destinations) == 0:
        raise ValueError("No log destinations enabled")
    elif len(destinations) == 1:
        return destinations[0]
    else:
        return CompositeDestination(destinations)
```

### Step 2: Update Server Initialization

```python
# In server/app.py
from {{cookiecutter.project_slug}}.logging.factory import create_log_destination

def create_mcp_server(config: Optional[ServerConfig] = None) -> FastMCP:
    # Initialize logging with configured destination(s)
    destination = create_log_destination(config)
    UnifiedLogger.initialize(destination)
```

### Step 3: Configuration Schema

```python
@dataclass
class ServerConfig:
    """Server configuration with multi-destination logging support."""
    # Logging destinations
    enable_local_logging: bool = True
    enable_production_logging: bool = False
    log_retry_attempts: int = 2
    log_retry_delay_ms: int = 50
    
    # Production destination config
    log_destination_type: str = "sqlite"  # kafka, elasticsearch, convex
    
    # Destination-specific settings
    kafka_bootstrap_servers: Optional[str] = None
    kafka_topic: Optional[str] = None
    elasticsearch_hosts: Optional[List[str]] = None
    elasticsearch_index_prefix: Optional[str] = None
    convex_endpoint_url: Optional[str] = None
    convex_api_key: Optional[str] = None
```

## Destination Implementations

### 1. Kafka Destination

**Time Estimate**: 2-3 hours  
**Dependencies**: `pip install aiokafka`  
**Reference**: https://aiokafka.readthedocs.io/en/stable/

```python
class KafkaDestination(LogDestination):
    """Kafka destination with connection pooling for fast writes."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.topic = config.kafka_topic or "mcp-logs"
        self.producer = None
        self._connected = asyncio.Event()
        
        # Start connection in background
        asyncio.create_task(self._connect())
    
    async def _connect(self):
        """Connect to Kafka in background."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode(),
                linger_ms=0,  # Don't wait to batch
                acks=0,  # Don't wait for acknowledgment
                compression_type=None  # No compression for speed
            )
            await self.producer.start()
            self._connected.set()
        except Exception:
            pass  # Connection failed - skip logs
    
    async def write(self, entry: LogEntry) -> None:
        """Fire-and-forget write to Kafka."""
        if not self._connected.is_set():
            return  # Skip if not connected
        
        log_dict = {
            'correlation_id': entry.correlation_id,
            'timestamp': entry.timestamp.isoformat(),
            'level': entry.level,
            'log_type': entry.log_type,
            'message': entry.message,
            'tool_name': entry.tool_name,
            'duration_ms': entry.duration_ms,
            'status': entry.status,
            'input_args': entry.input_args,
            'output_summary': entry.output_summary,
            'error_message': entry.error_message,
            'module': entry.module,
            'function': entry.function,
            'line': entry.line,
            'thread_name': entry.thread_name,
            'process_id': entry.process_id,
            'extra_data': entry.extra_data
        }
        
        # Send without waiting
        await self.producer.send(self.topic, value=log_dict)
```

### 2. Elasticsearch Destination

**Time Estimate**: 3 hours  
**Dependencies**: `pip install elasticsearch[async]`  
**Reference**: https://elasticsearch-py.readthedocs.io/en/stable/async.html

```python
class ElasticsearchDestination(LogDestination):
    """Elasticsearch destination with automatic index management."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.hosts = config.elasticsearch_hosts or ["localhost:9200"]
        self.index_prefix = config.elasticsearch_index_prefix or "mcp-logs"
        
        # Initialize client
        self.es = AsyncElasticsearch(
            hosts=self.hosts,
            verify_certs=False,
            ssl_show_warn=False
        )
        self._template_created = False
    
    async def _ensure_index_template(self):
        """Ensure index template exists for consistent mapping."""
        if self._template_created:
            return
            
        template_name = f"{self.index_prefix}-template"
        
        # Create index template
        await self.es.indices.put_index_template(
            name=template_name,
            body={
                "index_patterns": [f"{self.index_prefix}-*"],
                "template": {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "correlation_id": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "level": {"type": "keyword"},
                            "log_type": {"type": "keyword"},
                            "message": {"type": "text"},
                            "tool_name": {"type": "keyword"},
                            "duration_ms": {"type": "float"},
                            "status": {"type": "keyword"},
                            "input_args": {"type": "object", "enabled": False},
                            "output_summary": {"type": "text"},
                            "error_message": {"type": "text"},
                            "module": {"type": "keyword"},
                            "function": {"type": "keyword"},
                            "line": {"type": "integer"},
                            "thread_name": {"type": "keyword"},
                            "process_id": {"type": "integer"},
                            "extra_data": {"type": "object", "enabled": False}
                        }
                    }
                }
            }
        )
        self._template_created = True
    
    async def write(self, entry: LogEntry) -> None:
        """Write log entry to Elasticsearch."""
        await self._ensure_index_template()
        
        # Use daily indices
        index_name = f"{self.index_prefix}-{datetime.utcnow():%Y.%m.%d}"
        
        # Convert LogEntry to dict
        doc = {
            'correlation_id': entry.correlation_id,
            'timestamp': entry.timestamp,
            'level': entry.level,
            'log_type': entry.log_type,
            'message': entry.message,
            'tool_name': entry.tool_name,
            'duration_ms': entry.duration_ms,
            'status': entry.status,
            'input_args': entry.input_args,
            'output_summary': entry.output_summary,
            'error_message': entry.error_message,
            'module': entry.module,
            'function': entry.function,
            'line': entry.line,
            'thread_name': entry.thread_name,
            'process_id': entry.process_id,
            'extra_data': entry.extra_data
        }
        
        # Remove None values
        doc = {k: v for k, v in doc.items() if v is not None}
        
        try:
            await self.es.index(index=index_name, document=doc)
        except Exception:
            pass  # Ignore errors for fire-and-forget
```

### 3. PostgreSQL Destination

**Time Estimate**: 2 hours  
**Dependencies**: `pip install asyncpg`  
**Reference**: https://magicstack.github.io/asyncpg/current/

```python
class PostgresDestination(LogDestination):
    """PostgreSQL destination with connection pooling."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.dsn = config.postgres_dsn or "postgresql://localhost/mcp_logs"
        self.table_name = config.postgres_table or "unified_logs"
        self.pool = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure connection pool and table are initialized."""
        if not self._initialized:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            
            # Create table if not exists
            async with self.pool.acquire() as conn:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id BIGSERIAL PRIMARY KEY,
                        correlation_id TEXT NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL,
                        level TEXT NOT NULL,
                        log_type TEXT,
                        message TEXT NOT NULL,
                        tool_name TEXT,
                        duration_ms REAL,
                        status TEXT,
                        input_args JSONB,
                        output_summary TEXT,
                        error_message TEXT,
                        module TEXT,
                        function TEXT,
                        line INTEGER,
                        thread_name TEXT,
                        process_id INTEGER,
                        extra_data JSONB,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_correlation_id 
                        ON {self.table_name}(correlation_id);
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_timestamp 
                        ON {self.table_name}(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_tool_name 
                        ON {self.table_name}(tool_name) WHERE tool_name IS NOT NULL;
                ''')
            
            self._initialized = True
    
    async def write(self, entry: LogEntry) -> None:
        """Write log entry to PostgreSQL."""
        await self._ensure_initialized()
        
        async with self.pool.acquire() as conn:
            await conn.execute(f'''
                INSERT INTO {self.table_name} (
                    correlation_id, timestamp, level, log_type, message,
                    tool_name, duration_ms, status, input_args, output_summary,
                    error_message, module, function, line, thread_name,
                    process_id, extra_data
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                         $11, $12, $13, $14, $15, $16, $17)
            ''', 
                entry.correlation_id,
                entry.timestamp,
                entry.level,
                entry.log_type,
                entry.message,
                entry.tool_name,
                entry.duration_ms,
                entry.status,
                json.dumps(entry.input_args) if entry.input_args else None,
                entry.output_summary,
                entry.error_message,
                entry.module,
                entry.function,
                entry.line,
                entry.thread_name,
                entry.process_id,
                json.dumps(entry.extra_data) if entry.extra_data else None
            )
```

### 4. Convex Destination (HTTP-based)

**Time Estimate**: 2-3 hours  
**Dependencies**: `pip install httpx`  
**Reference**: https://www.python-httpx.org/async/

```python
class ConvexDestination(LogDestination):
    """Convex destination using HTTP actions for log ingestion."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.endpoint_url = config.convex_endpoint_url
        if not self.endpoint_url:
            raise ValueError("convex_endpoint_url is required")
        
        self.api_key = config.convex_api_key
        self.timeout = config.convex_timeout_seconds or 30
        
        # Use httpx for async HTTP
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers=self._build_headers()
        )
    
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers including optional auth."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"MCP-Server/{self.config.name}"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def write(self, entry: LogEntry) -> None:
        """Write log entry to Convex via HTTP action."""
        # Convert to Convex's expected format (camelCase)
        log_dict = {
            'correlationId': entry.correlation_id,
            'timestamp': entry.timestamp.isoformat() if hasattr(entry.timestamp, 'isoformat') else str(entry.timestamp),
            'level': entry.level,
            'logType': entry.log_type,
            'message': entry.message,
            'toolName': entry.tool_name,
            'durationMs': entry.duration_ms,
            'status': entry.status,
            'inputArgs': entry.input_args,
            'outputSummary': entry.output_summary,
            'errorMessage': entry.error_message,
            'module': entry.module,
            'function': entry.function,
            'line': entry.line,
            'threadName': entry.thread_name,
            'processId': entry.process_id,
            'extraData': entry.extra_data,
            'serverName': self.config.name,
            'serverVersion': getattr(self.config, 'version', 'unknown')
        }
        
        try:
            response = await self.client.post(
                self.endpoint_url,
                json={'log': log_dict}
            )
            response.raise_for_status()
        except Exception:
            pass  # Ignore errors for fire-and-forget
```

**Note**: Convex requires backend setup (HTTP action + mutation) to receive logs.

## Cookie Cutter Integration

### Updated cookiecutter.json

```json
{
  "project_name": "My MCP Server",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "description": "A Model Context Protocol server",
  "author_name": "Your Name",
  "author_email": "you@example.com",
  "python_version": ["3.11", "3.12"],
  "include_admin_ui": ["no", "yes"],
  "include_example_tools": ["yes", "no"],
  "include_parallel_example": ["yes", "no"],
  "log_level": ["INFO", "DEBUG", "WARNING", "ERROR"],
  "log_retention_days": "30",
  "local_log_destination": ["sqlite", "none"],
  "production_log_destination": ["none", "kafka", "elasticsearch", "postgres", "convex"],
  "log_retry_attempts": "2",
  "log_retry_delay_ms": "50",
  "kafka_bootstrap_servers": "localhost:9092",
  "kafka_topic": "mcp-logs",
  "elasticsearch_hosts": "localhost:9200",
  "elasticsearch_index_prefix": "mcp-logs",
  "postgres_dsn": "postgresql://localhost/mcp_logs",
  "convex_endpoint_url": "https://your-app.convex.site/logs/ingest",
  "convex_api_key": ""
}
```

### Conditional Dependencies in pyproject.toml

```toml
[project.optional-dependencies]
kafka = ["aiokafka>=0.8.0"]
postgres = ["asyncpg>=0.27.0"]
elasticsearch = ["elasticsearch[async]>=8.0.0"]
convex = ["httpx>=0.24.0"]
all-destinations = [
    "aiokafka>=0.8.0",
    "asyncpg>=0.27.0", 
    "elasticsearch[async]>=8.0.0",
    "httpx>=0.24.0"
]
```

### Environment Variable Support

```bash
# Enable/disable destinations
ENABLE_LOCAL_LOGGING=true
ENABLE_PRODUCTION_LOGGING=false

# Retry configuration
LOG_RETRY_ATTEMPTS=2
LOG_RETRY_DELAY_MS=50

# Destination selection
LOG_DESTINATION_TYPE=kafka  # or elasticsearch, postgres, convex

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS=broker1:9092,broker2:9092
KAFKA_TOPIC=mcp-logs-prod

# Elasticsearch configuration
ELASTICSEARCH_HOSTS=https://es.example.com:443
ELASTICSEARCH_INDEX_PREFIX=mcp-logs-prod

# PostgreSQL configuration
POSTGRES_DSN=postgresql://user:pass@localhost:5432/logs

# Convex configuration
CONVEX_ENDPOINT_URL=https://my-app.convex.site/logs/ingest
CONVEX_API_KEY=secret_key_here
```

## Testing Strategy

### Unit Tests

```python
# Test fire-and-forget behavior
async def test_write_does_not_block():
    dest = create_log_destination(config)
    start = time.time()
    await dest.write(log_entry)
    elapsed = time.time() - start
    assert elapsed < 0.1  # Should return quickly

# Test retry behavior
async def test_retry_on_failure():
    mock_dest = Mock(spec=LogDestination)
    mock_dest.write.side_effect = [asyncio.TimeoutError(), None]
    
    wrapped = RetryWrapper(mock_dest, max_attempts=2)
    await wrapped.write(log_entry)
    
    assert mock_dest.write.call_count == 2

# Test composite writes
async def test_composite_writes_to_all():
    dest1, dest2 = Mock(), Mock()
    composite = CompositeDestination([dest1, dest2])
    
    await composite.write(log_entry)
    await asyncio.sleep(0.1)  # Let background tasks complete
    
    dest1.write.assert_called_once()
    dest2.write.assert_called_once()
```

### Integration Tests

```python
# Test with each destination type
@pytest.mark.parametrize("dest_type", ["kafka", "elasticsearch", "postgres"])
async def test_destination_integration(dest_type, config):
    config.log_destination_type = dest_type
    dest = create_log_destination(config)
    
    # Should not raise
    await dest.write(sample_log_entry)
    
    # Cleanup
    await dest.close()
```

### Manual Testing

1. **SQLite Only (Development)**:
   ```bash
   ENABLE_LOCAL_LOGGING=true ENABLE_PRODUCTION_LOGGING=false python -m server.app
   ```

2. **Kafka + SQLite (Production)**:
   ```bash
   ENABLE_LOCAL_LOGGING=true \
   ENABLE_PRODUCTION_LOGGING=true \
   LOG_DESTINATION_TYPE=kafka \
   KAFKA_BOOTSTRAP_SERVERS=localhost:9092 \
   python -m server.app
   ```

3. **Verify Kafka Messages**:
   ```bash
   kafka-console-consumer --topic mcp-logs --from-beginning --bootstrap-server localhost:9092
   ```

4. **Verify Elasticsearch**:
   ```bash
   curl -X GET "localhost:9200/mcp-logs-*/_search?size=10&sort=timestamp:desc"
   ```

## Configuration Examples

### Development Setup
```yaml
# Local SQLite only
enable_local_logging: true
enable_production_logging: false
log_level: DEBUG
```

### Production Setup (Kafka)
```yaml
enable_local_logging: true  # Keep for debugging
enable_production_logging: true
log_destination_type: kafka
kafka_bootstrap_servers: "broker1:9092,broker2:9092,broker3:9092"
kafka_topic: "mcp-logs-prod"
log_retry_attempts: 3
log_retry_delay_ms: 100
```

### Cloud Setup (Elasticsearch)
```yaml
enable_local_logging: false
enable_production_logging: true
log_destination_type: elasticsearch
elasticsearch_hosts: 
  - "https://es1.cloud.elastic.co:443"
  - "https://es2.cloud.elastic.co:443"
elasticsearch_index_prefix: "mcp-logs"
log_level: INFO
```

### Edge Setup (Convex)
```yaml
enable_local_logging: true
enable_production_logging: true
log_destination_type: convex
convex_endpoint_url: "https://my-app.convex.site/logs/ingest"
convex_api_key: "${CONVEX_API_KEY}"
log_retry_attempts: 2
log_retry_delay_ms: 50
```

## Troubleshooting

### Common Issues

1. **Logs not appearing in destination**:
   - Check environment variables are set correctly
   - Verify destination service is running (Kafka, ES, etc.)
   - Check for connection errors in stderr
   - Ensure proper authentication credentials

2. **Tool execution slow**:
   - Reduce retry attempts or timeout
   - Check network latency to destination
   - Consider disabling production logging temporarily

3. **Memory usage increasing**:
   - Background tasks may be accumulating
   - Check for connection leaks
   - Monitor asyncio task count

### Debug Mode

Enable debug logging to see destination errors:
```python
import logging
logging.getLogger("asyncio").setLevel(logging.DEBUG)
```

## Summary

This architecture provides:
- ✅ Fire-and-forget logging that won't block MCP tools
- ✅ Support for multiple destinations (local + production)
- ✅ Configurable retry logic for best-effort delivery
- ✅ Cookie cutter integration for easy setup
- ✅ Runtime toggles via environment variables
- ✅ Simple architecture without complex queuing
- ✅ Extensible pattern for adding new destinations

The implementation maintains the existing LogDestination abstraction while adding multi-destination support optimized for MCP's quick-return requirements. New destinations can be added by implementing the LogDestination interface and updating the factory function.