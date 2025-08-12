import streamlit as st
import requests
import os
import tempfile
import PyPDF2
import io
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

OCR_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    pass

# Configure Gemini API
def configure_gemini_api(api_key: str):
    """Configure Gemini API with the provided key."""
    try:
        genai.configure(api_key=api_key)
        # Test the connection by listing models
        models = list(genai.list_models())
        if models:
            return True
        return False
    except Exception as e:
        st.error(f"Error configuring Gemini API: {e}")
        return False

@st.cache_data(ttl=3600)  # Cache for 1 hour
def answer_question_with_gemini(question: str, context: str, api_key: str) -> str:
    """Answer a question using Gemini API with the provided context."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Truncate context if too long to avoid API limits
        max_context_length = 8000  # Conservative limit
        if len(context) > max_context_length:
            context = context[:max_context_length] + "... [truncated]"

        prompt = f"""
        Based on the following research paper content, please answer the question accurately and comprehensively.

        Research Paper Content:
        {context}

        Question: {question}

        Instructions:
        1. Answer based only on the information provided in the research paper content
        2. If the information is not available in the content, clearly state that
        3. Provide specific details and quotes when relevant
        4. Keep the answer focused and academic in tone
        5. If applicable, mention the section or context where the information was found

        Answer:
        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Error generating answer: {str(e)}"

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file without OCR."""
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

def extract_text_with_ocr_if_available(pdf_file):
    """Extract text from PDF, using OCR if available, otherwise falling back to standard extraction."""
    if not OCR_AVAILABLE:
        st.warning("OCR functionality is not available. Installing dependencies would enable image text extraction.")
        st.info("To enable OCR, install: pip install pytesseract pdf2image pillow")
        st.info("You'll also need to install Poppler on your system.")
        return extract_text_from_pdf(pdf_file)
    
    full_text = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_file.getvalue())
            temp_file_path = temp_file.name
        
        # Standard text extraction
        with open(temp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text += text + "\n\n"
        
        # OCR for images in the PDF
        try:
            with st.spinner("Performing OCR on images in PDF..."):
                images = convert_from_path(temp_file_path)
                for i, image in enumerate(images):
                    # Save image temporarily
                    img_path = f"temp_img_{i}.png"
                    image.save(img_path, "PNG")
                    
                    # Perform OCR
                    img_text = pytesseract.image_to_string(Image.open(img_path))
                    if img_text.strip():  # Only add if we got meaningful text
                        full_text += f"\n[Image Content Page {i+1}]: {img_text}\n"
                    
                    # Clean up
                    if os.path.exists(img_path):
                        os.remove(img_path)
        except Exception as ocr_e:
            st.warning(f"OCR processing failed, but basic text extraction succeeded: {ocr_e}")
            st.info("Proceeding with text-only extraction. To enable OCR, ensure Poppler is properly installed.")
        
        os.unlink(temp_file_path)  # Delete the temporary file
        return full_text
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return ""

@st.cache_resource
def load_embeddings_model(model_type="fast"):
    """Load and cache the embeddings model with fallback options."""

    # Define model options with fallbacks
    model_options = {
        "fast": [
            "sentence-transformers/all-MiniLM-L6-v2",
            "sentence-transformers/paraphrase-MiniLM-L6-v2"
        ],
        "balanced": [
            "sentence-transformers/all-mpnet-base-v2",
            "sentence-transformers/all-MiniLM-L12-v2",
            "sentence-transformers/all-MiniLM-L6-v2"
        ],
        "accurate": [
            "sentence-transformers/all-mpnet-base-v2",
            "allenai/scibert_scivocab_uncased",
            "sentence-transformers/all-MiniLM-L6-v2"
        ]
    }

    # Get model list for the requested type
    models_to_try = model_options.get(model_type, model_options["fast"])

    for model_name in models_to_try:
        try:
            with st.spinner(f"Loading {model_type} embeddings model ({model_name})..."):
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                st.success(f"✅ Successfully loaded {model_name}")
                return embeddings

        except Exception as e:
            st.warning(f"⚠️ Failed to load {model_name}: {str(e)}")
            continue

    # If all models fail, raise an error
    raise Exception(f"Failed to load any {model_type} embedding model. Please check your internet connection.")

def create_vectorstore(text, model_type="fast"):
    """Create a vector store from the paper text."""
    # Import config for chunk sizes with proper path handling
    try:
        import sys
        import os
        # Add the parent directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(os.path.dirname(current_dir))
        sys.path.insert(0, parent_dir)

        from config import UI_SETTINGS
        chunk_size = UI_SETTINGS["chunk_size"]
        chunk_overlap = UI_SETTINGS["chunk_overlap"]
    except (ImportError, KeyError):
        chunk_size = 500  # Smaller chunks for faster processing
        chunk_overlap = 100

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Use cached embeddings model with selected type
    embeddings = load_embeddings_model(model_type)

    # Create vector store
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    return vectorstore

def evaluate_response(reference, candidate):
    """
    Evaluate the quality of the AI response using BLEU score
    Args:
        reference: The reference text (ground truth)
        candidate: The AI-generated response
    Returns:
        BLEU score
    """
    try:
        # Tokenize the texts (simple word tokenization)
        reference_tokens = [reference.lower().split()]
        candidate_tokens = candidate.lower().split()
        
        # Calculate BLEU score with smoothing
        smooth = SmoothingFunction().method1
        bleu_score = sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smooth)
        
        return bleu_score
    except Exception as e:
        st.warning(f"Error calculating BLEU score: {e}")
        return 0.0

def run_research_assistant():
    st.subheader("📚 Research Paper Assistant")
    st.write("Upload your research paper and ask questions about it.")

    # Configuration in sidebar
    with st.sidebar:
        st.write("### API Configuration")

        # Try to get API key from environment first
        try:
            from env_loader import get_api_key
            default_api_key = get_api_key()
        except ImportError:
            default_api_key = os.getenv('GEMINI_API_KEY', '')

        api_key = st.text_input("Enter Gemini API Key",
                               type="password",
                               key="gemini_api_key_input",
                               value=default_api_key,
                               help="Get your API key from https://makersuite.google.com/app/apikey")
        if api_key:
            st.session_state.gemini_api_key = api_key
            if configure_gemini_api(api_key):
                st.success("✅ Gemini API configured successfully!")
            else:
                st.error("❌ Failed to configure Gemini API. Please check your key.")
        else:
            st.warning("⚠️ Please enter your Gemini API key to use the Q&A feature.")
            st.info("💡 Tip: You can set the GEMINI_API_KEY environment variable to avoid entering it each time.")

        st.write("### Performance Settings")
        model_choice = st.selectbox(
            "Model Speed",
            ["fast", "balanced", "accurate"],
            index=0,
            help="Fast: Quick loading (~90MB), Balanced: Good performance (~420MB), Accurate: Best for academic (~440MB)"
        )
        st.session_state.model_choice = model_choice

    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type="pdf")
    
    if uploaded_file:
        if st.button("Process Paper"):
            with st.spinner("Processing PDF..."):
                paper_text = extract_text_with_ocr_if_available(uploaded_file)
                if not paper_text:
                    st.error("Failed to extract text from the PDF. Please try another file.")
                    return
                
                st.session_state.paper_text = paper_text
                st.success(f"Successfully processed paper ({len(paper_text)} characters)")
                
                model_type = getattr(st.session_state, 'model_choice', 'fast')
                with st.spinner(f"Creating knowledge base with {model_type} embeddings..."):
                    vectorstore = create_vectorstore(paper_text, model_type)
                    st.session_state.vectorstore = vectorstore
                    st.success("Paper knowledge base created! You can now ask questions.")
    
    if 'vectorstore' in st.session_state:
        st.write("### Ask Questions About Your Paper")
        question = st.text_input("What would you like to know about this paper?", 
                                placeholder="e.g., What is the main conclusion of this study?")
        
        if question and st.button("Get Answer"):
            # Check if API key is provided
            if 'gemini_api_key' not in st.session_state or not st.session_state.gemini_api_key:
                st.error("Please provide your Gemini API key in the sidebar to get answers.")
                return

            with st.spinner("Thinking..."):
                try:
                    # Get relevant sections from vector store
                    docs = st.session_state.vectorstore.similarity_search(question, k=3)
                    contexts = [doc.page_content for doc in docs]
                    combined_context = " ".join(contexts)

                    # Use Gemini API to answer the question
                    response = answer_question_with_gemini(
                        question,
                        combined_context,
                        st.session_state.gemini_api_key
                    )

                    st.write("### Answer")
                    st.write(response)

                    # Calculate and display BLEU score
                    bleu = evaluate_response(combined_context, response)
                    
                    # Display evaluation metrics
                    st.write("### Response Evaluation")
                    st.write(f"BLEU Score: {bleu:.4f}")
                    
                    # Create color coding based on BLEU score
                    if bleu > 0.5:
                        score_color = "green"
                        quality = "Excellent"
                    elif bleu > 0.3:
                        score_color = "orange"
                        quality = "Good"
                    else:
                        score_color = "red"
                        quality = "Fair"
                    
                    st.markdown(f"<div style='background-color:{score_color}; padding:10px; border-radius:5px;'>"
                               f"<p style='color:white; margin:0;'>Response Quality: {bleu:.4f} ({quality})</p></div>", 
                               unsafe_allow_html=True)
                    
                    with st.expander("See relevant sections from the paper"):
                        for i, doc in enumerate(docs):
                            st.markdown(f"**Relevant Section {i+1}:**")
                            st.write(doc.page_content)
                            st.write("---")
                    
                except Exception as e:
                    st.error(f"Error generating answer: {e}")
                    st.info("Please check your Gemini API key and internet connection.")

    if 'vectorstore' not in st.session_state:
        st.info("👆 Upload a research paper (PDF) to get started.")
        
        feature_set = "text extraction"
        if OCR_AVAILABLE:
            feature_set = "text extraction and OCR for images"
            
        st.write(f"""
        **How it works:**
        1. Enter your Gemini API key in the sidebar
        2. Upload your research paper in PDF format
        3. The system performs {feature_set}
        4. Creates a searchable knowledge base using SciBERT embeddings
        5. Ask specific questions about the paper's content
        6. Get contextual answers using Google's Gemini AI
        7. View quality metrics for the AI's response
        """)
        
        # Display dependency information
        with st.expander("System Requirements"):
            st.markdown("""
            **Core Dependencies:**
            - Python 3.7+
            - Streamlit
            - PyPDF2
            - FAISS
            - SciBERT embeddings (HuggingFace)
            - Google Gemini API access

            **For OCR Features (Optional):**
            - pytesseract
            - pdf2image
            - Poppler (system installation required)
            - Tesseract OCR (system installation required)

            **For BLEU Score Evaluation:**
            - NLTK
            """)

if __name__ == "__main__":
    # Set up page configuration
    st.set_page_config(page_title="Research Paper Assistant", page_icon="📚", layout="wide")
    
    # Add dependencies check
    try:
        import nltk
        nltk.download('punkt', quiet=True)
    except ImportError:
        st.warning("NLTK not installed. Evaluation metrics might not work properly.")
    
    run_research_assistant()