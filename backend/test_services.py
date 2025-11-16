"""
Tests for new services: embedding, AI, and social search
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from app.services.embedding_service import EmbeddingService, get_embedding_service
from app.services.ai_service import AIService, get_ai_service
from app.services.social_search import SocialSearchService, get_social_search_service


class TestEmbeddingService:
    """Tests for EmbeddingService"""
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_embed_text_returns_list(self, mock_transformer):
        """Test that embed_text returns a list of floats"""
        # Mock the model
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        import numpy as np
        mock_model.encode.return_value = np.random.rand(384)
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        text = "This is a test resume with skills like Python and JavaScript"
        embedding = service.embed_text(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_embed_empty_text(self, mock_transformer):
        """Test embedding empty text returns zero vector"""
        # Mock the model
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        import numpy as np
        mock_model.encode.return_value = np.zeros(384)
        mock_transformer.return_value = mock_model
        
        service = EmbeddingService()
        embedding = service.embed_text("")
        
        assert isinstance(embedding, list)
        assert len(embedding) > 0
        # Should be all zeros or very close
        assert all(abs(x) < 0.01 for x in embedding)
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        import numpy as np
        service = EmbeddingService.__new__(EmbeddingService)
        
        # Same embeddings should have similarity close to 1
        emb = np.random.rand(384)
        emb = emb / np.linalg.norm(emb)  # Normalize
        similarity = service.cosine_similarity(emb.tolist(), emb.tolist())
        
        assert 0.95 <= similarity <= 1.0
    
    def test_cosine_similarity_different_texts(self):
        """Test cosine similarity with different embeddings"""
        import numpy as np
        service = EmbeddingService.__new__(EmbeddingService)
        
        emb1 = np.random.rand(384)
        emb2 = np.random.rand(384)
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)
        similarity = service.cosine_similarity(emb1.tolist(), emb2.tolist())
        
        # Should be between 0 and 1 for normalized vectors
        assert -1.0 <= similarity <= 1.0
    
    def test_compute_match_score(self):
        """Test match score computation"""
        import numpy as np
        service = EmbeddingService.__new__(EmbeddingService)
        
        # Create similar embeddings
        emb1 = np.ones(384)
        emb2 = np.ones(384) * 0.9
        emb1 = emb1 / np.linalg.norm(emb1)
        emb2 = emb2 / np.linalg.norm(emb2)
        score = service.compute_match_score(emb1.tolist(), emb2.tolist())
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    @patch('app.services.embedding_service.SentenceTransformer')
    def test_singleton_pattern(self, mock_transformer):
        """Test that get_embedding_service returns singleton"""
        mock_model = MagicMock()
        mock_transformer.return_value = mock_model
        
        service1 = get_embedding_service()
        service2 = get_embedding_service()
        assert service1 is service2


class TestAIService:
    """Tests for AIService with mocked Gemini"""
    
    @patch('app.services.ai_service.genai')
    def test_analyze_resume_with_mocked_gemini(self, mock_genai):
        """Test resume analysis with mocked Gemini response"""
        # Setup mock
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "model_fit_score": 75,
            "strengths": ["Strong Python skills", "Good experience"],
            "gaps": ["Limited cloud experience"],
            "recommended_questions": ["Tell me about your Python projects"],
            "matched_skills": ["Python", "JavaScript"],
            "missing_skills": ["AWS", "Docker"],
            "summary": "Good candidate overall"
        }
        '''
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test
        os.environ['GEMINI_API_KEY'] = 'test_key'
        service = AIService()
        result = service.analyze_resume_with_gemini(
            "Python developer with 5 years experience",
            "Looking for senior Python developer"
        )
        
        assert isinstance(result, dict)
        assert 'model_fit_score' in result
        assert 'strengths' in result
        assert 'gaps' in result
        assert result['model_fit_score'] == 75
        assert len(result['strengths']) > 0
    
    def test_extract_skills_from_text(self):
        """Test skill extraction from text"""
        os.environ['GEMINI_API_KEY'] = 'test_key'
        service = AIService()
        
        text = "I have experience with Python, JavaScript, React, and AWS"
        skills = service.extract_skills_from_text(text)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        # Check for expected skills (case-insensitive check in original code)
        skill_lower = [s.lower() for s in skills]
        assert any('python' in s for s in skill_lower)
    
    @patch('app.services.ai_service.genai')
    def test_analyze_resume_error_handling(self, mock_genai):
        """Test error handling in resume analysis"""
        # Setup mock to raise error
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        os.environ['GEMINI_API_KEY'] = 'test_key'
        service = AIService()
        result = service.analyze_resume_with_gemini("Test resume")
        
        # Should return fallback result
        assert isinstance(result, dict)
        assert result['model_fit_score'] == 50
        assert 'error' in result.get('summary', '').lower() or 'unable' in result.get('strengths', [''])[0].lower()


class TestSocialSearchService:
    """Tests for SocialSearchService"""
    
    def test_search_without_api_key(self):
        """Test social search without API key returns manual check"""
        # Ensure no API key
        if 'SERPAPI_KEY' in os.environ:
            del os.environ['SERPAPI_KEY']
        
        service = SocialSearchService()
        result = service.search_public_profiles("John Doe", "john@example.com")
        
        assert isinstance(result, dict)
        assert result.get('manual_check_required') == True
        assert 'message' in result
    
    def test_search_disabled(self):
        """Test social search when disabled"""
        os.environ['SOCIAL_SEARCH_ENABLED'] = 'false'
        service = SocialSearchService()
        result = service.search_public_profiles("John Doe")
        
        assert isinstance(result, dict)
        assert result.get('status') == 'disabled'
        assert result.get('manual_check_required') == True
        
        # Cleanup
        os.environ['SOCIAL_SEARCH_ENABLED'] = 'true'
    
    @patch('app.services.social_search.SocialSearchService._search_with_serpapi')
    def test_search_with_api_key(self, mock_search):
        """Test social search with mocked SerpAPI"""
        # Setup mock
        mock_search.return_value = [
            {
                'link': 'https://linkedin.com/in/johndoe',
                'title': 'John Doe - Software Engineer',
                'snippet': 'Python developer with cloud experience'
            },
            {
                'link': 'https://github.com/johndoe',
                'title': 'johndoe (John Doe) - GitHub',
                'snippet': 'Open source contributor'
            }
        ]
        
        os.environ['SERPAPI_KEY'] = 'test_key'
        service = SocialSearchService()
        result = service.search_public_profiles("John Doe", "john@example.com")
        
        assert isinstance(result, dict)
        assert result.get('status') == 'success'
        assert result.get('manual_check_required') == False
        assert 'platforms_found' in result
        assert len(result['platforms_found']) > 0
    
    def test_extract_topics(self):
        """Test topic extraction from text"""
        service = SocialSearchService()
        text = "Python developer working on machine learning projects with AWS and Docker"
        topics = service._extract_topics(text)
        
        assert isinstance(topics, list)
        # Should extract relevant tech topics
        if len(topics) > 0:
            topics_lower = [t.lower() for t in topics]
            assert any('python' in t for t in topics_lower) or \
                   any('machine learning' in t for t in topics_lower) or \
                   any('aws' in t for t in topics_lower)


@patch('app.services.embedding_service.SentenceTransformer')
def test_service_singletons(mock_transformer):
    """Test that all services implement singleton pattern correctly"""
    mock_model = MagicMock()
    mock_transformer.return_value = mock_model
    
    emb1 = get_embedding_service()
    emb2 = get_embedding_service()
    assert emb1 is emb2
    
    # AI service singleton
    os.environ['GEMINI_API_KEY'] = 'test_key'
    ai1 = get_ai_service()
    ai2 = get_ai_service()
    assert ai1 is ai2
    
    # Social search singleton
    social1 = get_social_search_service()
    social2 = get_social_search_service()
    assert social1 is social2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
