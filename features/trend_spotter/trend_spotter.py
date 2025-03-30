import streamlit as st
import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import Counter
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import plotly.express as px
from wordcloud import WordCloud

# Set page configuration
st.set_page_config(
    page_title="Research Trend Spotter",
    page_icon="📈",
    layout="wide"
)

@st.cache_data(ttl=3600)
def fetch_recent_papers(query, limit=100, min_year=2018):
    """Fetch recent papers from Semantic Scholar with caching to avoid rate limits."""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        'query': query,
        'limit': limit,
        'fields': 'title,abstract,year,citationCount,authors,url',
        'sort': 'year:desc'
    }
    
    try:
        st.info(f"📚 Fetching papers about '{query}'...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        papers = response.json().get('data', [])
        
        # Filter and format papers
        filtered_papers = []
        for paper in papers:
            if paper.get('abstract') and paper.get('year') and isinstance(paper.get('year'), int) and paper.get('year') >= min_year:
                authors = paper.get('authors', [])
                author_names = ', '.join([a.get('name', '') for a in authors[:2]])
                if len(authors) > 2:
                    author_names += ' et al.'
                
                filtered_papers.append({
                    'title': paper.get('title', ''),
                    'abstract': paper.get('abstract', ''),
                    'year': paper.get('year', 'Unknown'),
                    'text': paper.get('title', '') + " " + paper.get('abstract', ''),
                    'citations': paper.get('citationCount', 0),
                    'authors': author_names,
                    'url': paper.get('url', '')
                })
        
        return filtered_papers
    except Exception as e:
        st.error(f"Couldn't fetch papers: {e}")
        return []

@st.cache_resource
def load_embedding_model():
    """Load and cache the embedding model to avoid reloading."""
    return SentenceTransformer('all-MiniLM-L6-v2')

def extract_key_phrases(text, n=2):
    """Extract important phrases from text using frequency analysis."""
    # Common stop words to filter out
    stop_words = {'in', 'the', 'and', 'of', 'to', 'a', 'that', 'is', 'for', 'on', 'with', 'as', 
                  'an', 'by', 'this', 'we', 'are', 'be', 'from', 'have', 'it', 'or', 'at', 'our',
                  'was', 'were', 'these', 'has', 'been', 'which', 'they', 'their', 'can', 'such'}
    
    # Extract single words, bigrams and trigrams
    words = re.findall(r'\w+', text.lower())
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1) 
              if words[i] not in stop_words and words[i+1] not in stop_words]
    
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2) 
               if words[i] not in stop_words and words[i+1] not in stop_words]
    
    # Count frequencies
    all_phrases = filtered_words + bigrams + trigrams
    phrase_counts = Counter(all_phrases)
    
    # Return top n phrases
    return phrase_counts.most_common(n)

def spot_trends(papers, current_year=2025, recent_threshold=2):
    """Analyze papers to identify trending and fading topics."""
    if not papers:
        return [], [], {}, {}
    
    # Group papers by year
    papers_by_year = {}
    for paper in papers:
        year = paper['year']
        if year not in papers_by_year:
            papers_by_year[year] = []
        papers_by_year[year].append(paper)
    
    # Define recent vs older papers
    recent_cutoff = current_year - recent_threshold
    recent_papers = [p for p in papers if p['year'] >= recent_cutoff]
    older_papers = [p for p in papers if p['year'] < recent_cutoff]
    
    # Extract and count phrases
    recent_text = ' '.join([p['text'] for p in recent_papers])
    older_text = ' '.join([p['text'] for p in older_papers])
    
    recent_phrases = extract_key_phrases(recent_text, 20)
    older_phrases = extract_key_phrases(older_text, 20)
    
    # Find trending phrases (high in recent, lower in older)
    recent_dict = dict(recent_phrases)
    older_dict = dict(older_phrases)
    
    trending_terms = []
    for phrase, count in recent_phrases:
        older_count = older_dict.get(phrase, 0)
        if older_count == 0 or count/len(recent_papers) > 1.5 * older_count/len(older_papers):
            trending_terms.append((phrase, count))
    
    # Find cooling phrases (high in older, lower in recent)
    cooling_terms = []
    for phrase, count in older_phrases:
        recent_count = recent_dict.get(phrase, 0)
        if recent_count == 0 or count/len(older_papers) > 1.5 * recent_count/len(recent_papers):
            cooling_terms.append((phrase, count))
    
    return trending_terms[:5], cooling_terms[:5], papers_by_year, recent_papers

