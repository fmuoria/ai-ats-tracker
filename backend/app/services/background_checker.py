import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time
import validators


class BackgroundChecker:
    """Service for performing online background checks"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def validate_email(self, email: str) -> Dict:
        """Validate email format and professionalism"""
        if not email:
            return {"valid": False, "professional": False, "note": "No email provided"}
        
        # Basic validation
        if not validators.email(email):
            return {"valid": False, "professional": False, "note": "Invalid email format"}
        
        # Check if it's a professional email (not free email services)
        free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        domain = email.split('@')[1].lower()
        is_professional = domain not in free_domains
        
        return {
            "valid": True,
            "professional": is_professional,
            "domain": domain,
            "note": "Professional email domain" if is_professional else "Personal email domain"
        }
    
    def validate_phone(self, phone: str) -> Dict:
        """Validate phone number format"""
        if not phone:
            return {"valid": False, "note": "No phone number provided"}
        
        # Remove common formatting
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Check length (10-15 digits is reasonable)
        is_valid = 10 <= len(cleaned.replace('+', '')) <= 15
        
        return {
            "valid": is_valid,
            "formatted": phone,
            "note": "Valid phone format" if is_valid else "Invalid phone format"
        }
    
    def check_linkedin_profile(self, linkedin_url: str) -> Dict:
        """Check if LinkedIn profile exists and extract basic info"""
        if not linkedin_url:
            return {
                "found": False,
                "url": None,
                "note": "No LinkedIn URL provided"
            }
        
        # Normalize URL
        if not linkedin_url.startswith('http'):
            linkedin_url = 'https://' + linkedin_url
        
        try:
            # Simple check - we won't scrape LinkedIn due to ToS
            # Just verify the URL format is valid
            if 'linkedin.com/in/' in linkedin_url:
                return {
                    "found": True,
                    "url": linkedin_url,
                    "note": "LinkedIn profile URL provided (profile verification requires manual check)"
                }
            else:
                return {
                    "found": False,
                    "url": linkedin_url,
                    "note": "Invalid LinkedIn profile URL format"
                }
        except Exception as e:
            return {
                "found": False,
                "url": linkedin_url,
                "note": f"Error checking LinkedIn: {str(e)}"
            }
    
    def search_online_presence(self, name: str, email: Optional[str] = None) -> Dict:
        """
        Search for candidate's online presence
        Note: This is a simplified implementation. Real-world would use search APIs.
        """
        if not name:
            return {
                "search_attempted": False,
                "findings": [],
                "note": "Insufficient information for search"
            }
        
        findings = []
        search_query = name
        
        # In a real implementation, this would use Google Custom Search API
        # For now, we'll return a structured response indicating what would be searched
        
        findings.append({
            "type": "general_search",
            "query": search_query,
            "note": "Manual search recommended: Search for candidate's name on Google to find professional profiles, publications, and mentions"
        })
        
        if email:
            findings.append({
                "type": "email_search",
                "query": email,
                "note": "Email-based search can reveal professional accounts and registrations"
            })
        
        return {
            "search_attempted": True,
            "search_query": search_query,
            "findings": findings,
            "recommendation": "Perform manual web search to verify online presence",
            "note": "Automated web search requires Search API configuration (see .env.example)"
        }
    
    def check_social_media_presence(self, name: str, email: Optional[str] = None) -> Dict:
        """
        Check for social media presence across major platforms
        Note: This is a simplified implementation
        """
        platforms = {
            "linkedin": "Professional networking",
            "github": "Developer platform",
            "twitter": "Microblogging",
            "stackoverflow": "Developer Q&A",
            "medium": "Blogging platform"
        }
        
        results = []
        
        for platform, description in platforms.items():
            results.append({
                "platform": platform,
                "description": description,
                "status": "manual_check_required",
                "note": f"Search for candidate on {platform} to verify presence"
            })
        
        return {
            "platforms_checked": list(platforms.keys()),
            "results": results,
            "overall_assessment": "Manual verification recommended for social media presence",
            "note": "Automated social media checking requires platform-specific API access"
        }
    
    def verify_work_experience(self, work_experiences: List[Dict]) -> Dict:
        """
        Attempt to verify work experience
        Note: This is a simplified implementation
        """
        if not work_experiences:
            return {
                "attempted": False,
                "results": [],
                "note": "No work experience provided for verification"
            }
        
        verification_results = []
        
        for exp in work_experiences:
            company = exp.get('company', '')
            position = exp.get('position', '')
            
            if not company:
                continue
            
            result = {
                "company": company,
                "position": position,
                "verification_status": "manual_check_required",
                "confidence": "unknown",
                "method": "Company website or LinkedIn company page check recommended",
                "note": f"Search '{company}' website and LinkedIn for employee directory"
            }
            
            verification_results.append(result)
        
        return {
            "attempted": True,
            "total_positions": len(work_experiences),
            "results": verification_results,
            "overall_assessment": "Manual verification recommended through company websites and LinkedIn",
            "note": "Automated employment verification requires specialized services or APIs"
        }
    
    def perform_full_background_check(self, candidate_info: Dict) -> Dict:
        """Perform comprehensive background check"""
        name = candidate_info.get('name')
        email = candidate_info.get('email')
        phone = candidate_info.get('phone')
        linkedin = candidate_info.get('linkedin_url')
        work_experience = candidate_info.get('work_experience', [])
        
        return {
            "contact_validation": {
                "email": self.validate_email(email),
                "phone": self.validate_phone(phone),
                "linkedin": self.check_linkedin_profile(linkedin)
            },
            "online_presence": self.search_online_presence(name, email),
            "social_media": self.check_social_media_presence(name, email),
            "work_verification": self.verify_work_experience(work_experience)
        }
