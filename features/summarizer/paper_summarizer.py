# features/summarizer/paper_summarizer.py

import streamlit as st
import requests
import json
import re
from transformers import pipeline
from bs4 import BeautifulSoup
import PyPDF2
import io
from datetime import datetime

class PaperSource:
    def search(self, query, limit=5):
        pass
    
    def get_paper(self, paper_id):
        pass

class ArxivSource(PaperSource):
    def search(self, query, limit=5):
        base_url = "http://export.arxiv.org/api/query?"
        search_query = f"search_query=all:{query}&start=0&max_results={limit}"
        response = requests.get(base_url + search_query)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')
        
        results = []
        for entry in entries:
            paper_id = entry.id.text.split('/')[-1]
            title = entry.title.text.replace('\n', ' ').strip()
            abstract = entry.summary.text.replace('\n', ' ').strip()
            authors = [author.name.text for author in entry.find_all('author')]
            published = entry.published.text
            
            results.append({
                'id': paper_id,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'published': published,
                'source': 'arxiv',
                'url': entry.id.text
            })
        
        return results
    
    def get_paper(self, paper_id):
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        response = requests.get(pdf_url)
        
        if response.status_code != 200:
            return None
        
        return response.content

class SemanticScholarSource(PaperSource):
    def search(self, query, limit=5):
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,year,url,externalIds"
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for paper in data.get('data', []):
            paper_id = paper.get('paperId')
            arxiv_id = paper.get('externalIds', {}).get('arxiv')
            
            results.append({
                'id': paper_id,
                'arxiv_id': arxiv_id,
                'title': paper.get('title'),
                'abstract': paper.get('abstract', ''),
                'authors': [author.get('name') for author in paper.get('authors', [])],
                'published': paper.get('year'),
                'source': 'semantic_scholar',
                'url': paper.get('url')
            })
        
        return results
    
    def get_paper(self, paper_id):
        # For Semantic Scholar, we'll try to get the PDF if available
        paper_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=openAccessPdf"
        response = requests.get(paper_url)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        pdf_url = data.get('openAccessPdf', {}).get('url')
        
        if pdf_url:
            pdf_response = requests.get(pdf_url)
            if pdf_response.status_code == 200:
                return pdf_response.content
        
        return None

class CrossrefSource(PaperSource):
    def search(self, query, limit=5):
        url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "rows": limit,
            "sort": "relevance"
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        results = []
        
        for item in data.get('message', {}).get('items', []):
            if item.get('type') not in ['journal-article', 'proceedings-article']:
                continue
                
            doi = item.get('DOI')
            title = item.get('title', [''])[0] if item.get('title') else ''
            
            authors = []
            for author in item.get('author', []):
                name_parts = []
                if author.get('given'):
                    name_parts.append(author.get('given'))
                if author.get('family'):
                    name_parts.append(author.get('family'))
                authors.append(' '.join(name_parts))
            
            published = item.get('created', {}).get('date-parts', [['']])[0][0]
            
            results.append({
                'id': doi,
                'title': title,
                'abstract': '',  # Crossref doesn't typically provide abstracts
                'authors': authors,
                'published': published,
                'source': 'crossref',
                'url': f"https://doi.org/{doi}" if doi else ''
            })
        
        return results
    
    def get_paper(self, paper_id):
        # For Crossref, we'll try to resolve the DOI and get the PDF
        doi_url = f"https://doi.org/{paper_id}"
        headers = {
            'Accept': 'application/pdf'
        }
        
        try:
            response = requests.get(doi_url, headers=headers, allow_redirects=True)
            if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
                return response.content
        except:
            pass
        
        return None

class PaperSummarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    def extract_sections(self, text):
        # This is a simplified section extraction
        # Common section headers in research papers
        section_patterns = [
            r'(?:\n|\r\n)(\d+\.\s+\w+.*?)(?=\n|\r\n)',  # Numbered sections like "1. Introduction"
            r'(?:\n|\r\n)([A-Z][A-Z\s]+)(?=\n|\r\n)',  # ALL CAPS sections
            r'(?:\n|\r\n)(\w+\s*\w+)(?=\n|\r\n)',  # Regular sections
        ]
        
        # First, try to find section headers
        section_headers = []
        for pattern in section_patterns:
            headers = re.findall(pattern, text)
            section_headers.extend(headers)
        
        # If no headers found, chunk the text by paragraphs
        if not section_headers:
            paragraphs = re.split(r'\n\s*\n', text)
            sections = []
            
            for i, para in enumerate(paragraphs):
                if i == 0:
                    sections.append(("Abstract", para))
                elif i == len(paragraphs) - 1:
                    sections.append(("Conclusion", para))
                else:
                    sections.append((f"Section {i}", para))
            
            return sections
        
        # If headers found, split the text by those headers
        sections = []
        for i, header in enumerate(section_headers):
            if i < len(section_headers) - 1:
                next_header = section_headers[i + 1]
                section_text = text.split(header)[1].split(next_header)[0]
            else:
                section_text = text.split(header)[1]
            
            sections.append((header, section_text))
        
        return sections
    
    def summarize_section(self, section_text, max_length=150):
        # Clean up the text
        text = section_text.strip()
        
        # Skip empty sections
        if not text or len(text.split()) < 20:
            return "Section is too short to summarize."
        
        # Limit input length to avoid model errors
        max_input_length = 1024
        if len(text.split()) > max_input_length:
            text = ' '.join(text.split()[:max_input_length])
        
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)[0]['summary_text']
            return summary
        except Exception as e:
            return f"Error summarizing section: {str(e)}"
    
    def summarize_paper(self, pdf_content):
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        
        # Extract sections
        sections = self.extract_sections(text)
        
        # Summarize each section
        summaries = []
        for section_title, section_text in sections:
            summary = self.summarize_section(section_text)
            summaries.append((section_title, summary))
        
        return summaries

