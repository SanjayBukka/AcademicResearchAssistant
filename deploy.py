#!/usr/bin/env python3
"""
Deployment script for Academic Research Assistant
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = {
        'pip': 'pip --version',
        'git': 'git --version'
    }
    
    missing = []
    for dep, cmd in dependencies.items():
        try:
            subprocess.run(cmd.split(), capture_output=True, check=True)
            print(f"✅ {dep} is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {dep} is not available")
            missing.append(dep)
    
    return len(missing) == 0

def create_virtual_environment():
    """Create a virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_requirements():
    """Install Python requirements"""
    venv_python = "venv/Scripts/python" if os.name == 'nt' else "venv/bin/python"
    venv_pip = "venv/Scripts/pip" if os.name == 'nt' else "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([venv_pip, "install", "--upgrade", "pip"], check=True)
        print("✅ Pip upgraded")
        
        # Install requirements
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def setup_environment():
    """Setup environment file"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ .env file created from template")
        print("⚠️  Please edit .env file and add your GEMINI_API_KEY")
        return True
    else:
        print("❌ .env.example not found")
        return False

def run_application():
    """Run the application"""
    venv_python = "venv/Scripts/python" if os.name == 'nt' else "venv/bin/python"
    
    print("\n🚀 Starting Academic Research Assistant...")
    print("📝 The application will open in your browser")
    print("🔑 Make sure to add your GEMINI_API_KEY in the .env file")
    print("⏹️  Press Ctrl+C to stop the application\n")
    
    try:
        subprocess.run([
            venv_python, "-m", "streamlit", "run", "main.py",
            "--server.port=8502"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

def main():
    """Main deployment function"""
    print("🎓 Academic Research Assistant - Deployment Setup\n")
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        return False
    
    # Setup environment
    print("\n📦 Setting up environment...")
    if not create_virtual_environment():
        return False
    
    if not install_requirements():
        return False
    
    if not setup_environment():
        return False
    
    print("\n✅ Setup completed successfully!")
    
    # Ask if user wants to run the application
    response = input("\n🚀 Would you like to start the application now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        run_application()
    else:
        print("\n📋 To start the application later, run:")
        if os.name == 'nt':
            print("   venv\\Scripts\\python -m streamlit run main.py")
        else:
            print("   venv/bin/python -m streamlit run main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
