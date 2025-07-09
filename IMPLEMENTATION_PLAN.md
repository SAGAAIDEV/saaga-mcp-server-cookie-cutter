# MCP Server Cookie Cutter with SAAGA Base Decorators - Implementation Plan

## Executive Summary

This document outlines the implementation plan for creating an enhanced MCP (Model Context Protocol) server cookie cutter template that incorporates decorator patterns from the SAAGA base MCP server. The template will provide developers with a quick-start solution that automatically includes logging, exception handling, and parallelization capabilities while maintaining clean separation between business logic and administrative functions through an optional Streamlit UI.

## Project Overview

### Goals
1. Create a cookie cutter template that generates production-ready MCP servers
2. Integrate SAAGA decorator patterns (exception handling, logging, parallelization)
3. Add optional Streamlit-based administrative UI for configuration and log viewing
4. Maintain clean architecture with proper separation of concerns
5. Ensure zero-boilerplate developer experience

### Non-Goals (Deferred Features)
1. Backend authentication (OAuth flows, token management)
2. Scheduled tool functionality (Celery/Redis infrastructure)
3. Enterprise logging integrations (CloudWatch, Datadog, etc.)

## Architecture Overview

### Core Components

```
{{cookiecutter.project_slug}}/
├── {{cookiecutter.project_slug}}/          # Main package
│   ├── __init__.py
│   ├── config.py                           # Shared configuration module
│   ├── server/                             # MCP server implementation
│   │   ├── __init__.py
│   │   └── app.py                          # FastMCP server with auto-decorators
│   ├── tools/                              # Business logic tools
│   │   ├── __init__.py
│   │   └── example.py                      # Example tool
│   ├── decorators/                         # SAAGA-based decorators
│   │   ├── __init__.py
│   │   ├── exceptions.py                   # Exception handler decorator
│   │   ├── logging.py                      # Tool logger decorator
│   │   └── parallelize.py                  # Parallelization decorator
│   └── ui/                                 # Streamlit admin UI (optional)
│       ├── __init__.py
│       ├── app.py                          # Main Streamlit application
│       ├── pages/                          # Multi-page app structure
│       │   ├── 1_🏠_Home.py               # Server info and status
│       │   ├── 2_⚙️_Configuration.py       # Configuration editor
│       │   └── 3_📊_Logs.py                # SQLite log viewer
│       └── lib/                            # UI utilities
│           ├── components.py               # Reusable UI components
│           ├── state_manager.py            # Streamlit session state
│           ├── config_io.py                # Configuration file I/O
│           └── log_viewer.py               # SQLite log queries
├── pyproject.toml                          # Package configuration
├── README.md                               # Generated documentation
├── DEVELOPMENT.md                          # Developer guide
└── .gitignore                              # Git ignore patterns
```

### Data Flow

1. **MCP Client** (Claude Desktop, Cursor, etc.) launches the server via configured command
2. **Server** automatically applies decorators to all registered tools
3. **Decorators** handle cross-cutting concerns:
   - Exception handling → formats errors gracefully
   - Logging → writes to SQLite database
   - Parallelization → enables batch operations
4. **Tools** execute business logic without awareness of decorators
5. **Admin UI** (optional) reads logs and manages configuration separately

## Detailed Component Specifications

### 1. Cookie Cutter Template Configuration

```json
{
  "project_name": "My MCP Server",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "description": "MCP server with SAAGA decorators",
  "author_name": "Your Name",
  "author_email": "email@example.com",
  "python_version": ["3.11", "3.12"],
  "include_admin_ui": ["yes", "no"],
  "include_example_tools": ["yes", "no"],
  "include_parallel_example": ["yes", "no"],
  "server_port": "3001",
  "log_level": ["INFO", "DEBUG", "WARNING", "ERROR"],
  "log_retention_days": "30"
}
```

### 2. Decorator Implementations

