from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..models import get_db, Candidate
from ..services import DocumentParser, AIAnalyzer, BackgroundChecker

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

# Thread pool for background processing
executor = ThreadPoolExecutor(max_workers=3)


@router.post("/upload")
async def upload_candidate_documents(
    cv_file: UploadFile = File(...),
    cover_letter_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Upload CV and optionally cover letter for a candidate
    """
    # Validate file types
    allowed_extensions = ['pdf', 'docx', 'txt']
    cv_ext = cv_file.filename.split('.')[-1].lower()
    
    if cv_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Invalid CV file type. Allowed: {', '.join(allowed_extensions)}")
    
    if cover_letter_file:
        cl_ext = cover_letter_file.filename.split('.')[-1].lower()
        if cl_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Invalid cover letter file type. Allowed: {', '.join(allowed_extensions)}")
    
    try:
        # Read file contents
        cv_content = await cv_file.read()
        cover_letter_content = await cover_letter_file.read() if cover_letter_file else None
        
        # Parse CV
        parser = DocumentParser()
        cv_text = parser.parse_document(cv_content, cv_file.filename)
        candidate_info = parser.extract_candidate_info(cv_text)
        
        # Parse cover letter if provided
        cover_letter_text = None
        if cover_letter_content:
            cover_letter_text = parser.parse_document(cover_letter_content, cover_letter_file.filename)
        
        # Create candidate record
        candidate = Candidate(
            name=candidate_info.get('name'),
            email=candidate_info.get('email'),
            phone=candidate_info.get('phone'),
            linkedin_url=candidate_info.get('linkedin_url'),
            cv_filename=cv_file.filename,
            cv_text=cv_text,
            cover_letter_filename=cover_letter_file.filename if cover_letter_file else None,
            cover_letter_text=cover_letter_text,
            skills=candidate_info.get('skills', []),
            processing_status="pending"
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        return {
            "message": "Candidate documents uploaded successfully",
            "candidate_id": candidate.id,
            "status": "pending_analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@router.post("/{candidate_id}/analyze")
async def analyze_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Trigger AI analysis and background check for a candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.processing_status == "processing":
        raise HTTPException(status_code=400, detail="Candidate is already being processed")
    
    # Update status
    candidate.processing_status = "processing"
    db.commit()
    
    try:
        # Initialize services
        ai_analyzer = AIAnalyzer()
        background_checker = BackgroundChecker()
        
        # Analyze CV
        cv_analysis = ai_analyzer.analyze_cv(candidate.cv_text)
        candidate.cv_analysis = cv_analysis
        candidate.cv_score = cv_analysis.get('score', 0)
        
        # Analyze cover letter if available
        cover_letter_analysis = None
        if candidate.cover_letter_text:
            cover_letter_analysis = ai_analyzer.analyze_cover_letter(candidate.cover_letter_text)
            candidate.cover_letter_analysis = cover_letter_analysis
            candidate.cover_letter_score = cover_letter_analysis.get('score', 0)
        
        # Calculate overall score
        scores = ai_analyzer.generate_overall_assessment(cv_analysis, cover_letter_analysis)
        candidate.overall_score = scores['overall_score']
        
        # Perform background check
        candidate_info = {
            'name': candidate.name,
            'email': candidate.email,
            'phone': candidate.phone,
            'linkedin_url': candidate.linkedin_url,
            'work_experience': candidate.work_experience or []
        }
        
        background_results = background_checker.perform_full_background_check(candidate_info)
        candidate.online_presence = background_results.get('online_presence')
        candidate.social_media_presence = background_results.get('social_media')
        candidate.work_verification = background_results.get('work_verification')
        
        # Update status
        candidate.processing_status = "completed"
        db.commit()
        db.refresh(candidate)
        
        return {
            "message": "Analysis completed successfully",
            "candidate_id": candidate.id,
            "overall_score": candidate.overall_score,
            "status": "completed"
        }
        
    except Exception as e:
        candidate.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Error analyzing candidate: {str(e)}")


@router.get("/")
async def list_candidates(db: Session = Depends(get_db)):
    """
    List all candidates with their basic information and scores
    """
    candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    
    return {
        "total": len(candidates),
        "candidates": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "overall_score": c.overall_score,
                "processing_status": c.processing_status,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in candidates
        ]
    }


@router.get("/{candidate_id}")
async def get_candidate_details(candidate_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information and analysis results for a candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate.to_dict()


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """
    Delete a candidate record
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"}
