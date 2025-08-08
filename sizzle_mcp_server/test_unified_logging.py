#!/usr/bin/env python3
"""
Test script for unified logging system with correlation IDs.

This script demonstrates and tests the unified logging functionality:
- Correlation ID generation and propagation
- Different log types (tool_execution, internal, framework)
- SQLite destination persistence
- Query capabilities
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sizzle_mcp_server.config import get_config
from sizzle_mcp_server.logging import (
    get_tool_logger,
    get_correlation_id,
    set_correlation_id,
    CorrelationContext,
    UnifiedLogger,
    SQLiteDestination
)

# Also test standard logging integration
standard_logger = logging.getLogger(__name__)


async def test_tool_simulation():
    """Simulate a tool execution with correlation ID."""
    # Set a correlation ID for this tool execution
    correlation_id = set_correlation_id()
    
    # Get a tool logger
    logger = get_tool_logger("test_tool")
    
    logger.info("Starting test tool execution", 
                log_type="tool_execution",
                tool_name="test_tool",
                status="running")
    
    # Simulate some work with internal logs
    standard_logger.info("Standard logging should also have correlation ID")
    logger.debug("Processing input data")
    
    # Simulate success
    logger.info("Test tool completed successfully",
                log_type="tool_execution", 
                tool_name="test_tool",
                status="success",
                duration_ms=150.5,
                output_summary="Processed 10 items")
    
    return correlation_id


async def test_error_scenario():
    """Test error logging with correlation."""
    with CorrelationContext() as correlation_id:
        logger = get_tool_logger("error_test")
        
        logger.warning("Starting risky operation")
        
        try:
            # Simulate an error
            raise ValueError("Simulated error for testing")
        except Exception as e:
            logger.error(f"Operation failed: {e}",
                        log_type="tool_execution",
                        tool_name="error_test",
                        status="error",
                        error_message=str(e))
        
        return correlation_id


async def test_concurrent_logging():
    """Test that correlation IDs are properly isolated between concurrent tasks."""
    async def task(task_id: int):
        correlation_id = set_correlation_id()
        logger = get_tool_logger(f"concurrent_task_{task_id}")
        
        logger.info(f"Task {task_id} started")
        await asyncio.sleep(0.1)  # Simulate work
        logger.info(f"Task {task_id} completed")
        
        return correlation_id
    
    # Run multiple tasks concurrently
    tasks = [task(i) for i in range(5)]
    correlation_ids = await asyncio.gather(*tasks)
    
    # Verify all correlation IDs are unique
    assert len(set(correlation_ids)) == len(correlation_ids)
    print(f"✓ All {len(correlation_ids)} concurrent tasks had unique correlation IDs")
    
    return correlation_ids


async def test_query_logs(destination: SQLiteDestination):
    """Test querying logs from the destination."""
    print("\n📊 Testing log queries...")
    
    # Query all logs
    all_logs = await destination.query(limit=10)
    print(f"Found {len(all_logs)} total log entries")
    
    # Query by correlation ID (using the first one from our tests)
    if all_logs:
        test_correlation_id = all_logs[0].correlation_id
        correlated_logs = await destination.query(correlation_id=test_correlation_id)
        print(f"Found {len(correlated_logs)} logs with correlation ID {test_correlation_id}")
        
        for log in correlated_logs[:3]:  # Show first 3
            print(f"  - [{log.level}] {log.message}")
    
    # Query by log type
    tool_logs = await destination.query(log_type="tool_execution", limit=5)
    print(f"Found {len(tool_logs)} tool execution logs")
    
    # Query by level
    error_logs = await destination.query(level="ERROR", limit=5)
    print(f"Found {len(error_logs)} error logs")
    
    # Get statistics
    stats = destination.get_statistics()
    print("\n📈 Log Statistics:")
    print(f"  Total logs: {stats['total_logs']}")
    print(f"  Logs by type: {stats['logs_by_type']}")
    print(f"  Logs by level: {stats['logs_by_level']}")
    print(f"  Tool executions: {stats['tool_executions']}")


async def main():
    """Run all tests."""
    print("🧪 Testing Unified Logging System with Correlation IDs\n")
    
    # Initialize configuration
    config = get_config()
    print(f"Using database: {config.data_dir / 'unified_logs.db'}")
    
    # Initialize unified logging
    destination = SQLiteDestination(config)
    UnifiedLogger.initialize(destination)
    UnifiedLogger.set_event_loop(asyncio.get_running_loop())
    
    try:
        # Test 1: Basic tool simulation
        print("\n1️⃣ Testing basic tool logging...")
        correlation_id1 = await test_tool_simulation()
        print(f"✓ Tool execution logged with correlation ID: {correlation_id1}")
        
        # Test 2: Error scenario
        print("\n2️⃣ Testing error logging...")
        correlation_id2 = await test_error_scenario()
        print(f"✓ Error scenario logged with correlation ID: {correlation_id2}")
        
        # Test 3: Concurrent logging
        print("\n3️⃣ Testing concurrent logging isolation...")
        await test_concurrent_logging()
        
        # Test 4: Framework logging
        print("\n4️⃣ Testing framework logging...")
        framework_logger = UnifiedLogger.get_logger("framework.test")
        framework_logger.info("Framework component initialized",
                            log_type="framework")
        print("✓ Framework logging working")
        
        # Give async writes a moment to complete
        await asyncio.sleep(0.5)
        
        # Test 5: Query capabilities
        await test_query_logs(destination)
        
        print("\n✅ All tests completed successfully!")
        
    finally:
        # Clean up
        await UnifiedLogger.close()


if __name__ == "__main__":
    asyncio.run(main())