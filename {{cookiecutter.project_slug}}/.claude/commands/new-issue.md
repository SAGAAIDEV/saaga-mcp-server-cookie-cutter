---
description: Create a new Jira issue by gathering details from the user and using Conduit
usage: /project:new-issue issue-type
example: /project:new-issue bug 

---

I'll help you create a new Jira issue in project $ARGUMENTS.

## Parse Arguments
Let me extract the project key and site alias from the provided arguments:
- Arguments provided: $ARGUMENTS
- Expected format: [PROJECT-KEY] default (e.g., "CLD saaga")

## Step 1: Gather Information from User

Before creating the issue, I need to gather some comprehensive information from you to ensure the issue is descriptive, actionable, and properly categorized.

Ask the user for:
- **Summary**: A clear, concise title (ask for clarification if too vague)
- **Description**: Detailed explanation of what needs to be done
- **Context**: Why is this needed? What problem does it solve?
- **Location**: Where in the codebase will this work happen?
- **Acceptance Criteria**: How will we know when it's complete?

## Step 2: Structure the Issue Description

Once I have the necessary information, I will use this template to structure the description:

```markdown
## Goal
[Clear statement of what needs to be achieved]

## Context
[Background information and why this is needed]

## Project Location
Directory: `[Full path to the relevant directory]`
Repository: [If applicable]

## Tasks
- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]
- [ ] Update documentation
- [ ] Add tests if applicable

## Acceptance Criteria
- [Specific measurable outcome 1]
- [Specific measurable outcome 2]
- [Configuration/documentation is updated]

## Additional Notes
[Any other relevant information]
```

## Step 3: Create the Issue

I will use the gathered information and the structured description to create the issue using Conduit or jira mcp server:

```python
# Use Conduit to create the issue
mcp__<conduit|jira>__create_jira_issue(
    project="{{cookiecutter.jira_project_key}}",
    summary="[Descriptive summary from user]",
    description="[Formatted description using template above]",
    issue_type="[issue-type from arguments]"
)
```



## Example Conversation Flow

**Assistant**: I'll help you create a Jira issue. Let me gather some information:

1. What's a brief summary of what needs to be done?
2. Can you provide more context about why this is needed?
3. Which directory or part of the codebase will this affect?
4. What should be the acceptance criteria?

**User**: We need to add authentication to the API

**Assistant**: Let me get more details to create a comprehensive issue:
- Which authentication method? (JWT, OAuth, API keys?)
- Which API endpoints need protection?
- Are there any existing authentication systems to integrate with?
- What's the directory path for the API code?

## Best Practices

### DO:
- Ask clarifying questions before creating the issue
- Include specific file paths and directories
- Break down work into checkable tasks
- Define clear acceptance criteria
- Add context about WHY this work is needed

### DON'T:
- Create vague issues like "Fix bugs" or "Improve performance"
- Skip the context section
- Forget to include the project location
- Create issues without acceptance criteria

## Complete Example

```python
# After gathering information from user:

# Step 1: Create the issue
response = mcp__<conduit|jira>__create_jira_issue(
    project="CLD",
    summary="Add JWT authentication to FastAPI backend",
    description="""## Goal
Implement JWT-based authentication for all API endpoints in the FastAPI backend.

## Context
Currently, the API endpoints are unprotected. We need to add authentication to secure user data and ensure only authorized users can access specific endpoints.

## Project Location
Directory: `/Users/andrew/saga/saaga/backend/src/api`
Main auth module: `/Users/andrew/saga/saaga/backend/src/auth`

## Tasks
- [ ] Create JWT token generation and validation utilities
- [ ] Add authentication middleware to FastAPI
- [ ] Protect existing endpoints with auth decorators
- [ ] Create login and refresh token endpoints
- [ ] Add user session management
- [ ] Update API documentation with auth requirements
- [ ] Add authentication tests

## Acceptance Criteria
- All API endpoints require valid JWT tokens (except login/register)
- Tokens expire after 24 hours with refresh capability
- Invalid tokens return 401 Unauthorized
- API documentation shows which endpoints require auth
- All auth flows have test coverage
- Configuration uses environment variables for secrets""",
    issue_type="Task"
)



print(f"Created issue {issue_key} and set status to ISSUE")
```

## Quick Reference

1. **Parse**: Extract PROJECT-KEY and SITE-ALIAS from arguments
2. **Gather**: Get detailed information from user (Summary, Description, Context, Location, Acceptance Criteria)
3. **Structure**: Use the template to format description
4. **Create**: Use `create_jira_issue` with gathered info
5. **Update**: Change status to "ISSUE" with `update_jira_status`
6. **Confirm**: Tell user the issue key and link