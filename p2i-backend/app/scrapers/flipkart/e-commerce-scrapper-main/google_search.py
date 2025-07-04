"""
Google Custom Search API integration for Prompt2Insight
"""

import os
import requests
from typing import List, Dict, Optional
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class GoogleSearchAPI:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_CSE_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key:
            logger.warning("GOOGLE_CSE_API_KEY not found in environment variables")
        if not self.search_engine_id:
            logger.warning("GOOGLE_CSE_ENGINE_ID not found in environment variables")
    
    def search_products(self, query: str, num_results: int = 3) -> List[Dict]:
        """
        Search for products using Google Custom Search API
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 3)
            
        Returns:
            List of product results with title, link, snippet, and image
        """
        if not self.api_key or not self.search_engine_id:
            raise HTTPException(
                status_code=500, 
                detail="Google Search API not configured. Missing API key or search engine ID."
            )
        
        try:
            # First try web search (more reliable)
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": f"{query} product buy price",  # Enhance query for product search
                "num": min(num_results, 10),  # Google API max is 10
                "safe": "medium",
                "lr": "lang_en"  # English results
            }
            
            logger.info(f"Searching Google for: {query}")
            logger.debug(f"Search params: {params}")
            
            response = requests.get(self.base_url, params=params, timeout=10)
            logger.debug(f"Google API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Google API error: {response.status_code} - {response.text}")
                response.raise_for_status()
            
            data = response.json()
            results = []
            
            items = data.get("items", [])
            for item in items[:num_results]:
                # Get image from pagemap or use a placeholder
                image_url = None
                if "pagemap" in item:
                    # Try to get image from pagemap
                    cse_image = item["pagemap"].get("cse_image", [])
                    if cse_image:
                        image_url = cse_image[0].get("src")
                    else:
                        # Try other image sources
                        metatags = item["pagemap"].get("metatags", [])
                        if metatags:
                            image_url = metatags[0].get("og:image")
                
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "description": item.get("snippet", ""),
                    "image": image_url or "https://via.placeholder.com/300x200?text=No+Image",
                    "source": "google_search"
                }
                
                # Clean up the title and description
                result["title"] = self._clean_text(result["title"])
                result["description"] = self._clean_text(result["description"])
                
                results.append(result)
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
            
        except requests.RequestException as e:
            logger.error(f"Google Search API request failed: {e}")
            raise HTTPException(status_code=503, detail=f"Google Search API unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Google Search: {e}")
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and clean up common issues
        text = " ".join(text.split())
        
        # Remove common unwanted patterns
        unwanted_patterns = ["...", " - ", " | "]
        for pattern in unwanted_patterns:
            text = text.replace(pattern, " ")
        
        return text.strip()

# Global instance
google_search = GoogleSearchAPI()
