---
description: Fetch and understand a JIRA issue for template development
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
allowed-tools: ["mcp__Conduit__search_jira_issues", "mcp__mcp_jira__search_jira_issues"]
---

## Fetch JIRA Issue - Template Development

I'll fetch and summarize JIRA issue $ARGUMENTS for template development work.

## Grounding References
- **Template Context**: Working on the cookie cutter template repository itself
- **Evolution Guidelines**: See `.reference/template-evolution.md` for version management

### Step 1: Parse Arguments
- Arguments: $ARGUMENTS
- Expected format: [ISSUE-KEY] [SITE-ALIAS] (e.g., "ACT-123 saaga")

### Step 2: Fetch Issue Details
Using the parsed issue key and site alias to retrieve the issue from JIRA.

### Step 3: Summary
After fetching, I'll provide:
- **Issue Type**: (Bug/Feature/Task/Story)
- **Summary**: Brief description
- **Status**: Current workflow state
- **Key Requirements**: What needs to be done
- **Acceptance Criteria**: How we'll know it's complete
- **Priority**: Issue priority level
- **Assignee**: Who's responsible

---

## 🔄 Next Step

Once I've fetched the issue, you should analyze if it's already implemented:

```
/project:devflow/analyze-feasibility
```

This will check the codebase for existing implementations before we proceed.