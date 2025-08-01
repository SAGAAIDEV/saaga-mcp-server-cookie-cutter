"""{% if cookiecutter.include_admin_ui == "yes" %}
Streamlit Admin UI for {{cookiecutter.project_name}}

This admin interface provides web-based management for the MCP server configuration
and log viewing. It runs independently of the MCP server and communicates through
shared configuration files and SQLite database.

Run with: streamlit run {{cookiecutter.project_slug}}/ui/app.py
{% else %}
Placeholder for optional Streamlit admin UI.
This file is only populated when include_admin_ui=yes during cookiecutter generation.
{% endif %}"""

{% if cookiecutter.include_admin_ui == "yes" %}
import streamlit as st
from pathlib import Path
import sys
import traceback
from typing import Dict, Any, Optional

# Add the parent directory to the path to import project modules
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Global flag for component availability
components_available = True
error_details = None

try:
    from lib.components import render_header, render_sidebar, render_error_message
    from lib.styles import apply_custom_styles, hide_streamlit_style
    from lib.utils import check_server_status, get_project_info
except ImportError as e:
    components_available = False
    error_details = str(e)
    
    # Fallback: Create minimal error display
    def render_error_message(error, context=""):
        st.error("❌ Error{}: {}".format(" in " + context if context else "", error))
    
    def apply_custom_styles():
        pass
    
    def hide_streamlit_style():
        pass
    
    def render_header():
        st.title("{{cookiecutter.project_name}} Admin")
        st.caption("MCP Server Administration Interface")
    
    def render_sidebar():
        with st.sidebar:
            st.markdown("### ⚠️ Limited Mode")
            st.warning("Some UI components are not available.")
    
    def check_server_status():
        return "unknown"
    
    def get_project_info():
        return {"name": "{{cookiecutter.project_name}}", "version": "0.1.0"}

# Page configuration
st.set_page_config(
    page_title="{{cookiecutter.project_name}} Admin",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.server_status = "unknown"
    st.session_state.last_status_check = None


def main():
    """Main application entry point"""
    try:
        # Apply custom styles and hide Streamlit branding
        apply_custom_styles()
        hide_streamlit_style()
        
        # Show component availability status
        if not components_available:
            st.warning("⚠️ **Limited Functionality Mode**")
            st.warning(f"UI components failed to load: {error_details}")
            st.info("The admin interface is running in limited mode. Some features may not work correctly.")
            st.markdown("---")
        
        # Render header and sidebar
        render_header()
        render_sidebar()
        
        # Show component status in sidebar if there are issues
        if not components_available:
            with st.sidebar:
                st.markdown("---")
                st.error("⚠️ Component Issues")
                st.caption("Some UI features are unavailable due to import errors.")
        
        # Redirect to Home page (Streamlit will auto-discover pages in /pages/ directory)
        st.switch_page("pages/1_🏠_Home.py")
        
    except Exception as e:
        st.error("❌ Critical Application Error")
        st.error(f"The admin interface encountered a critical error: {str(e)}")
        
        with st.expander("🔍 Technical Details"):
            st.code(traceback.format_exc())
        
        st.markdown("---")
        st.info("""
        💡 **Troubleshooting Steps:**
        1. Refresh the page (Ctrl+R / Cmd+R)
        2. Check that all dependencies are installed
        3. Verify the MCP server is properly configured
        4. Check server logs for additional error information
        5. Ensure the virtual environment is activated
        """)
        
        # Show system information for debugging
        with st.expander("🔧 System Information"):
            st.code(f"""
Python Version: {sys.version}
Working Directory: {Path.cwd()}
Application Path: {Path(__file__).parent}
Components Available: {components_available}
Session State Keys: {list(st.session_state.keys()) if hasattr(st, 'session_state') else 'N/A'}
            """)

if __name__ == "__main__":
    main()
{% endif %}