import streamlit as st
import requests

st.title("AI-Powered Project Risk Management")

if st.button("Get Risk Report"):
    response = requests.get("http://127.0.0.1:8000/risk-report")
    st.write(response.json()["risk_report"])