#### 2.1 Exception Handler Decorator
```python
# decorators/exceptions.py
import functools
import traceback
from typing import Any, Callable, Dict

def exception_handler(func: Callable) -> Callable:
    """Decorator to catch and format exceptions from MCP tools."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log the full traceback
            error_details = {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc(),
                "tool": func.__name__
            }
            # Return formatted error response
            return {
                "error": f"{type(e).__name__}: {str(e)}",
                "tool": func.__name__
            }
    return wrapper
```

#### 2.2 Tool Logger Decorator
```python
# decorators/logging.py
import functools
import time
import sqlite3
from typing import Any, Callable
from pathlib import Path
import json
import threading

class ToolLogger:
    """Thread-safe SQLite logger for MCP tools."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._local = threading.local()
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create logging table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tool_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                tool_name TEXT NOT NULL,
                duration_ms REAL,
                status TEXT NOT NULL,
                input_args TEXT,
                output_summary TEXT,
                error_message TEXT,
                level TEXT NOT NULL DEFAULT 'INFO'
            )
        """)
        conn.commit()
        conn.close()
    
    def log_execution(self, tool_name: str, duration_ms: float, 
                     status: str, input_args: dict, output: Any, 
                     error: str = None):
        """Log tool execution details."""
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO tool_logs 
            (timestamp, tool_name, duration_ms, status, input_args, 
             output_summary, error_message, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            tool_name,
            duration_ms,
            status,
            json.dumps(input_args),
            str(output)[:500] if output else None,
            error,
            'ERROR' if error else 'INFO'
        ))
        conn.commit()
    
    def _get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
        return self._local.conn

# Global logger instance
_logger = None

def tool_logger(func: Callable) -> Callable:
    """Decorator to log MCP tool executions."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        global _logger
        if _logger is None:
            # Initialize logger with configured path
            from ..config import get_log_db_path
            _logger = ToolLogger(get_log_db_path())
        
        start_time = time.time()
        error_msg = None
        result = None
        
        try:
            result = await func(*args, **kwargs)
            status = 'success'
        except Exception as e:
            status = 'error'
            error_msg = str(e)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            _logger.log_execution(
                tool_name=func.__name__,
                duration_ms=duration_ms,
                status=status,
                input_args=kwargs,
                output=result,
                error=error_msg
            )
        
        return result
    
    return wrapper
```

#### 2.3 Parallelize Decorator
```python
# decorators/parallelize.py
import asyncio
import functools
from typing import Any, Callable, List, Dict

def parallelize(func: Callable) -> Callable:
    """
    Decorator that transforms a function to accept a list of kwargs 
    and execute them in parallel.
    """
    @functools.wraps(func)
    async def wrapper(items: List[Dict[str, Any]]) -> List[Any]:
        """
        Execute function in parallel for multiple inputs.
        
        Args:
            items: List of dictionaries containing kwargs for each execution
            
        Returns:
            List of results in the same order as inputs
        """
        tasks = [func(**item) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results to handle exceptions gracefully
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "error": str(result),
                    "input_index": i,
                    "input": items[i]
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    # Update function signature and documentation
    wrapper.__name__ = f"batch_{func.__name__}"
    wrapper.__doc__ = f"""Batch version of {func.__name__}.
    
Executes multiple instances in parallel.

Args:
    items: List of dictionaries containing arguments for each execution
    
Returns:
    List of results corresponding to each input

Original function:
{func.__doc__ or 'No documentation available'}
"""
    
    return wrapper
```

### 3. Server Implementation with Auto-Decorators

