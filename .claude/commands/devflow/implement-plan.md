---
description: Implement the approved plan - actual coding phase
argument-hint: ""
allowed-tools: ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep", "Glob", "TodoWrite"]
---

## Implement Approved Plan - Template Development

I'll now implement the plan that was previously created and approved.

## Prerequisites
This command should only be run after:
1. `/project:devflow/plan-implementation` has been executed
2. You have reviewed and approved the plan

## Grounding References for Implementation
- **Template Patterns**: `.reference/cookiecutter-maintenance.md`
- **MCP Tool Patterns**: `{{cookiecutter.project_slug}}/.reference/patterns/tool_patterns.py`
- **Integration Tests**: `{{cookiecutter.project_slug}}/.reference/patterns/integration_test_patterns.py`
- **Unit Tests**: `{{cookiecutter.project_slug}}/.reference/patterns/unit_test_patterns.py`
- **SAAGA Integration**: `{{cookiecutter.project_slug}}/.reference/saaga-mcp-integration.md`

## Implementation Process

### Step 1: Review Plan
I'll reference the plan created earlier to ensure alignment.

### Step 2: Implement Changes
Following the approved plan, I'll:
- Create new files as specified
- Modify existing files according to requirements  
- Apply all required patterns and conventions
- Follow grounding references from `.reference/`

### Step 3: Generate Tests
**CRITICAL**: Tests must be created alongside implementation:
- **For MCP Tools**: Create integration tests following `integration_test_patterns.py`
- **For Utilities**: Create unit tests following `unit_test_patterns.py`
- **For Template Changes**: Update test fixtures in `tests/`
- All tests must use the patterns from `.reference/patterns/`
- Tests should validate both success and error cases

### Step 4: Track Progress
I'll use TodoWrite to track implementation tasks as I complete them.

### Step 5: Verify Implementation
After each major component:
- Ensure code follows patterns
- Check decorator requirements
- Validate async/await usage
- Confirm Context parameter inclusion
- Confirm tests are created and follow patterns

---

## 🔄 Next Step

After implementation is complete, test the changes:

```
/project:devflow/test-issue
```

This will:
- Analyze what was implemented
- Run appropriate tests
- Validate the implementation meets requirements

**Important**: Don't skip testing! Always verify your implementation works before creating a PR.