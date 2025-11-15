from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    linkedin_url = Column(String)
    
    # Document Information
    cv_filename = Column(String)
    cv_text = Column(Text)
    cover_letter_filename = Column(String)
    cover_letter_text = Column(Text)
    
    # Scores
    overall_score = Column(Float)
    cv_score = Column(Float)
    cover_letter_score = Column(Float)
    
    # Analysis Results (stored as JSON)
    cv_analysis = Column(JSON)
    cover_letter_analysis = Column(JSON)
    work_experience = Column(JSON)
    education = Column(JSON)
    skills = Column(JSON)
    
    # Background Check Results
    online_presence = Column(JSON)
    social_media_presence = Column(JSON)
    work_verification = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    
    def to_dict(self):
        """Convert candidate to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin_url": self.linkedin_url,
            "cv_filename": self.cv_filename,
            "cover_letter_filename": self.cover_letter_filename,
            "overall_score": self.overall_score,
            "cv_score": self.cv_score,
            "cover_letter_score": self.cover_letter_score,
            "cv_analysis": self.cv_analysis,
            "cover_letter_analysis": self.cover_letter_analysis,
            "work_experience": self.work_experience,
            "education": self.education,
            "skills": self.skills,
            "online_presence": self.online_presence,
            "social_media_presence": self.social_media_presence,
            "work_verification": self.work_verification,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processing_status": self.processing_status,
        }
