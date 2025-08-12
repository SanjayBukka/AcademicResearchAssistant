"""
Status check script for Academic Research Assistant
"""

import sys
import os

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        from features.question.trend_spotter import run_research_assistant
        print("✅ Q&A module imported successfully")
    except ImportError as e:
        print(f"❌ Q&A module import failed: {e}")
        return False
    
    try:
        from features.writing.writing_assistant import run_writing
        print("✅ Writing assistant imported successfully")
    except ImportError as e:
        print(f"❌ Writing assistant import failed: {e}")
        return False
    
    try:
        from features.references.reference_finder import run_references
        print("✅ Reference finder imported successfully")
    except ImportError as e:
        print(f"❌ Reference finder import failed: {e}")
        return False
    
    try:
        from features.summarizer.paper_summarizer import run_summarization_tool
        print("✅ Paper summarizer imported successfully")
    except ImportError as e:
        print(f"❌ Paper summarizer import failed: {e}")
        return False
    
    try:
        from features.gap_finder.gap_finder import run_gap_finder
        print("✅ Gap finder imported successfully")
    except ImportError as e:
        print(f"❌ Gap finder import failed: {e}")
        return False
    
    return True

def check_api_key():
    """Check if API key is available."""
    print("\n🔑 Checking API key...")
    
    try:
        from env_loader import get_api_key
        api_key = get_api_key()
        if api_key:
            print("✅ Gemini API key found in environment")
            return True
        else:
            print("⚠️ No Gemini API key found in environment")
            print("💡 You can set it in the .env file or enter it in the app")
            return True  # Not a critical error
    except Exception as e:
        print(f"⚠️ Could not check API key: {e}")
        return True  # Not a critical error

def main():
    """Run all status checks."""
    print("🚀 Academic Research Assistant - Status Check")
    print("=" * 50)
    
    all_good = True
    
    # Check imports
    if not check_imports():
        all_good = False
    
    # Check API key
    check_api_key()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ All systems ready! You can run the application with:")
        print("   streamlit run main.py")
        print("   or")
        print("   streamlit run run_fast.py  (for faster startup)")
    else:
        print("❌ Some issues found. Please check the errors above.")
    
    return all_good

if __name__ == "__main__":
    main()
