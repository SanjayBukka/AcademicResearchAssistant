import streamlit as st
from features.references.reference_finder import run_references
from features.writing.writing_assistant import run_writing
from features.chatbot.paper_chatbot import run_chatbot
from features.gap_finder.gap_finder import run_gap_finder
from features.trend_spotter.trend_spotter import run_trend_spotter

# App-wide configuration
st.set_page_config(page_title="Academic Research Assistant", page_icon="📚")

# Initialize session state for feature selection
if "current_feature" not in st.session_state:
    st.session_state.current_feature = "home"

# Home screen with buttons
def show_home():
    st.title("Welcome to Your Research Companion")
    st.write("Choose a feature to get started:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Finding References"):
            st.session_state.current_feature = "references"
        if st.button("🕳️ Research Gap Finder"):
            st.session_state.current_feature = "gap_finder"
    with col2:
        if st.button("✍️ Writing Guidance"):
            st.session_state.current_feature = "writing"
        if st.button("📈 Research Trend Spotter"):
            st.session_state.current_feature = "trend_spotter"
    with col3:
        if st.button("💬 Paper Chatbot"):
            st.session_state.current_feature = "chatbot"
    
    # Back to home button (appears on all feature pages)
    if st.session_state.current_feature != "home":
        if st.button("🏠 Back to Home"):
            st.session_state.current_feature = "home"

# Feature routing
if st.session_state.current_feature == "home":
    show_home()
elif st.session_state.current_feature == "references":
    show_home()
    run_references()
elif st.session_state.current_feature == "writing":
    show_home()
    run_writing()
elif st.session_state.current_feature == "chatbot":
    show_home()
    run_chatbot()
elif st.session_state.current_feature == "gap_finder":
    show_home()
    run_gap_finder()
elif st.session_state.current_feature == "trend_spotter":
    show_home()
    run_trend_spotter()

# Footer
st.write("---")
st.write("Built by Ashok | March 2025")