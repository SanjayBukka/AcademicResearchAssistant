import streamlit as st
import requests
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
import numpy as np
import re

def fetch_papers(query, limit=50):
    """Fetch papers from Semantic Scholar, arXiv, and CrossRef."""
    papers = []
    limit_per_source = limit // 3
    
    # Semantic Scholar
    ss_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    ss_params = {'query': query, 'limit': limit_per_source, 'fields': 'title,abstract'}
    try:
        response = requests.get(ss_url, params=ss_params)
        papers.extend([(p.get('abstract', ''), 'Semantic Scholar') for p in response.json().get('data', []) if p.get('abstract')])
    except:
        st.warning("Semantic Scholar’s acting up—moving on!")
    
    # arXiv
    arxiv_url = "http://export.arxiv.org/api/query"
    arxiv_params = {'search_query': f'all:{query}', 'max_results': limit_per_source}
    try:
        response = requests.get(arxiv_url, params=arxiv_params)
        root = ET.fromstring(response.text)
        entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        papers.extend([(entry.findtext('{http://www.w3.org/2005/Atom}summary', ''), 'arXiv') 
                       for entry in entries if entry.findtext('{http://www.w3.org/2005/Atom}summary')])
    except:
        st.warning("arXiv’s being shy—skipping it!")
    
    # CrossRef
    cr_url = "https://api.crossref.org/works"
    cr_params = {'query': query, 'rows': limit_per_source}
    try:
        response = requests.get(cr_url, params=cr_params)
        items = response.json().get('message', {}).get('items', [])
        abstracts = [re.sub(r'jats:p|<[^>]+>', '', item.get('abstract', '')) if item.get('abstract') else '' 
                     for item in items]
        papers.extend([(abstract, 'CrossRef') for abstract in abstracts if abstract])
    except:
        st.warning("CrossRef’s out—sticking with what we’ve got!")
    
    return papers[:limit]

def find_gaps(topic, papers):
    """Use SBERT to find research gaps."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    abstracts, sources = zip(*papers)
    embeddings = model.encode(abstracts, show_progress_bar=False)
    
    field_center = np.mean(embeddings, axis=0)
    similarities = np.dot(embeddings, field_center) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(field_center)
    )
    
    outlier_indices = [i for i, s in enumerate(similarities) if s < 0.75][:3]
    if not outlier_indices:
        outlier_indices = similarities.argsort()[:3]
    gap_data = [(abstracts[i], sources[i], similarities[i]) for i in outlier_indices]
    
    return gap_data

def suggest_gap_idea(abstract, topic):
    """Generate specific, relevant gap ideas."""
    abstract_lower = abstract.lower()
    if "financial" in abstract_lower or "trading" in abstract_lower:
        return "What if you mixed healthcare AI governance with financial market lessons? Cross-sector trust rules could be a game-changer!"
    elif "human oversight" in abstract_lower or "decision-making" in abstract_lower:
        return "How about zooming into human-AI team-ups in healthcare regs? Everyone’s on systems, but who’s nailing the human bit?"
    elif "telecommunications" in abstract_lower or "policy" in abstract_lower:
        return "Yo, what if you pulled telecom policy tricks into healthcare AI? Cross-jurisdiction bandwidth for rules—untapped gold!"
    else:
        return f"How about a fresh spin on {topic.split(':')[0]}? This one’s off the radar—could be your big win!"

def run_gap_finder():
    st.subheader("🕳️ Research Gap Finder")
    st.write("Let’s hunt down some fresh angles in your research field!")
    
    topic = st.text_input("What’s your research topic?", "Global AI Governance in Healthcare: A Cross-Jurisdictional Regulatory Analysis")
    if st.button("Find Gaps"):
        with st.spinner("Scouring the lit for hidden gems..."):
            papers = fetch_papers(topic)
            if not papers:
                st.warning("No papers found—try a shorter topic or check your connection!")
                return
            
            gaps = find_gaps(topic, papers)
            if gaps:
                st.write("### Hot Research Gaps to Explore")
                for i, (abstract, source, score) in enumerate(gaps, 1):
                    st.write(f"**Gap {i} (from {source}):**")
                    st.write(f"- **Snippet**: {abstract[:300]}...")
                    st.write(f"- **Why**: Stands out from the crowd (score: {score:.2f}).")
                    st.write(f"- **Idea**: {suggest_gap_idea(abstract, topic)}")
                    st.write("---")
                st.write("Dude, these are your golden tickets! Which one’s got you hyped?")
            else:
                st.write("Hmm, no juicy gaps this time. Try a broader topic or hit it again!")