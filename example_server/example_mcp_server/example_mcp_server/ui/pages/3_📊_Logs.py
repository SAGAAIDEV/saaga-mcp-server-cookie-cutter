"""
Log viewer page for Example MCP Server Admin UI

This page provides interface for viewing, filtering, and analyzing server logs
from the SQLite logging database. Includes export capabilities and real-time updates.

Note: This is a placeholder implementation for Phase 4, Issue 1.
Full functionality will be implemented in Phase 4, Issue 3.
"""


import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from lib.components import (
        render_log_filters,
        render_log_table,
        render_log_metrics,
        render_export_options
    )
    from lib.utils import (
        load_logs_from_database,
        filter_logs,
        export_logs,
        get_log_statistics
    )
except ImportError as e:
    st.error(f"Failed to import UI components: {e}")
    st.info("Log viewer may have limited functionality.")

# Note: Page configuration is handled by main app.py

def generate_mock_log_data() -> pd.DataFrame:
    """Generate mock log data for demonstration"""
    import random
    from datetime import datetime, timedelta
    
    # Mock log entries
    log_levels = ["INFO", "DEBUG", "WARNING", "ERROR"]
    tools = ["example_tool", "list_files", "search_content", "get_config", "health_check"]
    statuses = ["success", "error", "timeout"]
    
    logs = []
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(100):
        timestamp = base_time + timedelta(
            hours=random.randint(0, 168),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        tool_name = random.choice(tools)
        status = random.choice(statuses)
        level = random.choice(log_levels)
        
        # Generate realistic error rates
        if status == "error":
            level = random.choice(["WARNING", "ERROR"])
        elif status == "success":
            level = random.choice(["INFO", "DEBUG"])
            
        duration_ms = random.randint(10, 5000)
        
        logs.append({
            "timestamp": timestamp,
            "level": level,
            "tool_name": tool_name,
            "status": status,
            "duration_ms": duration_ms,
            "input_args": '{"arg1": "value' + str(i) + '", "arg2": ' + str(random.randint(1, 100)) + '}',
            "output_summary": "Processed " + str(random.randint(1, 50)) + " items" if status == "success" else "Failed to process",
            "error_message": "Error code: " + str(random.randint(400, 500)) if status == "error" else None
        })
    
    return pd.DataFrame(logs)

def render_placeholder_notice():
    """Render notice that this is a placeholder implementation"""
    st.info("""
    🚧 **Placeholder Implementation**
    
    This log viewer interface is part of Phase 4, Issue 1 (Base Structure).
    Full log management functionality will be implemented in Phase 4, Issue 3.
    
    **Planned Features:**
    - Real SQLite database integration
    - Advanced filtering and search
    - Export to multiple formats (CSV, JSON, Excel)
    - Real-time log streaming
    - Performance analytics and charts
    - Log retention management
    """)

def render_log_metrics_section(df: pd.DataFrame):
    """Render log metrics and statistics"""
    st.subheader("📈 Log Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_logs = len(df)
        st.metric("Total Logs", f"{total_logs:,}")
    
    with col2:
        error_count = len(df[df['status'] == 'error'])
        error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
        st.metric("Error Rate", f"{error_rate:.1f}%", delta=f"{error_count} errors")
    
    with col3:
        avg_duration = df['duration_ms'].mean()
        st.metric("Avg Duration", f"{avg_duration:.0f}ms")
    
    with col4:
        unique_tools = df['tool_name'].nunique()
        st.metric("Active Tools", unique_tools)

def render_log_filters_section():
    """Render log filtering controls"""
    st.subheader("🔍 Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        log_level = st.selectbox(
            "Log Level",
            options=["All", "DEBUG", "INFO", "WARNING", "ERROR"],
            key="log_level_filter"
        )
    
    with col2:
        tool_filter = st.selectbox(
            "Tool",
            options=["All", "example_tool", "list_files", "search_content", "get_config", "health_check"],
            key="tool_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            options=["All", "success", "error", "timeout"],
            key="status_filter"
        )
    
    with col4:
        time_range = st.selectbox(
            "Time Range",
            options=["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=2,
            key="time_range_filter"
        )
    
    return {
        "log_level": log_level if log_level != "All" else None,
        "tool": tool_filter if tool_filter != "All" else None,
        "status": status_filter if status_filter != "All" else None,
        "time_range": time_range
    }

def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """Apply filters to the log dataframe"""
    filtered_df = df.copy()
    
    if filters["log_level"]:
        filtered_df = filtered_df[filtered_df['level'] == filters["log_level"]]
    
    if filters["tool"]:
        filtered_df = filtered_df[filtered_df['tool_name'] == filters["tool"]]
    
    if filters["status"]:
        filtered_df = filtered_df[filtered_df['status'] == filters["status"]]
    
    # Apply time range filter
    now = datetime.now()
    if filters["time_range"] == "Last Hour":
        cutoff = now - timedelta(hours=1)
    elif filters["time_range"] == "Last 24 Hours":
        cutoff = now - timedelta(days=1)
    elif filters["time_range"] == "Last 7 Days":
        cutoff = now - timedelta(days=7)
    elif filters["time_range"] == "Last 30 Days":
        cutoff = now - timedelta(days=30)
    else:
        cutoff = None
    
    if cutoff:
        filtered_df = filtered_df[filtered_df['timestamp'] >= cutoff]
    
    return filtered_df

def render_log_table_section(df: pd.DataFrame):
    """Render the log table with pagination"""
    st.subheader("📋 Log Entries")
    
    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        page_size = st.selectbox("Rows per page", [25, 50, 100, 200], index=1)
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Sort and paginate
    df_sorted = df.sort_values('timestamp', ascending=False)
    total_rows = len(df_sorted)
    total_pages = (total_rows + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df_sorted.iloc[start_idx:end_idx]
    else:
        df_page = df_sorted
    
    # Display table
    if len(df_page) > 0:
        # Format timestamp for display
        df_display = df_page.copy()
        df_display['timestamp'] = df_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color code status
        def color_status(val):
            if val == 'success':
                return 'background-color: #d4edda'
            elif val == 'error':
                return 'background-color: #f8d7da'
            elif val == 'timeout':
                return 'background-color: #fff3cd'
            return ''
        
        # Display the styled dataframe
        styled_df = df_display.style.applymap(color_status, subset=['status'])
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "Timestamp",
                "level": "Level",
                "tool_name": "Tool",
                "status": "Status",
                "duration_ms": st.column_config.NumberColumn("Duration (ms)", format="%d ms"),
                "input_args": "Input",
                "output_summary": "Output",
                "error_message": "Error"
            }
        )
        
        st.caption(f"Showing {len(df_page)} of {total_rows} log entries")
    else:
        st.info("No log entries match the current filters.")

def render_export_section(df: pd.DataFrame):
    """Render export options"""
    st.subheader("📥 Export Logs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export CSV", disabled=True):
            st.info("CSV export will be available in Phase 4, Issue 3")
    
    with col2:
        if st.button("📊 Export Excel", disabled=True):
            st.info("Excel export will be available in Phase 4, Issue 3")
    
    with col3:
        if st.button("🔗 Export JSON", disabled=True):
            st.info("JSON export will be available in Phase 4, Issue 3")

def main():
    """Main logs page content"""
    # Page header
    st.title("📊 Example MCP Server Logs")
    st.markdown("View and analyze server logs with filtering and export capabilities.")
    st.markdown("---")
    
    # Placeholder notice
    render_placeholder_notice()
    st.markdown("---")
    
    # Generate mock data
    log_data = generate_mock_log_data()
    
    # Render filters
    filters = render_log_filters_section()
    
    # Apply filters
    filtered_data = apply_filters(log_data, filters)
    
    st.markdown("---")
    
    # Metrics section
    render_log_metrics_section(filtered_data)
    
    st.markdown("---")
    
    # Log table
    render_log_table_section(filtered_data)
    
    st.markdown("---")
    
    # Export section
    render_export_section(filtered_data)
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("pages/1_🏠_Home.py")
    
    with col2:
        if st.button("⚙️ Configuration", use_container_width=True):
            st.switch_page("pages/2_⚙️_Configuration.py")
    
    # Footer
    st.caption("Log viewer interface • Phase 4, Issue 1 placeholder with mock data")

if __name__ == "__main__":
    main()
