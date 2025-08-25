---
description: Run tests created during implementation to validate changes
argument-hint: "[OPTIONAL-HINTS]"
allowed-tools: ["Bash", "Read", "Grep", "Task"]
---

## Run Tests for Current Implementation - Template Development

I'll run the tests that were created during the implementation phase to validate all changes work correctly.

## Grounding References
- **Test Patterns**: `{{cookiecutter.project_slug}}/.reference/patterns/integration_test_patterns.py` 
- **Unit Tests**: `{{cookiecutter.project_slug}}/.reference/patterns/unit_test_patterns.py`

### Step 1: Verify Tests Exist
Check that tests were created during implementation:
- Look for new test files in `tests/` directory
- Confirm test coverage for new functionality
- If tests are missing, return to `implement-plan` to add them

### Step 2: Run Tests
Execute the appropriate test suites:
- **Integration Tests**: `pytest tests/integration/ -v`
- **Unit Tests**: `pytest tests/unit/ -v`
- **Full Suite**: `pytest -v`
- **With Coverage**: `pytest --cov={{cookiecutter.project_slug}} --cov-report=term-missing`

### Step 3: Fix Failures
If any tests fail:
- Analyze the failure reason
- Fix implementation or test as needed
- Re-run tests to confirm fixes

### Step 4: Validate Coverage
Ensure adequate test coverage:
- New code should have >80% coverage
- Critical paths should have 100% coverage
- Error cases must be tested

---

## 🔄 Next Step

After tests pass successfully, complete the issue:

```
/project:devflow/complete-issue [SITE-ALIAS]
```

This will:
- Create a pull request with your changes
- Update JIRA status to Done
- Provide PR link for review