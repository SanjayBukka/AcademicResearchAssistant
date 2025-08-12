"""
Streamlit Cloud Health Check
Verifies deployment readiness
"""

import streamlit as st
import sys
import importlib

def check_deployment_health():
    """Check if deployment is healthy"""
    st.title("🏥 Deployment Health Check")
    
    # Python version check
    st.subheader("🐍 Python Environment")
    st.write(f"Python Version: {sys.version}")
    
    # Package availability check
    st.subheader("📦 Package Availability")
    
    required_packages = [
        "streamlit",
        "requests", 
        "pandas",
        "numpy",
        "google.generativeai",
        "PyPDF2",
        "plotly",
        "PIL"
    ]
    
    optional_packages = [
        "sentence_transformers",
        "transformers", 
        "torch",
        "langchain",
        "faiss",
        "nltk"
    ]
    
    # Check required packages
    st.write("**Required Packages:**")
    for package in required_packages:
        try:
            importlib.import_module(package)
            st.success(f"✅ {package}")
        except ImportError:
            st.error(f"❌ {package} - MISSING")
    
    # Check optional packages
    st.write("**Optional Packages:**")
    for package in optional_packages:
        try:
            importlib.import_module(package)
            st.success(f"✅ {package}")
        except ImportError:
            st.warning(f"⚠️ {package} - Not available (features may be limited)")
    
    # Environment variables check
    st.subheader("🔑 Environment Variables")
    import os
    
    if os.getenv('GEMINI_API_KEY'):
        st.success("✅ GEMINI_API_KEY is set")
    else:
        st.error("❌ GEMINI_API_KEY is not set")
        st.info("Add your API key in Streamlit Cloud Secrets")
    
    # Feature availability
    st.subheader("🎯 Feature Availability")
    
    features = {
        "Reference Finder": True,
        "Writing Assistant": bool(os.getenv('GEMINI_API_KEY')),
        "Paper Summarizer": True,
        "Q&A Assistant": True,  # Simple version always available
        "Research Gap Analyzer": False  # Disabled for deployment
    }
    
    for feature, available in features.items():
        if available:
            st.success(f"✅ {feature}")
        else:
            st.warning(f"⚠️ {feature} - Limited/Disabled")

if __name__ == "__main__":
    check_deployment_health()
