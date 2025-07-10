"""
Streamlit Admin UI for Demo MCP Server

This admin interface provides web-based management for the MCP server configuration
and log viewing. It runs independently of the MCP server and communicates through
shared configuration files and SQLite database.

Run with: streamlit run demo_mcp_server/ui/app.py
"""


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
        st.title("Demo MCP Server Admin")
        st.caption("MCP Server Administration Interface")
    
    def render_sidebar():
        with st.sidebar:
            st.markdown("### ⚠️ Limited Mode")
            st.warning("Some UI components are not available.")
    
    def check_server_status():
        return "unknown"
    
    def get_project_info():
        return {"name": "Demo MCP Server", "version": "0.1.0"}

# Page configuration
st.set_page_config(
    page_title="Demo MCP Server Admin",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.server_status = "unknown"
    st.session_state.last_status_check = None

def home_page():
    """Main dashboard page"""
    st.title("🏠 Demo MCP Server Admin")
    st.markdown("---")
    
    # Server status section
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("Server Status", "Unknown", help="Current MCP server status")
        
    with col2:
        st.metric("Admin UI", "Active", help="This admin interface is running")
        
    with col3:
        if st.button("🔄 Check Server Status", help="Refresh server status"):
            try:
                status = check_server_status()
                st.session_state.server_status = status
                st.success(f"Server status: {status}")
            except Exception as e:
                st.error(f"Failed to check server status: {e}")
    
    st.markdown("---")
    
    # Project information
    st.subheader("📋 Project Information")
    
    try:
        project_info = get_project_info()
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Project Name:** Demo MCP Server")
            st.write("**Version:** 0.1.0")
            st.write("**Author:** Tim Kitchens")
            
        with col2:
            st.write("**Python Version:** 3.11+")
            st.write("**Admin UI:** Enabled")
            st.write("**Log Level:** INFO")
            
    except Exception as e:
        st.error(f"Failed to load project information: {e}")
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Edit Configuration", help="Modify server configuration"):
            st.session_state.current_page = "Configuration"
            st.rerun()
            
    with col2:
        if st.button("📊 View Logs", help="Browse server logs"):
            st.session_state.current_page = "Logs"
            st.rerun()
            
    with col3:
        if st.button("🔄 Restart Server", help="Restart the MCP server"):
            st.warning("⚠️ Server restart functionality not yet implemented")
            st.info("This will require the MCP server to be restarted manually.")

def configuration_page():
    """Configuration management page (placeholder)"""
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    st.info("🚧 Configuration management interface will be implemented in Phase 4, Issue 2")
    
    st.markdown("""
    **Planned Features:**
    - Server configuration editing
    - Environment variable management
    - Tool configuration
    - Logging settings
    - Platform-specific paths
    """)
    
    if st.button("🏠 Back to Home"):
        st.session_state.current_page = "Home"
        st.rerun()

def logs_page():
    """Log viewer page (placeholder)"""
    st.title("📊 Logs")
    st.markdown("---")
    
    st.info("🚧 Log viewer interface will be implemented in Phase 4, Issue 3")
    
    st.markdown("""
    **Planned Features:**
    - SQLite log database viewer
    - Filtering and search capabilities
    - Export functionality
    - Real-time log streaming
    - Performance metrics
    """)
    
    if st.button("🏠 Back to Home"):
        st.session_state.current_page = "Home"
        st.rerun()

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
        
        # Initialize current page in session state
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"
        
        # Add navigation to sidebar
        with st.sidebar:
            st.markdown("### 📱 Navigation")
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.current_page = "Home"
                st.rerun()
            if st.button("⚙️ Configuration", use_container_width=True):
                st.session_state.current_page = "Configuration"
                st.rerun()
            if st.button("📊 Logs", use_container_width=True):
                st.session_state.current_page = "Logs"
                st.rerun()
        
        # Display the selected page
        try:
            if st.session_state.current_page == "Home":
                home_page()
            elif st.session_state.current_page == "Configuration":
                configuration_page()
            elif st.session_state.current_page == "Logs":
                logs_page()
        except Exception as e:
            st.error("❌ Page Display Error")
            render_error_message(e, f"displaying {st.session_state.current_page} page")
            
            # Fallback to home page
            st.markdown("---")
            st.info("🏠 **Fallback to Home**")
            home_page()
        
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
