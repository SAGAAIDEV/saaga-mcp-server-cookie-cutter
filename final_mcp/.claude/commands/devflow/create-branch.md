---
description: Create Git branch and update JIRA status to In Progress
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
allowed-tools: ["Bash", "mcp__Conduit__update_jira_status"]
---

I'll create a Git branch for issue $ARGUMENTS and update its JIRA status.

## Step 1: Determine Branch Type
Based on the issue type identified earlier:
- **Feature/Story**: `feature/[ISSUE-KEY]-brief-description`
- **Bug**: `fix/[ISSUE-KEY]-brief-description`  
- **Task**: `task/[ISSUE-KEY]-brief-description`

## Step 2: Create Branch
Creating the branch with appropriate naming convention.

## Step 3: Update JIRA Status
Updating the issue to "In Progress" status.

## Summary
- Branch created and checked out
- JIRA issue marked as In Progress
- Ready for implementation

---

## 🚀 Next Step
Now plan the implementation:
```
/project:plan-implementation
```
This will create a detailed implementation plan based on the issue requirements and codebase analysis.