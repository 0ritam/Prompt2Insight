"""
Quick test script to verify the Flipkart scraper works
without distutils compatibility issues
"""

import sys
import os

def test_scraper_import():
    """Test if the scraper can be imported without errors"""
    try:
        print("🔄 Testing scraper import...")
        from flipkart_microservice_scraper import FlipkartScraper
        print("✅ Successfully imported FlipkartScraper")
        return True
    except Exception as e:
        print(f"❌ Failed to import FlipkartScraper: {e}")
        return False

def test_scraper_initialization():
    """Test if the scraper can be initialized"""
    try:
        print("🔄 Testing scraper initialization...")
        from flipkart_microservice_scraper import FlipkartScraper
        
        # Try to initialize with headless mode
        scraper = FlipkartScraper(headless=True, max_products=1)
        print("✅ Successfully initialized scraper")
        
        # Clean up
        scraper.close()
        print("✅ Successfully closed scraper")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return False

def test_api_import():
    """Test if the API can be imported"""
    try:
        print("🔄 Testing API import...")
        from flipkart_api import app
        print("✅ Successfully imported FastAPI app")
        return True
    except Exception as e:
        print(f"❌ Failed to import API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Flipkart Scraper Compatibility Test")
    print("=" * 40)
    
    # Test 1: Import scraper
    test1_passed = test_scraper_import()
    
    # Test 2: Initialize scraper (only if import works)
    test2_passed = False
    if test1_passed:
        test2_passed = test_scraper_initialization()
    
    # Test 3: Import API
    test3_passed = test_api_import()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Scraper Import:        {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Scraper Initialization: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"   API Import:            {'✅ PASS' if test3_passed else '❌ FAIL'}")
    
    if all([test1_passed, test2_passed, test3_passed]):
        print("\n🎉 All tests passed! The server should work correctly.")
        print("   You can now run: python server.py")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        if not test1_passed:
            print("   💡 Try installing missing dependencies:")
            print("      pip install selenium webdriver-manager undetected-chromedriver")
        if not test3_passed:
            print("   💡 Check if FastAPI dependencies are installed:")
            print("      pip install fastapi uvicorn")
    
    print("=" * 40)