```python
# server/app.py
import os
from typing import List, Callable, Optional
from mcp.server.fastmcp import FastMCP
import click

from ..decorators import exception_handler, tool_logger, parallelize
from ..config import load_config

def create_decorated_server(
    name: str,
    tools: List[Callable] = None,
    parallel_tools: List[Callable] = None
) -> FastMCP:
    """
    Create MCP server with automatic decorator application.
    
    Args:
        name: Server name
        tools: List of regular tool functions
        parallel_tools: List of tools to be parallelized
        
    Returns:
        Configured FastMCP server instance
    """
    server = FastMCP(name)
    
    # Apply decorators to regular tools
    for func in (tools or []):
        # Apply decorators in order: exception_handler → tool_logger
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        
        # Register with MCP server
        server.tool()(decorated)
    
    # Apply decorators to parallel tools
    for func in (parallel_tools or []):
        # Apply decorators: exception_handler → tool_logger → parallelize
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        decorated = parallelize(decorated)
        
        # Register with MCP server
        server.tool()(decorated)
    
    return server

# Import tools based on configuration
{% if cookiecutter.include_example_tools == 'yes' %}
from ..tools.example import hello_world, calculate_sum
{% if cookiecutter.include_parallel_example == 'yes' %}
from ..tools.example import process_item
{% endif %}
{% endif %}

# Create server with tools
mcp = create_decorated_server(
    name="{{ cookiecutter.project_name }}",
    tools=[
        {% if cookiecutter.include_example_tools == 'yes' %}
        hello_world,
        calculate_sum,
        {% endif %}
        # Add your tools here
    ],
    parallel_tools=[
        {% if cookiecutter.include_parallel_example == 'yes' %}
        process_item,
        {% endif %}
        # Add tools to parallelize here
    ]
)

@click.command()
@click.option('--transport', '-t', 
              type=click.Choice(['stdio', 'sse']), 
              default='stdio',
              help='Transport type for MCP communication')
@click.option('--port', '-p', 
              type=int, 
              default={{ cookiecutter.server_port }},
              help='Port for SSE transport')
def main(transport: str, port: int):
    """Run the MCP server."""
    config = load_config()
    
    if transport == 'stdio':
        import asyncio
        asyncio.run(mcp.run(transport='stdio'))
    else:
        # SSE transport
        import uvicorn
        from mcp.server.sse import SseServerTransport
        
        sse = SseServerTransport(f"/{config.name}")
        mcp.link(sse)
        uvicorn.run(sse.get_asgi_app(), port=port, log_level=config.log_level.lower())

if __name__ == '__main__':
    main()
```

### 4. Configuration Management

```python
# config.py
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import yaml
import platformdirs

@dataclass
class ServerConfig:
    """Configuration for the MCP server."""
    name: str = "{{ cookiecutter.project_name }}"
    log_level: str = "{{ cookiecutter.log_level }}"
    log_retention_days: int = {{ cookiecutter.log_retention_days }}
    
    # Add your custom configuration fields here
    # example_api_key: Optional[str] = None
    # example_endpoint: str = "https://api.example.com"
    
    # Internal fields
    loaded_config_path: Optional[str] = None

def get_config_dir() -> Path:
    """Get platform-specific configuration directory."""
    return Path(platformdirs.user_config_dir(
        "{{ cookiecutter.project_slug }}", 
        "{{ cookiecutter.author_name.replace(' ', '') }}"
    ))

def get_log_db_path() -> Path:
    """Get platform-specific log database path."""
    data_dir = Path(platformdirs.user_data_dir(
        "{{ cookiecutter.project_slug }}", 
        "{{ cookiecutter.author_name.replace(' ', '') }}"
    ))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "logs.db"

def load_config(path_override: Optional[str] = None) -> ServerConfig:
    """Load configuration from file or create default."""
    if path_override:
        config_path = Path(path_override)
    else:
        config_dir = get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        config = ServerConfig(**data)
        config.loaded_config_path = str(config_path)
    else:
        # Create default configuration
        config = ServerConfig()
        config.loaded_config_path = str(config_path)
        save_config(config, config_path)
    
    return config

def save_config(config: ServerConfig, path: Optional[Path] = None):
    """Save configuration to file."""
    if path is None:
        path = Path(config.loaded_config_path) if config.loaded_config_path else get_config_dir() / "config.yaml"
    
    # Convert to dict and remove internal fields
    data = {k: v for k, v in config.__dict__.items() if not k.startswith('_') and k != 'loaded_config_path'}
    
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
```

{% if cookiecutter.include_admin_ui == 'yes' %}
### 5. Streamlit Admin UI

