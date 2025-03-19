# settings.py
import streamlit as st
import requests

def show_settings(api_url):
    st.title("Settings")
    
    # Project Settings
    st.header("Project Settings")
    
    with st.form("project_settings"):
        st.subheader("Risk Thresholds")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_risk_threshold = st.slider(
                "High Risk Threshold", 
                min_value=10, 
                max_value=25,
                value=15,
                help="Minimum score for High risks (Probability × Impact)"
            )
        
        with col2:
            medium_risk_threshold = st.slider(
                "Medium Risk Threshold", 
                min_value=5, 
                max_value=15,
                value=8,
                help="Minimum score for Medium risks (Probability × Impact)"
            )
        
        with col3:
            low_risk_threshold = st.slider(
                "Low Risk Threshold", 
                min_value=1, 
                max_value=10,
                value=1,
                help="Minimum score for Low risks (Probability × Impact)"
            )
        
        st.subheader("Notification Settings")
        notify_high = st.checkbox("Notify on High Risk", value=True)
        notify_medium = st.checkbox("Notify on Medium Risk", value=True)
        notify_low = st.checkbox("Notify on Low Risk", value=False)
        
        email_notifications = st.text_input("Email Notifications", 
                                            placeholder="Enter email addresses separated by commas")
        
        submitted = st.form_submit_button("Save Settings")
        
        if submitted:
            # In a real application, this would save to the database
            st.success("Settings saved successfully!")
    
    # API Settings
    st.header("API Settings")
    
    with st.form("api_settings"):
        gemini_api_key = st.text_input("Gemini API Key", 
                                      type="password", 
                                      value=st.secrets.get("GEMINI_API_KEY", ""))
        
        supabase_url = st.text_input("Supabase URL", 
                                    value=st.secrets.get("SUPABASE_URL", ""))
        
        supabase_key = st.text_input("Supabase Key", 
                                    type="password", 
                                    value=st.secrets.get("SUPABASE_KEY", ""))
        
        submitted_api = st.form_submit_button("Save API Settings")
        
        if submitted_api:
            # In a real application, this would update the environment variables or secrets
            st.success("API settings saved! You may need to restart the application for changes to take effect.")
    
    # System Settings
    st.header("System Settings")
    
    with st.form("system_settings"):
        st.subheader("Analysis Settings")
        
        analysis_frequency = st.selectbox(
            "Risk Analysis Frequency",
            options=["Daily", "Weekly", "Bi-weekly", "Monthly"],
            index=1
        )
        
        auto_analysis = st.checkbox("Enable Automatic Analysis", value=True)
        
        st.subheader("Data Retention")
        
        data_retention = st.slider(
            "Data Retention Period (months)",
            min_value=1,
            max_value=60,
            value=12
        )
        
        submitted_system = st.form_submit_button("Save System Settings")
        
        if submitted_system:
            # In a real application, this would save to the database
            st.success("System settings saved successfully!")
    
    # Add a data reset option
    st.header("Data Management")
    
    if st.button("Reset Demo Data", type="primary", use_container_width=True):
        # In a real application, this would reset the data
        with st.spinner("Resetting demo data..."):
            # Simulate reset process
            import time
            time.sleep(2)
            st.success("Demo data has been reset!")