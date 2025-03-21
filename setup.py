"""
Setup script for the Project Risk Management System.
"""
from setuptools import setup, find_packages

setup(
    name="project_risk_management",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Backend dependencies
        "crewai>=0.1.32",
        "langchain>=0.0.267",
        "google-generativeai>=0.4.0",
        "supabase>=1.0.3",
        "chromadb>=0.4.6",
        "pandas>=1.5.3",
        "numpy>=1.24.3",
        "scikit-learn>=1.2.2",
        
        # Frontend dependencies
        "streamlit>=1.24.0",
        "plotly>=5.13.1",
        "altair>=5.0.1",
        
        # Utils
        "python-dotenv>=1.0.0",
        "pytest>=7.3.1",
        "requests>=2.31.0",
        "pydantic>=2.0.3"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered project risk management system",
    keywords="project management, risk assessment, AI",
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "prms=project_risk_management.backend.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)