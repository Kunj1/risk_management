import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Any, Optional, Union
import uuid
import altair as alt

from utils.auth_interface import login, register, logout, check_auth
from utils.chat_interface import display_chat_interface

# Configure the page
st.set_page_config(
    page_title="AI Project Risk Management",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API endpoint
API_URL = "http://localhost:8000"  # Adjust if your backend is on a different URL

# Define CSS
st.markdown(
    """
    <style>
    .risk-critical {
        color: #FF4B4B;
        font-weight: bold;
    }
    .risk-high {
        color: #FF8C00;
        font-weight: bold;
    }
    .risk-medium {
        color: #FFC107;
        font-weight: bold;
    }
    .risk-low {
        color: #28A745;
        font-weight: bold;
    }
    .dashboard-metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 2px rgba(0,0,0,0.1);
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 24px;
        font-weight: bold;
    }
    .header-subtitle {
        font-size: 16px;
        color: #6c757d;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def format_risk_level(risk_level: str) -> str:
    """Format risk level with appropriate CSS class."""
    return f'<span class="risk-{risk_level.lower()}">{risk_level}</span>'

def main():
    # Check if user is logged in
    if not check_auth():
        display_login_page()
        return
    
    # Initialize session state for page navigation if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x60?text=RiskShield", width=150)
        st.header("Navigation")
        
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.current_page = 'dashboard'
        
        if st.button("🔍 Project Details", use_container_width=True):
            st.session_state.current_page = 'projects'
        
        if st.button("📈 Risk Trends", use_container_width=True):
            st.session_state.current_page = 'risk_trends'
        
        if st.button("⚠️ Alerts", use_container_width=True):
            st.session_state.current_page = 'alerts'
        
        if st.button("💬 Risk Assistant", use_container_width=True):
            st.session_state.current_page = 'chat'
        
        st.markdown("---")
        
        # User info and logout
        token = st.session_state.get('token', '')
        username = st.session_state.get('username', 'User')
        st.info(f"Logged in as: {username}")
        
        if st.button("Logout", type="primary"):
            logout()
            st.experimental_rerun()
    
    # Main content based on current page
    if st.session_state.current_page == 'dashboard':
        display_dashboard()
    elif st.session_state.current_page == 'projects':
        display_projects()
    elif st.session_state.current_page == 'risk_trends':
        display_risk_trends()
    elif st.session_state.current_page == 'alerts':
        display_alerts()
    elif st.session_state.current_page == 'chat':
        display_chat_page()

def display_login_page():
    """Display login form and handle authentication."""
    st.title("🛡️ AI Project Risk Management System")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                success, message = login(username, password)
                if success:
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error(message)
    
    with tab2:
        with st.form("register_form"):
            st.subheader("Register")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit_button = st.form_submit_button("Register")
            
            if submit_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, message = register(new_username, new_password, email, full_name)
                    if success:
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(message)

def display_dashboard():
    """Display the main dashboard with overall project health."""
    st.title("📊 Project Risk Dashboard")
    
    # Add refresh button and timestamp
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### Overview of Project Portfolio")
    with col2:
        if st.button("🔄 Refresh Data"):
            st.experimental_rerun()
    
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Fetch executive summary
    try:
        response = requests.get(
            f"{API_URL}/reporting/executive-summary",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            summary_data = response.json()
            
            # Display key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="dashboard-metric-box">', unsafe_allow_html=True)
                st.metric("Total Projects", summary_data.get("total_projects", 0))
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="dashboard-metric-box">', unsafe_allow_html=True)
                high_risk = summary_data.get("risk_distribution", {}).get("HIGH", 0) + summary_data.get("risk_distribution", {}).get("CRITICAL", 0)
                st.metric("High Risk Projects", high_risk)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col3:
                st.markdown('<div class="dashboard-metric-box">', unsafe_allow_html=True)
                st.metric("Unacknowledged Alerts", summary_data.get("unacknowledged_alerts", 0))
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col4:
                st.markdown('<div class="dashboard-metric-box">', unsafe_allow_html=True)
                st.metric("Market Risk", summary_data.get("market_summary", {}).get("market_risk_level", "UNKNOWN"))
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Risk distribution chart
            st.subheader("Risk Distribution")
            
            risk_dist = summary_data.get("risk_distribution", {})
            risk_data = pd.DataFrame({
                "Risk Level": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                "Count": [risk_dist.get("LOW", 0), risk_dist.get("MEDIUM", 0), risk_dist.get("HIGH", 0), risk_dist.get("CRITICAL", 0)]
            })
            
            colors = ["#28A745", "#FFC107", "#FF8C00", "#FF4B4B"]
            
            fig = px.pie(
                risk_data, 
                names="Risk Level", 
                values="Count",
                color="Risk Level",
                color_discrete_map={
                    "LOW": "#28A745",
                    "MEDIUM": "#FFC107",
                    "HIGH": "#FF8C00",
                    "CRITICAL": "#FF4B4B"
                },
                hole=0.4
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Projects requiring attention
            st.subheader("Projects Requiring Immediate Attention")
            
            high_risk_projects = summary_data.get("projects_requiring_attention", [])
            
            if high_risk_projects:
                for i, project in enumerate(high_risk_projects):
                    with st.expander(f"🚨 {project['name']} - {project['risk_level']}"):
                        st.markdown("**Key Issues:**")
                        for issue in project.get("key_issues", []):
                            st.markdown(f"- {issue}")
            else:
                st.info("No high-risk projects at the moment.")
            
            # Recommendations
            st.subheader("Recommendations")
            
            recommendations = summary_data.get("recommendations", [])
            if recommendations:
                for rec in recommendations:
                    st.markdown(f"- **{rec}**")
            else:
                st.info("No recommendations at this time.")
                
        else:
            st.error(f"Error fetching dashboard data: {response.text}")
    
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def display_projects():
    """Display detailed information about projects and their risks."""
    st.title("🔍 Project Details")
    
    # Fetch projects data
    try:
        projects_response = requests.get(
            f"{API_URL}/projects",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if projects_response.status_code == 200:
            projects = projects_response.json()
            
            # Project selection dropdown
            project_names = [p.get("name", f"Project {i+1}") for i, p in enumerate(projects)]
            selected_project_name = st.selectbox("Select Project", ["All Projects"] + project_names)
            
            if selected_project_name == "All Projects":
                # Display table of all projects
                st.subheader("Project Overview")
                
                # Create DataFrame for projects table
                projects_data = []
                for project in projects:
                    # Get latest risk score for project
                    try:
                        risk_response = requests.get(
                            f"{API_URL}/risks/{project.get('project_id')}",
                            headers={"Authorization": f"Bearer {st.session_state.token}"}
                        )
                        
                        risk_score = "Unknown"
                        risk_level = "Unknown"
                        
                        if risk_response.status_code == 200:
                            risk_data = risk_response.json()
                            risk_score = f"{risk_data.get('overall_risk_score', 0):.2f}"
                            risk_level = risk_data.get('risk_level', 'Unknown')
                    except:
                        risk_score = "Error"
                        risk_level = "Error"
                    
                    projects_data.append({
                        "Name": project.get("name", "Unnamed"),
                        "Start Date": project.get("start_date", "Unknown"),
                        "End Date": project.get("end_date", "Unknown"),
                        "Status": project.get("status", "Unknown"),
                        "Risk Score": risk_score,
                        "Risk Level": risk_level
                    })
                
                df = pd.DataFrame(projects_data)
                
                # Apply color formatting to risk level
                def format_risk(val):
                    if val == "CRITICAL":
                        return "background-color: #FFCDD2"
                    elif val == "HIGH":
                        return "background-color: #FFECB3"
                    elif val == "MEDIUM":
                        return "background-color: #FFF9C4"
                    elif val == "LOW":
                        return "background-color: #DCEDC8"
                    return ""
                
                st.dataframe(df.style.applymap(format_risk, subset=["Risk Level"]), use_container_width=True)
                
            else:
                # Display detailed information for selected project
                selected_project = next((p for p in projects if p.get("name") == selected_project_name), None)
                
                if selected_project:
                    project_id = selected_project.get("project_id")
                    
                    # Project header with summary information
                    st.header(selected_project_name)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Description:** {selected_project.get('description', 'No description')}")
                        st.markdown(f"**Status:** {selected_project.get('status', 'Unknown')}")
                    with col2:
                        start_date = selected_project.get('start_date', 'Unknown')
                        end_date = selected_project.get('end_date', 'Unknown')
                        st.markdown(f"**Timeline:** {start_date} to {end_date}")
                        
                        # Calculate days remaining if dates are available
                        try:
                            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                            days_remaining = (end_date_obj - datetime.now()).days
                            st.markdown(f"**Days Remaining:** {days_remaining}")
                        except:
                            st.markdown("**Days Remaining:** Unknown")
                    
                    # Get risk information for this project
                    try:
                        risk_response = requests.get(
                            f"{API_URL}/risks/{project_id}",
                            headers={"Authorization": f"Bearer {st.session_state.token}"}
                        )
                        
                        if risk_response.status_code == 200:
                            risk_data = risk_response.json()
                            
                            # Risk score and level
                            risk_score = risk_data.get('overall_risk_score', 0)
                            risk_level = risk_data.get('risk_level', 'Unknown')
                            
                            st.markdown("### Risk Assessment")
                            
                            # Risk gauge chart
                            fig = go.Figure(go.Indicator(
                                mode = "gauge+number",
                                value = risk_score * 100,
                                domain = {'x': [0, 1], 'y': [0, 1]},
                                title = {'text': "Risk Score"},
                                gauge = {
                                    'axis': {'range': [0, 100]},
                                    'bar': {'color': "darkgray"},
                                    'steps': [
                                        {'range': [0, 40], 'color': "#28A745"},
                                        {'range': [40, 60], 'color': "#FFC107"},
                                        {'range': [60, 80], 'color': "#FF8C00"},
                                        {'range': [80, 100], 'color': "#FF4B4B"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "red", 'width': 4},
                                        'thickness': 0.75,
                                        'value': risk_score * 100
                                    }
                                }
                            ))
                            
                            fig.update_layout(
                                height=250,
                                margin=dict(l=20, r=20, t=30, b=20)
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Identified risks
                            st.markdown("### Identified Risks")
                            
                            identified_risks = risk_data.get('identified_risks', [])
                            
                            if identified_risks:
                                for risk in identified_risks:
                                    if risk.get('risk_identified', False):
                                        risk_type = risk.get('risk_type', 'Unknown').title()
                                        details = risk.get('details', 'No details')
                                        score = risk.get('risk_score', 0)
                                        
                                        # Determine severity color
                                        if score >= 0.8:
                                            severity = "🔴 Critical"
                                        elif score >= 0.6:
                                            severity = "🟠 High"
                                        elif score >= 0.4:
                                            severity = "🟡 Medium"
                                        else:
                                            severity = "🟢 Low"
                                        
                                        st.markdown(f"**{risk_type} Risk - {severity}**")
                                        st.markdown(f"- {details}")
                                        st.markdown("---")
                            else:
                                st.info("No risks identified for this project.")
                            
                        else:
                            st.error(f"Error fetching risk data: {risk_response.text}")
                    
                    except Exception as e:
                        st.error(f"Error retrieving risk data: {str(e)}")
                
                else:
                    st.error("Project not found.")
        
        else:
            st.error(f"Error fetching projects: {projects_response.text}")
    
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def display_risk_trends():
    """Display risk trends over time for projects."""
    st.title("📈 Risk Trends Analysis")
    
    # Fetch projects for selection
    try:
        projects_response = requests.get(
            f"{API_URL}/projects",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if projects_response.status_code == 200:
            projects = projects_response.json()
            
            # Project selection
            project_names = [p.get("name", f"Project {i+1}") for i, p in enumerate(projects)]
            project_ids = [p.get("project_id") for p in projects]
            
            project_options = ["All Projects"] + project_names
            selected_project = st.selectbox("Select Project", project_options)
            
            # Time range selection
            col1, col2 = st.columns(2)
            with col1:
                time_range = st.selectbox(
                    "Time Range",
                    ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 180 Days"]
                )
            
            # Convert time range to days
            days_mapping = {
                "Last 7 Days": 7,
                "Last 30 Days": 30,
                "Last 90 Days": 90,
                "Last 180 Days": 180
            }
            days = days_mapping[time_range]
            
            # Get project ID if specific project selected
            project_id = None
            if selected_project != "All Projects":
                idx = project_names.index(selected_project)
                project_id = project_ids[idx]
            
            # Fetch risk trend data
            trend_response = requests.get(
                f"{API_URL}/reporting/risk-trends",
                params={"project_id": project_id, "days": days},
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            
            if trend_response.status_code == 200:
                trend_data = trend_response.json()
                
                # Process data for visualization
                trend_dict = trend_data.get("trend_data", {})
                
                if trend_dict:
                    # Convert to DataFrame for easier plotting
                    rows = []
                    for date, risks in trend_dict.items():
                        for risk_type, score in risks.items():
                            rows.append({
                                "Date": date,
                                "Risk Type": risk_type.title(),
                                "Risk Score": score
                            })
                    
                    df = pd.DataFrame(rows)
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.sort_values("Date")
                    
                    # Plot chart
                    st.subheader(f"Risk Trends for {selected_project}")
                    
                    # Line chart for risk trends
                    fig = px.line(
                        df,
                        x="Date",
                        y="Risk Score",
                        color="Risk Type",
                        markers=True,
                        color_discrete_map={
                            "Resource": "#FF6B6B",
                            "Payment": "#4ECDC4",
                            "Schedule": "#FFD166",
                            "Timeline": "#845EC2",
                            "Market": "#F9F871"
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Risk Score",
                        yaxis=dict(range=[0, 1]),
                        hovermode="x unified"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Risk level bands for context
                    st.markdown("""
                    **Risk Level Reference:**
                    - 0.0 - 0.4: Low Risk (Green)
                    - 0.4 - 0.6: Medium Risk (Yellow)
                    - 0.6 - 0.8: High Risk (Orange)
                    - 0.8 - 1.0: Critical Risk (Red)
                    """)
                    
                    # Risk type breakdown
                    with st.expander("View Risk Type Breakdown"):
                        # Group by risk type
                        risk_type_avg = df.groupby("Risk Type")["Risk Score"].mean().reset_index()
                        risk_type_avg = risk_type_avg.sort_values("Risk Score", ascending=False)
                        
                        fig2 = px.bar(
                            risk_type_avg,
                            x="Risk Type",
                            y="Risk Score",
                            color="Risk Type",
                            title="Average Risk Score by Risk Type",
                            color_discrete_sequence=px.colors.qualitative.Bold
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                    
                else:
                    st.info("No risk trend data available for the selected parameters.")
            
            else:
                st.error(f"Error fetching risk trends: {trend_response.text}")
        
        else:
            st.error(f"Error fetching projects: {projects_response.text}")
    
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def display_alerts():
    """Display active alerts and allow acknowledgment."""
    st.title("⚠️ Risk Alerts")
    
    # Fetch active alerts
    try:
        alerts_response = requests.get(
            f"{API_URL}/reporting/alerts",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if alerts_response.status_code == 200:
            alerts_data = alerts_response.json()
            alerts = alerts_data.get("alerts", [])
            
            if alerts:
                st.subheader(f"Active Alerts ({len(alerts)})")
                
                # Sort alerts by creation time (newest first)
                alerts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                
                for alert in alerts:
                    alert_id = alert.get("alert_id")
                    project_name = alert.get("project_name", "Unknown Project")
                    alert_type = alert.get("alert_type", "UNKNOWN")
                    message = alert.get("message", "No details")
                    created_at = alert.get("created_at", "Unknown time")
                    
                    # Format datetime if available
                    try:
                        created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                    
                    # Determine alert color based on type
                    if alert_type == "CRITICAL":
                        alert_color = "🔴"
                    elif alert_type == "HIGH":
                        alert_color = "🟠"
                    elif alert_type == "MEDIUM":
                        alert_color = "🟡"
                    else:
                        alert_color = "🔵"
                    
                    # Display alert in expander
                    with st.expander(f"{alert_color} {project_name} - {alert_type} Alert"):
                        st.markdown(f"**Created at:** {created_at}")
                        st.markdown(f"**Message:**\n{message}")
                        
                        # Acknowledge button
                        if st.button(f"Acknowledge Alert", key=f"ack_{alert_id}"):
                            try:
                                ack_response = requests.post(
                                    f"{API_URL}/reporting/acknowledge-alert/{alert_id}",
                                    headers={"Authorization": f"Bearer {st.session_state.token}"}
                                )
                                
                                if ack_response.status_code == 200:
                                    st.success("Alert acknowledged successfully!")
                                    # Refresh the page after a short delay
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.error(f"Error acknowledging alert: {ack_response.text}")
                            
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            else:
                st.info("No active alerts at this time.")
                
                # Show a success image
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image("https://via.placeholder.com/300x200?text=All+Clear", use_column_width=True)
        
        else:
            st.error(f"Error fetching alerts: {alerts_response.text}")
    
    except Exception as e:
        st.error(f"Error connecting to backend: {str(e)}")

def display_chat_page():
    """Display the conversational AI assistant interface."""
    st.title("💬 Project Risk Assistant")
    
    st.markdown("""
    Ask questions about project risks, get recommendations, or request status updates.
    The AI assistant can provide insights based on all available project and risk data.
    """)
    
    # Project context selection
    projects_response = requests.get(
        f"{API_URL}/projects",
        headers={"Authorization": f"Bearer {st.session_state.token}"}
    )
    
    project_context = "All Projects"
    
    if projects_response.status_code == 200:
        projects = projects_response.json()
        project_names = [p.get("name") for p in projects]
        
        project_context = st.selectbox(
            "Project Context (optional):",
            ["All Projects"] + project_names
        )
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_input = st.chat_input("How can I help you with project risks today?")
    
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get project ID if specific project selected
        project_id = None
        if project_context != "All Projects" and projects_response.status_code == 200:
            projects = projects_response.json()
            for project in projects:
                if project.get("name") == project_context:
                    project_id = project.get("project_id")
                    break
        
        # Send to API
        try:
            chat_response = requests.post(
                f"{API_URL}/chat",
                json={
                    "message": user_input,
                    "project_id": project_id
                },
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            
            if chat_response.status_code == 200:
                response_data = chat_response.json()
                response_message = response_data.get("response", "Sorry, I couldn't process your request.")
                
                # Display assistant response with typing effect
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = response_message
                    
                    # Simulate typing
                    message_placeholder.markdown(full_response)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })
            
            else:
                # Display error message
                with st.chat_message("assistant"):
                    st.error(f"Error: Could not get a response. Status code: {chat_response.status_code}")
                    st.write("Please try again or rephrase your question.")
        
        except Exception as e:
            # Display connection error
            with st.chat_message("assistant"):
                st.error(f"Connection error: {str(e)}")
                st.write("Please check if the backend server is running.")

if __name__ == "__main__":
    main()