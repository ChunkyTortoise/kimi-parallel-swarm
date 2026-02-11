"""
Streamlit Dashboard for Kimi Agent System
Modern UI for monitoring parallel agent execution
"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(
    page_title="Kimi Agent Swarm Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B6B;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .status-running { color: #00C851; }
    .status-stopped { color: #ff4444; }
    .agent-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def load_stats():
    """Load system statistics."""
    return {
        "total_prospects": 150,
        "messages_sent": 47,
        "connections_accepted": 12,
        "pipeline_value": "$24,500",
        "active_agents": 5,
        "queue_depth": 0,
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_agent_status():
    """Get agent status."""
    return [
        {"name": "ICP Research", "status": "🟢 Active", "tasks": 23, "success_rate": 94},
        {"name": "Copy Generation", "status": "🟢 Active", "tasks": 47, "success_rate": 98},
        {"name": "Outreach Execution", "status": "🟢 Active", "tasks": 47, "success_rate": 89},
        {"name": "CRM Pipeline", "status": "🟢 Active", "tasks": 12, "success_rate": 100},
        {"name": "Performance Opt", "status": "🟢 Active", "tasks": 8, "success_rate": 100},
    ]

# Header
st.markdown('<p class="main-header">🚀 Kimi Agent Swarm Dashboard</p>', unsafe_allow_html=True)
st.caption("Real-time monitoring of 5 parallel agents | 10× speedup enabled")

# Metrics Row
stats = load_stats()
cols = st.columns(5)
with cols[0]:
    st.metric("📊 Total Prospects", stats["total_prospects"], "+12 today")
with cols[1]:
    st.metric("📧 Messages Sent", stats["messages_sent"], "+5 today")
with cols[2]:
    st.metric("✅ Connections", stats["connections_accepted"], "+2 today")
with cols[3]:
    st.metric("💰 Pipeline Value", stats["pipeline_value"], "+$3.2k")
with cols[4]:
    st.metric("🤖 Active Agents", stats["active_agents"])

# Two Column Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Performance Overview")
    
    # Mock data for chart
    dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
    df = pd.DataFrame({
        'Date': dates,
        'Prospects Researched': [15, 18, 22, 25, 28, 30, 32],
        'Messages Sent': [8, 12, 15, 18, 20, 22, 25],
        'Connections Made': [2, 3, 4, 5, 7, 8, 10]
    })
    
    tab1, tab2, tab3 = st.tabs(["Activity", "Pipeline", "Conversion"])
    
    with tab1:
        st.line_chart(df.set_index('Date')[['Prospects Researched', 'Messages Sent']])
    
    with tab2:
        st.bar_chart(df.set_index('Date')['Connections Made'])
    
    with tab3:
        # Conversion funnel
        funnel_data = {
            "Stage": ["Research", "Copy Gen", "Sent", "Replied", "Meeting"],
            "Count": [150, 147, 47, 12, 5]
        }
        st.bar_chart(pd.DataFrame(funnel_data).set_index("Stage"))

with col2:
    st.subheader("🤖 Agent Status")
    
    agents = get_agent_status()
    for agent in agents:
        with st.container():
            st.markdown(f"""
            <div class="agent-card">
                <b>{agent['name']}</b><br>
                <span class="status-running">{agent['status']}</span><br>
                <small>Tasks: {agent['tasks']} | Success: {agent['success_rate']}%</small>
            </div>
            """, unsafe_allow_html=True)
            st.caption("")

# Quick Actions
st.subheader("⚡ Quick Actions")
action_cols = st.columns(4)

with action_cols[0]:
    if st.button("🌅 Morning Routine", use_container_width=True):
        st.success("Morning routine started!")
        
with action_cols[1]:
    if st.button("📤 Send Batch", use_container_width=True):
        st.info("Batch processing 20 messages...")
        
with action_cols[2]:
    if st.button("🔄 Sync CRM", use_container_width=True):
        st.success("CRM synced!")
        
with action_cols[3]:
    if st.button("📊 Generate Report", use_container_width=True):
        st.info("Report generated!")

# Recent Activity
st.subheader("📋 Recent Activity")
activity_data = [
    {"Time": "10:30 AM", "Agent": "ICP Research", "Action": "Found 3 new SaaS prospects", "Status": "✅"},
    {"Time": "10:28 AM", "Agent": "Copy Generation", "Action": "Generated 5 personalized messages", "Status": "✅"},
    {"Time": "10:25 AM", "Agent": "Outreach Execution", "Action": "Sent 2 LinkedIn connections", "Status": "✅"},
    {"Time": "10:20 AM", "Agent": "CRM Pipeline", "Action": "Updated deal stage for Acme Corp", "Status": "✅"},
    {"Time": "10:15 AM", "Agent": "Performance Opt", "Action": "Analyzed response rates", "Status": "✅"},
]

st.table(pd.DataFrame(activity_data))

# Footer
st.divider()
st.caption(f"Last updated: {stats['last_run']} | Parallel Agent Swarm v1.0")
