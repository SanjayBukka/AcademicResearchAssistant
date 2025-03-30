import streamlit as st
import requests
import xml.etree.ElementTree as ET
from sentence_transformers import SentenceTransformer
import numpy as np
import re
import pandas as pd
import plotly.express as px
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import time

# Download NLTK resources - wrapped in try/except to handle cases where they're already downloaded
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

def fetch_papers(query, limit=75):
    """Fetch papers from Semantic Scholar, arXiv, and CrossRef with improved error handling."""
    papers = []
    limit_per_source = limit // 3
    
    # Progress bar for paper fetching
    paper_progress = st.progress(0)
    progress_text = st.empty()
    progress_text.text("Fetching papers from multiple sources...")
    
    # Semantic Scholar
    ss_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    ss_params = {'query': query, 'limit': limit_per_source, 'fields': 'title,abstract,year,authors'}
    try:
        response = requests.get(ss_url, params=ss_params, timeout=10)
        if response.status_code == 200:
            data = response.json().get('data', [])
            for p in data:
                if p.get('abstract'):
                    title = p.get('title', 'Untitled')
                    abstract = p.get('abstract', '')
                    year = p.get('year', 'Unknown')
                    authors = ", ".join([a.get('name', '') for a in p.get('authors', [])[:3]])
                    if len(p.get('authors', [])) > 3:
                        authors += " et al."
                    papers.append({
                        'title': title,
                        'abstract': abstract,
                        'source': 'Semantic Scholar', 
                        'year': year,
                        'authors': authors
                    })
        else:
            st.warning(f"Semantic Scholar returned status code {response.status_code}")
    except Exception as e:
        st.warning(f"Semantic Scholar's acting up—moving on! Error: {str(e)}")
    
    paper_progress.progress(33)
    progress_text.text("Fetching papers from arXiv...")
    
    # arXiv
    arxiv_url = "http://export.arxiv.org/api/query"
    arxiv_params = {'search_query': f'all:{query}', 'max_results': limit_per_source}
    try:
        response = requests.get(arxiv_url, params=arxiv_params, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            for entry in entries:
                abstract = entry.findtext('{http://www.w3.org/2005/Atom}summary', '')
                if abstract:
                    title = entry.findtext('{http://www.w3.org/2005/Atom}title', 'Untitled')
                    published = entry.findtext('{http://www.w3.org/2005/Atom}published', '')
                    year = published[:4] if published else 'Unknown'
                    authors = ", ".join([author.findtext('{http://www.w3.org/2005/Atom}name', '') 
                                       for author in entry.findall('.//{http://www.w3.org/2005/Atom}author')[:3]])
                    if len(entry.findall('.//{http://www.w3.org/2005/Atom}author')) > 3:
                        authors += " et al."
                    papers.append({
                        'title': title,
                        'abstract': abstract,
                        'source': 'arXiv',
                        'year': year,
                        'authors': authors
                    })
        else:
            st.warning(f"arXiv returned status code {response.status_code}")
    except Exception as e:
        st.warning(f"arXiv's being shy—skipping it! Error: {str(e)}")
    
    paper_progress.progress(66)
    progress_text.text("Fetching papers from CrossRef...")
    
    # CrossRef
    cr_url = "https://api.crossref.org/works"
    cr_params = {'query': query, 'rows': limit_per_source}
    try:
        response = requests.get(cr_url, params=cr_params, timeout=10)
        if response.status_code == 200:
            items = response.json().get('message', {}).get('items', [])
            for item in items:
                abstract = re.sub(r'jats:p|<[^>]+>', '', item.get('abstract', '')) if item.get('abstract') else ''
                if abstract:
                    title = item.get('title', ['Untitled'])[0] if isinstance(item.get('title', []), list) else 'Untitled'
                    year = item.get('published-print', {}).get('date-parts', [['']])[0][0]
                    if not year:
                        year = item.get('published-online', {}).get('date-parts', [['']])[0][0]
                    year = year or 'Unknown'
                    
                    authors_list = item.get('author', [])
                    authors = ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in authors_list[:3]])
                    if len(authors_list) > 3:
                        authors += " et al."
                        
                    papers.append({
                        'title': title,
                        'abstract': abstract,
                        'source': 'CrossRef',
                        'year': year,
                        'authors': authors
                    })
        else:
            st.warning(f"CrossRef returned status code {response.status_code}")
    except Exception as e:
        st.warning(f"CrossRef's out—sticking with what we've got! Error: {str(e)}")
    
    paper_progress.progress(100)
    progress_text.empty()
    paper_progress.empty()
    
    return papers[:limit]

