"""
FastAPI Microservice for Flipkart Scraping
Usage: uvicorn flipkart_api:app --reload --port 8000
"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Debug: Check if environment variables are loaded
google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
print(f"🔑 Google API Key loaded: {'✅' if google_api_key else '❌'}")
print(f"🔍 Google Engine ID loaded: {'✅' if google_engine_id else '❌'}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import uuid
import time
import re
from flipkart_microservice_scraper import FlipkartScraper
from google_search import google_search
from datetime import datetime

app = FastAPI(
    title="Flipkart Scraper API",
    description="Fast microservice for scraping Flipkart products",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global scraper instance
scraper = None

class ScrapeRequest(BaseModel):
    query: str
    max_products: int = 5
    filters: Optional[Dict] = None

class ExactURLRequest(BaseModel):
    urls: List[str]
    filters: Optional[Dict] = None

class StructuredScrapeRequest(BaseModel):
    """Request format matching your prompt parser agent output"""
    intent: str  # "compare", "search", "recommend"
    products: List[str]  # ["product1", "product2"]
    filters: Optional[Dict[str, str]] = None  # {"price": "under ₹20000", "brand": "Apple"}
    attributes: Optional[List[str]] = None  # ["processor", "ram", "storage"]
    site: str = "flipkart"  # Target site
    max_products_per_query: int = 5  # How many products per search term

class GoogleSearchRequest(BaseModel):
    query: str
    num_results: int = 3

class ScrapeResponse(BaseModel):
    success: bool
    task_id: str
    query: str
    products_found: int
    execution_time: float
    products: List[Dict]
    timestamp: int
    error: Optional[str] = None

# In-memory storage for async tasks (use Redis in production)
task_results = {}

# AI fallback products
FAKE_AI_PRODUCTS = [
    {
        "title": "AI Generated Product 1",
        "price": "₹15,999",
        "rating": "4.5",
        "reviews": "1,234",
        "description": "High-quality AI generated product with excellent features",
        "url": "#ai-product-1",
        "image": "https://picsum.photos/400/400?random=1"
    },
    {
        "title": "AI Generated Product 2", 
        "price": "₹25,999",
        "rating": "4.3",
        "reviews": "856",
        "description": "Premium AI generated product for professional use",
        "url": "#ai-product-2",
        "image": "https://picsum.photos/400/400?random=2"
    },
    {
        "title": "AI Generated Product 3",
        "price": "₹12,999", 
        "rating": "4.7",
        "reviews": "2,456",
        "description": "Budget-friendly AI generated product with great value",
        "url": "#ai-product-3",
        "image": "https://picsum.photos/400/400?random=3"
    }
]

@app.on_event("startup")
async def startup_event():
    """Initialize scraper on startup"""
    global scraper
    scraper = FlipkartScraper(headless=True, max_products=10)
    print("🚀 Flipkart Scraper API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scraper
    if scraper:
        scraper.close()
    print("🛑 Flipkart Scraper API stopped")

@app.get("/")
async def root():
    return {
        "message": "Flipkart Scraper API",
        "status": "running",
        "endpoints": {
            "/scrape": "POST - Search and scrape products",
            "/scrape-exact": "POST - Scrape exact URLs",
            "/scrape-structured": "POST - Scrape with structured input (prompt parser format)",
            "/scrape-natural": "POST - Natural language queries (e.g., 'lenovo gaming laptops under 80000')",
            "/google-search": "POST - Search products using Google Custom Search API",
            "/task/{task_id}": "GET - Get async task result",
            "/health": "GET - Health check",
            "/health-check": "GET - Scraper health check"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scraper_ready": scraper is not None
    }

@app.get("/health-check")
async def scraper_health_check():
    """Check if scraper selectors are working properly"""
    try:
        from scraper_health_checker import ScraperHealthChecker
        
        checker = ScraperHealthChecker()
        health_results = checker.check_selector_health()
        
        return {
            "scraper_health": health_results,
            "api_status": "healthy",
            "scraper_initialized": scraper is not None,
            "last_check": health_results["timestamp"]
        }
    except Exception as e:
        return {
            "error": str(e),
            "api_status": "healthy", 
            "scraper_initialized": scraper is not None,
            "scraper_health": "check_failed"
        }

@app.post("/scrape-structured")
async def scrape_with_structured_input(request: StructuredScrapeRequest, force_ai: bool = False):
    """
    Scrape products using structured input from prompt parser agent
    Matches the exact format from your prompt template
    """
    try:
        print(f"DEBUG: force_ai parameter: {force_ai}")
        print(f"DEBUG: Request: {request}")
        
        if force_ai:
            # Return AI fallback products
            return {
                "success": True,
                "intent": request.intent,
                "products_requested": request.products,
                "products_found": len(FAKE_AI_PRODUCTS),
                "execution_time": 0.1,
                "results": FAKE_AI_PRODUCTS,
                "source": "ai-fallback",
                "timestamp": int(time.time())
            }
        
        if not scraper:
            raise HTTPException(status_code=500, detail="Scraper not initialized")
        
        if not request.products:
            raise HTTPException(status_code=400, detail="Products list cannot be empty")
        
        # Process each product in the list
        all_results = []
        total_start_time = time.time()
        
        # Use the max_products_per_query from request
        max_products = min(request.max_products_per_query, 10)  # Cap at 10 for performance
        
        for product_name in request.products:
            
            # Build enhanced query with intelligent attribute integration
            enhanced_query = product_name
            
            # Add attributes intelligently based on product type
            if request.attributes:
                for attribute in request.attributes:
                    # Add common attributes that enhance search
                    if attribute.lower() in ['i5', 'i7', 'ryzen', 'intel', 'amd']:
                        enhanced_query += f" {attribute} processor"
                    elif attribute.lower() in ['4gb', '6gb', '8gb', '12gb', '16gb']:
                        enhanced_query += f" {attribute} ram"
                    elif attribute.lower() in ['gaming', 'business', 'student', 'professional']:
                        enhanced_query += f" {attribute}"
                    elif attribute.lower() in ['ssd', '256gb', '512gb', '1tb']:
                        enhanced_query += f" {attribute} storage"
                    else:
                        enhanced_query += f" {attribute}"
            
            # Convert structured filters to internal format and enhance query
            internal_filters = {}
            if request.filters:
                for filter_key, filter_value in request.filters.items():
                    if filter_key == "price":
                        # Parse price filter and add to search query for better results
                        price_text = filter_value.lower()
                        if "under" in price_text or "below" in price_text:
                            import re
                            price_match = re.search(r'₹?(\d+(?:,\d+)*)', price_text)
                            if price_match:
                                max_price = int(price_match.group(1).replace(',', ''))
                                internal_filters["max_price"] = max_price
                                # Add price range to search query for better targeting
                                enhanced_query += f" under {max_price}"
                        elif "above" in price_text or "over" in price_text:
                            import re
                            price_match = re.search(r'₹?(\d+(?:,\d+)*)', price_text)
                            if price_match:
                                min_price = int(price_match.group(1).replace(',', ''))
                                internal_filters["min_price"] = min_price
                                enhanced_query += f" above {min_price}"
                        elif "between" in price_text:
                            import re
                            price_matches = re.findall(r'₹?(\d+(?:,\d+)*)', price_text)
                            if len(price_matches) >= 2:
                                min_price = int(price_matches[0].replace(',', ''))
                                max_price = int(price_matches[1].replace(',', ''))
                                internal_filters["min_price"] = min_price
                                internal_filters["max_price"] = max_price
                                enhanced_query += f" {min_price} to {max_price}"
                    
                    elif filter_key == "brand":
                        # Add brand to search query for better targeting
                        enhanced_query = f"{filter_value} {enhanced_query}"
                    
                    elif filter_key == "rating":
                        # Add rating filter
                        rating_text = filter_value.lower()
                        if "above" in rating_text:
                            import re
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                min_rating = float(rating_match.group(1))
                                internal_filters["min_rating"] = min_rating
                    
                    elif filter_key == "availability":
                        if filter_value.lower() in ["in stock", "available"]:
                            enhanced_query += " available"
            
            # Perform scraping for this product
            try:
                result = scraper.scrape_for_microservice(
                    query=enhanced_query.strip(),
                    filters=internal_filters
                )
                
                # Limit results per product
                if result["success"] and result["products"]:
                    limited_products = result["products"][:max_products]
                    for product in limited_products:
                        product["source_query"] = product_name
                        product["enhanced_query"] = enhanced_query.strip()
                        product["applied_filters"] = internal_filters
                    all_results.extend(limited_products)
                
            except Exception as e:
                continue
        
        total_time = time.time() - total_start_time
        
        # Build response in your expected format
        response_data = {
            "success": True,
            "intent": request.intent,
            "products_requested": request.products,
            "products_found": len(all_results),
            "execution_time": round(total_time, 2),
            "filters_applied": request.filters,
            "attributes_used": request.attributes,
            "results": all_results,
            "timestamp": int(time.time())
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structured scraping failed: {str(e)}")

@app.post("/scrape-exact", response_model=ScrapeResponse)
async def scrape_exact_urls(request: ExactURLRequest):
    """Scrape specific product URLs provided by user"""
    try:
        if not scraper:
            raise HTTPException(status_code=500, detail="Scraper not initialized")
        
        if not request.urls:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        # Validate URLs are Flipkart URLs
        invalid_urls = []
        for url in request.urls:
            if "flipkart.com" not in url:
                invalid_urls.append(url)
        
        if invalid_urls:
            raise HTTPException(
                status_code=400, 
                detail=f"Non-Flipkart URLs found: {invalid_urls[:3]}..."  # Show first 3
            )
        
        # Perform scraping
        result = scraper.scrape_exact_urls_for_microservice(
            urls=request.urls,
            filters=request.filters
        )
        
        # Generate task ID for tracking
        task_id = str(uuid.uuid4())
        
        return ScrapeResponse(
            success=result["success"],
            task_id=task_id,
            query=f"exact_urls_{len(request.urls)}_products",
            products_found=result["products_found"],
            execution_time=result["execution_time"],
            products=result["products"],
            timestamp=result["timestamp"],
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exact URL scraping failed: {str(e)}")

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_products(request: ScrapeRequest):
    """Synchronous scraping endpoint"""
    try:
        if not scraper:
            raise HTTPException(status_code=500, detail="Scraper not initialized")
        
        # Perform scraping
        result = scraper.scrape_for_microservice(
            query=request.query,
            filters=request.filters
        )
        
        # Generate task ID for tracking
        task_id = str(uuid.uuid4())
        
        return ScrapeResponse(
            success=result["success"],
            task_id=task_id,
            query=result["query"],
            products_found=result["products_found"],
            execution_time=result["execution_time"],
            products=result["products"],
            timestamp=result["timestamp"],
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """Get async task result"""
    if task_id not in task_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_results[task_id]

@app.post("/scrape-with-attributes")
async def scrape_with_attributes(request: Dict):
    """
    Special endpoint for instruction agent integration
    Accepts complex queries with attributes
    """
    try:
        # Parse instruction agent format
        query = request.get("product_name", "")
        attributes = request.get("attributes", {})
        filters = request.get("filters", {})
        
        # Build enhanced query from attributes
        if attributes:
            # Add attributes to search query
            for key, value in attributes.items():
                if key in ["processor", "brand", "ram", "storage"]:
                    query += f" {value}"
        
        # Convert attributes to filters
        if "price_budget" in request:
            filters["max_price"] = request["price_budget"]
        
        # Perform scraping
        result = scraper.scrape_for_microservice(
            query=query.strip(),
            filters=filters
        )
        
        # Add original request context
        result["original_request"] = request
        result["enhanced_query"] = query.strip()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attribute-based scraping failed: {str(e)}")

@app.post("/scrape-natural")
async def scrape_with_natural_language(request: Dict):
    """
    Enhanced endpoint for natural language queries like:
    "lenovo gaming laptops under 80,000"
    "best smartphones with 8gb ram under 25000"
    """
    try:
        if not scraper:
            raise HTTPException(status_code=500, detail="Scraper not initialized")
        
        natural_query = request.get("query", "")
        if not natural_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Parse natural language query into structured format
        parsed_request = parse_natural_language_query(natural_query)
        
        # Process using the structured scraping logic
        start_time = time.time()
        all_results = []
        
        for product_name in parsed_request["products"]:
            
            # Build enhanced query
            enhanced_query = product_name
            
            # Add extracted attributes
            if parsed_request.get("attributes"):
                for attribute in parsed_request["attributes"]:
                    enhanced_query += f" {attribute}"
            
            # Add extracted brand
            if parsed_request.get("brand"):
                enhanced_query = f"{parsed_request['brand']} {enhanced_query}"
            
            # Add price range to query
            if parsed_request.get("price_hint"):
                enhanced_query += f" {parsed_request['price_hint']}"
            
            # Convert to internal filters
            internal_filters = {}
            if parsed_request.get("max_price"):
                internal_filters["max_price"] = parsed_request["max_price"]
            if parsed_request.get("min_price"):
                internal_filters["min_price"] = parsed_request["min_price"]
            if parsed_request.get("min_rating"):
                internal_filters["min_rating"] = parsed_request["min_rating"]
            
            # Perform scraping
            try:
                result = scraper.scrape_for_microservice(
                    query=enhanced_query.strip(),
                    filters=internal_filters
                )
                
                if result["success"] and result["products"]:
                    max_products = request.get("max_products", 5)
                    limited_products = result["products"][:max_products]
                    for product in limited_products:
                        product["source_query"] = natural_query
                        product["enhanced_query"] = enhanced_query.strip()
                        product["parsed_intent"] = parsed_request
                    all_results.extend(limited_products)
                
            except Exception as e:
                continue
        
        total_time = time.time() - start_time
        
        # Build response
        response_data = {
            "success": True,
            "original_query": natural_query,
            "parsed_intent": parsed_request,
            "products_found": len(all_results),
            "execution_time": round(total_time, 2),
            "results": all_results,
            "timestamp": int(time.time())
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Natural language scraping failed: {str(e)}")

def parse_natural_language_query(query: str) -> Dict:
    """Parse natural language queries into structured format"""
    import re
    
    query_lower = query.lower()
    parsed = {
        "products": [],
        "attributes": [],
        "brand": None,
        "max_price": None,
        "min_price": None,
        "price_hint": None
    }
    
    # Extract brands (common laptop/phone brands)
    brands = ["lenovo", "hp", "dell", "asus", "acer", "apple", "samsung", "oneplus", "xiaomi", "redmi", "realme", "oppo", "vivo", "motorola", "nokia"]
    for brand in brands:
        if brand in query_lower:
            parsed["brand"] = brand
            query_lower = query_lower.replace(brand, "").strip()
            break
    
    # Extract product categories
    product_keywords = {
        "laptop": ["laptop", "notebooks", "computer"],
        "smartphone": ["phone", "smartphone", "mobile"],
        "tablet": ["tablet", "ipad"],
        "headphones": ["headphones", "earphones", "earbuds"],
        "watch": ["smartwatch", "watch"],
        "tv": ["tv", "television", "smart tv"]
    }
    
    for product, keywords in product_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            parsed["products"].append(product)
            break
    
    # If no specific product found, use the main words as product
    if not parsed["products"]:
        # Remove common words and extract main product terms
        common_words = ["best", "good", "top", "under", "above", "with", "and", "or", "the", "a", "an"]
        words = [word for word in query_lower.split() if word not in common_words and not word.isdigit()]
        if words:
            parsed["products"] = [" ".join(words[:2])]  # Take first 2 meaningful words
    
    # Extract attributes
    attributes = {
        "gaming": ["gaming", "gamer"],
        "business": ["business", "professional", "office"],
        "student": ["student", "study"],
        "i5": ["i5", "intel i5"],
        "i7": ["i7", "intel i7"],
        "ryzen": ["ryzen", "amd ryzen"],
        "4gb": ["4gb", "4 gb"],
        "6gb": ["6gb", "6 gb"],
        "8gb": ["8gb", "8 gb"],
        "12gb": ["12gb", "12 gb"],
        "16gb": ["16gb", "16 gb"],
        "ssd": ["ssd", "solid state"],
        "256gb": ["256gb", "256 gb"],
        "512gb": ["512gb", "512 gb"],
        "1tb": ["1tb", "1 tb"]
    }
    
    for attr, keywords in attributes.items():
        if any(keyword in query_lower for keyword in keywords):
            parsed["attributes"].append(attr)
    
    # Extract price information
    price_patterns = [
        r"under ₹?(\d+(?:,\d+)*)",
        r"below ₹?(\d+(?:,\d+)*)",
        r"less than ₹?(\d+(?:,\d+)*)",
        r"₹?(\d+(?:,\d+)*) or less"
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            price = int(match.group(1).replace(',', ''))
            parsed["max_price"] = price
            parsed["price_hint"] = f"under {price}"
            break
    
    # Extract minimum price
    min_price_patterns = [
        r"above ₹?(\d+(?:,\d+)*)",
        r"over ₹?(\d+(?:,\d+)*)",
        r"more than ₹?(\d+(?:,\d+)*)"
    ]
    
    for pattern in min_price_patterns:
        match = re.search(pattern, query_lower)
        if match:
            price = int(match.group(1).replace(',', ''))
            parsed["min_price"] = price
            if not parsed["price_hint"]:
                parsed["price_hint"] = f"above {price}"
            break
    
    return parsed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

@app.post("/google-search")
async def search_google_products(request: GoogleSearchRequest):
    """
    Search for products using Google Custom Search API
    Returns top product results with images and descriptions
    """
    try:
        results = google_search.search_products(
            query=request.query, 
            num_results=request.num_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "results_found": len(results),
            "results": results,
            "timestamp": int(time.time())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google search failed: {str(e)}")
