---
description: Research and create implementation plan ONLY - does NOT implement code
argument-hint: ""
allowed-tools: ["mcp__context7__resolve-library-id", "mcp__context7__get-library-docs", "WebSearch", "Read", "ExitPlanMode"]
---

## Plan Implementation - Template Development

⚠️ **CRITICAL COMMAND BOUNDARY** ⚠️
- This command MUST ONLY create plans
- This command MUST NOT write any code
- This command MUST NOT implement anything
- This command MUST NOT use Write, Edit, or MultiEdit tools
- Even if the user says "approved" or "looks good", DO NOT IMPLEMENT

I'll create a detailed implementation plan for modifying the cookie cutter template based on the JIRA issue requirements.

## Grounding References - Template Maintenance
- **Template Patterns**: `.reference/cookiecutter-maintenance.md` - How to modify the template
- **Critical Files**: `.reference/critical-files.md` - What not to break
- **Evolution**: `.reference/template-evolution.md` - Version and breaking change guidelines

## Grounding References - Understanding Generated Code
- **MCP Patterns**: `{{cookiecutter.project_slug}}/.reference/patterns/tool_patterns.py` - What tools should look like
- **Testing Patterns**: `{{cookiecutter.project_slug}}/.reference/patterns/integration_test_patterns.py` - How tests work
- **SAAGA Integration**: `{{cookiecutter.project_slug}}/.reference/saaga-mcp-integration.md` - Decorator requirements
- **Templates**: `{{cookiecutter.project_slug}}/.reference/templates/` - Code generation templates

### Step 1: Technical Research
If the issue mentions unfamiliar technologies:
- Use Context7 for library/framework documentation
- Research best practices for the specific technology
- Note any special setup requirements

### Step 2: Identify Components
Based on requirements and existing code:
- Files to modify
- New files to create (following `.reference/patterns/`)
- Integration points with existing code

### Step 3: Define Testing Strategy
Determine the appropriate testing approach:
- **UI Testing**: For user interfaces and visual elements
- **API/MCP Testing**: For endpoints and tools (see `.reference/patterns/integration_test_patterns.py`)
- **Integration Testing**: For system components
- **Unit Testing**: For isolated functions (see `.reference/patterns/unit_test_patterns.py`)

### Step 4: Create Implementation Plan
Present a structured plan with:
1. Overview of approach
2. Implementation order
3. Components to build/modify (with pattern references)
4. Testing strategy (grounded in test patterns)
5. Risk factors or dependencies

**Key Patterns to Follow**:
- All tools must be async with `ctx: Context = None` parameter
- Decorator chain: type_converter → tool_logger → exception_handler
- Use templates from `.reference/templates/` for new components

### Step 5: Present Plan and STOP COMPLETELY
I'll use ExitPlanMode to present the complete plan for your review.

**THEN I MUST STOP. NO FURTHER ACTION.**

---

## 🛑 FULL STOP - Plan Presented

**THIS COMMAND ENDS HERE. I WILL NOT IMPLEMENT ANYTHING.**

After the plan is presented:
1. **You review the plan** 
2. **You decide** what to do next

## 🔄 What YOU Must Do Next

**To implement the plan**, YOU must explicitly run:
```
/project:devflow/implement-plan
```

**To revise the plan**:
- Tell me what needs to be different
- I'll revise the plan (still no implementation)
- We stay in planning mode only

**CRITICAL RULES**:
- Even if you say "approved" → I MUST NOT implement
- Even if you say "looks good" → I MUST NOT implement  
- Even if you say "go ahead" → I MUST NOT implement
- ONLY the command `/project:devflow/implement-plan` can trigger implementation

**No code will be written by this command under ANY circumstances.**