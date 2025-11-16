import os
import requests
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from collections import Counter
import re


class SocialSearchService:
    """
    Service for safe public social media profile search
    Uses SerpAPI if available, otherwise returns manual check required
    """
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.search_enabled = os.getenv("SOCIAL_SEARCH_ENABLED", "true").lower() == "true"
        self.timeout = 10
        
    def search_public_profiles(self, candidate_name: str, email: Optional[str] = None) -> Dict:
        """
        Search for public profiles using SerpAPI if available
        Returns summary or manual_check_required flag
        """
        if not self.search_enabled:
            return {
                "status": "disabled",
                "manual_check_required": True,
                "message": "Social search is disabled"
            }
        
        if not self.serpapi_key:
            return {
                "status": "no_api_key",
                "manual_check_required": True,
                "message": "SerpAPI key not configured. Please verify profiles manually.",
                "suggestions": [
                    f"Search LinkedIn for: {candidate_name}",
                    f"Search GitHub for: {candidate_name}",
                    f"Search StackOverflow for: {candidate_name}"
                ]
            }
        
        try:
            # Build search query
            search_query = f"{candidate_name}"
            if email:
                # Extract username from email for better search
                username = email.split('@')[0]
                search_query += f" {username}"
            
            results = self._search_with_serpapi(search_query)
            
            if not results or len(results) == 0:
                return {
                    "status": "no_results",
                    "manual_check_required": True,
                    "message": f"No public profiles found for {candidate_name}"
                }
            
            # Analyze results
            profile_summary = self._analyze_search_results(results)
            
            return {
                "status": "success",
                "manual_check_required": False,
                "summary": profile_summary.get("summary", "Profile found"),
                "platforms_found": profile_summary.get("platforms", []),
                "topics": profile_summary.get("topics", []),
                "profile_links": profile_summary.get("links", [])[:5]  # Limit to top 5
            }
            
        except Exception as e:
            print(f"Error during social search: {str(e)}")
            return {
                "status": "error",
                "manual_check_required": True,
                "message": f"Error during search: {str(e)}. Please verify manually."
            }
    
    def _search_with_serpapi(self, query: str) -> List[Dict]:
        """Search using SerpAPI"""
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": 10,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            return organic_results
            
        except Exception as e:
            print(f"SerpAPI error: {str(e)}")
            return []
    
    def _analyze_search_results(self, results: List[Dict]) -> Dict:
        """Analyze search results to extract insights"""
        platforms = []
        links = []
        all_text = []
        
        # Known professional platforms
        professional_domains = [
            "linkedin.com", "github.com", "stackoverflow.com", 
            "gitlab.com", "bitbucket.org", "medium.com",
            "dev.to", "kaggle.com", "behance.net", "dribbble.com"
        ]
        
        for result in results:
            link = result.get("link", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            
            # Check if it's a professional platform
            for domain in professional_domains:
                if domain in link:
                    platform_name = domain.split('.')[0].title()
                    if platform_name not in platforms:
                        platforms.append(platform_name)
                    links.append({
                        "platform": platform_name,
                        "url": link,
                        "title": title
                    })
                    break
            
            all_text.append(f"{title} {snippet}")
        
        # Extract topics from text
        topics = self._extract_topics(" ".join(all_text))
        
        # Generate summary
        if platforms:
            summary = f"Found profiles on {', '.join(platforms)}. "
            if topics:
                summary += f"Mostly posts about {', '.join(topics[:3])}."
            else:
                summary += "Professional presence detected."
        else:
            summary = "Limited public professional profiles found."
        
        return {
            "summary": summary,
            "platforms": platforms,
            "topics": topics,
            "links": links
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extract main topics using simple word frequency analysis
        This is a basic implementation - could be enhanced with NLP
        """
        # Common tech/professional keywords to look for
        tech_keywords = [
            "python", "javascript", "java", "react", "angular", "vue", "node",
            "machine learning", "ai", "data science", "cloud", "aws", "azure",
            "docker", "kubernetes", "devops", "backend", "frontend", "fullstack",
            "mobile", "android", "ios", "web development", "software engineering",
            "database", "api", "microservices", "agile", "scrum"
        ]
        
        text_lower = text.lower()
        found_topics = []
        
        for keyword in tech_keywords:
            if keyword in text_lower:
                # Count occurrences
                count = text_lower.count(keyword)
                if count >= 2:  # Mentioned at least twice
                    found_topics.append((keyword, count))
        
        # Sort by frequency and return top topics
        found_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic[0].title() for topic in found_topics[:5]]
    
    def fetch_public_page_content(self, url: str) -> Optional[str]:
        """
        Safely fetch public page content (for public profiles only)
        Returns visible text or None if blocked/error
        """
        if not self.search_enabled:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text
                text = soup.get_text(separator=' ', strip=True)
                return text[:5000]  # Limit length
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching page content: {str(e)}")
            return None


# Singleton instance
_social_search_service = None


def get_social_search_service() -> SocialSearchService:
    """Get or create social search service singleton"""
    global _social_search_service
    if _social_search_service is None:
        _social_search_service = SocialSearchService()
    return _social_search_service
