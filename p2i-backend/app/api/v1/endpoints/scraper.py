from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.amazon_scraper import AmazonScraper
import json

# Pydantic models for request/response
class ScraperRequest(BaseModel):
    """Request model for scraper endpoint."""
    intent: str
    products: List[str]
    filters: Dict[str, Any]
    attributes: List[str] = []
    max_products_per_query: int = 5

class ProductData(BaseModel):
    """Model for individual product data."""
    name: str
    price: str
    link: str
    image: str
    rating: str

class ScraperResponse(BaseModel):
    """Response model for scraper endpoint."""
    success: bool
    search_query: str
    target_url: str
    products_found: int
    max_products_requested: int
    products: List[ProductData]
    metadata: Dict[str, Any]
    error: Optional[str] = None

# Create router
router = APIRouter()

@router.post("/amazon", response_model=ScraperResponse)
async def scrape_amazon_products(request: ScraperRequest):
    """
    Scrape Amazon products based on parsed prompt JSON.
    
    Accepts a structured request with intent, products, filters, and attributes,
    then automatically generates the target URL and scrapes product data.
    
    Example request:
    {
        "intent": "search",
        "products": ["laptops"],
        "filters": {
            "price": "under ₹50000",
            "brand": "any"
        },
        "attributes": ["gaming", "intel"],
        "max_products_per_query": 5
    }
    """
    try:
        print(f"🔍 Received scraper request:")
        print(f"   Intent: {request.intent}")
        print(f"   Products: {request.products}")
        print(f"   Filters: {request.filters}")
        print(f"   Attributes: {request.attributes}")
        print(f"   Max products: {request.max_products_per_query}")
        
        # Convert request to dictionary
        prompt_data = {
            "intent": request.intent,
            "products": request.products,
            "filters": request.filters,
            "attributes": request.attributes,
            "max_products_per_query": request.max_products_per_query
        }
        
        # Initialize scraper
        scraper = AmazonScraper()
        
        # Scrape products
        result = scraper.scrape_products(prompt_data)
        
        if result["success"]:
            # Convert products to ProductData objects
            products = []
            for product in result["products"]:
                products.append(ProductData(
                    name=product["name"],
                    price=product["price"],
                    link=product["link"],
                    image=product["image"],
                    rating=product["rating"]
                ))
            
            return ScraperResponse(
                success=True,
                search_query=result["search_query"],
                target_url=result["target_url"],
                products_found=result["products_found"],
                max_products_requested=result["max_products_requested"],
                products=products,
                metadata=result["metadata"]
            )
        else:
            return ScraperResponse(
                success=False,
                search_query=result.get("search_query", ""),
                target_url=result.get("target_url", ""),
                products_found=0,
                max_products_requested=request.max_products_per_query,
                products=[],
                metadata={},
                error=result.get("error", "Unknown error")
            )
            
    except Exception as e:
        print(f"❌ Error in scraper endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Scraper processing failed: {str(e)}"
        )

@router.get("/test")
async def test_scraper():
    """
    Test endpoint to verify scraper functionality.
    """
    try:
        scraper = AmazonScraper()
        
        # Test with sample data
        test_prompt = {
            "intent": "search",
            "products": ["laptops"],
            "filters": {
                "price": "under ₹50000",
                "brand": "any"
            },
            "attributes": ["gaming", "intel"],
            "max_products_per_query": 3
        }
        
        result = scraper.scrape_products(test_prompt)
        
        return {
            "message": "Scraper test completed",
            "result": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        ) 