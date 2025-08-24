---
description: Check if JIRA issue requirements already exist in codebase
allowed-tools: ["Grep", "Task", "Read", "Glob", "Bash"]
---

I'll analyze the codebase to determine if this feature already exists or conflicts with current architecture.

## Search Strategy
Based on the JIRA issue requirements from the previous step, I'll:
1. Search for keywords from the issue description
2. Look for related function/class names
3. Check for similar components or endpoints
4. Review recent commits for related work

## Analysis Output
I'll report my findings:
- **Implementation Status**: 
  - ✅ Not found - safe to proceed
  - 🔄 Partially exists - showing what's already there
  - ❌ Fully implemented - feature already exists
  - ⚠️ Conflicts detected - architectural concerns

- **Evidence**: Specific files and code locations found
- **Recommendation**: Whether to proceed or discuss with team

---

## 🚀 Next Steps
Based on the analysis:
- **If safe to proceed**: 
  ```
  /project:create-branch [ISSUE-KEY] [SITE-ALIAS]
  ```
- **If partially exists or has concerns**: Review findings, then decide whether to proceed
- **If fully implemented**: Consider closing the JIRA issue