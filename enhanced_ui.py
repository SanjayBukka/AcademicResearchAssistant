"""
Enhanced UI components for Academic Research Assistant
"""

import streamlit as st

def apply_enhanced_styling():
    """Apply enhanced CSS styling for better UI components"""
    st.markdown("""
    <style>
    /* Enhanced input fields */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
        transform: translateY(-2px);
    }
    
    /* Enhanced selectbox */
    .stSelectbox > div > div > select {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* Enhanced file uploader */
    .stFileUploader > div {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        transform: translateY(-2px);
    }
    
    /* Enhanced metrics */
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Enhanced progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Enhanced expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 10px;
        border: 1px solid #e9ecef;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Enhanced tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 15px;
        padding: 1rem 2rem;
        border: 2px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Enhanced columns */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Paper cards */
    .paper-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .paper-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .paper-card:hover::before {
        left: 100%;
    }
    
    .paper-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    }
    
    .paper-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
    
    .paper-authors {
        color: #667eea;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .paper-abstract {
        color: #5a6c7d;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .paper-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
        color: #6c757d;
    }
    
    /* Loading animations */
    .loading-container {
        text-align: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-success {
        background: linear-gradient(135deg, #00b894, #00cec9);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
    }
    
    .status-info {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def create_paper_card(paper, index):
    """Create an enhanced paper card with modern styling"""
    return f"""
    <div class="paper-card">
        <div class="paper-title">{paper.get('title', 'No title')}</div>
        <div class="paper-authors">👥 {', '.join(paper.get('authors', ['Unknown']))}</div>
        <div class="paper-abstract">{paper.get('abstract', 'No abstract available')[:300]}...</div>
        <div class="paper-meta">
            <span>📅 {paper.get('year', 'Unknown')}</span>
            <span>📊 Score: {paper.get('similarity', 0):.2f}</span>
            <span>🔗 {paper.get('source', 'Unknown')}</span>
        </div>
    </div>
    """

def create_metric_card(title, value, delta=None, icon="📊"):
    """Create an enhanced metric card"""
    delta_html = f"<div style='color: #00b894; font-size: 0.9rem;'>{delta}</div>" if delta else ""
    return f"""
    <div class="metric-container">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: 600; color: #2c3e50;">{value}</div>
        <div style="color: #6c757d; margin-bottom: 0.5rem;">{title}</div>
        {delta_html}
    </div>
    """

def create_status_badge(text, status_type="info"):
    """Create a status badge"""
    return f'<span class="status-badge status-{status_type}">{text}</span>'

def show_loading_animation(text="Loading..."):
    """Show a loading animation"""
    return f"""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <p>{text}</p>
    </div>
    """
