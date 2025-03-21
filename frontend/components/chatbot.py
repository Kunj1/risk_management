# chatbot.py
import streamlit as st
import requests
import json
from datetime import datetime

def display_chatbot(api_url, project_id=None):
    """
    Display a chatbot interface for interacting with the risk management system
    
    Args:
        api_url (str): Base URL for the API
        project_id (str, optional): ID of the current project
    """
    # Initialize chat messages in session state if not present
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your Project Risk Assistant. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about project risks..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Send message to backend
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{api_url}/chat",
                    json={"content": prompt, "project_id": project_id}
                )
                
                if response.status_code == 200:
                    assistant_response = response.json().get("response", "I'm sorry, I couldn't process your request.")
                else:
                    assistant_response = f"Error: {response.status_code}. Please try again later."
        except Exception as e:
            assistant_response = f"Error: {str(e)}. Please check your connection."
        
        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)