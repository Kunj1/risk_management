import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any, Optional

# API endpoint
API_URL = "http://localhost:8000"  # Adjust if your backend is on a different URL

def send_message(message: str, project_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a message to the chat API and get the response.
    
    Args:
        message: The user's message text
        project_id: Optional project ID to provide context
        
    Returns:
        Dictionary containing the API response
    """
    token = st.session_state.get('token', '')
    
    if not token:
        return {"error": "Not authenticated"}
    
    try:
        payload = {"message": message}
        if project_id:
            payload["project_id"] = project_id
        
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"API error: {response.status_code}",
                "detail": response.text
            }
    
    except Exception as e:
        return {"error": f"Connection error: {str(e)}"}

def get_chat_history() -> List[Dict[str, Any]]:
    """
    Retrieve chat history from session state or initialize if not exists.
    
    Returns:
        List of chat messages
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    return st.session_state.chat_history

def add_message_to_history(role: str, content: str) -> None:
    """
    Add a message to the chat history.
    
    Args:
        role: Either 'user' or 'assistant'
        content: Message text
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    st.session_state.chat_history.append({
        "role": role,
        "content": content
    })

def clear_chat_history() -> None:
    """
    Clear the chat history.
    """
    st.session_state.chat_history = []

def display_chat_interface(project_id: Optional[str] = None) -> None:
    """
    Displays the chat interface and handles message sending/receiving.
    
    This function is meant to be called from the main streamlit_app.py
    but is not used directly since the main file already implements
    the chat interface in the display_chat_page function.
    
    Args:
        project_id: Optional project ID to provide context
    """
    st.subheader("💬 Chat with Risk Management Assistant")
    
    # Get chat history
    chat_history = get_chat_history()
    
    # Display chat history
    for message in chat_history:
        role = message["role"]
        content = message["content"]
        
        with st.chat_message(role):
            st.write(content)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        with st.chat_message("user"):
            st.write(user_input)
        
        add_message_to_history("user", user_input)
        
        # Get response from API
        with st.spinner("Thinking..."):
            response_data = send_message(user_input, project_id)
        
        # Check for errors
        if "error" in response_data:
            with st.chat_message("assistant"):
                st.error(response_data["error"])
                if "detail" in response_data:
                    st.write(response_data["detail"])
        else:
            # Display assistant response
            assistant_response = response_data.get("response", "I couldn't process your request.")
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Simulate typing effect
                full_response = ""
                for chunk in assistant_response.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)  # Adjust typing speed
                
                # Final response without cursor
                message_placeholder.markdown(assistant_response)
            
            add_message_to_history("assistant", assistant_response)
    
    # Option to clear chat
    if chat_history and st.button("Clear chat history"):
        clear_chat_history()
        st.experimental_rerun()

def format_risk_analysis(risk_data: Dict[str, Any]) -> str:
    """
    Format risk analysis data for display in chat.
    
    Args:
        risk_data: Dictionary containing risk analysis information
        
    Returns:
        Formatted string with risk analysis
    """
    result = "## Risk Analysis Summary\n\n"
    
    # Overall risk score
    risk_score = risk_data.get("overall_risk_score", 0)
    risk_level = risk_data.get("risk_level", "Unknown")
    
    result += f"### Overall Risk: {risk_level} ({risk_score:.2f})\n\n"
    
    # Individual risk factors
    result += "### Risk Factors:\n\n"
    
    identified_risks = risk_data.get("identified_risks", [])
    if identified_risks:
        for risk in identified_risks:
            if risk.get("risk_identified", False):
                risk_type = risk.get("risk_type", "Unknown").title()
                details = risk.get("details", "No details")
                score = risk.get("risk_score", 0)
                
                # Emoji based on severity
                if score >= 0.8:
                    emoji = "🔴"
                elif score >= 0.6:
                    emoji = "🟠"
                elif score >= 0.4:
                    emoji = "🟡"
                else:
                    emoji = "🟢"
                
                result += f"{emoji} **{risk_type} Risk ({score:.2f})**: {details}\n\n"
    else:
        result += "No specific risks identified.\n\n"
    
    # Recommendations
    recommendations = risk_data.get("recommendations", [])
    if recommendations:
        result += "### Recommendations:\n\n"
        for rec in recommendations:
            result += f"- {rec}\n"
    
    return result