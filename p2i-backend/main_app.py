#!/usr/bin/env python3
"""
Main FastAPI application for Prompt2Insight Backend
Amazon product scraping functionality
"""

from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Debug: Check if environment variables are loaded
google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
print(f"🔑 Google API Key loaded: {'✅' if google_api_key else '❌'}")
print(f"🔍 Google Engine ID loaded: {'✅' if google_engine_id else '❌'}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the new API router (includes RAG and Amazon scraper)
from app.api.v1.router import api_router

# Create the main app
app = FastAPI(
    title="Prompt2Insight Backend API",
    description="Amazon product scraping API",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the new API router (includes RAG and Amazon scraper)
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Prompt2Insight Backend API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "/api/v1/rag": "RAG (Retrieval-Augmented Generation) endpoints",
            "/api/v1/scraper": "Amazon scraper endpoints",
            "/docs": "API documentation"
        },
        "features": [
            "Amazon product scraping",
            "RAG-based product analysis",
            "Structured prompt processing"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-01-27T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Prompt2Insight Backend Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "main_app:app",
        host="0.0.0.0", 
        port=8001,
        reload=True
    ) 