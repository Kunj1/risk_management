# risk_analysis.py
import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from components.risk_matrix import display_risk_matrix

def show_risk_analysis(api_url, project_id):
    st.title("Risk Analysis")
    
    # Load project and risk data
    @st.cache_data(ttl=300)
    def load_analysis_data(pid):
        try:
            project = requests.get(f"{api_url}/projects/{pid}").json()
            risks = requests.get(f"{api_url}/projects/{pid}/risks").json()
            return project, risks
        except Exception as e:
            st.error(f"Error loading analysis data: {e}")
            return None, []
    
    project, risks = load_analysis_data(project_id)
    
    if not project:
        st.error("Project details could not be loaded")
        return
    
    # Analysis header
    st.header(f"Risk Analysis for {project['name']}")
    
    # Run new analysis button
    if st.button("Run New Risk Analysis"):
        with st.spinner("Running comprehensive risk analysis..."):
            try:
                response = requests.post(f"{api_url}/analyze", params={"project_id": project_id})
                st.success("Risk analysis completed successfully!")
                # Reload the data
                st.cache_data.clear()
                project, risks = load_analysis_data(project_id)
            except Exception as e:
                st.error(f"Error running analysis: {e}")
    
    # Risk overview
    st.subheader("Risk Overview")
    
    if risks:
        # Calculate risk metrics
        high_risks = sum(1 for r in risks if r.get('severity') == 'high')
        medium_risks = sum(1 for r in risks if r.get('severity') == 'medium')
        low_risks = sum(1 for r in risks if r.get('severity') == 'low')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Risks", high_risks)
        
        with col2:
            st.metric("Medium Risks", medium_risks)
        
        with col3:
            st.metric("Low Risks", low_risks)
        
        # Risk categories analysis
        risk_df = pd.DataFrame(risks)
        
        if 'category' in risk_df.columns:
            st.subheader("Risk Categories")
            
            category_counts = risk_df['category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            
            fig = px.pie(
                category_counts,
                values='Count',
                names='Category',
                title='Risks by Category'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Risk matrix
        st.subheader("Risk Matrix")
        display_risk_matrix(risk_df)
        
        # Detailed risk analysis
        st.subheader("Risk Details")
        
        # Create tabs for different risk categories
        if 'category' in risk_df.columns:
            categories = ['All'] + sorted(risk_df['category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)
            
            if selected_category != 'All':
                filtered_df = risk_df[risk_df['category'] == selected_category]
            else:
                filtered_df = risk_df
            
            st.dataframe(
                filtered_df[['id', 'name', 'category', 'probability', 'impact', 'severity', 'description']],
                use_container_width=True
            )
        else:
            st.dataframe(
                risk_df,
                use_container_width=True
            )
        
        # Risk mitigation recommendations
        st.subheader("Mitigation Recommendations")
        
        for risk in sorted(risks, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('severity', 'low'), 3)):
            if risk.get('severity') == 'high':
                color = "🔴"
            elif risk.get('severity') == 'medium':
                color = "🟠"
            else:
                color = "🟢"
            
            with st.expander(f"{color} {risk.get('name', 'Unnamed Risk')} ({risk.get('severity', 'unknown').upper()})"):
                st.markdown(f"**Description:** {risk.get('description', 'No description')}")
                st.markdown(f"**Impact:** {risk.get('impact_description', 'No impact information')}")
                st.markdown(f"**Mitigation Strategy:**")
                
                if 'mitigation' in risk:
                    for step in risk['mitigation']:
                        st.markdown(f"- {step}")
                else:
                    st.info("No mitigation strategy defined yet.")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Owner:** {risk.get('owner', 'Unassigned')}")
                with col2:
                    st.markdown(f"**Due Date:** {risk.get('due_date', 'Not set')}")
    else:
        st.info("No risks have been identified yet. Run a risk analysis to identify project risks.")