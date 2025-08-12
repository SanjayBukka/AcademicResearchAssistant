"""
Simple Q&A Assistant without heavy dependencies
Fallback version for deployment environments with limited dependencies
"""

import streamlit as st
import PyPDF2
import io
import os
import google.generativeai as genai

def configure_gemini_api(api_key):
    """Configure Gemini API"""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        return False

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def answer_question_with_context(question, context, api_key):
    """Answer question using Gemini with document context"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Based on the following research paper content, please answer the question.
        
        Document Content:
        {context[:8000]}  # Limit context to avoid token limits
        
        Question: {question}
        
        Please provide a detailed answer based on the document content. If the answer is not in the document, please say so.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating answer: {e}"

def run_simple_qa():
    """Simple Q&A interface without heavy dependencies"""
    st.subheader("📚 Simple Q&A Assistant")
    st.write("Upload a research paper and ask questions about it.")
    st.info("💡 This is a simplified version that works without heavy ML dependencies.")
    
    # API Key configuration
    with st.sidebar:
        st.write("### API Configuration")
        
        # Try to get API key from environment
        default_api_key = os.getenv('GEMINI_API_KEY', '')
        
        api_key = st.text_input("Enter Gemini API Key",
                               type="password",
                               value=default_api_key,
                               help="Get your API key from https://makersuite.google.com/app/apikey")
        
        if not api_key:
            st.warning("⚠️ Please enter your Gemini API key to use this feature.")
            return
    
    # File upload
    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type=['pdf'])
    
    if uploaded_file is not None:
        # Extract text from PDF
        with st.spinner("Extracting text from PDF..."):
            text_content = extract_text_from_pdf(uploaded_file)
        
        if text_content:
            st.success(f"✅ Successfully extracted {len(text_content)} characters from the PDF")
            
            # Show preview of extracted text
            with st.expander("📄 Preview extracted text"):
                st.text_area("Extracted content (first 1000 characters):", 
                           text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                           height=200)
            
            # Question input
            question = st.text_input("Ask a question about the paper:")
            
            if question:
                if st.button("Get Answer", type="primary"):
                    with st.spinner("Generating answer..."):
                        answer = answer_question_with_context(question, text_content, api_key)
                    
                    st.markdown("### 💬 Answer:")
                    st.markdown(answer)
            
            # Suggested questions
            st.markdown("### 💡 Suggested Questions:")
            suggested_questions = [
                "What is the main research question or hypothesis?",
                "What methodology was used in this study?",
                "What are the key findings or results?",
                "What are the limitations of this study?",
                "What future research directions are suggested?"
            ]
            
            for i, suggestion in enumerate(suggested_questions):
                if st.button(suggestion, key=f"suggestion_{i}"):
                    with st.spinner("Generating answer..."):
                        answer = answer_question_with_context(suggestion, text_content, api_key)
                    
                    st.markdown("### 💬 Answer:")
                    st.markdown(answer)
        else:
            st.error("❌ Failed to extract text from the PDF. Please try a different file.")
    else:
        st.info("👆 Please upload a PDF file to get started.")
        
        # Show example
        st.markdown("### 📖 How it works:")
        st.markdown("""
        1. **Upload** a research paper in PDF format
        2. **Ask questions** about the content
        3. **Get answers** powered by Google Gemini AI
        4. **Explore** with suggested questions
        """)
        
        st.markdown("### ✨ Features:")
        st.markdown("""
        - 📄 PDF text extraction
        - 🤖 AI-powered question answering
        - 💡 Suggested research questions
        - 🔍 Context-aware responses
        """)

if __name__ == "__main__":
    run_simple_qa()
