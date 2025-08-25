---
description: Complete the issue with PR creation and JIRA update
argument-hint: "[SITE-ALIAS]"
allowed-tools: ["Bash", "mcp__Conduit__update_jira_status", "mcp__mcp_jira__update_jira_issue"]
---

## Complete Issue and Create PR - Template Development

I'll finalize your implementation, create a pull request, and update JIRA.

## Parse Arguments
- Site alias provided: $ARGUMENTS (e.g., "saaga")
- I'll extract the JIRA issue key from the current branch name

### Step 1: Run Final Quality Checks
Ensure code quality before creating PR:

!ruff check .
!ruff format --check .
!pytest

**IMPORTANT**: If any of these checks fail:
- **Linting errors**: Fix with `ruff check --fix .` or manually
- **Format errors**: Fix with `ruff format .`
- **Test failures**: Return to implementation to fix issues
- Do NOT proceed until all checks pass!

### Step 2: Stage and Commit Changes
I'll create a comprehensive commit with:
- Conventional commit format based on issue type
- Detailed description of changes
- JIRA issue reference
- Claude Code attribution

!git add -A

### Step 3: Push Branch
Push the feature branch to remote:

!git push -u origin $(git branch --show-current)

### Step 4: Create Pull Request
First, verify GitHub CLI is available:
!gh --version

If `gh` is not installed:
- macOS: `brew install gh`
- Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
- Then run: `gh auth login`

Create PR using GitHub CLI with:
- Clear title referencing JIRA issue
- Summary of changes
- Test plan
- Claude Code attribution

### Step 5: Update JIRA Status
Update the issue to "Done" and add PR link as comment.

---

## 🔄 Next Step

After your PR is reviewed and merged by a team member:

```
/project:devflow/post-merge
```

This will:
- Sync your local main with remote
- Clean up the feature branch
- Prepare for your next issue

**Important**: Notify your team in Slack/Teams about the PR!