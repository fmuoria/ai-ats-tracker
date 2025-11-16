import os
import json
import re
import google.generativeai as genai
from typing import Dict, Optional, List


class AIService:
    """Enhanced AI service for resume analysis with job description matching using Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from response, handling markdown code blocks"""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        
        # Clean up the text
        response_text = response_text.strip()
        
        # Try to find JSON object
        if not response_text.startswith('{'):
            json_start = response_text.find('{')
            if json_start != -1:
                response_text = response_text[json_start:]
        
        if not response_text.endswith('}'):
            json_end = response_text.rfind('}')
            if json_end != -1:
                response_text = response_text[:json_end + 1]
        
        return json.loads(response_text)
    
    def analyze_resume_with_gemini(self, resume_text: str, job_text: Optional[str] = None) -> Dict:
        """
        Analyze resume with Gemini, optionally comparing against job description
        Returns: strengths, gaps, recommended_questions, model_fit_score (0-100)
        """
        if job_text:
            prompt = f"""You are an expert HR recruiter. Analyze the following resume against the job description.

Job Description:
{job_text[:2000]}

Resume:
{resume_text[:4000]}

Provide a detailed analysis in the following JSON format:
{{
    "model_fit_score": <number 0-100 indicating how well the candidate fits the job>,
    "strengths": [<list of 3-5 key strengths relevant to the job>],
    "gaps": [<list of 2-4 areas where candidate may not fully meet requirements>],
    "recommended_questions": [<list of 3-5 interview questions to ask>],
    "matched_skills": [<list of skills from resume that match job requirements>],
    "missing_skills": [<list of skills in job description not found in resume>],
    "summary": "<brief 2-3 sentence overall assessment>"
}}

Respond ONLY with valid JSON, no additional text."""
        else:
            prompt = f"""You are an expert HR recruiter. Analyze the following resume and provide insights.

Resume:
{resume_text[:4000]}

Provide a detailed analysis in the following JSON format:
{{
    "model_fit_score": <number 0-100 indicating overall quality of the resume>,
    "strengths": [<list of 3-5 key strengths>],
    "gaps": [<list of 2-4 potential areas for improvement>],
    "recommended_questions": [<list of 3-5 general interview questions>],
    "matched_skills": [<list of notable skills found in resume>],
    "missing_skills": [],
    "summary": "<brief 2-3 sentence overall assessment>"
}}

Respond ONLY with valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise ValueError("Gemini API returned empty response")
            
            result = self._parse_json_response(response.text)
            
            # Validate required fields
            if "model_fit_score" not in result:
                result["model_fit_score"] = 50
            if "strengths" not in result:
                result["strengths"] = []
            if "gaps" not in result:
                result["gaps"] = []
            if "recommended_questions" not in result:
                result["recommended_questions"] = []
            if "matched_skills" not in result:
                result["matched_skills"] = []
            if "missing_skills" not in result:
                result["missing_skills"] = []
            
            return result
            
        except Exception as e:
            print(f"Error analyzing resume with Gemini: {str(e)}")
            return {
                "model_fit_score": 50,
                "strengths": ["Unable to fully analyze due to error"],
                "gaps": ["Analysis error occurred"],
                "recommended_questions": ["Please review manually"],
                "matched_skills": [],
                "missing_skills": [],
                "summary": f"Error occurred during analysis: {str(e)}"
            }
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extract skills from text using simple keyword matching
        This is a fallback/supplement to AI analysis
        """
        common_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "fastapi", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "git", "ci/cd",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "machine learning", "deep learning", "ai", "data science", "tensorflow", "pytorch",
            "leadership", "communication", "project management", "agile", "scrum",
            "rest api", "graphql", "microservices", "cloud computing", "devops"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates


# Singleton instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
