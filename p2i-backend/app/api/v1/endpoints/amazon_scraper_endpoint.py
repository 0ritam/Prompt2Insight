"""
Amazon Scraper Endpoint for Prompt2Insight - Phase 9
Exposes the Amazon scraper as an API endpoint within the main architecture
"""

import logging
import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import the Amazon scraper service
from app.services.amazon_scraper import AmazonScraper

logger = logging.getLogger(__name__)

# Create the Amazon scraper router
router = APIRouter()

# Request/Response Models
class AmazonScrapeRequest(BaseModel):
    """Request model for Amazon scraping endpoint - matches AmazonScraper format"""
    intent: str = "search"
    products: List[str]
    filters: Dict[str, str] = {}
    attributes: List[str] = []
    max_products_per_query: int = 5
    
    class Config:
        schema_extra = {
            "example": {
                "intent": "search",
                "products": ["laptops"],
                "filters": {
                    "price": "under ₹60000",
                    "brand": "any"
                },
                "attributes": ["gaming"],
                "max_products_per_query": 5
            }
        }

class AmazonScrapeResponse(BaseModel):
    """Response model for Amazon scraping endpoint"""
    success: bool
    search_query: str
    target_url: str
    products_found: int
    max_products_requested: int
    products: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "search_query": "laptops gaming",
                "target_url": "https://www.amazon.in/s?k=laptops+gaming",
                "products_found": 3,
                "max_products_requested": 5,
                "products": [
                    {
                        "name": "ASUS TUF Gaming F15 Laptop",
                        "price": "₹55,990",
                        "rating": "4.3 stars",
                        "link": "https://www.amazon.in/...",
                        "image": "https://m.media-amazon.com/..."
                    }
                ],
                "metadata": {
                    "scraper": "Amazon",
                    "source": "amazon.in",
                    "timestamp": "2025-08-04T00:00:00"
                }
            }
        }

@router.post("/scrape_amazon", response_model=AmazonScrapeResponse)
async def scrape_amazon_products(request: AmazonScrapeRequest):
    """
    Scrape Amazon products based on structured prompt data
    
    This endpoint takes structured prompt data and uses the Amazon scraper
    to find and return live product data from Amazon.in
    
    Args:
        request: AmazonScrapeRequest containing structured prompt data
        
    Returns:
        AmazonScrapeResponse with scraped product data
    """
    try:
        logger.info(f"Amazon scraping request: {request.products} with filters: {request.filters}")
        
        # Initialize the Amazon scraper
        scraper = AmazonScraper()
        
        # Convert the request to the exact format expected by the scraper
        prompt_data = {
            "intent": request.intent,
            "products": request.products,
            "filters": request.filters,
            "attributes": request.attributes,
            "max_products_per_query": request.max_products_per_query
        }
        
        # Call the Amazon scraper with the proper format
        scrape_result = scraper.scrape_products(prompt_data)
        
        # Check if scraping was successful
        if not scrape_result.get("success", False):
            error_msg = scrape_result.get("error", "Unknown scraping error")
            logger.error(f"Amazon scraping failed: {error_msg}")
            raise HTTPException(
                status_code=500,
                detail=f"Amazon scraping failed: {error_msg}"
            )
        
        logger.info(f"Amazon scraping completed: {scrape_result.get('products_found', 0)} products found")
        
        # Return the result in the same format as the scraper provides
        return AmazonScrapeResponse(
            success=scrape_result.get("success", False),
            search_query=scrape_result.get("search_query", ""),
            target_url=scrape_result.get("target_url", ""),
            products_found=scrape_result.get("products_found", 0),
            max_products_requested=scrape_result.get("max_products_requested", request.max_products_per_query),
            products=scrape_result.get("products", []),
            metadata=scrape_result.get("metadata", {})
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = f"Amazon scraping error: {str(e)}"
        logger.error(error_msg)
        
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

@router.get("/amazon/health")
async def amazon_scraper_health():
    """
    Health check endpoint for Amazon scraper service
    
    Returns:
        Health status and service information
    """
    try:
        # Test if we can initialize the scraper
        scraper = AmazonScraper()
        
        return {
            "status": "healthy",
            "service": "amazon_scraper",
            "version": "1.0.0",
            "token_configured": bool(scraper.token),
            "max_products_limit": scraper.max_products,
            "endpoints": {
                "/scrape_amazon": "Main Amazon scraping endpoint",
                "/amazon/health": "Health check endpoint"
            }
        }
    except Exception as e:
        logger.error(f"Amazon scraper health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Amazon scraper service unavailable: {str(e)}"
        )
