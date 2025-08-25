---
description: Execute appropriate tests for the current implementation
argument-hint: "[OPTIONAL-HINTS]"
allowed-tools: ["Bash", "Read", "Grep", "Task"]
---

## Test Current Implementation - Template Development

I'll analyze the changes and run appropriate tests based on what was implemented.

## Grounding References
- **Test Patterns**: `{{cookiecutter.project_slug}}/.reference/patterns/integration_test_patterns.py` 
- **Unit Tests**: `{{cookiecutter.project_slug}}/.reference/patterns/unit_test_patterns.py`

### Step 1: Analyze Changes
Review what was modified to determine appropriate test approach.

### Step 2: Run Tests
Based on the implementation type:
- **MCP Tools**: Run integration tests
- **Utilities**: Run unit tests  
- **Template Changes**: Generate test server
- **Documentation**: Verify examples work

### Step 3: Validate
Ensure all tests pass and implementation meets requirements.

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