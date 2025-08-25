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

## Implementation Process

### Step 1: Review Plan
I'll reference the plan created earlier to ensure alignment.

### Step 2: Implement Changes
Following the approved plan, I'll:
- Create new files as specified
- Modify existing files according to requirements  
- Apply all required patterns and conventions
- Follow grounding references from `.reference/`

### Step 3: Track Progress
I'll use TodoWrite to track implementation tasks as I complete them.

### Step 4: Verify Implementation
After each major component:
- Ensure code follows patterns
- Check decorator requirements
- Validate async/await usage
- Confirm Context parameter inclusion

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