#### 5.1 Main Application
```python
# ui/app.py
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from {{ cookiecutter.project_slug }}.config import load_config, save_config
from .lib.state_manager import initialize_session_state, reset_state

st.set_page_config(
    page_title="{{ cookiecutter.project_name }} Admin",
    page_icon="⚙️",
    layout="wide"
)

st.title("{{ cookiecutter.project_name }} Administration")

# Initialize session state
initialize_session_state()

# Display any feedback messages
if 'feedback' in st.session_state:
    feedback = st.session_state.feedback
    if feedback['type'] == 'success':
        st.success(feedback['message'])
    elif feedback['type'] == 'warning':
        st.warning(feedback['message'])
    elif feedback['type'] == 'error':
        st.error(feedback['message'])
    del st.session_state.feedback

# Navigation info
st.markdown("""
This administration interface allows you to:
- 🏠 **Home**: View server information and status
- ⚙️ **Configuration**: Edit server configuration
- 📊 **Logs**: View and analyze server logs

Select a page from the sidebar to continue.
""")

# Sidebar info
with st.sidebar:
    st.markdown("### Quick Actions")
    
    if st.button("🔄 Reload Configuration"):
        reset_state()
        st.session_state.feedback = {
            'type': 'success',
            'message': 'Configuration reloaded successfully'
        }
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Notes")
    st.info("""
    Changes to configuration require restarting the MCP server to take effect.
    """)
```

#### 5.2 Configuration Page
```python
# ui/pages/2_⚙️_Configuration.py
import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from {{ cookiecutter.project_slug }}.config import ServerConfig, save_config, get_config_dir
from ..lib.components import render_config_form
from ..lib.config_io import validate_and_save_config

st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")

st.title("⚙️ Server Configuration")

# Get current config from session state
config = st.session_state.config

# Render configuration form
with st.form("config_form"):
    st.subheader("General Settings")
    
    updated_config = render_config_form(config)
    
    # Custom configuration section
    st.subheader("Custom Settings")
    st.info("Add your server-specific configuration fields here")
    
    # Example custom fields (replace with your own)
    # updated_config.example_api_key = st.text_input(
    #     "API Key",
    #     value=config.example_api_key or "",
    #     type="password"
    # )
    
    submitted = st.form_submit_button("💾 Save Configuration")
    
    if submitted:
        if validate_and_save_config(updated_config):
            st.session_state.config = updated_config
            st.success("✅ Configuration saved successfully!")
            st.info("Restart the MCP server for changes to take effect.")
        else:
            st.error("❌ Failed to save configuration")

# Display current configuration path
st.markdown("---")
st.caption(f"Configuration file: `{config.loaded_config_path or get_config_dir() / 'config.yaml'}`")
```

