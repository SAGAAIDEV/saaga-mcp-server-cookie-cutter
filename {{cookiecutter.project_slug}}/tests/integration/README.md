# Integration Tests

This directory contains integration tests for {{ cookiecutter.project_name }}, focusing on end-to-end testing of MCP server functionality.

## Correlation ID Tests

The `test_correlation_ids.py` file contains comprehensive tests for correlation ID functionality:

### Test Coverage

1. **Client-Provided Correlation IDs**
   - Verifies that correlation IDs provided by MCP clients are properly logged
   - Tests all 6 example tools with unique correlation IDs
   - Ensures multiple tools can share the same correlation ID

2. **Auto-Generated Correlation IDs**
   - Tests that correlation IDs are auto-generated when not provided
   - Verifies ULID format (req_XXXXXXXXXXXXXXXXXXXXXXXXXXXX)
   - Ensures uniqueness of generated IDs

3. **Edge Cases**
   - Tool errors include correlation IDs in error logs
   - Empty correlation IDs trigger auto-generation
   - Database persistence and querying

## Running the Tests

### Using pytest directly:
```bash
# Run all integration tests
pytest tests/integration/

# Run with verbose output
pytest tests/integration/ -vv

# Run only client-provided ID tests
pytest tests/integration/ -k "client_provided"

# Run only auto-generated ID tests
pytest tests/integration/ -k "auto_generated"

# Run tests for a specific tool
pytest tests/integration/ -k "echo_tool"
```

### Using the helper script:
```bash
# Run all integration tests
python run_integration_tests.py

# Run with verbose output
python run_integration_tests.py -v

# Run only tests matching a keyword
python run_integration_tests.py -k "auto"

# Disable coverage reporting for faster runs
python run_integration_tests.py --no-cov
```

## Test Architecture

### Fixtures (in `conftest.py`)

1. **`isolated_db_path`** - Creates isolated database for each test
2. **`mock_platformdirs`** - Overrides platform directories for test isolation
3. **`mcp_server`** - Starts MCP server subprocess with test configuration
4. **`mcp_client`** - Creates connected MCP client session
5. **`db_connection`** - Provides SQLite connection for verification

### Test Isolation

- Each test gets its own temporary database
- Server subprocess is started fresh for each test session
- No interference between tests
- Automatic cleanup after tests complete

## Debugging Failed Tests

1. **Check server startup**:
   ```bash
   pytest tests/integration/ -vv -s
   ```
   The `-s` flag shows print statements and server output.

2. **Examine database contents**:
   Tests create databases in temporary directories. Add debugging code:
   ```python
   print(f"Database path: {db_connection}")
   ```

3. **Check correlation ID format**:
   Failed assertions will show the actual vs expected values.

## Adding New Integration Tests

1. Create new test classes for different features
2. Use the existing fixtures for server/client setup
3. Follow the parametrized test pattern for multiple scenarios
4. Always clean up resources in fixtures

## Performance Considerations

- Integration tests are slower than unit tests (server startup overhead)
- Use `pytest-xdist` for parallel execution: `pytest -n auto tests/integration/`
- Consider grouping related tests to share server instances
- Use the `--no-cov` flag for faster local development runs