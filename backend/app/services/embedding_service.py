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
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word.split())
            if current_length + word_length > max_length:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
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
