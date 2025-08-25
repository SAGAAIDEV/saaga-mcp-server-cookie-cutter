---
description: Fetch and understand a JIRA issue
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
allowed-tools: ["mcp__Conduit__search_jira_issues"]
---

I'll fetch JIRA issue $ARGUMENTS and provide a clear summary.

## Fetch Issue Details
Using the provided issue key and site alias to retrieve the JIRA issue.

## Summary Format
After fetching, I'll provide:
- **Issue Type**: (Feature/Bug/Task)
- **Summary**: One-line description
- **Key Requirements**: Main points from description
- **Acceptance Criteria**: What defines "done"
- **Priority/Labels**: Any important metadata

---

## 🚀 Next Step
After reviewing the issue summary, run:
```
/project:analyze-feasibility
```
This will check if the feature already exists in the codebase.