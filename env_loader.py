"""
Simple environment variable loader for the Academic Research Assistant
"""

import os

def load_env_file(env_file='.env'):
    """Load environment variables from a .env file."""
    try:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
    except Exception as e:
        print(f"Warning: Could not load {env_file}: {e}")
    return False

def get_api_key():
    """Get the Gemini API key from environment variables."""
    # Try to load from .env file first
    load_env_file()
    
    # Get the API key
    api_key = os.getenv('GEMINI_API_KEY', '')
    return api_key

# Load environment variables when this module is imported
load_env_file()
