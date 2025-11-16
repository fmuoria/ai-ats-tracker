"""
Embedding Service for computing semantic similarity between resumes and job descriptions.

Uses sentence-transformers (all-MiniLM-L6-v2) for local embeddings.
"""

import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_model = None


def _get_model():
    """Lazy load the sentence transformer model"""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers model: {e}")
            raise
    return _model


def embed_text(text: str, max_length: int = 5000) -> List[float]:
    """
    Compute normalized embedding for input text.
    
    For long texts, chunks them and averages embeddings.
    
    Args:
        text: Input text to embed
        max_length: Maximum characters per chunk (default 5000)
        
    Returns:
        List of floats representing the normalized embedding
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for embedding")
        # Return zero vector for empty text
        model = _get_model()
        embedding_dim = model.get_sentence_embedding_dimension()
        return [0.0] * embedding_dim
    
    text = text.strip()
    
    try:
        model = _get_model()
        
        # If text is short enough, embed directly
        if len(text) <= max_length:
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        
        # For long texts, chunk and average embeddings
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        logger.info(f"Text too long ({len(text)} chars), split into {len(chunks)} chunks")
        
        # Compute embeddings for all chunks
        chunk_embeddings = model.encode(chunks, normalize_embeddings=True)
        
        # Average the embeddings
        avg_embedding = np.mean(chunk_embeddings, axis=0)
        
        # Re-normalize after averaging
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm
        
        return avg_embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error computing embedding: {e}")
        raise


def cosine_similarity(embedding_a: List[float], embedding_b: List[float]) -> float:
    """
    Compute cosine similarity between two embeddings.
    
    Args:
        embedding_a: First embedding vector
        embedding_b: Second embedding vector
        
    Returns:
        Cosine similarity score between -1 and 1 (typically 0 to 1 for normalized vectors)
    """
    if not embedding_a or not embedding_b:
        logger.warning("One or both embeddings are empty")
        return 0.0
    
    if len(embedding_a) != len(embedding_b):
        logger.error(f"Embedding dimension mismatch: {len(embedding_a)} vs {len(embedding_b)}")
        return 0.0
    
    try:
        vec_a = np.array(embedding_a)
        vec_b = np.array(embedding_b)
        
        # For normalized vectors, dot product equals cosine similarity
        similarity = np.dot(vec_a, vec_b)
        
        # Clip to [-1, 1] range due to potential floating point errors
        similarity = np.clip(similarity, -1.0, 1.0)
        
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error computing cosine similarity: {e}")
        return 0.0


def compute_similarity_percentage(embedding_a: List[float], embedding_b: List[float]) -> float:
    """
    Compute similarity as a percentage (0-100).
    
    Converts cosine similarity from [-1, 1] range to [0, 100] percentage.
    For normalized embeddings, the range is effectively [0, 1] -> [0, 100].
    
    Args:
        embedding_a: First embedding vector
        embedding_b: Second embedding vector
        
    Returns:
        Similarity percentage between 0 and 100
    """
    similarity = cosine_similarity(embedding_a, embedding_b)
    
    # Convert from [-1, 1] to [0, 100]
    # For normalized vectors, similarity is typically in [0, 1] range
    percentage = ((similarity + 1) / 2) * 100
    
    return round(percentage, 2)