def cluster_papers(papers, n_clusters=4):
    """Cluster papers based on their embeddings to identify research themes."""
    if len(papers) < n_clusters:
        return None, None, None
    
    model = load_embedding_model()
    texts = [p['text'] for p in papers]
    
    # Create embeddings
    embeddings = model.encode(texts, show_progress_bar=False)
    
    # Cluster embeddings
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(embeddings)
    
    # Dimensionality reduction for visualization
    tsne = TSNE(n_components=2, random_state=42)
    reduced_embeddings = tsne.fit_transform(embeddings)
    
    # Create dataframe with results
    df = pd.DataFrame({
        'title': [p['title'] for p in papers],
        'year': [p['year'] for p in papers],
        'x': reduced_embeddings[:, 0],
        'y': reduced_embeddings[:, 1],
        'cluster': clusters,
        'citations': [p.get('citations', 0) for p in papers]
    })
    
    # Identify cluster themes
    cluster_themes = {}
    for cluster_id in range(n_clusters):
        cluster_papers = [papers[i] for i in range(len(papers)) if clusters[i] == cluster_id]
        cluster_text = ' '.join([p['text'] for p in cluster_papers])
        top_terms = extract_key_phrases(cluster_text, 5)
        cluster_themes[cluster_id] = [term for term, _ in top_terms]
    
    return df, clusters, cluster_themes

def create_trend_chart(papers_by_year):
    """Create a chart showing paper publication trends over time."""
    if not papers_by_year:
        return None
    
    years = sorted(papers_by_year.keys())
    counts = [len(papers_by_year[year]) for year in years]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(years, counts, color='cornflowerblue')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of papers')
    ax.set_title('Research Volume Over Time')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    return fig

def create_wordcloud(text):
    """Generate a word cloud from text."""
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        contour_width=1,
        contour_color='steelblue'
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    
    return fig

