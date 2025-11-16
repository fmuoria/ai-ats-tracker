"""
API endpoints for Job Description management
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..models import get_db, JobDescription
from ..services import DocumentParser, embed_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/job-descriptions", tags=["job-descriptions"])


@router.post("/")
async def create_job_description(
    title: str = Form(...),
    description_file: Optional[UploadFile] = File(None),
    description_text: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Create a new job description.
    Can provide either a file or text directly.
    """
    if not description_file and not description_text:
        raise HTTPException(
            status_code=400, 
            detail="Either description_file or description_text must be provided"
        )
    
    try:
        # Extract text from file or use provided text
        if description_file:
            allowed_extensions = ['pdf', 'docx', 'txt']
            file_ext = description_file.filename.split('.')[-1].lower()
            
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
                )
            
            file_content = await description_file.read()
            parser = DocumentParser()
            jd_text = parser.parse_document(file_content, description_file.filename)
        else:
            jd_text = description_text
        
        # Create job description record
        job_desc = JobDescription(
            title=title,
            description_text=jd_text
        )
        
        db.add(job_desc)
        db.commit()
        db.refresh(job_desc)
        
        # Compute embedding in background
        if background_tasks:
            background_tasks.add_task(_compute_jd_embedding, job_desc.id, jd_text)
        else:
            # Compute immediately if no background tasks
            _compute_jd_embedding(job_desc.id, jd_text)
        
        return {
            "message": "Job description created successfully",
            "job_description_id": job_desc.id,
            "title": job_desc.title
        }
        
    except Exception as e:
        logger.error(f"Error creating job description: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job description: {str(e)}")


def _compute_jd_embedding(jd_id: int, jd_text: str):
    """Background task to compute and store job description embedding"""
    try:
        from ..models import SessionLocal
        db = SessionLocal()
        
        try:
            # Compute embedding
            logger.info(f"Computing embedding for JD {jd_id}")
            embedding = embed_text(jd_text)
            
            # Update job description with embedding
            job_desc = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
            if job_desc:
                job_desc.embedding = embedding
                db.commit()
                logger.info(f"Embedding computed and stored for JD {jd_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error computing embedding for JD {jd_id}: {e}")


@router.get("/")
async def list_job_descriptions(db: Session = Depends(get_db)):
    """
    List all job descriptions
    """
    job_descriptions = db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()
    
    return {
        "total": len(job_descriptions),
        "job_descriptions": [
            {
                "id": jd.id,
                "title": jd.title,
                "description_preview": jd.description_text[:200] + "..." if len(jd.description_text) > 200 else jd.description_text,
                "has_embedding": jd.embedding is not None,
                "created_at": jd.created_at.isoformat() if jd.created_at else None
            }
            for jd in job_descriptions
        ]
    }


@router.get("/{jd_id}")
async def get_job_description(jd_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific job description
    """
    job_desc = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    
    if not job_desc:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    return job_desc.to_dict()


@router.delete("/{jd_id}")
async def delete_job_description(jd_id: int, db: Session = Depends(get_db)):
    """
    Delete a job description
    """
    job_desc = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
    
    if not job_desc:
        raise HTTPException(status_code=404, detail="Job description not found")
    
    db.delete(job_desc)
    db.commit()
    
    return {"message": "Job description deleted successfully"}
