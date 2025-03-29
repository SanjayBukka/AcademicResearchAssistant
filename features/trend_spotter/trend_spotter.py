import streamlit as st
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import Counter
import re

def fetch_recent_papers(query, limit=50):
    """Fetch recent papers from Semantic Scholar, sorted by year."""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,abstract,year',
        'sort': 'year:desc'
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        papers = response.json().get('data', [])
        return [(paper.get('title', '') + " " + paper.get('abstract', ''), paper.get('year', 'Unknown')) 
                for paper in papers if paper.get('abstract') and paper.get('year')]
    except Exception as e:
        st.error(f"Whoops, couldn’t fetch papers: {e}")
        return []

def spot_trends(papers):
    """Use SBERT and term frequency to find trending topics."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts, years = zip(*papers)
    embeddings = model.encode(texts, show_progress_bar=False)
    
    # Split recent (2023+) vs older (<2023)
    recent_texts = [text for text, year in papers if isinstance(year, int) and year >= 2023]
    older_texts = [text for text, year in papers if isinstance(year, int) and year < 2023]
    
    # Extract meaningful phrases (bigrams/trigrams) and filter stop words
    stop_words = {'in', 'the', 'and', 'of', 'to', 'a', 'that', 'is', 'for', 'on'}
    def get_phrases(text):
        words = re.findall(r'\w+', text.lower())
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1) if words[i] not in stop_words and words[i+1] not in stop_words]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2) if words[i] not in stop_words]
        return bigrams + trigrams
    
    recent_phrases = Counter(sum([get_phrases(text) for text in recent_texts], []))
    older_phrases = Counter(sum([get_phrases(text) for text in older_texts], []))
    
    # Hot: Top phrases in recent papers not dominant in older ones
    hot_terms = [phrase for phrase, count in recent_phrases.most_common(5) 
                 if phrase not in [p for p, _ in older_phrases.most_common(5)]][:3]
    # Cooling: Top phrases in older papers fading in recent ones
    cooling_terms = [phrase for phrase, count in older_phrases.most_common(5) 
                     if phrase not in [p for p, _ in recent_phrases.most_common(5)]][:3]
    
    return hot_terms, cooling_terms

def run_trend_spotter():
    st.subheader("📈 Research Trend Spotter")
    st.write("Let’s see what’s hot and what’s not in your research area!")
    
    topic = st.text_input("What’s your research topic?", "ai in health care")
    if st.button("Spot Trends"):
        with st.spinner("Scanning the research vibes..."):
            papers = fetch_recent_papers(topic)
            if not papers:
                st.warning("No recent papers found—try tweaking your topic!")
                return
            
            hot_terms, cooling_terms = spot_trends(papers)
            if hot_terms or cooling_terms:
                st.write("### Trend Report")
                if hot_terms:
                    st.write("**Heating Up:**")
                    for term in hot_terms:
                        st.write(f"- **{term}**: This is blowing up right now—everyone’s jumping on it!")
                        st.progress(0.8)
                if cooling_terms:
                    st.write("**Cooling Off:**")
                    for term in cooling_terms:
                        st.write(f"- **{term}**: Used to be the jam, but it’s fading fast.")
                        st.progress(0.2)
                st.write("So, you riding the hot wave or shaking up the old school?")
            else:
                st.write("Hmm, trends are hiding today. Try a broader topic maybe?")