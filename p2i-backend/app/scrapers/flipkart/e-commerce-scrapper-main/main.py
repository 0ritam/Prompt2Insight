from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
import sys

# Add the current directory to the path so we can import the scraper
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the scraper functionality
from flipkart_microservice_scraper import FlipkartScraper

app = FastAPI(title="Prompt2Insight Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the ScrapeTask model
class ScrapeTaskFilters(BaseModel):
    price: Optional[str] = None
    brand: Optional[str] = None

class ScrapeTask(BaseModel):
    productName: str
    site: str = "flipkart"
    taskType: str  # "detail" or "listing"
    filters: Optional[ScrapeTaskFilters] = None
    attributes: Optional[List[str]] = None

class ScrapeRequest(BaseModel):
    tasks: List[ScrapeTask]

# Example AI fallback function
FAKE_AI_PRODUCTS = [
    {"title": "AI Product 1", "price": "₹10,000", "url": "#"},
    {"title": "AI Product 2", "price": "₹20,000", "url": "#"},
]

def get_ai_fallback_products():
    return FAKE_AI_PRODUCTS

@app.post("/scrape-structured")
async def scrape_structured_products(request: Request):
    try:
        body = await request.json()
        force_ai = request.query_params.get("force_ai") == "true"
        
        print(f"DEBUG: force_ai parameter: {force_ai}")
        print(f"DEBUG: Request body: {body}")
        
        # Convert the body format to match our ScrapeRequest model
        tasks = []
        for product in body.get("products", []):
            task = ScrapeTask(
                productName=product,
                taskType="listing",
                filters=ScrapeTaskFilters(**body.get("filters", {})) if body.get("filters") else None
            )
            tasks.append(task)

        if force_ai:
            # Always return AI fallback products
            return {
                "success": True, 
                "data": [{"products": get_ai_fallback_products()}], 
                "source": "ai-fallback"
            }
            
        # Create scrape request from tasks
        scrape_request = ScrapeRequest(tasks=tasks)
        
        # Process the request using existing scraping logic
        results = []
        max_products = body.get("max_products_per_query", 5)
        scraper = FlipkartScraper(headless=True, max_products=max_products)
        
        try:
            for task in scrape_request.tasks:
                filters = {}
                if task.filters:
                    if task.filters.price:
                        # Parse price filter
                        price_filter = task.filters.price
                        if "<=" in price_filter or "under" in price_filter:
                            price_value = ''.join(filter(str.isdigit, price_filter))
                            if price_value:
                                filters["max_price"] = int(price_value)
                        elif ">=" in price_filter:
                            price_value = ''.join(filter(str.isdigit, price_filter))
                            if price_value:
                                filters["min_price"] = int(price_value)
                    
                    if task.filters.brand:
                        filters["brand"] = task.filters.brand

                result = scraper.scrape_for_microservice(
                    query=task.productName,
                    filters=filters
                )
                results.append(result)
        finally:
            scraper.close()
        
        return {"success": True, "data": results, "source": "scraper"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

# Simple health check endpoint
@app.get("/")
def read_root():
    return {"status": "online", "service": "Prompt2Insight Scraper API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to port 8001
