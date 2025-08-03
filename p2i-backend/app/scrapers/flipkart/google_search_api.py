#!/usr/bin/env python3
"""
Minimal Google Search API for Prompt2Insight Backend
Only contains Google Search functionality - all Flipkart scraping removed
"""

import os
import time
from dotenv import load_dotenv

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
from google_search import google_search
from datetime import datetime

app = FastAPI(
    title="Google Search API",
    description="Google Custom Search API for product search",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GoogleSearchRequest(BaseModel):
    """Request model for Google search endpoint."""
    query: str
    num_results: int = 10

@app.get("/")
async def root():
    return {
        "message": "Google Search API for Prompt2Insight",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "/google-search": "Google Custom Search for products",
            "/health": "Health check endpoint",
            "/docs": "API documentation"
        },
        "features": [
            "Google Custom Search integration",
            "Product search with images and descriptions"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "google_api_configured": bool(google_api_key and google_engine_id)
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
