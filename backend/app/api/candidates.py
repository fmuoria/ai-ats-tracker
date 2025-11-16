from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..models import get_db, Candidate, JobDescription
from ..services import DocumentParser, AIAnalyzer, BackgroundChecker
from ..services.embedding_service import get_embedding_service
from ..services.ai_service import get_ai_service
from ..services.social_search import get_social_search_service

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

# Thread pool for background processing
executor = ThreadPoolExecutor(max_workers=3)


def process_candidate_analysis(candidate_id: int, job_id: Optional[int], job_text: Optional[str]):
    """
    Background task to analyze candidate with job matching
    """
    from ..models.database import SessionLocal
    db = SessionLocal()
    
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return
        
        # Update status
        candidate.processing_status = "analyzing"
        db.commit()
        
        # Get services
        embedding_service = get_embedding_service()
        ai_service = get_ai_service()
        social_search_service = get_social_search_service()
        
        # Generate resume embedding
        resume_text = candidate.cv_text or ""
        resume_embedding = embedding_service.embed_text(resume_text)
        candidate.resume_embedding = resume_embedding
        
        # Get job description if provided
        job_description_text = job_text
        job_embedding = None
        
        if job_id:
            job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
            if job:
                candidate.jd_id = job_id
                job_description_text = job.description_text
                job_embedding = job.embedding
        
        # Compute JD match score if job provided
        if job_embedding:
            jd_match_score = embedding_service.compute_match_score(resume_embedding, job_embedding)
            candidate.jd_match_score = jd_match_score
        
        # Run AI analysis with Gemini
        ai_analysis = ai_service.analyze_resume_with_gemini(resume_text, job_description_text)
        
        # Extract skills
        candidate.matched_skills = ai_analysis.get("matched_skills", [])
        candidate.missing_skills = ai_analysis.get("missing_skills", [])
        
        # Store AI analysis results
        candidate.cv_analysis = {
            "strengths": ai_analysis.get("strengths", []),
            "gaps": ai_analysis.get("gaps", []),
            "recommended_questions": ai_analysis.get("recommended_questions", []),
            "summary": ai_analysis.get("summary", ""),
            "model_fit_score": ai_analysis.get("model_fit_score", 50)
        }
        
        # Calculate cv_score from model_fit_score (normalize to 60)
        model_fit = ai_analysis.get("model_fit_score", 50)
        candidate.cv_score = (model_fit / 100) * 60
        
        # Perform social search
        if candidate.name:
            social_results = social_search_service.search_public_profiles(
                candidate.name,
                candidate.email
            )
            candidate.social_media_presence = social_results
        
        # Calculate final score
        if candidate.jd_match_score is not None:
            # Weighted: 60% JD match + 40% CV structure score
            final_score = (0.6 * candidate.jd_match_score) + (0.4 * candidate.cv_score)
            candidate.final_score = round(final_score, 2)
        else:
            # No JD match, use CV score normalized to 100
            candidate.final_score = round((candidate.cv_score / 60) * 100, 2)
        
        # Update overall score for backward compatibility
        candidate.overall_score = candidate.final_score
        
        # Complete
        candidate.processing_status = "completed"
        db.commit()
        
    except Exception as e:
        print(f"Error processing candidate {candidate_id}: {str(e)}")
        if candidate:
            candidate.processing_status = "error"
            db.commit()
    finally:
        db.close()


