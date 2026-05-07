"""
Load and manage embeddings using sentence-transformers.
"""
from sentence_transformers import SentenceTransformer


def get_embeddings_model():
    """
    Load the sentence-transformers embedding model.
    Returns the model for generating embeddings.
    """
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model


def embed_text(model, text):
    """
    Generate embedding for a given text.
    """
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding
