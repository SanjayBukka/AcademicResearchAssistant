import streamlit as st
from features.references.reference_finder import run_references
from features.writing.writing_assistant import run_writing
from features.chatbot.paper_chatbot import run_chatbot
from features.gap_finder.gap_finder import run_gap_finder
from features.trend_spotter.trend_spotter import run_trend_spotter

# App-wide configuration
st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .feature-description {
        padding: 1rem;
        background-color: #f5f7f9;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .footer {
        text-align: center;
        padding: 1rem;
        font-size: 0.8rem;
        color: #9e9e9e;
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for feature selection
if "current_feature" not in st.session_state:
    st.session_state.current_feature = "home"

# Sidebar with navigation buttons
st.sidebar.markdown('<div class="sidebar-header">Research Tools</div>', unsafe_allow_html=True)

if st.sidebar.button("🏠 Home"):
    st.session_state.current_feature = "home"
    
if st.sidebar.button("🔍 Finding References"):
    st.session_state.current_feature = "references"
    
if st.sidebar.button("✍️ Writing Guidance"):
    st.session_state.current_feature = "writing"
    
if st.sidebar.button("💬 Paper Chatbot"):
    st.session_state.current_feature = "chatbot"
    
if st.sidebar.button("🕳️ Research Gap Finder"):
    st.session_state.current_feature = "gap_finder"
    
if st.sidebar.button("📈 Research Trend Spotter"):
    st.session_state.current_feature = "trend_spotter"

# Team information in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Team Members")
st.sidebar.markdown("Sharan • Vatsav • Gayathri • Sanjay ")
st.sidebar.markdown("Semester 6 Applicative Project")

st.sidebar.markdown("---")

# Main content area
# Home page
if st.session_state.current_feature == "home":
    st.markdown('<div class="main-header">Academic Research Assistant</div>', unsafe_allow_html=True)
    st.write("Welcome to your research companion. Select a tool from the sidebar to get started.")
    
    st.markdown("### Available Features:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-description">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Finding References")
        st.markdown("Discover relevant papers and sources for your research topic.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="feature-description">', unsafe_allow_html=True)
        st.markdown("#### ✍️ Writing Guidance")
        st.markdown("Get assistance with academic writing and paper structure.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="feature-description">', unsafe_allow_html=True)
        st.markdown("#### 💬 Paper Chatbot")
        st.markdown("Have conversations about academic papers and get insights.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-description">', unsafe_allow_html=True)
        st.markdown("#### 🕳️ Research Gap Finder")
        st.markdown("Identify unexplored areas and opportunities in your field.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="feature-description">', unsafe_allow_html=True)
        st.markdown("#### 📈 Research Trend Spotter")
        st.markdown("Stay updated with emerging trends in your research area.")
        st.markdown("</div>", unsafe_allow_html=True)

# Feature pages
elif st.session_state.current_feature == "references":
    st.markdown('<div class="main-header">Finding References</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("This tool helps you find relevant academic papers, articles, and citations for your research topic. Simply enter your research area or specific keywords to discover sources that will enrich your work.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_references()

elif st.session_state.current_feature == "writing":
    st.markdown('<div class="main-header">Writing Guidance</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Get assistance with academic writing, including paper structure, language improvement, citation formatting, and more. This tool can help you refine your academic writing and ensure it meets scholarly standards.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_writing()

elif st.session_state.current_feature == "chatbot":
    st.markdown('<div class="main-header">Paper Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Have interactive conversations about academic papers to better understand complex concepts. Upload a paper or provide its details, and the chatbot will help you analyze and discuss its content.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_chatbot()

elif st.session_state.current_feature == "gap_finder":
    st.markdown('<div class="main-header">Research Gap Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Discover unexplored areas in your field of research. This tool analyzes existing literature to identify potential research gaps that could be addressed in your work, helping you find novel research directions.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_gap_finder()

elif st.session_state.current_feature == "trend_spotter":
    st.markdown('<div class="main-header">Research Trend Spotter</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Stay updated with the latest trends and emerging topics in your research area. This tool helps you identify hot topics, growing research directions, and recent developments to keep your work relevant and cutting-edge.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_trend_spotter()

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        Academic Research Assistant | Developed by Team: Sharan, Vatsav, Gayathri, and Sanjay | April 2025
    </div>
""", unsafe_allow_html=True)