import os
import json
import google.generativeai as genai
from typing import Dict, Optional


class AIAnalyzer:
    """Service for AI-powered CV and cover letter analysis"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_resume_with_gemini(self, resume_text: str, job_text: Optional[str] = None) -> Dict:
        """
        Analyze resume with Gemini AI, optionally considering job description.
        
        Args:
            resume_text: Resume/CV text
            job_text: Optional job description text for job-aware analysis
            
        Returns:
            Dictionary with strengths, gaps, recommended_questions, and model_fit_score
        """
        if job_text:
            prompt = f"""Analyze the following resume in the context of this job description. Provide a comprehensive evaluation.

Job Description:
{job_text[:3000]}

Resume:
{resume_text[:4000]}

Provide your response in the following JSON format:
{{
    "strengths": [<list of key strengths relevant to the job>],
    "gaps": [<list of gaps or areas for improvement>],
    "recommended_questions": [<interview questions to ask based on resume and job>],
    "model_fit_score": <score from 0-100 indicating how well candidate fits the job>,
    "key_match_points": [<specific points where resume aligns with job requirements>],
    "summary": "<brief overall assessment>"
}}"""
        else:
            prompt = f"""Analyze the following resume and provide a comprehensive evaluation.

Resume:
{resume_text[:4000]}

Provide your response in the following JSON format:
{{
    "strengths": [<list of key strengths>],
    "gaps": [<list of areas for improvement>],
    "recommended_questions": [<suggested interview questions>],
    "model_fit_score": <score from 0-100 indicating overall quality>,
    "summary": "<brief overall assessment>"
}}"""
        
        try:
            system_prompt = "You are an expert HR recruiter and career advisor. Provide objective, constructive feedback."
            full_prompt = f"{system_prompt}\n\n{prompt}\n\nProvide your response as a valid JSON object."
            
            response = self.model.generate_content(full_prompt)
            
            if not response.text:
                raise ValueError("Gemini API returned empty response")
            
            # Clean up response text (remove markdown code blocks if present)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response as JSON: {e}")
            print(f"Response was: {response.text if 'response' in locals() else 'No response'}")
            return {
                "strengths": ["Unable to parse AI response"],
                "gaps": ["Analysis parsing error occurred"],
                "recommended_questions": ["What are your key qualifications for this role?"],
                "model_fit_score": 50,
                "summary": "Error occurred during analysis"
            }
        except Exception as e:
            print(f"Error in Gemini analysis: {str(e)}")
            return {
                "strengths": ["Unable to complete AI analysis"],
                "gaps": ["Analysis error occurred"],
                "recommended_questions": ["Tell me about your experience"],
                "model_fit_score": 50,
                "summary": f"Error: {str(e)}"
            }
    
    def analyze_cv(self, cv_text: str, job_text: Optional[str] = None) -> Dict:
        """
        Analyze CV content and generate score out of 60 points.
        If job_text is provided, scoring considers job relevance.
        """
        job_context = ""
        if job_text:
            job_context = f"""
Job Description Context:
{job_text[:2000]}

Consider the above job requirements when evaluating the CV.
"""
        
        prompt = f"""{job_context}

Analyze the following CV and provide a detailed evaluation. Score it out of 60 points based on:
- Relevant work experience (20 points)
- Skills match and technical expertise (15 points)
- Education qualifications (10 points)
- Career progression and growth (8 points)
- Professional achievements (5 points)
- Document quality and presentation (2 points)

CV Content:
{cv_text[:4000]}

Provide your response in the following JSON format:
{{
    "score": <number out of 60>,
    "breakdown": {{
        "work_experience": <score out of 20>,
        "skills": <score out of 15>,
        "education": <score out of 10>,
        "career_progression": <score out of 8>,
        "achievements": <score out of 5>,
        "presentation": <score out of 2>
    }},
    "strengths": [<list of key strengths>],
    "areas_for_improvement": [<list of areas to improve>],
    "key_qualifications": [<list of notable qualifications>],
    "years_of_experience": <estimated years>,
    "summary": "<brief overall summary>"
}}"""

        try:
            system_prompt = "You are an expert HR recruiter and CV analyst. Provide objective, fair, and constructive feedback."
            full_prompt = f"{system_prompt}\n\n{prompt}\n\nProvide your response as a valid JSON object."
            
            response = self.model.generate_content(full_prompt)
            
            if not response.text:
                raise ValueError("Gemini API returned empty response")
            
            result = json.loads(response.text)
            return result
        except Exception as e:
            print(f"Error analyzing CV: {str(e)}")
            return {
                "score": 30,
                "breakdown": {
                    "work_experience": 10,
                    "skills": 8,
                    "education": 5,
                    "career_progression": 4,
                    "achievements": 2,
                    "presentation": 1
                },
                "strengths": ["Unable to fully analyze"],
                "areas_for_improvement": ["Analysis error occurred"],
                "key_qualifications": [],
                "years_of_experience": 0,
                "summary": "Error occurred during analysis"
            }
    
    def analyze_cover_letter(self, cover_letter_text: str) -> Dict:
        """
        Analyze cover letter content and generate score out of 40 points
        """
        prompt = f"""Analyze the following cover letter and provide a detailed evaluation. Score it out of 40 points based on:
- Writing quality and professionalism (12 points)
- Motivation and enthusiasm (10 points)
- Company research and fit (8 points)
- Specific examples and achievements (7 points)
- Communication skills (3 points)

Cover Letter Content:
{cover_letter_text[:3000]}

Provide your response in the following JSON format:
{{
    "score": <number out of 40>,
    "breakdown": {{
        "writing_quality": <score out of 12>,
        "motivation": <score out of 10>,
        "company_fit": <score out of 8>,
        "examples": <score out of 7>,
        "communication": <score out of 3>
    }},
    "strengths": [<list of key strengths>],
    "areas_for_improvement": [<list of areas to improve>],
    "key_points": [<main points from the letter>],
    "summary": "<brief overall summary>"
}}"""

        try:
            system_prompt = "You are an expert HR recruiter analyzing cover letters. Provide objective and constructive feedback."
            full_prompt = f"{system_prompt}\n\n{prompt}\n\nProvide your response as a valid JSON object."
            
            response = self.model.generate_content(full_prompt)
            
            if not response.text:
                raise ValueError("Gemini API returned empty response")
            
            result = json.loads(response.text)
            return result
        except Exception as e:
            print(f"Error analyzing cover letter: {str(e)}")
            return {
                "score": 20,
                "breakdown": {
                    "writing_quality": 6,
                    "motivation": 5,
                    "company_fit": 4,
                    "examples": 3,
                    "communication": 2
                },
                "strengths": ["Unable to fully analyze"],
                "areas_for_improvement": ["Analysis error occurred"],
                "key_points": [],
                "summary": "Error occurred during analysis"
            }
    
    def generate_overall_assessment(self, cv_analysis: Dict, cover_letter_analysis: Optional[Dict] = None) -> Dict:
        """
        Generate overall assessment combining CV and cover letter scores
        """
        cv_score = cv_analysis.get("score", 0)
        
        if cover_letter_analysis:
            cover_letter_score = cover_letter_analysis.get("score", 0)
            overall_score = cv_score + cover_letter_score
        else:
            # If no cover letter, normalize CV score to 100
            overall_score = (cv_score / 60) * 100
            cover_letter_score = 0
        
        return {
            "overall_score": round(overall_score, 2),
            "cv_score": round(cv_score, 2),
            "cover_letter_score": round(cover_letter_score, 2) if cover_letter_analysis else None
        }
