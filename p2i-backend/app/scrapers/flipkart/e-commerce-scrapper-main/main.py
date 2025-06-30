from fastapi import FastAPI, HTTPException
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

@app.post("/scrape")
async def scrape_products(request: ScrapeRequest):
    try:
        results = []
        scraper = FlipkartScraper(headless=True, max_products=5)
        
        try:
            for task in request.tasks:
                filters = {}
                if task.filters:
                    if task.filters.price:
                        # Parse price filter
                        price_filter = task.filters.price
                        if "<=" in price_filter or "under" in price_filter:
                            # Extract the number from filters like "<=50000" or "under 50000"
                            price_value = ''.join(filter(str.isdigit, price_filter))
                            if price_value:
                                filters["max_price"] = int(price_value)
                        elif ">=" in price_filter:
                            # Extract the number from filters like ">=20000"
                            price_value = ''.join(filter(str.isdigit, price_filter))
                            if price_value:
                                filters["min_price"] = int(price_value)
                    
                    if task.filters.brand:
                        filters["brand"] = task.filters.brand

                if task.taskType == "detail":
                    # For product detail pages, we need exact URLs or we scrape first result
                    result = scraper.scrape_for_microservice(
                        query=task.productName, 
                        filters=filters
                    )
                    results.append(result)
                
                elif task.taskType == "listing":
                    # For product listings/search results
                    result = scraper.scrape_for_microservice(
                        query=task.productName,
                        filters=filters
                    )
                    results.append(result)
        finally:
            scraper.close()
        
        return {"success": True, "data": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

# Simple health check endpoint
@app.get("/")
def read_root():
    return {"status": "online", "service": "Prompt2Insight Scraper API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
