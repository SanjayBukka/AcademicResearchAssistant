from sentence_transformers import SentenceTransformer
import numpy as np

class VectorStore:
    def __init__(self):
        # Explicitly using SBERT model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # SBERT model optimized for sentence embeddings
        self.embeddings = None
        self.chunks = None
    
    def store(self, chunks):
        """Store text chunks and their SBERT embeddings."""
        self.chunks = chunks
        # Generate embeddings with SBERT
        self.embeddings = self.model.encode(chunks, convert_to_tensor=False, show_progress_bar=True)
        print(f"Stored {len(chunks)} chunks with SBERT embeddings.")  # Debugging
    
    def retrieve(self, query, top_k=3):
        """Retrieve top_k most similar chunks using SBERT embeddings."""
        query_embedding = self.model.encode([query], convert_to_tensor=False)[0]
        # Compute cosine similarity between query and stored embeddings
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        # Get indices of top_k most similar chunks
        top_indices = similarities.argsort()[-top_k:][::-1]
        top_chunks = [self.chunks[i] for i in top_indices]
        top_scores = similarities[top_indices]
        return top_chunks, top_scores