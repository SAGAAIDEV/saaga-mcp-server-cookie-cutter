---
description: Create a branch for the JIRA issue and update its status
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
allowed-tools: ["Bash", "mcp__Conduit__update_jira_status", "mcp__mcp_jira__update_jira_issue"]
---

## Create Branch and Update Status - Template Development

I'll create an appropriate Git branch for template development and update the JIRA issue status to "In Progress".

## Grounding References
- **Version Management**: Follow `.reference/template-evolution.md` for branch naming conventions
- **Breaking Changes**: Check `.reference/template-evolution.md#breaking-changes` if this is a major change

### Step 1: Determine Branch Type
Based on the issue type from our earlier fetch:
- **Feature/Story**: `feature/[ISSUE-KEY]-<description>`
- **Bug**: `fix/[ISSUE-KEY]-<description>`
- **Task**: `task/[ISSUE-KEY]-<description>`
- **Other**: `issue/[ISSUE-KEY]-<description>`

### Step 2: Create Branch
Create and checkout the new branch with appropriate naming.

### Step 3: Update JIRA Status
Update the issue status to "In Progress" using the provided site alias.

### Step 4: Confirm
Report the new branch name and confirm JIRA status update.

---

## 🔄 Next Step

Now that you're on a development branch, plan the implementation:

```
/project:devflow/plan-implementation
```

This will:
- Research any unfamiliar technologies
- Create a detailed implementation plan
- Prepare for exit plan mode

The plan will be grounded in:
- `.reference/patterns/tool_patterns.py` for MCP tool structure
- `.reference/saaga-mcp-integration.md` for decorator patterns
- Your project's existing code conventions