def run_paper_summarizer():
    st.subheader("📃 Section-wise Paper Summarization")
    
    # Initialize session state
    if "paper_summaries" not in st.session_state:
        st.session_state.paper_summaries = {}
    
    # Set up the paper sources
    sources = {
        "arXiv": ArxivSource(),
        "Semantic Scholar": SemanticScholarSource(),
        "Crossref": CrossrefSource()
    }
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Enter research topic or keywords", placeholder="e.g., natural language processing deep learning")
    
    with col2:
        source_name = st.selectbox("Source", list(sources.keys()))
    
    if st.button("Find Papers"):
        if search_query:
            with st.spinner(f"Searching {source_name} for papers..."):
                try:
                    results = sources[source_name].search(search_query)
                    st.session_state.search_results = results
                    st.session_state.current_source = source_name
                except Exception as e:
                    st.error(f"Error searching {source_name}: {str(e)}")
                    st.session_state.search_results = []
    
    # Alternative: Upload a PDF directly
    uploaded_file = st.file_uploader("Or upload a PDF paper directly", type="pdf")
    if uploaded_file is not None:
        with st.spinner("Processing uploaded paper..."):
            pdf_content = uploaded_file.read()
            try:
                summarizer = PaperSummarizer()
                summaries = summarizer.summarize_paper(pdf_content)
                paper_id = "uploaded_" + datetime.now().strftime("%Y%m%d%H%M%S")
                paper = {
                    'id': paper_id,
                    'title': uploaded_file.name,
                    'abstract': '',
                    'authors': ['Unknown'],
                    'published': 'Unknown',
                    'source': 'uploaded',
                    'url': ''
                }
                st.session_state.paper_summaries[paper_id] = {
                    'paper': paper,
                    'summaries': summaries
                }
                st.success("Paper summarized successfully!")
            except Exception as e:
                st.error(f"Error summarizing uploaded paper: {str(e)}")
    
    # Display search results
    if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
        st.subheader("Search Results")
        for i, paper in enumerate(st.session_state.search_results):
            with st.expander(f"{i+1}. {paper['title']}"):
                st.write(f"**Authors:** {', '.join(paper['authors'])}")
                st.write(f"**Published:** {paper['published']}")
                if paper['abstract']:
                    st.write(f"**Abstract:** {paper['abstract'][:300]}...")
                
                if st.button("Generate Section Summaries", key=f"summarize_{i}"):
                    source = sources[st.session_state.current_source]
                    paper_id = paper['id']
                    
                    with st.spinner("Downloading and processing paper..."):
                        pdf_content = source.get_paper(paper_id)
                        
                        if pdf_content:
                            summarizer = PaperSummarizer()
                            try:
                                summaries = summarizer.summarize_paper(pdf_content)
                                st.session_state.paper_summaries[paper_id] = {
                                    'paper': paper,
                                    'summaries': summaries
                                }
                                st.success("Paper summarized successfully!")
                            except Exception as e:
                                st.error(f"Error summarizing paper: {str(e)}")
                        else:
                            st.error("Could not download the paper. It might be behind a paywall or not available in PDF format.")
    
    # Display summaries
    if st.session_state.paper_summaries:
        st.subheader("Section Summaries")
        for paper_id, data in st.session_state.paper_summaries.items():
            paper = data['paper']
            summaries = data['summaries']
            
            with st.expander(f"Summary of: {paper['title']}"):
                for section_title, summary in summaries:
                    st.markdown(f"### {section_title}")
                    st.write(summary)
                
                # Save to library button
                if st.button("Save to My Library", key=f"save_{paper_id}"):
                    if "my_library" not in st.session_state:
                        st.session_state.my_library = []
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.my_library.append({
                        'paper': paper,
                        'summaries': summaries,
                        'added_on': timestamp
                    })
                    st.success("Added to your library!")
    
    # My Library tab
    if st.checkbox("Show My Library", value=False):
        st.subheader("My Library")
        if "my_library" in st.session_state and st.session_state.my_library:
            for i, item in enumerate(st.session_state.my_library):
                paper = item['paper']
                with st.expander(f"{paper['title']}"):
                    st.write(f"**Authors:** {', '.join(paper['authors'])}")
                    st.write(f"**Added on:** {item['added_on']}")
                    st.write(f"**Source:** {paper['source']}")
                    
                    st.markdown("### Section Summaries")
                    for section_title, summary in item['summaries']:
                        st.markdown(f"#### {section_title}")
                        st.write(summary)
                    
                    if st.button("Remove from Library", key=f"remove_{i}"):
                        st.session_state.my_library.pop(i)
                        st.experimental_rerun()
        else:
            st.info("Your library is empty. Save summaries to view them here.")

if __name__ == "__main__":
    run_paper_summarizer()