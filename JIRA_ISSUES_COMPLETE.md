# MCP Server Cookie Cutter with SAAGA Decorators - Complete JIRA Issues

## Project Overview

This document contains all JIRA issues for the MCP Server Cookie Cutter project that integrates SAAGA decorator patterns. The project creates an enhanced cookie cutter template for MCP servers with automatic decorator application, optional Streamlit administrative UI, and SQLite-based logging system.

## Issue Summary Table

| Phase | Title | Labels | Dependencies |
|-------|-------|--------|-------------|
| 1 | Cookie Cutter Repository Setup and Basic Structure | mcp, cookie-cutter, saaga-decorators, phase-1 | None |
| 1 | Base Template Directory Structure with Placeholders | mcp, cookie-cutter, saaga-decorators, phase-1 | Cookie Cutter Repository Setup |
| 1 | Core MCP Server Scaffolding Implementation | mcp, cookie-cutter, saaga-decorators, phase-1 | Base Template Directory Structure |
| 2 | Extract and Adapt SAAGA Decorators | mcp, cookie-cutter, saaga-decorators, phase-2 | Core MCP Server Scaffolding |
| 2 | Implement Auto-Decorator Application Pattern | mcp, cookie-cutter, saaga-decorators, phase-2 | Extract and Adapt SAAGA Decorators |
| 2 | SQLite Logging Schema and Infrastructure | mcp, cookie-cutter, saaga-decorators, phase-2 | Extract and Adapt SAAGA Decorators |
| 3 | Platform-Aware Configuration Management | mcp, cookie-cutter | Core MCP Server Scaffolding |
| 3 | Shared Configuration Module Implementation | mcp, cookie-cutter | Platform-Aware Configuration Management |
| 3 | Configuration Template and Validation | mcp, cookie-cutter | Shared Configuration Module |
| 4 | Streamlit Admin UI Base Structure | mcp, cookie-cutter, streamlit-ui | Shared Configuration Module, SQLite Logging Schema |
| 4 | Configuration Editor Page Implementation | mcp, cookie-cutter, streamlit-ui | Streamlit Admin UI Base Structure |
| 4 | SQLite Log Viewer with Filtering and Export | mcp, cookie-cutter, streamlit-ui | Streamlit Admin UI Base Structure |
| 5 | README and Documentation Templates | mcp, cookie-cutter, documentation | All Phase 1-4 issues |
| 5 | Example Tools and Usage Patterns | mcp, cookie-cutter, documentation | Auto-Decorator Application Pattern |
| 5 | Developer Guide and Troubleshooting | mcp, cookie-cutter, documentation | All Phase 1-4 issues |
| 6 | Cookie Cutter Template Testing Framework | mcp, cookie-cutter, testing | All Phase 1-5 issues |
| 6 | Cross-Platform Compatibility Testing | mcp, cookie-cutter, testing | Cookie Cutter Template Testing Framework |
| 6 | End-to-End Validation and Release Preparation | mcp, cookie-cutter, testing | Cross-Platform Compatibility Testing |

## Issue Interdependencies

### Dependency Flow Diagram

```
Phase 1: Core Template Structure
├── Cookie Cutter Repository Setup (no dependencies)
├── Base Template Directory Structure (depends on Repository Setup)
└── Core MCP Server Scaffolding (depends on Directory Structure)

Phase 2: Decorator Integration
├── Extract and Adapt SAAGA Decorators (depends on Core MCP Server Scaffolding)
├── Auto-Decorator Application Pattern (depends on Extract SAAGA Decorators)
└── SQLite Logging Schema (depends on Extract SAAGA Decorators)

Phase 3: Configuration System
├── Platform-Aware Configuration (depends on Core MCP Server Scaffolding)
├── Shared Configuration Module (depends on Platform-Aware Configuration)
└── Configuration Template (depends on Shared Configuration Module)

Phase 4: Admin UI (optional features)
├── Streamlit UI Base Structure (depends on Shared Config Module + SQLite Logging)
├── Configuration Editor Page (depends on Streamlit UI Base)
└── SQLite Log Viewer (depends on Streamlit UI Base)

Phase 5: Documentation
├── README and Documentation Templates (depends on ALL Phase 1-4 issues)
├── Example Tools and Usage Patterns (depends on Auto-Decorator Application)
└── Developer Guide (depends on ALL Phase 1-4 issues)

Phase 6: Testing & Release
├── Template Testing Framework (depends on ALL Phase 1-5 issues)
├── Cross-Platform Testing (depends on Template Testing Framework)
└── End-to-End Validation (depends on Cross-Platform Testing)
```

