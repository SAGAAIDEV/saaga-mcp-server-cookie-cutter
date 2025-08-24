---
description: Quick start for JIRA issue workflow - intelligently chains the devflow commands
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
allowed-tools: ["mcp__Conduit__search_jira_issues", "Grep", "Glob", "Read", "Bash", "mcp__Conduit__update_jira_status", "ExitPlanMode"]
---

## Start Issue Workflow

I'll guide you through the complete JIRA issue workflow using our decomposed commands.

### Workflow Overview

I'll execute these phases in sequence, pausing for your approval at key decision points:

1. **Fetch Issue** - Retrieve and understand the JIRA issue
2. **Analyze Feasibility** - Check if already implemented
3. **Create Branch** - Setup development environment (if needed)
4. **Plan Implementation** - Research and create detailed plan

### Phase 1: Fetch Issue
First, I'll fetch JIRA issue $ARGUMENTS and provide a summary.

### Phase 2: Feasibility Check
After understanding the issue, I'll analyze the codebase for existing implementations.

**Decision Point**: Based on findings, you'll decide whether to proceed.

### Phase 3: Branch Creation (If Proceeding)
If you approve, I'll:
- Create an appropriate branch
- Update JIRA to "In Progress"

### Phase 4: Implementation Planning
Finally, I'll:
- Research any unfamiliar technologies
- Create a detailed implementation plan
- Use ExitPlanMode for your approval

---

## Manual Control

If you prefer to run each phase separately:

```bash
# Phase 1
/project:devflow/fetch-issue [ISSUE-KEY] [SITE-ALIAS]

# Phase 2
/project:devflow/analyze-feasibility

# Phase 3 (if needed)
/project:devflow/create-branch [ISSUE-KEY] [SITE-ALIAS]

# Phase 4
/project:devflow/plan-implementation
```

Let's begin with fetching the issue details...