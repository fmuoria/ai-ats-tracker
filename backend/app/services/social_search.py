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
        url_lower = url.lower()
        
        if 'linkedin.com' in url_lower:
            return 'linkedin'
        elif 'github.com' in url_lower:
            return 'github'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        elif 'stackoverflow.com' in url_lower:
            return 'stackoverflow'
        elif 'medium.com' in url_lower:
            return 'medium'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        
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