def run_trend_spotter():
    st.title("📈 Research Trend Spotter")
    st.markdown("""
    Discover what's hot and what's cooling down in your research field.
    This tool analyzes recent papers to identify emerging trends and fading topics.
    """)
    
    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        topic = st.text_input("Research Topic", "ai in healthcare")
        paper_limit = st.slider("Number of papers to analyze", 50, 200, 100)
        min_year = st.slider("Minimum publication year", 2015, 2024, 2018)
        cluster_count = st.slider("Number of research clusters", 3, 8, 4)
        recent_years = st.slider("Recent years threshold", 1, 3, 2)
        
    # Main analysis
    if st.button("🔍 Spot Trends"):
        # Fetch and analyze papers
        papers = fetch_recent_papers(topic, limit=paper_limit, min_year=min_year)
        
        if not papers:
            st.warning("No papers found for this topic. Try adjusting your search terms.")
            return
        
        st.success(f"Found {len(papers)} papers about '{topic}'")
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Trend Report", "🔬 Research Clusters", "📚 Paper Explorer", "📝 Text Analysis"])
        
        trending_terms, cooling_terms, papers_by_year, recent_papers = spot_trends(
            papers, 
            current_year=2025, 
            recent_threshold=recent_years
        )
        
        # Tab 1: Trend Report
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Heating Up")
                if trending_terms:
                    for term, count in trending_terms:
                        st.markdown(f"**{term.title()}**")
                        st.progress(min(count / 10, 1.0))
                        st.caption(f"Mentioned in {count} recent papers")
                else:
                    st.info("No clear trending topics identified")
            
            with col2:
                st.subheader("❄️ Cooling Down")
                if cooling_terms:
                    for term, count in cooling_terms:
                        st.markdown(f"**{term.title()}**")
                        st.progress(min(count / 10, 0.5))
                        st.caption(f"Less prominent in recent research")
                else:
                    st.info("No clearly cooling topics identified")
            
            # Publication trend chart
            st.subheader("Publication Trend")
            trend_chart = create_trend_chart(papers_by_year)
            if trend_chart:
                st.pyplot(trend_chart)
        
        # Tab 2: Research Clusters
        with tab2:
            st.subheader("Research Theme Clusters")
            
            df, clusters, cluster_themes = cluster_papers(papers, n_clusters=cluster_count)
            
            if df is not None:
                # Create cluster visualization
                df['size'] = df['citations'].apply(lambda x: max(5, min(20, 5 + x/2)))
                df['hover_text'] = df.apply(lambda row: f"{row['title']} ({row['year']})", axis=1)
                
                fig = px.scatter(
                    df, x='x', y='y', 
                    color='cluster', 
                    size='size',
                    hover_name='hover_text',
                    color_continuous_scale=px.colors.qualitative.Bold,
                )
                
                fig.update_layout(
                    title="Research Paper Clusters",
                    xaxis_title="", yaxis_title="",
                    xaxis=dict(showticklabels=False),
                    yaxis=dict(showticklabels=False),
                    width=800, height=600
                )
                
                st.plotly_chart(fig)
                
                # Show cluster themes
                st.subheader("Cluster Themes")
                cols = st.columns(min(4, cluster_count))
                for i, (cluster_id, themes) in enumerate(cluster_themes.items()):
                    with cols[i % len(cols)]:
                        st.markdown(f"**Cluster {cluster_id+1}**")
                        for theme in themes:
                            st.markdown(f"• {theme}")
            else:
                st.info("Not enough papers for meaningful clustering")
        
        # Tab 3: Paper Explorer
        with tab3:
            st.subheader("Explore Papers")
            
            # Sort options
            sort_by = st.selectbox(
                "Sort by",
                options=["Year (newest first)", "Year (oldest first)", "Citations (highest first)"]
            )
            
            if sort_by == "Year (newest first)":
                sorted_papers = sorted(papers, key=lambda p: p.get('year', 0), reverse=True)
            elif sort_by == "Year (oldest first)":
                sorted_papers = sorted(papers, key=lambda p: p.get('year', 0))
            else:  # Citations
                sorted_papers = sorted(papers, key=lambda p: p.get('citations', 0), reverse=True)
            
            # Create paper list
            for paper in sorted_papers[:20]:  # Show top 20 papers
                with st.expander(f"{paper['title']} ({paper['year']})"):
                    st.markdown(f"**Authors:** {paper['authors']}")
                    if paper.get('citations') is not None:
                        st.markdown(f"**Citations:** {paper['citations']}")
                    st.markdown("**Abstract:**")
                    st.markdown(paper['abstract'])
                    if paper.get('url'):
                        st.markdown(f"[View Paper]({paper['url']})")
        
        # Tab 4: Text Analysis
        with tab4:
            # Word cloud from recent papers
            st.subheader("Word Cloud: Recent Research")
            recent_text = ' '.join([p['text'] for p in recent_papers])
            if recent_text:
                wordcloud_fig = create_wordcloud(recent_text)
                st.pyplot(wordcloud_fig)
            
            # Citation impact analysis
            st.subheader("Citation Impact by Year")
            if papers:
                citation_df = pd.DataFrame([
                    {'year': p['year'], 'citations': p.get('citations', 0)} 
                    for p in papers if p.get('citations') is not None
                ])
                
                if not citation_df.empty:
                    citation_summary = citation_df.groupby('year').agg(
                        mean_citations=('citations', 'mean'),
                        total_citations=('citations', 'sum'),
                        paper_count=('citations', 'count')
                    ).reset_index()
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    ax.bar(citation_summary['year'], citation_summary['mean_citations'], color='teal')
                    ax.set_xlabel('Year')
                    ax.set_ylabel('Average Citations')
                    ax.set_title('Citation Impact by Publication Year')
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    
                    st.pyplot(fig)
            else:
                st.info("Not enough citation data available")

