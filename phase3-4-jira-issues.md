# Phase 3 JIRA Issues - Configuration System

## ACT-152: Platform-Aware Configuration Management

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter  
**Parent**: ACT-149  

### Background & Goal

The MCP Server Cookie Cutter needs a robust configuration management system that respects platform-specific conventions for configuration file locations. This system must work across Windows, macOS, and Linux, using the appropriate directories for each platform (e.g., ~/Library/Application Support on macOS, %APPDATA% on Windows, ~/.config on Linux).

**Goal**: Implement a platform-aware configuration management module that handles configuration file creation, loading, and updating using platformdirs for cross-platform compatibility.

### Acceptance Criteria

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

### Technical Guidance

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

## ACT-153: Shared Configuration Module Implementation

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter  
**Parent**: ACT-149  

### Background & Goal

The configuration system needs to be shared between the MCP server and the optional Streamlit admin UI. This requires a well-structured configuration module that defines the configuration schema, provides validation, and handles updates from both the server runtime and the UI.

**Goal**: Implement a shared configuration module with a defined schema, validation, and update mechanisms that can be used by both the MCP server and Streamlit UI.

### Acceptance Criteria

1. Define a configuration schema using Pydantic or dataclasses
2. Implement configuration validation with helpful error messages
3. Create methods for updating individual configuration values
4. Support configuration versioning for future migrations
5. Implement configuration merge logic for partial updates
6. Add configuration change detection for server restart notifications
7. Include example configuration values in the cookie cutter template
8. Document all configuration options

### Technical Guidance

- Define configuration schema in `{{cookiecutter.project_slug}}/config.py`
- Use Pydantic for validation and serialization:
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

## ACT-154: Configuration Template and Validation

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter  
**Parent**: ACT-149  

### Background & Goal

The cookie cutter template needs to generate appropriate default configuration files based on user choices during project creation. This includes creating initial configuration files with sensible defaults and providing validation utilities to ensure configuration integrity.

**Goal**: Create configuration templates for the cookie cutter that generate appropriate default configurations based on user choices, with comprehensive validation utilities.

### Acceptance Criteria

1. Create Jinja2 templates for initial configuration files
2. Generate different defaults based on cookie cutter variables
3. Implement configuration validation utilities
4. Add configuration health check functionality
5. Create example configurations for common use cases
6. Include configuration documentation in generated README
7. Add configuration migration utilities for future updates
8. Implement configuration backup before updates

### Technical Guidance

- Create template at `{{cookiecutter.project_slug}}/config.yaml.j2`:
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

# Phase 4 JIRA Issues - Admin UI

## ACT-155: Streamlit Admin UI Base Structure

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter, streamlit-ui  
**Parent**: ACT-149  

### Background & Goal

The optional Streamlit admin UI provides a web-based interface for managing MCP server configuration and viewing logs. This UI runs as a separate application from the MCP server and communicates through the shared configuration files and SQLite database. The base structure needs to support multiple pages and provide a clean, intuitive interface.

**Goal**: Implement the base Streamlit application structure with multi-page support, shared components, and proper separation from the MCP server.

### Acceptance Criteria

1. Create Streamlit app entry point with multi-page support
2. Implement base layout with sidebar navigation
3. Create home/dashboard page with server status information
4. Set up page routing for configuration and logs pages
5. Implement shared UI components (headers, alerts, etc.)
6. Add error handling and user feedback mechanisms
7. Include CSS customization for consistent styling
8. Ensure UI works without server running

### Technical Guidance

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

## ACT-156: Configuration Editor Page Implementation

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter, streamlit-ui  
**Parent**: ACT-149  

### Background & Goal

The configuration editor page allows users to view and modify server configuration through a user-friendly web interface. Changes made through the UI are saved to the configuration file, and users are notified that the server needs to be restarted for changes to take effect.

**Goal**: Implement a Streamlit page for editing MCP server configuration with validation, save functionality, and clear user feedback.

### Acceptance Criteria

1. Create configuration editor page with form inputs
2. Load current configuration and display in editable format
3. Implement input validation matching configuration schema
4. Add save functionality with confirmation
5. Show diff of changes before saving
6. Display server restart notification after changes
7. Include configuration reset to defaults option
8. Add configuration export/import functionality

### Technical Guidance

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

## ACT-157: SQLite Log Viewer with Filtering and Export

**Project**: ACT  
**Type**: Task  
**Labels**: mcp, cookie-cutter, streamlit-ui  
**Parent**: ACT-149  

### Background & Goal

The log viewer page provides insights into MCP server operations by displaying logs from the SQLite database. Users need to filter logs by various criteria, view detailed information about tool executions, and export logs for further analysis.

**Goal**: Implement a comprehensive log viewer page with filtering, sorting, detailed views, and export capabilities.

### Acceptance Criteria

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

### Technical Guidance

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