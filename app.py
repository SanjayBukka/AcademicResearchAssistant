#!/usr/bin/env python3
"""
Production-ready entry point for Academic Research Assistant
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

# Set default environment variables for deployment
# Use PORT from environment (Heroku) or default to 8502
port = os.environ.get('PORT', '8502')
os.environ.setdefault('STREAMLIT_SERVER_PORT', port)
os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
os.environ.setdefault('STREAMLIT_SERVER_ENABLE_CORS', 'false')
os.environ.setdefault('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', 'false')

# Import and run the main application
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    
    # Set up streamlit arguments
    sys.argv = [
        "streamlit",
        "run",
        "main.py",
        "--server.port=" + os.environ.get('STREAMLIT_SERVER_PORT', '8502'),
        "--server.address=" + os.environ.get('STREAMLIT_SERVER_ADDRESS', '0.0.0.0'),
        "--server.headless=" + os.environ.get('STREAMLIT_SERVER_HEADLESS', 'true'),
        "--server.enableCORS=" + os.environ.get('STREAMLIT_SERVER_ENABLE_CORS', 'false'),
        "--server.enableXsrfProtection=" + os.environ.get('STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION', 'false')
    ]
    
    # Run streamlit
    stcli.main()
