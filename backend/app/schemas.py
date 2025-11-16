from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobDescriptionCreate(BaseModel):
    title: str
    description_text: str


class JobDescriptionOut(BaseModel):
    id: int
    title: str
    description_text: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None


class CandidateCreate(CandidateBase):
    cv_filename: str
    cv_text: str
    cover_letter_filename: Optional[str] = None
    cover_letter_text: Optional[str] = None


class CandidateOut(CandidateBase):
    id: int
    cv_filename: Optional[str] = None
    cover_letter_filename: Optional[str] = None
    jd_id: Optional[int] = None
    jd_match_score: Optional[float] = None
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    overall_score: Optional[float] = None
    cv_score: Optional[float] = None
    cover_letter_score: Optional[float] = None
    final_score: Optional[float] = None
    processing_status: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CandidateDetails(CandidateOut):
    cv_analysis: Optional[dict] = None
    cover_letter_analysis: Optional[dict] = None
    work_experience: Optional[List] = None
    education: Optional[List] = None
    skills: Optional[List[str]] = None
    online_presence: Optional[dict] = None
    social_media_presence: Optional[dict] = None
    work_verification: Optional[dict] = None
    
    class Config:
        from_attributes = True
