"""Shared fixtures for integration tests."""

import asyncio
import os
import sys
import sqlite3
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any
from unittest import mock

import pytest
import pytest_asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Add warning suppression for the entire test session
import warnings
warnings.filterwarnings("ignore", 
                       message="coroutine 'SQLiteDestination.write' was never awaited",
                       category=RuntimeWarning)
warnings.filterwarnings("ignore", 
                       message=".*found in sys.modules after import.*", 
                       category=RuntimeWarning)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def isolated_db_path(tmp_path: Path) -> Path:
    """Create an isolated database path for each test."""
    db_dir = tmp_path / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "unified_logs.db"


@pytest.fixture
def mock_platformdirs(isolated_db_path: Path, monkeypatch):
    """Mock platformdirs to use isolated test directory."""
    import platformdirs
    
    def mock_user_data_dir(appname: str, *args, **kwargs) -> str:
        return str(isolated_db_path.parent)
    
    monkeypatch.setattr(platformdirs, "user_data_dir", mock_user_data_dir)
    return isolated_db_path


@pytest_asyncio.fixture
async def mcp_server(mock_platformdirs: Path) -> AsyncGenerator[Dict[str, Any], None]:
    """Start MCP server subprocess for tests."""
    # Environment variables for the subprocess
    env = os.environ.copy()
    env['PYTHONWARNINGS'] = 'ignore::RuntimeWarning'
    # Force the server to use our test database path
    env['{{ cookiecutter.project_slug|upper }}_DATA_DIR'] = str(mock_platformdirs.parent)
    
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "{{ cookiecutter.project_slug }}.server.app", "--transport", "stdio"],
        env=env
    )
    
    # Store server info
    server_info = {
        "params": server_params,
        "db_path": mock_platformdirs
    }
    
    yield server_info
    
    # Cleanup is handled by stdio_client context manager


@pytest_asyncio.fixture
async def mcp_client(mcp_server: Dict[str, Any]) -> AsyncGenerator[ClientSession, None]:
    """Create MCP client session connected to test server."""
    server_params = mcp_server["params"]
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Verify tools are available
            tools = await session.list_tools()
            assert len(tools.tools) > 0, "No tools found in MCP server"
            
            yield session


@pytest.fixture
def db_connection(mcp_server: Dict[str, Any]) -> Generator[sqlite3.Connection, None, None]:
    """Create a database connection for verification."""
    db_path = mcp_server["db_path"]
    
    # Wait a bit for database to be created
    import time
    for _ in range(10):
        if db_path.exists():
            break
        time.sleep(0.1)
    
    if not db_path.exists():
        pytest.fail(f"Database not created at {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def query_correlation_logs(conn: sqlite3.Connection, correlation_id: str) -> list[dict]:
    """Query logs for a specific correlation ID."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, tool_name, duration_ms, status, 
               input_args, output_summary, error_message, correlation_id
        FROM unified_logs
        WHERE correlation_id = ?
        ORDER BY timestamp
    """, (correlation_id,))
    
    results = [dict(row) for row in cursor.fetchall()]
    cursor.close()
    return results


def get_latest_tool_log(conn: sqlite3.Connection, tool_name: str) -> dict:
    """Get the most recent log entry for a specific tool."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT correlation_id, timestamp, status, duration_ms
        FROM unified_logs 
        WHERE tool_name = ? AND status = 'success'
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (tool_name,))
    
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        return dict(row)
    return None