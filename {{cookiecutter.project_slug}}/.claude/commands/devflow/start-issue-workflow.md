---
description: Guided workflow for starting a JIRA issue (uses atomic commands)
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
---

I'll guide you through starting work on JIRA issue $ARGUMENTS using our atomic workflow.

## 📋 Workflow Overview
This guided flow breaks down the complex process into focused steps:

1. **Fetch & Understand** - Get JIRA issue details
2. **Analyze Feasibility** - Check if already implemented
3. **Create Branch** - Set up Git and update JIRA
4. **Plan Implementation** - Create detailed plan

Each step is a separate command that does one thing well. You review the output and decide whether to proceed.

## Step 1: Fetch Issue
First, let's fetch and understand the JIRA issue:
```
/project:fetch-issue $ARGUMENTS
```

**What happens**: I'll retrieve the issue and provide a clear summary of requirements and acceptance criteria.

**Your decision point**: Review the requirements to ensure you understand what needs to be built.

## Step 2: Analyze Feasibility
After understanding the issue, check if it's already implemented:
```
/project:analyze-feasibility
```

**What happens**: I'll search the codebase for existing implementations or conflicts.

**Your decision point**: Based on findings, decide whether to:
- Proceed (not implemented)
- Modify approach (partially exists)
- Stop (fully implemented)

## Step 3: Create Branch
If proceeding, create the branch and update JIRA:
```
/project:create-branch $ARGUMENTS
```

**What happens**: I'll create an appropriately named Git branch and set JIRA to "In Progress".

**Your decision point**: Confirm branch creation before planning.

## Step 4: Plan Implementation
Finally, create the implementation plan:
```
/project:plan-implementation
```

**What happens**: I'll research any unfamiliar tech and create a detailed plan with test strategy.

**Your decision point**: Review and approve the plan before starting to code.

---

## 💡 Why This Approach?

- **Clear Signal**: Each command has a single, focused purpose
- **Human Control**: You review and decide at each step
- **Natural Flow**: Commands build on each other progressively
- **Flexible**: Can stop, restart, or skip steps as needed

## 🚦 Ready to Start?
Begin with:
```
/project:fetch-issue $ARGUMENTS
```