### Critical Path Dependencies

1. **Sequential Dependencies Within Phases:**
   - Phase 1 issues must be completed in order (1 → 2 → 3)
   - Phase 2: Decorators must be extracted before application pattern
   - Phase 3: Configuration builds sequentially (platform → shared → template)
   - Phase 6: Testing builds on previous testing (framework → cross-platform → E2E)

2. **Cross-Phase Dependencies:**
   - Phase 2 cannot start until Phase 1 Issue 3 (Core MCP Server) is complete
   - Phase 3 can start after Phase 1 Issue 3, parallel to Phase 2
   - Phase 4 requires both Configuration (Phase 3) and Logging (Phase 2)
   - Phase 5 documentation requires all implementation phases (1-4) complete
   - Phase 6 testing requires all other phases complete

3. **Parallel Work Opportunities:**
   - Phase 2 and Phase 3 can proceed in parallel after Phase 1
   - Within Phase 2: SQLite Logging can be developed parallel to Auto-Decorator Pattern
   - Within Phase 4: Config Editor and Log Viewer can be developed in parallel
   - Within Phase 5: Example Tools can start once decorators are ready

---

## Phase 1: Core Template Structure

### Phase 1, Issue 1: Cookie Cutter Repository Setup and Basic Structure

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1
**Dependencies:** None (Starting point)

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
- Cookiecutter Documentation References:
  - Tutorial Create from Scratch: https://cookiecutter.readthedocs.io/en/stable/tutorials/tutorial2.html
  - Choice Variables: https://cookiecutter.readthedocs.io/en/stable/advanced/choice_variables.html
  - Boolean Variables: https://cookiecutter.readthedocs.io/en/stable/advanced/boolean_variables.html

---

### Phase 1, Issue 2: Base Template Directory Structure with Placeholders

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1
**Dependencies:** Phase 1, Issue 1 (Cookie Cutter Repository Setup)

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
- Cookiecutter Documentation References:
  - Copy without Render: https://cookiecutter.readthedocs.io/en/stable/advanced/copy_without_render.html
  - Hooks: https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html

---

### Phase 1, Issue 3: Core MCP Server Scaffolding Implementation

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-1
**Dependencies:** Phase 1, Issue 2 (Base Template Directory Structure)

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
- Cookiecutter Documentation References:
  - Hooks: https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html

---

## Phase 2: Decorator Integration

### Phase 2, Issue 1: Extract and Adapt SAAGA Decorators

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2
**Dependencies:** Phase 1, Issue 3 (Core MCP Server Scaffolding)

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
- Cookiecutter Documentation References:
  - Hooks: https://cookiecutter.readthedocs.io/en/stable/advanced/hooks.html

---

### Phase 2, Issue 2: Implement Auto-Decorator Application Pattern

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2
**Dependencies:** Phase 2, Issue 1 (Extract and Adapt SAAGA Decorators)

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

### Phase 2, Issue 3: SQLite Logging Schema and Infrastructure

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, saaga-decorators, phase-2
**Dependencies:** Phase 2, Issue 1 (Extract and Adapt SAAGA Decorators)

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

---

## Phase 3: Configuration System

### Phase 3, Issue 1: Platform-Aware Configuration Management

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter
**Dependencies:** Phase 1, Issue 3 (Core MCP Server Scaffolding)  

**Background & Goal:**
The MCP Server Cookie Cutter needs a robust configuration management system that respects platform-specific conventions for configuration file locations. This system must work across Windows, macOS, and Linux, using the appropriate directories for each platform (e.g., ~/Library/Application Support on macOS, %APPDATA% on Windows, ~/.config on Linux).

**Goal:** Implement a platform-aware configuration management module that handles configuration file creation, loading, and updating using platformdirs for cross-platform compatibility.

**Acceptance Criteria:**
1. Create a configuration module that uses platformdirs to determine appropriate config locations
2. Implement functions for:
   - Getting the configuration directory path
   - Creating configuration directory if it doesn't exist
   - Loading configuration from YAML files
   - Saving configuration to YAML files
