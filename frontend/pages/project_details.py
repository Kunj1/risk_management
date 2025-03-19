import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from components.risk_matrix import display_risk_matrix
from components.chatbot import display_chatbot

def show_project_details(api_url, project_id):
    # Load project details
    @st.cache_data(ttl=300)
    def load_project_details(pid):
        try:
            project = requests.get(f"{api_url}/projects/{pid}").json()
            risks = requests.get(f"{api_url}/projects/{pid}/risks").json()
            return project, risks
        except Exception as e:
            st.error(f"Error loading project details: {e}")
            return None, []
    
    project, risks = load_project_details(project_id)
    
    if not project:
        st.error("Project details could not be loaded")
        return
    
    # Project header
    st.title(f"Project: {project['name']}")
    
    # Project details card
    with st.expander("Project Details", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Industry:** {project.get('industry', 'N/A')}")
            st.markdown(f"**Technology:** {project.get('technology', 'N/A')}")
            st.markdown(f"**Start Date:** {project.get('start_date', 'N/A')}")
        
        with col2:
            st.markdown(f"**Status:** {project.get('status', 'N/A')}")
            st.markdown(f"**Duration:** {project.get('duration', 'N/A')} months")
            st.markdown(f"**End Date:** {project.get('end_date', 'N/A')}")
    
    # Project metrics
    st.subheader("Project Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Schedule Variance", 
            f"{project.get('schedule_variance', 0)}%", 
            delta=project.get('schedule_variance_trend', 0)
        )
    
    with col2:
        st.metric(
            "Budget Variance", 
            f"{project.get('budget_variance', 0)}%", 
            delta=project.get('budget_variance_trend', 0)
        )
    
    with col3:
        st.metric(
            "Resource Utilization", 
            f"{project.get('resource_utilization', 0)}%", 
            delta=project.get('resource_utilization_trend', 0)
        )
    
    with col4:
        high_risks = len([r for r in risks if r.get('severity') == 'high'])
        st.metric(
            "High Risks", 
            high_risks, 
            delta=-project.get('resolved_high_risks', 0),
            delta_color="inverse"
        )
    
    # Risk summary
    st.subheader("Risk Summary")
    
    # Create dataframe for risks
    if risks:
        risk_df = pd.DataFrame(risks)
        
        # Display risk matrix
        display_risk_matrix(risk_df)
        
        # Risk table
        st.dataframe(
            risk_df[['id', 'name', 'category', 'probability', 'impact', 'severity', 'mitigation_status']],
            use_container_width=True
        )
    else:
        st.info("No risks identified for this project yet.")
    
    # Project timeline
    st.subheader("Project Timeline")
    
    # Create sample timeline data
    if 'milestones' in project:
        milestones = project['milestones']
    else:
        # Sample milestones
        milestones = [
            {"name": "Requirements Gathering", "start_date": "2025-01-15", "end_date": "2025-01-30", "status": "Completed"},
            {"name": "Design Phase", "start_date": "2025-02-01", "end_date": "2025-02-28", "status": "Completed"},
            {"name": "Development Phase", "start_date": "2025-03-01", "end_date": "2025-04-15", "status": "In Progress"},
            {"name": "Testing", "start_date": "2025-04-16", "end_date": "2025-05-15", "status": "Not Started"},
            {"name": "Deployment", "start_date": "2025-05-16", "end_date": "2025-05-30", "status": "Not Started"}
        ]
    
    milestone_df = pd.DataFrame(milestones)
    
    # Define colors for status
    color_map = {
        "Completed": "#4BD964",
        "In Progress": "#FFA64B",
        "Not Started": "#D3D3D3",
        "Delayed": "#FF4B4B"
    }
    
    fig = px.timeline(
        milestone_df, 
        x_start="start_date", 
        x_end="end_date", 
        y="name",
        color="status",
        color_discrete_map=color_map,
        title="Project Timeline"
    )
    
    fig.update_layout(yaxis={"title": "Milestone"})
    st.plotly_chart(fig, use_container_width=True)
    
    # Chat with project assistant
    st.subheader("Project Risk Assistant")
    display_chatbot(api_url, project_id)