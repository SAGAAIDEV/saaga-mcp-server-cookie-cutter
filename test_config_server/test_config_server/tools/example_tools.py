"""Example MCP tools for Test Config Server

This module provides example tools that demonstrate how to create MCP tools
with the SAAGA decorator pattern. These tools are automatically registered
with the server and decorated with exception handling, logging, and optional
parallelization.
"""

import time
import random
from typing import List, Dict, Any, Optional

async def echo_tool(message: str) -> str:
    """Echo back the input message.
    
    This is a simple example tool that demonstrates basic MCP tool functionality.
    It will be automatically decorated with SAAGA decorators for exception handling
    and logging.
    
    Args:
        message: The message to echo back
        
    Returns:
        The echoed message with a prefix
    """
    return f"Echo: {message}"


async def get_time() -> str:
    """Get the current time.
    
    Returns the current time in a human-readable format.
    
    Returns:
        Current time as a string
    """
    return f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}"


async def random_number(min_value: int = 1, max_value: int = 100) -> Dict[str, Any]:
    """Generate a random number within a specified range.
    
    Args:
        min_value: Minimum value (default: 1)
        max_value: Maximum value (default: 100)
        
    Returns:
        Dictionary containing the random number and range info
    """
    if min_value > max_value:
        raise ValueError("min_value must be less than or equal to max_value")
    
    number = random.randint(min_value, max_value)
    return {
        "number": number,
        "range": f"{min_value}-{max_value}",
        "timestamp": time.time()
    }


async def calculate_fibonacci(n: int) -> Dict[str, Any]:
    """Calculate the nth Fibonacci number.
    
    This is a more computationally intensive example that demonstrates
    how tools can handle more complex operations.
    
    Args:
        n: The position in the Fibonacci sequence (must be >= 0)
        
    Returns:
        Dictionary containing the Fibonacci number and calculation info
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return {"position": n, "value": n, "calculation_time": 0}
    
    start_time = time.time()
    
    # Calculate Fibonacci number
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    calculation_time = time.time() - start_time
    
    return {
        "position": n,
        "value": b,
        "calculation_time": calculation_time
    }


async def process_batch_data(items: List[str], operation: str = "upper") -> Dict[str, Any]:
    """Process a batch of data items.
    
    This is an example of a tool that benefits from parallelization.
    It will be automatically decorated with the parallelize decorator
    in addition to exception handling and logging.
    
    Args:
        items: List of strings to process
        operation: Operation to perform ('upper', 'lower', 'reverse')
        
    Returns:
        Processed items with metadata
    """
    # Simulate some processing time
    import asyncio
    await asyncio.sleep(0.1)
    
    processed_items = []
    for item in items:
        if operation == "upper":
            processed = item.upper()
        elif operation == "lower":
            processed = item.lower()
        elif operation == "reverse":
            processed = item[::-1]
        else:
            raise ValueError(f"Unknown operation: {operation}")
        processed_items.append(processed)
    
    return {
        "original": items,
        "processed": processed_items,
        "operation": operation,
        "timestamp": time.time()
    }


async def simulate_heavy_computation(complexity: int = 5) -> Dict[str, Any]:
    """Simulate a heavy computation task.
    
    This tool demonstrates parallelization benefits by performing
    a computationally intensive task that can be parallelized.
    
    Args:
        complexity: Complexity level (1-10, higher = more computation)
        
    Returns:
        Dictionary containing computation results
    """
    if complexity < 1 or complexity > 10:
        raise ValueError("complexity must be between 1 and 10")
    
    start_time = time.time()
    
    # Simulate heavy computation
    result = 0
    iterations = complexity * 100000  # Reduced for async context
    
    for i in range(iterations):
        result += i * 2
        if i % 10000 == 0:
            # Yield control to allow other tasks to run
            import asyncio
            await asyncio.sleep(0.001)
    
    computation_time = time.time() - start_time
    
    return {
        "complexity": complexity,
        "iterations": iterations,
        "result": result,
        "computation_time": computation_time,
        "operations_per_second": iterations / computation_time if computation_time > 0 else 0
    }


# List of tools that benefit from parallelization
parallel_example_tools = [
    process_batch_data,
    simulate_heavy_computation
]
# List of regular example tools
example_tools = [
    echo_tool,
    get_time,
    random_number,
    calculate_fibonacci
]

async def get_tool_info() -> Dict[str, Any]:
    """Get information about available tools.
    
    Returns:
        Dictionary containing tool information
    """
    return {
        "total_tools": len(example_tools) + len(parallel_example_tools),
        "regular_tools": len(example_tools),
        "parallel_tools": len(parallel_example_tools),
        "tool_names": {
            "regular": [tool.__name__ for tool in example_tools],
            "parallel": [tool.__name__ for tool in parallel_example_tools]
        }
    }


if __name__ == "__main__":
    # Test tools functionality
    import asyncio
    
    async def test_tools():
        print("Tool Information:")
        print(await get_tool_info())
        
        print("\nTesting example tools:")
        print(await echo_tool("Hello, World!"))
        print(await get_time())
        print(await random_number(1, 10))
        print(await calculate_fibonacci(10))
        
        print("\nTesting parallel tools (individual calls):")
        print(await process_batch_data("hello", "upper"))
        print(await simulate_heavy_computation(2))
        asyncio.run(test_tools())