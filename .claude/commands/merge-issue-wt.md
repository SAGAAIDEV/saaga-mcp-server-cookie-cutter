---
description: Merge an issue from worktree to main and clean up the worktree without creating a PR
argument-hint: "[SITE-ALIAS]"
allowed-tools: ["Bash", "mcp__Conduit__search_jira_issues", "mcp__Conduit__update_jira_status"]
---

I'll help you merge the current issue from the worktree to main locally, update JIRA, and clean up the worktree without creating a PR.

## Parse Arguments
- Site alias provided: $ARGUMENTS (e.g., "saaga")
- I'll extract the JIRA issue key from the current branch name
- I'll determine the worktree location and main repository path

## Step 1: Review Changes
First, let me check the current status and verify we're in a worktree:

!pwd
!git status
!git diff --stat
!git worktree list

## Step 2: Run Quality Checks
Running linting and tests before merging:

!ruff check .
!pytest

## Step 3: Commit Changes
I'll stage all changes and create a detailed commit message:

!git add -A

The commit message will follow conventional commits format based on issue type:
- **Feature/Story**: `feat: [Description]`
- **Bug**: `fix: [Description]`
- **Task**: `task: [Description]`
- **Other**: `chore: [Description]`

The commit will include:
- Brief description
- Detailed changes
- Reference to JIRA issue
- Claude Code attribution

## Step 4: Navigate to Main Repository
Before merging, I need to go back to the main repository:

!cd ../../
!pwd

Verify we're in the main repository root:
!git status

## Step 5: Merge from Worktree
Merge the issue branch from the worktree to main:

!git checkout main
!git merge [ISSUE-BRANCH-NAME]

## Step 6: Update JIRA to Done
After the merge, I'll:
1. Extract the JIRA issue key from the branch name (e.g., fix/ASEP-40-description → ASEP-40)
2. Update the issue status to 'Done' using mcp__Conduit__update_jira_status with the site alias
3. Add a comment about local merge completion using mcp__conduit__update_jira_issue

## Step 7: Clean Up Worktree and Branch
Remove the worktree and associated branch:

!git worktree remove trees/[WORKTREE-NAME]
!git branch -d [ISSUE-BRANCH-NAME]

Verify cleanup:
!git worktree list
!git branch

## Step 8: Return to Original Working Location
Navigate back to where you were working before:

!cd [ORIGINAL-WORKING-DIRECTORY]

Let's start by reviewing your changes and current worktree status...

---

## 🚀 Next Steps After Worktree Merge

Once your issue is merged and worktree cleaned up:

1. **Start your next issue with a new worktree:**
   ```
   /project:start-issue [NEW-ISSUE-KEY] [SITE-ALIAS]
   ```
   This will create a fresh worktree for the new issue

2. **Continue working in main (if needed):**
   - You're now back in the main workspace
   - Can make quick fixes or start work that doesn't need isolation

3. **When ready to sync with remote:**
   ```
   !git push origin main
   ```
   Push all accumulated changes to remote

4. **If you need to create PRs later:**
   - Use individual commits in main to create separate PRs
   - Or create a single PR with all accumulated changes

💡 **Tips:** 
- The worktree is completely removed - no disk space waste
- Each issue gets its own isolated environment via worktrees
- You can have multiple worktrees active simultaneously for parallel work
- Use `git worktree list` anytime to see active worktrees
- Main workspace remains clean and available for quick tasks 