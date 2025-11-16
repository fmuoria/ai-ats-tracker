"""
Tests for job description endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)


def test_create_job_description():
    """Test creating a job description"""
    job_data = {
        "title": "Senior Python Developer",
        "description_text": "Looking for a senior Python developer with 5+ years experience in backend development, FastAPI, and cloud technologies."
    }
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        # Mock embedding response
        mock_embed.return_value = [0.1] * 384  # Mock embedding vector
        
        response = client.post("/api/jobs/", json=job_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == job_data["title"]
        assert data["description_text"] == job_data["description_text"]


def test_list_jobs():
    """Test listing job descriptions"""
    response = client.get("/api/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_job_by_id():
    """Test getting a specific job description"""
    # First create a job
    job_data = {
        "title": "Test Job",
        "description_text": "Test description"
    }
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        mock_embed.return_value = [0.1] * 384
        
        create_response = client.post("/api/jobs/", json=job_data)
        assert create_response.status_code == 200
        job_id = create_response.json()["id"]
        
        # Get the job
        get_response = client.get(f"/api/jobs/{job_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == job_id
        assert data["title"] == job_data["title"]


def test_get_nonexistent_job():
    """Test getting a job that doesn't exist"""
    response = client.get("/api/jobs/99999")
    assert response.status_code == 404


def test_delete_job():
    """Test deleting a job description"""
    # First create a job
    job_data = {
        "title": "Job to Delete",
        "description_text": "This will be deleted"
    }
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        mock_embed.return_value = [0.1] * 384
        
        create_response = client.post("/api/jobs/", json=job_data)
        job_id = create_response.json()["id"]
        
        # Delete the job
        delete_response = client.delete(f"/api/jobs/{job_id}")
        assert delete_response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f"/api/jobs/{job_id}")
        assert get_response.status_code == 404


def test_create_job_invalid_data():
    """Test creating job with invalid data"""
    invalid_data = {
        "title": "Test"
        # Missing description_text
    }
    
    response = client.post("/api/jobs/", json=invalid_data)
    assert response.status_code == 422  # Validation error


def test_candidate_upload_with_job():
    """Test uploading candidate with job matching"""
    # First create a job
    job_data = {
        "title": "Python Developer",
        "description_text": "Need Python expert"
    }
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        mock_embed.return_value = [0.1] * 384
        
        job_response = client.post("/api/jobs/", json=job_data)
        job_id = job_response.json()["id"]
        
        # Upload candidate with job
        sample_cv = b"John Doe - Python Developer with 5 years experience"
        files = {"cv_file": ("test_cv.txt", sample_cv, "text/plain")}
        data = {"job_id": str(job_id)}
        
        response = client.post("/api/candidates/upload", files=files, data=data)
        assert response.status_code == 200
        candidate_data = response.json()
        assert "candidate_id" in candidate_data
        assert candidate_data["status"] == "pending_analysis"


def test_candidate_upload_with_adhoc_job():
    """Test uploading candidate with ad-hoc job text"""
    sample_cv = b"Jane Smith - JavaScript Developer"
    adhoc_job = "Looking for JavaScript expert with React experience"
    
    files = {"cv_file": ("test_cv.txt", sample_cv, "text/plain")}
    data = {"job_text": adhoc_job}
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        mock_embed.return_value = [0.1] * 384
        
        response = client.post("/api/candidates/upload", files=files, data=data)
        assert response.status_code == 200
        candidate_data = response.json()
        assert "candidate_id" in candidate_data


def test_match_existing_candidate_to_job():
    """Test matching an existing candidate to a job"""
    # Create a candidate first
    sample_cv = b"Test candidate CV"
    files = {"cv_file": ("test.txt", sample_cv, "text/plain")}
    
    with patch('app.services.embedding_service.EmbeddingService.embed_text') as mock_embed:
        mock_embed.return_value = [0.1] * 384
        
        upload_response = client.post("/api/candidates/upload", files=files)
        candidate_id = upload_response.json()["candidate_id"]
        
        # Create a job
        job_data = {"title": "Test Job", "description_text": "Test description"}
        job_response = client.post("/api/jobs/", json=job_data)
        job_id = job_response.json()["id"]
        
        # Match candidate to job
        match_data = {"job_id": str(job_id)}
        match_response = client.post(
            f"/api/candidates/{candidate_id}/match",
            data=match_data
        )
        assert match_response.status_code == 200
        match_result = match_response.json()
        assert match_result["status"] == "processing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
