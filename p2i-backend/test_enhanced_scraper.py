#!/usr/bin/env python3
"""
Test script for the enhanced DataScraper with Serper.dev integration
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.services.data_scraper import DataScraper

def test_enhanced_data_scraper():
    """Test the enhanced DataScraper with all methods"""
    
    print("🧪 Testing Enhanced DataScraper Integration")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if required API keys are present
    serper_key = os.getenv("SERPER_API_KEY")
    google_key = os.getenv("GOOGLE_CSE_API_KEY")
    google_engine = os.getenv("GOOGLE_CSE_ENGINE_ID")
    
    print("🔑 API Key Status:")
    print(f"   Serper.dev API: {'✅' if serper_key else '❌'}")
    print(f"   Google Search API: {'✅' if google_key else '❌'}")
    print(f"   Google Engine ID: {'✅' if google_engine else '❌'}")
    print()
    
    # Initialize the enhanced scraper
    scraper = DataScraper()
    print("✅ DataScraper initialized with static User-Agent rotation")
    print()
    
    # Test products
    test_products = [
        "iPhone 15",
        "Samsung Galaxy S24",
        "Google Pixel 8"
    ]
    
    for product in test_products:
        print(f"🎯 Testing Product: {product}")
        print("-" * 40)
        
        try:
            # Test the main get_documents method (full pipeline)
            documents = scraper.get_documents(product)
            
            if documents:
                print(f"✅ SUCCESS: Found {len(documents)} documents for {product}")
                
                # Show first document snippet
                first_doc = documents[0]
                print(f"📄 First document preview:")
                print(f"   Length: {len(first_doc)} characters")
                print(f"   Source: {first_doc.split(']')[0] + ']' if '[Source:' in first_doc else 'Unknown'}")
                print(f"   Preview: {first_doc[:200]}...")
                print()
                
                # Check what method was successful
                if "[Source: Serper.dev Search" in first_doc:
                    print("🎯 PRIMARY METHOD SUCCESS: Serper.dev + Smart Scraper")
                elif "[Relevance:" in first_doc:
                    print("📡 FALLBACK 1 SUCCESS: RSS Feeds")
                elif "Title:" in first_doc and "Description:" in first_doc:
                    print("📰 FALLBACK 2 SUCCESS: Google News")
                elif "[Source: Google Search" in first_doc:
                    print("🔍 FALLBACK 3 SUCCESS: Google Search API")
                else:
                    print("❓ SUCCESS: Unknown method")
                
            else:
                print(f"❌ FAILED: No documents found for {product}")
                
        except Exception as e:
            print(f"❌ ERROR testing {product}: {e}")
        
        print("\n" + "="*60 + "\n")

def test_individual_methods():
    """Test individual scraper methods separately"""
    
    print("🔬 Testing Individual Scraper Methods")
    print("="*60)
    
    scraper = DataScraper()
    test_product = "iPhone 15"
    
    # Test 1: Serper.dev URL finding
    print("🎯 Test 1: Serper.dev URL Finding")
    print("-" * 30)
    
    try:
        urls = scraper._find_review_urls(test_product, num_results=3)
        if urls:
            print(f"✅ Found {len(urls)} URLs")
            for i, url in enumerate(urls, 1):
                print(f"   {i}. {url}")
        else:
            print("❌ No URLs found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Smart content extraction
    print("🤖 Test 2: Smart Content Extraction")
    print("-" * 30)
    
    # Use a sample tech review URL for testing
    test_url = "https://www.trustedreviews.com/reviews/apple-iphone-15"
    
    try:
        content = scraper._fetch_article_with_ua(test_url)
        if content:
            print(f"✅ Extracted {len(content)} characters")
            print(f"   Preview: {content[:150]}...")
        else:
            print("❌ No content extracted")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: RSS Fallback
    print("📡 Test 3: RSS Fallback")
    print("-" * 30)
    
    try:
        rss_docs = scraper.scrape_from_rss(test_product)
        if rss_docs:
            print(f"✅ Found {len(rss_docs)} RSS documents")
        else:
            print("❌ No RSS documents found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

def test_environment_setup():
    """Test if the environment is properly set up"""
    
    print("🔧 Environment Setup Test")
    print("="*60)
    
    load_dotenv()
    
    required_packages = [
        "requests", 
        "trafilatura",
        "feedparser",
        "beautifulsoup4"
    ]
    
    print("📦 Package Dependencies:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING!")
    
    print()
    
    print("🔑 Environment Variables:")
    env_vars = [
        "SERPER_API_KEY",
        "GOOGLE_CSE_API_KEY", 
        "GOOGLE_CSE_ENGINE_ID",
        "GOOGLE_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ MISSING"
        masked_value = f"{value[:8]}..." if value and len(value) > 8 else "Not set"
        print(f"   {status} {var}: {masked_value}")
    
    print()

if __name__ == "__main__":
    print("🚀 Enhanced DataScraper Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_environment_setup()
    test_individual_methods()
    test_enhanced_data_scraper()
    
    print("🎉 Test Suite Complete!")
    print("=" * 60)
