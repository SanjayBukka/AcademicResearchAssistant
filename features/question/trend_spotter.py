import streamlit as st
import requests
import os
import tempfile
import PyPDF2
from langchain_community.llms import Ollama
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.getvalue())
            temp_file_path = temp_file.name
        
        with open(temp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        os.unlink(temp_file_path)  # Delete the temporary file
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def create_vectorstore(text):
    """Create a vector store from the paper text."""
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Create embeddings using SciBERT
    embeddings = HuggingFaceEmbeddings(
        model_name="allenai/scibert_scivocab_uncased",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create vector store
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

def run_research_assistant():
    st.subheader("📚 Research Paper Assistant")
    st.write("Upload your research paper and ask questions about it.")
    
    # File uploader for research papers (PDF)
    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")
    
    if uploaded_file:
        # Button to process the uploaded file
        if st.button("Process Paper"):
            with st.spinner("Extracting text from paper..."):
                paper_text = extract_text_from_pdf(uploaded_file)
                if not paper_text:
                    st.error("Failed to extract text from the PDF. Please try another file.")
                    return
                
                st.session_state.paper_text = paper_text
                st.success(f"Successfully processed paper ({len(paper_text)} characters)")
                
                # Create vector store for RAG
                with st.spinner("Creating knowledge base with SciBERT embeddings..."):
                    vectorstore = create_vectorstore(paper_text)
                    st.session_state.vectorstore = vectorstore
                    st.success("Paper knowledge base created! You can now ask questions.")
    
    # Only show question input if a paper has been processed
    if 'vectorstore' in st.session_state:
        st.write("### Ask Questions About Your Paper")
        question = st.text_input("What would you like to know about this paper?", 
                                placeholder="e.g., What is the main conclusion of this study?")
        
        if question and st.button("Get Answer"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize the LLM
                    llm = Ollama(model="tinyllama")
                    
                    # Create a retrieval QA chain
                    qa_chain = RetrievalQA.from_chain_type(
                        llm=llm,
                        chain_type="stuff",
                        retriever=st.session_state.vectorstore.as_retriever(
                            search_kwargs={"k": 3}
                        )
                    )
                    
                    # Get answer
                    response = qa_chain.run(question)
                    
                    # Display answer
                    st.write("### Answer")
                    st.write(response)
                    
                    # Show context (optional)
                    with st.expander("See relevant sections from the paper"):
                        docs = st.session_state.vectorstore.similarity_search(question, k=3)
                        for i, doc in enumerate(docs):
                            st.markdown(f"**Relevant Section {i+1}:**")
                            st.write(doc.page_content)
                            st.write("---")
                    
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
                    st.info("Make sure Ollama is running with the TinyLlama model installed. You can install it with: 'ollama pull tinyllama'")
    
    # Display additional information if no paper is uploaded
    if 'vectorstore' not in st.session_state:
        st.info("👆 Upload a research paper (PDF) to get started.")
        st.write("""
        **How it works:**
        1. Upload your research paper in PDF format
        2. The system extracts text and creates a searchable knowledge base using SciBERT embeddings
        3. Ask specific questions about the paper's content
        4. Get contextual answers based on the paper's information
        """)