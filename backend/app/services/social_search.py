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
"""
Social and Online Presence Search Service.

Uses SerpAPI when available, otherwise provides manual search guidance.
"""

import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import serpapi, but make it optional
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    logger.info("serpapi not available, will use manual search guidance")


class SocialSearchService:
    """Service for searching candidate's online and social media presence"""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY") or os.getenv("SEARCH_API_KEY")
        self.use_api = SERPAPI_AVAILABLE and self.serpapi_key is not None
        
        if self.use_api:
            logger.info("SerpAPI enabled for web searches")
        else:
            logger.info("SerpAPI not configured, using manual search guidance")
    
    def search_online_presence(self, name: str, email: Optional[str] = None, 
                              linkedin_url: Optional[str] = None) -> Dict:
        """
        Search for candidate's online presence.
        
        Args:
            name: Candidate's full name
            email: Candidate's email (optional)
            linkedin_url: Candidate's LinkedIn URL (optional)
            
        Returns:
            Dictionary with search results or guidance
        """
        if not name:
            return {
                "search_performed": False,
                "results": [],
                "note": "Name required for online presence search"
            }
        
        if self.use_api:
            return self._search_with_serpapi(name, email, linkedin_url)
        else:
            return self._generate_manual_search_guidance(name, email, linkedin_url)
    
    def _search_with_serpapi(self, name: str, email: Optional[str], 
                            linkedin_url: Optional[str]) -> Dict:
        """Perform actual web search using SerpAPI"""
        try:
            # Build search query
            query_parts = [f'"{name}"']
            if email:
                domain = email.split('@')[1] if '@' in email else None
                if domain and domain not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
                    query_parts.append(domain)
            
            query = ' '.join(query_parts)
            
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
            # Extract relevant information
            organic_results = results.get("organic_results", [])
            
            findings = []
            platforms_found = set()
            
            for result in organic_results[:10]:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                # Detect platform
                platform = self._detect_platform(link)
                if platform and platform not in platforms_found:
                    platforms_found.add(platform)
                
                findings.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                    "platform": platform or "other"
                })
            
            return {
                "search_performed": True,
                "query": query,
                "results_count": len(findings),
                "findings": findings,
                "platforms_found": list(platforms_found),
                "linkedin_url": linkedin_url if linkedin_url else None,
                "note": "Web search completed via SerpAPI"
            }
            
        except Exception as e:
            logger.error(f"Error performing SerpAPI search: {e}")
            return {
                "search_performed": False,
                "error": str(e),
                "note": "Search API error, falling back to manual guidance",
                **self._generate_manual_search_guidance(name, email, linkedin_url)
            }
    
    def _generate_manual_search_guidance(self, name: str, email: Optional[str],
                                        linkedin_url: Optional[str]) -> Dict:
        """Generate manual search guidance when API is not available"""
        search_queries = []
        
        # Basic name search
        search_queries.append({
            "query": f'"{name}"',
            "purpose": "General online presence",
            "url": f"https://www.google.com/search?q={name.replace(' ', '+')}"
        })
        
        # Name + professional
        search_queries.append({
            "query": f'"{name}" professional OR developer OR engineer',
            "purpose": "Professional profiles and work",
            "url": f"https://www.google.com/search?q={name.replace(' ', '+')}+professional"
        })
        
        if email:
            domain = email.split('@')[1] if '@' in email else None
            if domain:
                search_queries.append({
                    "query": f'"{name}" {domain}',
                    "purpose": "Company-affiliated profiles",
                    "url": f"https://www.google.com/search?q={name.replace(' ', '+')}+{domain}"
                })
        
        platforms_to_check = [
            {
                "platform": "LinkedIn",
                "url": f"https://www.linkedin.com/search/results/all/?keywords={name.replace(' ', '%20')}",
                "status": "provided" if linkedin_url else "not_provided",
                "note": "Primary professional network" + (f" - URL provided: {linkedin_url}" if linkedin_url else "")
            },
            {
                "platform": "GitHub",
                "url": f"https://github.com/search?q={name.replace(' ', '+')}",
                "status": "manual_check_required",
                "note": "Check for code repositories and contributions"
            },
            {
                "platform": "Stack Overflow",
                "url": f"https://stackoverflow.com/search?q={name.replace(' ', '+')}",
                "status": "manual_check_required",
                "note": "Technical Q&A contributions"
            },
            {
                "platform": "Twitter/X",
                "url": f"https://twitter.com/search?q={name.replace(' ', '%20')}",
                "status": "manual_check_required",
                "note": "Professional presence and thought leadership"
            },
            {
                "platform": "Medium",
                "url": f"https://medium.com/search?q={name.replace(' ', '%20')}",
                "status": "manual_check_required",
                "note": "Technical blogs and articles"
            }
        ]
        
        return {
            "search_performed": False,
            "search_method": "manual",
            "candidate_name": name,
            "search_queries": search_queries,
            "platforms_to_check": platforms_to_check,
            "note": "API key not configured. Please perform manual searches using the provided queries and links.",
            "setup_instructions": "To enable automated search, add SERPAPI_KEY to your .env file. Get your key from https://serpapi.com/"
        }
    
    def _detect_platform(self, url: str) -> Optional[str]:
        """Detect social media platform from URL"""
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            # Check domain precisely - must be exact match or subdomain
            if domain == 'linkedin.com' or domain.endswith('.linkedin.com'):
                return 'linkedin'
            elif domain == 'github.com' or domain.endswith('.github.com'):
                return 'github'
            elif domain == 'twitter.com' or domain.endswith('.twitter.com') or domain == 'x.com' or domain.endswith('.x.com'):
                return 'twitter'
            elif domain == 'stackoverflow.com' or domain.endswith('.stackoverflow.com'):
                return 'stackoverflow'
            elif domain == 'medium.com' or domain.endswith('.medium.com'):
                return 'medium'
            elif domain == 'facebook.com' or domain.endswith('.facebook.com'):
                return 'facebook'
            elif domain == 'instagram.com' or domain.endswith('.instagram.com'):
                return 'instagram'
        except Exception:
            # Fall back to returning None if parsing fails
            pass
        
        return None
    
    def check_social_media_profiles(self, name: str, platforms: Optional[List[str]] = None) -> Dict:
        """
        Check for presence on specific social media platforms.
        
        Args:
            name: Candidate's full name
            platforms: List of platforms to check (default: ['linkedin', 'github', 'twitter'])
            
        Returns:
            Dictionary with platform check results
        """
        if platforms is None:
            platforms = ['linkedin', 'github', 'twitter', 'stackoverflow']
        
        platform_checks = []
        
        for platform in platforms:
            if self.use_api:
                # Search for name on specific platform
                query = f'"{name}" site:{platform}.com'
                check_result = self._quick_platform_check(query, platform)
            else:
                # Generate manual check guidance
                check_result = {
                    "platform": platform,
                    "status": "manual_check_required",
                    "search_url": self._get_platform_search_url(platform, name),
                    "note": f"Manually check {platform} for candidate's presence"
                }
            
            platform_checks.append(check_result)
        
        return {
            "platforms_checked": platforms,
            "results": platform_checks,
            "api_enabled": self.use_api
        }
    
    def _quick_platform_check(self, query: str, platform: str) -> Dict:
        """Quick check for presence on a specific platform"""
        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": 3,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            return {
                "platform": platform,
                "status": "found" if organic_results else "not_found",
                "results_count": len(organic_results),
                "top_results": [
                    {"title": r.get("title"), "url": r.get("link")}
                    for r in organic_results[:2]
                ]
            }
        except Exception as e:
            logger.error(f"Error checking {platform}: {e}")
            return {
                "platform": platform,
                "status": "error",
                "error": str(e)
            }
    
    def _get_platform_search_url(self, platform: str, name: str) -> str:
        """Get search URL for a specific platform"""
        name_encoded = name.replace(' ', '%20')
        
        urls = {
            'linkedin': f"https://www.linkedin.com/search/results/all/?keywords={name_encoded}",
            'github': f"https://github.com/search?q={name.replace(' ', '+')}",
            'twitter': f"https://twitter.com/search?q={name_encoded}",
            'stackoverflow': f"https://stackoverflow.com/search?q={name.replace(' ', '+')}",
            'medium': f"https://medium.com/search?q={name_encoded}"
        }
        
        return urls.get(platform, f"https://www.google.com/search?q={name.replace(' ', '+')}+{platform}")
