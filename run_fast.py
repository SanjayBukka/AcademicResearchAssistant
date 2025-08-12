"""
Fast startup script for Academic Research Assistant
This script optimizes the application for faster loading
"""

import os
import sys
import streamlit as st

# Set environment variables for faster startup
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Avoid tokenizer warnings
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'  # Disable symlink warnings

# Configure Streamlit for better performance
st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add performance tips
st.sidebar.markdown("""
### ⚡ Performance Tips
- **Fast Mode**: Uses lightweight models (~90MB)
- **First Load**: May take 1-2 minutes to download models
- **Subsequent Loads**: Much faster due to caching
- **Tip**: Keep the app running to avoid reloading
""")

# Import and run main app
if __name__ == "__main__":
    from main import *
