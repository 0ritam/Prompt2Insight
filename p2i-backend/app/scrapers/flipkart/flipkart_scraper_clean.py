"""
CLEANED VERSION: Flipkart scraper functionality removed
This file now only contains stub classes to prevent import errors.
All scraping functionality has been replaced with Google Search API in google_search_api.py.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ProductData:
    """Product data structure - kept for compatibility"""
    title: str = "N/A"
    price: str = "N/A"
    rating: str = "N/A"
    url: str = "N/A"
    image: str = ""
    in_stock: str = "N/A"

class FlipkartScraper:
    """
    DEPRECATED: Stub class to prevent import errors
    All functionality has been moved to Google Search API
    """
    
    def __init__(self, headless: bool = True, max_products: int = 5):
        """Initialize stub scraper"""
        self.max_products = max_products
        self.config = {"stub": True}
        self.driver = None
        print("⚠️  FlipkartScraper is deprecated - using Google Search API instead")

    def search_products(self, query: str) -> List[Dict]:
        """Stub method - returns empty list"""
        print(f"⚠️  search_products() is deprecated. Use Google Search API instead.")
        return []

    def scrape_for_microservice(self, query: str, filters: Dict = None) -> Dict:
        """Stub method for compatibility"""
        print(f"⚠️  scrape_for_microservice() is deprecated. Use Google Search API instead.")
        return {
            "success": False,
            "query": query,
            "products_found": 0,
            "execution_time": 0.0,
            "products": [],
            "timestamp": 0,
            "error": "FlipkartScraper is deprecated. Use Google Search API instead.",
            "scraper_method": "deprecated_stub"
        }

    def close(self):
        """Stub close method"""
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# For backwards compatibility
if __name__ == "__main__":
    print("⚠️  FlipkartScraper has been deprecated.")
    print("   Use Google Search API in google_search_api.py instead.")
    print("   All Selenium dependencies have been removed.")