#### 5.3 Log Viewer Page
```python
# ui/pages/3_📊_Logs.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from ..lib.log_viewer import LogViewer
from {{ cookiecutter.project_slug }}.config import get_log_db_path

st.set_page_config(page_title="Logs", page_icon="📊", layout="wide")

st.title("📊 Server Logs")

# Initialize log viewer
log_viewer = LogViewer(get_log_db_path())

# Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Date range filter
    date_range = st.selectbox(
        "Date Range",
        ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom"]
    )
    
    if date_range == "Custom":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
    else:
        end_date = datetime.now()
        if date_range == "Last Hour":
            start_date = end_date - timedelta(hours=1)
        elif date_range == "Last 24 Hours":
            start_date = end_date - timedelta(days=1)
        elif date_range == "Last 7 Days":
            start_date = end_date - timedelta(days=7)
        else:  # Last 30 Days
            start_date = end_date - timedelta(days=30)

with col2:
    # Log level filter
    log_levels = st.multiselect(
        "Log Levels",
        ["INFO", "WARNING", "ERROR"],
        default=["INFO", "WARNING", "ERROR"]
    )

with col3:
    # Tool filter
    available_tools = log_viewer.get_unique_tools()
    selected_tools = st.multiselect(
        "Tools",
        available_tools,
        default=[]
    )

with col4:
    # Search
    search_term = st.text_input("Search", placeholder="Search in logs...")

# Refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Get and display logs
logs_df = log_viewer.get_logs(
    start_time=start_date,
    end_time=end_date,
    levels=log_levels,
    tools=selected_tools if selected_tools else None,
    search=search_term if search_term else None
)

if not logs_df.empty:
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Logs", len(logs_df))
    
    with col2:
        error_count = len(logs_df[logs_df['status'] == 'error'])
        st.metric("Errors", error_count)
    
    with col3:
        avg_duration = logs_df['duration_ms'].mean()
        st.metric("Avg Duration", f"{avg_duration:.2f} ms")
    
    with col4:
        unique_tools = logs_df['tool_name'].nunique()
        st.metric("Unique Tools", unique_tools)
    
    # Display logs
    st.subheader("Log Entries")
    
    # Format dataframe for display
    display_df = logs_df.copy()
    display_df['timestamp'] = pd.to_datetime(display_df['timestamp'], unit='s')
    display_df = display_df.sort_values('timestamp', ascending=False)
    
    # Use expander for each log entry
    for _, log in display_df.iterrows():
        status_emoji = "✅" if log['status'] == 'success' else "❌"
        with st.expander(f"{status_emoji} {log['tool_name']} - {log['timestamp']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Duration:** {log['duration_ms']:.2f} ms")
                st.write(f"**Status:** {log['status']}")
                
            with col2:
                st.write(f"**Level:** {log['level']}")
                if log['error_message']:
                    st.error(f"**Error:** {log['error_message']}")
            
            if log['input_args']:
                st.write("**Input Arguments:**")
                st.json(log['input_args'])
            
            if log['output_summary']:
                st.write("**Output Summary:**")
                st.text(log['output_summary'])
    
    # Export functionality
    st.subheader("Export Logs")
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("No logs found matching the selected filters.")

# Database info
st.markdown("---")
st.caption(f"Log database: `{get_log_db_path()}`")
```

#### 5.4 Supporting Libraries

```python
# ui/lib/log_viewer.py
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List
from datetime import datetime

class LogViewer:
    """Utility class for querying MCP server logs."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def get_logs(
        self, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        levels: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        search: Optional[str] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Get logs with optional filters."""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM tool_logs WHERE 1=1"
        params = []
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.timestamp())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.timestamp())
        
        if levels:
            placeholders = ','.join(['?' for _ in levels])
            query += f" AND level IN ({placeholders})"
            params.extend(levels)
        
        if tools:
            placeholders = ','.join(['?' for _ in tools])
            query += f" AND tool_name IN ({placeholders})"
            params.extend(tools)
        
        if search:
            query += " AND (tool_name LIKE ? OR input_args LIKE ? OR output_summary LIKE ? OR error_message LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern] * 4)
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_unique_tools(self) -> List[str]:
        """Get list of unique tool names from logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT tool_name FROM tool_logs ORDER BY tool_name")
        tools = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tools
    
    def get_stats(self) -> dict:
        """Get summary statistics from logs."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total logs
        cursor.execute("SELECT COUNT(*) FROM tool_logs")
        stats['total_logs'] = cursor.fetchone()[0]
        
        # Logs by status
        cursor.execute("SELECT status, COUNT(*) FROM tool_logs GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())
        
        # Logs by level
        cursor.execute("SELECT level, COUNT(*) FROM tool_logs GROUP BY level")
        stats['by_level'] = dict(cursor.fetchall())
        
        # Average duration
        cursor.execute("SELECT AVG(duration_ms) FROM tool_logs WHERE duration_ms IS NOT NULL")
        stats['avg_duration_ms'] = cursor.fetchone()[0] or 0
        
        conn.close()
        return stats
```

