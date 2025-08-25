---
description: Create implementation plan based on JIRA requirements and codebase analysis
allowed-tools: ["ExitPlanMode", "mcp__context7__resolve-library-id", "mcp__context7__get-library-docs", "WebSearch"]
---

I'll create a detailed implementation plan based on the issue requirements and our codebase analysis.

## Research Phase
If the issue mentions unfamiliar technologies, I'll:
1. Use Context7 to research libraries and frameworks
2. Look up best practices for the specific use case

## Implementation Plan
Based on all gathered information, I'll provide:

### Components to Create/Modify
- List of files to create or change
- Order of implementation

### Testing Strategy
- **Test Type**: UI/MCP/Integration/Regression
- **Key Test Cases**: Based on acceptance criteria

### Integration Points
- How new code integrates with existing codebase
- Any refactoring needed based on feasibility analysis

### Risk Assessment
- Technical challenges identified
- Dependencies or blockers

## Ready for Implementation
Once you approve this plan, I'll use ExitPlanMode and you can begin coding.

---

## 🚀 After Implementation
Once you've coded the solution:
```
/project:test-issue
```
This will run appropriate tests for your implementation.

When tests pass:
```
/project:complete-issue [SITE-ALIAS]
```
This will commit, create PR, and update JIRA to Done.