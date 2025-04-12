import streamlit as st
import requests
import json
from typing import Tuple, Dict, Any, Optional

# API endpoint
API_URL = "http://localhost:8000"  # Adjust if your backend is on a different URL
'''
def login(username: str, password: str) -> Tuple[bool, str]:
    """
    Attempt to log in the user with provided credentials.
    
    Args:
        username: The username to log in with
        password: The password to authenticate with
        
    Returns:
        Tuple of (success, message) where success is a boolean and message is feedback
    """
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            # Login successful, store token in session state
            data = response.json()
            st.session_state.token = data.get("access_token")
            st.session_state.username = username
            return True, "Login successful"
        else:
            # Login failed
            error_msg = response.json().get("detail", "Invalid credentials")
            return False, f"Login failed: {error_msg}"
    
    except Exception as e:
        return False, f"Connection error: {str(e)}"
'''
def login(username: str, password: str) -> Tuple[bool, str]:
    """
    Attempt to log in the user with provided credentials.
    
    Args:
        username: The username to log in with
        password: The password to authenticate with
        
    Returns:
        Tuple of (success, message) where success is a boolean and message is feedback
    """
    try:
        response = requests.post(
            f"{API_URL}/auth/token",  # Changed from /auth/login to /auth/token
            data={"username": username, "password": password}  # Changed from json to data
        )
        
        if response.status_code == 200:
            # Login successful, store token in session state
            data = response.json()
            st.session_state.token = data.get("access_token")
            st.session_state.username = username
            return True, "Login successful"
        else:
            # Login failed
            error_msg = response.json().get("detail", "Invalid credentials")
            return False, f"Login failed: {error_msg}"
    
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def register(username: str, password: str, email: str, full_name: str) -> Tuple[bool, str]:
    """
    Register a new user account.
    
    Args:
        username: Desired username
        password: Password
        email: User's email
        full_name: User's full name
        
    Returns:
        Tuple of (success, message) where success is a boolean and message is feedback
    """
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "password": password,
                "email": email,
                "full_name": full_name,
                "role": "project_manager"  # Default role
            }
        )
        
        if response.status_code == 201:
            # Registration successful
            return True, "Registration successful!"
        else:
            # Registration failed
            error_msg = response.json().get("detail", "Registration failed")
            return False, f"Registration failed: {error_msg}"
    
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def logout() -> None:
    """
    Log out the current user by clearing session state.
    """
    # Clear auth-related session state
    if 'token' in st.session_state:
        del st.session_state.token
    
    if 'username' in st.session_state:
        del st.session_state.username
    
    # Clear chat history if exists
    if 'chat_history' in st.session_state:
        del st.session_state.chat_history
    
    # Reset current page to dashboard
    st.session_state.current_page = 'dashboard'

def check_auth() -> bool:
    """
    Check if user is authenticated.
    
    Returns:
        Boolean indicating if the user is authenticated
    """
    # Check if token exists in session state
    if 'token' not in st.session_state:
        return False
    
    # Optionally verify token validity with backend
    try:
        response = requests.get(
            f"{API_URL}/auth/verify",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return True
        else:
            # Token is invalid, clear it
            logout()
            return False
    
    except Exception:
        # If server is unreachable, assume token is valid to allow offline usage
        # This can be changed based on security requirements
        return True

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get current user details.
    
    Returns:
        Dictionary with user details or None if not logged in
    """
    if not check_auth():
        return None
    
    try:
        response = requests.get(
            f"{API_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    except Exception:
        return None