3. Handle missing configuration files gracefully with sensible defaults
4. Support both server and UI configuration needs
5. Include proper error handling for file system operations
6. Add logging for configuration operations
7. Ensure thread-safe configuration access

**Technical Guidance:**
- Use platformdirs library for cross-platform directory resolution
- Store configuration in YAML format for human readability
- Configuration path pattern: `<platform_config_dir>/<project_slug>/config.yaml`
- Implement a ConfigManager class with methods like:
  - `get_config_path()`: Returns platform-specific config file path
  - `load_config()`: Loads configuration with defaults fallback
  - `save_config()`: Saves configuration with validation
  - `ensure_config_dir()`: Creates config directory if needed
- Use file locking for concurrent access safety
- Example structure:
```python
from platformdirs import user_config_dir
import yaml
import os
from pathlib import Path

class ConfigManager:
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.config_dir = Path(user_config_dir(app_name))
        self.config_file = self.config_dir / "config.yaml"
```

---

### Phase 3, Issue 2: Shared Configuration Module Implementation

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter
**Dependencies:** Phase 3, Issue 1 (Platform-Aware Configuration Management)  

**Background & Goal:**
The configuration system needs to be shared between the MCP server and the optional Streamlit admin UI. This requires a well-structured configuration module that defines the configuration schema, provides validation, and handles updates from both the server runtime and the UI.

**Goal:** Implement a shared configuration module with a defined schema, validation, and update mechanisms that can be used by both the MCP server and Streamlit UI.

**Acceptance Criteria:**
1. Define a configuration schema using Pydantic or dataclasses
2. Implement configuration validation with helpful error messages
3. Create methods for updating individual configuration values
4. Support configuration versioning for future migrations
5. Implement configuration merge logic for partial updates
6. Add configuration change detection for server restart notifications
7. Include example configuration values in the cookie cutter template
8. Document all configuration options

**Technical Guidance:**
- Define configuration schema in `{{cookiecutter.project_slug}}/config.py`
- Use Pydantic for validation and serialization
- Cookiecutter Documentation References:
  - Dictionary Variables: https://cookiecutter.readthedocs.io/en/stable/advanced/dict_variables.html
  - Choice Variables: https://cookiecutter.readthedocs.io/en/stable/advanced/choice_variables.html
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class ServerConfig(BaseModel):
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR)$")
    log_retention_days: int = Field(default=30, ge=1, le=365)
    parallel_max_workers: Optional[int] = Field(default=None, ge=1, le=10)
    
class ToolConfig(BaseModel):
    enabled_tools: List[str] = Field(default_factory=list)
    tool_timeout_seconds: int = Field(default=300, ge=1)
    
