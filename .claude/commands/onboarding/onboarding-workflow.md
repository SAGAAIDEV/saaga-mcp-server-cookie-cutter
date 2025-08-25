---
description: Guide new team members through the AI-driven development workflow from JIRA issue to merged PR
argument-hint: ""
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep", "Glob"]
---

# 🚀 Welcome to AI-Driven Development with Claude!

I'll guide you through our complete development workflow. This process leverages Claude Code to implement JIRA issues efficiently while maintaining code quality.

## 📋 Complete Workflow Overview

Here's EXACTLY what you'll do from start to finish:

1. **Start JIRA Work** → `/project:devflow/fetch-issue [ISSUE-KEY] saaga`
   - Fetches JIRA ticket and analyzes requirements

2. **Guide Claude's Coding** → Monitor and provide feedback
   - Review changes, answer questions, course-correct as needed

3. **Run Automated Tests** → Have Claude run pytest/npm test
   - Ensures existing functionality isn't broken

4. **Generate & Launch Test MCP Server** → `/project:generate-test-server`
   - Creates fresh MCP server, launches Inspector & Admin UI for manual testing

5. **Create Pull Request** → `/project:devflow/complete-issue`
   - Commits changes, pushes branch, creates PR
   - **YOU MUST notify team in Slack/Teams**

6. **Sync After PR Merged** → `/project:devflow/post-merge`
   - Updates local main with merged changes, cleans up branch

Would you like detailed information about what each command does? Let me know and I'll explain the complete process for any step.

## Step 1: Start Your JIRA Issue 🎯

Begin by having Claude retrieve and analyze your assigned JIRA issue:

```bash
/project:devflow/fetch-issue [ISSUE-KEY] saaga
```

**Example**: `/project:devflow/fetch-issue ASEP-42 saaga`

### What happens:
- Claude fetches the JIRA issue details
- Reviews the current codebase structure
- Analyzes feasibility
- Creates a feature branch
- Forms an implementation plan
- Begins coding the solution after plan approval

### Your role:
- ✅ Review Claude's understanding of the issue
- ✅ Confirm the implementation plan makes sense
- ✅ Guide Claude if additional context is needed

## Step 2: Monitor and Guide Implementation 👀

As Claude implements the solution:

### Watch for:
- File modifications and creations
- Claude's use of the TodoWrite tool to track progress
- Any questions or clarifications Claude requests

### Provide guidance by:
- Answering Claude's questions about business logic
- Pointing out any missed requirements
- Suggesting specific approaches if needed
- Asking Claude to explain complex implementations

### Course corrections:
- If Claude goes off track: "Actually, let's approach this differently..."
- If something's missing: "Don't forget we also need to..."
- If you spot an issue: "I notice that might cause a problem with..."

## Step 3: Run Automated Tests 🧪

Once implementation appears complete, ensure quality:

```bash
# Ask Claude to run existing tests
"Please run the test suite to ensure nothing is broken"

# Claude will typically run:
# - pytest (for Python projects)
# - npm test (for Node projects)
# - ruff/flake8 (for linting)
```

### If tests fail:
- Have Claude analyze the failures
- Guide fixes for any broken tests
- Ensure new functionality has appropriate test coverage

## Step 4: Test with Generated MCP Server 🔧

**CRITICAL STEP**: Test the actual MCP tools implementation:

```bash
/project:generate-test-server
```

### Testing process:
1. Wait for the command to complete
2. Open **MCP Inspector** at http://localhost:6274
3. Open **Streamlit UI** at http://localhost:8501
4. Follow the testing guide at `./generated_servers/test_mcp_server/docs/MCP_INSPECTOR_GUIDE.md`

### Test each tool:
- Verify all 6 example tools work correctly
- Check error handling with invalid inputs
- Monitor logs in Streamlit UI
- Confirm decorators are functioning (logging, parallelization)

### Success criteria:
- ✅ All tools execute without errors
- ✅ Logs show proper decorator execution
- ✅ Error handling works as expected
- ✅ UI displays server status correctly

## Step 5: Complete the Issue 🎉

Once you're confident the implementation is successful:

```bash
/project:devflow/complete-issue
```

### This command will:
- Create a pull request with all changes
- Update JIRA issue status
- Generate PR description from commits
- Add implementation summary

### Your next steps:
1. Review the created PR on GitHub
2. **Notify your team** that you have a PR ready for review
3. Share PR link in Slack/Teams channel
4. Tag a teammate for code review
5. Address any review feedback with Claude's help

## Step 6: Post-Merge Cleanup 🧹

**IMPORTANT**: Only run this AFTER your PR has been merged into main branch by a reviewer.

```bash
/project:devflow/post-merge
```

### This handles:
- Switching to your local main branch
- Pulling latest changes from remote main (including your merged PR)
- Verifying your changes are included
- Deleting the feature branch
- Updating dependencies
- Running tests to ensure everything still works
- Preparing environment for next issue

## 💡 Pro Tips for Success

### DO:
- **Communicate clearly** - Be specific about what you want
- **Review frequently** - Check Claude's work as it progresses
- **Test thoroughly** - Use both automated tests and manual testing
- **Ask questions** - Have Claude explain complex code
- **Trust but verify** - Claude is powerful but benefits from guidance

### DON'T:
- **Skip testing** - Always verify with generate-test-server
- **Rush through** - Take time to understand the implementation
- **Ignore CI/CD** - Check that automated checks pass
- **Merge without review** - Always get peer review

## 🆘 Common Issues and Solutions

### Claude seems stuck or confused:
```
"Let's take a step back. Can you summarize what we're trying to achieve and where we are now?"
```

### Implementation doesn't match requirements:
```
"I notice this doesn't quite match the JIRA requirements. Specifically, we need to..."
```

### Tests are failing:
```
"Please analyze why these tests are failing and propose fixes"
```

### MCP server won't start:
```
"Check the logs at ./generated_servers/test_mcp_server/mcp_inspector.log"
```

## 📚 Quick Command Reference

1. **Start work**: `/project:devflow/fetch-issue ASEP-XX saaga`
2. **Test server**: `/project:generate-test-server`
3. **Complete work**: `/project:devflow/complete-issue`
4. **After merge**: `/project:devflow/post-merge`

## 🎯 Success Checklist

Before marking issue complete:
- [ ] JIRA requirements fully implemented
- [ ] Automated tests passing
- [ ] MCP test server validated all tools
- [ ] Code follows project conventions
- [ ] Documentation updated if needed

## 🚦 Ready to Start?

Your first JIRA issue is waiting! Run:
```bash
/project:devflow/fetch-issue [YOUR-ISSUE-KEY] saaga
```

Remember: Claude is your AI pair programmer. Guide it, verify its work, and together you'll deliver high-quality implementations efficiently.

Good luck! 🎉