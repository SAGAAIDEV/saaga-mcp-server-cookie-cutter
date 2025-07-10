"""{% if cookiecutter.include_admin_ui == "yes" %}
Configuration management page for {{cookiecutter.project_name}} Admin UI

This page provides interface for managing server configuration, environment variables,
and tool settings. Changes require server restart to take effect.

Note: This is a placeholder implementation for Phase 4, Issue 1.
Full functionality will be implemented in Phase 4, Issue 2.
{% else %}
Placeholder for optional Streamlit admin UI configuration page.
{% endif %}"""

{% if cookiecutter.include_admin_ui == "yes" %}
import streamlit as st
from pathlib import Path
import sys
from typing import Dict, Any, Optional
import yaml

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from ui.lib.components import (
        render_info_card,
        render_warning_banner,
        render_config_section
    )
    from ui.lib.utils import (
        load_configuration,
        validate_configuration,
        save_configuration
    )
except ImportError as e:
    st.error(f"Failed to import UI components: {e}")
    st.info("Configuration management may have limited functionality.")

# Page configuration
st.set_page_config(
    page_title="{{cookiecutter.project_name}} - Configuration",
    page_icon="⚙️",
    layout="wide"
)

def render_placeholder_notice():
    """Render notice that this is a placeholder implementation"""
    st.info("""
    🚧 **Placeholder Implementation**
    
    This configuration interface is part of Phase 4, Issue 1 (Base Structure).
    Full configuration management functionality will be implemented in Phase 4, Issue 2.
    
    **Planned Features:**
    - Real-time configuration editing
    - Validation and error checking  
    - Platform-aware path management
    - Environment variable configuration
    - Tool and decorator settings
    """)

def render_current_config_preview():
    """Render a preview of current configuration"""
    st.subheader("📋 Current Configuration Preview")
    
    # Mock configuration data based on cookiecutter variables
    config_preview = {
        "server": {
            "name": "{{cookiecutter.project_name}}",
            "port": {{cookiecutter.server_port}},
            "log_level": "{{cookiecutter.log_level}}",
            "log_retention_days": {{cookiecutter.log_retention_days}}
        },
        "features": {
            "admin_ui": True,
            "example_tools": {{cookiecutter.include_example_tools == "yes"}},
            "parallel_examples": {{cookiecutter.include_parallel_example == "yes"}}
        },
        "paths": {
            "config_dir": "~/.config/{{cookiecutter.project_slug}}",
            "log_dir": "~/.local/share/{{cookiecutter.project_slug}}/logs",
            "data_dir": "~/.local/share/{{cookiecutter.project_slug}}/data"
        }
    }
    
    # Display configuration in tabs
    tab1, tab2, tab3 = st.tabs(["🔧 Server", "🎛️ Features", "📁 Paths"])
    
    with tab1:
        st.json(config_preview["server"])
        
    with tab2:
        st.json(config_preview["features"])
        
    with tab3:
        st.json(config_preview["paths"])

def render_configuration_form():
    """Render configuration editing form (placeholder)"""
    st.subheader("✏️ Configuration Editor")
    
    with st.form("config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("Server Name", value="{{cookiecutter.project_name}}", disabled=True)
            st.number_input("Server Port", value={{cookiecutter.server_port}}, disabled=True)
            st.selectbox("Log Level", 
                        options=["DEBUG", "INFO", "WARNING", "ERROR"],
                        index=["DEBUG", "INFO", "WARNING", "ERROR"].index("{{cookiecutter.log_level}}"),
                        disabled=True)
        
        with col2:
            st.number_input("Log Retention (days)", value={{cookiecutter.log_retention_days}}, disabled=True)
            st.checkbox("Enable Example Tools", value={{cookiecutter.include_example_tools == "yes"}}, disabled=True)
            st.checkbox("Enable Parallel Examples", value={{cookiecutter.include_parallel_example == "yes"}}, disabled=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            save_button = st.form_submit_button("💾 Save Configuration", disabled=True)
            
        with col2:
            reset_button = st.form_submit_button("🔄 Reset to Defaults", disabled=True)
            
        with col3:
            st.caption("⚠️ Configuration editing will be enabled in Phase 4, Issue 2")

def render_environment_variables():
    """Render environment variables section (placeholder)"""
    st.subheader("🌍 Environment Variables")
    
    # Mock environment variables
    env_vars = {
        "{{cookiecutter.project_slug.upper()}}_LOG_LEVEL": "{{cookiecutter.log_level}}",
        "{{cookiecutter.project_slug.upper()}}_PORT": "{{cookiecutter.server_port}}",
        "{{cookiecutter.project_slug.upper()}}_CONFIG_PATH": "~/.config/{{cookiecutter.project_slug}}",
        "PYTHONPATH": "Current directory included"
    }
    
    st.markdown("**Current Environment:**")
    for key, value in env_vars.items():
        st.code(f"{key}={value}")
    
    st.caption("🔧 Environment variable management will be available in Phase 4, Issue 2")

def render_validation_section():
    """Render configuration validation section"""
    st.subheader("✅ Configuration Validation")
    
    # Mock validation results
    validation_results = [
        {"check": "Server port availability", "status": "✅ Pass", "message": "Port {{cookiecutter.server_port}} is available"},
        {"check": "Python version compatibility", "status": "✅ Pass", "message": "Python {{cookiecutter.python_version}}+ detected"},
        {"check": "Required dependencies", "status": "✅ Pass", "message": "All required packages installed"},
        {"check": "Configuration file syntax", "status": "✅ Pass", "message": "Valid YAML configuration"},
        {"check": "Log directory permissions", "status": "⚠️ Warning", "message": "Directory will be created on first run"}
    ]
    
    for result in validation_results:
        col1, col2, col3 = st.columns([2, 1, 3])
        with col1:
            st.write(result["check"])
        with col2:
            st.write(result["status"])
        with col3:
            st.caption(result["message"])

def render_restart_notice():
    """Render server restart requirement notice"""
    st.warning("""
    ⚠️ **Server Restart Required**
    
    Configuration changes require the MCP server to be restarted to take effect.
    The admin UI will continue to function independently during server restarts.
    
    **To restart the server:**
    1. Stop the current server process
    2. Run the server again with: `python -m {{cookiecutter.project_slug}}`
    3. Verify the new configuration is loaded
    """)

def main():
    """Main configuration page content"""
    # Page header
    st.title("⚙️ {{cookiecutter.project_name}} Configuration")
    st.markdown("Manage server settings, features, and environment configuration.")
    st.markdown("---")
    
    # Placeholder notice
    render_placeholder_notice()
    st.markdown("---")
    
    # Current configuration preview
    render_current_config_preview()
    st.markdown("---")
    
    # Configuration form
    render_configuration_form()
    st.markdown("---")
    
    # Environment variables
    render_environment_variables()
    st.markdown("---")
    
    # Validation section
    render_validation_section()
    st.markdown("---")
    
    # Restart notice
    render_restart_notice()
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        if st.button("📊 View Logs", use_container_width=True):
            st.switch_page("pages/3_📊_Logs.py")
    
    # Footer
    st.caption("Configuration management interface • Phase 4, Issue 1 placeholder")

if __name__ == "__main__":
    main()
{% endif %}