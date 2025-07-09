# MCP Server Cookie Cutter - Phase 1 & 2 JIRA Issues

## Phase 1: Core Template Structure

### ACT-150: Cookie Cutter Repository Setup and Basic Structure

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1

**Background & Goal:**
We need to create a new cookie cutter template that extends the existing Python MCP server cookie cutter with SAAGA decorator patterns. This issue focuses on setting up the repository structure and basic cookiecutter configuration.

**Goal:**
Create the foundational repository structure for the enhanced MCP server cookie cutter template with proper cookiecutter.json configuration and initial project scaffolding.

**Acceptance Criteria:**
1. Create new repository structure following cookiecutter conventions
2. Configure cookiecutter.json with all required variables:
   - project_name
   - project_slug (auto-generated from project_name)
   - include_admin_ui (yes/no)
   - include_example_tools (yes/no)
   - include_parallel_example (yes/no)
   - log_level (INFO/DEBUG/WARNING/ERROR)
   - log_retention_days (default: 30)
3. Set up hooks directory with pre_gen_project.py and post_gen_project.py placeholders
4. Create README.md for the cookie cutter itself (not the generated project)
5. Initialize git repository with appropriate .gitignore
6. Add LICENSE file (MIT or appropriate license)

**Technical Guidance:**
- Reference the existing cookie cutter structure from codingthefuturewithai/mcp-cookie-cutter
- Use Jinja2 templating syntax for variable substitution
- Ensure cookiecutter.json validates properly
- Follow cookiecutter best practices for directory naming (use {{cookiecutter.project_slug}} pattern)

---

### ACT-151: Base Template Directory Structure with Placeholders

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1

**Background & Goal:**
With the cookie cutter repository established, we need to create the complete directory structure for generated projects. This includes all directories and placeholder files that will be populated in later phases.

**Goal:**
Implement the complete directory structure template with appropriate placeholder files and conditional directory creation based on cookie cutter variables.

**Acceptance Criteria:**
1. Create main project directory structure:
   ```
   {{cookiecutter.project_slug}}/
   ├── {{cookiecutter.project_slug}}/
   │   ├── __init__.py
   │   ├── config.py
   │   ├── server/
   │   │   ├── __init__.py
   │   │   └── app.py
   │   ├── tools/
   │   │   └── __init__.py
   │   ├── decorators/
   │   │   ├── __init__.py
   │   │   ├── exceptions.py
   │   │   ├── logging.py
   │   │   └── parallelize.py
   │   └── {% if cookiecutter.include_admin_ui == 'yes' %}ui/{% endif %}
   │       ├── __init__.py
   │       ├── app.py
   │       ├── pages/
   │       │   └── __init__.py
   │       └── lib/
   │           └── __init__.py
   ├── tests/
   │   └── __init__.py
   ├── pyproject.toml
   ├── README.md
   └── .gitignore
   ```
2. Implement conditional directory creation for ui/ based on include_admin_ui
3. Add placeholder content to all Python files (docstrings explaining purpose)
4. Create pyproject.toml template with dynamic dependencies
5. Add comprehensive .gitignore for Python projects
6. Create README.md template with project name substitution

**Technical Guidance:**
- Use Jinja2 conditionals for optional directories: {% if cookiecutter.include_admin_ui == 'yes' %}
- Ensure all __init__.py files are created even if empty
- pyproject.toml should conditionally include streamlit dependency
- Use proper Python package structure conventions

---

### ACT-152: Core MCP Server Scaffolding Implementation

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1

**Background & Goal:**
Implement the core MCP server functionality using FastMCP, including the server initialization, dual transport support (stdio/SSE), and the framework for decorator application.

**Goal:**
Create a functional MCP server template that can be generated and run, with hooks in place for decorator integration in Phase 2.

**Acceptance Criteria:**
1. Implement server/app.py with:
   - FastMCP server initialization
   - Dual transport support (stdio and SSE)
   - Placeholder for decorator application function
   - Basic server metadata configuration
2. Create config.py with:
   - Platform-aware configuration paths using platformdirs
   - Log level configuration from cookie cutter variable
   - Shared configuration class for server and UI
3. Implement basic example tool in tools/ directory (if include_example_tools == 'yes')
4. Add proper logging setup using Python logging module
5. Create run instructions in generated README.md
6. Ensure server can be launched via MCP client configuration

