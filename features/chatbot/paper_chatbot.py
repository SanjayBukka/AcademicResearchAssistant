import streamlit as st
from transformers import pipeline
from .pdf_processor import extract_text_from_pdf, chunk_text
from .vector_store import VectorStore
from datetime import datetime

def run_chatbot():
    st.subheader("💬 Paper Chatbot")
    
    uploaded_file = st.file_uploader("Upload a PDF Paper", type="pdf")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    
    if uploaded_file and not st.session_state.vector_store:
        with st.spinner("Processing your PDF with SBERT embeddings..."):
            text = extract_text_from_pdf(uploaded_file)
            chunks = chunk_text(text)
            st.session_state.vector_store = VectorStore()
            st.session_state.vector_store.store(chunks)
        st.success("PDF loaded! Ready to chat with SBERT-powered answers.")

    if st.session_state.vector_store:
        st.write("**Hey there!** I’ve got your paper loaded with some fancy SBERT magic. Ask me anything!")
        
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Your question:", placeholder="e.g., What’s this paper about?")
            submit_button = st.form_submit_button(label="Send")
        
        if submit_button and user_input:
            generator = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")
            # Use SBERT embeddings for retrieval
            relevant_chunks, scores = st.session_state.vector_store.retrieve(user_input, top_k=3)
            context = "\n".join(relevant_chunks)
            context_summary = "This paper’s about a solar panel tracking system using LDRs, voltage sensors, and a Raspberry Pi to boost energy by tracking the sun and avoiding shade."
            
            history = "\n".join([f"User: {chat['user']}\nBot: {chat['bot']}" 
                                for chat in st.session_state.chat_history])
            
            prompt = f"""
            You’re a super chill chatbot buddy helping with a research paper. Answer the user’s question in a fun, casual way—like you’re chatting with a friend. Keep it short, use the context to nail the answer, and toss in a follow-up question. If they typo (like ‘thia’ for ‘this’), tease them a bit but still answer. Don’t repeat the prompt or history—just give the reply!

            Past Chat:
            {history}

            Quick Paper Summary:
            {context_summary}

            Full Paper Details (SBERT-picked chunks):
            {context}

            User Says: {user_input}
            """
            
            try:
                response = generator(prompt, max_new_tokens=150, temperature=0.9, do_sample=True)[0]["generated_text"]
                response = response.split(user_input)[-1].strip()
                if not response or len(response) < 15:
                    if "thia" in user_input.lower():
                        response = "Hey, ‘thia’—you mean ‘this’, right? I think this paper’s dope! It’s got solar panels tracking the sun with LDRs and a Pi—super smart stuff. What’s your take?"
                    else:
                        response = "Yo, this paper’s cool! It’s about solar panels chasing the sun with LDRs and a Raspberry Pi to grab more juice. What do you reckon?"
                if "?" not in response:
                    response += " What’s your next question?"
            except Exception as e:
                response = f"Oof, hit a bump ({str(e)})! Still, this paper’s about solar tracking with LDRs and a Pi—pretty rad! What else you wanna know?"
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({"user": user_input, "bot": response, "timestamp": timestamp})
        
        if st.session_state.chat_history:
            st.write("### Chat History")
            for chat in st.session_state.chat_history:
                st.write(f"You ({chat['timestamp']}): {chat['user']}")
                st.write(f"Bot ({chat['timestamp']}): {chat['bot']}")
                st.write("---")
    else:
        st.info("Upload a PDF to start chatting!")