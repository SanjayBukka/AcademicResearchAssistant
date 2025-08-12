import streamlit as st
import os
from pathlib import Path
from features.references.reference_finder import run_references
from features.writing.writing_assistant import run_writing
from features.summarizer.paper_summarizer import run_summarization_tool
from features.gap_finder.gap_finder import run_gap_finder
from features.question.trend_spotter import run_research_assistant

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

# App-wide configuration
st.set_page_config(
    page_title="Academic Research Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for modern styling
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Animated gradient header */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        animation: gradientShift 4s ease-in-out infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        border-radius: 0 20px 20px 0;
    }

    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #ecf0f1;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }

    /* Enhanced feature cards */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.5s;
    }

    .feature-card:hover::before {
        left: 100%;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }

    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
        text-align: center;
    }

    .feature-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        text-align: center;
    }

    .feature-description {
        color: #5a6c7d;
        line-height: 1.6;
        text-align: center;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(45deg, #764ba2, #667eea);
    }

    /* Sidebar buttons */
    .css-1d391kg .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        color: #ecf0f1;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 0.5rem;
    }

    .css-1d391kg .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }

    /* Footer styling */
    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-top: 3rem;
        font-weight: 500;
    }

    /* Team info styling */
    .team-info {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        color: #ecf0f1;
    }

    /* Loading animations */
    .stSpinner > div {
        border-color: #667eea transparent #667eea transparent;
    }

    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #00b894, #00cec9);
        border-radius: 10px;
        color: white;
    }

    .stError {
        background: linear-gradient(135deg, #e17055, #d63031);
        border-radius: 10px;
        color: white;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .feature-card {
            padding: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for feature selection
if "current_feature" not in st.session_state:
    st.session_state.current_feature = "home"

# Enhanced Sidebar with modern navigation
st.sidebar.markdown('<div class="sidebar-header">🎓 Research Tools</div>', unsafe_allow_html=True)

# Navigation buttons with icons and descriptions
nav_items = [
    {"key": "home", "icon": "🏠", "title": "Home", "desc": "Dashboard"},
    {"key": "references", "icon": "🔍", "title": "Find References", "desc": "Discover papers"},
    {"key": "writing", "icon": "✍️", "title": "Writing Guide", "desc": "AI assistance"},
    {"key": "summarizer", "icon": "�", "title": "Summarizer", "desc": "Paper summaries"},
    {"key": "gap_finder", "icon": "🕳️", "title": "Gap Finder", "desc": "Research opportunities"},
    {"key": "trend_spotter", "icon": "💬", "title": "Q&A Assistant", "desc": "Clear doubts"}
]

for item in nav_items:
    if st.sidebar.button(f"{item['icon']} {item['title']}", key=f"nav_{item['key']}", help=item['desc']):
        st.session_state.current_feature = item['key']

# Quick stats section
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="team-info">
    <h4 style="margin-bottom: 1rem; color: #ecf0f1;">� Quick Stats</h4>
    <p style="margin-bottom: 0.5rem;">📄 Papers Analyzed: 10,000+</p>
    <p style="margin-bottom: 0.5rem;">� Research Areas: 50+</p>
    <p style="margin-bottom: 1rem;">� Active Users: 500+</p>
</div>
""", unsafe_allow_html=True)

# Performance indicator
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="team-info">
    <h4 style="color: #ecf0f1;">⚡ Performance</h4>
    <p style="font-size: 0.9rem;">Fast Mode Active</p>
    <div style="background: linear-gradient(90deg, #00b894, #00cec9); height: 4px; border-radius: 2px; margin-top: 0.5rem;"></div>
</div>
""", unsafe_allow_html=True)

# Main content area
# Home page
if st.session_state.current_feature == "home":
    # Hero section
    st.markdown('<div class="main-header">Academic Research Assistant</div>', unsafe_allow_html=True)

    # Welcome message with stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔍 Papers Searched", "10K+", "↗️ 15%")
    with col2:
        st.metric("✍️ Papers Written", "500+", "↗️ 8%")
    with col3:
        st.metric("📄 Summaries Generated", "2K+", "↗️ 12%")
    with col4:
        st.metric("🎯 Research Gaps Found", "300+", "↗️ 20%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards in a properly aligned grid
    st.markdown("### 🚀 Powerful Research Tools")

    # First row - 3 cards
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Smart Reference Finder</div>
                <div class="feature-description">
                    Discover relevant papers from arXiv, Semantic Scholar, and CrossRef.
                    Advanced AI-powered search with similarity scoring.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="feature-icon">✍️</div>
                <div class="feature-title">AI Writing Assistant</div>
                <div class="feature-description">
                    Get intelligent guidance for academic writing with Gemini AI.
                    Structure, style, and content suggestions.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="feature-icon">📄</div>
                <div class="feature-title">Paper Summarizer</div>
                <div class="feature-description">
                    Generate section-wise summaries of research papers.
                    Support for multiple sources and formats.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Second row - 3 cards
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="feature-icon">�️</div>
                <div class="feature-title">Research Gap Analyzer</div>
                <div class="feature-description">
                    Identify unexplored research opportunities using SciBERT embeddings
                    and advanced clustering algorithms.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div class="feature-icon">�</div>
                <div class="feature-title">Q&A Assistant</div>
                <div class="feature-description">
                    Upload papers and ask questions. Get contextual answers
                    powered by advanced RAG architecture.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Quick start card
        st.markdown("""
        <div class="feature-card" style="height: 280px; display: flex; flex-direction: column; justify-content: space-between; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div>
                <div class="feature-icon">🚀</div>
                <div class="feature-title" style="color: white;">Quick Start</div>
                <div class="feature-description" style="color: rgba(255,255,255,0.9);">
                    New to research? Start with our Reference Finder to discover
                    papers in your field!
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

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

elif st.session_state.current_feature == "summarizer":
    st.markdown('<div class="main-header">Paper Summarizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Generate section-wise summaries of research papers from arXiv, Semantic Scholar, Crossref, or upload your own PDFs. This tool breaks down papers into their component sections and provides concise summaries of each, making it easier to understand complex research quickly.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_summarization_tool()

elif st.session_state.current_feature == "gap_finder":
    st.markdown('<div class="main-header">Research Gap Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Discover unexplored areas in your field of research. This tool analyzes existing literature to identify potential research gaps that could be addressed in your work, helping you find novel research directions.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_gap_finder()

elif st.session_state.current_feature == "trend_spotter":
    st.markdown('<div class="main-header">Clear Doughts</div>', unsafe_allow_html=True)
    st.markdown('<div class="feature-description">', unsafe_allow_html=True)
    st.markdown("Stay updated with the latest trends and emerging topics in your research area. This tool helps you identify hot topics, growing research directions, and recent developments to keep your work relevant and cutting-edge.")
    st.markdown("</div>", unsafe_allow_html=True)
    run_research_assistant()

# # Enhanced Footer
# st.markdown("""
# <div class="footer">
#     <h3 style="margin-bottom: 1rem;">🎓 Academic Research Assistant</h3>
#     <p style="margin-bottom: 1rem;">Empowering researchers with AI-powered tools for academic excellence</p>
#     <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;">
#         <div>👨‍🏫 <strong>Mentor:</strong> Dr. Ajin R Nair</div>
#         <div>👥 <strong>Team:</strong> Sharan • Vatsav • Gayathri • Sanjay</div>
#     </div>
#     <p style="font-size: 0.9rem; opacity: 0.8;">Semester 6 Applicative Project | 2024-2025</p>
#     <div style="margin-top: 1rem;">
#         <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">🚀 Fast Mode</span>
#         <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">🤖 AI Powered</span>
#         <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0 0.5rem;">📚 Research Ready</span>
#     </div>
# </div>
# """, unsafe_allow_html=True)