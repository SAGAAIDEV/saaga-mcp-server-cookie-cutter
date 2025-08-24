---
description: Analyze if a JIRA issue's requirements are already implemented
argument-hint: ""
allowed-tools: ["Grep", "Glob", "Read", "Task", "Bash"]
---

## Analyze Implementation Feasibility - Template Repository

I'll analyze the cookie cutter template codebase to determine if the JIRA issue's requirements are already implemented or if there are any conflicts.

## Grounding References
- **Critical Files**: Check `.reference/critical-files.md` before modifying core components
- **Template Patterns**: See `.reference/cookiecutter-maintenance.md` for implementation patterns
- **MCP/SAAGA Patterns**: Reference `{{cookiecutter.project_slug}}/.reference/` for understanding what template generates

### Step 1: Extract Key Terms
From the previously fetched JIRA issue, I'll identify:
- Function/class names mentioned
- Feature keywords
- UI components or endpoints
- Configuration settings

### Step 2: Search Codebase
I'll search for existing implementations:
- Grep for relevant keywords and patterns
- Check file structure for mentioned components
- Review recent commits for related work
- Look for feature flags or configuration

### Step 3: Check Documentation
- Search README and docs for feature mentions
- Look for architecture decisions
- Check for deprecation notices

### Step 4: Report Findings
I'll provide a clear assessment:
- **Not Implemented**: Ready to proceed ✅
- **Partially Implemented**: What exists vs. what's missing 🔄
- **Fully Implemented**: Evidence of existing implementation ❌
- **Conflicts Found**: Architectural concerns to discuss ⚠️

---

## 🔄 Next Steps

Based on my findings:

**If NOT implemented or PARTIALLY implemented:**
```
/project:devflow/create-branch [ISSUE-KEY] [SITE-ALIAS]
```
This will create a development branch and update JIRA status.

**If FULLY implemented:**
Consider closing the JIRA issue or converting to documentation task.

**If CONFLICTS found:**
Discuss with team before proceeding.