class Config(BaseModel):
    version: int = 1
    server: ServerConfig = Field(default_factory=ServerConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
```
- Implement configuration loading with migration support
- Add methods for partial updates that preserve existing values
- Include configuration validation in both server startup and UI saves

---

### Phase 3, Issue 3: Configuration Template and Validation

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter
**Dependencies:** Phase 3, Issue 2 (Shared Configuration Module)  

**Background & Goal:**
The cookie cutter template needs to generate appropriate default configuration files based on user choices during project creation. This includes creating initial configuration files with sensible defaults and providing validation utilities to ensure configuration integrity.

**Goal:** Create configuration templates for the cookie cutter that generate appropriate default configurations based on user choices, with comprehensive validation utilities.

**Acceptance Criteria:**
1. Create Jinja2 templates for initial configuration files
2. Generate different defaults based on cookie cutter variables
3. Implement configuration validation utilities
4. Add configuration health check functionality
5. Create example configurations for common use cases
6. Include configuration documentation in generated README
7. Add configuration migration utilities for future updates
8. Implement configuration backup before updates

**Technical Guidance:**
- Create template at `{{cookiecutter.project_slug}}/config.yaml.j2`
- Cookiecutter Documentation References:
  - Boolean Variables: https://cookiecutter.readthedocs.io/en/stable/advanced/boolean_variables.html
```yaml
version: 1
server:
  log_level: "{{ cookiecutter.log_level }}"
  log_retention_days: {{ cookiecutter.log_retention_days }}
  {% if cookiecutter.include_parallel_example == 'yes' %}
  parallel_max_workers: 4
  {% endif %}
tools:
  enabled_tools: []
  tool_timeout_seconds: 300
```
- Add validation utility functions:
  - `validate_config_file(path)`: Validates configuration file structure
  - `check_config_compatibility(config)`: Checks version compatibility
  - `migrate_config(old_config)`: Migrates old config to new format
- Include pre-commit hook for configuration validation
- Generate configuration documentation from schema

---

## Phase 4: Admin UI

### Phase 4, Issue 1: Streamlit Admin UI Base Structure

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, streamlit-ui
**Dependencies:** 
- Phase 3, Issue 2 (Shared Configuration Module)
- Phase 2, Issue 3 (SQLite Logging Schema)  

**Background & Goal:**
The optional Streamlit admin UI provides a web-based interface for managing MCP server configuration and viewing logs. This UI runs as a separate application from the MCP server and communicates through the shared configuration files and SQLite database. The base structure needs to support multiple pages and provide a clean, intuitive interface.

**Goal:** Implement the base Streamlit application structure with multi-page support, shared components, and proper separation from the MCP server.

**Acceptance Criteria:**
1. Create Streamlit app entry point with multi-page support
2. Implement base layout with sidebar navigation
3. Create home/dashboard page with server status information
4. Set up page routing for configuration and logs pages
5. Implement shared UI components (headers, alerts, etc.)
6. Add error handling and user feedback mechanisms
7. Include CSS customization for consistent styling
8. Ensure UI works without server running

**Technical Guidance:**
- Create UI structure at `{{cookiecutter.project_slug}}/ui/`:
```
ui/
├── app.py              # Main Streamlit entry point
├── pages/              # Multi-page structure
│   ├── 1_🏠_Home.py
│   ├── 2_⚙️_Configuration.py
│   └── 3_📊_Logs.py
└── lib/               # Shared utilities
    ├── components.py  # Reusable UI components
    ├── styles.py      # CSS and theming
    └── utils.py       # Helper functions
```
- Use Streamlit's native multi-page support
- Implement session state management for UI state
- Add configuration file monitoring for live updates
- Include "Server must be restarted" warnings
- Example app.py structure:
```python
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="{{ cookiecutter.project_name }} Admin",
    page_icon="🛠️",
    layout="wide"
)

# Sidebar with project info
st.sidebar.title("{{ cookiecutter.project_name }}")
st.sidebar.info("MCP Server Administration")
```

---

### Phase 4, Issue 2: Configuration Editor Page Implementation

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, streamlit-ui
**Dependencies:** Phase 4, Issue 1 (Streamlit Admin UI Base Structure)  

**Background & Goal:**
The configuration editor page allows users to view and modify server configuration through a user-friendly web interface. Changes made through the UI are saved to the configuration file, and users are notified that the server needs to be restarted for changes to take effect.

**Goal:** Implement a Streamlit page for editing MCP server configuration with validation, save functionality, and clear user feedback.

**Acceptance Criteria:**
1. Create configuration editor page with form inputs
2. Load current configuration and display in editable format
3. Implement input validation matching configuration schema
4. Add save functionality with confirmation
5. Show diff of changes before saving
6. Display server restart notification after changes
7. Include configuration reset to defaults option
8. Add configuration export/import functionality

**Technical Guidance:**
- Use Streamlit form components for configuration editing:
```python
import streamlit as st
from {{cookiecutter.project_slug}}.config import Config, ConfigManager

def render_configuration_page():
    st.title("⚙️ Configuration")
    
    config_manager = ConfigManager("{{ cookiecutter.project_slug }}")
    config = config_manager.load_config()
    
    with st.form("config_form"):
        st.subheader("Server Settings")
        log_level = st.selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR"],
            index=["DEBUG", "INFO", "WARNING", "ERROR"].index(config.server.log_level)
        )
        
        log_retention = st.number_input(
            "Log Retention (days)",
            min_value=1,
            max_value=365,
            value=config.server.log_retention_days
        )
        
        if st.form_submit_button("Save Configuration"):
            # Update and save config
            # Show restart notification
