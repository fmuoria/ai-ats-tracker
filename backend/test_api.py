"""
Basic tests for the AI ATS Tracker API

To run tests:
1. Install test dependencies: pip install pytest pytest-asyncio httpx
2. Set OPENAI_API_KEY in environment
3. Run: pytest test_api.py
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "AI ATS Tracker API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_candidates_empty():
    """Test listing candidates when database is empty"""
    response = client.get("/api/candidates/")
    assert response.status_code == 200
    data = response.json()
    assert "candidates" in data
    assert "total" in data
    assert isinstance(data["candidates"], list)


def test_upload_without_file():
    """Test upload endpoint without file returns error"""
    response = client.post("/api/candidates/upload")
    assert response.status_code == 422  # Unprocessable Entity


def test_get_nonexistent_candidate():
    """Test getting a candidate that doesn't exist"""
    response = client.get("/api/candidates/99999")
    assert response.status_code == 404


def test_delete_nonexistent_candidate():
    """Test deleting a candidate that doesn't exist"""
    response = client.delete("/api/candidates/99999")
    assert response.status_code == 404


def test_analyze_nonexistent_candidate():
    """Test analyzing a candidate that doesn't exist"""
    response = client.post("/api/candidates/99999/analyze")
    assert response.status_code == 404


# Integration test (requires actual file upload)
def test_full_candidate_workflow():
    """
    Test full workflow: upload -> analyze -> get -> delete
    Note: Requires OPENAI_API_KEY to be set
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set")
    
    # Create a sample CV content
    sample_cv = b"""John Doe
john.doe@example.com
+1234567890
https://linkedin.com/in/johndoe

PROFESSIONAL EXPERIENCE
Senior Software Engineer - Tech Company (2020-Present)
- Developed scalable web applications
- Led team of 5 engineers
- Improved system performance by 40%

Software Engineer - StartUp Inc (2018-2020)
- Built RESTful APIs
- Implemented CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2014-2018)

SKILLS
Python, JavaScript, React, FastAPI, Docker, AWS
"""
    
    # Upload candidate
    files = {"cv_file": ("test_cv.txt", sample_cv, "text/plain")}
    upload_response = client.post("/api/candidates/upload", files=files)
    
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert "candidate_id" in upload_data
    
    candidate_id = upload_data["candidate_id"]
    
    # Analyze candidate
    analyze_response = client.post(f"/api/candidates/{candidate_id}/analyze")
    assert analyze_response.status_code == 200
    
    # Get candidate details
    get_response = client.get(f"/api/candidates/{candidate_id}")
    assert get_response.status_code == 200
    candidate_data = get_response.json()
    assert candidate_data["id"] == candidate_id
    assert candidate_data["processing_status"] == "completed"
    assert candidate_data["overall_score"] is not None
    
    # Delete candidate
    delete_response = client.delete(f"/api/candidates/{candidate_id}")
    assert delete_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
