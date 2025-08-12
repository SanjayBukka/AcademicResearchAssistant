"""
Configuration settings for Academic Research Assistant
"""

# Model configurations for different performance needs
MODEL_CONFIGS = {
    "fast": {
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",  # Faster, smaller
        "description": "Fast loading, good performance",
        "size": "~90MB"
    },
    "balanced": {
        "embedding_model": "sentence-transformers/all-mpnet-base-v2",  # Balanced
        "description": "Balanced speed and accuracy",
        "size": "~420MB"
    },
    "accurate": {
        "embedding_model": "allenai/scibert_scivocab_uncased",  # Most accurate for academic
        "description": "Best accuracy for academic content",
        "size": "~440MB"
    }
}

# Default configuration
DEFAULT_CONFIG = "fast"  # Changed from "accurate" to "fast"

# API settings
API_SETTINGS = {
    "timeout": 10,
    "max_retries": 3,
    "rate_limit_delay": 1
}

# UI settings
UI_SETTINGS = {
    "max_papers_display": 20,
    "default_search_limit": 10,  # Reduced from 50
    "chunk_size": 500,  # Reduced from 1000 for faster processing
    "chunk_overlap": 100  # Reduced from 200
}

# Cache settings
CACHE_SETTINGS = {
    "ttl": 3600,  # 1 hour
    "max_entries": 100
}