```
- Implement configuration comparison before save
- Use st.warning() for restart notifications
- Add undo/redo functionality using session state
- Include tooltips for configuration options

---

### Phase 4, Issue 3: SQLite Log Viewer with Filtering and Export

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, streamlit-ui
**Dependencies:** Phase 4, Issue 1 (Streamlit Admin UI Base Structure)  

**Background & Goal:**
The log viewer page provides insights into MCP server operations by displaying logs from the SQLite database. Users need to filter logs by various criteria, view detailed information about tool executions, and export logs for further analysis.

**Goal:** Implement a comprehensive log viewer page with filtering, sorting, detailed views, and export capabilities.

**Acceptance Criteria:**
1. Create log viewer page with paginated table display
2. Implement filters for:
   - Date/time range
   - Tool name
   - Status (success/error)
   - Log level
3. Add sorting by any column
4. Include detailed view modal for individual log entries
5. Implement CSV export functionality
6. Add log statistics dashboard (success rate, avg duration, etc.)
7. Include real-time log refresh option
8. Add log search functionality

**Technical Guidance:**
- Use Streamlit's dataframe display with pagination:
```python
import streamlit as st
import pandas as pd
from {{cookiecutter.project_slug}}.decorators.logging import LogDatabase

def render_logs_page():
    st.title("📊 Logs")
    
    # Filters in sidebar
    with st.sidebar:
        st.subheader("Filters")
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now())
        )
        
        tool_filter = st.multiselect(
            "Tools",
            options=get_unique_tools()
        )
        
        status_filter = st.radio(
            "Status",
            options=["All", "Success", "Error"]
        )
    
    # Load and filter logs
    log_db = LogDatabase()
    logs_df = log_db.get_logs_dataframe(
        start_date=date_range[0],
        end_date=date_range[1],
        tools=tool_filter,
        status=status_filter
    )
    
    # Display with pagination
    page_size = st.selectbox("Rows per page", [10, 25, 50, 100])
    total_pages = len(logs_df) // page_size + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    st.dataframe(
        logs_df.iloc[(page-1)*page_size:page*page_size],
        use_container_width=True
    )