```python
# ui/lib/components.py
import streamlit as st
from {{ cookiecutter.project_slug }}.config import ServerConfig

def render_config_form(config: ServerConfig) -> ServerConfig:
    """Render configuration form and return updated config."""
    
    config.name = st.text_input(
        "Server Name",
        value=config.name,
        help="Display name for the MCP server"
    )
    
    config.log_level = st.selectbox(
        "Log Level",
        ["DEBUG", "INFO", "WARNING", "ERROR"],
        index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.log_level),
        help="Minimum log level to record"
    )
    
    config.log_retention_days = st.number_input(
        "Log Retention Days",
        min_value=1,
        max_value=365,
        value=config.log_retention_days,
        help="Number of days to retain logs"
    )
    
    return config
```

```python
# ui/lib/state_manager.py
import streamlit as st
from {{ cookiecutter.project_slug }}.config import load_config

def initialize_session_state():
    """Initialize Streamlit session state with configuration."""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None

def reset_state():
    """Reset session state and reload configuration."""
    if 'config' in st.session_state:
        del st.session_state.config
    initialize_session_state()
```

```python
# ui/lib/config_io.py
from pathlib import Path
from {{ cookiecutter.project_slug }}.config import ServerConfig, save_config

def validate_and_save_config(config: ServerConfig) -> bool:
    """Validate and save configuration to file."""
    try:
        # Add validation logic here
        if not config.name:
            return False
        
        # Save configuration
        save_config(config)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
```
{% endif %}

### 6. Example Tools

{% if cookiecutter.include_example_tools == 'yes' %}
```python
# tools/example.py
from mcp.types import TextContent

async def hello_world(name: str = "World") -> TextContent:
    """
    A simple greeting tool.
    
    Args:
        name: Name to greet (default: "World")
        
    Returns:
        Greeting message
    """
    return TextContent(text=f"Hello, {name}!")

async def calculate_sum(a: float, b: float) -> TextContent:
    """
    Calculate the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    result = a + b
    return TextContent(text=f"The sum of {a} and {b} is {result}")

{% if cookiecutter.include_parallel_example == 'yes' %}
async def process_item(item_id: str, action: str) -> TextContent:
    """
    Process a single item with the specified action.
    
    Args:
        item_id: Identifier of the item to process
        action: Action to perform on the item
        
    Returns:
        Processing result
    """
    # Simulate some processing
    import asyncio
    await asyncio.sleep(0.1)  # Simulate work
    
    return TextContent(text=f"Processed item {item_id} with action: {action}")
{% endif %}
```
{% endif %}

## Cookiecutter Documentation References

The following Cookiecutter documentation resources are essential for implementing this template:

### Core Documentation
- **Tutorial Create from Scratch**: https://cookiecutter.readthedocs.io/en/stable/tutorials/tutorial2.html
  - Comprehensive guide for creating a new cookiecutter template from scratch
  - Essential for Phase 1 implementation

### Advanced Features
- **Hooks**: https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html
  - Pre and post-generation hooks for custom logic
  - Used for validating inputs and post-processing generated projects

- **Choice Variables**: https://cookiecutter.readthedocs.io/en/stable/advanced/choice_variables.html
  - Implementing select/dropdown options in cookiecutter.json
  - Used for log_level, python_version selections

- **Boolean Variables**: https://cookiecutter.readthedocs.io/en/stable/advanced/boolean_variables.html
  - Implementing yes/no choices for optional features
  - Used for include_admin_ui, include_example_tools flags

- **Dictionary Variables**: https://cookiecutter.readthedocs.io/en/stable/advanced/dict_variables.html
  - Complex configuration structures
  - Useful for advanced configuration options

- **Copy without Render**: https://cookiecutter.readthedocs.io/en/stable/advanced/copy_without_render.html
  - Preventing Jinja2 processing of certain files
  - Important for template files that contain Jinja2 syntax

### API Reference
- **API Reference**: https://cookiecutter.readthedocs.io/en/stable/cookiecutter.html
  - Complete API documentation for programmatic usage
  - Essential for testing framework implementation

## Implementation Phases

### Phase 1: Core Template Structure
1. Set up cookie cutter repository structure
2. Create base template with placeholders
3. Implement basic MCP server scaffolding
4. Add pyproject.toml with dependencies
5. Create README and DEVELOPMENT templates

