---
description: Create a detailed JIRA issue (Executable Spec or Bug) by analyzing the codebase and structuring the issue according to team standards
argument-hint: "[TYPE] [SITE-ALIAS] '[TITLE]' '[BRIEF-DESCRIPTION]'"
allowed-tools: ["Bash", "Read", "Grep", "Glob", "LS", "mcp__Conduit__create_jira_issue", "mcp__mcp_jira__create_jira_issue"]
---

I'll help you create a detailed JIRA issue by analyzing the codebase and structuring it according to team standards. Let me parse your request and gather the necessary information.

## Parse Arguments
Let me extract the issue details from your request:
- Arguments provided: $ARGUMENTS
- Expected format: [TYPE] [SITE-ALIAS] "[TITLE]" "[BRIEF-DESCRIPTION]"

**Accepted TYPE values:**
- For new features: `feature`, `spec`, `executable-spec`, `story`
- For bugs: `bug`, `defect`, `fix`

All feature-related types will create an **Executable Spec** in JIRA.
All bug-related types will create a **Bug** in JIRA.

## Step 1: Analyze Codebase Context

Based on the issue type and description, I'll analyze the codebase to gather relevant context:

### For Executable Specs:
1. **Search for Related Implementations**
   - Check if similar features exist
   - Identify integration points
   - Find relevant patterns to follow
   - Locate appropriate directories for new code

2. **Analyze Architecture**
   - Understand current system design
   - Identify affected components
   - Check for conflicting implementations
   - Review configuration structures

### For Bugs:
1. **Investigate Symptoms**
   - Search for error patterns in code
   - Find related log statements
   - Identify affected components
   - Check recent changes that might have introduced the issue

2. **Reproduce Understanding**
   - Analyze code flow where bug occurs
   - Identify root cause possibilities
   - Find related test cases
   - Check for similar fixed issues

## Step 2: Gather Additional Information

I'll ask you a few clarifying questions based on what I find:

### For Executable Specs:
- What problem does this feature solve?
- Who are the primary users/consumers?
- Are there any performance or scalability requirements?
- Should this be configurable? If so, how?
- Any specific acceptance criteria you already have in mind?

### For Bugs:
- When did this issue first appear?
- What are the exact steps to reproduce?
- What is the expected behavior vs actual behavior?
- How critical is this issue (blocking production, affecting users, etc.)?
- Any error messages or stack traces?

## Step 3: Structure the JIRA Issue

Based on my analysis and your input, I'll create a properly structured issue.

**Issue Type Mapping:**
- If you specified: `feature`, `spec`, `executable-spec`, or `story` → Creates **Executable Spec**
- If you specified: `bug`, `defect`, or `fix` → Creates **Bug**

### For Executable Spec:

**Title**: [Clear action verb] + [Specific feature/component] + [Key technical aspects]

**Description Structure**:
1. **Background/Goal**
   - Current state analysis from codebase
   - Problem this solves
   - Ultimate goal
   - Future extensibility considerations

2. **Acceptance Criteria**
   - Numbered list of specific, testable requirements
   - Functional requirements
   - Technical requirements
   - Performance requirements (if applicable)
   - Backward compatibility requirements
   - Configuration requirements

3. **Technical Guidance**
   - Implementation approach
   - File structure and locations
   - Key classes/interfaces to create
   - Integration points with existing code
   - Code examples where helpful
   - Configuration schema changes

4. **Testing Checklist**
   - Unit test requirements
   - Integration test requirements
   - Manual testing scenarios

5. **Additional Considerations**
   - Migration requirements
   - Documentation updates needed
   - Security considerations

### For Bug:

**Title**: Fix + [Specific issue] + [Affected component/area]

**Description Structure**:
1. **Problem Statement**
   - Clear description of the issue
   - Impact on users/developers
   - Scope of affected areas

2. **Issues Identified**
   - Numbered list of specific problems found
   - Current behavior vs expected behavior
   - Code references where issue occurs
   - Root cause analysis

3. **Reproduction Steps**
   - Step-by-step guide to reproduce
   - Environment/configuration needed
   - Expected vs actual results

4. **Acceptance Criteria**
   - Specific fixes required
   - Validation steps
   - Regression test requirements

5. **Technical Notes**
   - Why this is happening (based on code analysis)
   - Proposed solution approach
   - Any risks or side effects

6. **Impact**
   - Who/what is affected
   - Severity and urgency
   - Workarounds (if any)

## Step 4: Review and Refine

I'll present the complete issue structure for your review. You can:

1. **Review** the entire issue content
2. **Request changes** to any section
3. **Add missing information** I might have overlooked
4. **Adjust** priority, acceptance criteria, or technical approach

**Important**: I will NOT create the issue automatically. Once you're satisfied with the content, you can:
- Copy the content to create the issue manually in JIRA
- Ask me to create it using the MCP JIRA server
- Save it for later refinement

This ensures the issue meets your standards before it enters your backlog.

## Step 5: Next Steps

After creation, I'll provide:
- The JIRA issue key and URL
- Suggested branch name for when work begins
- Any immediate codebase references to bookmark
- Related issues that might be relevant

---

## 💡 Tips for Best Results

**For Executable Specs:**
- Be specific about the problem you're solving
- Think about configuration early
- Consider how this fits with existing patterns
- Include performance requirements upfront

**For Bugs:**
- Provide specific examples or error messages
- Include any patterns you've noticed
- Mention when this started happening
- Rate the severity honestly

**General:**
- The more context you provide, the better the AI can analyze the codebase
- Reference existing code or patterns you want to follow/avoid
- Mention any deadlines or dependencies
- Include any design decisions already made

Ready to create your JIRA issue! Please provide the issue type, site alias, title, and brief description to get started.