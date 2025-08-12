#!/usr/bin/env python3
"""
Quick deployment fix script for Academic Research Assistant
"""

import shutil
import os
from pathlib import Path

def fix_requirements():
    """Fix requirements.txt for deployment compatibility"""
    
    print("🔧 Fixing deployment requirements...")
    
    # Check which requirements files exist
    files = {
        'minimal': Path('requirements-minimal.txt'),
        'streamlit': Path('requirements-streamlit.txt'),
        'original': Path('requirements.txt')
    }
    
    print("\n📋 Available requirements files:")
    for name, path in files.items():
        status = "✅" if path.exists() else "❌"
        print(f"  {status} {name}: {path}")
    
    print("\n🎯 Deployment strategies:")
    print("1. Minimal (fastest, basic features)")
    print("2. Streamlit Cloud optimized")
    print("3. Keep current requirements")
    
    choice = input("\nChoose strategy (1-3): ").strip()
    
    if choice == "1" and files['minimal'].exists():
        shutil.copy(files['minimal'], files['original'])
        print("✅ Switched to minimal requirements")
        print("📝 Features available: Basic UI, Writing Assistant, Simple Reference Finder")
        print("⚠️  Limited: No advanced ML features, embeddings, or gap analysis")
        
    elif choice == "2" and files['streamlit'].exists():
        shutil.copy(files['streamlit'], files['original'])
        print("✅ Switched to Streamlit Cloud optimized requirements")
        print("📝 Features available: Most features with cloud-optimized dependencies")
        
    elif choice == "3":
        print("✅ Keeping current requirements")
        print("💡 If deployment fails, try option 1 or 2")
        
    else:
        print("❌ Invalid choice or file not found")
        return False
    
    return True

def create_runtime_file():
    """Create runtime.txt for Python version specification"""
    
    runtime_file = Path('runtime.txt')
    
    if runtime_file.exists():
        print(f"✅ runtime.txt already exists: {runtime_file.read_text().strip()}")
        return
    
    print("\n🐍 Python version options:")
    print("1. python-3.11 (recommended for compatibility)")
    print("2. python-3.10 (stable)")
    print("3. python-3.9 (most compatible)")
    print("4. Skip (use platform default)")
    
    choice = input("Choose Python version (1-4): ").strip()
    
    versions = {
        "1": "python-3.11",
        "2": "python-3.10", 
        "3": "python-3.9"
    }
    
    if choice in versions:
        runtime_file.write_text(versions[choice])
        print(f"✅ Created runtime.txt with {versions[choice]}")
    else:
        print("⏭️  Skipping runtime.txt creation")

def check_environment():
    """Check environment setup"""
    
    print("\n🔍 Checking environment...")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if API key is set
        try:
            with open(env_file) as f:
                content = f.read()
                if 'GEMINI_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
                    print("✅ API key appears to be configured")
                else:
                    print("⚠️  API key may not be configured properly")
        except:
            print("⚠️  Could not read .env file")
    else:
        print("❌ .env file missing")
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env from template")
            print("⚠️  Please edit .env and add your GEMINI_API_KEY")

def main():
    """Main deployment fix function"""
    
    print("🚀 Academic Research Assistant - Deployment Fix\n")
    
    # Fix requirements
    if not fix_requirements():
        return
    
    # Create runtime file
    create_runtime_file()
    
    # Check environment
    check_environment()
    
    print("\n🎉 Deployment fix complete!")
    print("\n📋 Next steps:")
    print("1. Commit your changes:")
    print("   git add .")
    print("   git commit -m 'Fix deployment requirements'")
    print("   git push")
    print("\n2. Redeploy your application")
    print("\n3. If issues persist, check DEPLOYMENT_TROUBLESHOOTING.md")

if __name__ == "__main__":
    main()
