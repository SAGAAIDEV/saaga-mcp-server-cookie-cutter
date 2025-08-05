"""Shared fixtures for integration tests."""

import asyncio
import os
import sys
import sqlite3
import shutil
import uuid
from pathlib import Path
from typing import AsyncGenerator, Generator, Dict, Any

import pytest
import pytest_asyncio
import platformdirs
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
def backup_and_cleanup_db():
    """Backup existing database before tests and restore after."""
    # Get the real database path
    real_db_path = Path(platformdirs.user_data_dir("{{ cookiecutter.project_slug }}")) / "unified_logs.db"
    backup_path = None
    
    # Backup existing database if it exists
    if real_db_path.exists():
        backup_path = real_db_path.with_suffix('.db.backup')
        shutil.copy2(real_db_path, backup_path)
    
    # Let tests run
    yield
    
    # Cleanup test data from database
    if real_db_path.exists():
        try:
            # Remove the test database
            real_db_path.unlink()
        except Exception as e:
            print(f"Warning: Failed to remove test database: {e}")
    
    # Restore backup if it existed
    if backup_path and backup_path.exists():
        try:
            shutil.move(backup_path, real_db_path)
        except Exception as e:
            print(f"Warning: Failed to restore database backup: {e}")


@pytest_asyncio.fixture
async def mcp_server(backup_and_cleanup_db) -> AsyncGenerator[Dict[str, Any], None]:
    """Start MCP server subprocess for tests."""
    # Environment variables for the subprocess
    env = os.environ.copy()
    env['PYTHONWARNINGS'] = 'ignore::RuntimeWarning'
    
    # Use the standard server - tests will use the real user directories
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "{{ cookiecutter.project_slug }}.server.app", "--transport", "stdio"],
        env=env
    )
    
    # Store server info - we'll use the real user directory for the database
    real_db_path = Path(platformdirs.user_data_dir("{{ cookiecutter.project_slug }}")) / "unified_logs.db"
    
    server_info = {
        "params": server_params,
        "db_path": real_db_path,
        "real_data_dir": Path(platformdirs.user_data_dir("{{ cookiecutter.project_slug }}"))
    }
    
    yield server_info


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
    
    # Wait longer for database to be created (server startup + first log write)
    import time
    max_wait_seconds = 5
    wait_interval = 0.2
    
    for _ in range(int(max_wait_seconds / wait_interval)):
        if db_path.exists():
            break
        time.sleep(wait_interval)
    
    if not db_path.exists():
        # Create the database directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # The database will be created on first write, so we'll connect anyway
        # This allows the test to proceed and fail later if there's a real issue
    
    conn = sqlite3.connect(str(db_path))
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