### Phase 2: Decorator Integration
1. Extract decorator implementations from SAAGA base
2. Adapt decorators for standalone use
3. Implement auto-decorator application in server
4. Add SQLite logging schema
5. Test decorator chain functionality

### Phase 3: Configuration System
1. Implement platform-aware configuration paths
2. Create configuration dataclass structure
3. Add YAML load/save functionality
4. Create default configuration template
5. Test cross-platform compatibility

### Phase 4: Admin UI (if selected)
1. Create Streamlit app structure
2. Implement configuration editor page
3. Build SQLite log viewer
4. Add log filtering and search
5. Create export functionality
6. Test UI independently from server

### Phase 5: Documentation and Examples
1. Write comprehensive README template
2. Create DEVELOPMENT guide
3. Add example tools demonstrating patterns
4. Document decorator usage
5. Create troubleshooting guide

### Phase 6: Testing and Validation
1. Test cookie cutter generation
2. Validate generated project structure
3. Test MCP server functionality
4. Verify decorator behavior
5. Test admin UI (if included)
6. Cross-platform testing

## Technical Considerations

### 1. Dependency Management
- Use modern Python packaging (pyproject.toml)
- Pin major versions for stability
- Separate UI dependencies (optional)
- Consider using poetry or uv for development

### 2. Platform Compatibility
- Use platformdirs for OS-specific paths
- Test on Windows, macOS, Linux
- Handle path separators correctly
- Consider Docker support

### 3. Performance
- SQLite logging is lightweight
- Decorators add minimal overhead
- Parallelization improves throughput
- UI runs separately (no impact on server)

### 4. Security
- No sensitive data in logs by default
- Configuration files use safe YAML loading
- UI requires local filesystem access
- No network exposure for admin functions

### 5. Extensibility
- Easy to add new decorators
- Simple tool registration pattern
- UI pages can be added/removed
- Configuration is extensible

## Success Criteria

1. **Developer Experience**
   - Zero boilerplate for common patterns
   - Clear documentation and examples
   - Fast project generation
   - Intuitive project structure

2. **Production Readiness**
   - Robust error handling
   - Comprehensive logging
   - Performance monitoring capability
   - Clean separation of concerns

3. **Maintainability**
   - Modular architecture
   - Clear upgrade path
   - Minimal dependencies
   - Well-documented code

4. **Flexibility**
   - Optional components (UI, examples)
   - Extensible configuration
   - Custom decorator support
   - Multiple transport options

## Future Enhancements (Out of Scope)

1. **Enterprise Logging**
   - CloudWatch integration
   - Datadog support
   - OpenTelemetry compatibility
   - Log aggregation

2. **Authentication System**
   - OAuth provider support
   - Token management
   - Backend API authentication
   - Multi-tenant support

3. **Scheduled Tools**
   - Celery integration
   - Redis configuration
   - Cron-like scheduling
   - Task management UI

4. **Advanced Features**
   - Distributed tracing
   - Performance profiling
   - A/B testing support
   - Feature flags

## Risks and Mitigation

1. **Risk**: Decorator overhead impacts performance
   - **Mitigation**: Profile and optimize critical paths
   - **Mitigation**: Make decorators optional via configuration

2. **Risk**: SQLite scaling issues with high volume
   - **Mitigation**: Implement log rotation
   - **Mitigation**: Document enterprise alternatives

3. **Risk**: UI complexity grows beyond Streamlit capabilities
   - **Mitigation**: Keep UI focused on essential features
   - **Mitigation**: Design for future migration to React/Vue

4. **Risk**: Cross-platform compatibility issues
   - **Mitigation**: Extensive testing on all platforms
   - **Mitigation**: Use established libraries (platformdirs)

## Conclusion

This implementation plan provides a clear path to creating an enhanced MCP server cookie cutter that incorporates the best practices from SAAGA decorators while maintaining clean architecture and excellent developer experience. The optional Streamlit UI provides administrative capabilities without impacting server performance, and the modular design allows for future enhancements as needs evolve.