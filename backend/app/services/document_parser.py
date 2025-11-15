import re
import PyPDF2
from docx import Document
from typing import Dict, Optional, List
import io


class DocumentParser:
    """Service for parsing CV and cover letter documents"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1').strip()
            except Exception as e:
                raise Exception(f"Error parsing TXT: {str(e)}")
    
    @classmethod
    def parse_document(cls, file_content: bytes, filename: str) -> str:
        """Parse document based on file extension"""
        extension = filename.lower().split('.')[-1]
        
        if extension == 'pdf':
            return cls.extract_text_from_pdf(file_content)
        elif extension == 'docx':
            return cls.extract_text_from_docx(file_content)
        elif extension == 'txt':
            return cls.extract_text_from_txt(file_content)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Various phone number patterns
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?\d{10,15}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    @staticmethod
    def extract_linkedin_url(text: str) -> Optional[str]:
        """Extract LinkedIn URL from text"""
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+'
        urls = re.findall(linkedin_pattern, text, re.IGNORECASE)
        return urls[0] if urls else None
    
    @staticmethod
    def extract_name(text: str) -> Optional[str]:
        """Extract candidate name from text (first non-empty line)"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Usually the name is in the first few lines
            first_line = lines[0]
            # Check if it looks like a name (not too long, no special characters)
            if len(first_line) < 50 and not re.search(r'[0-9@#$%]', first_line):
                return first_line
        return None
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract skills from text"""
        # Common skills section headers
        skills_pattern = r'(?:Skills?|Technical Skills?|Core Competencies|Expertise)[\s:]+(.+?)(?=\n\n|\n[A-Z]|$)'
        matches = re.findall(skills_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if matches:
            skills_text = matches[0]
            # Split by common delimiters
            skills = re.split(r'[,;•\n]', skills_text)
            # Clean and filter
            skills = [s.strip() for s in skills if s.strip() and len(s.strip()) > 2]
            return skills[:20]  # Limit to 20 skills
        
        return []
    
    @classmethod
    def extract_candidate_info(cls, text: str) -> Dict:
        """Extract all candidate information from document text"""
        return {
            "name": cls.extract_name(text),
            "email": cls.extract_email(text),
            "phone": cls.extract_phone(text),
            "linkedin_url": cls.extract_linkedin_url(text),
            "skills": cls.extract_skills(text)
        }