**Technical Guidance:**
- Reference FastMCP patterns from existing cookie cutter
- Use platformdirs for cross-platform configuration paths
- Server should work with minimal configuration out of the box
- Include proper error handling for missing dependencies
- Structure code to easily add decorator application in Phase 2

---

## Phase 2: Decorator Integration

### ACT-153: Extract and Adapt SAAGA Decorators

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2

**Background & Goal:**
Extract the working decorator implementations from SAAGA base POC and adapt them for the cookie cutter template. This includes exception handling, logging, and parallelization decorators.

**Goal:**
Port and enhance the SAAGA decorator patterns into reusable, well-documented decorators that can be automatically applied to MCP tools.

**Acceptance Criteria:**
1. Implement decorators/exceptions.py:
   - exception_handler decorator with proper error formatting
   - Configurable error response format
   - Integration with logging system
2. Implement decorators/logging.py:
   - tool_logger decorator with timing functionality
   - SQLite database logging with thread-safe connections
   - Log entry schema: timestamp, tool_name, duration_ms, status, input_args, output_summary, error_message
3. Implement decorators/parallelize.py:
   - Async wrapper for synchronous functions
   - Thread pool executor management
   - Proper cleanup on shutdown
4. Add comprehensive docstrings and type hints
5. Create decorator tests in tests/test_decorators.py
6. Ensure decorators can be chained in correct order

**Technical Guidance:**
- Reference implementation from SAGAAIDEV/saaga-mcp-servers/base
- Use functools.wraps to preserve function metadata
- Implement thread-safe SQLite connections using threading.local()
- Consider using asyncio.run_in_executor for parallelization
- Ensure decorators work with FastMCP tool registration

---

### ACT-154: Implement Auto-Decorator Application Pattern

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2

**Background & Goal:**
Create the automatic decorator application system that wraps MCP tools with appropriate decorators based on configuration. This removes the need for manual decorator application on each tool.

**Goal:**
Implement a clean pattern for automatically applying decorators to tools during server initialization, with support for different decorator chains for regular vs parallel tools.

**Acceptance Criteria:**
1. Create create_decorated_server function in server/app.py:
   - Accept lists of regular tools and parallel tools
   - Apply decorator chain: exception_handler → tool_logger for regular tools
   - Apply decorator chain: exception_handler → tool_logger → parallelize for parallel tools
2. Implement tool discovery mechanism:
   - Auto-import tools from tools/ directory
   - Support for marking tools as parallel via naming convention or configuration
3. Update server initialization to use decorated tools
4. Add configuration for enabling/disabling specific decorators
5. Create example parallel tool if include_parallel_example == 'yes'
6. Document the decorator application pattern in code comments

**Technical Guidance:**
- Use importlib for dynamic tool discovery
- Consider using a decorator or class attribute to mark parallel tools
- Ensure proper error handling if decorators fail to apply
- Make the system extensible for future decorators
- Test with both synchronous and asynchronous tool implementations

---

### ACT-155: SQLite Logging Schema and Infrastructure

**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2

**Background & Goal:**
Implement the SQLite-based logging infrastructure that captures tool execution data, including proper schema design, rotation policies, and query interfaces for the admin UI.

**Goal:**
Create a robust, thread-safe SQLite logging system that can handle high-volume tool logging with appropriate retention policies and query capabilities.

**Acceptance Criteria:**
1. Design and implement SQLite schema:
   ```sql
   CREATE TABLE tool_logs (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
       tool_name TEXT NOT NULL,
       duration_ms INTEGER,
       status TEXT CHECK(status IN ('success', 'error')),
       input_args TEXT,  -- JSON
       output_summary TEXT,
       error_message TEXT,
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   CREATE INDEX idx_timestamp ON tool_logs(timestamp);
   CREATE INDEX idx_tool_name ON tool_logs(tool_name);
   CREATE INDEX idx_status ON tool_logs(status);
   ```
2. Implement log rotation based on log_retention_days setting
3. Create thread-safe database connection management
4. Add utility functions for querying logs:
   - get_logs_by_date_range()
   - get_logs_by_tool()
   - get_error_logs()
   - export_logs_to_csv()
5. Store database in platform-specific data directory
6. Implement automatic database initialization on first use

**Technical Guidance:**
- Use platformdirs to determine appropriate data directory
- Implement connection pooling with thread-local storage
- Use context managers for database transactions
- Consider using SQLite's WAL mode for better concurrency
- Add database migration support for future schema changes
- Include vacuum/analyze operations in rotation logic