def extract_keywords(abstracts, top_n=20):
    """Extract the most common keywords from abstracts."""
    stop_words = set(stopwords.words('english'))
    
    # Additional research-specific stopwords
    research_stopwords = {'research', 'study', 'paper', 'analysis', 'data', 'method', 
                         'results', 'finding', 'findings', 'approach', 'using', 'used', 
                         'propose', 'proposed', 'show', 'shows', 'shown', 'result'}
    stop_words.update(research_stopwords)
    
    all_words = []
    for abstract in abstracts:
        words = word_tokenize(abstract.lower())
        # Only keep alphanumeric words with length > 3 that aren't stopwords
        words = [word for word in words if word.isalnum() and len(word) > 3 and word not in stop_words]
        all_words.extend(words)
    
    # Count word frequencies
    word_counts = Counter(all_words)
    
    # Return top N keywords
    return word_counts.most_common(top_n)

def simple_dimensionality_reduction(embeddings, n_components=2):
    """A simple PCA implementation without using sklearn."""
    # Center the data
    mean = np.mean(embeddings, axis=0)
    centered_data = embeddings - mean
    
    # Compute covariance matrix
    cov_matrix = np.cov(centered_data, rowvar=False)
    
    # Compute eigenvalues and eigenvectors
    eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
    
    # Sort eigenvectors by eigenvalues in descending order
    idx = eigenvalues.argsort()[::-1]
    eigenvectors = eigenvectors[:, idx]
    
    # Take the first n_components eigenvectors
    principal_components = eigenvectors[:, :n_components]
    
    # Project the data
    projected_data = np.dot(centered_data, principal_components)
    
    return projected_data

def find_gaps(papers, similarity_threshold=0.75, visualization=True):
    """Use SBERT to find research gaps with visualizations."""
    if not papers:
        return [], None
    
    with st.spinner("Analyzing paper embeddings..."):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        abstracts = [p['abstract'] for p in papers]
        
        # Generate embeddings
        embeddings = model.encode(abstracts, show_progress_bar=False)
        
        # Find the center of the field
        field_center = np.mean(embeddings, axis=0)
        
        # Calculate similarities to the center
        similarities = np.dot(embeddings, field_center) / (
            np.linalg.norm(embeddings, axis=1) * np.linalg.norm(field_center)
        )
        
        # Find outliers
        outlier_indices = [i for i, s in enumerate(similarities) if s < similarity_threshold]
        
        # If no clear outliers, take the most dissimilar papers
        if len(outlier_indices) < 3:
            outlier_indices = similarities.argsort()[:5]
        
        # Add similarity scores to papers
        for i, paper in enumerate(papers):
            paper['similarity'] = float(similarities[i])
        
        # Prepare gap data
        gap_data = [papers[i] for i in outlier_indices]
        
        # Create visualization if requested
        viz_fig = None
        if visualization and len(embeddings) > 5:
            # Use our simple PCA function instead of sklearn's
            reduced_embeddings = simple_dimensionality_reduction(embeddings, n_components=2)
            
            # Create dataframe for plotting
            df = pd.DataFrame({
                'x': reduced_embeddings[:, 0],
                'y': reduced_embeddings[:, 1],
                'title': [p['title'] for p in papers],
                'source': [p['source'] for p in papers],
                'year': [p['year'] for p in papers],
                'similarity': similarities,
                'is_gap': [i in outlier_indices for i in range(len(papers))]
            })
            
            # Create interactive scatter plot
            viz_fig = px.scatter(
                df, x='x', y='y', 
                color='similarity', size=(1-df['similarity'])*10+5,
                hover_data=['title', 'source', 'year'],
                labels={'similarity': 'Similarity to field center'},
                color_continuous_scale='Viridis',
                title='Research Landscape: Potential Gaps in Dark Blue'
            )
            
            # Highlight potential gap papers
            gap_df = df[df['is_gap']]
            gap_trace = px.scatter(
                gap_df, x='x', y='y',
                text=[f"Gap {i+1}" for i in range(len(gap_df))],
                color_discrete_sequence=['red']
            ).data[0]
            
            viz_fig.add_trace(gap_trace)
            viz_fig.update_traces(marker=dict(line=dict(width=2, color='DarkRed')),
                                 selector=dict(mode='markers+text'))
            
            # Improve layout
            viz_fig.update_layout(
                height=500,
                legend_title_text='Paper Data',
                xaxis_title="First Principal Component",
                yaxis_title="Second Principal Component"
            )
        
        return gap_data, viz_fig

