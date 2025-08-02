# Coverage Testing for MCP Integration Tests

## Quick Start

Integration tests spawn the MCP server as a subprocess, which requires special coverage configuration to track code execution in the subprocess.

### 1. One-Time Setup (already included in template)

```bash
# .coveragerc file configures coverage for subprocesses
# sitecustomize.py enables coverage in spawned processes
```

### 2. Running Tests with Coverage

```bash
# Set environment variable to enable subprocess coverage
export COVERAGE_PROCESS_START=$(pwd)/.coveragerc

# Run the complete coverage workflow
coverage erase && \
coverage run -m pytest tests/integration/test_mcp_integration.py -v && \
coverage combine && \
coverage report

# Generate HTML report for detailed analysis
coverage html
# Open htmlcov/index.html in your browser
```

### 3. Alternative: Without Coverage (faster)

```bash
# Run tests without coverage tracking
python -m pytest tests/integration/test_mcp_integration.py -v --no-cov
```

## Understanding Coverage Reports

- **0% Coverage**: Subprocess code not being tracked (check COVERAGE_PROCESS_START)
- **Partial Coverage**: Normal - integration tests may not hit all code paths
- **Missing Lines**: Use HTML report to see exactly which lines weren't executed

## Troubleshooting Low Coverage

1. **Ensure subprocess tracking is enabled**:
   ```bash
   echo $COVERAGE_PROCESS_START  # Should show path to .coveragerc
   ```

2. **Check for coverage data files**:
   ```bash
   ls -la .coverage.*  # Should see multiple files after test run
   ```

3. **Verify sitecustomize.py is being loaded**:
   ```bash
   python -c "import sitecustomize"  # Should not error
   ```

## Coverage Configuration Details

### .coveragerc
```ini
[run]
source = your_project_name
parallel = true
concurrency = multiprocessing

[report]
skip_empty = true

[paths]
source =
    your_project_name/
    */your_project_name/
```

### sitecustomize.py
```python
"""Enable coverage measurement in subprocesses."""
import coverage
coverage.process_startup()
```

## Tips for Better Coverage

1. **Write comprehensive integration tests** that exercise all tool functionality
2. **Test error paths** in addition to success paths  
3. **Include edge cases** like empty inputs, invalid types
4. **Run full test suite** including unit tests for complete coverage
5. **Use branch coverage** to ensure all code paths are tested:
   ```bash
   coverage run --branch -m pytest
   ```