from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models import get_db, JobDescription
from ..schemas import JobDescriptionCreate, JobDescriptionOut
from ..services.embedding_service import get_embedding_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/", response_model=JobDescriptionOut)
async def create_job_description(
    job_data: JobDescriptionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job description and compute its embedding
    """
    try:
        # Get embedding service
        embedding_service = get_embedding_service()
        
        # Generate embedding for job description
        embedding = embedding_service.embed_text(job_data.description_text)
        
        # Create job description record
        job = JobDescription(
            title=job_data.title,
            description_text=job_data.description_text,
            embedding=embedding
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating job description: {str(e)}")


@router.get("/", response_model=List[JobDescriptionOut])
async def list_job_descriptions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all job descriptions
    """
    jobs = db.query(JobDescription).order_by(
        JobDescription.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return jobs


@router.get("/{job_id}", response_model=JobDescriptionOut)
async def get_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific job description by ID
    """
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return job


@router.delete("/{job_id}")
async def delete_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job description
    """
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job description deleted successfully"}
