---
description: Sync with remote after PR merge and clean up
argument-hint: ""
allowed-tools: ["Bash", "Read"]
---

## Post-Merge Sync and Cleanup - Template Development

I'll sync your local repository with the merged changes and prepare for the next issue.

### Step 1: Check Current State
Verify current branch and status:

!git status
!git branch --show-current

### Step 2: Switch to Main
Return to main branch:

!git checkout main

### Step 3: Pull Latest Changes
Get the merged PR and any other updates:

!git pull origin main

### Step 4: Verify Merge
Confirm your changes are in main:

!git log --oneline -10

### Step 5: Clean Up Feature Branch
Remove the local feature branch:

!git branch -d $(git rev-parse --abbrev-ref @{-1})

Optional: Remove remote branch if not auto-deleted:
!git push origin --delete $(git rev-parse --abbrev-ref @{-1})

### Step 6: Update Dependencies
Ensure environment is current:

!uv sync

### Step 7: Run Tests
Verify everything still works after merge:

!pytest

---

## 🚀 Ready for Next Issue!

Your environment is clean and ready. Start your next issue:

```
/project:devflow/fetch-issue [NEW-ISSUE-KEY] [SITE-ALIAS]
```

This will begin a new development cycle with:
- Fresh JIRA issue fetch
- New feature branch
- Clean workspace

💡 **Tip**: Keep your main branch updated regularly to avoid conflicts!