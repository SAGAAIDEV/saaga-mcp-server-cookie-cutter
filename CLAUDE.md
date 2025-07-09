# Claude Session Context - SAAGA MCP Server Cookie Cutter

## Project Overview

Creating an enhanced MCP (Model Context Protocol) server cookie cutter template that combines:
1. The existing Python MCP server cookie cutter structure
2. SAAGA decorator patterns (exception handling, logging, parallelization)
3. Optional Streamlit administrative UI
4. SQLite-based logging system

## CURRENT STATUS - PHASE 1 COMPLETE ✅

### ✅ COMPLETED: ASEP-14 - Cookie Cutter Repository Setup and Basic Structure
**Status**: FULLY IMPLEMENTED AND TESTED
**Branch**: `feature/ASEP-14-cookie-cutter-repository-setup`
**JIRA**: In Progress → Ready for completion

#### What Was Delivered:
1. **Complete Repository Structure**:
   - Root files: .gitignore, LICENSE, README.md, CONTRIBUTING.md
   - cookiecutter.json with all required variables
   - requirements.txt with development dependencies
   - .pre-commit-config.yaml for code quality
   - GitHub Actions workflow for testing

2. **Template Directory Structure**:
   ```
   {{cookiecutter.project_slug}}/
   ├── {{cookiecutter.project_slug}}/
   │   ├── server/          # FastMCP server location
   │   ├── tools/           # MCP tools
   │   ├── decorators/      # SAAGA decorators
   │   └── ui/              # Optional Streamlit UI
   ├── tests/
   ├── docs/
   ├── pyproject.toml       # With conditional dependencies
   └── README.md
   ```

3. **Configuration Variables** (cookiecutter.json):
   - project_name, project_slug, description, author info
   - python_version: ["3.11", "3.12"]
   - include_admin_ui: ["no", "yes"]
   - include_example_tools: ["yes", "no"]
   - include_parallel_example: ["yes", "no"]
   - log_level: ["INFO", "DEBUG", "WARNING", "ERROR"]
   - log_retention_days: "30"

4. **Testing Results**:
   - ✅ Template generates successfully
   - ✅ Conditional dependencies work correctly
   - ✅ All required files/directories created
   - ✅ Proper variable substitution

## NEXT STEPS - PHASE 2

### 🎯 NEXT ISSUE: ASEP-15 - Core MCP Server Scaffolding Implementation
**Status**: Ready to start
**Priority**: High
**Dependencies**: ASEP-14 (Complete)

#### Acceptance Criteria for ASEP-15:
1. **Implement server/app.py** with:
   - FastMCP server initialization
   - Dual transport support (stdio and SSE)
   - Placeholder for decorator application function
   - Basic server metadata configuration

2. **Create config.py** with:
   - Platform-aware configuration paths using platformdirs
   - Log level configuration from cookie cutter variable
   - Shared configuration class for server and UI

3. **Implement basic example tool** in tools/ directory (if include_example_tools == 'yes')

4. **Add proper logging setup** using Python logging module

5. **Create run instructions** in generated README.md

6. **Ensure server can be launched** via MCP client configuration

## Architecture Summary

### Directory Structure (Current)
```
saaga-mcp-server-cookie-cutter/
├── cookiecutter.json                    # ✅ Complete
├── {{cookiecutter.project_slug}}/       # ✅ Complete structure
├── README.md                            # ✅ Complete
├── CONTRIBUTING.md                      # ✅ Complete
├── LICENSE                              # ✅ Complete
├── requirements.txt                     # ✅ Complete
├── .pre-commit-config.yaml             # ✅ Complete
├── .github/workflows/test.yml           # ✅ Complete
└── .gitignore                          # ✅ Complete
```

### Key Insights from Repository Analysis

#### Current Cookie Cutter (codingthefuturewithai/mcp-cookie-cutter)
- Clean, well-structured template
- Dual transport support (stdio/SSE)
- Good logging setup with platformdirs
- No decorator functionality

#### SAAGA Base POC (SAGAAIDEV/saaga-mcp-servers)
- Working decorator implementations
- SQLite logging system
- **Problem**: Exposes admin tools as MCP functions (read_logs, etc.)
- Shows successful decorator chaining pattern

#### MCP JIRA Example (codingthefuturewithai/mcp_jira)
- Demonstrates Streamlit UI integration pattern
- UI runs separately, manages config via file system
- Platform-aware configuration paths
- Good separation of concerns

## Implementation Strategy for ASEP-15

1. **Phase 1**: Create server/app.py with FastMCP and dual transport
2. **Phase 2**: Implement config.py with platform-aware paths
3. **Phase 3**: Add example tools (conditional)
4. **Phase 4**: Set up logging integration
5. **Phase 5**: Update README with run instructions
6. **Phase 6**: Test MCP client integration

## Technical Details to Remember

### Decorator Application Pattern (for future phases)
```python
def create_decorated_server(name, tools, parallel_tools):
    server = FastMCP(name)
    
    # Regular tools: exception_handler → tool_logger
    for func in tools:
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        server.tool()(decorated)
    
    # Parallel tools: exception_handler → tool_logger → parallelize
    for func in parallel_tools:
        decorated = exception_handler(func)
        decorated = tool_logger(decorated)
        decorated = parallelize(decorated)
        server.tool()(decorated)
    
    return server
```

### Configuration Management
- YAML-based configuration files
- Platform-specific paths (macOS: ~/Library/Application Support/...)
- Shared between server and UI
- Server must restart to pick up changes

### Logging System (for future phases)
- SQLite database with thread-safe connections
- Tracks: timestamp, tool_name, duration_ms, status, input_args, output_summary, error_message
- Located at platform-specific data directory via platformdirs

## Important References

- Current cookie cutter: https://github.com/codingthefuturewithai/mcp-cookie-cutter.git
- SAAGA base with decorators: https://github.com/SAGAAIDEV/saaga-mcp-servers/tree/main/src/saaga_mcp_servers/base
- MCP JIRA with Streamlit UI: https://github.com/codingthefuturewithai/mcp_jira.git
- FastMCP documentation: Context7 /jlowin/fastmcp

## Ready to Resume Work

**When resuming, run**: `/start-feature ASEP-15 saaga`

This will:
1. Fetch ASEP-15 from JIRA
2. Create feature branch: `feature/ASEP-15-core-mcp-server-scaffolding`
3. Update JIRA to "In Progress"
4. Present implementation plan for approval
5. Begin Phase 2 implementation

**Site alias**: `saaga` (for JIRA operations)
**Current branch**: `feature/ASEP-14-cookie-cutter-repository-setup` (ready for completion)

---

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.