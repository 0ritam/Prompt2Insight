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
from flipkart_scraper_clean import FlipkartScraper  # Updated to use the new clean scraper
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
    try:
        scraper = FlipkartScraper(headless=True, max_products=10)
        print("🚀 Flipkart Scraper API started with clean scraper")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        scraper = None

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scraper
    if scraper:
        try:
            scraper.close()
            print("✅ Scraper closed successfully")
        except Exception as e:
            print(f"❌ Error closing scraper: {e}")
    print("🛑 Flipkart Scraper API stopped")

@app.get("/")
async def root():
    return {
        "message": "Flipkart Product Search API - Google Search Powered",
        "status": "running",
        "primary_method": "google_search",
        "scraper_version": "google_search_v1.0",
        "endpoints": {
            "/scrape": "POST - Search and scrape products (now uses Google Search)",
            "/scrape-exact": "POST - Scrape exact URLs (not yet implemented)",
            "/scrape-structured": "POST - Scrape with structured input (now uses Google Search)",
            "/scrape-natural": "POST - Natural language queries (now uses Google Search)",
            "/google-search": "POST - Direct Google Custom Search API",
            "/test-clean-scraper": "POST - Test the scraper (fallback method)",
            "/task/{task_id}": "GET - Get async task result",
            "/health": "GET - Health check",
            "/health-check": "GET - Scraper health check"
        },
        "improvements": [
            "Primary method now uses Google Search for better reliability",
            "Faster response times with Google Custom Search API",
            "Better product coverage and availability",
            "Reduced anti-bot detection issues",
            "Fallback to scraper if needed"
        ]
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
        if not scraper:
            return {
                "error": "Scraper not initialized",
                "api_status": "healthy", 
                "scraper_initialized": False,
                "scraper_health": "not_initialized"
            }
        
        # Test the scraper with a simple query
        test_result = scraper.scrape_for_microservice(
            query="test laptop",
            filters={"max_price": 100000}
        )
        
        health_status = {
            "scraper_health": {
                "driver_initialized": scraper.driver is not None,
                "test_query_success": test_result.get("success", False),
                "test_products_found": test_result.get("products_found", 0),
                "test_execution_time": test_result.get("execution_time", 0),
                "timestamp": datetime.now().isoformat()
            },
            "api_status": "healthy",
            "scraper_initialized": True,
            "scraper_type": "clean_selenium_scraper"
        }
        
        return health_status
        
    except Exception as e:
        return {
            "error": str(e),
            "api_status": "healthy", 
            "scraper_initialized": scraper is not None,
            "scraper_health": "check_failed",
            "scraper_type": "clean_selenium_scraper"
        }

@app.post("/scrape-structured")
async def scrape_with_structured_input(request: StructuredScrapeRequest, force_ai: bool = False):
    """
    Scrape products using structured input from prompt parser agent
    Now primarily uses Google Search for better reliability
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
        
        # Use Google Search as primary method instead of scraper
        print("🔍 Using Google Search as primary method for better reliability")
        
        if not request.products:
            raise HTTPException(status_code=400, detail="Products list cannot be empty")
        
        # Process each product using Google Search instead of scraping
        all_results = []
        total_start_time = time.time()
        
        # Use the max_products_per_query from request
        max_products = min(request.max_products_per_query, 10)  # Cap at 10 for performance
        
        for product_name in request.products:
            
            # Build enhanced query for Google Search
            enhanced_query = product_name
            
            # Add attributes intelligently
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
            
            # Add filters to query for better Google Search results
            if request.filters:
                for filter_key, filter_value in request.filters.items():
                    if filter_key == "price":
                        # Add price filter to search query
                        enhanced_query += f" {filter_value}"
                    elif filter_key == "brand":
                        # Add brand to search query
                        enhanced_query = f"{filter_value} {enhanced_query}"
            
            # Add "flipkart" to ensure we get Flipkart results
            google_search_query = f"{enhanced_query.strip()} flipkart"
            
            # Perform Google Search for this product
            try:
                print(f"🔍 Google searching for: {product_name}")
                print(f"📝 Enhanced Google query: {google_search_query}")
                
                # Use the google_search function
                from google_search import google_search
                search_results = google_search.search_products(
                    query=google_search_query,
                    num_results=max_products
                )
                
                print(f"📊 Google search result: {len(search_results)} products found")
                
                # Convert Google search results to our format
                for result in search_results:
                    formatted_product = {
                        "title": result.get("title", "N/A"),
                        "price": result.get("price", "N/A"),
                        "rating": result.get("rating", "N/A"),
                        "url": result.get("url", "N/A"),
                        "image": result.get("image", ""),
                        "in_stock": "Available",
                        "method": "google_search",
                        "source_query": product_name,
                        "enhanced_query": google_search_query,
                        "description": result.get("description", "")
                    }
                    all_results.append(formatted_product)
                
                print(f"✅ Added {len(search_results)} products from Google Search")
                
            except Exception as e:
                print(f"❌ Error in Google search for {product_name}: {e}")
                continue
        
        total_time = time.time() - total_start_time
        
        print(f"🏁 Final results summary:")
        print(f"   📊 Total products found: {len(all_results)}")
        print(f"   ⏱️  Total execution time: {round(total_time, 2)}s")
        if all_results:
            print(f"   📋 Sample result: {all_results[0].get('title', 'No title')[:50]}...")
        
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
            "source": "google_search",  # Indicate we're using Google Search
            "timestamp": int(time.time())
        }
        
        print(f"📤 Returning Google Search response with {len(all_results)} products")
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
        
        # Note: The new clean scraper doesn't have exact URL scraping yet
        # For now, we'll return a placeholder response
        # TODO: Implement exact URL scraping in the clean scraper
        
        # Generate task ID for tracking
        task_id = str(uuid.uuid4())
        
        return ScrapeResponse(
            success=False,
            task_id=task_id,
            query=f"exact_urls_{len(request.urls)}_products",
            products_found=0,
            execution_time=0.1,
            products=[],
            timestamp=int(time.time()),
            error="Exact URL scraping not yet implemented in the new clean scraper"
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
        
        # Update max_products for this request
        scraper.max_products = min(request.max_products, 20)  # Cap at 20
        
        # Perform scraping using the new clean scraper
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
    Now uses Google Search for better reliability
    """
    try:
        natural_query = request.get("query", "")
        if not natural_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        print(f"🔍 Processing natural language query: {natural_query}")
        
        # Parse natural language query into structured format
        parsed_request = parse_natural_language_query(natural_query)
        
        # Process using Google Search instead of scraping
        start_time = time.time()
        all_results = []
        
        for product_name in parsed_request["products"]:
            
            # Build enhanced query for Google Search
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
            
            # Add "flipkart" to ensure we get Flipkart results
            google_search_query = f"{enhanced_query.strip()} flipkart"
            
            # Perform Google Search
            try:
                print(f"🔍 Google searching for: {google_search_query}")
                
                from google_search import google_search
                search_results = google_search.search_products(
                    query=google_search_query,
                    num_results=request.get("max_products", 5)
                )
                
                # Convert Google search results to our format
                for result in search_results:
                    formatted_product = {
                        "title": result.get("title", "N/A"),
                        "price": result.get("price", "N/A"),
                        "rating": result.get("rating", "N/A"),
                        "url": result.get("url", "N/A"),
                        "image": result.get("image", ""),
                        "in_stock": "Available",
                        "method": "google_search",
                        "source_query": natural_query,
                        "enhanced_query": google_search_query,
                        "parsed_intent": parsed_request,
                        "description": result.get("description", "")
                    }
                    all_results.append(formatted_product)
                
                print(f"✅ Added {len(search_results)} products from Google Search")
                
            except Exception as e:
                print(f"❌ Error in Google search: {e}")
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
            "source": "google_search",  # Indicate we're using Google Search
            "timestamp": int(time.time())
        }
        
        print(f"📤 Returning natural language response with {len(all_results)} products")
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

@app.post("/test-clean-scraper")
async def test_clean_scraper(query: str = "test laptop", max_products: int = 3):
    """Test endpoint for the new clean scraper"""
    try:
        if not scraper:
            raise HTTPException(status_code=500, detail="Scraper not initialized")
        
        # Update scraper settings for test
        original_max = scraper.max_products
        scraper.max_products = max_products
        
        # Test the scraper
        start_time = time.time()
        result = scraper.scrape_for_microservice(
            query=query,
            filters=None
        )
        
        # Restore original setting
        scraper.max_products = original_max
        
        return {
            "test_results": result,
            "scraper_info": {
                "type": "clean_selenium_scraper",
                "driver_active": scraper.driver is not None,
                "config_loaded": scraper.config is not None
            },
            "test_query": query,
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clean scraper test failed: {str(e)}")

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
