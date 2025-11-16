import os
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers"""
    
    def __init__(self):
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_name)
        self.chunk_size = 512  # Maximum tokens per chunk
        
    def _chunk_text(self, text: str, max_length: int = 512) -> List[str]:
        """Split text into chunks to avoid token limit"""
        words = text.split()
        chunks = []
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
            import os
            
            # Check if model is already cached locally
            model_name = 'all-MiniLM-L6-v2'
            cache_folder = os.path.expanduser('~/.cache/torch/sentence_transformers')
            
            logger.info(f"Loading sentence-transformers model: {model_name}")
            
            try:
                _model = SentenceTransformer(model_name)
                logger.info("Model loaded successfully")
            except Exception as download_error:
                logger.warning(f"Failed to download model from HuggingFace: {download_error}")
                logger.info("Attempting to use local cache or creating fallback...")
                
                # Try to use sentence-transformers/all-MiniLM-L6-v2 from any available cache
                try:
                    _model = SentenceTransformer(f'sentence-transformers/{model_name}')
                    logger.info("Model loaded from alternative path")
                except Exception as e2:
                    logger.error(f"Could not load model from any source: {e2}")
                    # Create a mock model for testing purposes
                    logger.warning("Using fallback: basic TF-IDF based embeddings")
                    _model = "FALLBACK_MODE"
                    
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            _model = "FALLBACK_MODE"
    
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
        # Return zero vector for empty text (384 dimensions for MiniLM)
        return [0.0] * 384
    
    text = text.strip()
    
    try:
        model = _get_model()
        
        # Check if using fallback mode
        if model == "FALLBACK_MODE":
            return _fallback_embedding(text)
        
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
            word_length = len(word.split())
            if current_length + word_length > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text[:1000]]  # Fallback to truncation
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate normalized embedding for text with chunking support
        Returns averaged embedding if text is chunked
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            embedding_dim = self.model.get_sentence_embedding_dimension()
            return [0.0] * embedding_dim
        
        # Chunk text if too long
        chunks = self._chunk_text(text, max_length=self.chunk_size)
        
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = self.model.encode(chunk, normalize_embeddings=True)
            embeddings.append(embedding)
        
        # Average embeddings if multiple chunks
        if len(embeddings) > 1:
            avg_embedding = np.mean(embeddings, axis=0)
            # Normalize the averaged embedding
            norm = np.linalg.norm(avg_embedding)
            if norm > 0:
                avg_embedding = avg_embedding / norm
            final_embedding = avg_embedding
        else:
            final_embedding = embeddings[0]
        
        return final_embedding.tolist()
    
    def cosine_similarity(self, embedding1: Union[List[float], np.ndarray], 
                         embedding2: Union[List[float], np.ndarray]) -> float:
        """
        Compute cosine similarity between two embeddings
        Returns value between -1 and 1 (typically 0 to 1 for normalized embeddings)
        """
        # Convert to numpy arrays if needed
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [-1, 1] to handle floating point errors
        return float(np.clip(similarity, -1.0, 1.0))
    
    def compute_match_score(self, embedding1: Union[List[float], np.ndarray],
                           embedding2: Union[List[float], np.ndarray]) -> float:
        """
        Compute match score (0-100) based on cosine similarity
        """
        similarity = self.cosine_similarity(embedding1, embedding2)
        # Convert from [-1, 1] to [0, 100]
        # Since embeddings are normalized, similarity is typically [0, 1]
        score = ((similarity + 1) / 2) * 100
        return round(score, 2)


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
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
        logger.warning("Falling back to simple TF-IDF based embedding")
        return _fallback_embedding(text)


def _fallback_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Fallback embedding when sentence-transformers is not available.
    Uses a simple TF-IDF-like approach with hashing.
    
    Args:
        text: Input text
        dim: Embedding dimension (default 384 to match MiniLM)
        
    Returns:
        List of floats representing a pseudo-embedding
    """
    import hashlib
    
    # Tokenize
    words = text.lower().split()
    
    # Create a simple embedding based on word hashes
    embedding = np.zeros(dim)
    
    for word in words:
        # Hash each word to multiple dimensions
        hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
        for i in range(3):  # Use 3 hash values per word
            idx = (hash_val + i) % dim
            embedding[idx] += 1.0
    
    # Normalize
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding.tolist()


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