def analyze_keyword_coverage(papers, gap_papers):
    """Analyze keyword coverage to find potential research gaps."""
    all_abstracts = [p['abstract'] for p in papers]
    gap_abstracts = [p['abstract'] for p in gap_papers]
    
    # Extract keywords from all papers and gap papers
    all_keywords = dict(extract_keywords(all_abstracts, top_n=50))
    gap_keywords = dict(extract_keywords(gap_abstracts, top_n=30))
    
    # Find keywords that are more prominent in gap papers (potential new directions)
    keyword_opportunities = {}
    for keyword, count in gap_keywords.items():
        if keyword in all_keywords:
            # Calculate relative frequency in gap papers vs all papers
            gap_frequency = count / len(gap_abstracts)
            all_frequency = all_keywords[keyword] / len(all_abstracts)
            
            # If keyword is more common in gap papers, it might represent an opportunity
            if gap_frequency > all_frequency * 1.5:
                keyword_opportunities[keyword] = gap_frequency / all_frequency
        else:
            # Keywords unique to gap papers are very interesting
            keyword_opportunities[keyword] = 5.0  # Arbitrary high score
    
    # Sort keywords by opportunity score
    sorted_opportunities = sorted(keyword_opportunities.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_opportunities[:10]  # Return top 10 opportunity keywords

def suggest_gap_idea(paper, topic, opportunity_keywords):
    """Generate specific, relevant gap ideas based on the paper and trending keywords."""
    abstract = paper['abstract'].lower()
    title = paper['title'].lower()
    
    # Combine ideas based on paper content and opportunity keywords
    ideas = []
    
    # Check for specific domains in the abstract
    if any(kw in abstract or kw in title for kw in ['financial', 'trading', 'economic', 'market']):
        ideas.append("Consider combining healthcare AI governance frameworks with financial regulatory models. Cross-sector governance principles could address similar trust and transparency challenges.")
    
    if any(kw in abstract or kw in title for kw in ['human', 'oversight', 'decision', 'ethical', 'ethics']):
        ideas.append("Explore the human-AI collaboration aspects in healthcare regulatory frameworks. Most research focuses on systems, but the human-in-the-loop governance needs deeper investigation.")
    
    if any(kw in abstract or kw in title for kw in ['policy', 'regulation', 'compliance', 'standard']):
        ideas.append("Investigate how different jurisdictional approaches to AI governance could be harmonized into a cross-border regulatory framework specifically for healthcare applications.")
    
    if any(kw in abstract or kw in title for kw in ['data', 'privacy', 'security', 'confidential']):
        ideas.append("Research the tension between data sharing requirements for AI development and privacy regulations across different healthcare systems and jurisdictions.")
    
    # Add ideas based on opportunity keywords
    if opportunity_keywords:
        keyword_idea = f"Consider exploring the intersection of {topic.split(':')[0]} with {', '.join([k for k, _ in opportunity_keywords[:3]])}. These emerging keywords appear in outlier papers but aren't mainstream yet."
        ideas.append(keyword_idea)
    
    # If no specific ideas were generated, provide a general suggestion
    if not ideas:
        ideas.append(f"This paper's approach differs from mainstream research on {topic.split(':')[0]}. Consider how its methodologies could be applied to solve current challenges in the field.")
    
    # Return the most relevant idea or combine multiple if needed
    if len(ideas) == 1:
        return ideas[0]
    else:
        return ideas[0] + "\n\n" + "Alternative approach: " + ideas[1]

def run_gap_finder():
    st.title("🕳️ Advanced Research Gap Finder")
    st.write("Discover untapped research opportunities and emerging trends in your field")
    
    # Sidebar for advanced options
    with st.sidebar:
        st.header("Advanced Options")
        similarity_threshold = st.slider("Similarity Threshold", 0.5, 0.9, 0.75, 0.05, 
                                       help="Lower values find more radical gaps, higher values find subtle variations")
        paper_limit = st.slider("Number of Papers to Analyze", 20, 100, 75, 5,
                              help="More papers provide better analysis but take longer")
        show_visualization = st.checkbox("Show Research Landscape Visualization", True,
                                       help="Visual representation of the research field and potential gaps")
        st.divider()
        st.markdown("### About This Tool")
        st.markdown("""
        This tool uses NLP and embedding analysis to identify potential research gaps by finding papers that stand out from the mainstream.
        
        It works by:
        1. Collecting papers from multiple academic sources
        2. Creating vector embeddings using SBERT
        3. Identifying outlier papers that differ from the field center
        4. Analyzing keyword trends and suggesting research directions
        """)
    
    # Main input area
    topic = st.text_input("Research Topic", 
                          "Global AI Governance in Healthcare: A Cross-Jurisdictional Regulatory Analysis",
                          help="Enter a specific research topic to find gaps")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_button = st.button("Find Research Gaps", type="primary", use_container_width=True)
    with col2:
        advanced_mode = st.checkbox("Advanced Analysis", True)
    
    if search_button:
        # Step 1: Fetch papers
        with st.spinner("Searching for papers..."):
            papers = fetch_papers(topic, limit=paper_limit)
            
            if not papers:
                st.error("No papers found. Try a broader topic or check your internet connection.")
                return
            
            st.success(f"Found {len(papers)} papers related to your topic")
        
        # Step 2: Analyze gaps
        gaps, viz_fig = find_gaps(papers, similarity_threshold, show_visualization)
        
        # Show visualization if available
        if viz_fig and show_visualization:
            st.plotly_chart(viz_fig, use_container_width=True)
            st.caption("Papers further from the center (darker blue) represent potential research gaps")
        
        # Step 3: Advanced keyword analysis
        if advanced_mode:
            opportunity_keywords = analyze_keyword_coverage(papers, gaps)
            
            # Show keyword opportunities
            st.subheader("🔍 Emerging Research Keywords")
            keyword_df = pd.DataFrame(opportunity_keywords, columns=["Keyword", "Opportunity Score"])
            keyword_df["Opportunity Score"] = keyword_df["Opportunity Score"].round(2)
            
            # Create horizontal bar chart for keywords
            keyword_fig = px.bar(
                keyword_df, 
                y="Keyword", 
                x="Opportunity Score", 
                orientation='h',
                title="Keywords More Common in Gap Papers",
                color="Opportunity Score",
                color_continuous_scale="Viridis",
            )
            
            st.plotly_chart(keyword_fig, use_container_width=True)
        else:
            opportunity_keywords = []
        
        # Step 4: Display gap opportunities
        st.subheader("🌟 High-Potential Research Gap Opportunities")
        st.write("These papers stand out from the mainstream literature and may indicate research gaps")
        
        with st.expander("What makes these good gap opportunities?", expanded=False):
            st.markdown("""
            Papers are ranked as potential gap opportunities when they:
            - Differ significantly from the central themes in the field
            - Use unusual approaches or methodologies
            - Address similar problems from different angles
            - Contain keywords that aren't common in the mainstream literature
            
            Not every outlier represents a viable research gap, but they often point to fruitful directions for original research.
            """)
        
        # Display gap papers in cards using columns
        for i, paper in enumerate(gaps[:5], 1):
            st.markdown(f"### Gap Opportunity {i}: {paper['title']}")
            
            col1, col2 = st.columns([7, 3])
            with col1:
                st.markdown(f"**Source**: {paper['source']} ({paper['year']})")
                st.markdown(f"**Authors**: {paper['authors']}")
                st.markdown(f"**Similarity Score**: {paper['similarity']:.2f}")
                
                # Show abstract in expandable section
                with st.expander("Abstract", expanded=False):
                    st.write(paper['abstract'])
                
            with col2:
                # Research gap idea
                st.markdown("#### Research Gap Idea")
                idea = suggest_gap_idea(paper, topic, opportunity_keywords)
                st.info(idea)
            
            st.divider()
            
        # Step 5: Final summary and tips
        st.subheader("✨ Research Strategy Tips")
        st.markdown("""
        To leverage these gaps effectively:
        1. **Explore outlier combinations**: Consider how elements from different gap papers might be combined
        2. **Cross-domain application**: Look for methods used in other fields that could be applied to your topic
        3. **Investigate emerging keywords**: Focus on the trending keywords identified in the analysis
        4. **Challenge assumptions**: Question why the gap papers differ from the mainstream approach
        """)
        
        # Option to download results as CSV
        if advanced_mode:
            # Prepare data for download
            download_data = []
            for paper in papers:
                download_data.append({
                    'Title': paper['title'],
                    'Source': paper['source'],
                    'Year': paper['year'],
                    'Authors': paper['authors'],
                    'Similarity': paper.get('similarity', 'N/A'),
                    'Is Gap Paper': paper in gaps,
                    'Abstract': paper['abstract']
                })
            
            download_df = pd.DataFrame(download_data)
            csv = download_df.to_csv(index=False)
            
            st.download_button(
                label="Download All Paper Data (CSV)",
                data=csv,
                file_name=f"research_gaps_{topic.split(':')[0]}.csv",
                mime="text/csv",
            )

if __name__ == "__main__":
    st.set_page_config(
        page_title="Research Gap Finder",
        page_icon="🕳️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    run_gap_finder()