@router.post("/upload")
async def upload_candidate_documents(
    background_tasks: BackgroundTasks,
    cv_file: UploadFile = File(...),
    cover_letter_file: Optional[UploadFile] = File(None),
    job_id: Optional[int] = Form(None),
    job_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload CV and optionally cover letter for a candidate
    Supports optional job_id or ad-hoc job_text for matching
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
            processing_status="pending_analysis"
        )
        
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        
        # Schedule background analysis
        background_tasks.add_task(
            process_candidate_analysis,
            candidate.id,
            job_id,
            job_text
        )
        
        return {
            "message": "Candidate documents uploaded successfully",
            "candidate_id": candidate.id,
            "status": "pending_analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@router.post("/{candidate_id}/analyze")
async def analyze_candidate(
    candidate_id: int, 
    jd_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Trigger AI analysis and background check for a candidate.
    If jd_id is provided, performs job-aware analysis with semantic matching.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.processing_status == "processing":
        raise HTTPException(status_code=400, detail="Candidate is already being processed")
    
    # Get job description if provided
    job_desc = None
    job_text = None
    if jd_id:
        from ..models import JobDescription
        job_desc = db.query(JobDescription).filter(JobDescription.id == jd_id).first()
        if not job_desc:
            raise HTTPException(status_code=404, detail="Job description not found")
        job_text = job_desc.description_text
        candidate.jd_id = jd_id
    
    # Update status
    candidate.processing_status = "processing"
    db.commit()
    
    try:
        # Initialize services
        ai_analyzer = AIAnalyzer()
        background_checker = BackgroundChecker()
        
        # Analyze CV (with job context if available)
        cv_analysis = ai_analyzer.analyze_cv(candidate.cv_text, job_text)
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
        
        # Compute JD matching if job description provided
        if job_desc and job_desc.embedding:
            from ..services import embed_text, compute_similarity_percentage
            
            # Compute CV embedding
            cv_embedding = embed_text(candidate.cv_text)
            
            # Compute semantic similarity
            jd_match_score = compute_similarity_percentage(cv_embedding, job_desc.embedding)
            candidate.jd_match_score = jd_match_score
            
            # Extract matched and missing skills
            candidate_skills = set(candidate.skills or [])
            # Use AI to identify JD required skills
            jd_skills_analysis = ai_analyzer.analyze_resume_with_gemini(
                job_text, 
                None  # No resume for JD analysis
            )
            
            # For now, use simple keyword matching for skills
            # In a more sophisticated version, we'd use NER or AI to extract skills
            import re
            jd_lower = job_text.lower()
            common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 
                           'docker', 'kubernetes', 'git', 'agile', 'scrum', 'leadership',
                           'communication', 'teamwork', 'problem solving']
            
            jd_skills = set()
            for skill in common_skills:
                if skill in jd_lower:
                    jd_skills.add(skill.capitalize())
            
            matched_skills = list(candidate_skills.intersection(jd_skills))
            missing_skills = list(jd_skills - candidate_skills)
            
            candidate.matched_skills = matched_skills
            candidate.missing_skills = missing_skills
            
            # Calculate final score: weighted combination of CV structural score and JD match
            # CV structural score (60%) + JD semantic match (40%)
            structural_score_normalized = (candidate.cv_score / 60) * 100  # Normalize to 0-100
            final_score = (structural_score_normalized * 0.6) + (jd_match_score * 0.4)
            candidate.final_score = round(final_score, 2)
        
        # Perform background check with enhanced social search
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
        
        # Enhanced social/online presence search
        from ..services import SocialSearchService
        social_search = SocialSearchService()
        enhanced_presence = social_search.search_online_presence(
            candidate.name,
            candidate.email,
            candidate.linkedin_url
        )
        # Merge with existing online presence data
        if candidate.online_presence:
            candidate.online_presence['enhanced_search'] = enhanced_presence
        else:
            candidate.online_presence = {'enhanced_search': enhanced_presence}
        
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


@router.post("/{candidate_id}/match")
async def match_candidate_to_job(
    candidate_id: int,
    background_tasks: BackgroundTasks,
    job_id: Optional[int] = Form(None),
    job_text: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Trigger job matching for an existing candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if not job_id and not job_text:
        raise HTTPException(status_code=400, detail="Either job_id or job_text must be provided")
    
    # Schedule background analysis
    background_tasks.add_task(
        process_candidate_analysis,
        candidate_id,
        job_id,
        job_text
    )
    
    return {
        "message": "Job matching started",
        "candidate_id": candidate_id,
        "status": "processing"
    }


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
