"""
Test script to verify Google Search integration works
"""

import sys
import os
from pathlib import Path

# Add the main backend directory to Python path to access the .env file
current_dir = Path(__file__).parent
backend_dir = current_dir.parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from the main .env file
from dotenv import load_dotenv
env_path = backend_dir / ".env"
load_dotenv(env_path)

print(f"Loading .env from: {env_path}")
print(f"GOOGLE_CSE_API_KEY found: {'✅' if os.getenv('GOOGLE_CSE_API_KEY') else '❌'}")
print(f"GOOGLE_CSE_ENGINE_ID found: {'✅' if os.getenv('GOOGLE_CSE_ENGINE_ID') else '❌'}")

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_search import google_search

def test_google_search():
    print("🧪 Testing Google Search Integration")
    print("=" * 40)
    
    try:
        # Test the Google Search
        query = "laptop under 80000 flipkart"
        print(f"🔍 Testing query: {query}")
        
        results = google_search.search_products(query, num_results=3)
        
        print(f"📊 Results: {len(results)} products found")
        
        if results:
            print("\n🛍️ Sample Results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.get('title', 'No title')[:60]}...")
                print(f"      URL: {result.get('url', 'No URL')}")
                print(f"      Description: {result.get('description', 'No description')[:80]}...")
                print()
        else:
            print("❌ No results found")
            
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_google_search()
    if success:
        print("✅ Google Search integration is working!")
    else:
        print("❌ Google Search integration failed!")
