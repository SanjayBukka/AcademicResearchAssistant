#!/usr/bin/env python3
"""
Health check script for Academic Research Assistant
"""

import requests
import sys
import os
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

def check_health(url="http://localhost:8502"):
    """Check if the application is healthy"""
    try:
        # Check if the main page loads
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Application is healthy at {url}")
            print(f"📅 Checked at: {datetime.now()}")
            return True
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to application at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Application timeout at {url}")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Main health check function"""
    print("🏥 Academic Research Assistant - Health Check\n")
    
    # Check environment
    env_ok = check_environment()
    
    # Check application health
    url = os.environ.get('HEALTH_CHECK_URL', 'http://localhost:8502')
    app_ok = check_health(url)
    
    # Overall status
    if env_ok and app_ok:
        print("\n✅ Overall status: HEALTHY")
        return 0
    else:
        print("\n❌ Overall status: UNHEALTHY")
        return 1

if __name__ == "__main__":
    sys.exit(main())
