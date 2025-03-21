# dashboard.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from components.risk_matrix import display_risk_matrix

def show_dashboard(api_url):
    st.title("Project Risk Dashboard")
    
    # Load project data
    @st.cache_data(ttl=300)
    def load_dashboard_data():
        try:
            projects = requests.get(f"{api_url}/projects").json()
            
            # For each project, get risks
            for project in projects:
                project['risks'] = requests.get(f"{api_url}/projects/{project['id']}/risks").json()
            
            return projects
        except Exception as e:
            st.error(f"Error loading dashboard data: {e}")
            return []
    
    projects_data = load_dashboard_data()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Projects", len(projects_data))
    
    # Calculate metrics from project data
    total_high_risks = sum(len([r for r in project.get('risks', []) if r.get('severity') == 'high']) for project in projects_data)
    total_medium_risks = sum(len([r for r in project.get('risks', []) if r.get('severity') == 'medium']) for project in projects_data)
    total_low_risks = sum(len([r for r in project.get('risks', []) if r.get('severity') == 'low']) for project in projects_data)
    
    with col2:
        st.metric("High Risk Projects", sum(1 for p in projects_data if any(r.get('severity') == 'high' for r in p.get('risks', []))))
    
    with col3:
        st.metric("Medium Risk Projects", sum(1 for p in projects_data if any(r.get('severity') == 'medium' for r in p.get('risks', []))))
    
    with col4:
        st.metric("Low Risk Projects", sum(1 for p in projects_data if all(r.get('severity') == 'low' for r in p.get('risks', []))))
    
    # Projects overview
    st.subheader("Projects Overview")
    
    # Create a summary dataframe
    if projects_data:
        df = pd.DataFrame([
            {
                "Project": p["name"],
                "High Risks": len([r for r in p.get('risks', []) if r.get('severity') == 'high']),
                "Medium Risks": len([r for r in p.get('risks', []) if r.get('severity') == 'medium']),
                "Low Risks": len([r for r in p.get('risks', []) if r.get('severity') == 'low']),
                "Total Risks": len(p.get('risks', [])),
                "Status": p.get("status", "Unknown")
            }
            for p in projects_data
        ])
        
        st.dataframe(df)
        
        # Risk distribution chart
        st.subheader("Risk Distribution by Project")
        
        fig = px.bar(
            df, 
            x="Project", 
            y=["High Risks", "Medium Risks", "Low Risks"],
            title="Risk Distribution by Project",
            color_discrete_sequence=["#FF4B4B", "#FFA64B", "#4BD964"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk trends
        st.subheader("Risk Trend")
        
        # For a real app, this would show historical risk data
        # Here we'll create sample trend data
        import numpy as np
        
        # Generate sample trend data
        dates = pd.date_range(end=pd.now().date(), periods=30, freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'High Risks': np.random.randint(total_high_risks - 5, total_high_risks + 5, 30),
            'Medium Risks': np.random.randint(total_medium_risks - 8, total_medium_risks + 8, 30),
            'Low Risks': np.random.randint(total_low_risks - 10, total_low_risks + 10, 30)
        })
        # Plot the trend
        fig_trend = px.line(
            trend_data, 
            x='Date', 
            y=['High Risks', 'Medium Risks', 'Low Risks'],
            title='Risk Trend Over Time',
            color_discrete_sequence=["#FF4B4B", "#FFA64B", "#4BD964"]
        )
    
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Recent risk alerts
    st.subheader("Recent Risk Alerts")
    
    if projects_data:
    # In a real app, these would be actual alerts
        alerts = [
        {"project": projects_data[0]["name"], "risk": "Schedule delay risk increased to HIGH", "timestamp": "Today 10:30 AM"},
        {"project": projects_data[-1]["name"] if len(projects_data) > 1 else projects_data[0]["name"], 
         "risk": "New regulatory compliance risk identified", "timestamp": "Yesterday 3:45 PM"},
        {"project": projects_data[1]["name"] if len(projects_data) > 1 else projects_data[0]["name"], 
         "risk": "Resource availability risk escalated", "timestamp": "Mar 15, 2025"}
    ]
    
        for alert in alerts:
            st.info(f"**{alert['project']}**: {alert['risk']} - *{alert['timestamp']}*")
    else:
        st.warning("No projects available. Please make sure the backend API is running and returning data.")