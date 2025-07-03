#!/usr/bin/env python3
"""
Main server entry point for Prompt2Insight Backend
Run this file to start the scraper API server
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add the scraper directory to Python path
scraper_dir = Path(__file__).parent / "app" / "scrapers" / "flipkart" / "e-commerce-scrapper-main"
sys.path.insert(0, str(scraper_dir))

# Import the FastAPI app from flipkart_api
try:
    from flipkart_api import app
    print("✅ Successfully imported flipkart_api")
except ImportError as e:
    print(f"❌ Failed to import flipkart_api: {e}")
    print(f"Make sure you're in the correct directory and dependencies are installed")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Prompt2Insight Backend Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API docs will be available at: http://localhost:8001/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        # Change working directory to the scraper directory for reload to work
        os.chdir(scraper_dir)
        
        uvicorn.run(
            "flipkart_api:app",  # Use import string instead of app object
            host="0.0.0.0", 
            port=8001,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
