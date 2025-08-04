#!/usr/bin/env python3
"""
Main server entry point for Prompt2Insight Backend
Run this file to start the scraper API server
"""

import sys
import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Check if environment variables are loaded
google_api_key = os.getenv("GOOGLE_CSE_API_KEY")
google_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
print(f"🔑 Google API Key loaded: {'✅' if google_api_key else '❌'}")
print(f"🔍 Google Engine ID loaded: {'✅' if google_engine_id else '❌'}")

# Add the scraper directory to Python path
scraper_dir = Path(__file__).parent / "app" / "scrapers" / "flipkart"
sys.path.insert(0, str(scraper_dir))

# Import the FastAPI app from flipkart_api (now cleaned up to only contain Google Search)
try:
    from flipkart_api import app
    from app.api.v1.router import api_router
    print("✅ Successfully imported flipkart_api (cleaned) and api_router")
except ImportError as e:
    print(f"❌ Failed to import flipkart_api: {e}")
    print(f"Make sure you're in the correct directory and dependencies are installed")
    sys.exit(1)

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    print("🚀 Starting Prompt2Insight Backend Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("\n🔌 Available API Endpoints:")
    print("   🔍 Google Search: /google-search")
    print("   🧠 Central Query Handler: /api/v1/query/handle_query")
    print("   📚 RAG Analysis: /api/v1/rag/ask")
    print("   🛒 Amazon Scraper: /api/v1/amazon/scrape_amazon")
    print("   ❤️  Health Checks: /health, /api/v1/amazon/health")
    print("="*60)
    
    try:
        # Change working directory to the scraper directory for reload to work
        os.chdir(scraper_dir)
        
        uvicorn.run(
            "flipkart_api:app",  # Now clean version with only Google Search
            host="0.0.0.0", 
            port=8001,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")