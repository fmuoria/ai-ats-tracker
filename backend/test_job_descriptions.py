"""
Tests for Job Description functionality
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)


def test_create_job_description_with_text():
    """Test creating a job description with direct text"""
    response = client.post(
        "/api/job-descriptions/",
        data={
            "title": "Senior Software Engineer",
            "description_text": """
We are seeking a Senior Software Engineer with 5+ years of experience.

Requirements:
- Strong Python programming skills
- Experience with FastAPI and Django
- Knowledge of databases (PostgreSQL, MongoDB)
- AWS cloud experience
- Docker and Kubernetes
- Team leadership skills

Responsibilities:
- Design and implement scalable backend systems
- Mentor junior developers
- Participate in architecture decisions
            """
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "job_description_id" in data
    assert data["title"] == "Senior Software Engineer"
    
    return data["job_description_id"]


def test_list_job_descriptions():
    """Test listing all job descriptions"""
    # First create one
    test_create_job_description_with_text()
    
    # Then list
    response = client.get("/api/job-descriptions/")
    assert response.status_code == 200
    data = response.json()
    assert "job_descriptions" in data
    assert "total" in data
    assert data["total"] > 0


def test_get_job_description():
    """Test getting a specific job description"""
    # Create a job description first
    jd_id = test_create_job_description_with_text()
    
    # Get it
    response = client.get(f"/api/job-descriptions/{jd_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == jd_id
    assert data["title"] == "Senior Software Engineer"


def test_get_nonexistent_job_description():
    """Test getting a job description that doesn't exist"""
    response = client.get("/api/job-descriptions/99999")
    assert response.status_code == 404


def test_delete_job_description():
    """Test deleting a job description"""
    # Create a job description first
    jd_id = test_create_job_description_with_text()
    
    # Delete it
    response = client.delete(f"/api/job-descriptions/{jd_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get(f"/api/job-descriptions/{jd_id}")
    assert response.status_code == 404


def test_create_job_description_without_data():
    """Test that creating JD without text or file fails"""
    response = client.post(
        "/api/job-descriptions/",
        data={"title": "Test Job"}
    )
    assert response.status_code == 400


def test_candidate_analysis_with_job_description():
    """Test analyzing a candidate against a job description"""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")
    
    # Create a job description
    jd_response = client.post(
        "/api/job-descriptions/",
        data={
            "title": "Python Developer",
            "description_text": "We need a Python developer with FastAPI experience"
        }
    )
    assert jd_response.status_code == 200
    jd_id = jd_response.json()["job_description_id"]
    
    # Upload a candidate
    sample_cv = b"""John Doe
john.doe@example.com
+1234567890

PROFESSIONAL EXPERIENCE
Senior Python Developer - Tech Company (2020-Present)
- Developed FastAPI applications
- Built scalable microservices
- Led team of developers

SKILLS
Python, FastAPI, Docker, AWS, PostgreSQL
"""
    
    files = {"cv_file": ("test_cv.txt", sample_cv, "text/plain")}
    upload_response = client.post("/api/candidates/upload", files=files)
    assert upload_response.status_code == 200
    candidate_id = upload_response.json()["candidate_id"]
    
    # Analyze with job description
    analyze_response = client.post(
        f"/api/candidates/{candidate_id}/analyze?jd_id={jd_id}"
    )
    assert analyze_response.status_code == 200
    
    # Get candidate details and verify JD matching fields
    candidate_response = client.get(f"/api/candidates/{candidate_id}")
    assert candidate_response.status_code == 200
    candidate_data = candidate_response.json()
    
    assert candidate_data["jd_id"] == jd_id
    assert "jd_match_score" in candidate_data
    assert "matched_skills" in candidate_data
    assert "missing_skills" in candidate_data
    assert "final_score" in candidate_data
    
    # Cleanup
    client.delete(f"/api/candidates/{candidate_id}")
    client.delete(f"/api/job-descriptions/{jd_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
