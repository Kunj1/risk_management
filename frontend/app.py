# app.py
import streamlit as st
import requests
import json
import pandas as pd
from pages.dashboard import show_dashboard
from pages.project_details import show_project_details
from pages.risk_analysis import show_risk_analysis
from pages.settings import show_settings

# Configure the page
st.set_page_config(
    page_title="Project Risk Management System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# Function to load all projects
@st.cache_data(ttl=300)
def load_projects():
    try:
        response = requests.get(f"{API_URL}/projects")
        return response.json()
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        return []

# Sidebar navigation
st.sidebar.title("Project Risk Management")

# Project selector
projects = load_projects()
project_names = [p["name"] for p in projects]
selected_project_name = st.sidebar.selectbox(
    "Select Project",
    options=project_names,
    index=0 if project_names else None
)

# Update selected project in session state
if selected_project_name:
    selected_project = next((p for p in projects if p["name"] == selected_project_name), None)
    st.session_state.selected_project = selected_project

# Navigation menu
pages = {
    "dashboard": "📊 Dashboard",
    "project_details": "📋 Project Details",
    "risk_analysis": "🔍 Risk Analysis",
    "settings": "⚙️ Settings"
}

st.sidebar.markdown("---")
selected_page = st.sidebar.radio("Navigation", list(pages.values()))

# Convert display name back to page key
selected_page_key = next(k for k, v in pages.items() if v == selected_page)
st.session_state.page = selected_page_key

# Display the selected page
if st.session_state.page == "dashboard":
    show_dashboard(API_URL)
elif st.session_state.page == "project_details":
    if st.session_state.selected_project:
        show_project_details(API_URL, st.session_state.selected_project["id"])
    else:
        st.warning("Please select a project first")
elif st.session_state.page == "risk_analysis":
    if st.session_state.selected_project:
        show_risk_analysis(API_URL, st.session_state.selected_project["id"])
    else:
        st.warning("Please select a project first")
elif st.session_state.page == "settings":
    show_settings(API_URL)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("AI-Powered Project Risk Management System")