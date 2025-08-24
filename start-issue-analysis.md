# Start-Issue Command Analysis: Applying Prompt Engineering Insights

## Current Issues (Aligned with Article's Warnings)

### 1. Long-tail Probability Problem
The command demands complex, sequential reasoning (Steps 1-8) in a single prompt. As the author notes, LLMs generate what's *likely*, not what's *reasonable*. This 138-line command is asking for very specific, unlikely behaviors all at once.

### 2. Signal-to-Noise Ratio
The command mixes multiple concerns:
- JIRA operations
- Git branching
- Codebase analysis
- Technical research
- Testing strategy
- Implementation planning

This creates noise and conflicting instruction vectors.

### 3. Missing Anchoring
The command jumps straight into complex instructions without letting the model establish a baseline understanding first.

## Recommended Approach Using Article's Strategies

### 1. Decompose into Atomic Commands
Break this into smaller, composable commands:

```
/project:fetch-issue [ISSUE-KEY] [SITE]     # Just fetch and summarize
/project:analyze-feasibility                 # Check if already implemented
/project:create-branch                       # Create appropriate branch
/project:plan-implementation                 # Generate implementation plan
```

### 2. Use Anchoring + Nudging Pattern
Instead of front-loading all logic, let the model generate baseline understanding first:

```markdown
---
description: Fetch and understand a JIRA issue
---

First, fetch JIRA issue $ARGUMENTS and provide a summary.

After you've understood the issue, I'll guide you through:
- Checking if it's already implemented
- Creating an appropriate branch
- Planning the implementation
```

### 3. Shift Probability Distributions Incrementally
Rather than one complex command, use a conversation flow:

```markdown
---
description: Start JIRA issue - Phase 1: Understanding
---

Fetch JIRA issue $ARGUMENTS and answer:
1. What is the issue asking for?
2. What are the acceptance criteria?
3. What type of issue is this?

Stop here and wait for confirmation.
```

### 4. Simplify Decision Trees
Move complex conditionals out of the prompt:

**Current (Noisy):**
```
If Fully Implemented: Stop and report...
If Partially Implemented: Document what exists...
If Conflicts Detected: Highlight concerns...
```

**Better (Clear Signal):**
```
After analyzing the codebase, report what you found.
I'll decide the next step based on your findings.
```

## Proposed Revised Command Structure

```markdown
---
description: Fetch and analyze JIRA issue
argument-hint: "[ISSUE-KEY] [SITE-ALIAS]"
---

## Phase 1: Fetch and Understand
Fetch JIRA issue $ARGUMENTS and provide:
- Issue type and summary
- Key requirements
- Acceptance criteria

## Phase 2: Codebase Check
Search for existing implementations of these requirements.
Report what you find.

[User reviews and decides whether to proceed]

## Phase 3: Implementation
Based on our analysis, I'll guide you through:
- Branch creation
- Status update
- Implementation planning
```

## Key Improvements

1. **Reduced Cognitive Load**: Each phase has a clear, limited scope
2. **Natural Probability Flow**: Commands align with what LLMs naturally generate well
3. **Human-in-the-Loop**: Critical decisions aren't delegated to probability
4. **Composable**: Can reuse phases in different combinations
5. **Clear Signal**: Each instruction has a single, clear intent vector

## Core Principle Applied

The author's key insight - "guide probabilities, don't demand miracles" - suggests breaking your ambitious command into smaller, more probable chunks that build on each other naturally. Instead of a single 138-line command that fights against the model's probability distributions, we create a series of focused commands that work *with* the model's natural tendencies.