```
- Implement CSV export using st.download_button()
- Add expandable rows for detailed log information
- Include charts for log statistics (success rate over time, tool usage)
- Use st.experimental_rerun() for auto-refresh functionality
- Add caching for performance with large log volumes

---

## Phase 5: Documentation and Examples

### Phase 5, Issue 1: README and Documentation Templates

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, documentation
**Dependencies:** All Phase 1-4 issues must be complete

**Background & Goal:**
The cookie cutter template needs comprehensive documentation that helps developers understand both how to use the template and how to work with the generated MCP server. This includes the main README for the cookie cutter itself, README template for generated projects, and additional documentation templates that cover common scenarios.

**Goal:** Create a complete documentation suite that enables developers to quickly understand and effectively use both the cookie cutter template and the generated MCP servers.

**Acceptance Criteria:**
1. Create main cookie cutter README.md with:
   - Clear project overview and benefits
   - Prerequisites and installation instructions
   - Cookie cutter variables explanation
   - Quick start guide with examples
   - Links to additional resources

2. Create README template for generated projects ({{cookiecutter.project_slug}}/README.md.jinja2) with:
   - Dynamic content based on cookie cutter choices
   - Installation and setup instructions
   - MCP client configuration examples (Claude Desktop, Cursor)
   - Tool documentation placeholders
   - Troubleshooting section

3. Create CONTRIBUTING.md template with:
   - Development setup instructions
   - Code style guidelines
   - Testing requirements
   - Pull request process

4. Create API_DOCUMENTATION.md template with:
   - Tool documentation structure
   - Parameter descriptions
   - Example requests and responses
   - Error handling documentation

5. Create ARCHITECTURE.md template explaining:
   - Decorator pattern implementation
   - Logging system design
   - Configuration management
   - Optional Streamlit UI integration

**Technical Guidance:**
- Use Jinja2 templating for dynamic content based on cookie cutter variables
- Include code snippets and examples throughout
- Ensure documentation works for both stdio and SSE transport modes
- Reference the SAAGA decorator patterns clearly
- Include platform-specific instructions where needed (Windows, macOS, Linux)

---

### Phase 5, Issue 2: Example Tools and Usage Patterns

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, documentation
**Dependencies:** Phase 2, Issue 2 (Auto-Decorator Application Pattern)

**Background & Goal:**
Developers need concrete examples to understand how to build tools with the SAAGA decorator patterns. The template should include optional example tools that demonstrate best practices for exception handling, logging, and parallelization.

**Goal:** Provide well-documented example tools that serve as templates for developers to build their own MCP tools using SAAGA patterns.

**Acceptance Criteria:**
1. Create basic example tools when include_example_tools is "yes":
   - Simple calculation tool (demonstrates basic decorator usage)
   - File operation tool (demonstrates exception handling)
   - API fetch tool (demonstrates async patterns)
   - Data processing tool (demonstrates logging)

2. Create parallel example tool when include_parallel_example is "yes":
   - Batch processing tool using parallelize decorator
   - Clear documentation on when to use parallelization
   - Performance comparison examples

3. Create example_patterns.py with common patterns:
   - Input validation patterns
   - Error handling strategies
   - Logging best practices
   - Configuration usage examples

4. Create tests/test_examples.py demonstrating:
   - How to test decorated tools
   - Mocking strategies for decorators
   - Integration testing patterns

5. Include inline documentation in all examples:
   - Clear docstrings following Google style
   - Comments explaining decorator behavior
   - Type hints throughout

**Technical Guidance:**
- Examples should be functional but simple enough to understand
- Show both successful and error scenarios
- Demonstrate proper use of all three decorators (exception_handler, tool_logger, parallelize)
- Include examples of configuration customization
- Show how to access logs programmatically

---

### Phase 5, Issue 3: Developer Guide and Troubleshooting

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, documentation
**Dependencies:** All Phase 1-4 issues must be complete

**Background & Goal:**
Developers need guidance on common development tasks, debugging strategies, and solutions to frequently encountered issues. This comprehensive guide will help them work effectively with the generated MCP servers.

**Goal:** Create a developer guide that addresses common scenarios, provides debugging strategies, and offers solutions to typical problems.

**Acceptance Criteria:**
1. Create DEVELOPER_GUIDE.md with sections on:
   - Setting up development environment
   - Understanding the decorator chain
   - Adding new tools
   - Customizing decorators
   - Working with the configuration system

2. Create debugging section covering:
   - Enabling debug logging
   - Inspecting decorator behavior
   - Using the SQLite log viewer
   - Common error messages and solutions
   - Performance profiling tips

3. Create troubleshooting guide with:
   - MCP client connection issues
   - Decorator ordering problems
   - Configuration loading errors
   - Streamlit UI issues
   - Platform-specific problems

4. Create FAQ section addressing:
   - When to use each decorator
   - How to handle async tools
   - Configuration best practices
   - Log rotation and maintenance
   - Security considerations

5. Include code snippets for common tasks:
   - Adding custom decorators
   - Extending the logging system
   - Creating custom UI pages
   - Integrating with external services

**Technical Guidance:**
- Use real error messages from testing
- Include command-line examples
- Provide diagnostic scripts where helpful
- Reference specific log entries
- Include platform-specific sections clearly marked

---

## Phase 6: Testing and Validation

### Phase 6, Issue 1: Cookie Cutter Template Testing Framework

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, testing
**Dependencies:** All Phase 1-5 issues must be complete

**Background & Goal:**
The cookie cutter template needs comprehensive testing to ensure it generates valid projects under all configuration combinations. This includes testing the template rendering, generated code functionality, and integration between components.

**Goal:** Implement a robust testing framework that validates the cookie cutter template and all generated project variations.

**Acceptance Criteria:**
1. Create test suite for cookie cutter template:
   - Test all variable combinations
   - Validate generated file structure
   - Ensure Jinja2 templates render correctly
   - Check for syntax errors in generated Python code

2. Implement automated project generation tests:
   - Generate projects with different configurations
   - Run generated project tests
   - Validate that decorators apply correctly
   - Test both stdio and SSE transport modes

3. Create integration tests for:
   - MCP server startup and shutdown
   - Tool registration with decorators
   - Configuration loading
   - Logging system functionality
   - Optional Streamlit UI launch

4. Implement pre-commit hooks for:
   - Template syntax validation
   - Python code formatting (black)
   - Import sorting (isort)
   - Type checking (mypy)

5. Create GitHub Actions workflow for:
   - Running all tests on PR
   - Testing on Python 3.10, 3.11, 3.12
   - Validating documentation builds
   - Checking for broken links

**Technical Guidance:**
- Use pytest for test framework
- Implement fixtures for common test scenarios
- Use temporary directories for generated projects
- Mock external dependencies appropriately
- Ensure tests run in isolated environments
- Cookiecutter Documentation References:
  - API Reference: https://cookiecutter.readthedocs.io/en/stable/cookiecutter.html

---

### Phase 6, Issue 2: Cross-Platform Compatibility Testing

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, testing
**Dependencies:** Phase 6, Issue 1 (Cookie Cutter Template Testing Framework)

**Background & Goal:**
MCP servers need to work reliably across Windows, macOS, and Linux. The cookie cutter template must generate projects that handle platform-specific differences in paths, processes, and system behaviors.

**Goal:** Ensure generated MCP servers work correctly on all major platforms with proper handling of platform-specific concerns.

**Acceptance Criteria:**
1. Test configuration paths on all platforms:
   - Verify platformdirs usage is correct
   - Test path normalization
   - Validate file permissions handling
   - Check Unicode path support

2. Validate process management across platforms:
   - Test stdio communication on each OS
   - Verify signal handling differences
   - Check process cleanup behavior
   - Test with different shells/terminals

3. Test Streamlit UI on all platforms:
   - Verify UI launches correctly
   - Test file upload/download features
   - Check log file access permissions
   - Validate configuration editing

4. Create platform-specific test matrix:
   - Windows 10/11 with PowerShell and CMD
   - macOS 12+ with zsh and bash
   - Ubuntu 20.04/22.04
   - Common Docker environments

5. Document platform-specific requirements:
   - Required system libraries
   - Python version constraints
   - Shell/terminal requirements
   - Known limitations per platform

**Technical Guidance:**
- Use GitHub Actions matrix builds
- Test with os.path and pathlib variations
- Include tests for different file encodings
- Test with spaces and special characters in paths
- Verify SQLite works correctly on all platforms

---

### Phase 6, Issue 3: End-to-End Validation and Release Preparation

**Issue Type:** Executable Spec
**Labels:** mcp, cookie-cutter, testing
**Dependencies:** Phase 6, Issue 2 (Cross-Platform Compatibility Testing)

**Background & Goal:**
Before releasing the cookie cutter template, we need comprehensive end-to-end validation that simulates real developer workflows. This includes testing the complete journey from template installation to deploying a working MCP server.

**Goal:** Validate the complete developer experience and prepare the template for public release with all necessary documentation and tooling.

**Acceptance Criteria:**
1. Create end-to-end test scenarios:
   - Fresh developer installing template
   - Creating first MCP server
   - Adding custom tools
   - Configuring with MCP clients
   - Using the Streamlit UI

2. Implement release checklist validation:
   - All documentation is complete and accurate
   - Examples run without errors
   - Tests pass on all platforms
   - Security scan shows no vulnerabilities
   - License files are in place

3. Create performance benchmarks:
   - Measure decorator overhead
   - Test logging system performance
   - Validate parallel tool efficiency
   - Check memory usage patterns
   - Document performance characteristics

4. Prepare release automation:
   - Version bumping scripts
   - Changelog generation
   - PyPI package building
   - GitHub release creation
   - Documentation deployment

5. Create post-release validation:
   - Test pip installation
   - Verify cookiecutter command works
   - Check all links in documentation
   - Monitor initial user issues
   - Establish feedback channels

**Technical Guidance:**
- Use semantic versioning
- Create comprehensive CHANGELOG.md
- Include migration guides for future versions
- Set up issue templates for bug reports
- Establish clear contribution guidelines

---

## Summary

This document contains 18 JIRA issues covering all 6 phases of the MCP Server Cookie Cutter project:

- **Phase 1 (3 issues)**: Core template structure and basic MCP server scaffolding
- **Phase 2 (3 issues)**: SAAGA decorator integration and automatic application
- **Phase 3 (3 issues)**: Platform-aware configuration management system
- **Phase 4 (3 issues)**: Optional Streamlit administrative UI
- **Phase 5 (3 issues)**: Documentation, examples, and developer guides
- **Phase 6 (3 issues)**: Testing framework and release preparation

Each issue includes detailed acceptance criteria and technical guidance to ensure successful implementation of this enhanced MCP server cookie cutter template with SAAGA decorator patterns.